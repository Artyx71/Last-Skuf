"""Actual filesystem/flock/subprocess probes in temporary checkouts only."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from bootstrap_runtime_fence import build, legacy_ast, sha
import cold_bootstrap as cb
from cold_bootstrap import Bootstrap, Refused

OLD = (ROOT / 'tools/fixtures/autopilot_legacy_02b.py.txt').read_bytes()
FENCE = (ROOT / 'autopilot/runner.py').read_bytes()
NEW = build(OLD, FENCE)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ['.git', '.autopilot', 'automation', 'autopilot']:
            (self.root / directory).mkdir()
        self.runner = self.root / cb.RUNNER
        self.runner.write_bytes(OLD)
        self.runner.chmod(0o755)
        self.lock = self.root / 'automation/.executor.lock'
        self.lock.touch(mode=0o600)
        self.inode = self.lock.stat().st_ino
        self.state = self.root / 'automation/phase_state.json'
        self.state.write_text('{"active_phase":"P07","attempts":2,"autopilot":{"history":["keep"],"paused":false}}')
        self.state_before = self.state.read_bytes()
        (self.root / 'autopilot/config.json').write_text('{}')
        self.protected = ['automation/phase_state.json', 'autopilot/config.json', '.autopilot/STATE.json']

    def tearDown(self):
        self.assertEqual(self.lock.stat().st_ino, self.inode)
        self.temp.cleanup()

    def begin(self):
        with Bootstrap(self.root).lease() as install:
            return install.begin(NEW, self.protected)

    def assert_state(self):
        self.assertEqual(self.state.read_bytes(), self.state_before)
        self.assertFalse((self.root / '.autopilot/STATE.json').exists())
        self.assertFalse((self.root / '.autopilot/RUNNING.lock').exists())

    def test_builder_is_hash_pinned_and_legacy_ast_equivalent(self):
        self.assertEqual(sha(NEW), cb.BOOTSTRAP_SHA)
        self.assertEqual(legacy_ast(OLD), legacy_ast(NEW, True))
        for old, fence in [(OLD+b'\n', FENCE), (OLD, FENCE+b'\n')]:
            with self.assertRaises(ValueError):
                build(old, fence)

    def test_apply_and_fresh_readonly_process(self):
        ident = self.begin()
        with Bootstrap(self.root).lease() as install:
            record = install.finish(ident)
        self.assertEqual(record['status'], 'VERIFIED')
        self.assertEqual(self.runner.read_bytes(), NEW)
        self.assertEqual(self.runner.stat().st_mode & 0o777, 0o755)
        run = subprocess.run([sys.executable, str(self.runner), 'status'], cwd=self.root,
                             capture_output=True, text=True, timeout=5)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn('"history"', run.stdout)
        self.assert_state()

    def test_every_interruption_boundary_recovers_old_or_guarded_old(self):
        for stage in ['prepared', 'before_replace', 'after_replace', 'before_commit', 'after_commit']:
            for rollback in [False, True]:
                if stage == 'after_commit' and rollback:
                    continue  # durable terminal outcome is immutable
                with self.subTest(stage=stage, rollback=rollback):
                    with tempfile.TemporaryDirectory() as scratch:
                        root = Path(scratch) / 'checkout'
                        shutil.copytree(self.root, root)
                        def crash(at):
                            if at == stage:
                                raise InterruptedError(at)
                        with Bootstrap(root, hook=crash).lease() as install:
                            if stage == 'prepared':
                                with self.assertRaises(InterruptedError):
                                    install.begin(NEW, self.protected)
                            else:
                                ident = install.begin(NEW, self.protected)
                                with self.assertRaises(InterruptedError):
                                    install.finish(ident)
                        marker = json.loads((root / cb.MARKER).read_text())
                        self.assertIn((root / cb.RUNNER).read_bytes(), (OLD, NEW))
                        with Bootstrap(root).lease() as recovery:
                            recovery.finish(marker['id'], rollback=rollback)
                        self.assertEqual((root / cb.RUNNER).read_bytes(), OLD if rollback else NEW)
                        self.assertEqual((root / 'automation/phase_state.json').read_bytes(), self.state_before)
                        self.assertFalse((root / cb.MARKER).exists())

    def test_busy_real_flock_refuses_without_touching_source(self):
        fd = os.open(self.lock, os.O_RDWR)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaises(BlockingIOError):
                with Bootstrap(self.root).lease():
                    self.fail('Concurrent maintenance admitted')
        finally:
            os.close(fd)
        self.assertEqual(self.runner.read_bytes(), OLD)
        self.assert_state()

    def test_changed_source_protected_state_and_backup_are_not_overwritten(self):
        for changed in ['runner', 'state', 'backup', 'candidate', 'mode']:
            with self.subTest(changed=changed):
                with tempfile.TemporaryDirectory() as scratch:
                    root = Path(scratch) / 'checkout'
                    shutil.copytree(self.root, root)
                    with Bootstrap(root).lease() as install:
                        ident = install.begin(NEW, self.protected)
                        if changed == 'runner': (root / cb.RUNNER).write_bytes(b'USER CHANGE')
                        if changed == 'state': (root / 'automation/phase_state.json').write_bytes(b'NEW HISTORY')
                        if changed in ['backup', 'candidate']:
                            name = 'old.py' if changed == 'backup' else 'new.py'
                            (root / '.autopilot/bootstrap' / ident / name).write_bytes(b'CORRUPT')
                        if changed == 'mode': (root / cb.RUNNER).chmod(0o644)
                        prior = (root / cb.RUNNER).read_bytes()
                        with self.assertRaises(Refused): install.finish(ident, rollback=True)
                        self.assertEqual((root / cb.RUNNER).read_bytes(), prior)
                        self.assertTrue((root / cb.MARKER).exists())

    def test_symlink_and_changed_lock_are_refused(self):
        ident = self.begin()
        self.runner.unlink()
        self.runner.symlink_to(self.state)
        with Bootstrap(self.root).lease() as install:
            with self.assertRaises(Refused): install.finish(ident)
        self.assert_state()

    def test_bundle_dependency_forbids_A_rollback(self):
        ident = self.begin()
        (self.root / cb.B_HISTORY).write_text('{"B":"started"}')
        with Bootstrap(self.root).lease() as install:
            with self.assertRaises(Refused): install.finish(ident, rollback=True)
        self.assertEqual(self.runner.read_bytes(), OLD)

    def test_os_write_fsync_and_replace_errors_do_not_claim_commit(self):
        for syscall in ['fsync', 'replace']:
            with self.subTest(syscall=syscall):
                ident = self.begin()
                with Bootstrap(self.root).lease() as install:
                    with patch.object(cb.os, syscall, side_effect=PermissionError('TEST_ONLY')):
                        with self.assertRaises(PermissionError): install.finish(ident)
                self.assertTrue((self.root / cb.MARKER).exists())
                journal = self.root / '.autopilot/bootstrap' / ident / 'journal.json'
                self.assertEqual(json.loads(journal.read_text())['status'], 'PREPARED')
                with Bootstrap(self.root).lease() as install:
                    install.finish(ident, rollback=True)
                self.assertEqual(self.runner.read_bytes(), OLD)
        self.assert_state()

    def test_duplicate_json_and_missing_intent_are_refused(self):
        ident = self.begin()
        marker = self.root / cb.MARKER
        original = marker.read_bytes()
        marker.write_text('{"id":"x","id":"y"}')
        with Bootstrap(self.root).lease() as install:
            with self.assertRaises(Refused): install.finish(ident)
        marker.write_bytes(original)
        marker.unlink()
        with Bootstrap(self.root).lease() as install:
            with self.assertRaises(Refused): install.finish(ident)
        self.assertEqual(self.runner.read_bytes(), OLD)

    def test_immutable_intent_and_marker_corruption_are_refused(self):
        for mutation in ['protected', 'mode', 'marker']:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch) / 'checkout'
                shutil.copytree(self.root, root)
                with Bootstrap(root).lease() as install:
                    ident = install.begin(NEW, self.protected)
                    intent = root / '.autopilot/bootstrap' / ident / 'intent.json'
                    if mutation == 'marker':
                        marker = root / cb.MARKER
                        d = json.loads(marker.read_text())
                        d['intent_sha256'] = '0' * 64
                        marker.write_text(json.dumps(d))
                    else:
                        d = json.loads(intent.read_text())
                        if mutation == 'protected':
                            d['protected'] = {}
                            (root / 'automation/phase_state.json').write_bytes(b'NEW HISTORY')
                        else:
                            d['target']['mode'] = 0o777
                        intent.write_text(json.dumps(d))
                    with self.assertRaises(Refused): install.finish(ident)
                    self.assertEqual((root / cb.RUNNER).read_bytes(), OLD)
                    self.assertTrue((root / cb.MARKER).exists())

    def test_precommit_lock_replacement_cannot_clear_marker(self):
        # Separate fixture: replacement itself is the injected fault, so the
        # enclosing test's persistent-lock invariant must not be weakened.
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / 'checkout'
            shutil.copytree(self.root, root)
            lock = root / 'automation/.executor.lock'
            def replace_lock(stage):
                if stage == 'before_commit':
                    lock.rename(lock.with_name('old-inode'))
                    lock.touch(mode=0o600)
            with Bootstrap(root, hook=replace_lock).lease() as install:
                ident = install.begin(NEW, self.protected)
                with self.assertRaises(Refused): install.finish(ident)
            self.assertTrue((root / cb.MARKER).exists())
            journal = root / '.autopilot/bootstrap' / ident / 'journal.json'
            self.assertEqual(json.loads(journal.read_text())['status'], 'PREPARED')

    def test_after_commit_mutation_preserves_intent_for_independent_recovery(self):
        ident = self.begin()
        def mutate(stage):
            if stage == 'after_commit':
                (self.root / 'autopilot/config.json').write_bytes(b'NEW CONFIG')
        with Bootstrap(self.root, hook=mutate).lease() as install:
            with self.assertRaises(Refused): install.finish(ident)
        self.assertTrue((self.root / cb.MARKER).exists())
        self.assertEqual((self.root / 'autopilot/config.json').read_bytes(), b'NEW CONFIG')
        self.assert_state()

    def test_candidate_must_be_exact_reviewed_build(self):
        with Bootstrap(self.root).lease() as install:
            with self.assertRaises(Refused): install.begin(NEW+b'\n', self.protected)
        self.assertFalse((self.root / cb.MARKER).exists())
        self.assert_state()


if __name__ == '__main__':
    unittest.main()

# Exercise the same actual CLI/loaded-process/cross-root controls on A, rather
# than assuming that extracting the reviewed guard preserves its integration.
import test_runtime_fence as fence_tests


class GuardedLegacyFenceTests(fence_tests.RuntimeFenceTests):
    def setUp(self):
        super().setUp()
        (self.code / 'runner.py').write_bytes(NEW)
