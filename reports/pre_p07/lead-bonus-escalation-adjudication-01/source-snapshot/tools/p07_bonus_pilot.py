#!/usr/bin/env python3
"""Actual Godot sidecar IO/session pilot; no finished bonus missions or production unlock."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from p07_room_pilot import ROOT, digest, inventory, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--goal-probe', action='store_true', help='Only review the host-fixture callback delta; preserve full IO proof separately')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit('Fresh output required; preserve prior runs')
    out.mkdir(parents=True)
    before = inventory()
    write(out / 'source_before.json', before)
    project = out / 'isolated_project/game'
    shutil.copytree(ROOT / 'game', project, ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    for name in ['p07_bonus_contract.gd', 'p07_bonus_host.gd']:
        shutil.copy2(ROOT / 'tools/fixtures' / name, project / 'tests' / name)
    prior = subprocess.check_output(['git', 'show', '50a7a837236f8f9b263cedc72406b17db30e7b89:tools/fixtures/p07_bonus_progress.gd'], cwd=ROOT)
    prior_path = project / 'tests/p07_bonus_before_strict.gd'
    prior_path.write_bytes(prior)
    write(out / 'strictness-reference.json', {'commit': '50a7a837236f8f9b263cedc72406b17db30e7b89',
                                            'path': 'tools/fixtures/p07_bonus_progress.gd', 'sha256': digest(prior_path)})
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    saves = out / 'isolated_saves'
    profiles = saves / 'profiles'
    service = saves / 'autoload'
    service.mkdir(parents=True)
    env = dict(os.environ, XDG_DATA_HOME=str(saves / 'data'), XDG_CONFIG_HOME=str(saves / 'config'),
               XDG_CACHE_HOME=str(saves / 'cache'), GODOT_SILENCE_ROOT_WARNING='1',
               AYAY_STORY_SAVE_PATH=str(service / 'story_v2.json'), AYAY_BP_PROFILE=str(profiles))
    stages = [('import', ['--headless', '--editor', '--quit'])]
    stages += [(name, ['--headless', '--script', 'res://tests/p07_bonus_contract.gd']) for name in
               ['checks', 'prepare', 'before_rename', 'recover_before', 'after_rename', 'recover_after']]
    stages += [(name, ['--headless', '--script', f'res://tests/{name}_test.gd']) for name in ['story_state', 'story_graph', 'story_integration']]
    if args.goal_probe:
        stages = [('import', ['--headless', '--editor', '--quit']),
                  ('goals', ['--headless', '--script', 'res://tests/p07_bonus_contract.gd'])]
    runs = []
    for name, flags in stages:
        result_path = out / f'{name}-result.json'
        boundary = out / f'{name}-boundary.txt'
        run_env = dict(env, AYAY_BP_MODE=name, AYAY_BP_RESULT=str(result_path), AYAY_BP_BOUNDARY=str(boundary))
        if name.startswith('story_'):
            directory = saves / name
            directory.mkdir()
            run_env['AYAY_STORY_SAVE_PATH'] = str(directory / 'story.json')
        argv = [str(engine), '--path', str(project), *flags]
        process = subprocess.run(argv, cwd=ROOT, env=run_env, capture_output=True, text=True, timeout=180)
        log = process.stdout + process.stderr
        (out / f'{name}.log').write_text(log + f'\nexit_code={process.returncode}\n')
        row = {'name': name, 'argv': argv, 'exit_code': process.returncode, 'log_sha256': digest(out / f'{name}.log')}
        if name in ['before_rename', 'after_rename']:
            row['expected_process_interruption'] = True
            row['passed'] = process.returncode == -9 and boundary.is_file() and boundary.read_text() == name and not result_path.exists()
        else:
            row['passed'] = process.returncode == 0 and not any(x in log for x in ['SCRIPT ERROR:', 'Parse Error:', 'FAIL BONUS'])
            if name not in ['import', 'story_state', 'story_graph', 'story_integration']:
                data = json.loads(result_path.read_text()) if result_path.exists() else {}
                checks = data.get('checks', [])
                row['checks'] = len(checks)
                row['passed'] = row['passed'] and bool(checks) and len({r['check'] for r in checks}) == len(checks) \
                    and all(r.get('passed') is True for r in checks) and data.get('failed') == 0 and data.get('passed') == len(checks)
        runs.append(row)
        write(out / 'runs.json', runs)
        if not row['passed']:
            break
    after = inventory()
    write(out / 'source_after.json', after)
    # Retain actual profile files as portable evidence; no real user profile is consulted.
    evidence = out / 'profile_evidence'
    evidence.mkdir()
    for file in profiles.rglob('*') if profiles.exists() else []:
        if file.is_file():
            target = evidence / file.relative_to(profiles)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
    passed = len(runs) == len(stages) and all(row['passed'] for row in runs) and before == after
    report = {'schema': 1, 'passed': passed, 'scope': 'ISOLATED_BONUS_NAMESPACE_IO_SESSION_PILOT',
              'focused_goal_fixture_probe_only': args.goal_probe,
              'runs': runs, 'source_unchanged': before == after, 'engine_sha256': digest(engine),
              'real_current_campaign_positive_unlock': 'NOT_AVAILABLE_PLANNED_CH10_CH14',
              'positive_session_tests': 'EXPLICIT_CHAPTER_AND_SCENE_ELIGIBILITY_DOUBLE_ONLY',
              'shipped_UI_CLI_adapter_mission_ART_audio_exports_tested': False,
              'Readiness_P07_or_runtime_integration_approval': False}
    write(out / 'validation.json', report)
    print(json.dumps(report), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
