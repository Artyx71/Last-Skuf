import json,sys
from pathlib import Path
r=Path.cwd();w=r/'.autopilot/worktrees/P07';sys.path.insert(0,str(r/'autopilot'))
from runner import Controller,utc
c=Controller()
with c.exclusive():
 s=c.reconcile();a=s['autopilot'];p=a['phases']['P07'];assert a['active_author']['ended_at'] and p['status']=='PENDING' and p['attempts']==0 and a['operation']['consumed']
 lead_path=r/'reports/pre_p07/lead-bonus-live-03/decision.json'
 import hashlib
 assert hashlib.sha256(lead_path.read_bytes()).hexdigest()=='017e8bda184be63d5dedcfe70543ce5c75231f97b1e4a7d29b66b89c4612cfe1'
 decision=json.loads(lead_path.read_text());assert decision['stop_broad_retry_loop'] and decision['review_cycle']==3
 p=a['phases']['P07'];assert 'finite_legacy_supplement' not in p
 p['bonus_live_review_escalation']={'review_cycles':3,'broad_auto_loop':'STOPPED','Lead':str(lead_path.relative_to(r)),'Lead_sha256':'017e8bda184be63d5dedcfe70543ce5c75231f97b1e4a7d29b66b89c4612cfe1','permitted_scope':'ONE_FINITE_OLD_NATIVE_REPLAY_FIXTURE_SUPPLEMENT','Readiness_or_phase_approval':False}
 p['finite_legacy_supplement']={'started_at':utc(),'max_executions':1,'no_full_pipeline_retry':True};c.persist(s)
 code=c.stage('PRE_P07/H05-finite-legacy-native-supplement-01',[sys.executable,str(w/'tools/p07_legacy_startup_probe.py'),'--runtime-evidence',str(w/'reports/pre_p07/bonus-live-adapter-03'),'--output',str(w/'reports/pre_p07/bonus-legacy-supplement-01')],240,safe_retry=False,cwd=w)
 s=c.state();a=s['autopilot'];op=a['operation'];receipt=c.receipt(op)
 if receipt is not None:
  assert receipt['exit_code']==code;op['consumed']=True
  p=a['phases']['P07'];p['preproduction_checkpoint']='H05_FINITE_LEGACY_SUPPLEMENT_INSPECT_AND_INDEPENDENT_ADJUDICATION' if code==0 else 'H05_FINITE_SUPPLEMENT_FAILED_RENEWED_ESCALATION_REQUIRED'
  s['next_action']='Inspect actual H05 pilot receipt/raw/results. Independent QA/Lead required; no production integration/fullReadiness/P07 permission.'
  a['history'].append({'when':utc(),'event':'H05_FINITE_SUPPLEMENT_TERMINAL_CONSUMED','operation':op['id'],'exit_code':code});c.persist(s)
  for root in [r,w]:
   path=root/'reports/phases/P07/resume/decision.json';d=json.loads(path.read_text());d.update(checkpoint=p['preproduction_checkpoint'],next_action=s['next_action'],last_consumed_operation=op,current_author_kind='AUTHOR_RELEASED_ACTUAL_PILOT_RECEIPT_INSPECTION_REQUIRED');path.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'exit_code':code,'operation':op['id'],'consumed':op.get('consumed'),'receipt':op['receipt']}),flush=True)
