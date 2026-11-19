#!/usr/bin/env python3
"""One finite legacy-native supplement after the broad adapter review loop stopped."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from p07_room_pilot import ROOT, digest, inventory, write

DRIVER = 'game/scripts/qa/story_replay.gd'


def decoded(value):
    return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--runtime-evidence', type=Path, required=True)
    args = parser.parse_args()
    out, original = args.output.resolve(), args.runtime_evidence.resolve()
    if out.exists():
        raise SystemExit('Fresh finite-supplement output required')
    out.mkdir(parents=True)
    before = inventory()
    write(out / 'source_before.json', before)
    prior = json.loads((original / 'source_before.json').read_text())
    old_runs = json.loads((original / 'runs.json').read_text())
    assert [(r['name'], r['passed']) for r in old_runs[:4]] == [('live', True), ('cli', True), ('native', True), ('native_cli', True)]
    game = {key for key in before if key.startswith('game/')}
    assert game == {key for key in prior if key.startswith('game/')}
    assert all(before[key] == prior[key] for key in game - {DRIVER}), 'Runtime changes exceed the finite driver-only supplement'
    project = out / 'isolated_project/game'
    shutil.copytree(original / 'isolated_project/game', project)
    target = project / Path(DRIVER).relative_to('game')
    shutil.copyfile(ROOT / DRIVER, target)
    assert all(digest(project / Path(key).relative_to('game')) == before[key] for key in game)
    write(out / 'runtime-equivalence.json', {'only_changed_Game_input': DRIVER,
          'old_driver_sha256': prior[DRIVER], 'new_driver_sha256': before[DRIVER],
          'unchanged_runtime_pins': {key: before[key] for key in sorted(game - {DRIVER})},
          'retained_four_adapter_stages': str(original / 'runs.json'), 'not_a_fourth_broad_pipeline': True})
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    isolate = out / 'isolated_saves'
    profile = isolate / 'profile'
    profile.mkdir(parents=True)
    captures = out / 'captures'
    captures.mkdir()
    result = out / 'result.json'
    env = dict(os.environ, XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
               XDG_CACHE_HOME=str(isolate / 'cache'), AYAY_STORY_SAVE_PATH=str(profile / 'story.json'),
               AYAY_P05_CAPTURE_DIR=str(captures), AYAY_P05_RESULT_PATH=str(result), GODOT_SILENCE_ROOT_WARNING='1')
    argv = [str(engine), '--path', str(project), '--disable-vsync', '--max-fps', '60', '--', '--p05-replay']
    started = time.monotonic()
    timed_out = False
    try:
        process = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=180)
        code, log = process.returncode, process.stdout + process.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        code, log = None, decoded(error.stdout) + decoded(error.stderr) + '\nTIMEOUT 180s (unchanged)\n'
    (out / 'native.log').write_text(log)
    data = json.loads(result.read_text()) if result.exists() else {}
    checks = data.get('checks', {})
    after = inventory()
    write(out / 'source_after.json', after)
    passed = code == 0 and isinstance(checks, dict) and bool(checks) and all(v is True for v in checks.values()) \
        and data.get('passed') is True and data.get('rendered') is True and data.get('route_warps') == 0 \
        and before == after and not any(s in log for s in ['SCRIPT ERROR:', 'Parse Error:', 'FAIL: P05'])
    report = {'schema': 1, 'scope': 'FINITE_NATIVE_OLD_STORY_REPLAY_DRIVER_SUPPLEMENT_ONLY', 'passed': passed,
              'argv': argv, 'exit_code': code, 'timed_out': timed_out, 'timeout_seconds': 180,
              'wall_seconds': round(time.monotonic() - started, 3), 'checks': len(checks),
              'source_unchanged': before == after, 'log_sha256': digest(out / 'native.log'),
              'broad_review_budget_reset_or_H05_Readiness_approval': False}
    write(out / 'validation.json', report)
    print(json.dumps(report), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
