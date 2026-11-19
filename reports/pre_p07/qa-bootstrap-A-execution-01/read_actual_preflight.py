"""Pure read-only actual plan/337inputs/drain checks; never run apply or lease."""
from pathlib import Path
import ast,hashlib,json,os,sys
sys.dont_write_bytecode=True
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');Q=Path(__file__).resolve().parent;W=R/'.autopilot/worktrees/P07';S=R/'reports/pre_p07/qa-bootstrap-A-03/source';sys.path.insert(0,str(S/'tools'))
import cold_bootstrap as cb
from bootstrap_runtime_fence import build
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
planpath=R/'reports/pre_p07/bootstrap-actual-A-03/plan.json';blob=planpath.read_bytes();digest=hashlib.sha256(blob).hexdigest();assert digest=='2075eb9c7e0d5e6b1d39bbac8851b9113125b2a3c492ff66a914d98f1038abbe';plan=cb.parsejson(blob)
checks=[]
def ck(ok,name,details=None):checks.append({'name':name,'passed':bool(ok),'details':details})
wrapper=R/'.tools/pre-p07-bootstrap-maintenance.py';ck(sha(wrapper)==plan['wrapper_sha256']==sha(Q/'wrapper-A03.py.txt'),'current wrapper exactly bound to reviewedA03 plan')
ck(plan['root']==str(R) and plan['target_sha256']==cb.BOOTSTRAP_SHA and plan['legacy_sha256']==cb.LEGACY_SHA,'exact root/old02b/targetd1c, A-only scope')
records=[]
for rel,expected in plan['protected'].items():
 actual=cb.fingerprint(cb.checked(R,rel));records.append({'path':rel,'expected':expected,'actual':actual,'matches':actual==expected})
ck(len(records)==337 and all(x['matches'] for x in records),'all337 actual protected fingerprints match exactplan')
for rel,expected in plan['source_pins'].items():ck(sha(W/rel)==expected,'actual reviewed tool source pin '+rel)
legacy=cb.fingerprint(cb.checked(R,cb.RUNNER));target=build((R/cb.RUNNER).read_bytes(),(W/'autopilot/runner.py').read_bytes());ck(legacy['sha256']==cb.LEGACY_SHA and hashlib.sha256(target).hexdigest()==cb.BOOTSTRAP_SHA,'actual oldRoot/fence inputs build exact reviewed target without installation')
ck((legacy['uid'],legacy['gid'])==(os.geteuid(),os.getegid()),'actual runner ownership preservable by current user',legacy)
lock=R/'automation/.executor.lock';s=lock.stat();device=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}';lines=[x for x in Path('/proc/locks').read_text().splitlines() if device in x];ck(s.st_ino==plan['lock_inode']==1118521 and s.st_nlink==1 and lines==[],'same unheld canonical lock inode at readonlysnapshot',{'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'matching_proc_locks':lines})
markers={n:cb.checked(R,n).exists() for n in [cb.MARKER,cb.B_MARKER,cb.B_HISTORY]};ck(not any(markers.values()),'no pending A/B or Bstarted history',markers)
tree=ast.parse((Q/'wrapper-A03.py.txt').read_text());drain=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='drain');ns={'R':R,'Path':Path,'os':os,'readjson':cb.readjson,'sha':sha};exec(compile(ast.Module(body=[drain],type_ignores=[]),str(wrapper),'exec'),ns);actualdrain=ns['drain']();ck(actualdrain['last_operation']==plan['drain']['last_operation'] and actualdrain['receipt_sha256']==plan['drain']['receipt_sha256'] and actualdrain['known_launchers_or_engine']==[],'exact existing readonly drain passes currentPID/state/receipt/processconditions',actualdrain)
ck(plan['cold_single_author_no_launcher_premise'] is True and plan['all_old_entrypoint_technical_barrier_claim'] is False and plan['B_started'] is False,'cold external premise explicit; no false universaloldcodebarrier orBapproval')
component=R/'reports/pre_p07/qa-bootstrap-A-03/decision.json';cv=cb.readjson(component);ck(sha(component)=='0880bf18c6f623c6b4c78da91f7d2f92cd41ec5f823bd41a4f1b878876602b0d' and cv['status']=='PASS_COMPONENT' and cv['must_fix']==[],'actual independent componentQA03 accepted, not itself executionGO')
ck(planpath.read_bytes()==blob and sha(wrapper)==plan['wrapper_sha256'],'plan/wrapper bytes stable across readonlyreview')
out={'scope':'ACTUAL_A03_PLAN_READONLY_EXECUTION_PREFLIGHT_NO_LEASE_OR_INSTALL','passed':all(x['passed'] for x in checks),'checks':checks,'plan_sha256':digest,'wrapper_sha256':sha(wrapper),'protected_records':records,'expected_target_fingerprint':dict(legacy,sha256=cb.BOOTSTRAP_SHA),'actualdrain':actualdrain,'Controller_Bootstrap_constructor_lease_engine_or_apply_calls':0,'arbitrary_hidden_interpreter_guarantee':False};(Q/'actual-A03-preflight.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'checks':len(checks),'failed':[x['name'] for x in checks if not x['passed']],'protected':len(records)}))
