#!/usr/bin/env python3
"""Actual registered Pasha moving shot Input replay. Component only, never a P06 verdict."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from verify_p06_cast import ROOT, GODOT, ERRORS, sha, sources, write

SCOPE = 'PASHA_MOVING_SHOT_COMPONENT_ONLY'

def valid_replay(result, headless):
    if not isinstance(result, dict) or result.get('scope') != SCOPE:
        return False
    if result.get('phase_approval') is not False or result.get('actual_input') is not True or result.get('passed') is not True:
        return False
    allowed_renderers = {'headless'} if headless else {'X11', 'Wayland'}
    if not isinstance(result.get('renderer'), str) or result['renderer'] not in allowed_renderers:
        return False
    checks = result.get('checks')
    return bool(isinstance(checks, list) and checks and
                all(isinstance(c, dict) and c.get('passed') is True for c in checks) and
                isinstance(result.get('trace'), list) and result['trace'] and
                isinstance(result.get('contacts'), list) and result['contacts'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--movie', action='store_true')
    parser.add_argument('--build-output')
    args = parser.parse_args()
    if args.movie and (args.headless or not args.build_output):
        parser.error('Movie requires native renderer and a fresh --build-output')
    output = (ROOT / args.output).resolve()
    if output.exists(): parser.error('Use a new evidence directory; never replay consumed jobs')
    output.mkdir(parents=True)
    build = (ROOT / args.build_output).resolve() if args.build_output else None
    if build:
        if build.exists(): parser.error('Use a new movie directory')
        build.mkdir(parents=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    if sha(GODOT) != lock['linux_binary_sha256']: raise SystemExit('Pinned Godot hash mismatch')
    before = sources()
    write(output / 'source_hashes.json', before)
    commands = []
    results = []
    for mode in ['live', 'movie'] if args.movie else ['live']:
        scope = output / mode
        scope.mkdir()
        profile = ROOT / '.tools/p06-pasha-moving-shot-qa' / hashlib.sha256(str(scope).encode()).hexdigest()[:20]
        profile.mkdir(parents=True)
        env = os.environ | {'AYAY_P06_PASHA_OUTPUT': str(scope)}
        for key, filename in [('AYAY_STORY_SAVE_PATH', 'story.json'),
                              ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json'),
                              ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                              ('AYAY_OPTIONS_PATH', 'options.json')]:
            env[key] = str(profile / filename)
        env['XDG_CONFIG_HOME'] = str(profile / 'config')
        env['XDG_DATA_HOME'] = str(profile / 'data')
        argv = [str(GODOT), '--path', str(ROOT / 'game'), '--disable-vsync', '--max-fps', '60']
        if args.headless: argv += ['--headless', '--fixed-fps', '60']
        if mode == 'movie': argv += ['--write-movie', str(build / 'pasha-moving-shot.avi'), '--fixed-fps', '60']
        argv += ['--script', 'res://tests/pasha_moving_shot_replay.gd']
        started = time.monotonic()
        try:
            run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True,
                                 timeout=300 if mode == 'movie' else 210)
            code, log = run.returncode, run.stdout + run.stderr
        except subprocess.TimeoutExpired as error:
            code, log = 124, 'TIMEOUT\n' + str(error.stdout) + str(error.stderr)
        (output / (mode + '.log')).write_text(log + '\nexit_code=' + str(code) + '\n')
        result = json.loads((scope / 'result.json').read_text()) if (scope / 'result.json').is_file() else {}
        ok = bool(code == 0 and not ERRORS.search(log) and valid_replay(result, args.headless))
        commands.append({'name': mode, 'argv': argv, 'exit_code': code, 'passed': ok,
                         'seconds': round(time.monotonic() - started, 3), 'profile': str(profile)})
        results.append(result)
        write(output / 'commands.json', commands)
        print(mode, 'PASS' if ok else 'FAIL', flush=True)
        if not ok: break
    movie_probe = {}
    if args.movie and all(c['passed'] for c in commands):
        ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
        if not ffmpeg or not ffprobe: raise SystemExit('Existing ffmpeg/ffprobe required')
        argv = [ffmpeg, '-v', 'error', '-n', '-i', str(build / 'pasha-moving-shot.avi'),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                '-movflags', '+faststart', str(build / 'pasha-moving-shot.mp4')]
        run = subprocess.run(argv, capture_output=True, text=True, timeout=100)
        (output / 'encode.log').write_text(run.stdout + run.stderr)
        commands.append({'name': 'encode', 'argv': argv, 'exit_code': run.returncode, 'passed': run.returncode == 0})
        if run.returncode == 0:
            argv = [ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(build / 'pasha-moving-shot.mp4')]
            probe = subprocess.run(argv, capture_output=True, text=True, timeout=20)
            movie_probe = json.loads(probe.stdout) if probe.returncode == 0 else {}
            commands.append({'name': 'probe', 'argv': argv, 'exit_code': probe.returncode,
                             'passed': any(s.get('codec_type') == 'video' and int(s.get('nb_frames', 0)) >= 120 for s in movie_probe.get('streams', []))})
            write(output / 'movie_probe.json', movie_probe)
    unchanged = before == sources()
    ok = all(c['passed'] for c in commands) and unchanged
    summary = {'scope': 'PASHA_MOVING_SHOT_COMPONENT_ONLY', 'phase_approval': False, 'passed': ok,
               'source_unchanged': unchanged, 'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'headless': args.headless, 'actual_input': all(r.get('actual_input') for r in results),
               'checks': [{'passed': sum(c['passed'] for c in r.get('checks', [])), 'total': len(r.get('checks', []))} for r in results],
               'actual_captures': len(list(output.rglob('*.png'))), 'commands': commands,
               'movie_path': str(build / 'pasha-moving-shot.mp4') if movie_probe else None,
               'audio': 'Existing runtime cues only; no new media or listening claim',
               'native_windows': 'NOT_TESTED', 'exports': 'NOT_REQUESTED_FOR_THIS_COMPONENT'}
    summary['artifacts'] = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in sorted(output.rglob('*')) if p.is_file()]
    write(output / 'validation.json', summary)
    print(json.dumps({k: summary[k] for k in ['passed', 'checks', 'actual_captures', 'source_unchanged']}))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
