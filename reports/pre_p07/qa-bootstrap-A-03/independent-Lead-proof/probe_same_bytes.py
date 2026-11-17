"""Real read/parse interleaving injection in an isolated fake checkout only."""
from pathlib import Path
import tempfile, sys, json, hashlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'source-snapshot'))
import cold_bootstrap as cb
from bootstrap_runtime_fence import build
S=HERE/'source-snapshot';OLD=(S/'legacy.py.txt').read_bytes();NEW=build(OLD,(S/'fence.py.txt').read_bytes())
with tempfile.TemporaryDirectory(prefix='TEST_ONLY_read_binding_') as td:
 r=Path(td)
 for d in ['.git','.autopilot','automation','autopilot']:(r/d).mkdir()
 (r/cb.RUNNER).write_bytes(OLD);(r/cb.RUNNER).chmod(0o755)
 (r/'automation/.executor.lock').touch(mode=0o600)
 state=r/'automation/phase_state.json';state.write_bytes(b'{"TEST_ONLY":"original_history"}\n')
 (r/'autopilot/config.json').write_text('{}')
 protected=['automation/phase_state.json','autopilot/config.json','.autopilot/STATE.json']
 with cb.Bootstrap(r).lease() as b:ident=b.begin(NEW,protected)
 intent=r/'.autopilot/bootstrap'/ident/'intent.json';prepared=intent.read_bytes();prepared_sha=hashlib.sha256(prepared).hexdigest()
 state.write_bytes(b'{"TEST_ONLY":"new_unknown_history"}\n')
 original_readjson=cb.readjson;swaps=[]
 def interleaved_readjson(path):
  path=Path(path)
  if path==intent:
   good=path.read_bytes();bad=json.loads(good);bad['protected']={};path.write_text(json.dumps(bad))
   try:
    data=original_readjson(path)  # Actual parser reads the temporarily different file.
    swaps.append({'hashed_bytes_sha256':hashlib.sha256(good).hexdigest(),'parsed_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'parsed_protected_keys':list(data['protected'])})
    return data
   finally:path.write_bytes(good)
  return original_readjson(path)
 cb.readjson=interleaved_readjson
 error=None
 try:
  with cb.Bootstrap(r).lease() as b:record=b.finish(ident)
  actual=record['status'];record_protected=list(record['protected'])
 except Exception as e:actual='REFUSED';error=type(e).__name__+': '+str(e);record_protected=None
 finally:cb.readjson=original_readjson
 out={'scope':'TEST_ONLY_PURE_SAME_HASHED_PARSED_BYTES_BOUNDARY','expected':'REFUSED','actual':actual,'contract_passed':actual=='REFUSED','error':error,'swaps':swaps,'prepared_intent_sha256':prepared_sha,'intent_original_bytes_restored':intent.read_bytes()==prepared,'original_protected_keys':list(json.loads(prepared)['protected']),'returned_protected_keys':record_protected,'unknown_state_preserved_not_overwritten':state.read_bytes()==b'{"TEST_ONLY":"new_unknown_history"}\n','marker_exists':(r/cb.MARKER).exists(),'Controller_engine_network_Git_calls':0,'real_ROOT_mutations':0}
(HERE/'same-bytes-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
