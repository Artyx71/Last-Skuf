from pathlib import Path
import ast,json,math,hashlib,tempfile,copy
O=Path(__file__).resolve().parent
source=(O/'source-snapshot/tools/p07_pacing.py').read_text();house=(O/'source-snapshot/autopilot/readiness.py').read_text()
ns={'json':json,'math':math,'hashlib':hashlib,'Path':Path,'digest':lambda p:hashlib.sha256(p.read_bytes()).hexdigest()}
a=ast.parse(house);exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.FunctionDef)and n.name=='strict_json'],type_ignores=[]),'frozen/readiness.py','exec'),ns)
a=ast.parse(source);nodes=[n for n in a.body if isinstance(n,ast.FunctionDef)and n.name in ['percentile','load_contract','validate_pins','visual_key','analyze']or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CONTEXTS'for t in n.targets)];exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen82b/p07_pacing.py','exec'),ns)
rawpath=O.parent/'qa-pacing-calibration-01/actual-evidence/raw.json';raw=json.loads(rawpath.read_text());out={'scope':'FROZEN_PURE_FUNCTION_CLOSURE_NO_ENGINE_OR_CONTROLLER','source_sha256':hashlib.sha256(source.encode()).hexdigest(),'raw_sha256':hashlib.sha256(rawpath.read_bytes()).hexdigest(),'cases':[]}
def attempt(name,func,expected):
 try:value=func();accepted=True;message=None
 except Exception as e:accepted=False;value=None;message=type(e).__name__+': '+str(e)
 out['cases'].append({'name':name,'accepted':accepted,'expected_acceptance':expected,'matches_expected':accepted is expected,'exception':message});return value
metrics=attempt('original_actual74_baseline',lambda:ns['analyze'](raw),True)
out['metrics']={k:v for k,v in metrics.items()if k not in ['progress_events','death_causes']}
bad=copy.deepcopy(raw);anchor=raw['requests'][0]
for row in bad['requests']:
 for key in ['input_usec','accepted_usec','accepted_tick','render_usec','render_draw']:row[key]=anchor[key]
 if row['kind']=='restart':row['death_usec']=anchor['input_usec']-1
 if row['kind']=='melee':row['contact_usec']=anchor['render_usec']+1
attempt('original_Q02_all48_anchor_rebinding',lambda:ns['analyze'](bad),False)
for name,mutate in [
 ('wrong_context_accepted_state',lambda b:b['requests'][6]['accepted_state'].update(context='yakuza')),
 ('missing_outgoing_contact',lambda b:b['contacts'].pop(0)),
 ('fabricated_restart_death',lambda b:b['requests'][5].update(death_usec=b['requests'][5]['death_usec']+1)),
 ('wrong_full_render_state',lambda b:b['requests'][0]['render_state'].update(frame=999)),
 ('duplicate_request_id',lambda b:b['requests'][1].update(id=1)),
 ('functional_check_false_with_failed_summary_zero',lambda b:b['checks'][0].update(passed=False)),
 ('request_id_boolean_instead_of_int',lambda b:b['requests'][0].update(id=True))]:
 b=copy.deepcopy(raw);mutate(b);attempt(name,lambda b=b:ns['analyze'](b),False)
with tempfile.TemporaryDirectory(prefix='pacing-qa02-')as td:
 p=Path(td)/'contract.json';q=Path(td)/'review.json';good={'schema':1,'scope':'H04_PILOT_ACCEPTANCE','source_inventory_sha256':{'TEST_ONLY':'a'},'limits':{'accept_p95_ms':34,'render_p95_ms':60,'frame_p95_ms':24,'frame_p99_ms':32,'restart_max_ms':1000}};goodblob=json.dumps(good).encode();review={'schema':1,'status':'PASS_COMPONENT','scope':'H04_CALIBRATION_CONTRACT','role':'LEAD_REVIEWER','independent_of_author':True,'reviewer':'TEST_ONLY_LEAD','must_fix':[],'contract_sha256':hashlib.sha256(goodblob).hexdigest()}
 def reset():p.write_bytes(goodblob);q.write_text(json.dumps(review))
 reset();value=attempt('valid_contract',lambda:ns['load_contract'](p,q,{'TEST_ONLY':'a'}),True);pins=value[1]
 original=Path.read_text;swaps=[];badgood=copy.deepcopy(good);badgood['limits']['frame_p95_ms']=25;badblob=json.dumps(badgood).encode()
 def transient(self,*args,**kwargs):
  if self==p:
   p.write_bytes(badblob)
   try:swaps.append(True);return original(self,*args,**kwargs)
   finally:p.write_bytes(goodblob)
  return original(self,*args,**kwargs)
 Path.read_text=transient
 try:value=attempt('original_Q01_readtext_swap_now_unused',lambda:ns['load_contract'](p,q,{'TEST_ONLY':'a'}),True);out['old_readtext_swap_count']=len(swaps);out['loaded_approved_limit']=value[0]['limits']['frame_p95_ms']
 finally:Path.read_text=original
 assert not swaps and value[0]==good
 for target in [p,q]:
  reset();value=ns['load_contract'](p,q,{'TEST_ONLY':'a'});target.write_bytes(target.read_bytes()+b'\n');attempt('changed_'+target.name+'_pin',lambda value=value:ns['validate_pins'](value[1]),False)
  reset();value=ns['load_contract'](p,q,{'TEST_ONLY':'a'});target.unlink();attempt('deleted_'+target.name+'_pin',lambda value=value:ns['validate_pins'](value[1]),False)
 reset();q.write_text(json.dumps(review).replace('"status": "PASS_COMPONENT"','"status": "FAIL", "status": "PASS_COMPONENT"'));attempt('original_Q01_duplicate_FAIL_PASS_status',lambda:ns['load_contract'](p,q,{'TEST_ONLY':'a'}),False)
 reset();p.write_text(json.dumps(good).replace('"schema": 1','"schema": true'));review['contract_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();q.write_text(json.dumps(review));attempt('boolean_contract_schema',lambda:ns['load_contract'](p,q,{'TEST_ONLY':'a'}),False)
(O/'fixed-binding-results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out,ensure_ascii=False))
