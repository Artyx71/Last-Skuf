"""Fail-closed P07 production prerequisites. Read-only; never issues a verdict.

Authority records live in the existing canonical state. Separate independent
Lead decisions approve readiness and all21 MDS; concept/component PASS cannot
open production. Reports and source are checked again at phase entry.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess


class ReadinessBlocked(RuntimeError):
    pass


CAPABILITIES = {'full_p06', 'safe_handoff', 'navigation_pilot',
                'audio_playback_pipeline', 'pacing_instrumentation',
                'secret_integration_contract'}
OBLIGATIONS = {'chapter_delivery_21', 'campaign_pacing_actual',
               'new_audio_acceptance', 'secret_delivery_7'}
ACCEPTANCE_STAGE = 'P07_LEAD_PASS_AND_MERGE'


def strict_json(text):
    """Never silently replace a contradictory verdict/ID with its last key."""
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate JSON key: ' + key)
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError('Non-finite JSON constant: ' + value)

    return json.loads(text, object_pairs_hook=object_pairs, parse_constant=invalid_constant)


def require(condition, message):
    if not condition:
        raise ReadinessBlocked(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_under(root, relative, prefix):
    require(isinstance(relative, str) and not Path(relative).is_absolute(), 'Relative evidence/source path required')
    require('..' not in Path(relative).parts, 'Parent traversal is not an evidence path')
    component = root
    for part in Path(relative).parts:
        component = component / part
        require(not component.is_symlink(), 'Symlink evidence/source requires reconciliation: ' + relative)
    path = (root / relative).resolve()
    boundary = (root / prefix).resolve()
    require(boundary.is_relative_to(root) and path.is_relative_to(root) and
            path.is_relative_to(boundary) and path.is_file(), 'Missing or escaped file: ' + relative)
    return path


def production_files(root):
    game = root / 'game'
    require(game.is_dir() and not game.is_symlink(), 'Production game directory unavailable or symlinked')
    paths = set()

    def walk_error(error):
        raise ReadinessBlocked('Cannot inventory complete production tree') from error

    for directory, dirs, files in os.walk(game, followlinks=False, onerror=walk_error):
        dirs[:] = [name for name in dirs if name not in ['.godot', '__pycache__']]
        for name in dirs + files:
            path = Path(directory) / name
            require(not path.is_symlink(), 'Production symlink requires reconciliation: ' + str(path.relative_to(root)))
        paths.update(str((Path(directory) / name).relative_to(root)) for name in files)
    return paths


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
        data = strict_json(path.read_text())
    except (ValueError, OSError) as error:
        raise ReadinessBlocked('Invalid independent readiness decision') from error
    require(isinstance(data, dict) and type(data.get('schema')) is int and data['schema'] == 1, 'Unknown readiness decision schema')
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
        raw_severity = finding.get('severity')
        require(isinstance(raw_severity, str), 'Finding severity must be an explicit enum')
        severity = raw_severity.strip().upper()
        require(severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], 'Unknown finding severity')
        require(finding.get('status') in ['OPEN', 'CLOSED', 'RESOLVED', 'VERIFIED'], 'Unknown finding resolution status')
        if severity in ['CRITICAL', 'HIGH']:
            require(finding.get('status') in ['CLOSED', 'RESOLVED', 'VERIFIED'], 'Unresolved Critical/High blocks production')
    inventory = data.get('source_inventory_sha256')
    require(isinstance(inventory, dict) and bool(inventory), 'Source inventory missing')
    for relative, expected in inventory.items():
        path = file_under(root, relative, '.')
        require(digest(path) == expected, 'Readiness input changed: ' + relative)
    return data


def reviewed_evidence(root, evidence, inventory):
    require(isinstance(evidence, list) and bool(evidence), 'Actual reviewed evidence required')
    for item in evidence:
        require(isinstance(item, dict), 'Invalid evidence record')
        path = file_under(root, item.get('path'), '.')
        relative = str(path.relative_to(root))
        require(digest(path) == item.get('sha256') == inventory.get(relative), 'Evidence missing from reviewed inventory')


def readiness_contract(root, ready):
    capabilities = ready.get('preproduction_capabilities')
    require(isinstance(capabilities, dict) and set(capabilities) == CAPABILITIES,
            'Full actual preproduction capability matrix required')
    for capability in capabilities.values():
        require(isinstance(capability, dict) and capability.get('status') == 'PASS', 'Preproduction capability not accepted')
        reviewed_evidence(root, capability.get('evidence'), ready['source_inventory_sha256'])
    obligations = ready.get('future_acceptance_obligations')
    require(isinstance(obligations, dict) and set(obligations) == OBLIGATIONS,
            'Explicit future content acceptance contract required')
    for obligation in obligations.values():
        require(isinstance(obligation, dict) and obligation.get('severity') == 'HIGH' and
                obligation.get('status') == 'OPEN' and obligation.get('enforce_at') == ACCEPTANCE_STAGE,
                'Unknown/closed/downgraded future acceptance obligation')
        require(isinstance(obligation.get('requirement'), str) and bool(obligation['requirement'].strip()),
                'Acceptance obligation criteria missing')
        require(isinstance(obligation.get('source_findings'), list) and bool(obligation['source_findings']) and
                all(isinstance(i, str) and bool(i.strip()) for i in obligation['source_findings']),
                'Original finding/requirement trace required')
    return obligations


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
    obligations = readiness_contract(root, ready)
    game_tree = git_tree(root, ready['p06_base_head'], 'game')
    game_files = production_files(root)
    require(game_files == set(game_tree), 'Untracked/missing production game files must be reconciled')
    require(game_files.issubset(ready['source_inventory_sha256']), 'Readiness did not inventory the whole game tree')
    verify_git_files(root, game_tree, game_files)
    designs = load_gate(root, records.get('mission_designs'), 'P07_MISSION_DESIGN_APPROVAL', heads)
    require(designs.get('approved_for_mass_production') is True, 'Mission concepts are not full MDS approval')
    try:
        registry = strict_json((root / 'game/resources/story/registry.json').read_text())
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
    return {'readiness': True, 'mission_specs': 21, 'phase_approval': False,
            'future_acceptance_obligations': obligations}


def require_p07_review_acceptance(work, review, head):
    """Close future obligations only in actual independent phase review.

    Derive the original repository from Git metadata, not a worktree's stale
    phase_state. Called on every P07 PASS validation, including both merge checks.
    """
    work = Path(work).resolve()
    common = subprocess.run(['git', 'rev-parse', '--path-format=absolute', '--git-common-dir'],
                            cwd=work, text=True, capture_output=True, check=False)
    require(common.returncode == 0, 'Canonical Git authority unavailable')
    common_path = Path(common.stdout.strip()).resolve()
    require(common_path.name == '.git' and common_path.is_dir(), 'Unsupported canonical Git authority')
    root = common_path.parent
    try:
        state = strict_json((root / 'automation/phase_state.json').read_text())
    except (OSError, ValueError) as error:
        raise ReadinessBlocked('Canonical production authority missing') from error
    contract = require_p07_production(root, state)
    current = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=work,
                             text=True, capture_output=True, check=False)
    require(current.returncode == 0 and current.stdout.strip() == head, 'P07 review workspace is not current head')
    # Inline in the independent Lead verdict stored outside the worktree. A
    # committed proof containing its own final commit SHA would be circular.
    data = review.get('production_acceptance')
    require(isinstance(data, dict) and type(data.get('schema')) is int and data['schema'] == 1 and
            data.get('scope') == 'P07_CONTENT_ACCEPTANCE', 'Wrong content acceptance schema/scope')
    require(data.get('reviewed_commit') == head and data.get('readiness_sha256') ==
            state['autopilot']['production_gates']['readiness']['sha256'], 'Stale content acceptance source/contract')
    closed = data.get('closed_obligations')
    require(isinstance(closed, dict) and set(closed) == set(contract['future_acceptance_obligations']),
            'Lead must close every declared future content obligation')
    evidence_inventory = {e['path']: e.get('sha256') for e in review.get('evidence', [])
                          if isinstance(e, dict) and isinstance(e.get('path'), str)}
    for entry in closed.values():
        require(isinstance(entry, dict) and entry.get('status') == 'PASS', 'Future content acceptance incomplete')
        reviewed_evidence(work, entry.get('evidence'), evidence_inventory)
    return True
