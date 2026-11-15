#!/usr/bin/env python3
"""Actual registered Timka prime/two-context Input replay. Component only, never a P06 verdict."""
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

def completed_live_evidence(folder, current_sources):
    """Only a complete, unchanged native run may support a separate movie job."""
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value: raise ValueError('Duplicate evidence key: ' + key)
            value[key] = item
        return value
    def invalid_constant(value):
        raise ValueError('Non-finite evidence value: ' + value)
    def read(path):
        return json.loads(path.read_text(), object_pairs_hook=unique, parse_constant=invalid_constant)
    folder = folder.resolve()
    if not folder.is_relative_to(ROOT / 'reports'):
        raise ValueError('Live evidence must be inside project reports')
    manifest = folder / 'validation.json'
    report = read(manifest)
    if not (report.get('scope') == 'TIMKA_PRIME_CONTEXT_CANDIDATE_ONLY' and
            report.get('passed') is True and report.get('source_unchanged') is True and
            report.get('headless') is False and report.get('actual_input') is True and
            report.get('phase_approval') is False and report.get('movie_path') is None):
        raise ValueError('A complete native live-only validation is required')
    if read(folder / 'source_hashes.json') != current_sources:
        raise ValueError('Live source snapshot differs; do not reuse stale gameplay')
    commands = report.get('commands')
    if not (isinstance(commands, list) and len(commands) == 1 and
            commands[0].get('name') == 'live' and commands[0].get('passed') is True and
            type(commands[0].get('exit_code')) is int and commands[0]['exit_code'] == 0):
        raise ValueError('A successful native live command receipt is required')
    expected_argv = [str(GODOT), '--path', str(ROOT / 'game'), '--disable-vsync', '--max-fps', '60',
                     '--script', 'res://tests/timka_prime_replay.gd']
    if commands[0].get('argv') != expected_argv:
        raise ValueError('Live command does not match the current native replay')
    artifacts = report.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('Missing live artifact inventory')
    verified_paths = set()
    for item in artifacts:
        path = (ROOT / item['path']).resolve()
        if not path.is_relative_to(folder) or not path.is_file() or sha(path) != item['sha256']:
            raise ValueError('Live artifact missing, outside its run, or changed: ' + str(path))
        verified_paths.add(path)
    result_path = folder / 'live/result.json'
    if not {result_path, folder / 'source_hashes.json', folder / 'live.log', folder / 'commands.json'} <= verified_paths:
        raise ValueError('Required completed live artifacts are not bound')
    result = read(result_path)
    if not (result.get('passed') is True and result.get('actual_input') is True and
            result.get('renderer') not in [None, '', 'headless'] and result.get('checks') and
            all(item.get('passed') is True for item in result['checks'])):
        raise ValueError('Native live result does not establish successful actual Input')
    captures = result.get('captures')
    if not isinstance(captures, list) or not captures or type(report.get('actual_captures')) is not int or len(captures) != report['actual_captures']:
        raise ValueError('Completed native captures are required')
    for item in captures:
        if item.get('code') != 0 or Path(item['path']).resolve() not in verified_paths:
            raise ValueError('Native capture is not bound to the verified live inventory')
    if ERRORS.search((folder / 'live.log').read_text()):
        raise ValueError('Live log contains engine/test errors')
    return {'validation': str(manifest.relative_to(ROOT)), 'sha256': sha(manifest),
            'source_head': report['source_head'], 'checks': report['checks'],
            'captures': report['actual_captures'], 'all_artifacts_verified': True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--headless', action='store_true')
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--movie', action='store_true')
    modes.add_argument('--movie-only', action='store_true')
    parser.add_argument('--live-evidence')
    parser.add_argument('--build-output')
    args = parser.parse_args()
    movie_requested = args.movie or args.movie_only
    if movie_requested and (args.headless or not args.build_output):
        parser.error('Movie requires native renderer and a fresh --build-output')
    if bool(args.live_evidence) != args.movie_only:
        parser.error('--movie-only requires --live-evidence from a completed identical native live run')
    before = sources()
    reused_live = None
    if args.movie_only:
        try:
            reused_live = completed_live_evidence(ROOT / args.live_evidence, before)
        except (ValueError, OSError, KeyError, TypeError) as error:
            parser.error(str(error))
    output = (ROOT / args.output).resolve()
    if output.exists(): parser.error('Use a new evidence directory; never replay consumed jobs')
    output.mkdir(parents=True)
    build = (ROOT / args.build_output).resolve() if args.build_output else None
    if build:
        if build.exists(): parser.error('Use a new movie directory')
        build.mkdir(parents=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    if sha(GODOT) != lock['linux_binary_sha256']: raise SystemExit('Pinned Godot hash mismatch')
    write(output / 'source_hashes.json', before)
    commands = []
    results = []
    for mode in (['movie'] if args.movie_only else (['live', 'movie'] if args.movie else ['live'])):
        scope = output / mode
        scope.mkdir()
        profile = ROOT / '.tools/p06-timka-prime-qa' / hashlib.sha256(str(scope).encode()).hexdigest()[:20]
        profile.mkdir(parents=True)
        env = os.environ | {'AYAY_P06_TIMKA_PRIME_OUTPUT': str(scope)}
        for key, filename in [('AYAY_STORY_SAVE_PATH', 'story.json'),
                              ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json'),
                              ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                              ('AYAY_OPTIONS_PATH', 'options.json')]:
            env[key] = str(profile / filename)
        env['XDG_CONFIG_HOME'] = str(profile / 'config')
        env['XDG_DATA_HOME'] = str(profile / 'data')
        argv = [str(GODOT), '--path', str(ROOT / 'game'), '--disable-vsync', '--max-fps', '60']
        if args.headless: argv += ['--headless', '--fixed-fps', '60']
        if mode == 'movie': argv += ['--write-movie', str(build / 'timka-prime.avi'), '--fixed-fps', '60']
        argv += ['--script', 'res://tests/timka_prime_replay.gd']
        started = time.monotonic()
        try:
            run = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True,
                                 timeout=180 if mode == 'movie' else 140)
            code, log = run.returncode, run.stdout + run.stderr
        except subprocess.TimeoutExpired as error:
            code, log = 124, 'TIMEOUT\n' + str(error.stdout) + str(error.stderr)
        (output / (mode + '.log')).write_text(log + '\nexit_code=' + str(code) + '\n')
        result = json.loads((scope / 'result.json').read_text()) if (scope / 'result.json').is_file() else {}
        ok = bool(code == 0 and not ERRORS.search(log) and result.get('passed') and
                  result.get('actual_input') and ((result.get('renderer') == 'headless') == args.headless))
        commands.append({'name': mode, 'argv': argv, 'exit_code': code, 'passed': ok,
                         'seconds': round(time.monotonic() - started, 3), 'profile': str(profile)})
        results.append(result)
        write(output / 'commands.json', commands)
        print(mode, 'PASS' if ok else 'FAIL', flush=True)
        if not ok: break
    movie_probe = {}
    if movie_requested and all(c['passed'] for c in commands):
        ffmpeg, ffprobe = shutil.which('ffmpeg'), shutil.which('ffprobe')
        if not ffmpeg or not ffprobe: raise SystemExit('Existing ffmpeg/ffprobe required')
        argv = [ffmpeg, '-v', 'error', '-n', '-i', str(build / 'timka-prime.avi'),
                '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac',
                '-movflags', '+faststart', str(build / 'timka-prime.mp4')]
        run = subprocess.run(argv, capture_output=True, text=True, timeout=100)
        (output / 'encode.log').write_text(run.stdout + run.stderr)
        commands.append({'name': 'encode', 'argv': argv, 'exit_code': run.returncode, 'passed': run.returncode == 0})
        if run.returncode == 0:
            argv = [ffprobe, '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(build / 'timka-prime.mp4')]
            probe = subprocess.run(argv, capture_output=True, text=True, timeout=20)
            movie_probe = json.loads(probe.stdout) if probe.returncode == 0 else {}
            commands.append({'name': 'probe', 'argv': argv, 'exit_code': probe.returncode,
                             'passed': any(s.get('codec_type') == 'video' and int(s.get('nb_frames', 0)) >= 120 for s in movie_probe.get('streams', []))})
            write(output / 'movie_probe.json', movie_probe)
    unchanged = before == sources()
    ok = all(c['passed'] for c in commands) and unchanged
    summary = {'scope': 'TIMKA_PRIME_CONTEXT_CANDIDATE_ONLY', 'phase_approval': False, 'passed': ok,
               'source_unchanged': unchanged, 'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'headless': args.headless, 'actual_input': all(r.get('actual_input') for r in results),
               'checks': [{'passed': sum(c['passed'] for c in r.get('checks', [])), 'total': len(r.get('checks', []))} for r in results],
               'actual_captures': len(list(output.rglob('*.png'))), 'commands': commands,
               'reused_completed_live': reused_live,
               'movie_path': str(build / 'timka-prime.mp4') if movie_probe else None,
               'audio': 'Existing runtime cues only; no new media or listening claim',
               'native_windows': 'NOT_TESTED', 'exports': 'NOT_REQUESTED_FOR_THIS_COMPONENT'}
    summary['artifacts'] = [{'path': str(p.relative_to(ROOT)), 'sha256': sha(p)} for p in sorted(output.rglob('*')) if p.is_file()]
    write(output / 'validation.json', summary)
    print(json.dumps({k: summary[k] for k in ['passed', 'checks', 'actual_captures', 'source_unchanged']}))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
