import copy
import contextlib
import io
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'autopilot'))
from runner import Controller,Busy,Blocked,save,load
from github import guarded_merge,gate,validate_review


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name)
        (self.root/'autopilot').mkdir()
        shutil.copy(ROOT/'autopilot/worker.py',self.root/'autopilot/worker.py')
        shutil.copy(ROOT/'autopilot/config.json',self.root/'autopilot/config.json')
        save(self.root/'automation/phase_state.json',{'active_phase':'P03','status':'BLOCKED','attempts':1,'last_pass':'P02','custom':'preserve'})
        for phase,status in [('P00','PASS'),('P01','PASS'),('P02','PASS'),('P03','BLOCKED')]:
            save(self.root/f'reports/phases/{phase}/decision.json',{'phase':phase,'status':status,'attempt':2 if phase!='P03' else 1,'reviewer':'separate-fixture-reviewer'})
        self.controller=Controller(self.root)
        with self.controller.exclusive():
            st=self.controller.reconcile();st['autopilot']['paused']=False;self.controller.persist(st)
    def tearDown(self): self.temp.cleanup()
    def test_reconcile_preserves_progress_and_ignores_legacy_reset(self):
        save(self.root/'.autopilot/STATE.json',{'phases':{'P00':{'status':'UNVERIFIED'}}})
        with self.controller.exclusive(): st=self.controller.reconcile()
        self.assertEqual(st['custom'],'preserve');self.assertEqual(st['attempts'],1)
        self.assertEqual(st['autopilot']['phases']['P02']['status'],'PASS')
        self.assertEqual(st['autopilot']['phases']['P03']['attempts'],1)
    def test_two_controllers_cannot_hold_lease(self):
        with self.controller.exclusive():
            with self.assertRaises(Busy):
                with Controller(self.root).exclusive(): pass
    def test_prerequisite_cannot_skip_blocked_p03(self):
        with self.assertRaises(Blocked):self.controller.prerequisite('P04')
        with self.assertRaises(Blocked):self.controller.prerequisite('P07')
    def test_missing_state_is_not_reinitialized(self):
        self.controller.state_path.unlink()
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.reconcile()
        self.assertFalse(self.controller.state_path.exists())
    def test_invalid_decision_does_not_reset_state(self):
        save(self.root/'reports/phases/P02/decision.json',{'phase':'P02','status':'PASS'})
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.reconcile()
        self.assertEqual(self.controller.state()['last_pass'],'P02')
    def test_cannot_downgrade_pass_automatically(self):
        save(self.root/'reports/phases/P02/decision.json',{'phase':'P02','status':'FAIL','reviewer':'x'})
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.reconcile()
    def test_timeout_stops_whole_child_group(self):
        argv=[sys.executable,'-c','import time;time.sleep(60)']
        with self.controller.exclusive():code=self.controller.stage('fixture-timeout',argv,.2)
        self.assertEqual(code,124)
    def test_receipt_tampering_fails_closed(self):
        argv=[sys.executable,'-c','print("fixture")']
        with self.controller.exclusive():self.assertEqual(self.controller.stage('fixture',argv,3),0)
        job=self.controller.state()['autopilot']['operation'];Path(job['log']).write_text('tampered')
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.stage('fixture',argv,3)
    def test_changed_stage_inputs_not_adopted(self):
        argv=[sys.executable,'-c','print("one")']
        with self.controller.exclusive():self.controller.stage('fixture',argv,3)
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.stage('fixture',[sys.executable,'-c','print("two")'],3)
    def test_pause_blocks_execution_without_phase_reset(self):
        save(self.controller.pause_path,{'paused':True})
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.stage('fixture',[sys.executable,'-c','print(1)'],3)
        self.assertEqual(self.controller.state()['last_pass'],'P02')
    def test_killed_parent_worker_finishes_and_is_adopted_once(self):
        counter=self.root/'executions'; marker=self.root/'started'
        child=f'from pathlib import Path;import time;p=Path({str(counter)!r});p.write_text(p.read_text()+"x" if p.exists() else "x");Path({str(marker)!r}).touch();time.sleep(1.3)'
        argv=[sys.executable,'-c',child]
        script=f'import sys;sys.path.insert(0,{str(ROOT/"autopilot")!r});from runner import Controller;c=Controller({str(self.root)!r});\nwith c.exclusive():c.stage("recovery-fixture",{argv!r},5)'
        proc=subprocess.Popen([sys.executable,'-c',script],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        deadline=time.monotonic()+5
        while not marker.exists() and time.monotonic()<deadline:time.sleep(.02)
        self.assertTrue(marker.exists());proc.kill();proc.wait();proc.stderr.close()
        with self.assertRaises(Busy):
            with self.controller.exclusive():pass
        job=self.controller.state()['autopilot']['operation']
        deadline=time.monotonic()+5
        while not Path(job['receipt']).exists() and time.monotonic()<deadline:time.sleep(.02)
        self.assertTrue(Path(job['receipt']).exists())
        # Receipt is durable before worker teardown. Do not confuse receipt visibility
        # with lease release; a second executor must remain blocked until both occur.
        deadline=time.monotonic()+5
        while True:
            try:
                with self.controller.exclusive():self.assertEqual(self.controller.stage('recovery-fixture',argv,5),0)
                break
            except Busy:
                if time.monotonic()>=deadline:raise
                time.sleep(.02)
        self.assertEqual(counter.read_text(),'x')
        self.assertEqual(self.controller.state()['autopilot']['phases']['P02']['status'],'PASS')
    def test_phase_gate_pass_does_not_bypass_missing_merge(self):
        with self.controller.exclusive():
            st=self.controller.state();st['autopilot']['phases']['P03']['status']='PASS';self.controller.persist(st)
        with self.assertRaises(Blocked):self.controller.prerequisite('P04')
    def test_legacy_live_process_lock_is_not_deleted(self):
        process=subprocess.Popen([sys.executable,'-c','import time;time.sleep(10)'])
        try:
            save(self.controller.data/'RUNNING.lock',{'pid':process.pid,'legacy':True})
            with self.assertRaises(Busy):
                with self.controller.exclusive():pass
            self.assertTrue((self.controller.data/'RUNNING.lock').exists())
        finally:process.terminate();process.wait()
    def test_changed_script_after_completed_stage_requires_reconciliation(self):
        script=self.root/'probe.py';script.write_text('print("first")')
        argv=[sys.executable,str(script)]
        with self.controller.exclusive():self.controller.stage('script-fixture',argv,3)
        script.write_text('print("changed")')
        with self.controller.exclusive():
            with self.assertRaises(Blocked):self.controller.stage('script-fixture',argv,3)
    def test_historical_merge_never_regresses_authoring_progress(self):
        from github import manage
        with self.controller.exclusive():
            st=self.controller.state();st['autopilot']['phases']['P00']['pull_request_number']=1;self.controller.persist(st)
            with patch('github.api',return_value={'head':{'sha':'a'*40},'merged':False,'draft':False}), patch('github.guarded_merge',return_value={'status':'MERGED','merge_sha':'d'*40}), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P00','merge',{}),0)
        state=self.controller.state()
        self.assertEqual(state['active_phase'],'P03');self.assertEqual(state['last_pass'],'P02')
        self.assertEqual(state['attempts'],1);self.assertEqual(state['autopilot']['delivery_next'],'P01')
    def test_current_phase_merge_advances_after_confirmation(self):
        from github import manage
        with self.controller.exclusive():
            st=self.controller.state()
            for p in ['P00','P01','P02']:st['autopilot']['phases'][p]['merge']={'status':'MERGED'}
            st['autopilot']['phases']['P03'].update(status='PASS',pull_request_number=4)
            self.controller.persist(st)
            with patch('github.api',return_value={'head':{'sha':'a'*40},'merged':False,'draft':False}), patch('github.guarded_merge',return_value={'status':'MERGED','merge_sha':'d'*40}), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P03','merge',{}),0)
        state=self.controller.state();self.assertEqual(state['active_phase'],'P04')
        self.assertEqual(state['last_pass'],'P03');self.assertEqual(state['status'],'READY')
    def test_success_checkpoint_is_atomic_with_receipt_consumption(self):
        argv=[sys.executable,'-c','print("ok")']
        with self.controller.exclusive():
            self.controller.stage('P03/test',argv,3)
            self.controller.checkpoint('P03','validation')
        state=self.controller.state()
        self.assertEqual(state['autopilot']['phases']['P03']['checkpoint'],'validation')
        self.assertTrue(state['autopilot']['operation']['consumed'])
    def test_prepare_recovers_existing_pr_after_decision_loses_number(self):
        from github import manage
        calls=[]
        def api(endpoint,method='GET',payload=None):
            calls.append((endpoint,method,payload))
            if '/pulls?' in endpoint:
                return [{'number':4,'head':{'ref':'phase/p03-dialogue-audio','repo':{'full_name':'Artyx71/Last-Skuf'}}}]
            if method=='PATCH':return {}
            return {'base':{'ref':'phase/p02-combat'}}
        with self.controller.exclusive():
            state=self.controller.state();state['autopilot']['phases']['P02']['merge']={'status':'MERGED'};self.controller.persist(state)
            with patch('github.api',side_effect=api),patch('github.subprocess.check_output',return_value='phase/p03-dialogue-audio\n'),patch('github.publish_branch') as publish,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P03','prepare'),0)
                publish.assert_not_called()
        self.assertEqual(self.controller.state()['autopilot']['phases']['P03']['pull_request_number'],4)
        self.assertFalse(any(method=='POST' for _,method,_ in calls))
        self.assertIn(('repos/Artyx71/Last-Skuf/pulls/4','PATCH',{'base':'main'}),calls)
    def test_ambiguous_existing_prs_block_without_creating_duplicate(self):
        from github import manage
        pulls=[{'number':n,'head':{'ref':'phase/p03-audio','repo':{'full_name':'Artyx71/Last-Skuf'}}} for n in [4,5]]
        with self.controller.exclusive(),patch('github.api',return_value=pulls) as api,patch('github.subprocess.check_output',return_value='phase/p03-audio\n'),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(manage(self.controller,'P03','prepare'),4)
        self.assertEqual(api.call_count,1)
        self.assertIn('Multiple open PRs',self.controller.state()['autopilot']['phases']['P03']['merge']['blockers'][0])
    def test_missing_number_workspace_ownership_blocks_before_any_github_action(self):
        from github import manage
        with self.controller.exclusive():
            state=self.controller.state();state['autopilot']['phases']['P03'].update(workspace=str(self.root),branch='phase/p03-audio');self.controller.persist(state)
            with patch('github.api') as api,patch('github.subprocess.check_output',return_value='phase/p04-mission\n'),patch('github.publish_branch') as publish,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P03','prepare'),4)
                api.assert_not_called();publish.assert_not_called()
    def test_unregistered_wrong_phase_branch_cannot_discover_or_create_pr(self):
        from github import manage
        with self.controller.exclusive(),patch('github.api') as api,patch('github.subprocess.check_output',return_value='phase/p04-mission\n'),patch('github.publish_branch') as publish,contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(manage(self.controller,'P03','prepare'),4)
            api.assert_not_called();publish.assert_not_called()
    def test_existing_workspace_pr_publishes_repair_before_ci(self):
        from github import manage
        with self.controller.exclusive():
            state=self.controller.state();state['autopilot']['phases']['P03'].update(pull_request_number=4,workspace=str(self.root),branch='phase/p03-audio');self.controller.persist(state)
            view={'state':'open','head':{'ref':'phase/p03-audio','repo':{'full_name':'Artyx71/Last-Skuf'}},'base':{'ref':'main'}}
            with patch('github.api',return_value=view),patch('github.subprocess.check_output',return_value='phase/p03-audio\n'),patch('github.publish_branch') as publish,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P03','prepare'),0)
                publish.assert_called_once_with(self.root,'phase/p03-audio')
    def test_existing_workspace_cannot_publish_to_different_pr_branch(self):
        from github import manage
        with self.controller.exclusive():
            state=self.controller.state();state['autopilot']['phases']['P03'].update(pull_request_number=4,workspace=str(self.root),branch='phase/p03-audio');self.controller.persist(state)
            view={'state':'open','head':{'ref':'phase/p04-mission','repo':{'full_name':'Artyx71/Last-Skuf'}},'base':{'ref':'main'}}
            with patch('github.api',return_value=view),patch('github.subprocess.check_output',return_value='phase/p03-audio\n'),patch('github.publish_branch') as publish,contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(manage(self.controller,'P03','prepare'),4)
                publish.assert_not_called()


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        evidence=self.root/'evidence.txt';evidence.write_text('fixture independent evidence')
        self.review={'phase':'P04','status':'PASS','reviewed_commit':'a'*40,'base_branch':'main','base_sha':'b'*40,'independent_review':True,'reviewer':'independent-test-context','evidence':[{'path':'evidence.txt','sha256':hashlib.sha256(evidence.read_bytes()).hexdigest()}],'findings':[]}
        self.view={'number':4,'repository':'Artyx71/Last-Skuf','private':False,'head_repo':'Artyx71/Last-Skuf','head_sha':'a'*40,'base':'main','base_sha':'b'*40,'state':'open','draft':False,'squash_allowed':True,'permissions':{'push':True},'protection_inspected':True,'mergeable':True,'merge_state':'CLEAN','threads_complete':True,'unresolved_threads':0,'review_decision':'APPROVED','approvals_required':1,'queue_required':False,'required_checks':['bootstrap'],'integration_ids':{},'checks':{'bootstrap':{'status':'completed','conclusion':'success','head_sha':'a'*40,'app_id':1,'app_slug':'github-actions'}}}
    def tearDown(self):self.temp.cleanup()
    def test_exact_review_and_ci_pass(self):self.assertEqual(gate(self.root,self.view,self.review,'P04'),[])
    def test_fail_blocked_and_unresolved_critical_forbid_merge(self):
        for status in ['FAIL','BLOCKED']:
            r=copy.deepcopy(self.review);r['status']=status
            self.assertTrue(gate(self.root,self.view,r,'P04'))
        r=copy.deepcopy(self.review);r['findings']=[{'severity':'CRITICAL','status':'OPEN'}]
        self.assertTrue(gate(self.root,self.view,r,'P04'))
    def test_old_head_and_old_base_review_rejected(self):
        for field in ['reviewed_commit','base_sha']:
            r=copy.deepcopy(self.review);r[field]='c'*40
            self.assertTrue(gate(self.root,self.view,r,'P04'))
    def test_manual_approval_threads_protection_and_draft_block(self):
        for key,value in [('review_decision','REVIEW_REQUIRED'),('review_decision','CHANGES_REQUESTED'),('unresolved_threads',1),('threads_complete',False),('protection_inspected',False),('draft',True),('base','phase/p02'),('queue_required',True)]:
            view=copy.deepcopy(self.view);view[key]=value
            self.assertTrue(gate(self.root,view,self.review,'P04'),key)
    def test_missing_pending_failed_wrong_sha_ci_all_block(self):
        for mode in ['missing','pending','failure','wrongsha']:
            view=copy.deepcopy(self.view)
            if mode=='missing':view['checks']={}
            elif mode=='pending':view['checks']['bootstrap']['status']='in_progress'
            elif mode=='failure':view['checks']['bootstrap']['conclusion']='failure'
            else:view['checks']['bootstrap']['head_sha']='c'*40
            self.assertTrue(gate(self.root,view,self.review,'P04'),mode)
    def test_toctou_head_change_never_sends_merge(self):
        changed=copy.deepcopy(self.view);changed['head_sha']='c'*40
        views=iter([self.view,changed]); sent=[]
        result=guarded_merge(self.root,4,{},self.review,'P04',lambda *_:next(views),lambda *a:sent.append(a))
        self.assertEqual(result['status'],'BLOCKED');self.assertFalse(sent)
    def test_ci_changes_immediately_before_merge_block(self):
        changed=copy.deepcopy(self.view);changed['checks']['bootstrap']['status']='in_progress'
        views=iter([self.view,changed]);sent=[]
        result=guarded_merge(self.root,4,{},self.review,'P04',lambda *_:next(views),lambda *a:sent.append(a))
        self.assertEqual(result['status'],'BLOCKED');self.assertFalse(sent)
    def test_atomic_sha_squash_and_remote_confirmation(self):
        calls=[]
        def request(endpoint,method='GET',payload=None):
            calls.append((endpoint,method,payload))
            if method=='PUT':return {'merged':True,'sha':'d'*40}
            if '/git/commits/' in endpoint:return {'parents':[{'sha':'b'*40}]}
            return {'merged':True,'head':{'sha':'a'*40},'base':{'ref':'main'}}
        result=guarded_merge(self.root,4,{},self.review,'P04',lambda *_:copy.deepcopy(self.view),request)
        self.assertEqual(result['status'],'MERGED')
        self.assertEqual(calls[0][2],{'sha':'a'*40,'merge_method':'squash'})
    def test_merge_intent_is_persisted_before_request(self):
        events=[]
        def intent(view):events.append(('intent',view['head_sha']))
        def request(endpoint,method='GET',payload=None):
            if method=='PUT':
                self.assertEqual(events,[('intent','a'*40)]);events.append(('merge',payload['sha']))
                return {'merged':True,'sha':'d'*40}
            if '/git/commits/' in endpoint:return {'parents':[{'sha':'b'*40}]}
            return {'merged':True,'head':{'sha':'a'*40},'base':{'ref':'main'}}
        result=guarded_merge(self.root,4,{},self.review,'P04',lambda *_:copy.deepcopy(self.view),request,before_request=intent)
        self.assertEqual(result['status'],'MERGED')
    def test_unverified_merged_parent_blocks_progress(self):
        def request(endpoint,method='GET',payload=None):
            if method=='PUT':return {'merged':True,'sha':'d'*40}
            if '/git/commits/' in endpoint:return {'parents':[{'sha':'e'*40}]}
            return {'merged':True,'head':{'sha':'a'*40},'base':{'ref':'main'}}
        result=guarded_merge(self.root,4,{},self.review,'P04',lambda *_:copy.deepcopy(self.view),request)
        self.assertEqual(result['status'],'BLOCKED')
    def test_signal_metrics_cannot_close_artistic_gate(self):
        r=copy.deepcopy(self.review);r['phase']='P03';r['artistic_audio_acceptance']={'status':'PASS','method':'waveform'}
        self.assertTrue(validate_review(self.root,r,'a'*40,'P03'))
    def test_mutated_evidence_rejected(self):
        (self.root/'evidence.txt').write_text('changed')
        self.assertTrue(validate_review(self.root,self.review,'a'*40,'P04'))

if __name__=='__main__':unittest.main()
