import json,sys
from pathlib import Path
r=Path.cwd();w=r/'.autopilot/worktrees/P07';sys.path.insert(0,str(r/'autopilot'))
from runner import Controller,utc
c=Controller()
with c.exclusive():
 s=c.reconcile();a=s['autopilot'];p=a['phases']['P07'];assert a['active_author']['ended_at'] and p['status']=='PENDING' and p['attempts']==0 and a['operation']['consumed']
 code=c.stage('PRE_P07/H05-independent-namespace-witness-01',[sys.executable,str(r/'.tools/pre-p07-h05-namespace-witness.py')],180,safe_retry=False,cwd=r)
 s=c.state();a=s['autopilot'];op=a['operation'];receipt=c.receipt(op)
 if receipt is not None:
  assert receipt['exit_code']==code;op['consumed']=True
  p=a['phases']['P07'];p['preproduction_checkpoint']='H05_NAMESPACE_WITNESS_INSPECT' if code==0 else 'H05_NAMESPACE_WITNESS_EXECUTION_FAILURE'
  s['next_action']='Inspect actual H05 pilot receipt/raw/results. Independent QA/Lead required; no production integration/fullReadiness/P07 permission.'
  a['history'].append({'when':utc(),'event':'H05_QA_NAMESPACE_WITNESS_TERMINAL_CONSUMED','operation':op['id'],'exit_code':code});c.persist(s)
  for root in [r,w]:
   path=root/'reports/phases/P07/resume/decision.json';d=json.loads(path.read_text());d.update(checkpoint=p['preproduction_checkpoint'],next_action=s['next_action'],last_consumed_operation=op,current_author_kind='AUTHOR_RELEASED_ACTUAL_PILOT_RECEIPT_INSPECTION_REQUIRED');path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'exit_code':code,'operation':op['id'],'consumed':op.get('consumed'),'receipt':op['receipt']}),flush=True)
