#!/usr/bin/env python3
"""P05 story checks and actual Input evidence. Author never decides phase acceptance.

Default requests a renderer/audio device. --headless is technical simulation only.
--exports probes Linux ELF and Wine PE; native Windows remains separate host work.
Use a new empty output directory. All saves are isolated, including process reload.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import time

from verify_p04g import waveform, sha, winpath, write

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
GODOT = ROOT / '.tools/godot' / f'Godot_v{LOCK["release"]}_linux.x86_64'
ERRORS = re.compile(r'SCRIPT ERROR:|ERROR:|FAIL:|ObjectDB instances were leaked|resources still in use')


def sources():
    return {str(p.relative_to(ROOT)): sha(p)
            for folder in ['game', 'tools', '.github/workflows']
            for p in sorted((ROOT / folder).rglob('*'))
            if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--build-output', default='build/P05/host')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--exports', action='store_true')
    parser.add_argument('--movie', action='store_true')
    args = parser.parse_args()
    if args.headless and args.movie:
        parser.error('--movie requires actual rendering')
    output = (ROOT / args.output).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Use a new empty output directory; old evidence is immutable')
    output.mkdir(parents=True, exist_ok=True)
    build = (ROOT / args.build_output).resolve()
    build.mkdir(parents=True, exist_ok=True)
    logs = output / 'logs'
    logs.mkdir()
    local = ROOT / '.tools/p05-qa' / hashlib.sha256(str(output).encode()).hexdigest()[:16]
    local.mkdir(parents=True, exist_ok=True)
    before = sources()
    write(output / 'source_hashes.json', before)
    results = []

    def check(name, checks):
        ok = all(checks.values())
        results.append({'name': name, 'passed': ok, 'checks': checks})
        write(output / 'validation.json', results)
        print(name, 'OK' if ok else 'FAILED_OR_BLOCKED', flush=True)
        return ok

    def run(name, command, env, timeout=300):
        started = time.monotonic()
        command = list(map(str, command))
        try:
            process = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                     text=True, timeout=timeout)
            text, code = process.stdout + process.stderr, process.returncode
        except subprocess.TimeoutExpired as exc:
            def decode(value):
                return value.decode(errors='replace') if isinstance(value, bytes) else (value or '')
            text, code = decode(exc.stdout) + decode(exc.stderr) + '\nTIMEOUT', 124
        except OSError as exc:
            text, code = str(exc), 127
        selected = {k: v for k, v in env.items() if k.startswith('AYAY_') or k in
                    ['XDG_CONFIG_HOME', 'XDG_DATA_HOME', 'WINEPREFIX', 'WINEDEBUG', 'WINEDLLOVERRIDES']}
        log = logs / (name + '.log')
        log.write_text('environment=' + json.dumps(selected, sort_keys=True) + '\n$ ' +
                       shlex.join(command) + '\n' + text + f'\nexit_code={code}\n')
        ok = code == 0 and not ERRORS.search(text)
        results.append({'name': name, 'passed': bool(ok), 'exit_code': code,
                        'log': str(log.relative_to(ROOT)),
                        'elapsed_seconds': round(time.monotonic() - started, 3)})
        write(output / 'validation.json', results)
        print(name, 'OK' if ok else 'FAILED_OR_BLOCKED', flush=True)
        return ok

    def environment(name, wine=False, reduced=False):
        folder = local / name
        folder.mkdir(exist_ok=True)
        convert = winpath if wine else str
        env = dict(os.environ)
        for variable, directory in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data')]:
            (folder / directory).mkdir(exist_ok=True)
            env[variable] = str(folder / directory)
        for key, filename in [('AYAY_OPTIONS_PATH', 'options.json'),
                              ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                              ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json'),
                              ('AYAY_STORY_SAVE_PATH', 'story.json')]:
            env[key] = convert(folder / filename)
        if reduced:
            write(folder / 'options.json', {'schema': 2, 'values': {
                'reduced_gore': True, 'decals': False, 'shake': 0,
                'flashes': False, 'reduced_motion': True, 'vhs': False}})
        if wine:
            env.update(WINEPREFIX=str(local / 'wine-prefix'), WINEARCH='win64',
                       WINEDEBUG='-all', WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
        return env

    def replay(name, command, env, wine=False, resume=False, movie=False):
        convert = winpath if wine else str
        frames = output / (name + '_frames')
        frames.mkdir()
        for key, path in [('AYAY_P05_RESULT_PATH', output / (name + '.json')),
                          ('AYAY_P05_CAPTURE_DIR', frames),
                          ('AYAY_P04_CAPTURE_DIR', frames),
                          ('AYAY_P04_AUDIO_PATH', output / (name + '.wav'))]:
            env[key] = convert(path)
        command = list(command) + ['--', '--p05-replay'] + (['--p05-resume'] if resume else [])
        run(name, command, env)
        result_path = output / (name + '.json')
        data = json.loads(result_path.read_text()) if result_path.is_file() else {}
        checks = {'engine_checks': data.get('passed') is True,
                  'actual_input_no_warps': data.get('actual_input') is True and data.get('route_warps') == 0,
                  'canonical_one_reward': data.get('story', {}).get('completion_rewards') == 1,
                  'all_ch01_facts_once': len(data.get('story', {}).get('history', [])) == 4}
        if not resume:
            old = data.get('p04_input', {})
            checks['p04_retry_route'] = old.get('passed') is True and len(old.get('deaths', [])) == 10
        if not args.headless:
            checks['rendered_frames'] = data.get('rendered') is True and len(list(frames.glob('*.png'))) >= (4 if resume else 13)
            # MovieMaker uses the Dummy mixer; this is explicitly distinct from a live device.
            if not resume:
                audio = data.get('p04_input', {}).get('audio', {})
                checks['audio_driver'] = audio.get('audio_driver') == 'Dummy' if movie else audio.get('audio_driver') not in [None, 'Dummy']
        check(name + '_evidence', checks)
        if not resume:
            signal = waveform(output / (name + '.wav'))
            signal['scope'] = 'Numeric runtime PCM, no listening claim; ' + ('headless Dummy mixer' if args.headless else 'MovieMaker Dummy mixer' if movie else 'live mixer')
            write(output / (name + '_signal.json'), signal)
            if not args.headless:
                check(name + '_signal', {'nonempty_stereo': signal.get('channels') == 2 and signal.get('rms', 0) > .001,
                                          'duration': signal.get('duration', 0) > 40,
                                          'no_clipping': signal.get('full_scale_samples') == 0})
        return data

    def finish():
        check('sources_unchanged', {'exact_hashes': sources() == before})
        write(output / 'environment.json', {
            'platform': platform.platform(), 'scope': 'HEADLESS_TECHNICAL_ONLY' if args.headless else 'RENDERER_REQUESTED',
            'native_windows': 'NOT_TESTED; Wine runtime is recorded separately',
            'listening': 'NOT_CLAIMED; unchanged approved P04G audio, runtime signal evidence is separate from subjective listening',
            'phase_decision': 'NOT_DECIDED_BY_AUTHOR', 'independent_review': 'HOST_PENDING',
            'exports_requested': args.exports, 'movie_requested': args.movie,
            'live_qa_pacing': 'Explicit --disable-vsync --max-fps 60; real-time physics, no fixed-fps substitution' if not args.headless else 'Headless technical execution only',
            'timing_limits': 'Live retry gate remains <1000ms monotonic wall time. Existing P04 frame percentiles use physics delta, not measured wall-frame FPS. One host run does not prove all compositor/default-vsync conditions.',
            'linked_worktree_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()})
        write(output / 'artifacts.json', [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size, 'sha256': sha(p)}
                                        for p in sorted(output.rglob('*')) if p.is_file() and p.name != 'artifacts.json'])
        return 0 if all(row['passed'] for row in results) else 1

    if not check('pinned_engine', {'sha256': GODOT.is_file() and sha(GODOT) == LOCK['linux_binary_sha256']}):
        return finish()
    if args.exports and not check('export_runtime_preflight', {
            'existing_wine_runtime': (ROOT / '.tools/wine/usr/bin/wine').is_file()}):
        return finish()
    base = [GODOT, '--headless', '--path', ROOT / 'game']
    for suite in ['story_registry', 'story_state', 'story_graph', 'story_integration']:
        env = environment(suite)
        env['AYAY_STORY_GRAPH_PATH'] = str(output / 'graph_exploration.json')
        run(suite, base + ['--script', f'res://tests/{suite}_test.gd'], env)
    graph_path = output / 'graph_exploration.json'
    graph = json.loads(graph_path.read_text()) if graph_path.is_file() else {}
    check('exploration_counts', {'paths_6344': graph.get('paths') == 6344,
                                 'zero_failures': graph.get('failures') == 0,
                                 'explicit_states': graph.get('unique_observed_states', 0) > 20000,
                                 'four_reproducible_routes': len(graph.get('reproducible_witnesses', {})) == 4})
    command = [GODOT, '--path', ROOT / 'game']
    if args.headless:
        command += ['--headless', '--fixed-fps', '60', '--disable-vsync', '--max-fps', '0']
    else:
        # Keep renderer pacing explicit for unattended QA; preserve real-time physics
        # and the unchanged <1000ms wall-clock retry gate in mission_replay.gd.
        command += ['--disable-vsync', '--max-fps', '60']
        if not run('native_probe', command + ['--', '--smoke-bootstrap'], environment('native_probe'), 20):
            write(output / 'host_pending.json', {'reason': 'Renderer/audio probe failed; no native evidence claim',
                                               'command': 'python3 tools/verify_p05.py --exports --movie --output reports/phases/P05/attempt1/native-host-01 --build-output build/P05/native-host-01'})
            return finish()
    env = environment('input')
    full = replay('input', command, env)
    replay('process_reload', command, env, resume=True)
    reduced = replay('reduced_input', command, environment('reduced', reduced=True))
    check('full_reduced_story_invariance', {'same_story': bool(full.get('story')) and full.get('story') == reduced.get('story')})
    if args.movie:
        movie = build / 'story.avi'
        replay('movie', [GODOT, '--path', ROOT / 'game', '--disable-vsync', '--max-fps', '60', '--write-movie', movie, '--fixed-fps', '60'], environment('movie'), movie=True)
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            pinned = ROOT / '.tools/ci-media/bin/ffmpeg'
            ffmpeg = str(pinned) if pinned.is_file() else None
        if check('movie_tools', {'avi': movie.is_file() and movie.stat().st_size > 1000, 'ffmpeg': bool(ffmpeg)}):
            run('encode_movie', [ffmpeg, '-v', 'error', '-y', '-i', movie, '-c:v', 'libx264', '-crf', '20',
                                 '-pix_fmt', 'yuv420p', '-c:a', 'aac', output / 'story.mp4'], environment('encode'))
    if args.exports:
        exports = []
        for preset, folder, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'),
                                                ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
            target = build / folder / filename
            target.parent.mkdir(exist_ok=True)
            clean = run('export_' + folder, [GODOT, '--headless', '--path', ROOT / 'game', '--export-release', preset, target], environment('export_' + folder))
            present = target.is_file() and target.read_bytes().startswith(magic)
            check('export_' + folder + '_artifact', {'magic': present, 'clean_log': clean})
            row = {'platform': preset, 'path': str(target.relative_to(ROOT)), 'artifact_present': present,
                   'native_windows': 'NOT_TESTED' if folder == 'windows' else None}
            if present:
                row.update(sha256=sha(target), bytes=target.stat().st_size)
                if folder == 'linux':
                    target.chmod(0o755)
                    runtime = [target] + (['--headless', '--fixed-fps', '60', '--max-fps', '0'] if args.headless else ['--disable-vsync', '--max-fps', '60'])
                    replay('linux_input', runtime, environment('linux_input'))
                else:
                    wine = ROOT / '.tools/wine/usr/bin/wine'
                    env = environment('windows_input', wine=True)
                    runtime = [wine, target] + (['--headless', '--fixed-fps', '60', '--max-fps', '0'] if args.headless else ['--disable-vsync', '--max-fps', '60'])
                    row['wine_probe'] = run('wine_probe', runtime + ['--', '--smoke-bootstrap'], env, 30)
                    if row['wine_probe']:
                        replay('wine_input', runtime, env, wine=True)
            exports.append(row)
        write(output / 'exports.json', exports)
    return finish()


if __name__ == '__main__':
    raise SystemExit(main())
