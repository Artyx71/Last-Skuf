"""Pure report predicate tests using actual native JSON; no engine/renderer executed."""
from pathlib import Path
import runpy,sys,json,copy,hashlib
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';sys.path.insert(0,str(Q/'isolated-project/tools'));m=runpy.run_path(str(Q/'code-freeze-final/tools/verify_p06_ryzhik.py'),run_name='qa_frozen_ryzhik_schema');actual=W/'reports/phases/P06/ryzhik-roll-01/native-03/live/result.json';base=json.loads(actual.read_text());records=[]
for name in ['actual_native_positive','wrong_scope','phase_approval','actual_input_false','empty_renderer','whitespace_renderer','unknown_renderer','headless_renderer_for_native','empty_trace','empty_contacts','failed_assertion']:
 j=copy.deepcopy(base)
 if name=='wrong_scope':j['scope']='OTHER_COMPONENT'
 if name=='phase_approval':j['phase_approval']=True
 if name=='actual_input_false':j['actual_input']=False
 if name=='empty_renderer':j['renderer']=''
 if name=='whitespace_renderer':j['renderer']=' \t\n'
 if name=='unknown_renderer':j['renderer']='unknown'
 if name=='headless_renderer_for_native':j['renderer']='headless'
 if name=='empty_trace':j['trace']=[]
 if name=='empty_contacts':j['contacts']=[]
 if name=='failed_assertion':j['checks'][0]['passed']=False
 accepted=m['valid_replay'](j,False);records.append({'case':name,'accepted':accepted,'expected':name=='actual_native_positive','matches_expected':accepted==(name=='actual_native_positive')})
(Q/'report-schema-probes.json').write_text(json.dumps({'scope':'PURE_JSON_PREDICATE_ON_ACTUAL_JSON_COPIES','helper_sha256':hashlib.sha256((Q/'code-freeze-final/tools/verify_p06_ryzhik.py').read_bytes()).hexdigest(),'actual_native_result_sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'cases':records,'actual_WORK_or_native_mutation':False,'engine_invocations':0},indent=2)+'\n');print(json.dumps(records))
