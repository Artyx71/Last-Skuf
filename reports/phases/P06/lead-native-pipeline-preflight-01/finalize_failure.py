from pathlib import Path
import json,hashlib,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');O=R/'reports/phases/P06/lead-native-pipeline-preflight-01';Q=R/'reports/phases/P06/qa-native-pipeline-preflight-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert sha(Q/'decision.json')=='57b732d7e29566a138a82623dab91ae604a118b69c9a9b9af495cb04b02c63e2';q=read(Q/'decision.json');assert q['status']=='FAIL_COMPONENT' and q['actual_original_source_sha256']==sha(O/'frozen-454e-verify_p06.py')==read(O/'probe-input.json')['sha256']
refs=[]
for e in read(Q/'artifacts.json')['files']:
 p=Q/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'];refs.append({'ROOT_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
D=O/'independent-QA01';D.mkdir(exist_ok=True)
for n in ['decision.json','review.md','artifacts.json','FINAL_HASHES.json']:
 if (Q/n).exists():shutil.copyfile(Q/n,D/n);refs.append({'ROOT_relative_path':str((Q/n).relative_to(R)),'sha256':sha(Q/n),'bytes':(Q/n).stat().st_size})
put('QA01-reference-bindings.json',{'files':refs,'actual_source_SHA_crosschecked':True,'QA_initial_WIP_snapshot_not_used_as_original':True})
f=read(O/'findings-DRAFT.json');f['independent_QA_crossrefs']={'NPIPE-L01':'PIPE-Q01','NPIPE-L02':'PIPE-Q02'};put('findings.json',f);(O/'findings-DRAFT.json').unlink()
s=(O/'review-DRAFT.md').read_text().replace('# Native P06 pipeline preflight — frozen454e (draft awaiting immutable QA01)','# Native P06 pipeline preflight — frozen454e independent Lead FAIL').replace('Proposed **FAIL_COMPONENT**, no full native execution permission.','**FAIL_COMPONENT**, no full native execution permission.')
s+='\nIndependent QA01 is now immutable FAIL_COMPONENT57b732d7…, independently read with all30 portable files/hash bindings checked. It corroborates both process/report findings and adds its own4 parser controls/8 unsafe acceptances. QA transparently distinguishes its first6232 intermediate-WIP copy/failed AST extraction from the authoritative0357 original; this Lead uses its own exact frozen0357 source and actual original fixtures throughout. The first QA instrument failure is not a product result. The independent baseline15-pair QA acceptance is a different component and is not reopened.\n'
(O/'review.md').write_text(s);(O/'review-DRAFT.md').unlink()
put('metrics.json',{'schema':1,'frozen_original_commit':'454e5329b517f461e899760e0ba43156393f555c','declared_native_stages':13,'real_full_pipeline_runs':0,'own_process_leak_reproductions':2,'own_fixture_children_cleaned':2,'own_Godot_or_Controller_runs':0,'own_report_fixture_cases':7,'own_unsafe_report_acceptances':4,'QA_original_parser_controls':4,'QA_unsafe_report_acceptances':8,'QA_portable_files_verified':30,'new_fixed11_candidate_review':'SEPARATE_PENDING_NOT_OLD_FAIL_OVERRIDE'})
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['artifacts.json','decision.json','FINAL_HASHES.json']:
  assert not p.is_symlink();files.append({'path':str(p.relative_to(O)),'sha256':sha(p),'bytes':p.stat().st_size})
put('artifacts.json',{'schema':1,'base':'manifestdirectory','files':files,'test_only_invalid_JSON_fixtures_included':True,'no_Game_or_engine_orprivatephoto_copy':True})
put('decision.json',{'schema':1,'role':'INDEPENDENT_LEAD','status':'FAIL_COMPONENT','scope':'Original454e native pipeline launcher/report preflight only','frozen_commit':'454e5329b517f461e899760e0ba43156393f555c','frozen_original_source_sha256':sha(O/'frozen-454e-verify_p06.py'),'must_fix':['NPIPE-L01','NPIPE-L02'],'independent_QA_decision_sha256':sha(Q/'decision.json'),'permission_to_execute_full_native_pipeline':False,'fixed11_candidate_approval':False,'phase_approval':False,'full_P06_approval':False,'merge_approval':False,'P07_approval':False,'ROOT_installation_or_handoff_approval':False,'formal_phase_attempt_consumed':False,'native_13_execution_performed':False,'next_action':'Separate source-frozen fixclosure covering process ownership on success/nonzero/timeout and strict typed JSON. No full native engine run before independentQA+Lead GO.','proofs':{n:sha(O/n) for n in ['review.md','findings.json','metrics.json','artifacts.json','own-probe-result.json','silent-orphan-result.json','source-freeze.json','declared-13stage-plan.json','QA01-reference-bindings.json']},'Game_tools_Controller_state_or_Git_mutations_by_reviewer':0})
put('FINAL_HASHES.json',{n:sha(O/n) for n in ['decision.json','review.md','artifacts.json','findings.json','metrics.json']})
for e in files:assert sha(O/e['path'])==e['sha256']
print(json.dumps({'status':'FAIL_COMPONENT','files':len(files),'bytes':sum(e['bytes'] for e in files),'hashes':read(O/'FINAL_HASHES.json')},indent=2))
