"""Pure extracted-function review; no imports of operational project modules."""
import ast, copy, hashlib, json, math, tempfile
from pathlib import Path
O=Path(__file__).resolve().parent
R=O.parents[2]
W=R/'.autopilot/worktrees/P07'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=O/'source-final/tools/p07_pacing.py'
namespace={'math':math,'json':json,'hashlib':hashlib,'Path':Path,'digest':h}
tree=ast.parse(source.read_text())
names={'percentile','load_contract','validate_pins','visual_key','integer_fields','analyze'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTEXTS' for t in n.targets)]
readiness=ast.parse((O/'source-final/autopilot/readiness.py').read_text())
nodes += [n for n in readiness.body if isinstance(n,ast.FunctionDef) and n.name=='strict_json']
exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(source),'exec'),namespace)
rawpath=R/'reports/pre_p07/qa-pacing-calibration-01/actual-evidence/raw.json'
raw=json.loads(rawpath.read_text())
metrics=namespace['analyze'](raw)
assert metrics==json.loads((O/'final-proposal/metrics.json').read_text())
contractpath=O/'final-proposal/contract.PROPOSED.json'
contract=json.loads(contractpath.read_text()); inv=contract['source_inventory_sha256']; previous=contract['baseline_source_inventory_sha256']
changed=sorted(k for k in set(inv)|set(previous) if inv.get(k)!=previous.get(k))
assert changed==['tools/p07_pacing.py','tools/tests/test_p07_pacing.py']
for key,sha in inv.items(): assert h(W/key)==sha,key
assert contract['baseline_raw_sha256']==h(rawpath)
assert contract['baseline_metrics_sha256']==h(O/'final-proposal/metrics.json')
assert contract['limits']=={'accept_p95_ms':34,'render_p95_ms':60,'frame_p95_ms':24,'frame_p99_ms':33,'restart_max_ms':1000}
assert metrics['movement_frame_ms']['samples']==958 and metrics['idle_frame_ms']['samples']==239
cases=[]
def reject(name, change):
 data=copy.deepcopy(raw);change(data)
 try: namespace['analyze'](data);accepted=True;error=None
 except Exception as ex: accepted=False;error=type(ex).__name__+': '+str(ex)
 assert not accepted,name
 cases.append({'name':name,'rejected':True,'error':error})
reject('functional_check_false',lambda d:d['checks'][0].update(passed=False))
reject('boolean_request_id',lambda d:d['requests'][0].update(id=True))
reject('boolean_timestamp',lambda d:d['requests'][0].update(input_usec=True))
reject('boolean_raw_schema',lambda d:d.update(schema=True))
reject('wrong_full_before_context',lambda d:d['requests'][0]['before_state'].update(context='pasha_training'))
reject('invented_outgoing_contact_time',lambda d:d['requests'][4].update(contact_usec=d['requests'][4]['contact_usec']+1))
reject('invented_lethal_time',lambda d:d['requests'][5].update(death_usec=d['requests'][5]['death_usec']+1))
def late_accept(d):
 r=d['requests'][0];p=next(p for p in d['physics'] if p['usec']>r['accepted_usec'] and p['state']['context']==r['context'] and p['usec']<r['render_usec'])
 r.update(accepted_usec=p['usec'],accepted_tick=p['tick'],accepted_state=p['state'])
# The original first postdraw is before the next physics tick: use the second causal
# observation and let the ordering/first-observation contract reject the forged row.
def later_physics(d):
 r=d['requests'][0];p=next(p for p in d['physics'] if p['usec']>r['accepted_usec'] and p['state']['context']==r['context'])
 r.update(accepted_usec=p['usec'],accepted_tick=p['tick'],accepted_state=p['state'])
reject('later_accepted_anchor',later_physics)
def later_draw(d):
 r=d['requests'][0];p=next(p for p in d['draws'] if p['usec']>r['render_usec'] and p.get('state',{}).get('context')==r['context'])
 r.update(render_usec=p['usec'],render_draw=p['draw'],render_state=p['state'])
reject('later_changed_draw_anchor',later_draw)
with tempfile.TemporaryDirectory(prefix='lead-pacing-final-') as folder:
 f=Path(folder);c=f/'contract.json';v=f/'review.json';c.write_bytes(contractpath.read_bytes())
 review={'schema':1,'status':'PASS_COMPONENT','scope':'H04_CALIBRATION_CONTRACT','role':'LEAD_REVIEWER','reviewer':'TEST_ONLY','independent_of_author':True,'must_fix':[],'contract_sha256':h(c)}
 v.write_text(json.dumps(review))
 class Once:
  def __init__(self,p):self.p=p;self.reads=0
  def read_bytes(self):self.reads+=1;assert self.reads==1;return self.p.read_bytes()
  def resolve(self):return self.p.resolve()
 a,b=Once(c),Once(v);loaded,pins=namespace['load_contract'](a,b,inv)
 assert loaded==contract and a.reads==b.reads==1
 namespace['validate_pins'](pins)
 cases.append({'name':'valid_contract_same_blob_once_each','passed':True})
 for path in [c,v]:
  original=path.read_bytes();path.write_bytes(original+b'\n')
  try:namespace['validate_pins'](pins);raise AssertionError('pin admitted')
  except ValueError:pass
  path.write_bytes(original)
  cases.append({'name':'changed_'+path.name+'_pin','rejected':True})
 v.write_text(v.read_text()[:-1]+',"status":"FAIL"}')
 try:namespace['load_contract'](c,v,inv);raise AssertionError('duplicate admitted')
 except ValueError:pass
 cases.append({'name':'duplicate_review_status','rejected':True})
summary={'schema':1,'source_python_sha256':h(source),'contract_sha256':h(contractpath),'raw_sha256':h(rawpath),'actual_measurement_is_historical_85':True,'current_inventory_files_verified':len(inv),'changed_since_measurement':changed,'controlled_intervals':958,'idle_intervals':239,'metrics_exact_rederived':True,'cases':cases,'all_passed':True,'engine_Controller_Git_network_calls':0}
(O/'own-final-results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='cases'}));print('cases',len(cases))
