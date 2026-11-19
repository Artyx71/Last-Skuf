from pathlib import Path
import ast,json,math,hashlib,tempfile,copy
O=Path(__file__).resolve().parent
source=(O/'source-snapshot/tools/p07_pacing.py').read_text()
module=ast.parse(source);selected=ast.Module(body=[n for n in module.body if isinstance(n,ast.FunctionDef)and n.name in ['percentile','load_contract','analyze']],type_ignores=[])
ns={'json':json,'math':math,'digest':lambda p:hashlib.sha256(p.read_bytes()).hexdigest()};exec(compile(selected,'frozen85ca/p07_pacing.py','exec'),ns)
R=O.parents[2];raw_path=R/'.autopilot/worktrees/P07/reports/pre_p07/pacing-baseline-01/raw.json'
raw=json.loads(raw_path.read_text());results={'scope':'PURE_FROZEN_FUNCTION_PROBES_NO_ENGINE_OR_CONTROLLER','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'raw_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),'cases':[]}
x=ns['analyze'](raw);results['cases'].append({'name':'actual_baseline_control','accepted':True,'metrics':{k:v for k,v in x.items()if k not in ['progress_events','death_causes']}})
bad=copy.deepcopy(raw);anchor=raw['requests'][0]
for row in bad['requests']:
 for key in ['input_usec','accepted_usec','accepted_tick','render_usec','render_draw']:row[key]=anchor[key]
 if row['kind']=='restart':row['death_usec']=anchor['input_usec']-1
 if row['kind']=='melee':row['contact_usec']=anchor['render_usec']+1
try:
 x=ns['analyze'](bad);results['cases'].append({'name':'all48requests_bound_to_first_yakuza_observation_context_state_contact_death_mismatch','accepted':True,'metrics':{k:x[k]for k in ['input_accept_ms','input_render_ms','death_to_control_ms','accepted_to_contact_ms']},'wrong_context_bound_requests':sum(r['context']!='yakuza'for r in bad['requests'])})
except Exception as e:results['cases'].append({'name':'request_rebinding','accepted':False,'exception':str(e)})
with tempfile.TemporaryDirectory(prefix='qa-pacing-')as td:
 p=Path(td)/'contract.json';q=Path(td)/'review.json';good={'scope':'H04_PILOT_ACCEPTANCE','source_inventory_sha256':{'TEST_ONLY':'a'},'limits':{'accept_p95_ms':34,'render_p95_ms':60,'frame_p95_ms':24,'frame_p99_ms':32,'restart_max_ms':1000}}
 good_blob=json.dumps(good).encode();p.write_bytes(good_blob);review={'status':'PASS_COMPONENT','scope':'H04_CALIBRATION_CONTRACT','role':'LEAD_REVIEWER','independent_of_author':True,'reviewer':'TEST_ONLY_LEAD','must_fix':[],'contract_sha256':hashlib.sha256(good_blob).hexdigest()};q.write_text(json.dumps(review));assert ns['load_contract'](p,q,{'TEST_ONLY':'a'})==good
 # Simulate a transient write only during the actual parse read, restored before hash.
 bad_contract=copy.deepcopy(good);bad_contract['limits']['frame_p95_ms']=25;bad_blob=json.dumps(bad_contract).encode();original=Path.read_text;swaps=[]
 def transient_read(self,*args,**kwargs):
  if self==p:
   p.write_bytes(bad_blob)
   try:value=original(self,*args,**kwargs);swaps.append(True);return value
   finally:p.write_bytes(good_blob)
  return original(self,*args,**kwargs)
 Path.read_text=transient_read
 try:
  loaded=ns['load_contract'](p,q,{'TEST_ONLY':'a'});results['cases'].append({'name':'contract_hashed_original_but_parsed_unapproved_limit','accepted':True,'approved_limit':24,'actual_loaded_limit':loaded['limits']['frame_p95_ms'],'disk_restored_original':p.read_bytes()==good_blob,'parse_sha256':hashlib.sha256(bad_blob).hexdigest(),'approved_sha256':hashlib.sha256(good_blob).hexdigest()})
 except Exception as e:results['cases'].append({'name':'contract_same_byte','accepted':False,'exception':str(e)})
 finally:Path.read_text=original
 text=json.dumps(review);q.write_text(text.replace('"status": "PASS_COMPONENT"','"status": "FAIL", "status": "PASS_COMPONENT"'))
 try:ns['load_contract'](p,q,{'TEST_ONLY':'a'});results['cases'].append({'name':'contradictory_duplicate_review_status_FAIL_then_PASS','accepted':True})
 except Exception as e:results['cases'].append({'name':'duplicate_review','accepted':False,'exception':str(e)})
(O/'binding-probe-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False))
