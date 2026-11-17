#!/usr/bin/env python3
"""Cold runtime bundle B after independently verified bootstrap A.

Only seven pinned runtime files are writable. No Controller, engine, Git state,
phase advancement or authority restoration. Caller must hold the inherited
canonical maintenance lease and separately pass exact-plan independent review.
"""
import json
import os
from pathlib import Path
import uuid

from cold_bootstrap import (Bootstrap, BOOTSTRAP_SHA, Refused, atomic, checked,
                            fingerprint, parsejson, readjson, sha, syncdir, writejson)

# Install dependencies before runner: a crash must still reach the admission
# fence, rather than fail on a missing readiness import. Rollback uses reverse order.
TARGETS = {
    'autopilot/readiness.py': 'ed539635e4d8cd4d9f7d770ce591a73830343b2bd2a333eb7f08b9991cf44a4e',
    'autopilot/github.py': '3a7d7c7011c08631b377a1b4aa21b17dbc4be58e11a1bead18e8a414eee83fba',
    'autopilot/config.json': 'd004b30737356e1c18b7a9819ce9e32aaa2ef2a4e4008194a30638314139c95d',
    'autopilot/review_schema.json': '45bdeb187e2419076086a372c4f0cab0a0d6b3f2d5c4376df90c72e40dc3f5ae',
    'autopilot/prompts/INDEPENDENT_REVIEW.md': '09dafcfa7229f59b36b7b5735417990880496a1b7d41805c5cd03eb0c07a37ff',
    'autopilot/PRODUCTION_GATES.md': '9d74e56c6fea921ce0c9ef7a7af8925189891a179193ffda5fb1094df0a81ef6',
    'autopilot/runner.py': 'd700e88e585a2dfb4455290421109a7209acb34dd6fd6730afaf24bc3a6fe3a0',
}
MARKER = '.autopilot/HANDOFF_PENDING.json'
LEDGER = '.autopilot/RUNTIME_BUNDLE_STARTED.json'


class RuntimeBundle(Bootstrap):
    def verify_a(self, proof):
        relative = proof['path']
        if not relative.startswith('reports/pre_p07/'):
            raise Refused('Independent installed-A receipt required')
        blob = checked(self.root, relative).read_bytes()
        if sha(blob) != proof['sha256']:
            raise Refused('Installed-A receipt changed')
        data = parsejson(blob)
        if data.get('schema') != 1 or data.get('role') != 'INDEPENDENT_LEAD_ACTUAL_INSTALL_VERIFIER' or data.get('scope') != 'ACTUAL_SINGLE_FILE_BOOTSTRAP_A_INSTALLED_AND_POST_A_BASELINE_ONLY' or data.get('status') != 'PASS' or data.get('actual_A_verified') is not True or data.get('installed_runner_sha256') != BOOTSTRAP_SHA or data.get('journal_status') != 'VERIFIED' or data.get('state_continuity_verified') is not True:
            raise Refused('A component/execution GO is not installed-A verification')
        baseline_path = data.get('post_A_runtime_baseline_path', '')
        if not baseline_path.startswith('reports/pre_p07/'):
            raise Refused('Installed-A runtime baseline path missing')
        baseline_blob = checked(self.root, baseline_path).read_bytes()
        if sha(baseline_blob) != data.get('post_A_runtime_baseline_sha256'):
            raise Refused('Installed-A baseline binding failed')
        baseline = parsejson(baseline_blob)
        files = baseline.get('runtime_files')
        if not isinstance(files, dict) or set(files) != set(TARGETS) | {'autopilot/worker.py','tools/verify.py','tools/verify_p06.py'} or files['autopilot/runner.py']['sha256'] != BOOTSTRAP_SHA:
            raise Refused('Incomplete post-A runtime baseline')
        return files

    def refuse_unfinished_preparation(self):
        parent = checked(self.root, '.autopilot/runtime-bundles')
        if parent.exists():
            for directory in parent.iterdir():
                journal = checked(self.root, str(directory.relative_to(self.root)) + '/journal.json')
                if journal.exists() and readjson(journal).get('status') not in ('COMMIT_VERIFIED','ROLLED_BACK'):
                    raise Refused('Recover existing preparation before starting a new bundle')

    def begin_bundle(self, payloads, expected_before, protected_paths, installed_a):
        self.check_lock()
        if set(payloads) != set(TARGETS) or set(expected_before) != set(TARGETS):
            raise Refused('Exactly seven runtime targets required')
        if set(protected_paths) & set(TARGETS):
            raise Refused('Writable runtime cannot be a protected input')
        a_baseline = self.verify_a(installed_a)
        if self.protected(a_baseline) != a_baseline:
            raise Refused('Current runtime differs from independently verified A')
        self.refuse_unfinished_preparation()
        if checked(self.root, MARKER).exists() or checked(self.root, '.autopilot/BOOTSTRAP_PENDING.json').exists():
            raise Refused('Earlier maintenance is pending')
        before = self.protected(TARGETS)
        if before != expected_before or before['autopilot/runner.py']['sha256'] != BOOTSTRAP_SHA:
            raise Refused('Post-A baseline differs; refuse unguarded rollback baseline')
        protected = self.protected(protected_paths)
        for relative, blob in payloads.items():
            if sha(blob) != TARGETS[relative]:
                raise Refused('Unreviewed/missing target: ' + relative)
            if relative.endswith('.py'):
                compile(blob, relative, 'exec')
            elif relative.endswith('.json'):
                parsejson(blob)
        config = parsejson(payloads['autopilot/config.json'])
        if config.get('stop_after_phase') != 'P06':
            raise Refused('Bundle installation cannot enable P07')
        parent = checked(self.root, '.autopilot/runtime-bundles')
        if not parent.exists():
            parent.mkdir(mode=0o700)
            syncdir(parent.parent)
        folder = parent / uuid.uuid4().hex
        folder.mkdir(mode=0o700)
        syncdir(parent)
        target = {}
        for i, relative in enumerate(TARGETS):
            old = before[relative]
            if old is not None:
                if (old['uid'], old['gid']) != (os.geteuid(), os.getegid()):
                    raise Refused('Cannot preserve runtime ownership')
                atomic(folder / f'{i}.old', checked(self.root, relative).read_bytes())
                if sha((folder / f'{i}.old').read_bytes()) != old['sha256']:
                    raise Refused('Backup verification failed')
            target[relative] = {'sha256': TARGETS[relative], 'mode': old['mode'] if old else 0o644,
                                'uid': os.geteuid(), 'gid': os.getegid()}
            atomic(folder / f'{i}.new', payloads[relative])
            if sha((folder / f'{i}.new').read_bytes()) != TARGETS[relative]:
                raise Refused('Target backup verification failed')
        intent = {'schema': 1, 'kind': 'RUNTIME_BUNDLE_B', 'root': str(self.root),
                  'id': folder.name, 'lock': list(self.identity), 'before': before,
                  'target': target, 'protected': protected, 'installed_a': installed_a}
        intent_blob = (json.dumps(intent, ensure_ascii=False, indent=2) + '\n').encode()
        atomic(folder / 'intent.json', intent_blob)
        intent_sha = sha(intent_blob)
        if (folder / 'intent.json').read_bytes() != intent_blob:
            raise Refused('Prepared intent changed before binding')
        writejson(folder / 'journal.json', {'id': folder.name, 'intent_sha256': intent_sha, 'status': 'PREPARED'})
        ledger_path = checked(self.root, LEDGER)
        ledger = readjson(ledger_path) if ledger_path.exists() else {'schema': 1, 'transactions': []}
        if ledger.get('schema') != 1 or not isinstance(ledger.get('transactions'), list):
            raise Refused('Invalid bundle-start ledger')
        ledger['transactions'].append(folder.name)
        writejson(ledger_path, ledger)  # remains after rollback: never un-fence A
        writejson(checked(self.root, MARKER), {'id': folder.name, 'intent_sha256': intent_sha})
        self.hook('prepared')
        return folder.name

    def load_bundle(self, ident, allow_prepare_repair=False):
        self.check_lock()
        if len(ident) != 32 or any(c not in '0123456789abcdef' for c in ident):
            raise Refused('Invalid bundle ID')
        relative = '.autopilot/runtime-bundles/' + ident
        folder = checked(self.root, relative)
        blob = checked(self.root, relative + '/intent.json').read_bytes()
        intent_sha = sha(blob)
        intent = parsejson(blob)
        journal = readjson(checked(self.root, relative + '/journal.json'))
        if set(intent) != {'schema','kind','root','id','lock','before','target','protected','installed_a'} or intent.get('schema') != 1 or intent.get('kind') != 'RUNTIME_BUNDLE_B' or intent.get('root') != str(self.root) or intent.get('id') != ident or intent.get('lock') != list(self.identity):
            raise Refused('Invalid immutable bundle identity')
        if journal.get('id') != ident or journal.get('intent_sha256') != intent_sha or journal.get('status') not in ('PREPARED','COMMIT_VERIFIED','ROLLED_BACK'):
            raise Refused('Bundle journal binding failed')
        if set(intent['before']) != set(TARGETS) or set(intent['target']) != set(TARGETS):
            raise Refused('Runtime allowlist changed')
        if intent['before']['autopilot/runner.py']['sha256'] != BOOTSTRAP_SHA:
            raise Refused('Rollback would remove bootstrap fence')
        a_baseline = self.verify_a(intent['installed_a'])
        if intent['before'] != {p:a_baseline[p] for p in TARGETS}:
            raise Refused('Intent rollback baseline differs from installed-A receipt')
        unchanged = set(a_baseline) - set(TARGETS)
        if self.protected(unchanged) != {p:a_baseline[p] for p in unchanged}:
            raise Refused('Verify-only runtime dependency changed')
        if self.protected(intent['protected']) != intent['protected']:
            raise Refused('Protected data changed; never restore stale authority')
        for i, relative_path in enumerate(TARGETS):
            if intent['target'][relative_path]['sha256'] != TARGETS[relative_path]:
                raise Refused('Unreviewed target in intent')
            before, target = intent['before'][relative_path], intent['target'][relative_path]
            if before and sha(checked(self.root, str(folder.relative_to(self.root)) + f'/{i}.old').read_bytes()) != before['sha256']:
                raise Refused('Old backup corrupt')
            if sha(checked(self.root, str(folder.relative_to(self.root)) + f'/{i}.new').read_bytes()) != target['sha256']:
                raise Refused('New backup corrupt')
            current = fingerprint(checked(self.root, relative_path))
            if current not in (before, target):
                raise Refused('Unknown runtime mutation: ' + relative_path)
            if journal['status'] == 'COMMIT_VERIFIED' and current != target or journal['status'] == 'ROLLED_BACK' and current != before:
                raise Refused('Durable terminal outcome changed')
        ledger = readjson(checked(self.root, LEDGER))
        if ledger.get('schema') != 1 or ident not in ledger.get('transactions', []):
            raise Refused('Bundle-start history missing')
        marker = checked(self.root, MARKER)
        if marker.exists():
            if readjson(marker) != {'id': ident, 'intent_sha256': intent_sha}:
                raise Refused('Bundle marker ownership changed')
        elif journal['status'] == 'PREPARED':
            if not allow_prepare_repair or self.protected(TARGETS) != intent['before']:
                raise Refused('Pending marker missing outside coherent post-A preparation')
        return folder, dict(intent, status=journal['status'], intent_sha256=intent_sha)

    def finish_bundle(self, ident, rollback=False):
        folder, intent = self.load_bundle(ident, allow_prepare_repair=True)
        marker = checked(self.root, MARKER)
        if not marker.exists() and intent['status'] == 'PREPARED':
            # Marker-write failure copied no code. Repair only the exact,
            # hash-bound preparation on the independently verified A baseline.
            writejson(marker, {'id':ident, 'intent_sha256':intent['intent_sha256']})
            self.load_bundle(ident)
        terminal = 'ROLLED_BACK' if rollback else 'COMMIT_VERIFIED'
        if intent['status'] != 'PREPARED' and intent['status'] != terminal:
            raise Refused('Completed bundle cannot switch outcome')
        self.hook('before_first_replace')
        operations = list(enumerate(TARGETS))
        for i, relative in reversed(operations) if rollback else operations:
            self.load_bundle(ident)
            desired = intent['before' if rollback else 'target'][relative]
            path = checked(self.root, relative)
            if fingerprint(path) != desired:
                if desired is None:
                    # load_bundle already proved these are our exact target bytes.
                    path.unlink()
                    syncdir(path.parent)
                else:
                    data = checked(self.root, str(folder.relative_to(self.root)) + f'/{i}.old' if rollback else str(folder.relative_to(self.root)) + f'/{i}.new').read_bytes()
                    atomic(path, data, desired['mode'])
            self.hook('after_replace_' + str(i))
        self.hook('before_commit')
        self.load_bundle(ident)
        if self.protected(TARGETS) != intent['before' if rollback else 'target']:
            raise Refused('Incomplete bundle')
        writejson(folder / 'journal.json', {'id': ident, 'intent_sha256': intent['intent_sha256'], 'status': terminal})
        self.hook('after_commit')
        self.load_bundle(ident)
        marker = checked(self.root, MARKER)
        if marker.exists():
            marker.unlink()
            syncdir(marker.parent)
        return {'id': ident, 'status': terminal, 'intent_sha256': intent['intent_sha256']}
