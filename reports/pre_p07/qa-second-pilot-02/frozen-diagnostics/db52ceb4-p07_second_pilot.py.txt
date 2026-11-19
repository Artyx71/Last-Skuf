#!/usr/bin/env python3
"""Actual second navigation layout, all seven bodies and live door/AI probes."""
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
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        raise SystemExit('Fresh output required; preserve previous evidence')
    out.mkdir(parents=True)
    before = inventory()
    write(out / 'source_before.json', before)
    project = out / 'isolated_project/game'
    shutil.copytree(ROOT / 'game', project, ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    for name in ['p07_second_pilot.gd', 'p07_second_pilot_host.gd']:
        shutil.copy2(ROOT / 'tools/fixtures' / name, project / 'tests' / name)
    config = json.loads((ROOT / 'game/resources/combat/prototype.json').read_text())
    config.update(player_spawn=[80, 280], exit=[-4096, -4096, 16, 16],
                  walls=[[0, 0, 640, 16], [0, 344, 640, 16], [0, 0, 16, 360], [624, 0, 16, 360],
                         [304, 16, 16, 96], [304, 176, 16, 72], [304, 312, 16, 32], [176, 200, 48, 80]],
                  spawns=[{'kind': k, 'position': [128, 144 + i * 24], 'patrol_end': [544, 280]}
                          for i, k in enumerate(['patrol', 'rusher', 'shooter'])])
    write(project / 'tests/p07_second_pilot.json', config)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    stages = [('import', ['--headless', '--editor', '--quit']),
              ('pilot', ['--headless', '--fixed-fps', '60', '--script', 'res://tests/p07_second_pilot.gd'])]
    if args.native:
        stages.append(('native', ['--disable-vsync', '--max-fps', '60', '--script', 'res://tests/p07_second_pilot.gd']))
    runs = []
    for name, flags in stages:
        isolate = out / 'isolated_saves' / name
        result = out / f'{name}-result.json'
        capture = out / f'{name}-captures'
        capture.mkdir()
        env = dict(os.environ, XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
                   XDG_CACHE_HOME=str(isolate / 'cache'), GODOT_SILENCE_ROOT_WARNING='1',
                   AYAY_P07_SECOND_RESULT=str(result), AYAY_P07_SECOND_CAPTURE=str(capture))
        argv = [str(engine), '--path', str(project), *flags]
        process = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=480)
        log = process.stdout + process.stderr
        (out / f'{name}.log').write_text(log + f'\nexit_code={process.returncode}\n')
        data = json.loads(result.read_text()) if result.exists() else None
        ok = process.returncode == 0 and not any(x in log for x in ['SCRIPT ERROR:', 'Parse Error:'])
        if name != 'import':
            ok = ok and data is not None and data['failed'] == 0 and data['passed'] >= 50
        runs.append({'name': name, 'argv': argv, 'exit_code': process.returncode, 'passed': ok})
        write(out / 'runs.json', runs)
        if not ok:
            break
    after = inventory()
    write(out / 'source_after.json', after)
    passed = len(runs) == len(stages) and all(row['passed'] for row in runs) and before == after
    result = {'schema': 1, 'passed': passed, 'scope': 'SECOND_TECHNICAL_NAVIGATION_PILOT_NOT_CAMPAIGN',
              'runs': runs, 'source_game_tools_unchanged': before == after, 'engine_sha256': digest(engine),
              'full_H02_Readiness_phase_or_content_approval': False}
    write(out / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
