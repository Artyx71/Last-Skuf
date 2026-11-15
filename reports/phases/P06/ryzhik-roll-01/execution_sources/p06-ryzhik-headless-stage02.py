import sys,subprocess,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'autopilot'))
from runner import Controller,utc
c=Controller();w=c.root/'.autopilot/worktrees/P06'
with c.exclusive():
 s=c.reconcile();assert s['autopilot']['active_author'].get('ended_at') and s['autopilot']['operation']['consumed'];assert s['autopilot']['phases']['P06']['attempts']==1
 assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip()=='a33581e430109de3d80fcd517aaafbc76d6f3cd6'
 code=c.stage('P06/ryzhik-headless-02',[sys.executable,str(c.root/'.tools/p06-ryzhik-headless-job02.py')],240,safe_retry=False,cwd=w)
 s=c.state();op=s['autopilot']['operation'];assert c.receipt(op);op['consumed']=True;s['autopilot']['phases']['P06']['checkpoint']='ryzhik-validation-inspect';s['autopilot']['history'].append({'when':utc(),'event':'P06_RYZHIK_VALIDATION','operation':op['id'],'code':code,'phase_pass':False});c.persist(s);print(json.dumps({'code':code,'operation':op['id'],'receipt':op['receipt']}),flush=True);raise SystemExit(code)
