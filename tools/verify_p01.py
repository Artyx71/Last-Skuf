#!/usr/bin/env python3
"""P01 native art/movement tests, live render/replay and separate platform builds."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'reports/phases/P01'
BUILD = ROOT / 'build/P01'
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
GODOT = str(ROOT / '.tools/godot' / f'Godot_v{LOCK["release"]}_linux.x86_64')


def main():
    (OUTPUT / 'logs').mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(Path(GODOT).read_bytes()).hexdigest() == LOCK['linux_binary_sha256']
    results = []

    def run(name, command, env=None, timeout=90):
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            text, code = result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            text, code = str(error), 124
        ok = code == 0 and not any(x in text for x in ['SCRIPT ERROR:', 'ERROR:', 'FAIL:'])
        (OUTPUT / 'logs' / (name + '.log')).write_text('$ ' + ' '.join(command) + '\n' + text + f'\nexit_code={code}\n')
        results.append({'name': name, 'passed': ok, 'exit_code': code})
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        return ok

    base = [GODOT, '--headless', '--path', 'game']
    run('references', [sys.executable, 'tools/validate_pack.py'])
    run('privacy', [sys.executable, 'tools/check_privacy.py'])
    run('import', base + ['--editor', '--quit'])
    for test in ['bootstrap', 'art_structure', 'movement']:
        run(test, base + ['--script', f'res://tests/{test}_test.gd'])
    if all(r['passed'] for r in results):
        scene = 'res://scenes/world/movement_lab.tscn'
        env = dict(os.environ, AYAY_CAPTURE_PATH=str(OUTPUT / 'movement_lab.png'))
        run('render_lab', [GODOT, '--path', 'game', scene, '--', '--capture-lab'], env)
        past_env = dict(env, AYAY_CAPTURE_PATH=str(OUTPUT / 'movement_lab_past.png'), AYAY_LAB_PAST='1')
        run('render_lab_past', [GODOT, '--path', 'game', scene, '--', '--capture-lab'], past_env)
        run('replay', [GODOT, '--path', 'game', '--write-movie', str(BUILD / 'movement.avi'),
                       '--fixed-fps', '60', scene, '--', '--lab-replay'], timeout=120)
        if (BUILD / 'movement.avi').exists():
            run('encode_replay', ['ffmpeg', '-y', '-i', str(BUILD / 'movement.avi'), '-an', '-c:v', 'libx264',
                                  '-crf', '18', '-pix_fmt', 'yuv420p', str(OUTPUT / 'movement_replay.mp4')])
            run('replay_contact_sheet', ['ffmpeg', '-y', '-i', str(OUTPUT / 'movement_replay.mp4'),
                                        '-vf', 'fps=2,scale=640:360,tile=4x4', '-frames:v', '1', str(OUTPUT / 'animation_contact_sheet.png')])
        exports = []
        for preset, directory, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'),
                                                   ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
            target = BUILD / directory / filename
            target.parent.mkdir(exist_ok=True)
            ok = run('export_' + directory, base + ['--export-release', preset, str(target)], timeout=120)
            record = {'platform': preset, 'export_passed': ok, 'path': str(target.relative_to(ROOT)),
                      'runtime': 'BLOCKED: Windows/Wine unavailable' if preset == 'Windows' else 'not tested'}
            if ok and target.is_file():
                assert target.read_bytes().startswith(magic)
                record['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
                if preset == 'Linux':
                    target.chmod(0o755)
                    record['runtime'] = 'PASS' if run('linux_smoke', [str(target), '--headless', '--quit']) else 'FAIL'
                    env['AYAY_CAPTURE_PATH'] = str(OUTPUT / 'export_linux_lab.png')
                    record['lab_render_passed'] = run('linux_lab_render', [str(target), '--', '--open-lab', '--capture-lab'], env)
            exports.append(record)
        (OUTPUT / 'exports.json').write_text(json.dumps(exports, indent=2) + '\n')
    (OUTPUT / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
    return not all(r['passed'] for r in results)


if __name__ == '__main__':
    sys.exit(main())
