"""Single ROOT P07 author lease; the canonical Controller remains authority."""
import json,os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'autopilot'))
from runner import Controller,utc
from readiness import require_p07_production
c=Controller()
with c.exclusive():
 s=c.reconcile();a=s['autopilot'];p=a['phases']['P07']
 assert c.config['stop_after_phase']=='P07'
 assert a['operation']['consumed'] and (not a.get('active_author') or a['active_author'].get('ended_at'))
 c.prerequisite('P07');gate=require_p07_production(ROOT,s)
 if p['status']=='PENDING':
  assert p['attempts']==0
  p.update(status='IMPLEMENTING',attempts=1,checkpoint='implementation')
 else:
  assert p['status']=='IMPLEMENTING' and p['attempts']==1 and p['checkpoint']=='implementation'
 a['active_author']={'pid':os.getpid(),'phase':'P07','kind':'SOLE_HOST_P07_PRODUCTION_AUTHOR','started_at':utc(),'safe_retry':False,'checkpoint':'P07_CH02_A_TRUSTED_PRIME_CHAPTER_INTEGRATION'}
 a['history'].append({'when':utc(),'event':'P07_SOLE_HOST_AUTHOR_STARTED_AFTER_FULL_READINESS','formal_attempt':p['attempts'],'readiness':a['production_gates']['readiness'],'mission_specs':gate['mission_specs']})
 s.update(active_phase='P07',status='IMPLEMENTING',next_action='SequentialP07 CH02 trustedprimehost/controller/scene integration; preserve existingCore/styles/nav/H05. AllfourfutureHIGHOPEN; noP07PASS/merge/release fromReadiness.')
 c.persist(s)
 proof={'when':utc(),'actual_fresh_Controller_prerequisite':'PASS','actual_guard':gate,'config_stop_after_phase':'P07','P07_formal_attempt':1,'ROOT_Game_unchanged_P06':True,'parallel_executor':False,'phase_PASS_or_merge':False}
 proof_path=ROOT/'reports/pre_p07/production-entry-01/fresh-controller.json'
 if proof_path.exists(): proof_path=proof_path.with_name('fresh-controller-author-resume-'+str(os.getpid())+'.json')
 proof_path.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
 print('SOLE_P07_AUTHOR_LEASE_HELD pid='+str(os.getpid()),flush=True)
 for line in sys.stdin:
  command=json.loads(line);s=c.state();a=s['autopilot'];assert a['active_author']['pid']==os.getpid()
  if command['event']=='checkpoint':
   a['active_author'].update(checkpoint=command['name'],updated_at=utc());s['next_action']=command['next_action'];c.persist(s);print('P07_CHECKPOINT_SAVED',flush=True)
  elif command['event']=='release':
   a['active_author'].update(ended_at=utc(),outcome=command['reason']);c.persist(s);print('P07_AUTHOR_RELEASED',flush=True);break
  else:raise ValueError('Only checkpoint/release; author cannot issue phase/merge PASS')
 else:
  s=c.state();s['autopilot']['active_author'].update(ended_at=utc(),outcome='INTERRUPTED_INSPECT_WORK_BEFORE_CONTINUING');c.persist(s)
