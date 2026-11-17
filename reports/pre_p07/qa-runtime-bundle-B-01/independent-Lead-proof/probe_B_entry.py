"""Pure disposable B begin/recovery checks; no real ROOT/Controller/engine."""
from pathlib import Path
import sys,json,tempfile,hashlib
HERE=Path(__file__).resolve().parent;S=HERE/'source-snapshot';sys.path.insert(0,str(S))
import cold_runtime_bundle as b
from bootstrap_runtime_fence import build
A=build((S/'legacy.py.txt').read_bytes(),(S/'payloads/autopilot/runner.py').read_bytes())
PAYLOAD={p:(S/'payloads'/p).read_bytes()for p in b.TARGETS}
results=[]
with tempfile.TemporaryDirectory(prefix='TEST_ONLY_real_A_receipt_')as td:
 r=Path(td);(r/'.git').mkdir();(r/'reports/pre_p07').mkdir(parents=True)
 p=r/'reports/pre_p07/actual-installed-A.json';p.write_bytes((S/'actual-installed-A.json').read_bytes())
 proof={'path':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 try:b.RuntimeBundle(r).verify_a(proof);actual='ACCEPTED';error=None
 except Exception as e:actual='REFUSED';error=type(e).__name__+': '+str(e)
 results.append({'case':'exact_genuine_installed_A_receipt','receipt_sha256':proof['sha256'],'expected':'ACCEPTED','actual':actual,'error':error,'contract_passed':actual=='ACCEPTED'})
with tempfile.TemporaryDirectory(prefix='TEST_ONLY_B_marker_write_')as td:
 r=Path(td)
 for d in ['.git','.autopilot','automation','autopilot/prompts','reports/pre_p07']:(r/d).mkdir(parents=True,exist_ok=True)
 (r/'automation/.executor.lock').touch(mode=0o600)
 (r/'autopilot/runner.py').write_bytes(A)
 for path,data in {'autopilot/github.py':b'# OLD TEST_ONLY','autopilot/config.json':b'{"stop_after_phase":"P06"}','autopilot/review_schema.json':b'{"OLD_TEST_ONLY":true}','autopilot/prompts/INDEPENDENT_REVIEW.md':b'OLD TEST_ONLY','autopilot/worker.py':b'# WORKER TEST_ONLY','automation/phase_state.json':b'{"TEST_ONLY":"keep_history","attempts":2}','.git/index':b'INDEX TEST_ONLY'}.items():(r/path).write_bytes(data)
 p=r/'reports/pre_p07/synthetic-A.json';p.write_text(json.dumps({'status':'PASS','actual_A_verified':True,'installed_runner_sha256':b.BOOTSTRAP_SHA,'reviewer':'INDEPENDENT_TEST_ONLY','TEST_ONLY':True}))
 proof={'path':str(p.relative_to(r)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
 protected=['automation/phase_state.json','autopilot/worker.py','.git/index',proof['path']]
 obj=b.RuntimeBundle(r);before=obj.protected(b.TARGETS);kept=obj.protected(protected)
 original=b.writejson
 def fail_marker(path,data):
  if Path(path)==r/b.MARKER:raise PermissionError('TEST_ONLY pending marker creation denied')
  return original(path,data)
 b.writejson=fail_marker
 try:
  with b.RuntimeBundle(r).lease()as obj:obj.begin_bundle(PAYLOAD,before,protected,proof)
  preparation='UNEXPECTED_SUCCESS'
 except Exception as e:preparation=type(e).__name__+': '+str(e)
 finally:b.writejson=original
 ledger=json.loads((r/b.LEDGER).read_text());ident=ledger['transactions'][-1]
 journal=r/'.autopilot/runtime-bundles'/ident/'journal.json'
 recovery=[]
 for rollback in [False,True]:
  try:
   with b.RuntimeBundle(r).lease()as obj:v=obj.finish_bundle(ident,rollback=rollback)
   recovery.append({'rollback':rollback,'actual':v['status']})
  except Exception as e:recovery.append({'rollback':rollback,'actual':'REFUSED','error':type(e).__name__+': '+str(e)})
 marker_absent_before_retry=not(r/b.MARKER).exists()
 try:
  with b.RuntimeBundle(r).lease()as obj:second=obj.begin_bundle(PAYLOAD,before,protected,proof)
  second_result='ADMITTED_NEW_TRANSACTION'
 except Exception as e:second=None;second_result=type(e).__name__+': '+str(e)
 results.append({'case':'marker_creation_failure_after_durable_ledger','preparation':preparation,'old_transaction':ident,'old_journal_status':json.loads(journal.read_text())['status'],'marker_absent_before_retry':marker_absent_before_retry,'current_runtime_exact_post_A_baseline':b.RuntimeBundle(r).protected(b.TARGETS)==before,'protected_state_unchanged':b.RuntimeBundle(r).protected(protected)==kept,'original_resume_and_rollback':recovery,'new_begin_while_old_prepared':second_result,'second_id':second,'ledger_entries':len(json.loads((r/b.LEDGER).read_text())['transactions']),'contract_passed':all(z['actual']!='REFUSED'for z in recovery)and second_result!='ADMITTED_NEW_TRANSACTION'})
out={'scope':'PURE_TEST_ONLY_B_ENTRY_AND_RECOVERY','results':results,'actual_ROOT_Controller_engine_network_Git_calls':0,'actual_Root_production_mutations':0}
(HERE/'B-entry-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
