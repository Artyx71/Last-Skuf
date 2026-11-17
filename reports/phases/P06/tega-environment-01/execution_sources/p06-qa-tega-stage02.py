import sys,subprocess,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'autopilot'))
from runner import Controller,utc
c=Controller();w=c.root/'.autopilot/worktrees/P06'
with c.exclusive():
 s=c.reconcile();assert s['autopilot']['active_author'].get('ended_at') and s['autopilot']['operation']['consumed'];assert s['autopilot']['phases']['P06']['attempts']==1
 expected=(c.root/'.tools/p06-tega-expected-head.txt').read_text().strip();assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip()==expected
 assert not subprocess.check_output(['git','status','--porcelain','--','game','tools','assets/source_art/characters'],cwd=w,text=True).strip(),'Source must be clean before a frozen validation'
 import hashlib;job=c.root/'.tools/p06-qa-tega-job02.py';assert hashlib.sha256(job.read_bytes()).hexdigest()=='57209f171114553eff809d521ace003faae66ae7433d12d4d07b1cf3b080b72d';code=c.stage('P06/qa-tega-isolated-02',[sys.executable,str(job)],300,safe_retry=False,cwd=c.root)
 s=c.state();op=s['autopilot']['operation'];assert c.receipt(op);op['consumed']=True;s['autopilot']['phases']['P06']['checkpoint']='tega-validation-inspect';s['autopilot']['history'].append({'when':utc(),'event':'P06_TEGA_VALIDATION','operation':op['id'],'code':code,'phase_pass':False});c.persist(s);print(json.dumps({'code':code,'operation':op['id'],'receipt':op['receipt']}),flush=True);raise SystemExit(code)
