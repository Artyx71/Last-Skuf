"""Pure filesystem probes in temporary fake checkouts; no Controller/engine."""
from pathlib import Path
import tempfile, sys, json, os, fcntl, hashlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'source-snapshot'))
import cold_bootstrap as cb
from bootstrap_runtime_fence import build
S=HERE/'source-snapshot'
OLD=(S/'legacy.py.txt').read_bytes()
NEW=build(OLD,(S/'fence.py.txt').read_bytes())
results=[]
for case in ['positive','journal_protected_removed','journal_target_mode_changed','canonical_lock_replaced_before_commit','protected_changed_after_commit']:
 with tempfile.TemporaryDirectory(prefix='TEST_ONLY_bootstrap_A_') as td:
  r=Path(td)
  for d in ['.git','.autopilot','automation','autopilot']:(r/d).mkdir()
  (r/cb.RUNNER).write_bytes(OLD);(r/cb.RUNNER).chmod(0o755)
  lock=r/'automation/.executor.lock';lock.touch(mode=0o600);old_inode=lock.stat().st_ino
  state=r/'automation/phase_state.json';before=b'{"TEST_ONLY":"keep_history","attempts":2}\n';state.write_bytes(before)
  (r/'autopilot/config.json').write_text('{}')
  protected=['automation/phase_state.json','autopilot/config.json','.autopilot/STATE.json']
  with cb.Bootstrap(r).lease() as b:ident=b.begin(NEW,protected)
  journal=r/'.autopilot/bootstrap'/ident/'journal.json'
  original_journal_sha=hashlib.sha256(journal.read_bytes()).hexdigest()
  extra={}
  if case=='journal_protected_removed':
   state.write_bytes(b'{"TEST_ONLY":"new_unknown_history"}\n')
   j=json.loads(journal.read_text());j['protected']={};journal.write_text(json.dumps(j))
  if case=='journal_target_mode_changed':
   j=json.loads(journal.read_text());j['target']['mode']=0o700;journal.write_text(json.dumps(j))
  def hook(stage):
   if case=='canonical_lock_replaced_before_commit' and stage=='before_commit':
    lock.unlink();lock.touch(mode=0o600)
    fd=os.open(lock,os.O_RDWR)
    try:
     fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
     extra['replacement_canonical_lock_acquirable_while_old_lease_held']=True
    finally:os.close(fd)
   if case=='protected_changed_after_commit' and stage=='after_commit':
    state.write_bytes(b'{"TEST_ONLY":"changed_at_after_commit"}\n')
  actual='UNKNOWN';error=None
  try:
   with cb.Bootstrap(r,hook=hook).lease() as b:record=b.finish(ident)
   actual=record['status']
  except Exception as e:actual='REFUSED';error=type(e).__name__+': '+str(e)
  expected='VERIFIED' if case=='positive' else 'REFUSED'
  results.append({'case':case,'expected':expected,'actual':actual,'contract_passed':actual==expected,'error':error,'state_before_preserved':state.read_bytes()==before,'runner_mode':oct((r/cb.RUNNER).stat().st_mode&0o777),'lock_inode_preserved':lock.stat().st_ino==old_inode,'marker_exists':(r/cb.MARKER).exists(),'prepare_journal_sha':original_journal_sha,'extra':extra})
out={'scope':'PURE_TEST_ONLY_FILESYSTEM_BOUNDARY_PROBES_NO_REAL_ROOT','source':json.loads((HERE/'source-freeze.json').read_text()),'results':results,'Controller_calls':0,'engine_calls':0,'actual_ROOT_or_Git_mutations':0}
(HERE/'boundary-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(results,indent=2))
