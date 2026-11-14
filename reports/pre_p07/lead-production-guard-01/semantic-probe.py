"""Two pure load_gate controls on TEST_ONLY temporary files; no Git/controller calls."""
from pathlib import Path
import json,hashlib,tempfile
OUT=Path(__file__).parent
source=OUT/'source-snapshot/autopilot/readiness.py'
module={'__name__':'isolated_lead_semantic_probe','__file__':str(source)}
exec(compile(source.read_text(),str(source),'exec'),module)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(OUT/'tmp').mkdir(exist_ok=True)
results=[]
with tempfile.TemporaryDirectory(dir=OUT/'tmp',prefix='TEST_ONLY_') as folder:
 root=Path(folder);(root/'game').mkdir();file=root/'game/control.gd';file.write_text('# TEST_ONLY, not real game or approval\n');decision=root/'reports/pre_p07/TEST_ONLY/control.json';decision.parent.mkdir(parents=True)
 base={'schema':1,'status':'PASS','scope':'PRE_P07_PRODUCTION_READINESS','acceptance_level':'FULL','role':'LEAD_REVIEWER','reviewer':'TEST_ONLY_SYNTHETIC_NO_PRODUCTION_APPROVAL','independent_of_author':True,'p06_base_head':'a'*40,'must_fix':[],'ready_for_p07':True,'source_inventory_sha256':{'game/control.gd':sha(file)}}
 for name,finding in [('closed_preproduction_control',{'id':'TEST_ONLY_CAPABILITY','severity':'HIGH','status':'CLOSED','gate':'BEFORE_P07_ENTRY'}),('future_content_condition',{'id':'TEST_ONLY_CAMPAIGN_DURATION','severity':'HIGH','status':'OPEN','gate':'AFTER_CONTENT_IMPLEMENTATION_BEFORE_P07_COMPLETION','required_evidence':'actual complete campaign first-play data; levels not yet created'})]:
  data={**base,'findings':[finding]};decision.write_text(json.dumps(data));record={'decision':str(decision.relative_to(root)),'sha256':sha(decision)}
  try:module['load_gate'](root,record,'PRE_P07_PRODUCTION_READINESS',['a'*40]);outcome='ACCEPTED_LOAD_GATE_ONLY';message=None
  except module['ReadinessBlocked'] as error:outcome='BLOCKED';message=str(error)
  results.append({'name':name,'finding':finding,'actual_v2_outcome':outcome,'message':message})
assert results[0]['actual_v2_outcome']=='ACCEPTED_LOAD_GATE_ONLY' and results[1]['actual_v2_outcome']=='BLOCKED'
(OUT/'semantic-probe-result.json').write_text(json.dumps({'scope':'TEST_ONLY_PURE_LOADER_STAGE_SEMANTICS_NO_PRODUCTION_APPROVAL','source_sha256':sha(source),'cases':results,'current_v2_behavior_reproduced':True,'bypass_found':False,'mechanical_failure_claim':False,'git_controller_engine_network_calls':0,'real_state_mutations':0},indent=2)+'\n')
print(json.dumps(results,indent=2))
