"""Reject missing/false-positive child reports and prevent timeout orphan runs."""
import json
from pathlib import Path
import re
import sys
import tempfile
import time
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_p06 as pipeline


class PipelineGateTest(unittest.TestCase):
    def test_missing_empty_truthy_and_phase_approval_reports_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'validation.json'
            self.assertFalse(pipeline.valid_report(path))
            for value in [[], {}, [{'passed': 1}], {'passed': True, 'phase_approval': False},
                          {'passed': True, 'phase_approval': True, 'commands': [{'passed': True}]},
                          {'passed': True, 'phase_approval': False, 'commands': [{'passed': True}], 'source_unchanged': False}]:
                path.write_text(json.dumps(value))
                self.assertFalse(pipeline.valid_report(path), repr(value))
            path.write_text(json.dumps([{'passed': True}, {'passed': False}]))
            self.assertFalse(pipeline.valid_report(path))
            path.write_text(json.dumps({'passed': True, 'phase_approval': False,
                                        'commands': [{'passed': True}], 'source_unchanged': True}))
            self.assertTrue(pipeline.valid_report(path))
            path.write_text(json.dumps([{'passed': True}]))
            self.assertTrue(pipeline.valid_report(path))

    def test_zero_exit_with_script_error_is_failure(self):
        with tempfile.TemporaryDirectory() as folder:
            row = pipeline.run_command([sys.executable, '-c', 'print("SCRIPT ERROR: invalid replay")'],
                                       Path(folder) / 'error.log', 3)
            self.assertEqual(row['exit_code'], 0)
            self.assertFalse(row['passed'])

    def test_timeout_terminates_child_before_return(self):
        with tempfile.TemporaryDirectory() as folder:
            log = Path(folder) / 'timeout.log'
            code = 'import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(90)"]); print("CHILD_PID="+str(p.pid),flush=True); time.sleep(90)'
            started = time.monotonic()
            row = pipeline.run_command([sys.executable, '-c', code], log, .3)
            self.assertEqual(row['exit_code'], 124)
            self.assertFalse(row['passed'])
            self.assertLess(time.monotonic() - started, 5)
            child = int(re.search(r'CHILD_PID=(\d+)', log.read_text()).group(1))
            proc = Path('/proc') / str(child) / 'stat'
            self.assertTrue(not proc.exists() or proc.read_text().rsplit(')', 1)[1].split()[0] == 'Z')


if __name__ == '__main__':
    unittest.main()
