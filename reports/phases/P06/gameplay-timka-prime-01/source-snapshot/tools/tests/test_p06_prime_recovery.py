"""Cache integrity tests with toy files; these are NOT native-renderer evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS))
import verify_p06_timka_prime as replay


class CompletedLiveRecoveryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.folder = self.root / 'reports/native'
        (self.folder / 'live').mkdir(parents=True)
        self.patch_root = patch.object(replay, 'ROOT', self.root)
        self.patch_engine = patch.object(replay, 'GODOT', self.root / 'unit-engine')
        self.patch_root.start(); self.addCleanup(self.patch_root.stop)
        self.patch_engine.start(); self.addCleanup(self.patch_engine.stop)
        self.source = {'game/unit-fixture.gd': 'a' * 64}
        self.capture = self.folder / 'live/unit.png'
        self.capture.write_bytes(b'UNIT FIXTURE ONLY, not a generated screenshot')
        self.write('source_hashes.json', self.source)
        self.write('commands.json', [])
        (self.folder / 'live.log').write_text('UNIT fixture successful log\n')
        self.write('live/result.json', {'passed': True, 'actual_input': True, 'renderer': 'UNIT_RENDERER',
                   'checks': [{'passed': True}], 'captures': [{'path': str(self.capture), 'code': 0}]})
        self.report = {'scope': 'TIMKA_PRIME_CONTEXT_CANDIDATE_ONLY', 'passed': True,
                       'source_unchanged': True, 'headless': False, 'actual_input': True,
                       'phase_approval': False, 'movie_path': None, 'source_head': '0' * 40,
                       'checks': [{'passed': 1, 'total': 1}], 'actual_captures': 1,
                       'commands': [{'name': 'live', 'passed': True, 'exit_code': 0,
                                     'argv': [str(replay.GODOT), '--path', str(self.root / 'game'),
                                              '--disable-vsync', '--max-fps', '60', '--script',
                                              'res://tests/timka_prime_replay.gd']}],
                       'artifacts': [{'path': str(p.relative_to(self.root)), 'sha256': replay.sha(p)}
                                     for p in sorted(self.folder.rglob('*')) if p.is_file()]}
        self.save_report()

    def write(self, relative, value):
        (self.folder / relative).write_text(json.dumps(value))

    def save_report(self):
        self.write('validation.json', self.report)

    def validate(self):
        return replay.completed_live_evidence(self.folder, self.source)

    def test_intact_toy_inventory_is_reusable(self):
        self.assertTrue(self.validate()['all_artifacts_verified'])

    def test_stale_code_cannot_support_movie_only_job(self):
        with self.assertRaisesRegex(ValueError, 'source snapshot differs'):
            replay.completed_live_evidence(self.folder, {'game/unit-fixture.gd': 'b' * 64})

    def test_altered_native_artifact_is_rejected(self):
        self.capture.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'artifact'):
            self.validate()

    def test_incomplete_and_headless_runs_are_rejected(self):
        for key, value in [('passed', False), ('source_unchanged', False), ('headless', True),
                           ('actual_input', False), ('phase_approval', True), ('movie_path', 'partial.avi')]:
            with self.subTest(key=key):
                previous = self.report[key]
                self.report[key] = value
                self.save_report()
                with self.assertRaises(ValueError): self.validate()
                self.report[key] = previous
        self.save_report()

    def test_forged_command_is_rejected(self):
        self.report['commands'][0]['argv'].insert(1, '--headless')
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'current native replay'): self.validate()

    def test_parent_path_escape_is_rejected(self):
        outside = self.root / 'outside.txt'
        outside.write_text('UNIT fixture')
        self.report['artifacts'].append({'path': 'outside.txt', 'sha256': replay.sha(outside)})
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'outside'): self.validate()

    def test_missing_required_receipt_is_rejected(self):
        self.report['artifacts'] = [a for a in self.report['artifacts'] if not a['path'].endswith('commands.json')]
        self.save_report()
        with self.assertRaisesRegex(ValueError, 'Required'): self.validate()

    def test_duplicate_or_nonfinite_json_is_rejected(self):
        for text in ['{"passed": false, "passed": true}', '{"passed": NaN}']:
            with self.subTest(text=text):
                (self.folder / 'validation.json').write_text(text)
                with self.assertRaises(ValueError): self.validate()


if __name__ == '__main__':
    unittest.main()
