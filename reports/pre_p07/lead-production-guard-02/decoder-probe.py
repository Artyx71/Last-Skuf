"""Narrow independent decoder probe; frozen load() only, no controller/Git/network."""
from pathlib import Path
import ast, hashlib, json, tempfile
O = Path(__file__).resolve().parent
source = O / 'reviewed-source/autopilot/runner.py'
node = next(n for n in ast.parse(source.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'load')
namespace = {'Path': Path, 'json': json}
exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), 'exec'), namespace)
rows = []
with tempfile.TemporaryDirectory(prefix='decoder-only-', dir=O) as directory:
    path = Path(directory) / 'TEST_ONLY.json'
    raw = '{"production_acceptance":{"closed_obligations":{"new_audio_acceptance":{"status":"FAIL","evidence":[]},"new_audio_acceptance":{"status":"PASS","evidence":["TEST_ONLY"]}}}}'
    path.write_text(raw)
    parsed = namespace['load'](path, {})
    rows.append({'name':'duplicate_contradictory_closure_key', 'raw_key_occurrences':raw.count('"new_audio_acceptance"'), 'decoder_rejected':False, 'retained_status':parsed['production_acceptance']['closed_obligations']['new_audio_acceptance']['status'], 'earlier_FAIL_lost':True})
    path.write_text('{"status":"PASS","TEST_ONLY":true}')
    rows.append({'name':'ordinary_unique_key_control', 'decoded_as_expected':namespace['load'](path,{})=={'status':'PASS','TEST_ONLY':True}})
result = {'schema':1, 'scope':'FROZEN_RUNNER_LOAD_FUNCTION_PURE_TEMP_JSON_ONLY', 'runner_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(), 'results':rows, 'canonical_state_WORK_Git_controller_engine_network_mutations':False, 'phase_approval':False}
(O/'decoder-probe-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
