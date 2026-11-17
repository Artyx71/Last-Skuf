"""Source-transfer fault boundaries; disposable TEST_ONLY files, never real Game."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import canonical_source_transfer as source
from canonical_source_transfer import CanonicalSourceTransfer,Refused
from cold_runtime_bundle import TARGETS
import cold_bootstrap as fs


class SourceTransferTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        for d in ['.git','.autopilot','automation','game','tools','reports/pre_p07']:
            (self.root/d).mkdir(parents=True,exist_ok=True)
        (self.root/'automation/.executor.lock').touch(mode=0o600)
        self.inode=(self.root/'automation/.executor.lock').stat().st_ino
        (self.root/'.git/index').write_bytes(b'INDEX TEST_ONLY')
        (self.root/'automation/phase_state.json').write_text('{"active_phase":"P07","attempts":2,"autopilot":{"history":["keep"],"paused":false,"phases":{}}}')
        for p in TARGETS:
            dest=self.root/p;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/p).read_bytes())
        (self.root/'autopilot/worker.py').write_bytes(b'# TEST_ONLY worker; never replace\n')
        (self.root/'game/old.gd').write_bytes(b'extends Node\n# OLD TEST_ONLY\n')
        (self.root/'tools/verify.py').write_bytes(b'# OLD VERIFY TEST_ONLY\n')
        self.payloads={'game/old.gd':b'extends Node\n# NEW TEST_ONLY\n',
                       'game/rooms/new.gd':b'extends Node\n# NEW ROOM TEST_ONLY\n',
                       'tools/verify.py':b'# NEW VERIFY TEST_ONLY\n',
                       'tools/verify_p06.py':b'# NEW P06 VERIFY TEST_ONLY\n'}
        runtime=set(TARGETS)|{'autopilot/worker.py','tools/verify.py','tools/verify_p06.py'}
        m=CanonicalSourceTransfer(self.root)
        baseline=self.root/'reports/pre_p07/B-baseline-TEST_ONLY.json'
        baseline.write_text(json.dumps({'schema':1,'TEST_ONLY':True,'runtime_files':m.protected(runtime)}))
        actual=ROOT/'reports/pre_p07/lead-runtime-bundle-B-installed-01/decision.json'
        data=json.loads(actual.read_text());data.update(TEST_ONLY=True,
            post_B_runtime_baseline_path=str(baseline.relative_to(self.root)),
            post_B_runtime_baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest())
        receipt=self.root/'reports/pre_p07/B-TEST_ONLY.json';receipt.write_text(json.dumps(data))
        self.proof={'path':str(receipt.relative_to(self.root)),'sha256':hashlib.sha256(receipt.read_bytes()).hexdigest()}
        self.before=m.protected(self.payloads)
        self.kept_paths=['automation/phase_state.json','.git/index','autopilot/worker.py',self.proof['path']]
        self.kept=m.protected(self.kept_paths)

    def tearDown(self):
        self.assertEqual((self.root/'automation/.executor.lock').stat().st_ino,self.inode)
        self.temp.cleanup()

    def prepare(self):
        with CanonicalSourceTransfer(self.root).lease() as m:
            return m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)

    def test_complete_and_fresh_controller_preserves_progress(self):
        ident=self.prepare()
        with CanonicalSourceTransfer(self.root).lease() as m:result=m.finish_transfer(ident)
        self.assertEqual(result['status'],'COMMIT_VERIFIED')
        for p,b in self.payloads.items():self.assertEqual((self.root/p).read_bytes(),b)
        run=subprocess.run([sys.executable,str(self.root/'autopilot/runner.py'),'status'],capture_output=True,text=True,timeout=5)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(CanonicalSourceTransfer(self.root).protected(self.kept_paths),self.kept)

    def test_actual_exit_before_during_and_after_source_groups_recovers(self):
        for stage in ['before_first_copy','after_copy_0','after_copy_1','after_copy_3','before_commit']:
            for rollback in [False,True]:
                with self.subTest(stage=stage,rollback=rollback),tempfile.TemporaryDirectory() as scratch:
                    root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                    with CanonicalSourceTransfer(root).lease() as m:
                        ident=m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
                    script=root/'terminate_fixture.py'
                    script.write_text('import os,sys\nfrom pathlib import Path\n'+
                        f'sys.path.insert(0,{str(ROOT/"tools")!r})\n'+
                        'from canonical_source_transfer import CanonicalSourceTransfer\n'+
                        f'def stop(stage):\n if stage=={stage!r}: os._exit(78)\n'+
                        f'with CanonicalSourceTransfer(Path({str(root)!r}),hook=stop).lease() as m:m.finish_transfer({ident!r})\n')
                    run=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,timeout=5)
                    self.assertEqual(run.returncode,78,run.stderr)
                    blocked=subprocess.run([sys.executable,str(root/'autopilot/runner.py'),'pause'],capture_output=True,text=True,timeout=5)
                    self.assertNotEqual(blocked.returncode,0);self.assertIn('handoff pending',blocked.stderr)
                    self.assertFalse((root/'.autopilot/PAUSE').exists())
                    with CanonicalSourceTransfer(root).lease() as m:result=m.finish_transfer(ident,rollback=rollback)
                    self.assertEqual(result['status'],'ROLLED_BACK' if rollback else 'COMMIT_VERIFIED')
                    self.assertFalse((root/source.MARKER).exists())
                    self.assertEqual(CanonicalSourceTransfer(root).protected(self.kept_paths),self.kept)
                    if rollback:
                        expected={p:v for p,v in self.before.items() if v is not None}
                        self.assertEqual(CanonicalSourceTransfer(root).inventory(),expected)

    def test_unknown_user_source_is_never_overwritten_or_deleted(self):
        ident=self.prepare();path=self.root/'game/USER_CHANGE.gd';path.write_bytes(b'USER DATA')
        with CanonicalSourceTransfer(self.root).lease() as m:
            for rollback in [False,True]:
                with self.assertRaises(Refused):m.finish_transfer(ident,rollback=rollback)
        self.assertEqual(path.read_bytes(),b'USER DATA');self.assertTrue((self.root/source.MARKER).exists())

    def test_immutable_intent_backup_and_state_corruption_block(self):
        for mutation in ['intent','backup','state','mode']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as scratch:
                root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                with CanonicalSourceTransfer(root).lease() as m:
                    ident=m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
                    folder=root/'.autopilot/canonical-transfers'/ident
                    if mutation=='intent':
                        d=json.loads((folder/'intent.json').read_text());d['protected']={};(folder/'intent.json').write_text(json.dumps(d))
                    if mutation=='backup':(folder/'0.old').write_bytes(b'CORRUPT')
                    if mutation=='state':(root/'automation/phase_state.json').write_bytes(b'NEW HISTORY')
                    if mutation=='mode':(root/'game/old.gd').chmod(0o777)
                    with self.assertRaises(Refused):m.finish_transfer(ident,rollback=True)
                    self.assertEqual((root/'game/old.gd').read_bytes(),b'extends Node\n# OLD TEST_ONLY\n')
                    self.assertTrue((root/source.MARKER).exists())

    def test_missing_initial_marker_repairs_original_and_blocks_second_begin(self):
        real=source.writejson
        def deny(path,data):
            if path==self.root/source.MARKER:raise PermissionError('TEST_ONLY marker write')
            return real(path,data)
        with CanonicalSourceTransfer(self.root).lease() as m:
            with patch.object(source,'writejson',side_effect=deny):
                with self.assertRaises(PermissionError):m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
            ident=next((self.root/'.autopilot/canonical-transfers').iterdir()).name
            with self.assertRaises(Refused):m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
            result=m.finish_transfer(ident,rollback=True)
        self.assertEqual(result['status'],'ROLLED_BACK')
        self.assertEqual(CanonicalSourceTransfer(self.root).protected(self.kept_paths),self.kept)

    def test_partial_source_with_missing_marker_is_not_silently_readmitted(self):
        ident=self.prepare()
        def stop(stage):
            if stage=='after_copy_0':raise InterruptedError('TEST_ONLY')
        with CanonicalSourceTransfer(self.root,hook=stop).lease() as m:
            with self.assertRaises(InterruptedError):m.finish_transfer(ident)
        (self.root/source.MARKER).unlink()
        with CanonicalSourceTransfer(self.root).lease() as m:
            with self.assertRaises(Refused):m.finish_transfer(ident)

    def test_after_commit_rechecks_protected_state(self):
        ident=self.prepare()
        def mutate(stage):
            if stage=='after_commit':(self.root/'automation/phase_state.json').write_bytes(b'NEW HISTORY')
        with CanonicalSourceTransfer(self.root,hook=mutate).lease() as m:
            with self.assertRaises(Refused):m.finish_transfer(ident)
        self.assertTrue((self.root/source.MARKER).exists())
        self.assertEqual((self.root/'automation/phase_state.json').read_bytes(),b'NEW HISTORY')

    def test_precommit_lock_replacement_cannot_clear_marker(self):
        with tempfile.TemporaryDirectory() as scratch:
            root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
            lock=root/'automation/.executor.lock'
            def replace(stage):
                if stage=='before_commit':
                    lock.rename(lock.with_name('old-inode'));lock.touch(mode=0o600)
            with CanonicalSourceTransfer(root,hook=replace).lease() as m:
                ident=m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
                with self.assertRaises(Refused):m.finish_transfer(ident)
            self.assertTrue((root/source.MARKER).exists())
            journal=root/'.autopilot/canonical-transfers'/ident/'journal.json'
            self.assertEqual(json.loads(journal.read_text())['status'],'PREPARED')

    def test_write_fsync_rename_failures_preserve_pending(self):
        for syscall in ['fsync','replace']:
            with self.subTest(syscall=syscall),tempfile.TemporaryDirectory() as scratch:
                root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                with CanonicalSourceTransfer(root).lease() as m:
                    ident=m.begin_transfer(self.payloads,self.before,self.kept_paths,self.proof)
                    with patch.object(fs.os,syscall,side_effect=PermissionError('TEST_ONLY denied')):
                        with self.assertRaises(PermissionError):m.finish_transfer(ident)
                    self.assertTrue((root/source.MARKER).exists())
                    m.finish_transfer(ident,rollback=True)
                self.assertEqual(CanonicalSourceTransfer(root).protected(self.kept_paths),self.kept)


if __name__=='__main__':unittest.main()
