#!/usr/bin/env python3
"""P03 technical evidence: real rendered replay/audio, phase poses, fresh exports.

Run native evidence first with --no-exports, then --exports-only after sources
are frozen. Run without flags for the complete technical acceptance. This does
not replace independent review, human listening, or tools/verify.py regressions.
"""
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import struct
import subprocess
import sys
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
GODOT = ROOT / '.tools/godot' / f'Godot_v{LOCK["release"]}_linux.x86_64'
ERROR_PATTERN = re.compile(r'SCRIPT ERROR:|ERROR:|FAIL:|\bFAILED\b')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources():
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT / 'game').rglob('*'))
            if p.is_file() and '.godot' not in p.parts}


def windows_path(path):
    return 'Z:' + str(path.resolve()).replace('/', '\\')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='reports/phases/P03')
    parser.add_argument('--build-output', default='build/P03')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-exports', action='store_true')
    group.add_argument('--exports-only', action='store_true')
    group.add_argument('--snapshots-only', action='store_true', help='refresh only the four native dialogue/accessibility snapshots')
    parser.add_argument('--movie', action='store_true', help='also record a separate MovieMaker replay')
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    build = (ROOT / args.build_output).resolve()
    logs = output / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    isolated = ROOT / '.tools/p03-qa-state'
    isolated.mkdir(parents=True, exist_ok=True)
    validation_path = output / 'technical_validation.json'
    results = json.loads(validation_path.read_text()) if (args.exports_only or args.snapshots_only) and validation_path.exists() else []
    before = sources()
    snapshot_name = 'export_source_hashes.json' if args.exports_only else 'native_source_hashes.json'
    (output / snapshot_name).write_text(json.dumps(before, indent=2) + '\n')

    def save():
        validation_path.write_text(json.dumps(results, indent=2) + '\n')

    def check(name, checks, details=None):
        row = {'name': name, 'passed': all(checks.values()), 'checks': checks}
        if details is not None:
            row['details'] = details
        results[:] = [r for r in results if r['name'] != name]
        results.append(row)
        save()
        print(name, 'PASS' if row['passed'] else 'FAIL', flush=True)
        return row['passed']

    def run(name, command, env=None, timeout=180):
        command = list(map(str, command))
        start = time.monotonic()
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            text, code = result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            text = (error.stdout or b'').decode(errors='replace') if isinstance(error.stdout, bytes) else error.stdout or ''
            text += '\nTIMEOUT\n'
            code = 124
        matches = ERROR_PATTERN.findall(text)
        log = logs / (name + '.log')
        selected_env = {key: value for key, value in (env or {}).items() if key.startswith('AYAY_') or key in {'WINEPREFIX', 'WINEARCH', 'WINEDEBUG', 'WINEDLLOVERRIDES'}}
        log.write_text('environment=' + json.dumps(selected_env, sort_keys=True) + '\n$ ' + shlex.join(command) + '\n' + text + f'\nexit_code={code}\n')
        row = {'name': name, 'passed': code == 0 and not matches, 'exit_code': code,
               'error_tokens': matches, 'elapsed_seconds': round(time.monotonic() - start, 3),
               'log': str(log.relative_to(ROOT))}
        results[:] = [r for r in results if r['name'] != name]
        results.append(row)
        save()
        print(name, 'PASS' if row['passed'] else 'FAIL', flush=True)
        return row['passed']

    def environment(name, wine=False):
        settings = isolated / (name + '-options.json')
        dialogue = isolated / (name + '-dialogue.json')
        for path in [settings, dialogue, Path(str(settings) + '.tmp'), Path(str(dialogue) + '.tmp')]:
            path.unlink(missing_ok=True)
        convert = windows_path if wine else str
        env = dict(os.environ, AYAY_OPTIONS_PATH=convert(settings), AYAY_DIALOGUE_SAVE_PATH=convert(dialogue))
        if wine:
            env.update(WINEPREFIX=str(ROOT / '.tools/wine-prefix'), WINEARCH='win64', WINEDEBUG='-all',
                       WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
        return env

    def png_check(name, path):
        dimensions = None
        if path.is_file():
            data = path.read_bytes()
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                dimensions = list(struct.unpack('>II', data[16:24]))
        return check(name, {'real_png_640x360': dimensions == [640, 360]}, {'path': str(path.relative_to(ROOT)), 'dimensions': dimensions})

    def capture(name, command, extra=(), wine=False, preferences=None):
        env = environment(name, wine)
        if preferences:
            (isolated / (name + '-options.json')).write_text(json.dumps({'schema': 1, 'values': preferences}) + '\n')
        image = output / (name + '.png')
        image.unlink(missing_ok=True)
        env['AYAY_CAPTURE_PATH'] = windows_path(image) if wine else str(image)
        ok = run(name, command + ['--', '--open-dialogue', '--capture-dialogue', *extra], env)
        return png_check(name + '_image', image) and ok

    def replay(name, command, wine=False, movie=False, preferences=None):
        env = environment(name, wine)
        if preferences:
            (isolated / (name + '-options.json')).write_text(json.dumps({'schema': 1, 'values': preferences}) + '\n')
        paths = {key: output / (name + extension) for key, extension in
                 [('AYAY_CAPTURE_PATH', '.png'), ('AYAY_P03_RESULT_PATH', '.json'), ('AYAY_P03_AUDIO_PATH', '.wav')]}
        for key, path in paths.items():
            path.unlink(missing_ok=True)
            env[key] = windows_path(path) if wine else str(path)
        ok = run(name, command + ['--', '--open-dialogue', '--p03-replay'], env)
        report_path = paths['AYAY_P03_RESULT_PATH']
        report = json.loads(report_path.read_text()) if report_path.is_file() else {}
        audio = report.get('audio', {})
        events = audio.get('events', [])
        commits = [e for e in events if e.get('kind') == 'commit']
        states = {e.get('state') for e in commits}
        requests = [e for e in events if e.get('kind') == 'request']
        retry = [e for e in events if e.get('kind') == 'retry']
        death = [e for e in events if e.get('kind') == 'cue' and e.get('id') == 'death']
        checks = {
            'engine_report_passed': report.get('passed') is True,
            'actual_input_finished_once': report.get('actual_input') is True and report.get('finished') is True and report.get('exit_actions') == 1,
            'actual_deaths_10': report.get('actual_deaths') == 10 and len(death) == 10,
            'portrait_world_visible': report.get('motion_asset_ready') is True and report.get('world_visible') is True,
            'one_synchronized_player': audio.get('music_players') == 1 and audio.get('stem_starts') == 1,
            'actual_mixer_clock': audio.get('mixer_clock') is True and audio.get('clock', 0) > 18,
            'driver_matches_capture_scope': audio.get('audio_driver') == 'Dummy' if movie else audio.get('audio_driver') not in {None, 'Dummy'},
            'all_four_profiles_committed': states >= {'EXPLORE', 'SUSPICION', 'COMBAT', 'CLEAR'},
            'bar_requests_except_combat': all(e.get('state') == 'COMBAT' or e.get('scheduled_beat', -1) % 4 == 0 for e in requests),
            'commits_near_requested_beats': bool(commits) and all(abs(e['clock'] - e['beat'] * 60 / 144) < 0.12 for e in commits),
            'retry_no_stacking': len(retry) >= 10 and all(e.get('music_players') == 1 and e.get('stem_starts') == 1 for e in retry),
            'voices_drained': audio.get('active_voices') == 0 and audio.get('voice_limit') == 12,
            'capture_codes_ok': report.get('audio_capture_code') == 0 and report.get('capture_code') == 0,
        }
        check(name + '_acceptance', checks, {'driver': audio.get('audio_driver'), 'clock': audio.get('clock'), 'commits': commits, 'scope': 'MovieMaker fixed60 offline rendered mixer; not realtime driver or listening' if movie else 'realtime rendered playback; not listening', 'preferences': preferences or 'defaults'})
        png_check(name + '_image', paths['AYAY_CAPTURE_PATH'])
        waveform = {'listening': 'BLOCKED: audio input unsupported; waveform analysis is not listening'}
        try:
            with wave.open(str(paths['AYAY_P03_AUDIO_PATH']), 'rb') as wav:
                waveform.update(sample_rate=wav.getframerate(), channels=wav.getnchannels(), sample_width=wav.getsampwidth(), frames=wav.getnframes(), duration=wav.getnframes()/wav.getframerate())
                samples = array('h', wav.readframes(wav.getnframes()))
                if sys.byteorder != 'little':
                    samples.byteswap()
                waveform.update(peak=max(abs(v) for v in samples) / 32768,
                                rms=math.sqrt(sum(v * v for v in samples)/len(samples))/32768,
                                full_scale_samples=sum(abs(v) >= 32767 for v in samples))
            wave_checks = {'actual_stereo_pcm16': waveform['channels'] == 2 and waveform['sample_width'] == 2,
                           'real_nonempty_18s_capture': waveform['duration'] > 18 and waveform['rms'] > 0.001,
                           'no_full_scale_clipping': waveform['full_scale_samples'] == 0}
        except (OSError, wave.Error, ValueError) as error:
            waveform['error'] = str(error)
            wave_checks = {'valid_waveform': False}
        (output / (name + '_waveform.json')).write_text(json.dumps(waveform, indent=2) + '\n')
        check(name + '_waveform', wave_checks, waveform)
        return ok

    check('pinned_engine_hash', {'sha256_matches_lock': digest(GODOT) == LOCK['linux_binary_sha256']})
    if not args.exports_only:
        native = [GODOT, '--path', ROOT / 'game']
        capture('native_dialogue', native)
        capture('native_options', native, ['--capture-options'])
        capture('native_large_text', native, ['--capture-large-text'])
        capture('native_reduced_motion_vhs_off', native, preferences={'reduced_motion': True, 'vhs': False})
    if not args.exports_only and not args.snapshots_only:
        replay('native_replay', native)
        poses = output / 'weapon_poses'
        poses.mkdir(exist_ok=True)
        env = environment('weapon_poses')
        env['AYAY_WEAPON_CAPTURE_DIR'] = str(poses)
        run('native_weapon_poses', native + ['--script', 'res://tests/weapon_pose_capture.gd'], env)
        pose_path = poses / 'weapon_captures.json'
        report = json.loads(pose_path.read_text()) if pose_path.is_file() else {}
        rows = report.get('captures', [])
        expected = {(weapon, direction, phase) for direction in ['down', 'left', 'right', 'up']
                    for weapon, phases in [('melee', range(3)), ('ranged', [0])] for phase in phases}
        check('weapon_poses_acceptance', {'real_input_draw': report.get('real_input') is True and report.get('real_draw') is True,
              'all_16_unique_phases': len(rows) == 16 and {(r['weapon'], r['direction'], r['expected_phase']) for r in rows} == expected,
              'actual_phases_saved': bool(rows) and all(r.get('phase_verified') is True and r.get('saved') is True and (poses / r['file']).is_file() for r in rows)})
        if args.movie:
            for suffix, preferences in [('', None), ('_reduced_motion_vhs_off', {'reduced_motion': True, 'vhs': False})]:
                movie = build / ('dialogue_audio' + suffix + '.avi')
                movie.unlink(missing_ok=True)
                replay('native_movie_replay' + suffix, native + ['--write-movie', movie, '--fixed-fps', '60'], movie=True, preferences=preferences)
                if movie.is_file():
                    video = output / ('dialogue_audio_replay' + suffix + '.mp4')
                    run('encode_dialogue_movie' + suffix, ['ffmpeg', '-y', '-i', movie, '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', video])
                    run('dialogue_movie_contact_sheet' + suffix, ['ffmpeg', '-y', '-i', video, '-vf', 'fps=1,scale=320:180,tile=7x3', '-frames:v', '1', output / ('dialogue_replay_contact_sheet' + suffix + '.png')])
    if not args.no_exports and not args.snapshots_only:
        exports = []
        base = [GODOT, '--headless', '--path', ROOT / 'game']
        for preset, folder, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'), ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
            target = build / folder / filename
            target.parent.mkdir(exist_ok=True)
            target.unlink(missing_ok=True)
            ok = run('export_' + folder, base + ['--export-release', preset, target])
            item = {'platform': preset, 'path': str(target.relative_to(ROOT)), 'export_passed': ok}
            executable_ok = target.is_file() and target.read_bytes().startswith(magic)
            check(folder + '_executable', {'executable_magic': executable_ok})
            if executable_ok:
                item.update(sha256=digest(target), bytes=target.stat().st_size)
                if folder == 'linux':
                    target.chmod(0o755)
                    command = [target]
                    item['scope'] = 'actual native Linux runtime'
                else:
                    command = [ROOT / '.tools/wine/usr/bin/wine', target]
                    item['scope'] = 'actual Wine compatibility runtime on Linux; native Windows NOT_TESTED_UNAVAILABLE'
                env = environment(folder + '_smoke', folder == 'windows')
                run(folder + '_smoke', command + ['--headless', '--quit'], env)
                capture('export_' + folder + '_dialogue', command, wine=folder == 'windows')
                capture('export_' + folder + '_options', command, ['--capture-options'], wine=folder == 'windows')
                capture('export_' + folder + '_large_text', command, ['--capture-large-text'], wine=folder == 'windows')
                replay('export_' + folder + '_replay', command, wine=folder == 'windows')
            exports.append(item)
            (output / 'exports.json').write_text(json.dumps(exports, indent=2) + '\n')
    after = sources()
    check('export_sources_unchanged' if args.exports_only else 'native_sources_unchanged', {'source_snapshot_unchanged': before == after}, {'changed': [p for p in before.keys() | after.keys() if before.get(p) != after.get(p)]})
    inventory = [{'path': str(p.relative_to(ROOT)), 'sha256': digest(p), 'bytes': p.stat().st_size}
                 for folder in [output, build] for p in sorted(folder.rglob('*')) if p.is_file()
                 and p.name not in {'technical_artifacts.json'} and 'reviewer' not in str(p.relative_to(output) if p.is_relative_to(output) else p)]
    (output / 'technical_artifacts.json').write_text(json.dumps(inventory, indent=2) + '\n')
    return 0 if all(row['passed'] for row in results) else 1


if __name__ == '__main__':
    sys.exit(main())
