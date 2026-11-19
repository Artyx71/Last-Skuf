#!/usr/bin/env python3
"""Exercise the real CH01 navigation host, save/retry and existing mission controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory():
    return {str(p.relative_to(ROOT)): digest(p) for directory in ['game', 'tools']
            for p in sorted((ROOT / directory).rglob('*'))
            if p.is_file() and not any(x in p.parts for x in ['.godot', '__pycache__'])}

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--native', action='store_true', help='Also run existing real-input chapter replay with native renderer')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit('Use a fresh output directory; preserve earlier attempts')
    out.mkdir(parents=True)
    before = inventory()
    write(out / 'source_before.json', before)
    project = out / 'isolated_project/game'
    shutil.copytree(ROOT / 'game', project, ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    shutil.copy2(ROOT / 'tools/fixtures/p07_room_pilot.gd', project / 'tests/p07_room_pilot.gd')
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    stages = [('import', ['--headless', '--editor', '--quit']),
              ('room', ['--headless', '--fixed-fps', '60', '--script', 'res://tests/p07_room_pilot.gd']),
              ('mission', ['--headless', '--script', 'res://tests/mission_test.gd'])]
    if args.native:
        stages.append(('native', ['--', '--open-mission', '--p04-replay']))
    runs = []
    for name, flags in stages:
        isolate = out / 'isolated_saves' / name
        capture = out / 'native_captures'
        if name == 'native':
            capture.mkdir()
        env = dict(os.environ)
        env.update(XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
                   XDG_CACHE_HOME=str(isolate / 'cache'), GODOT_SILENCE_ROOT_WARNING='1',
                   AYAY_P07_ROOM_PILOT_RESULT=str(out / 'room-result.json'),
                   AYAY_P04_RESULT_PATH=str(out / 'native-result.json'),
                   AYAY_P04_CAPTURE_DIR=str(capture))
        argv = [str(engine), '--path', str(project), *flags]
        process = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        log = process.stdout + process.stderr
        (out / f'{name}.log').write_text(log + f'\nexit_code={process.returncode}\n')
        ok = process.returncode == 0 and not any(x in log for x in ['SCRIPT ERROR:', 'Parse Error:'])
        runs.append({'name': name, 'argv': argv, 'exit_code': process.returncode, 'passed': ok})
        write(out / 'runs.json', runs)
        if not ok:
            break
    after = inventory()
    write(out / 'source_after.json', after)
    room = json.loads((out / 'room-result.json').read_text()) if (out / 'room-result.json').exists() else None
    passed = len(runs) == len(stages) and all(r['passed'] for r in runs) and before == after and room is not None and room['failed'] == 0
    native = json.loads((out / 'native-result.json').read_text()) if (out / 'native-result.json').exists() else None
    if args.native:
        passed = passed and native is not None and native.get('passed') is True
    result = {'schema': 1, 'passed': passed, 'scope': 'CH01_EXISTING_PRODUCTION_HOST_NAVIGATION_PILOT_COMPONENT',
              'runs': runs, 'room_checks': room['passed'] if room else None,
              'native_replay_passed': native.get('passed') if native else None,
              'source_game_and_tools_unchanged': before == after, 'engine_sha256': digest(engine),
              'full_H02_Readiness_or_P07_approval': False,
              'new_export_audio_listening_hardware_latency_or_campaign_duration_claim': False}
    write(out / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if passed else 1

if __name__ == '__main__':
    raise SystemExit(main())
