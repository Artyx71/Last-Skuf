"""Cold runtime admission. Isolated roots only; never import a live controller."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class RuntimeFenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.code = self.root / 'autopilot'
        self.code.mkdir()
        shutil.copy2(ROOT / 'autopilot/runner.py', self.code / 'runner.py')
        shutil.copy2(ROOT / 'autopilot/config.json', self.code / 'config.json')
        # No real GitHub module or CLI is reachable from the isolated fixture.
        (self.code / 'github.py').write_text(
            "def manage(*args, **kwargs):\n"
            " from pathlib import Path\n"
            " Path(__file__).with_name('UNEXPECTED_REMOTE_CALL').write_text('called')\n"
            " return 0\n")
        (self.code / 'readiness.py').write_text(
            "import json\n"
            "strict_json=json.loads\n"
            "class ReadinessBlocked(RuntimeError): pass\n"
            "def require_p07_production(*args): raise ReadinessBlocked('TEST_ONLY')\n")
        (self.root / 'automation').mkdir()
        self.state = self.root / 'automation/phase_state.json'
        self.state.write_text(json.dumps({
            'active_phase': 'P07', 'status': 'READY', 'attempts': 2,
            'custom_owner_value': 'preserve',
            'autopilot': {'paused': False, 'phases': {}, 'history': ['keep'],
                          'operation': None, 'active_author': None}}))
        self.pending = self.root / '.autopilot/HANDOFF_PENDING.json'
        self.before_state = self.state.read_bytes()

    def tearDown(self):
        self.temp.cleanup()

    def cli(self, *args):
        return subprocess.run([sys.executable, str(self.code / 'runner.py'), *args],
                              cwd=self.root, capture_output=True, text=True, timeout=5)

    def probe(self, body):
        path = self.code / 'probe.py'
        path.write_text(body)
        return subprocess.run([sys.executable, str(path)], cwd=self.root,
                              capture_output=True, text=True, timeout=5)

    def assert_untouched(self):
        self.assertEqual(self.state.read_bytes(), self.before_state)
        self.assertFalse((self.code / 'UNEXPECTED_REMOTE_CALL').exists())
        self.assertFalse((self.root / '.autopilot/RUNNING.lock').exists())

    def test_fresh_readonly_status_preserves_real_values(self):
        run = self.cli('status')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('"history"', run.stdout)
        self.assert_untouched()

    def test_pending_transaction_blocks_every_entrypoint_before_mutation(self):
        self.pending.parent.mkdir()
        self.pending.write_text('{"status":"INSTALLING","TEST_ONLY":true}')
        for args in [('status',), ('pr', '--phase', 'P06', '--pr-action', 'merge'),
                     ('resume',), ('reconcile',), ('init',), ('run',),
                     ('run', '--task', 'audio-qa')]:
            with self.subTest(args=args):
                run = self.cli(*args)
                self.assertNotEqual(run.returncode, 0)
                self.assertIn('handoff pending', run.stderr)
                self.assert_untouched()

    def test_even_dangling_pending_marker_blocks(self):
        self.pending.parent.mkdir()
        self.pending.symlink_to(self.root / 'missing-journal')
        run = self.cli('status')
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('handoff pending', run.stderr)
        self.assert_untouched()

    def test_loaded_controller_rechecks_pending_before_lease(self):
        run = self.probe("""
import runner
c=runner.Controller()
runner.HANDOFF_PENDING.parent.mkdir()
runner.HANDOFF_PENDING.write_text('{"TEST_ONLY":true}')
try:
 with c.exclusive(): raise AssertionError('entered')
except runner.Blocked as error:
 assert 'handoff pending' in str(error)
else: raise AssertionError('not blocked')
""")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assert_untouched()

    def test_loaded_runtime_cannot_resume_after_bundle_replacement(self):
        for relative in ['autopilot/github.py', 'autopilot/config.json',
                         'autopilot/worker.py', 'tools/verify_p06.py']:
            with self.subTest(relative=relative):
                run = self.probe(f"""
import runner
c=runner.Controller()
p=runner.ROOT/{relative!r}
p.parent.mkdir(parents=True,exist_ok=True)
p.write_bytes((p.read_bytes() if p.exists() else b'')+b'\\n# changed TEST_ONLY\\n')
try:
 with c.exclusive(): raise AssertionError('entered')
except runner.Blocked as error:
 assert 'runtime changed' in str(error)
else: raise AssertionError('not blocked')
""")
                self.assertEqual(run.returncode, 0, run.stderr)
                # Each next independent import captures the fixture's new baseline.
                if relative.endswith('config.json'):
                    shutil.copy2(ROOT / 'autopilot/config.json', self.code / 'config.json')
                self.assert_untouched()

    def test_constructor_after_old_import_is_also_fenced(self):
        run = self.probe("""
import runner
p=runner.ROOT/'autopilot/runner.py'
p.write_bytes(p.read_bytes()+b'\\n# replacement TEST_ONLY\\n')
try: runner.Controller()
except runner.Blocked as error: assert 'runtime changed' in str(error)
else: raise AssertionError('not blocked')
""")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assert_untouched()

    def test_phase_worktree_cannot_start_second_authority(self):
        (self.root / '.git').write_text('gitdir: TEST_ONLY\n')
        run = self.cli('status')
        self.assertNotEqual(run.returncode, 0)
        self.assertIn('canonical checkout', run.stderr)
        self.assert_untouched()

    def test_cold_new_process_after_completed_change_is_allowed(self):
        path = self.code / 'github.py'
        path.write_text(path.read_text() + '\n# committed fixture replacement\n')
        run = self.cli('status')
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assert_untouched()


if __name__ == '__main__':
    unittest.main()
