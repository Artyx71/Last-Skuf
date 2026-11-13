#!/usr/bin/env python3
"""Sequential phase controller. automation/phase_state.json is the sole authority."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
DEFAULT_PHASES=['P00','P01','P02','P03','P04','P04G','P05','P06','P07','P08']


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')
def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path,default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default

def save(path,data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    with temp.open('w') as stream:
        json.dump(data,stream,ensure_ascii=False,indent=2); stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    os.replace(temp,path)
    directory=os.open(path.parent,os.O_RDONLY)
    try: os.fsync(directory)
    finally: os.close(directory)


class Busy(RuntimeError): pass
class Blocked(RuntimeError): pass


class Controller:
    def __init__(self,root=ROOT):
        self.root=Path(root).resolve(); self.data=self.root/'.autopilot'
        self.state_path=self.root/'automation/phase_state.json'
        self.lock_path=self.root/'automation/.executor.lock'
        self.pause_path=self.data/'PAUSE'
        self.config=load(self.root/'autopilot/config.json',{})
        self.phases=self.config.get('phase_order',DEFAULT_PHASES)
        if self.phases != DEFAULT_PHASES:
            raise Blocked('Phase order must preserve all gates, including P04G before P07')
        self.fd=None

    @contextmanager
    def exclusive(self):
        self.lock_path.parent.mkdir(parents=True,exist_ok=True)
        fd=os.open(self.lock_path,os.O_RDWR|os.O_CREAT,0o600)
        try:
            try: fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError: raise Busy('Another controller/worker holds the exclusive execution lease')
            self.fd=fd
            legacy=self.data/'RUNNING.lock'; previous=load(legacy)
            if previous and previous.get('pid')!=os.getpid():
                try: os.kill(int(previous['pid']),0)
                except ProcessLookupError:
                    save(self.data/('recovered-lock-'+uuid.uuid4().hex+'.json'),previous)
                else: raise Busy('Legacy executor lock names a live process; refusing a second executor')
            token=uuid.uuid4().hex
            save(legacy,{'pid':os.getpid(),'when':utc(),'token':token,'authority':'automation/.executor.lock'})
            yield
        finally:
            legacy=self.data/'RUNNING.lock'
            if 'token' in locals() and load(legacy,{}).get('token')==token:
                legacy.unlink(missing_ok=True)
            self.fd=None
            # Do NOT LOCK_UN: a surviving worker shares this open file description.
            os.close(fd)

    def state(self):
        state=load(self.state_path)
        if not isinstance(state,dict) or 'active_phase' not in state:
            raise Blocked('Existing automation/phase_state.json required; refusing to reset progress')
        return state

    def persist(self,state):
        if self.fd is None: raise RuntimeError('State mutation requires execution lease')
        save(self.state_path,state)
        # Compatibility mirror only; never read this as authority.
        auto=state['autopilot']
        if self.pause_path.exists(): auto['paused']=True
        save(self.data/'STATE.json',{'schema':2,'authority':'automation/phase_state.json',
            'current_phase':state['active_phase'],'paused':auto['paused'],'phases':auto['phases'],
            'history':auto['history'],'canonical_sha256':digest(self.state_path)})

    def reconcile(self):
        state=self.state(); self.data.mkdir(parents=True,exist_ok=True)
        if 'autopilot' not in state:
            legacy=load(self.data/'STATE.json')
            if legacy is not None: save(self.data/'legacy_state_backup.json',legacy)
            save(self.data/'preintegration_phase_state.json',state)
            state['autopilot']={'schema':2,'paused':True,'phases':{},'tasks':{},'history':[],
                                'operation':None,'authority':'automation/phase_state.json'}
        auto=state['autopilot']
        for phase in self.phases:
            path=self.root/f'reports/phases/{phase}/decision.json'
            decision=load(path)
            record=auto['phases'].setdefault(phase,{'status':'PENDING','attempts':0})
            if decision:
                if decision.get('phase')!=phase or decision.get('status') not in ['PASS','FAIL','BLOCKED'] or not decision.get('reviewer'):
                    raise Blocked(f'Invalid independent decision: {path}')
                value=digest(path)
                if record.get('decision_sha256')!=value:
                    if record['status']=='PASS' and decision['status']!='PASS':
                        raise Blocked(f'Previously passed {phase} now has a different non-PASS decision; reconcile manually')
                    record.update(status=decision['status'],attempts=max(record['attempts'],decision.get('attempt',0)),
                        decision=str(path.relative_to(self.root)),decision_sha256=value,reviewer=decision['reviewer'])
                    if phase==state['active_phase']:
                        state['status']=decision['status']; state['last_decision']=str(path.relative_to(self.root))
                        if decision['status']=='PASS': state['last_pass']=phase
        # Retain all legacy global progress, counters, findings and immutable historical decisions.
        self.persist(state)
        return state

    def record(self,event,**details):
        state=self.state(); state['autopilot']['history'].append({'when':utc(),'event':event,**details})
        self.persist(state)

    def receipt(self,job):
        receipt=load(job['receipt'])
        if receipt is None: return None
        if receipt.get('operation')!=job['id'] or receipt.get('argv_sha256')!=job['argv_sha256']:
            raise Blocked('Mismatched worker completion receipt')
        if digest(job['log'])!=receipt.get('log_sha256'):
            raise Blocked('Worker log changed after completion')
        return receipt

    def stage(self,task,argv,timeout,stdin='',safe_retry=True,cwd=None):
        if self.fd is None: raise RuntimeError('No exclusive execution lease')
        state=self.state(); auto=state['autopilot']; previous=auto.get('operation')
        argv=list(map(str,argv)); cwd=str(cwd or self.root)
        command_hash=hashlib.sha256(json.dumps(argv).encode()).hexdigest()
        inputs={}; output_argument=False
        for arg in argv[1:]:
            if output_argument:
                output_argument=False; continue
            if arg in ['--output-last-message','--output','-o']:
                output_argument=True; continue
            try:
                path=Path(cwd)/arg
                if path.is_file(): inputs[str(path)]=digest(path)
            except OSError:
                pass  # Inline -c text is an argv value, not a filesystem path.
        if task=='P03/audio-qa':
            for name in ['tools/fixtures/audio_qa_capture.gd','game/assets/audio/manifest.json']:
                inputs[name]=digest(self.root/name)
        input_hash=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
        if previous and not previous.get('consumed',False):
            if previous['task']!=task:
                raise Blocked(f'Recover unfinished {previous["task"]} before starting {task}')
            if previous['argv_sha256']!=command_hash or previous['cwd']!=cwd or previous.get('stdin','')!=stdin or previous.get('input_sha256')!=input_hash:
                raise Blocked('Stage inputs changed since interruption; reconcile before replay')
            completed=self.receipt(previous)
            if completed is not None:
                previous['status']='COMPLETED' if completed['exit_code']==0 else 'FAILED'
                previous['exit_code']=completed['exit_code']; self.persist(state)
                self.record('RECOVERED_COMPLETED_STAGE',task=task,operation=previous['id'])
                return completed['exit_code']
            if not previous.get('safe_retry',False):
                raise Blocked('Interrupted implementation has no receipt: independent recovery review required before any replay')
            auto['history'].append({'when':utc(),'event':'RETRY_INTERRUPTED_IDEMPOTENT_STAGE','operation':previous['id']})
        if self.pause_path.exists() or auto['paused']:
            raise Blocked('Execution paused; resume changes permission to run, not phase gates')
        ident=uuid.uuid4().hex; directory=self.data/'jobs'/ident; directory.mkdir(parents=True)
        argv=list(map(str,argv))
        job={'id':ident,'task':task,'argv':argv,'argv_sha256':hashlib.sha256(json.dumps(argv).encode()).hexdigest(),
            'cwd':cwd,'timeout':timeout,'stdin':stdin,'log':str(directory/'output.log'),
            'receipt':str(directory/'receipt.json'),'started':str(directory/'started.json'),
            'status':'RUNNING','consumed':False,'input_sha256':input_hash,'safe_retry':safe_retry,'created_at':utc()}
        auto['operation']=job; self.persist(state); save(directory/'input.json',job)
        worker=subprocess.Popen([sys.executable,str(self.root/'autopilot/worker.py'),str(directory/'input.json'),str(self.fd)],
            cwd=self.root,pass_fds=(self.fd,),start_new_session=True)
        interrupted=False
        def stop(_sig,_frame):
            nonlocal interrupted
            interrupted=True
        old_handlers={sig:signal.signal(sig,stop) for sig in [signal.SIGTERM,signal.SIGINT]}
        try:
            while worker.poll() is None:
                if interrupted or self.pause_path.exists():
                    worker.terminate()
                    try: worker.wait(timeout=5)
                    except subprocess.TimeoutExpired: worker.kill(); worker.wait()
                    break
                time.sleep(.1)
        finally:
            for sig,handler in old_handlers.items(): signal.signal(sig,handler)
        receipt=self.receipt(job)
        state=self.state(); operation=state['autopilot']['operation']
        if self.pause_path.exists(): state['autopilot']['paused']=True
        if receipt:
            code=receipt['exit_code']; operation.update(status='COMPLETED' if code==0 else 'FAILED',exit_code=code)
        else:
            code=130; operation['status']='RUNNING'  # Recovery must inspect the durable receipt, never assume success.
        self.persist(state)
        return code

    def run_audio(self):
        code=self.stage('P03/audio-qa',[sys.executable,'tools/audio_qa.py','--capture-engine','--output','reports/autopilot/P03/audio_qa'],180)
        path=self.root/'reports/autopilot/P03/audio_qa/report.json'
        report=load(path,{})
        ok=code==0 and report.get('technical_status')=='PASS' and report.get('engine')
        state=self.state(); state['autopilot']['tasks']['P03/audio-qa']={
            'status':'PASS' if ok else 'FAIL','report':str(path.relative_to(self.root)),
            'sha256':digest(path) if path.exists() else None,'scope':'Technical audio signal/runtime only; never clears artistic gate'}
        state['autopilot']['operation']['consumed']=True
        self.persist(state)
        return 0 if ok else 1

    def prerequisite(self,phase):
        state=self.state(); records=state['autopilot']['phases']
        missing=[p for p in self.phases[:self.phases.index(phase)] if records[p]['status']!='PASS']
        if missing: raise Blocked(f'{phase} prerequisites not PASS: {missing}')
        previous=self.phases[:self.phases.index(phase)]
        if previous and records[previous[-1]].get('merge',{}).get('status')!='MERGED':
            raise Blocked(f'{previous[-1]} must have a confirmed main merge before {phase}')
        if phase=='P07' and records['P04G']['status']!='PASS': raise Blocked('Full campaign requires Combat/Gore P04G PASS')

    def checkpoint(self,phase,value,status=None):
        state=self.state(); item=state['autopilot']['phases'][phase]
        item['checkpoint']=value
        if status:
            item['status']=status
            state['status']=status
            if status=='PASS':
                state['last_pass']=phase
                state['last_decision']=f'reports/phases/{phase}/decision.json'
        if state['autopilot'].get('operation'): state['autopilot']['operation']['consumed']=True
        self.persist(state)

    def workspace(self,phase):
        state=self.state(); item=state['autopilot']['phases'][phase]
        if item.get('workspace'):
            path=Path(item['workspace'])
            if not path.is_dir(): raise Blocked('Existing phase workspace missing; never reset it automatically')
            return path
        directory=self.data/'worktrees'/phase
        if directory.exists(): raise Blocked('Unregistered worktree exists; reconcile without overwriting it')
        branch='phase/'+phase.lower()+'-implementation'
        subprocess.run(['git','fetch','origin','main'],cwd=self.root,check=True,capture_output=True)
        directory.parent.mkdir(parents=True,exist_ok=True)
        subprocess.run(['git','worktree','add','-b',branch,str(directory),'origin/main'],cwd=self.root,check=True,capture_output=True)
        item.update(workspace=str(directory),branch=branch); self.persist(state)
        return directory

    def run_phase(self,phase):
        self.prerequisite(phase)
        from github import manage,validate_review,wait_ci
        item=self.state()['autopilot']['phases'][phase]
        if item['status']=='PASS': return manage(self,phase,'merge')
        if item['status']=='BLOCKED': raise Blocked(f'{phase} BLOCKED; independent recovery/new decision required')
        work=self.workspace(phase)
        while True:
            state=self.state(); item=state['autopilot']['phases'][phase]
            checkpoint=item.get('checkpoint')
            if not checkpoint:
                if item['attempts']>=self.config['max_attempts_per_phase']: raise Blocked('Repair budget exhausted')
                item['attempts']+=1; item['checkpoint']='implementation'; item['status']='IMPLEMENTING'
                state['active_phase']=phase; self.persist(state); checkpoint='implementation'
            cli=self.config['codex_binary']
            if checkpoint=='implementation':
                prompt=(self.root/'autopilot/prompts/PHASE_EXECUTION.md').read_text()
                prompt+=f'\nPhase={phase}; authoritative controller={self.state_path} (do not edit it). This worktree preserves prior main. One executor, no subagents. Commit source/evidence on this phase branch. Do not merge/change gates. Findings: {json.dumps(item.get("remediation",[]))}\n'
                code=self.stage(phase+'/implementation',[cli,'exec','--sandbox','workspace-write','--cd',work,'-'],
                    self.config['phase_timeout_seconds'],prompt,safe_retry=False,cwd=work)
                if code:
                    self.checkpoint(phase,'recovery-review','BLOCKED')
                    raise Blocked('Interrupted implementation: inspect preserved work with independent recovery review; no blind replay')
                self.checkpoint(phase,'validation'); checkpoint='validation'
            if checkpoint=='validation':
                code=self.stage(phase+'/validation',[sys.executable,'tools/verify.py','--output',f'reports/autopilot/{phase}/validation'],300,cwd=work)
                if code:
                    state=self.state(); item=state['autopilot']['phases'][phase]
                    item['remediation']=[{'severity':'HIGH','message':f'Validation failed; inspect reports/autopilot/{phase}/validation'}]
                    self.persist(state); self.checkpoint(phase,None,'FAIL'); continue
                self.checkpoint(phase,'publication'); checkpoint='publication'
            if checkpoint=='publication':
                if manage(self,phase,'prepare'): return 4
                self.checkpoint(phase,'ci'); checkpoint='ci'
            if checkpoint=='ci':
                if not wait_ci(self,phase): return 4
                self.checkpoint(phase,'review'); checkpoint='review'
            if checkpoint=='review':
                head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip()
                output=self.data/f'{phase}-{head}-review.json'
                prompt=(self.root/'autopilot/prompts/INDEPENDENT_REVIEW.md').read_text()
                prompt+=f'\nPhase={phase}; exact SHA={head}. Fetch current main SHA/PR base/CI; include base_branch/main and base_sha. Return only JSON; do not edit implementation. Previous findings={json.dumps(item.get("remediation",[]))}.\n'
                code=self.stage(phase+'/review',[cli,'exec','--sandbox','read-only','--cd',work,
                    '--output-schema',self.root/'autopilot/review_schema.json','--output-last-message',output,'-'],
                    self.config['review_timeout_seconds'],prompt,cwd=work)
                verdict=load(output,{})
                errors=validate_review(work,verdict,head,phase)
                if code or errors: raise Blocked(f'Invalid/missing independent review: {errors}')
                save(self.data/'reviews'/f'{phase}-{head}.json',verdict)
                save(self.root/f'reports/phases/{phase}/decision.json',verdict)
                state=self.state(); item=state['autopilot']['phases'][phase]
                item['remediation']=verdict['findings']; item['review_receipt']=str(output)
                item['decision']=f'reports/phases/{phase}/decision.json'
                item['decision_sha256']=digest(self.root/item['decision']); item['reviewer']=verdict['reviewer']
                self.persist(state)
                if verdict['status']=='FAIL':
                    self.record('REMEDIATION_QUEUED',phase=phase,findings=verdict['findings'])
                    self.checkpoint(phase,None,'FAIL'); continue
                self.checkpoint(phase,'merge',verdict['status'])
                if verdict['status']=='BLOCKED': raise Blocked('Lead BLOCKED; no merge/advance')
                checkpoint='merge'
            if checkpoint=='merge': return manage(self,phase,'merge')
            if checkpoint not in ['implementation','validation','publication','ci','review','merge']:
                raise Blocked('Recovery checkpoint requires independent investigation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['init','reconcile','status','run','pause','resume','pr'])
    parser.add_argument('--phase')
    parser.add_argument('--task',choices=['audio-qa','prepare-p04'])
    parser.add_argument('--pr-action',choices=['status','prepare','merge'],default='status')
    args=parser.parse_args(); controller=Controller()
    if args.command=='status':
        state=controller.state(); view=state.get('autopilot',{'not_integrated':True,'legacy_progress':state})
        view['effective_paused']=view.get('paused',True) or controller.pause_path.exists()
        print(json.dumps(view,ensure_ascii=False,indent=2)); return 0
    if args.command=='pause':
        save(controller.pause_path,{'requested_at':utc()}); print('Pause requested; no new stage will start.'); return 0
    try:
        with controller.exclusive():
            state=controller.reconcile()
            if args.command in ['init','reconcile']:
                print('Reconciled existing decisions; no phase or attempt reset.'); return 0
            if args.command=='resume':
                controller.pause_path.unlink(missing_ok=True); state['autopilot']['paused']=False; controller.persist(state)
                print('Resumed; run is explicit, phase/merge gates remain enforced.'); return 0
            phase=args.phase or state['active_phase']
            if args.command=='run' and not args.phase and not args.task:
                # Historical PASS phases can have open stacked PRs. Reconcile their
                # delivery first, without resetting them or redoing implementation.
                for candidate in controller.phases:
                    record=state['autopilot']['phases'][candidate]
                    if record['status']!='PASS' or record.get('merge',{}).get('status')!='MERGED':
                        phase=candidate; break
            if phase not in controller.phases: raise Blocked('Unknown phase')
            if args.command=='pr':
                from github import manage
                return manage(controller,phase,args.pr_action)
            if args.task=='audio-qa': return controller.run_audio()
            if args.task=='prepare-p04':
                code=controller.stage('prepare-p04',[sys.executable,'tools/p04_readiness.py'],60)
                state=controller.state(); state['autopilot']['operation']['consumed']=True; controller.persist(state)
                return code
            # A completed merge is the only event that advances the autonomous phase loop.
            while True:
                if controller.phases.index(phase)>controller.phases.index(controller.config['stop_after_phase']):
                    raise Blocked('Configured phase limit reached; later work remains queued')
                code=controller.run_phase(phase)
                if code or phase==controller.config['stop_after_phase']: return code
                state=controller.state()
                if state['autopilot']['phases'][phase].get('merge',{}).get('status')!='MERGED': return 4
                phase=controller.phases[controller.phases.index(phase)+1]
    except Busy as exc: print('BUSY:',exc,file=sys.stderr); return 3
    except (Blocked,ValueError,OSError) as exc: print('BLOCKED:',exc,file=sys.stderr); return 4

if __name__=='__main__': sys.exit(main())
