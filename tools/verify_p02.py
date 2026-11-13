#!/usr/bin/env python3
"""Native P02 acceptance: physics/tests, actual replay, separate exported builds."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
GODOT = ROOT / '.tools/godot' / f'Godot_v{LOCK["release"]}_linux.x86_64'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='reports/phases/P02')
    parser.add_argument('--build-output', default='build/P02')
    parser.add_argument('--references', action='store_true')
    parser.add_argument('--no-render', action='store_true')
    parser.add_argument('--no-exports', action='store_true')
    args = parser.parse_args()
    output = ROOT / args.output
    build = ROOT / args.build_output
    (output / 'logs').mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)
    assert hashlib.sha256(GODOT.read_bytes()).hexdigest() == LOCK['linux_binary_sha256']
    results = []

    def save_results():
        (output / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')

    def run(name, command, env=None, timeout=120):
        command = list(map(str, command))
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            text, code = result.stdout + result.stderr, result.returncode
        except subprocess.TimeoutExpired as error:
            text, code = str(error), 124
        ok = code == 0 and not any(token in text for token in ['SCRIPT ERROR:', 'ERROR:', 'FAIL:'])
        log = output / 'logs' / (name + '.log')
        log.write_text('$ ' + ' '.join(command) + '\n' + text + f'\nexit_code={code}\n')
        results.append({'name': name, 'passed': ok, 'exit_code': code, 'log': str(log.relative_to(ROOT))})
        save_results()
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        return ok

    base = [GODOT, '--headless', '--path', 'game']
    if args.references:
        run('references', [sys.executable, 'tools/validate_pack.py'])
    run('privacy', [sys.executable, 'tools/check_privacy.py'])
    run('import', base + ['--editor', '--quit'])
    for name in ['bootstrap', 'art_structure', 'movement', 'combat_art', 'combat', 'ai', 'restart', 'contact_timing']:
        run(name, base + ['--script', f'res://tests/{name}_test.gd'])
    if not all(row['passed'] for row in results):
        return 1
    scene = 'res://scenes/world/combat_lab.tscn'
    if not args.no_render:
        env = dict(os.environ, AYAY_CAPTURE_PATH=str(output / 'combat_lab.png'))
        run('combat_render', [GODOT, '--path', 'game', scene, '--', '--capture-combat'], env)
        metrics = output / 'combat_replay.json'
        metrics.unlink(missing_ok=True)
        env['AYAY_COMBAT_RESULT_PATH'] = str(metrics)
        env['AYAY_CAPTURE_PATH'] = str(output / 'combat_replay_end.png')
        replay_ok = run('combat_replay', [GODOT, '--path', 'game', '--write-movie', build / 'combat.avi',
                                          '--fixed-fps', '60', scene, '--', '--combat-replay'], env, 240)
        if replay_ok and metrics.is_file():
            report = json.loads(metrics.read_text())
            checks = {
                'replay_report_passed': report.get('passed') is True,
                'escape_cleared': report.get('escape', {}).get('cleared') is True,
                'escape_zero_kills': report.get('escape', {}).get('kills') == 0,
                'escape_real_input': report.get('escape', {}).get('real_input') is True,
                'escape_active_enemies': report.get('escape', {}).get('active_enemies', 0) >= 3,
                'escape_detected': report.get('escape', {}).get('detections', 0) >= 1,
                'escape_weak_kit': report.get('escape', {}).get('kit') == 'escape',
                'escape_at_exit': report.get('escape', {}).get('snapshot', {}).get('player', {}).get('position', [0])[0] >= 584,
                'escape_no_gun': report.get('escape', {}).get('snapshot', {}).get('shots_fired') == 0,
                'escape_state': report.get('escape', {}).get('snapshot', {}).get('state') == 'escaped',
                'restart_real_ai_death': report.get('restart', {}).get('actual_ai_death') is True,
                'restart_alive': report.get('restart', {}).get('retry_alive') is True,
                'restart_exact_state': report.get('restart', {}).get('snapshots_equal') is True,
                'restart_below_second': 0 < report.get('restart', {}).get('max_latency_ms', 0) < 1000,
                'training_separate_kit': report.get('training', {}).get('kit') == 'training',
                'training_melee_hits': report.get('training', {}).get('melee_hits', 0) >= 1,
                'training_ranged_hits': report.get('training', {}).get('ranged_hits', 0) >= 1,
            }
            (output / 'replay_acceptance.json').write_text(json.dumps(checks, indent=2) + '\n')
            results.append({'name': 'replay_acceptance', 'passed': all(checks.values()), 'exit_code': 0 if all(checks.values()) else 1})
        else:
            results.append({'name': 'replay_acceptance', 'passed': False, 'exit_code': 1})
        save_results()
        if (build / 'combat.avi').is_file():
            run('encode_replay', ['ffmpeg', '-y', '-i', build / 'combat.avi', '-an', '-c:v', 'libx264', '-crf', '18',
                                  '-pix_fmt', 'yuv420p', output / 'combat_replay.mp4'])
            run('replay_contact_sheet', ['ffmpeg', '-y', '-i', output / 'combat_replay.mp4', '-vf',
                                         'fps=2,scale=320:180,tile=7x4', '-frames:v', '1', output / 'combat_contact_sheet.png'])
    exports = []
    if not args.no_exports:
        for preset, folder, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'),
                                                 ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
            target = build / folder / filename
            target.parent.mkdir(exist_ok=True)
            ok = run('export_' + folder, base + ['--export-release', preset, target])
            item = {'platform': preset, 'export_passed': ok, 'path': str(target.relative_to(ROOT)),
                    'runtime': 'NOT_TESTED: native Windows unavailable' if preset == 'Windows' else 'not tested'}
            if ok and target.is_file():
                assert target.read_bytes().startswith(magic)
                item['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
                if preset == 'Linux':
                    target.chmod(0o755)
                    item['runtime'] = 'PASS' if run('linux_smoke', [target, '--headless', '--quit']) else 'FAIL'
                    if not args.no_render:
                        env = dict(os.environ, AYAY_CAPTURE_PATH=str(output / 'export_linux_combat.png'))
                        item['combat_render_passed'] = run('linux_combat_render', [target, '--', '--open-combat', '--capture-combat'], env)
                        env['AYAY_CAPTURE_PATH'] = str(output / 'export_linux_replay_end.png')
                        metrics = output / 'export_linux_replay.json'
                        metrics.unlink(missing_ok=True)
                        env['AYAY_COMBAT_RESULT_PATH'] = str(metrics)
                        item['combat_replay_passed'] = run('linux_export_replay', [target, '--', '--open-combat', '--combat-replay'], env)
                        item['combat_replay_passed'] = item['combat_replay_passed'] and metrics.is_file() and json.loads(metrics.read_text()).get('passed') is True
                        results.append({'name': 'linux_export_replay_report', 'passed': item['combat_replay_passed']})
                else:
                    wine = ROOT / '.tools/wine/usr/bin/wine'
                    if wine.is_file():
                        env = dict(os.environ, WINEPREFIX=str(ROOT / '.tools/wine-prefix'), WINEARCH='win64',
                                   WINEDEBUG='-all', WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
                        item['wine_smoke_passed'] = run('windows_wine_smoke', [wine, target, '--headless', '--quit'], env)
                        item['compatibility_scope'] = 'Wine 11.17 on Linux; native Windows remains untested'
                        if not args.no_render:
                            capture = output / 'export_windows_wine_combat.png'
                            env['AYAY_CAPTURE_PATH'] = 'Z:' + str(capture).replace('/', '\\')
                            item['wine_combat_render_passed'] = run('windows_wine_render', [wine, target, '--', '--open-combat', '--capture-combat'], env)
                            metrics = output / 'export_windows_replay.json'
                            metrics.unlink(missing_ok=True)
                            env['AYAY_CAPTURE_PATH'] = 'Z:' + str(output / 'export_windows_replay_end.png').replace('/', '\\')
                            env['AYAY_COMBAT_RESULT_PATH'] = 'Z:' + str(metrics).replace('/', '\\')
                            item['wine_combat_replay_passed'] = run('windows_wine_replay', [wine, target, '--', '--open-combat', '--combat-replay'], env)
                            item['wine_combat_replay_passed'] = item['wine_combat_replay_passed'] and metrics.is_file() and json.loads(metrics.read_text()).get('passed') is True
                            results.append({'name': 'windows_wine_replay_report', 'passed': item['wine_combat_replay_passed']})
            exports.append(item)
        (output / 'exports.json').write_text(json.dumps(exports, indent=2) + '\n')
    save_results()
    return not all(row['passed'] for row in results)


if __name__ == '__main__':
    sys.exit(main())
