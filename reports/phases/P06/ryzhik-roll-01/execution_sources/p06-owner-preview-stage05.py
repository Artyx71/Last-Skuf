import sys,subprocess,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'autopilot'))
from runner import Controller,utc
c=Controller();w=c.root/'.autopilot/worktrees/P06';expected='8ad1729984321fbd646e96bbe9762a8c4cca689e'
with c.exclusive():
 s=c.reconcile();assert s['autopilot']['active_author'].get('ended_at') and s['autopilot']['operation']['consumed'];assert s['autopilot']['phases']['P06']['status']=='IMPLEMENTING' and s['autopilot']['phases']['P06']['attempts']==1
 head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip();assert head==expected
 assert not subprocess.check_output(['git','status','--porcelain','--','game','tools','assets/source_art/characters'],cwd=w,text=True).strip(),'Source must be frozen and clean'
 for name in ['art-ryzhik-roll-02','gameplay-ryzhik-roll-02','qa-ryzhik-roll-02']:
  p=c.root/'reports/phases/P06'/name/'decision.json';d=json.loads(p.read_text());heads=[d[k] for k in ['source_head','frozen_commit'] if k in d];assert d['status']=='PASS_COMPONENT' and heads and all(h==expected for h in heads) and d['phase_approval'] is False,(name,'Wrong subreview')
 code=c.stage('P06/owner-preview-20261115-05',[sys.executable,str(c.root/'.tools/p06-owner-preview-job05.py')],420,safe_retry=False,cwd=w)
 s=c.state();op=s['autopilot']['operation'];assert c.receipt(op);op['consumed']=True;s['autopilot']['phases']['P06']['checkpoint']='ryzhik-DEV05-Lead-component-review' if code==0 else 'owner-preview05-inspect-failure';s['autopilot']['history'].append({'when':utc(),'event':'P06_OWNER_PREVIEW05_COMPLETE','operation':op['id'],'code':code,'source_head':head,'phase_pass':False});c.persist(s);print(json.dumps({'code':code,'operation':op['id'],'receipt':op['receipt'],'phase_approval':False}),flush=True);raise SystemExit(code)
