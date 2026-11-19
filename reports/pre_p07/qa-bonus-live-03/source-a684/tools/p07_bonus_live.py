#!/usr/bin/env python3
"""Isolated actual StoryService/journal/Bootstrap adapters; bonus content stays planned."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from p07_room_pilot import ROOT, digest, inventory, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--core-evidence', type=Path, help='Reuse immutable core proof only when every Game/core input and engine hash matches')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit('Fresh output required')
    out.mkdir(parents=True)
    before = inventory()
    write(out / 'source_before.json', before)
    core_dir = args.core_evidence.resolve() if args.core_evidence else out / 'core'
    if args.core_evidence:
        core_data = json.loads((core_dir / 'validation.json').read_text())
        saved = json.loads((core_dir / 'source_after.json').read_text())
        game = {key for key in before if key.startswith('game/')}
        assert game == {key for key in saved if key.startswith('game/')}
        required = game | {'tools/p07_bonus_pilot.py', 'tools/fixtures/p07_bonus_contract.gd', 'tools/fixtures/p07_bonus_host.gd'}
        assert all(saved[key] == before[key] for key in required), 'Changed core inputs require a fresh core run'
        assert core_data.get('source_unchanged') is True and all(row.get('passed') is True for row in core_data['runs'])
        write(out / 'core-reuse.json', {'kind': 'ACTUAL_COMPONENT_EVIDENCE_REUSED_NOT_RERUN', 'path': str(core_dir),
                                      'validation_sha256': digest(core_dir / 'validation.json'),
                                      'source_after_sha256': digest(core_dir / 'source_after.json'),
                                      'required_source_pins': {key: before[key] for key in sorted(required)}})
    else:
        core_argv = [sys.executable, str(ROOT / 'tools/p07_bonus_pilot.py'), '--output', str(core_dir)]
        core = subprocess.run(core_argv, cwd=ROOT, capture_output=True, text=True, timeout=420)
        (out / 'core.log').write_text(core.stdout + core.stderr)
        core_data = json.loads((core_dir / 'validation.json').read_text()) if (core_dir / 'validation.json').exists() else {}
        if core.returncode != 0: core_data['passed'] = False
    if core_data.get('passed') is not True:
        write(out / 'validation.json', {'passed': False, 'core_passed': False, 'scope': 'BONUS_LIVE_ADAPTER_PILOT'})
        return 1
    project = out / 'isolated_project/game'
    shutil.copytree(core_dir / 'isolated_project/game', project)
    assert all(digest(project / Path(key).relative_to('game')) == value
               for key, value in before.items() if key.startswith('game/')), 'Copied runtime differs from declared Game inputs'
    shutil.copy2(ROOT / 'tools/fixtures/p07_bonus_live.gd', project / 'tests/p07_bonus_live.gd')
    (project / 'tests/p07_bonus_host.tscn').write_text('[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path="res://tests/p07_bonus_host.gd" id="1"]\n[node name="ContractGoalOnly" type="Node"]\nscript = ExtResource("1")\n')
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    assert core_data['engine_sha256'] == digest(engine), 'Changed engine cannot reuse core evidence'
    stages = [('live', ['--headless', '--script', 'res://tests/p07_bonus_live.gd']),
              ('cli', ['--headless', '--script', 'res://tests/p07_bonus_live.gd', '--', '--open-mission'])]
    if args.native:
        stages += [('native', ['--disable-vsync', '--max-fps', '60', '--script', 'res://tests/p07_bonus_live.gd']),
                   ('native_cli', ['--disable-vsync', '--max-fps', '60', '--script', 'res://tests/p07_bonus_live.gd', '--', '--open-mission']),
                   ('old_story_replay', ['--disable-vsync', '--max-fps', '60', '--', '--p05-replay'])]
    runs = []
    for name, flags in stages:
        isolate = out / 'isolated_saves' / name
        profile = isolate / 'profile'
        profile.mkdir(parents=True)
        captures = out / f'{name}-captures'
        captures.mkdir()
        result = out / f'{name}-result.json'
        mode = 'cli' if name in ['cli', 'native_cli'] else name
        env = dict(os.environ, XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
                   XDG_CACHE_HOME=str(isolate / 'cache'), AYAY_STORY_SAVE_PATH=str(profile / 'story.json'),
                   AYAY_BP_PROFILE=str(profile), AYAY_BP_MODE=mode, AYAY_BP_RESULT=str(result),
                   AYAY_BP_CAPTURE=str(captures), AYAY_P05_CAPTURE_DIR=str(captures),
                   AYAY_P05_RESULT_PATH=str(result), GODOT_SILENCE_ROOT_WARNING='1')
        argv = [str(engine), '--path', str(project), *flags]
        process = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        log = process.stdout + process.stderr
        (out / f'{name}.log').write_text(log + f'\nexit_code={process.returncode}\n')
        data = json.loads(result.read_text()) if result.exists() else {}
        checks = data.get('checks', [])
        if isinstance(checks, dict):
            valid_checks = bool(checks) and all(value is True for value in checks.values())
        else:
            valid_checks = bool(checks) and len({c['check'] for c in checks}) == len(checks) and all(c.get('passed') is True for c in checks)
        passed = process.returncode == 0 and valid_checks and not any(x in log for x in ['SCRIPT ERROR:', 'Parse Error:', 'FAIL BONUS', 'FAIL: P05'])
        runs.append({'name': name, 'argv': argv, 'exit_code': process.returncode, 'checks': len(checks),
                     'passed': passed, 'log_sha256': digest(out / f'{name}.log')})
        write(out / 'runs.json', runs)
        if not passed:
            break
    after = inventory()
    write(out / 'source_after.json', after)
    passed = before == after and len(runs) == len(stages) and all(r['passed'] for r in runs)
    report = {'schema': 1, 'scope': 'WORK_ONLY_REAL_BONUS_OWNER_UI_BOOTSTRAP_ADAPTER_PILOT', 'passed': passed,
              'core_passed': True, 'runs': runs, 'source_unchanged': before == after,
              'core_reused_not_rerun': bool(args.core_evidence),
              'future_chapter_eligibility_double': True, 'CLI_return_intent_seeded': True,
              'actual_bonus_levels_or_real_positive_CH10_CH14_unlock': False,
              'ROOT_installation_Readiness_phase_or_merge_approval': False}
    write(out / 'validation.json', report)
    print(json.dumps(report), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
