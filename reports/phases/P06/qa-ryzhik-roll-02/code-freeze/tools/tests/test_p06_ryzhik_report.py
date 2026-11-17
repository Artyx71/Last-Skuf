"""Reject false renderer/mode evidence; pure schema controls, never renderer QA."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from verify_p06_ryzhik import valid_replay

class ReplayReportTests(unittest.TestCase):
    def report(self, renderer='X11'):
        return dict(scope='RYZHIK_ROLL_COMPONENT_ONLY', phase_approval=False,
                    actual_input=True, passed=True, renderer=renderer,
                    checks=[dict(passed=True)], trace=[dict(tick=1)], contacts=[dict(id=1)])

    def test_actual_supported_backend_and_mode(self):
        for renderer in ['X11', 'Wayland']:
            self.assertTrue(valid_replay(self.report(renderer), False))
            self.assertFalse(valid_replay(self.report(renderer), True))
        self.assertTrue(valid_replay(self.report('headless'), True))
        self.assertFalse(valid_replay(self.report('headless'), False))

    def test_renderer_cannot_be_missing_blank_or_forged(self):
        for renderer in ['', ' ', '\t\n', None, True, 1, [], {}, 'unknown', 'X11 ', ' X11']:
            with self.subTest(renderer=renderer):
                self.assertFalse(valid_replay(self.report(renderer), False))
                self.assertFalse(valid_replay(self.report(renderer), True))
        report = self.report()
        report.pop('renderer')
        self.assertFalse(valid_replay(report, False))

    def test_schema_does_not_accept_truthy_or_empty_evidence(self):
        changes = [('phase_approval', 0), ('actual_input', 1), ('passed', 'true'),
                   ('scope', 'FULL_P06'), ('checks', []), ('checks', [{'passed': 1}]),
                   ('checks', [{'passed': False}]), ('trace', []), ('contacts', [])]
        for key, value in changes:
            report = copy.deepcopy(self.report())
            report[key] = value
            with self.subTest(field=key, value=value):
                self.assertFalse(valid_replay(report, False))

if __name__ == '__main__':
    unittest.main()
