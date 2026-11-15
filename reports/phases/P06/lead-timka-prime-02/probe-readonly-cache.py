"""Exact helper function only; no import/main/engine/Git/controller/state mutation."""
from pathlib import Path
import ast,json,hashlib,re
ROOT_REPORT=Path(__file__).resolve().parent
WORK=ROOT_REPORT.parents[3]/'.autopilot/worktrees/P06'
source=ROOT_REPORT/'source-snapshot/tools/verify_p06_timka_prime.py'
fn=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='completed_live_evidence')
lock=json.loads((WORK/'tools/toolchain.lock.json').read_text())
space={'Path':Path,'json':json,'ROOT':WORK,'GODOT':WORK/'.tools/godot'/f'Godot_v{lock["release"]}_linux.x86_64','ERRORS':re.compile(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use'),'sha':lambda p:hashlib.sha256(p.read_bytes()).hexdigest()}
exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),space)
base=WORK/'reports/phases/P06/timka-prime-01';historical=json.loads((base/'native-03/source_hashes.json').read_text());current={p:hashlib.sha256((WORK/p).read_bytes()).hexdigest() for p in historical};rows=[]
for name,folder,mapping,want in [('actual_complete_native03_historical_exact',base/'native-03',historical,True),('current_test_source_delta_rejects_historical_reuse',base/'native-03',current,False),('old02_helper_source_stale_rejected',base/'native-02',historical,False),('interrupted_old01_no_validation_rejected',base/'native-01',historical,False)]:
 try:value=space['completed_live_evidence'](folder,mapping);accepted=True;error=None
 except Exception as e:value=None;accepted=False;error=type(e).__name__+': '+str(e)
 assert accepted==want,(name,accepted,error)
 rows.append({'case':name,'accepted':accepted,'expected':want,'value':value,'error':error})
(ROOT_REPORT/'readonly-cache-results.json').write_text(json.dumps({'schema':1,'scope':'PURE_FROZEN_HELPER_READ_ONLY_EXISTING_REAL_EVIDENCE','helper_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':rows,'engine_Git_controller_network_calls':0,'WORK_or_original_evidence_mutations':False},indent=2)+'\n')
print(json.dumps({'cases_correct':len(rows),'helper_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}))
