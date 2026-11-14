"""Fail-closed P07 production prerequisites. Read-only; never issues a verdict.

Authority records live in the existing canonical state. Separate independent
Lead decisions approve readiness and all21 MDS; concept/component PASS cannot
open production. Reports and source are checked again at phase entry.
"""
import hashlib
import json
from pathlib import Path
import subprocess


class ReadinessBlocked(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise ReadinessBlocked(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_under(root, relative, prefix):
    require(isinstance(relative, str) and not Path(relative).is_absolute(), 'Relative evidence/source path required')
    path = (root / relative).resolve()
    require(path.is_relative_to((root / prefix).resolve()) and path.is_file(), 'Missing or escaped file: ' + relative)
    return path


def git_tree(root, head, prefix):
    require(isinstance(head, str) and len(head) == 40 and all(c in '0123456789abcdef' for c in head), 'Invalid frozen Git SHA')
    result = subprocess.run(['git', 'ls-tree', '-rz', head, '--', prefix], cwd=root,
                            capture_output=True, check=False)
    require(result.returncode == 0, 'Frozen source commit unavailable')
    tree = {}
    for record in result.stdout.split(b'\0'):
        if not record:
            continue
        metadata, raw_path = record.split(b'\t', 1)
        mode, kind, oid = metadata.decode().split()
        require(kind == 'blob' and mode != '120000', 'Production source symlinks/submodules require explicit reconciliation')
        tree[raw_path.decode()] = oid
    require(bool(tree), 'Empty frozen source tree')
    return tree


def verify_git_files(root, tree, paths):
    # Batch each blob instead of trusting a claimed JSON digest alone.
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=root,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for relative in sorted(paths):
            require(relative in tree, 'Approved file not in frozen Git tree: ' + relative)
            process.stdin.write((tree[relative] + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().decode().split()
            require(len(header) == 3 and header[1] == 'blob', 'Cannot read frozen Git blob')
            remaining = int(header[2]); hashed = hashlib.sha256()
            while remaining:
                chunk = process.stdout.read(min(remaining, 1024 * 1024))
                require(bool(chunk), 'Truncated frozen Git blob')
                hashed.update(chunk); remaining -= len(chunk)
            require(process.stdout.read(1) == b'\n', 'Invalid frozen blob delimiter')
            require(digest(root / relative) == hashed.hexdigest(), 'Current file differs from frozen source: ' + relative)
    finally:
        process.stdin.close(); process.stdout.close(); process.stderr.close(); process.wait()


def load_gate(root, record, scope, p06_heads):
    require(isinstance(record, dict), scope + ' independent approval record missing')
    path = file_under(root, record.get('decision'), 'reports/pre_p07')
    require(digest(path) == record.get('sha256'), scope + ' decision hash changed')
    try:
        data = json.loads(path.read_text())
    except (ValueError, OSError) as error:
        raise ReadinessBlocked('Invalid independent readiness decision') from error
    require(isinstance(data, dict) and data.get('schema') == 1, 'Unknown readiness decision schema')
    require(data.get('status') == 'PASS' and data.get('scope') == scope, 'Full ' + scope + ' PASS required')
    require(data.get('acceptance_level') == 'FULL', 'Concept/component approval cannot open production')
    require(data.get('role') == 'LEAD_REVIEWER' and data.get('independent_of_author') is True,
            'Independent Lead approval required')
    require(isinstance(data.get('reviewer'), str) and bool(data['reviewer'].strip()), 'Reviewer identity missing')
    require(data.get('p06_base_head') in p06_heads, 'Approval is not bound to the confirmed P06 source')
    require(data.get('must_fix') == [], 'Unresolved mandatory readiness findings')
    findings = data.get('findings', [])
    require(isinstance(findings, list), 'Invalid readiness findings')
    for finding in findings:
        require(isinstance(finding, dict), 'Invalid finding entry')
        severity = str(finding.get('severity', '')).upper()
        if severity in ['CRITICAL', 'HIGH']:
            require(finding.get('status') in ['CLOSED', 'RESOLVED', 'VERIFIED'], 'Unresolved Critical/High blocks production')
    inventory = data.get('source_inventory_sha256')
    require(isinstance(inventory, dict) and bool(inventory), 'Source inventory missing')
    for relative, expected in inventory.items():
        path = file_under(root, relative, '.')
        require(digest(path) == expected, 'Readiness input changed: ' + relative)
    return data


def require_p07_production(root, state):
    root = Path(root).resolve()
    require(isinstance(state, dict), 'Invalid canonical state')
    autopilot = state.get('autopilot')
    require(isinstance(autopilot, dict), 'Autopilot state missing')
    phases = autopilot.get('phases')
    require(isinstance(phases, dict), 'Phase records missing')
    p06 = phases.get('P06', {})
    require(isinstance(p06, dict), 'Invalid P06 record')
    merge = p06.get('merge', {})
    require(isinstance(merge, dict), 'Invalid P06 merge record')
    require(p06.get('status') == 'PASS' and merge.get('status') == 'MERGED', 'P06 full PASS and confirmed merge required')
    heads = [merge.get('reviewed_head'), merge.get('merge_sha')]
    require(all(isinstance(h, str) and len(h) == 40 and all(c in '0123456789abcdef' for c in h) for h in heads), 'Confirmed P06 reviewed/merge SHA missing')
    records = autopilot.get('production_gates')
    require(isinstance(records, dict), 'Independent production gate records missing')
    ready = load_gate(root, records.get('readiness'), 'PRE_P07_PRODUCTION_READINESS', heads)
    require(ready.get('ready_for_p07') is True, 'Readiness does not authorize P07')
    game_tree = git_tree(root, ready['p06_base_head'], 'game')
    game_files = {str(p.relative_to(root)) for p in (root / 'game').rglob('*')
                  if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}
    require(game_files == set(game_tree), 'Untracked/missing production game files must be reconciled')
    require(game_files.issubset(ready['source_inventory_sha256']), 'Readiness did not inventory the whole game tree')
    verify_git_files(root, game_tree, game_files)
    designs = load_gate(root, records.get('mission_designs'), 'P07_MISSION_DESIGN_APPROVAL', heads)
    require(designs.get('approved_for_mass_production') is True, 'Mission concepts are not full MDS approval')
    try:
        registry = json.loads((root / 'game/resources/story/registry.json').read_text())
    except (OSError, ValueError) as error:
        raise ReadinessBlocked('Cannot read canonical chapter registry') from error
    require(isinstance(registry, dict), 'Invalid canonical chapter registry')
    chapters = registry.get('chapters')
    require(isinstance(chapters, list) and len(chapters) == 21 and all(isinstance(c, dict) and isinstance(c.get('id'), str) for c in chapters), 'Canonical21 chapter registry required')
    ids = {c['id'] for c in chapters}
    specifications = designs.get('mission_specs')
    require(len(ids) == 21 and isinstance(specifications, dict) and set(specifications) == ids, 'Lead must approve all21 exact chapter specifications')
    paths, hashes = set(), set()
    for chapter, entry in specifications.items():
        require(isinstance(entry, dict), 'Invalid mission specification record')
        path = file_under(root, entry.get('path'), 'planning')
        relative = str(path.relative_to(root))
        actual = digest(path)
        require(actual == entry.get('sha256') == designs['source_inventory_sha256'].get(relative), 'MDS file changed or not reviewed: ' + chapter)
        require(path not in paths and actual not in hashes, 'One duplicated specification cannot approve multiple chapters')
        require(bool(path.read_text().strip()), 'Empty MDS cannot authorize production')
        paths.add(path); hashes.add(actual)
    return {'readiness': True, 'mission_specs': 21, 'phase_approval': False}
