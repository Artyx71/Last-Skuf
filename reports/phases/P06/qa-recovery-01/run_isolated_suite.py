#!/usr/bin/env python3
"""Independent QA fixture-only AUTOPILOT suite; real GitHub calls prohibited."""
import sys,os,json,time,hashlib,importlib.util,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
WORK=ROOT/'.autopilot/worktrees/P06'
OUT=Path(__file__).parent
assert Path.cwd()==WORK
source=WORK/'tools/tests/test_autopilot.py'
spec=importlib.util.spec_from_file_location('qa_isolated_autopilot_tests',source)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.ROOT==WORK
started=time.monotonic()
with (OUT/'unittest.log').open('w') as stream:
 with patch('github.gh',side_effect=AssertionError('QA forbids actual GitHub/gh access; fixtures must mock every external request')):
  result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
summary={'schema':1,'scope':'EXISTING_AUTOPILOT_ISOLATED_UNIT_FIXTURES_ONLY','reviewer':'/root/qa_resume_recovery','phase_approval':False,'production_controller_invoked':False,'actual_github_requests_permitted':False,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'successful':result.wasSuccessful(),'seconds':round(time.monotonic()-started,3),'bytecode_writes_disabled':sys.dont_write_bytecode,'environment_git_user_config_disabled':os.environ.get('GIT_CONFIG_GLOBAL')=='/dev/null'}
(OUT/'unittest_result.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary));sys.exit(0 if result.wasSuccessful() else 1)
