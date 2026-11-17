"""Bundle recovery with real subprocess termination in disposable checkouts."""
import hashlib
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
from bootstrap_runtime_fence import build
import cold_runtime_bundle as bundle
from cold_runtime_bundle import RuntimeBundle, TARGETS, Refused
import cold_bootstrap as fs

A = build((ROOT / 'tools/fixtures/autopilot_legacy_02b.py.txt').read_bytes(),
          (ROOT / 'autopilot/runner.py').read_bytes())
PAYLOADS = {p: (ROOT / p).read_bytes() for p in TARGETS}


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for directory in ['.git', '.autopilot', 'automation', 'autopilot/prompts', 'reports/pre_p07']:
            (self.root / directory).mkdir(parents=True, exist_ok=True)
        (self.root / 'automation/.executor.lock').touch(mode=0o600)
        self.inode = (self.root / 'automation/.executor.lock').stat().st_ino
        (self.root / 'autopilot/runner.py').write_bytes(A)
        (self.root / 'autopilot/github.py').write_text('# OLD TEST_ONLY, no network\n')
        (self.root / 'autopilot/config.json').write_text('{"stop_after_phase":"P06"}')
        (self.root / 'autopilot/review_schema.json').write_text('{"OLD_TEST_ONLY":true}')
        (self.root / 'autopilot/prompts/INDEPENDENT_REVIEW.md').write_text('OLD TEST_ONLY')
        (self.root / 'autopilot/worker.py').write_text('# never replace this worker\n')
        (self.root / '.git/index').write_bytes(b'INDEX TEST_ONLY')
        self.state = self.root / 'automation/phase_state.json'
        self.state.write_text('{"active_phase":"P07","attempts":2,"autopilot":{"history":["retain"],"phases":{},"paused":false}}')
        self.state_bytes = self.state.read_bytes()
        receipt = self.root / 'reports/pre_p07/installed-A.json'
        # Use the actual installed-A wire schema; notably it has role, not reviewer.
        record=json.loads((ROOT/'reports/pre_p07/lead-bootstrap-A-installed-01/decision.json').read_text())
        baseline=self.root/'reports/pre_p07/baseline-TEST_ONLY.json'
        names=set(TARGETS)|{'autopilot/worker.py','tools/verify.py','tools/verify_p06.py'}
        baseline.write_text(json.dumps({'schema':1,'TEST_ONLY':True,'runtime_files':RuntimeBundle(self.root).protected(names)}))
        record.update(TEST_ONLY=True,post_A_runtime_baseline_path=str(baseline.relative_to(self.root)),
                      post_A_runtime_baseline_sha256=hashlib.sha256(baseline.read_bytes()).hexdigest())
        receipt.write_text(json.dumps(record))
        self.proof = {'path':str(receipt.relative_to(self.root)), 'sha256':hashlib.sha256(receipt.read_bytes()).hexdigest()}
        self.protected = ['automation/phase_state.json','autopilot/worker.py','.git/index',self.proof['path']]
        self.before = RuntimeBundle(self.root).protected(TARGETS)
        self.kept = RuntimeBundle(self.root).protected(self.protected)

    def tearDown(self):
        self.assertEqual((self.root / 'automation/.executor.lock').stat().st_ino, self.inode)
        self.temp.cleanup()

    def prepare(self):
        with RuntimeBundle(self.root).lease() as install:
            return install.begin_bundle(PAYLOADS, self.before, self.protected, self.proof)

    def assert_kept(self):
        self.assertEqual(RuntimeBundle(self.root).protected(self.protected), self.kept)
        self.assertEqual(self.state.read_bytes(), self.state_bytes)
        self.assertFalse((self.root / '.autopilot/RUNNING.lock').exists())

    def test_complete_bundle_fresh_process_preserves_authority(self):
        ident = self.prepare()
        with RuntimeBundle(self.root).lease() as install:
            result = install.finish_bundle(ident)
        self.assertEqual(result['status'], 'COMMIT_VERIFIED')
        for name, expected in TARGETS.items():
            self.assertEqual(hashlib.sha256((self.root / name).read_bytes()).hexdigest(), expected)
        run = subprocess.run([sys.executable,str(self.root / 'autopilot/runner.py'),'status'],
                             cwd=self.root,capture_output=True,text=True,timeout=5)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assert_kept()

    def test_actual_process_exit_at_all_copy_boundaries_can_resume_or_rollback(self):
        stages = ['before_first_replace'] + ['after_replace_'+str(i) for i in range(7)] + ['before_commit']
        for stage in stages:
            for rollback in [False,True]:
                with self.subTest(stage=stage,rollback=rollback), tempfile.TemporaryDirectory() as scratch:
                    root = Path(scratch) / 'checkout'
                    shutil.copytree(self.root,root)
                    with RuntimeBundle(root).lease() as install:
                        ident = install.begin_bundle(PAYLOADS, self.before, self.protected, self.proof)
                    script = root / 'terminate_fixture.py'
                    script.write_text('import os,sys\nfrom pathlib import Path\n'
                        f'sys.path.insert(0,{str(ROOT / "tools")!r})\n'
                        'from cold_runtime_bundle import RuntimeBundle\n'
                        f'def stop(stage):\n if stage=={stage!r}: os._exit(77)\n'
                        f'with RuntimeBundle(Path({str(root)!r}),hook=stop).lease() as i: i.finish_bundle({ident!r})\n')
                    run = subprocess.run([sys.executable,str(script)],capture_output=True,text=True,timeout=5)
                    self.assertEqual(run.returncode,77,run.stderr)
                    self.assertTrue((root / bundle.MARKER).exists())
                    blocked = subprocess.run([sys.executable,str(root / 'autopilot/runner.py'),'pause'],
                                             capture_output=True,text=True,timeout=5)
                    self.assertNotEqual(blocked.returncode,0)
                    self.assertIn('handoff pending',blocked.stderr)
                    self.assertFalse((root / '.autopilot/PAUSE').exists())
                    with RuntimeBundle(root).lease() as install:
                        outcome = install.finish_bundle(ident,rollback=rollback)
                    self.assertEqual(outcome['status'],'ROLLED_BACK' if rollback else 'COMMIT_VERIFIED')
                    self.assertEqual(RuntimeBundle(root).protected(self.protected),self.kept)
                    self.assertFalse((root / bundle.MARKER).exists())
                    self.assertTrue((root / bundle.LEDGER).exists())
                    if rollback:
                        self.assertEqual(RuntimeBundle(root).protected(TARGETS),self.before)
                        self.assertEqual((root / 'autopilot/runner.py').read_bytes(),A)
                        self.assertFalse((root / 'autopilot/readiness.py').exists())

    def test_pending_bundle_blocks_every_operational_entrypoint(self):
        self.prepare()
        for argv in [['status'],['pause'],['resume'],['init'],['reconcile'],['run'],
                     ['run','--task','audio-qa'],['pr','--phase','P06','--pr-action','merge']]:
            with self.subTest(argv=argv):
                run = subprocess.run([sys.executable,str(self.root / 'autopilot/runner.py'),*argv],
                                     capture_output=True,text=True,timeout=5)
                self.assertNotEqual(run.returncode,0)
                self.assertIn('handoff pending',run.stderr)
                self.assert_kept()

    def test_unknown_target_or_backup_or_intent_mutation_is_not_overwritten(self):
        for mutation in ['target','backup','intent','marker','protected']:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as scratch:
                root = Path(scratch) / 'checkout';shutil.copytree(self.root,root)
                with RuntimeBundle(root).lease() as install:
                    ident = install.begin_bundle(PAYLOADS,self.before,self.protected,self.proof)
                    folder = root / '.autopilot/runtime-bundles' / ident
                    if mutation == 'target': (root / 'autopilot/github.py').write_bytes(b'USER CHANGE')
                    if mutation == 'backup': (folder / '1.old').write_bytes(b'CORRUPT')
                    if mutation == 'intent':
                        d=json.loads((folder/'intent.json').read_text());d['protected']={};(folder/'intent.json').write_text(json.dumps(d))
                    if mutation == 'marker':
                        d=json.loads((root/bundle.MARKER).read_text());d['intent_sha256']='0'*64;(root/bundle.MARKER).write_text(json.dumps(d))
                    if mutation == 'protected': (root/'automation/phase_state.json').write_bytes(b'NEW HISTORY')
                    before=(root/'autopilot/github.py').read_bytes()
                    with self.assertRaises(Refused): install.finish_bundle(ident,rollback=True)
                    self.assertEqual((root/'autopilot/github.py').read_bytes(),before)
                    self.assertTrue((root/bundle.MARKER).exists())

    def test_missing_readiness_or_bad_json_target_refuses_before_intent(self):
        for variant in ['missing','bad_json']:
            payloads=dict(PAYLOADS)
            if variant=='missing': del payloads['autopilot/readiness.py']
            else:payloads['autopilot/config.json']=b'{BROKEN'
            with RuntimeBundle(self.root).lease() as install:
                with self.assertRaises(Refused):install.begin_bundle(payloads,self.before,self.protected,self.proof)
            self.assertFalse((self.root/bundle.MARKER).exists())
        self.assert_kept()

    def test_symlink_and_unguarded_baseline_refused(self):
        self.prepare()
        target=self.root/'autopilot/readiness.py';target.symlink_to(self.state)
        ident=json.loads((self.root/bundle.MARKER).read_text())['id']
        with RuntimeBundle(self.root).lease() as install:
            with self.assertRaises(Refused):install.finish_bundle(ident)
        self.assert_kept()

    def test_runtime_fsync_rename_write_failures_keep_pending_and_allow_rollback(self):
        for syscall in ['fsync','replace','open']:
            with self.subTest(syscall=syscall),tempfile.TemporaryDirectory() as scratch:
                root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                with RuntimeBundle(root).lease() as install:
                    ident=install.begin_bundle(PAYLOADS,self.before,self.protected,self.proof)
                    real_open=fs.os.open
                    def deny_write(path,flags,*args,**kw):
                        if flags & os.O_WRONLY:raise PermissionError('TEST_ONLY write denied')
                        return real_open(path,flags,*args,**kw)
                    effect=deny_write if syscall=='open' else PermissionError('TEST_ONLY denied')
                    with patch.object(fs.os,syscall,side_effect=effect):
                        with self.assertRaises(PermissionError):install.finish_bundle(ident)
                    self.assertTrue((root/bundle.MARKER).exists())
                    install.finish_bundle(ident,rollback=True)
                self.assertEqual(RuntimeBundle(root).protected(TARGETS),self.before)
                self.assertEqual(RuntimeBundle(root).protected(self.protected),self.kept)

    def test_actual_147c_installed_receipt_wire_is_accepted_without_reviewer_field(self):
        src=ROOT/'reports/pre_p07/lead-bootstrap-A-installed-01'
        record=json.loads((src/'decision.json').read_text())
        self.assertNotIn('reviewer',record)
        target=self.root/'reports/pre_p07/real-A-wire.json'
        target.write_bytes((src/'decision.json').read_bytes())
        baseline=self.root/record['post_A_runtime_baseline_path']
        baseline.parent.mkdir(parents=True,exist_ok=True)
        baseline.write_bytes((src/'post-A-runtime-baseline.json').read_bytes())
        with RuntimeBundle(self.root).lease() as install:
            verified=install.verify_a({'path':str(target.relative_to(self.root)),
                'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        self.assertEqual(verified['autopilot/runner.py']['sha256'],fs.BOOTSTRAP_SHA)

    def test_failed_pending_marker_repairs_same_prepare_and_blocks_new_begin(self):
        for rollback in [False,True]:
            with self.subTest(rollback=rollback),tempfile.TemporaryDirectory() as scratch:
                root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                real_write=bundle.writejson
                def fail_marker(path,data):
                    if path==root/bundle.MARKER:raise PermissionError('TEST_ONLY marker write')
                    return real_write(path,data)
                with RuntimeBundle(root).lease() as install:
                    with patch.object(bundle,'writejson',side_effect=fail_marker):
                        with self.assertRaises(PermissionError):
                            install.begin_bundle(PAYLOADS,self.before,self.protected,self.proof)
                    ident=json.loads((root/bundle.LEDGER).read_text())['transactions'][-1]
                    with self.assertRaises(Refused):
                        install.begin_bundle(PAYLOADS,self.before,self.protected,self.proof)
                    result=install.finish_bundle(ident,rollback=rollback)
                self.assertEqual(result['status'],'ROLLED_BACK' if rollback else 'COMMIT_VERIFIED')
                self.assertEqual(len(json.loads((root/bundle.LEDGER).read_text())['transactions']),1)
                self.assertEqual(RuntimeBundle(root).protected(self.protected),self.kept)

    def test_load_rejects_the_same_malformed_ledgers_as_begin(self):
        for kind in ['dictionary','string','duplicate','invalid_id','boolean_schema']:
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as scratch:
                root=Path(scratch)/'checkout';shutil.copytree(self.root,root)
                with RuntimeBundle(root).lease() as install:
                    ident=install.begin_bundle(PAYLOADS,self.before,self.protected,self.proof)
                    values={'dictionary':{ident:True},'string':ident,'duplicate':[ident,ident],
                            'invalid_id':[ident,'../escape'],'boolean_schema':[ident]}
                    data={'schema':True if kind=='boolean_schema' else 1,'transactions':values[kind]}
                    (root/bundle.LEDGER).write_text(json.dumps(data))
                    with self.assertRaises(Refused):install.finish_bundle(ident)
                    self.assertEqual(RuntimeBundle(root).protected(TARGETS),self.before)
                    self.assertTrue((root/bundle.MARKER).exists())

    def test_component_or_stale_A_receipt_cannot_authorize_bundle(self):
        path=self.root/self.proof['path'];d=json.loads(path.read_text());d['actual_A_verified']=False;path.write_text(json.dumps(d))
        proof=dict(self.proof,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        with RuntimeBundle(self.root).lease() as install:
            with self.assertRaises(Refused):install.begin_bundle(PAYLOADS,self.before,self.protected,proof)
        self.assertFalse((self.root/bundle.MARKER).exists())


if __name__ == '__main__': unittest.main()
