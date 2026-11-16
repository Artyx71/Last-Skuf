#!/usr/bin/env python3
"""Continue the five unexecuted P06 native stages using independently bound evidence.
Never rewrites the failed original attempt or reruns its seven successful stages.
Requires a hash-bound independent Lead contract; produces technical evidence only.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import verify_p06 as pipeline

ROOT = pipeline.ROOT
REUSED = ['gabar', 'olezhka', 'counter_feedback', 'timka_present', 'timka_prime', 'ryzhik', 'tega']
TAIL = ['cast', 'cast_large_text', 'finisher_audio', 'npc_baseline', 'combat_baseline']
ALLOWED_CHANGES = {'game/tests/pasha_moving_shot_replay.gd', 'game/scripts/qa/cast_replay.gd', 'tools/continue_p06_native.py',
                   'tools/tests/test_p06_continuation.py'}


def checked_path(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError('Evidence path must be relative text')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Evidence path escapes its root')
    return path


def check_changes(before, after, approved):
    changes = {p: {'before': before.get(p), 'after': after.get(p)}
               for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
    if changes != approved or not set(changes) <= ALLOWED_CHANGES:
        raise ValueError('Unapproved source delta; rerun affected evidence')


def verify_artifacts(root, artifacts):
    if not artifacts or len({x['path'] for x in artifacts}) != len(artifacts):
        raise ValueError('Missing or duplicate artifact inventory')
    for item in artifacts:
        path = checked_path(root, item['path'])
        if not path.is_file() or pipeline.sha(path) != item['sha256']:
            raise ValueError('Changed/missing artifact: ' + item['path'])


def binding_hashes(paths):
    result = {}
    for name, path in paths.items():
        try:
            result[name] = pipeline.sha(path)
        except OSError:
            result[name] = None
    return result


def held_data(path):
    data = pipeline.strict_report(path.read_text())
    for reduced in ['false', 'true']:
        for direction, vector in [('down', [0., 1.]), ('left', [-1., 0.]), ('right', [1., 0.]), ('up', [0., -1.])]:
            segment = 'moving_shot_' + reduced + '_' + direction
            samples = [x for x in data['ammo_trace'] if x['segment'] == segment]
            physical = [x for x in data['trace'] if x['segment'] == segment]
            if (not samples or [x['tick'] for x in samples] != [x['tick'] for x in physical]
                    or not all(x['run_pressed'] is True and x['input_vector'] == vector for x in samples)
                    or not all(samples[i]['tick'] > samples[i-1]['tick'] for i in range(1, len(samples)))):
                raise ValueError('Invalid/missing held-input evidence: ' + segment)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--contract', required=True)
    parser.add_argument('--approval', required=True)
    parser.add_argument('--approval-sha256', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--build-output', required=True)
    args = parser.parse_args()
    output, build = (ROOT / args.output).resolve(), (ROOT / args.build_output).resolve()
    for directory in [output, build]:
        if directory.exists() and any(directory.iterdir()):
            parser.error('Immutable evidence: inspect previous attempt; use fresh outputs')
        directory.mkdir(parents=True, exist_ok=True)
    (output / 'logs').mkdir()
    contract_path = checked_path(ROOT, args.contract)
    contract_bytes = contract_path.read_bytes()
    contract_sha = hashlib.sha256(contract_bytes).hexdigest()
    contract = pipeline.strict_report(contract_bytes.decode())
    approval_path = Path(args.approval).resolve()
    approval_bytes = approval_path.read_bytes()
    if hashlib.sha256(approval_bytes).hexdigest() != args.approval_sha256:
        parser.error('Independent approval hash mismatch')
    approval = pipeline.strict_report(approval_bytes.decode())
    if (approval.get('status') != 'PASS_COMPONENT_EXECUTION_ONLY'
            or approval.get('contract_sha256') != contract_sha
            or approval.get('phase_approval') is not False):
        parser.error('Missing exact independent continuation approval')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    before = pipeline.inventory()
    old_before = pipeline.strict_report(checked_path(ROOT, contract['old_sources_before']).read_text())
    old_after = pipeline.strict_report(checked_path(ROOT, contract['old_sources_after']).read_text())
    if old_before != old_after:
        parser.error('Original source freeze failed')
    check_changes(old_before, before, contract['source_changes'])
    verify_artifacts(ROOT, contract['artifacts'])
    parent = pipeline.strict_report(checked_path(ROOT, contract['old_validation']).read_text())
    old_commands = parent.get('commands', [])
    if (parent.get('passed') is not False or len(old_commands) != 8
            or [x['name'] for x in old_commands] != REUSED + ['pasha']
            or not all(x['passed'] is True and x['exit_code'] == 0 for x in old_commands[:7])
            or old_commands[7]['passed'] is not False):
        parser.error('Original attempt does not match the reviewed 7-positive/8th-failed boundary')
    rows = []
    for item in contract['reused_stages']:
        if not pipeline.valid_report(checked_path(ROOT, item['report'])):
            parser.error('Invalid retained child report')
        rows.append(dict(item, origin='REUSED_ORIGINAL_SUCCESS_NOT_FRESH', passed=True))
    if [x['name'] for x in rows] != REUSED:
        parser.error('Wrong retained stage set/order')
    for relative in contract['pasha_validations']:
        if not pipeline.valid_report(checked_path(ROOT, relative)):
            parser.error('Invalid targeted Pasha report')
    for relative in contract['pasha_traces']:
        held_data(checked_path(ROOT, relative))
    rows.append({'name': 'pasha', 'origin': 'TARGETED_651_CONTROLLED_INPUT_PLUS_7A76_GUARD_RECOMPUTATION',
                 'passed': True, 'reports': contract['pasha_validations'], 'original_failure_cause': 'UNKNOWN'})
    stages = [x for x in pipeline.plan(output, build, exports=True, movie=True) if x[0] in TAIL]
    if [x[0] for x in stages] != TAIL:
        parser.error('Unexpected continuation plan')
    pipeline.write(output / 'source_hashes_before.json', before)
    pipeline.write(output / 'plan.json', [{'name': n, 'argv': list(map(str, a)), 'timeout': t} for n, a, t in stages])
    lock = pipeline.strict_report((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / ('Godot_v' + lock['release'] + '_linux.x86_64')
    if pipeline.sha(engine) != lock['linux_binary_sha256']:
        parser.error('Pinned engine changed')
    pinned_bindings = {'contract': contract_sha, 'approval': args.approval_sha256}
    binding_paths = {'contract': contract_path, 'approval': approval_path}
    if binding_hashes(binding_paths) != pinned_bindings:
        parser.error('Continuation proof changed before fixture parse')
    parse = pipeline.run_command([engine, '--headless', '--path', ROOT / 'game', '--check-only',
                                  '--script', 'res://tests/pasha_moving_shot_replay.gd'],
                                 output / 'logs/current_fixture_parse.log', 60)
    pipeline.write(output / 'fixture_parse.json', parse)
    if not parse['passed']:
        return 1
    commands = []
    for name, argv, timeout in stages:
        if binding_hashes(binding_paths) != pinned_bindings:
            rows.append({'name': name, 'origin': 'NOT_EXECUTED_PROOF_BINDINGS_CHANGED', 'passed': False})
            break
        print('START', name, flush=True)
        item = pipeline.run_command(argv, output / 'logs' / (name + '.log'), timeout)
        item.update(name=name, report_passed=pipeline.valid_report(output / name / 'validation.json'))
        item['passed'] = bool(item['passed'] and item['report_passed'])
        commands.append(item)
        rows.append({'name': name, 'origin': 'FRESH_CONTINUATION', 'passed': item['passed'],
                     'report': str((output / name / 'validation.json').relative_to(ROOT))})
        pipeline.write(output / 'commands.json', commands)
        print('END', name, 'PASS' if item['passed'] else 'FAIL', flush=True)
        if not item['passed']:
            break
    after = pipeline.inventory()
    head_after = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    pipeline.write(output / 'source_hashes_after.json', after)
    verify_artifacts(ROOT, contract['artifacts'])
    final_bindings = binding_hashes(binding_paths)
    bindings_stable = final_bindings == pinned_bindings
    summary = {'schema': 1, 'scope': 'P06_COMPOSED_NATIVE_EVIDENCE_NOT_PHASE_APPROVAL',
               'passed': len(rows) == 13 and all(x['passed'] for x in rows) and before == after and head == head_after and bindings_stable,
               'phase_approval': False, 'merge_approval': False, 'stages': rows,
               'reused_original_successes': 7, 'separately_targeted_Pasha': 1, 'fresh_remaining_expected': 5,
               'fresh_remaining_completed': len(commands), 'current_fixture_parse_passed': parse['passed'], 'source_unchanged': before == after,
               'source_head': head, 'head_after': head_after, 'contract_sha256': contract_sha,
               'proof_bindings_unchanged': bindings_stable, 'final_binding_hashes': final_bindings,
               'approval_sha256': args.approval_sha256, 'original_failed_attempt_rewritten': False,
               'original_failed_attempt': contract['old_validation'], 'Pasha_original_cause': 'UNKNOWN',
               'listening': 'NOT_CLAIMED', 'native_Windows': 'NOT_TESTED_WINE_LABELLED_SEPARATELY',
               'hardware_latency': 'NOT_MEASURED', 'campaign_duration': 'NOT_MEASURED'}
    pipeline.write(output / 'validation.json', summary)
    print(json.dumps({'passed': summary['passed'], 'stages': len(rows), 'phase_approval': False}), flush=True)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
