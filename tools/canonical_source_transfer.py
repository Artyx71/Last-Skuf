#!/usr/bin/env python3
"""Cold additive transfer of approved Game/tools source; never restores authority.

The caller freezes and independently reviews the exact Git-derived payload plan.
Only game/ and tools/ may change. Existing source removal is deliberately forbidden.
"""
import json
import os
from pathlib import Path
import uuid

from cold_bootstrap import Bootstrap, Refused, atomic, checked, fingerprint, parsejson, readjson, sha, syncdir, writejson

MARKER = '.autopilot/HANDOFF_PENDING.json'
PREFIXES = {'game', 'tools'}
RUNNER_B = 'd700e88e585a2dfb4455290421109a7209acb34dd6fd6730afaf24bc3a6fe3a0'


class CanonicalSourceTransfer(Bootstrap):
    def relative_name(self, name):
        if not isinstance(name,str) or not name or name != str(Path(name)) or Path(name).is_absolute():
            raise Refused('Noncanonical relative path')
        checked(self.root,name)
        return name

    def source_name(self, name):
        self.relative_name(name)
        parts=Path(name).parts
        if len(parts)<2 or parts[0] not in PREFIXES or any(p in ('.godot','__pycache__') for p in parts):
            raise Refused('Only canonical source file paths are writable')
        return name

    def inventory(self):
        result = {}
        for prefix in sorted(PREFIXES):
            base = checked(self.root, prefix)
            if not base.is_dir():
                raise Refused('Existing source directory required: ' + prefix)
            for folder, dirs, files in os.walk(base, followlinks=False):
                dirs[:] = [p for p in dirs if p not in ('.godot','__pycache__')]
                for name in dirs + files:
                    p = Path(folder) / name
                    if p.is_symlink():
                        raise Refused('Source symlink: ' + str(p.relative_to(self.root)))
                for name in files:
                    p = Path(folder) / name
                    result[str(p.relative_to(self.root))] = fingerprint(p)
        return result

    def verify_b(self, proof):
        if not proof['path'].startswith('reports/pre_p07/'):
            raise Refused('Independent installed B receipt required')
        blob = checked(self.root, proof['path']).read_bytes()
        if sha(blob) != proof['sha256']:
            raise Refused('B receipt changed')
        data = parsejson(blob)
        if type(data.get('schema')) is not int or data.get('schema') != 1 or data.get('state_continuity_verified') is not True or data.get('role') != 'INDEPENDENT_LEAD_ACTUAL_INSTALL_VERIFIER' or data.get('scope') != 'ACTUAL_RUNTIME_BUNDLE_B_INSTALLED_AND_POST_B_BASELINE_ONLY' or data.get('status') != 'PASS' or data.get('actual_B_verified') is not True or data.get('journal_status') != 'COMMIT_VERIFIED' or data.get('installed_runner_sha256') != RUNNER_B:
            raise Refused('Full actual installed B verification required')
        name = data.get('post_B_runtime_baseline_path', '')
        if not name.startswith('reports/pre_p07/'):
            raise Refused('Missing B runtime baseline')
        raw = checked(self.root, name).read_bytes()
        if sha(raw) != data.get('post_B_runtime_baseline_sha256'):
            raise Refused('B baseline binding changed')
        files = parsejson(raw).get('runtime_files')
        required = {'autopilot/readiness.py','autopilot/github.py','autopilot/config.json',
                    'autopilot/review_schema.json','autopilot/prompts/INDEPENDENT_REVIEW.md',
                    'autopilot/PRODUCTION_GATES.md','autopilot/runner.py','autopilot/worker.py',
                    'tools/verify.py','tools/verify_p06.py'}
        if not isinstance(files,dict) or set(files) != required or files['autopilot/runner.py']['sha256'] != RUNNER_B:
            raise Refused('Incomplete B baseline')
        return files

    def begin_transfer(self, payloads, expected_before, protected, installed_b):
        protected = list(protected)
        self.check_lock()
        if checked(self.root, MARKER).exists():
            raise Refused('Recover pending maintenance first')
        parent = checked(self.root, '.autopilot/canonical-transfers')
        if parent.exists():
            for folder in parent.iterdir():
                p = checked(self.root, str(folder.relative_to(self.root)) + '/journal.json')
                if p.exists() and readjson(p).get('status') not in ('COMMIT_VERIFIED','ROLLED_BACK'):
                    raise Refused('Recover prior source preparation before a new begin')
        if not payloads or set(payloads) != set(expected_before):
            raise Refused('Explicit before state for every target, including absences, required')
        for name in payloads:
            self.source_name(name)
        for name in protected:
            self.relative_name(name)
        if self.protected(expected_before) != expected_before:
            raise Refused('Physical before state differs, including declared absences')
        current = self.inventory()
        if current != {p:f for p,f in expected_before.items() if f is not None}:
            raise Refused('Unknown/missing/modified source; preserve user changes')
        if set(protected) & set(payloads):
            raise Refused('Protected paths cannot be source targets')
        baseline = self.verify_b(installed_b)
        if self.protected(baseline) != baseline:
            raise Refused('Current runtime differs from verified B')
        for name in ('tools/verify.py','tools/verify_p06.py'):
            if expected_before.get(name) != baseline[name]:
                raise Refused('Source before state does not match B tools baseline')
        kept = self.protected(protected)
        if not parent.exists():
            parent.mkdir(mode=0o700);syncdir(parent.parent)
        folder = parent / uuid.uuid4().hex
        folder.mkdir(mode=0o700);syncdir(parent)
        target = {}; changes = []
        for i,name in enumerate(sorted(payloads)):
            old = expected_before[name]
            if old and (old['uid'],old['gid']) != (os.geteuid(),os.getegid()):
                raise Refused('Cannot preserve source ownership')
            # Preserve existing modes; new source defaults to ordinary data mode.
            target[name] = dict(old or {'mode':0o644,'uid':os.geteuid(),'gid':os.getegid()},sha256=sha(payloads[name]))
            if old != target[name]:
                changes.append({'path':name,'slot':i})
                if old:
                    atomic(folder / f'{i}.old',checked(self.root,name).read_bytes())
                    if sha((folder/f'{i}.old').read_bytes()) != old['sha256']:
                        raise Refused('Source backup mismatch')
                atomic(folder/f'{i}.new',payloads[name])
                if sha((folder/f'{i}.new').read_bytes()) != target[name]['sha256']:
                    raise Refused('Source target staging mismatch')
        intent = {'schema':1,'kind':'CANONICAL_SOURCE_TRANSFER','id':folder.name,'root':str(self.root),
                  'lock':list(self.identity),'before':expected_before,'target':target,'changes':changes,
                  'protected':kept,'installed_b':installed_b}
        raw=(json.dumps(intent,ensure_ascii=False,indent=2)+'\n').encode()
        atomic(folder/'intent.json',raw)
        if (folder/'intent.json').read_bytes()!=raw:
            raise Refused('Prepared source intent changed')
        digest=sha(raw)
        writejson(folder/'journal.json',{'id':folder.name,'intent_sha256':digest,'status':'PREPARED'})
        writejson(checked(self.root,MARKER),{'id':folder.name,'intent_sha256':digest,'kind':'CANONICAL_SOURCE_TRANSFER'})
        self.hook('prepared')
        return folder.name

    def load_transfer(self, ident, allow_prepare_repair=False):
        self.check_lock()
        if len(ident)!=32 or any(c not in '0123456789abcdef' for c in ident):
            raise Refused('Invalid source transaction ID')
        relative='.autopilot/canonical-transfers/'+ident
        folder=checked(self.root,relative)
        raw=checked(self.root,relative+'/intent.json').read_bytes();digest=sha(raw);data=parsejson(raw)
        journal=readjson(checked(self.root,relative+'/journal.json'))
        if set(data)!={'schema','kind','id','root','lock','before','target','changes','protected','installed_b'} or data.get('schema')!=1 or data.get('kind')!='CANONICAL_SOURCE_TRANSFER' or data.get('id')!=ident or data.get('root')!=str(self.root) or data.get('lock')!=list(self.identity):
            raise Refused('Invalid immutable source identity')
        if journal.get('id')!=ident or journal.get('intent_sha256')!=digest or journal.get('status') not in ('PREPARED','COMMIT_VERIFIED','ROLLED_BACK'):
            raise Refused('Source journal binding failed')
        if set(data['before'])!=set(data['target']):
            raise Refused('Source path set changed')
        for name in data['target']:
            self.source_name(name)
        for name in data['protected']:
            self.relative_name(name)
        if self.protected(data['protected'])!=data['protected']:
            raise Refused('Protected state changed; never restore stale authority')
        baseline=self.verify_b(data['installed_b']);unchanged={p:v for p,v in baseline.items() if not p.startswith('tools/')}
        if self.protected(unchanged)!=unchanged:
            raise Refused('B runtime/control-plane changed')
        for name in ('tools/verify.py','tools/verify_p06.py'):
            if data['before'].get(name)!=baseline[name]:raise Refused('B source baseline changed')
        current=self.inventory()
        if set(current)-set(data['target']):raise Refused('Unknown source file; do not delete it')
        for name,target in data['target'].items():
            before=data['before'][name];value=current.get(name)
            if value not in (before,target):raise Refused('Unknown source mutation: '+name)
            if journal['status']=='COMMIT_VERIFIED' and value!=target or journal['status']=='ROLLED_BACK' and value!=before:
                raise Refused('Durable source outcome changed')
        expected_changes=[{'path':p,'slot':i} for i,p in enumerate(sorted(data['target'])) if data['before'][p]!=data['target'][p]]
        if data['changes']!=expected_changes:raise Refused('Changed source allowlist differs')
        for entry in data['changes']:
            name=entry['path'];i=entry['slot']
            if data['before'][name] and sha(checked(self.root,relative+f'/{i}.old').read_bytes())!=data['before'][name]['sha256']:
                raise Refused('Source backup corrupt')
            if sha(checked(self.root,relative+f'/{i}.new').read_bytes())!=data['target'][name]['sha256']:
                raise Refused('Staged source corrupt')
        marker=checked(self.root,MARKER)
        if marker.exists():
            if readjson(marker)!={'id':ident,'intent_sha256':digest,'kind':'CANONICAL_SOURCE_TRANSFER'}:
                raise Refused('Other source maintenance owns marker')
        elif journal['status']=='PREPARED':
            if not allow_prepare_repair or current!={p:v for p,v in data['before'].items() if v is not None}:
                raise Refused('Missing marker outside untouched preparation')
        return folder,dict(data,status=journal['status'],intent_sha256=digest)

    def finish_transfer(self, ident, rollback=False):
        folder,data=self.load_transfer(ident,allow_prepare_repair=True)
        marker=checked(self.root,MARKER);binding={'id':ident,'intent_sha256':data['intent_sha256'],'kind':'CANONICAL_SOURCE_TRANSFER'}
        if not marker.exists() and data['status']=='PREPARED':writejson(marker,binding)
        terminal='ROLLED_BACK' if rollback else 'COMMIT_VERIFIED'
        if data['status'] not in ('PREPARED',terminal):raise Refused('Completed source outcome cannot switch')
        self.hook('before_first_copy')
        operations=list(data['changes'])
        for index,entry in enumerate(reversed(operations) if rollback else operations):
            self.load_transfer(ident)
            name=entry['path'];slot=entry['slot'];wanted=data['before' if rollback else 'target'][name];path=checked(self.root,name)
            if fingerprint(path)!=wanted:
                if wanted is None:
                    path.unlink();syncdir(path.parent)
                else:
                    # Only descendants of the two audited source roots are created.
                    missing=[];parent=path.parent
                    while not parent.exists():missing.append(parent);parent=parent.parent
                    for directory in reversed(missing):directory.mkdir();syncdir(directory.parent)
                    payload=checked(self.root,str(folder.relative_to(self.root))+f'/{slot}.old' if rollback else str(folder.relative_to(self.root))+f'/{slot}.new').read_bytes()
                    atomic(path,payload,wanted['mode'])
            self.hook('after_copy_'+str(index))
        self.hook('before_commit');self.load_transfer(ident)
        desired={p:v for p,v in data['before' if rollback else 'target'].items() if v is not None}
        if self.inventory()!=desired:raise Refused('Incomplete source transfer')
        writejson(folder/'journal.json',{'id':ident,'intent_sha256':data['intent_sha256'],'status':terminal})
        self.hook('after_commit');self.load_transfer(ident)
        if marker.exists():marker.unlink();syncdir(marker.parent)
        return {'id':ident,'status':terminal,'intent_sha256':data['intent_sha256'],'source_files':len(desired)}
