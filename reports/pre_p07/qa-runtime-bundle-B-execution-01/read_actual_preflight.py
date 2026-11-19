from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,os,sys,subprocess
sys.dont_write_bytecode=True
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P07';Q=Path(__file__).resolve().parent;S=Q.parent/'qa-runtime-bundle-B-02/source';sys.path.insert(0,str(S/'tools'))
import cold_bootstrap as cb
from cold_runtime_bundle import RuntimeBundle,TARGETS,MARKER,LEDGER
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ck(ok,name,details=None):checks.append({'name':name,'passed':bool(ok),'details':details})
path=R/'reports/pre_p07/bundle-actual-B-02/plan.json';blob=path.read_bytes();digest=hashlib.sha256(blob).hexdigest();assert digest=='b2ea1ac3a5fd62bbd4d565ce18a0f2cd0b0cd42c7f934c5f4a89fbdb342a3e95';plan=cb.parsejson(blob);wrapper=R/'.tools/pre-p07-bundle-maintenance.py'
ck(sha(wrapper)==plan['wrapper_sha256']==sha(Q/'wrapper-B02.py.txt'),'actual reviewed wrapper bound to exactB02plan')
ck(plan['root']==str(R) and plan['target_pins']==TARGETS and plan['stop_after_phase']=='P06','exact root/seventargets/stopP06')
records=[]
for rel,expected in plan['protected'].items():
 actual=cb.fingerprint(cb.checked(R,rel));records.append({'path':rel,'expected':expected,'actual':actual,'matches':actual==expected})
ck(len(records)==345 and all(x['matches'] for x in records),'actual345protected inputs exactplan')
before={n:cb.fingerprint(cb.checked(R,n)) for n in TARGETS};ck(before==plan['before'] and before['autopilot/runner.py']['sha256']==cb.BOOTSTRAP_SHA,'actualpostA before allseven Rootruntimeexact')
a_baseline=RuntimeBundle.verify_a(SimpleNamespace(root=R),plan['installed_A']);ck({n:cb.fingerprint(cb.checked(R,n)) for n in a_baseline}==a_baseline and len(a_baseline)==10,'genuine147c sameblob receipt andbound10baseline matchcurrentRoot')
ck(plan['installed_A']['sha256']=='147c691e86b13050ce3929816e53230198190c5d74fa02bab1d7f565a1a82308','exact independently verifiedinstalledAreceipt')
for rel,h in plan['source_pins'].items():ck(sha(W/rel)==h,'actual reviewed Worktoolpin '+rel)
ck(all(sha(W/n)==h for n,h in TARGETS.items()),'actualseven Workpayloadhashes exactknown reviewedcode')
for role,h in plan['component_decisions'].items():
 p=R/f'reports/pre_p07/{role}-runtime-bundle-B-02/decision.json';ck(sha(p)==h and cb.parsejson(p.read_bytes())['status']=='PASS_COMPONENT','actual independentcomponentdecision '+role)
lock=R/'automation/.executor.lock';s=lock.stat();key=f'{os.major(s.st_dev):02x}:{os.minor(s.st_dev):02x}:{s.st_ino}';locks=[x for x in Path('/proc/locks').read_text().splitlines() if key in x];ck(s.st_ino==plan['lock_inode']==1118521 and s.st_nlink==1 and not locks,'existing unheld canonical inode at readonlysnapshot',{'device':s.st_dev,'inode':s.st_ino,'nlink':s.st_nlink,'matching_proc_locks':locks})
marks={n:cb.checked(R,n).exists() for n in [MARKER,LEDGER,cb.MARKER]};ck(not any(marks.values()),'noAorBpending/noBledgerbeforefirstapply',marks)
common=subprocess.check_output(['git','rev-parse','--path-format=absolute','--git-common-dir'],cwd=W,text=True).strip();ck((R/'.git').is_dir() and (W/'.git').is_file() and common==str(R/'.git'),'real canonicalRoot/phaseworktree commonGitdir read-onlycheck')
tree=ast.parse((Q/'wrapper-B02.py.txt').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='drain');ns={'R':R,'Path':Path,'os':os,'readjson':cb.readjson,'sha':sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(wrapper),'exec'),ns);drain=ns['drain']();ck(drain['last_operation']==plan['drain']['last_operation'] and drain['receipt_sha256']==plan['drain']['receipt_sha256'] and drain['known_launchers_or_engine']==[],'actual exactreadonlydrain/checkpoint/receipt/PID/knownlauncherchecks',drain)
ck(all(v is None or (v['uid'],v['gid'])==(os.geteuid(),os.getegid()) for v in before.values()),'actual ownership preservable bycurrentuser')
oldconfig=cb.parsejson((R/'autopilot/config.json').read_bytes());newconfig=cb.parsejson((W/'autopilot/config.json').read_bytes());delta={k:[oldconfig.get(k),newconfig.get(k)] for k in oldconfig.keys()|newconfig.keys() if oldconfig.get(k)!=newconfig.get(k)};ck(oldconfig['stop_after_phase']==newconfig['stop_after_phase']=='P06' and set(delta)<= {'native_qa_timeout_seconds'},'configscope onlyreviewed nativebudget; stopP06 retained',delta)
ck(path.read_bytes()==blob and sha(wrapper)==plan['wrapper_sha256'],'plan/wrapper bytes stable acrossreadonlyreview')
result={'scope':'ACTUAL_B02_PLAN_READONLY_PREFLIGHT_NO_ROOT_B_OBJECT_LEASE_OR_APPLY','passed':all(x['passed'] for x in checks),'checks':checks,'plan_sha256':digest,'wrapper_sha256':sha(wrapper),'protected_records':records,'before_seven':before,'baseline10':a_baseline,'actualdrain':drain,'actual_ROOT_RuntimeBundle_constructor_lease_Controller_engine_or_apply_calls':0,'arbitrary_hidden_interpreter_absence_proven':False};(Q/'actual-B02-preflight.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'protected':len(records),'failed':[x['name'] for x in checks if not x['passed']]}))
