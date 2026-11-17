"""Pure predicates on copies of actual saved results; never run renderer/engine."""
from pathlib import Path
import runpy,sys,json,copy,hashlib
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';sys.path.insert(0,str(Q/'isolated-project/tools'))
m=runpy.run_path(str(Q/'code-freeze/tools/verify_p06_pasha.py'),run_name='qa_frozen_pasha_schema')
actual=W/'reports/phases/P06/pasha-moving-shot-01/native-01/live/result.json';base=json.loads(actual.read_text());records=[]
for name in ['actual_native_positive','wrong_scope','phase_approval','actual_input_false','empty_renderer','whitespace_renderer','unknown_renderer','numeric_renderer','headless_renderer_for_native','empty_trace','empty_contacts','failed_assertion','wrong_checks_type','numeric_passed','phase_zero_is_not_bool']:
 j=copy.deepcopy(base)
 if name=='wrong_scope':j['scope']='OTHER_COMPONENT'
 if name=='phase_approval':j['phase_approval']=True
 if name=='actual_input_false':j['actual_input']=False
 if name=='empty_renderer':j['renderer']=''
 if name=='whitespace_renderer':j['renderer']=' \t\n'
 if name=='unknown_renderer':j['renderer']='unknown'
 if name=='numeric_renderer':j['renderer']=7
 if name=='headless_renderer_for_native':j['renderer']='headless'
 if name=='empty_trace':j['trace']=[]
 if name=='empty_contacts':j['contacts']=[]
 if name=='failed_assertion':j['checks'][0]['passed']=False
 if name=='wrong_checks_type':j['checks']={}
 if name=='numeric_passed':j['passed']=1
 if name=='phase_zero_is_not_bool':j['phase_approval']=0
 accepted=m['valid_replay'](j,False);expected=name=='actual_native_positive';assert accepted==expected
 records.append({'case':name,'accepted':accepted,'expected':expected,'matches_expected':True})
h=W/'reports/phases/P06/pasha-moving-shot-01/headless-02/live/result.json';j=json.loads(h.read_text());assert m['valid_replay'](j,True) and not m['valid_replay'](j,False);records.append({'case':'actual_headless_mode_separation','headless_accept':True,'native_reject':True,'matches_expected':True})
(Q/'report-schema-probes.json').write_text(json.dumps({'scope':'PURE_JSON_PREDICATE_ON_ACTUAL_JSON_COPIES','helper_sha256':hashlib.sha256((Q/'code-freeze/tools/verify_p06_pasha.py').read_bytes()).hexdigest(),'actual_native_result_sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'cases':records,'actual_WORK_or_native_mutation':False,'engine_invocations':0},indent=2)+'\n')
print('PASS16/16 actual saved JSON positive/negative mode/schema predicates; no engine invoked')
