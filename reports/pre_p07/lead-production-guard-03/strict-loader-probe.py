"""Pure exact frozen functions + read-only compatibility; no controller/Git/network."""
from pathlib import Path
import ast,hashlib,json,tempfile
O=Path(__file__).resolve().parent;ROOT=O.parents[2]
readiness=O/'reviewed-source/autopilot/readiness.py';runner=O/'reviewed-source/autopilot/runner.py'
space={'json':json,'Path':Path}
for source,names in [(readiness,['strict_json']),(runner,['Blocked','load'])]:
 tree=ast.parse(source.read_text());nodes=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
 exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),space)
cases=[('contradictory_top_status','{"status":"FAIL","status":"PASS"}',True),('contradictory_nested_closure','{"closed_obligations":{"new_audio_acceptance":{"status":"FAIL"},"new_audio_acceptance":{"status":"PASS"}}}',True),('same_decoded_unicode_key','{"a":1,"\\u0061":2}',True),('NaN_constant','{"x":NaN}',True),('Infinity_constant','{"x":Infinity}',True),('ordinary_unique_control','{"status":"PASS","TEST_ONLY":true}',False)]
rows=[]
with tempfile.TemporaryDirectory(prefix='strict-loader-only-',dir=O) as directory:
 p=Path(directory)/'TEST_ONLY.json'
 for name,raw,expect in cases:
  p.write_text(raw)
  try:space['load'](p,{});blocked=False;error=None
  except space['Blocked'] as e:blocked=True;error=str(e.__cause__)
  assert blocked==expect,name
  rows.append({'name':name,'blocked':blocked,'expected_block':expect,'correct':True,'cause':error})
compat=[]
paths=['automation/phase_state.json','autopilot/config.json','automation/AUTHORIZATIONS.json']+[f'reports/phases/{phase}/decision.json' for phase in ['P00','P01','P02','P03','P04','P04G','P05']]
for rel in paths:
 p=ROOT/rel;b=p.read_bytes();space['strict_json'](b.decode());h=hashlib.sha256(b).hexdigest();assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 compat.append({'ROOT_relative':rel,'sha256':h,'strict_parse':'PASS','bytes_unchanged_during_read':True})
result={'schema':1,'scope':'PURE_FROZEN_FUNCTIONS_AND_READ_ONLY_ROOT_BYTES_NOT_CONTROLLER_INSTALLATION','loader_cases':rows,'ROOT_compatibility':compat,'source_sha256':{str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [readiness,runner]},'own_Git_controller_engine_network_calls':0,'WORK_or_canonical_state_mutations':False,'ROOT_installation_approval':False,'phase_approval':False}
(O/'strict-loader-probe-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'loader_cases_correct':len(rows),'ROOT_compatibility_files_parsed':len(compat),'mutation':False}))
