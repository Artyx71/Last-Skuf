"""Verify the immutable FAILED8/13 attempt. Read-only hashes/logs; not an engine/rerun."""
from pathlib import Path
import json,hashlib,re,shutil
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/full-native-current-source-01';ID='8e8ab4a27ccd47ebacf5a66dd3b6780c';J=R/'.autopilot/jobs'/ID
cache={}
def sha(p):
 p=p.resolve()
 if p not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
  cache[p]=h.hexdigest()
 return cache[p]
def read(p):return json.loads(p.read_text())
receipt=read(J/'receipt.json');job=read(J/'input.json');state=read(R/'automation/phase_state.json');phase=state['autopilot']['phases']['P06'];history=[x for x in state['autopilot']['history'] if x.get('operation')==ID];v=read(P/'validation.json');rows=read(P/'commands.json');plan=read(P/'plan.json');before=read(P/'source_hashes_before.json');after=read(P/'source_hashes_after.json');error=re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL:|ObjectDB instances were leaked|resources still in use')
checks={'worker_receipt_actual_failed1':receipt.get('operation')==ID and type(receipt.get('exit_code')) is int and receipt['exit_code']==1,'worker_log_actual_hash_matches':sha(J/'output.log')==receipt.get('log_sha256'),'worker_argv_exact_hash':job['argv_sha256']==receipt['argv_sha256']==hashlib.sha256(json.dumps(job['argv']).encode()).hexdigest(),'completion_event_matches_failed1':any(x.get('event')=='P06_CURRENT_FULL_NATIVE_PIPELINE_COMPLETED' and x.get('code')==1 and x.get('phase_approval') is False for x in history),'canonical_phase_retains_actual_validation_binding':phase.get('native_full_validation',{}).get('operation')==ID and phase['native_full_validation']['report_sha256']==sha(P/'validation.json'),'actual_first7pass_then_pasha_fail_stop':len(rows)==8 and len(plan)==13 and [x['name'] for x in rows]==[x['name'] for x in plan[:8]] and all(x['exit_code']==0 and x['passed'] is True for x in rows[:7]) and rows[7]['name']=='pasha' and rows[7]['exit_code']==1 and rows[7]['passed'] is False,'aggregate_failure_and_no_approvals':v.get('passed') is False and all(v.get(k) is False for k in ['phase_approval','merge_approval','native_acceptance_approval']),'source_and_HEAD_unchanged_during_actual_attempt':before==after and v.get('source_unchanged') is True and v.get('source_head')==v.get('head_after')=='beb30f319b2cf86a1799672ed24837c4640a9bee','no_remaining_or_unexpected_children_all8':all(bool(x.get('cleanup_events')) and all(e.get('unexpected_live_children') is False and e.get('remaining_live_children')==[] for e in x['cleanup_events']) for x in rows)}
# Current disk is observational: author may legitimately start a new candidate after receipt.
disk_delta=[k for k,d in before.items() if not (W/k).is_file() or sha(W/k)!=d]
artifacts=[];details=[]
for i,row in enumerate(rows):
 name=row['name'];folder=P/name;child=read(folder/'validation.json');log=P/'logs'/(name+'.log');txt=log.read_text(errors='replace');record={'name':name,'validation_sha256':sha(folder/'validation.json'),'wrapper_exit':row['exit_code'],'actual_command_seconds_not_FPS':row['seconds'],'argv_matches_plan':row['argv']==plan[i]['argv'],'log_hash_matches':sha(log)==row['log_sha256'],'log_final_exit_matches':txt.splitlines()[-1]=='exit_code='+str(row['exit_code']),'log_has_errors':bool(error.search(txt)),'child_sources_unchanged':child.get('source_unchanged'),'child_phase_approval':child.get('phase_approval'),'checks':child.get('checks',{'passed':child.get('checks_passed'),'total':child.get('checks_total')}),'actual_captures':child.get('actual_captures'),'commands':child['commands'],'movie_path':child.get('movie_path')}
 for item in child['artifacts']:
  p=W/item['path'];exists=p.is_file();digest=sha(p) if exists else None;artifacts.append({'stage':name,'path':item['path'],'expected':item['sha256'],'actual':digest,'passed':exists and digest==item['sha256']})
 details.append(record)
checks['all_actual_artifact_inventory_hashes_match']=all(x['passed'] for x in artifacts)
checks['all_plan_argv_and_wrapper_log_hashes_match']=all(x['argv_matches_plan'] and x['log_hash_matches'] and x['log_final_exit_matches'] for x in details)
# Retain small exact raw authoritative proofs; preserve original WORK files.
for name in ['input.json','receipt.json','started.json','output.log']:
 dst=Q/'actual-worker'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(J/name,dst)
for name in ['validation.json','commands.json','source_hashes_after.json']:
 shutil.copyfile(P/name,Q/'inputs'/name)
helper=R/'.tools/p06-full-native-current-stage01.py';shutil.copyfile(helper,Q/'inputs/actual-canonical-stage-helper.py.txt')
(Q/'completion-history-binding.json').write_text(json.dumps({'event':history,'native_full_validation':phase.get('native_full_validation'),'active_phase':state.get('active_phase'),'global_attempts':state.get('attempts'),'P06_autopilot_attempts':phase.get('attempts'),'consumption_evidence':'Exact helper persists consumed=True and completion event together; later canonical operation has advanced. Original job input consumed=False is creation-time evidence, not current state.'},indent=2)+'\n')
result={'scope':'EVIDENCE_INTEGRITY_OF_FAILED_NATIVE_ATTEMPT_NOT_PIPELINE_PASS','checks':checks,'evidence_integrity_verified':all(checks.values()),'actual_pipeline_passed':False,'stages_completed':8,'stages_planned':13,'first7_passed':True,'stage8':'PASHA_MOVIE4ASSERTIONS_FAILED','remaining5':'NOT_RUN','postreceipt_current_disk_delta_from_original_frozen_map':disk_delta,'artifact_records':artifacts,'stage_records':details,'unique_files_hashed':len(cache),'phase_approval':False,'Godot_Controller_or_runner_invoked':False};out=Q/'failed-attempt-integrity.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'evidence_integrity_verified':result['evidence_integrity_verified'],'failed_integrity_checks':[k for k,v in checks.items() if not v],'actual_pipeline_passed':False,'artifacts':len(artifacts),'current_disk_delta':disk_delta,'unique_files_hashed':len(cache)}))
