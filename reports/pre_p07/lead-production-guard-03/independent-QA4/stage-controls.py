"""Independent staged guard fixtures. All Git/state/merge requests are test-only."""
from pathlib import Path
import sys,json,copy,tempfile,subprocess,shutil
O=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(O/'isolated-source/tools/tests'));import test_production_readiness as tests
from readiness import require_p07_production,require_p07_review_acceptance,ReadinessBlocked,OBLIGATIONS
from github import validate_review,guarded_merge
from runner import load
rows=[]
def fixture(name,fn):
 t=tests.ProductionReadinessTests();t.setUp()
 try:row={'name':name,'scope':'TEMP_GIT_FAKE_APPROVAL_ONLY'};row.update(fn(t));rows.append(row)
 finally:t.tearDown()
def prod(t,mutate):
 mutate(t);t.publish();before=copy.deepcopy(t.state)
 try:result=require_p07_production(t.root,t.state);accepted=True;error=None
 except ReadinessBlocked as e:accepted=False;error=str(e)
 return {'accepted':accepted,'error':error,'state_unchanged':before==t.state}
fixture('open_HIGH_future_obligations_allow_mass_entry',lambda t:prod(t,lambda t:None))
for cap in ['full_p06','safe_handoff','navigation_pilot','audio_playback_pipeline','pacing_instrumentation','secret_integration_contract']:
 fixture('missing_capability_'+cap,lambda t,k=cap:prod(t,lambda t:t.ready['preproduction_capabilities'].pop(k)))
fixture('design_stage_string_cannot_skip_missing_capability',lambda t:prod(t,lambda t:(t.state['autopilot'].update(production_stage='DESIGN_ONLY'),t.ready['preproduction_capabilities'].pop('full_p06'))))
fixture('unknown_future_enforcement_stage',lambda t:prod(t,lambda t:t.ready['future_acceptance_obligations']['chapter_delivery_21'].update(enforce_at='AFTER_MERGE')))
fixture('missing_future_obligation',lambda t:prod(t,lambda t:t.ready['future_acceptance_obligations'].pop('secret_delivery_7')))
fixture('unknown_extra_future_obligation',lambda t:prod(t,lambda t:t.ready['future_acceptance_obligations'].update(UNKNOWN=copy.deepcopy(next(iter(t.ready['future_acceptance_obligations'].values()))))))
def review_case(t,mutate):
 review=t.acceptance_review();review.update(base_branch='main',base_sha='b'*40,next_action='TEST_ONLY',artistic_audio_acceptance=None);mutate(review);before=copy.deepcopy(t.state);errors=validate_review(t.root,review,t.head,'P07');return {'accepted':not errors,'errors':errors,'state_unchanged':before==t.state}
fixture('unknown_inline_scope',lambda t:review_case(t,lambda r:r['production_acceptance'].update(scope='P07_DESIGN_ONLY')))
fixture('boolean_inline_schema',lambda t:review_case(t,lambda r:r['production_acceptance'].update(schema=True)))
fixture('missing_closure_ID',lambda t:review_case(t,lambda r:r['production_acceptance']['closed_obligations'].pop('secret_delivery_7')))
fixture('extra_closure_ID',lambda t:review_case(t,lambda r:r['production_acceptance']['closed_obligations'].update(UNKNOWN={'status':'PASS','evidence':r['evidence']})))
fixture('stale_inline_head',lambda t:review_case(t,lambda r:r['production_acceptance'].update(reviewed_commit='f'*40)))
fixture('stale_inline_ReadinessSHA',lambda t:review_case(t,lambda r:r['production_acceptance'].update(readiness_sha256='f'*64)))
fixture('closure_status_FAIL',lambda t:review_case(t,lambda r:r['production_acceptance']['closed_obligations']['new_audio_acceptance'].update(status='FAIL')))
fixture('missing_hashed_closure_evidence',lambda t:review_case(t,lambda r:r['production_acceptance']['closed_obligations']['new_audio_acceptance'].update(evidence=[])))
fixture('valid_inline_full_closure_control',lambda t:review_case(t,lambda r:None))
# Actual second merge-gate re-read; API request callback is a zero-network spy.
def second_gate(t,mutation):
 review=t.acceptance_review();review.update(base_branch='main',base_sha='b'*40);calls=[];sent=[]
 def snapshot(*_):
  calls.append(1)
  if len(calls)==2:mutation(t,review)
  return t.merge_view()
 result=guarded_merge(t.root,4,{},review,'P07',snapshot,lambda *args:sent.append(args));assert result['status']=='BLOCKED' and len(calls)==2 and not sent
 return {'status':result['status'],'snapshot_count':len(calls),'request_count':len(sent),'blockers':result['blockers'],'zero_real_network':True}
def mutate_Readiness(t,review):
 t.ready['future_acceptance_obligations']['new_audio_acceptance']['requirement']='new independently changed TEST criterion';t.publish();tests.write(t.root/'automation/phase_state.json',t.state)
fixture('second_snapshot_changed_ReadinessSHA_blocks_before_PUT',lambda t:second_gate(t,mutate_Readiness))
fixture('second_snapshot_changed_content_evidence_blocks_before_PUT',lambda t:second_gate(t,lambda t,r:(t.root/r['evidence'][0]['path']).write_text('changed TEST proof')))
# Linked worktree has a genuinely newer P07 content commit; canonical P06 root remains frozen.
def linked(t):
 review=t.acceptance_review();before=copy.deepcopy(t.state)
 with tempfile.TemporaryDirectory(dir=O/'tmp') as td:
  work=Path(td)/'P07';subprocess.run(['git','worktree','add','-b','qa-p07-stage',str(work),t.head],cwd=t.root,check=True,capture_output=True)
  try:
   (work/'game/P07content.gd').write_text('TEST_ONLY new P07 content\n');subprocess.run(['git','add','game'],cwd=work,check=True,capture_output=True);subprocess.run(['git','-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','-qm','TEST_ONLY P07 implementation'],cwd=work,check=True,capture_output=True);head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=work,text=True).strip();shutil.copytree(t.root/'reports',work/'reports');tests.write(work/'automation/phase_state.json',{'STALE_WORK_COPY':True});review['reviewed_commit']=head;review['production_acceptance']['reviewed_commit']=head
   accepted=require_p07_review_acceptance(work,review,head);assert accepted and t.state==before and head!=t.head
   t.state['autopilot']['production_gates'].pop('readiness');tests.write(t.root/'automation/phase_state.json',t.state);errors=validate_review(work,review,head,'P07');assert errors
   return {'new_P07_commit_differs_from_P06':True,'valid_canonical_accepted':True,'stale_WORK_state_ignored':True,'canonical_readiness_removed_then_BLOCKED':bool(errors),'no_unintended_state_reset':True}
  finally:subprocess.run(['git','worktree','remove','--force',str(work)],cwd=t.root,check=True,capture_output=True)
fixture('linked_new_P07_head_and_canonical_ROOT_authority',linked)
# Malformed review inputs: collect observations without pretending parser rejection.
def malformed_findings(t):return review_case(t,lambda r:r.update(findings={}))
def duplicate_raw_key(t):
 review=t.acceptance_review();review.update(base_branch='main',base_sha='b'*40,next_action='TEST_ONLY',artistic_audio_acceptance=None);original=json.dumps(review);key='"new_audio_acceptance": ';bad='"new_audio_acceptance": {"status":"FAIL","evidence":[]}, '+key;raw=original.replace(key,bad,1);assert raw!=original;path=t.root/'TEST_ONLY_DUPLICATE_VERDICT.json';path.write_text(raw);parsed=load(path,{});errors=validate_review(t.root,parsed,t.head,'P07');sent=[];calls=[]
 def snapshot(*_):calls.append(1);return t.merge_view()
 def request(*args):sent.append(args);return {'merged':False,'message':'TEST_ONLY spy never merges'}
 result=guarded_merge(t.root,4,{},parsed,'P07',snapshot,request);return {'raw_duplicate_closure_keys':2,'contradictory_first_status':'FAIL','parsed_last_status':parsed['production_acceptance']['closed_obligations']['new_audio_acceptance']['status'],'phase_validation_errors':errors,'snapshot_count':len(calls),'mock_request_count':len(sent),'mock_request_methods':[x[1] for x in sent],'guarded_result':result['status'],'zero_real_network':True,'expected':'REJECT_DUPLICATE_CLOSURE_BEFORE_ANY_PUT'}
(O/'stage-control-results.json').write_text(json.dumps({'schema':1,'records':rows,'actual_phase_or_GitHub_actions':False},indent=2)+'\n');print(json.dumps(rows,indent=2))
