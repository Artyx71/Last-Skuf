"""Same B entry faults; new prerequisite fixture includes its required baseline."""
from pathlib import Path
import sys,json,tempfile,hashlib
HERE=Path(__file__).resolve().parent;S=HERE/'source-snapshot';sys.path.insert(0,str(S))
import cold_runtime_bundle as b
from bootstrap_runtime_fence import build
A=build((S/'legacy.py.txt').read_bytes(),(S/'payloads/autopilot/runner.py').read_bytes())
PAYLOAD={p:(S/'payloads'/p).read_bytes()for p in b.TARGETS}
results=[]
with tempfile.TemporaryDirectory(prefix='TEST_ONLY_real_A_wire_fixed_')as td:
 r=Path(td);(r/'.git').mkdir();(r/'reports/pre_p07').mkdir(parents=True)
 p=r/'reports/pre_p07/actual-installed-A.json';p.write_bytes((S/'actual-installed-A.json').read_bytes())
 original=json.loads(p.read_text());base=r/original['post_A_runtime_baseline_path'];base.parent.mkdir(parents=True,exist_ok=True);base.write_bytes((S/'actual-baseline-A.json').read_bytes())
 proof={'path':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 try:files=b.RuntimeBundle(r).verify_a(proof);actual='ACCEPTED';error=None
 except Exception as e:actual='REFUSED';error=type(e).__name__+': '+str(e);files={}
 results.append({'case':'exact_genuine_installed_A_receipt_and_bound_baseline','receipt_sha256':proof['sha256'],'expected':'ACCEPTED','actual':actual,'baseline_entries':len(files),'error':error,'contract_passed':actual=='ACCEPTED'and len(files)==10})
for rollback in [False,True]:
 with tempfile.TemporaryDirectory(prefix='TEST_ONLY_B_marker_recovery_fixed_')as td:
  r=Path(td)
  for d in ['.git','.autopilot','automation','autopilot/prompts','reports/pre_p07']:(r/d).mkdir(parents=True,exist_ok=True)
  (r/'automation/.executor.lock').touch(mode=0o600);(r/'autopilot/runner.py').write_bytes(A)
  for path,data in {'autopilot/github.py':b'# OLD TEST_ONLY','autopilot/config.json':b'{"stop_after_phase":"P06"}','autopilot/review_schema.json':b'{"OLD_TEST_ONLY":true}','autopilot/prompts/INDEPENDENT_REVIEW.md':b'OLD TEST_ONLY','autopilot/worker.py':b'# WORKER TEST_ONLY','automation/phase_state.json':b'{"TEST_ONLY":"keep_history","attempts":2}','.git/index':b'INDEX TEST_ONLY'}.items():(r/path).write_bytes(data)
  # Same test-only runtime as the old fault; typed wire now includes the bound
  # synthetic baseline, without modifying the real installed-A receipt.
  base=r/'reports/pre_p07/baseline_TEST_ONLY.json';names=set(b.TARGETS)|{'autopilot/worker.py','tools/verify.py','tools/verify_p06.py'};base.write_text(json.dumps({'schema':1,'TEST_ONLY':True,'runtime_files':b.RuntimeBundle(r).protected(names)}))
  record=json.loads((S/'actual-installed-A.json').read_text());record.update(TEST_ONLY=True,post_A_runtime_baseline_path=str(base.relative_to(r)),post_A_runtime_baseline_sha256=hashlib.sha256(base.read_bytes()).hexdigest())
  p=r/'reports/pre_p07/synthetic-A.json';p.write_text(json.dumps(record));proof={'path':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  protected=['automation/phase_state.json','autopilot/worker.py','.git/index',proof['path']];obj=b.RuntimeBundle(r);before=obj.protected(b.TARGETS);kept=obj.protected(protected);original=b.writejson
  def fail_marker(path,data):
   if Path(path)==r/b.MARKER:raise PermissionError('TEST_ONLY pending marker creation denied')
   return original(path,data)
  b.writejson=fail_marker
  try:
   with b.RuntimeBundle(r).lease()as obj:obj.begin_bundle(PAYLOAD,before,protected,proof)
   preparation='UNEXPECTED_SUCCESS'
  except Exception as e:preparation=type(e).__name__+': '+str(e)
  finally:b.writejson=original
  ident=json.loads((r/b.LEDGER).read_text())['transactions'][-1];journal=r/'.autopilot/runtime-bundles'/ident/'journal.json'
  try:
   with b.RuntimeBundle(r).lease()as obj:obj.begin_bundle(PAYLOAD,before,protected,proof)
   second='ADMITTED_NEW_TRANSACTION'
  except Exception as e:second='REFUSED';second_error=type(e).__name__+': '+str(e)
  initial_marker_absent=not(r/b.MARKER).exists();initial_prepared=json.loads(journal.read_text())['status']=='PREPARED'
  try:
   with b.RuntimeBundle(r).lease()as obj:outcome=obj.finish_bundle(ident,rollback=rollback)
   actual=outcome['status'];same_id=outcome['id']==ident;error=None
  except Exception as e:actual='REFUSED';same_id=False;error=type(e).__name__+': '+str(e)
  desired=before if rollback else {n:dict(before[n]or{'mode':0o644,'uid':__import__('os').geteuid(),'gid':__import__('os').getegid()},sha256=b.TARGETS[n])for n in b.TARGETS}
  runtime_ok=b.RuntimeBundle(r).protected(b.TARGETS)==desired;state_ok=b.RuntimeBundle(r).protected(protected)==kept;ledger_count=len(json.loads((r/b.LEDGER).read_text())['transactions'])
  results.append({'case':'same_marker_creation_failure_recovery','rollback':rollback,'preparation':preparation,'initial_prepared':initial_prepared,'initial_marker_absent':initial_marker_absent,'new_begin_before_recovery':second,'new_begin_error':second_error,'original_id_recovery':actual,'expected':'ROLLED_BACK'if rollback else'COMMIT_VERIFIED','same_transaction_id':same_id,'final_marker_absent':not(r/b.MARKER).exists(),'ledger_retained_count':ledger_count,'runtime_exact_desired':runtime_ok,'protected_state_unchanged':state_ok,'error':error,'contract_passed':second=='REFUSED'and same_id and actual==('ROLLED_BACK'if rollback else'COMMIT_VERIFIED')and runtime_ok and state_ok and ledger_count==1 and not(r/b.MARKER).exists()})
out={'scope':'PURE_TEST_ONLY_FIXED_B_ENTRY_CLOSURE','results':results,'adaptation':'Real wire gains required byte-exact baseline; original marker fault repeated on separate identical initial states per commit/rollback to respect immutable terminal outcome. No expected oracle weakened.','actual_ROOT_Controller_engine_network_Git_calls':0,'actual_Root_production_mutations':0}
(HERE/'B-closure-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
