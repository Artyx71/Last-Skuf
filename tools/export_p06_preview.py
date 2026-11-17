#!/usr/bin/env python3
"""Local owner DEV preview exports; not P06 acceptance, publication or release."""
import argparse
import json
import os
import subprocess
import time
from pathlib import Path

from verify_p06_cast import ROOT, GODOT, ERRORS, sha, sources, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    parser.add_argument('--build-output', required=True)
    args = parser.parse_args()
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    if not GODOT.is_file() or sha(GODOT) != lock['linux_binary_sha256']:
        parser.error('Pinned Godot executable is missing or changed')
    output = (ROOT / args.output).resolve()
    build = (ROOT / args.build_output).resolve()
    for path in [output, build]:
        if path.exists() and any(path.iterdir()):
            parser.error('Preserve previous artifacts; use a fresh directory')
        path.mkdir(parents=True, exist_ok=True)
    local = ROOT / '.tools/owner-preview' / output.name
    local.mkdir(parents=True, exist_ok=True)
    commands = []
    before = sources()
    write(output / 'source_hashes.json', before)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()

    def environment(name, wine=False):
        folder = local / name
        folder.mkdir(exist_ok=True)
        env = os.environ.copy()
        for key, part in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data')]:
            env[key] = str(folder / part)
        convert = (lambda p: 'Z:' + str(p).replace('/', '\\')) if wine else str
        for key, filename in [('AYAY_OPTIONS_PATH', 'options.json'),
                              ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                              ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json'),
                              ('AYAY_STORY_SAVE_PATH', 'story.json'),
                              ('AYAY_P06_DIALOGUE_SAVE_PATH', 'cast.json')]:
            env[key] = convert(folder / filename)
        if wine:
            env.update(WINEPREFIX=str(local / 'wine-prefix'), WINEARCH='win64',
                       WINEDEBUG='-all', WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
        return env

    def run(name, argv, env, timeout=120):
        start = time.monotonic()
        try:
            result = subprocess.run(list(map(str, argv)), cwd=ROOT, env=env,
                                    capture_output=True, text=True, timeout=timeout)
            code, text = result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired as error:
            code, text = 124, 'TIMEOUT\n' + str(error.stdout) + str(error.stderr)
        log = output / (name + '.log')
        log.write_text(text + '\nexit_code=' + str(code) + '\n')
        ok = code == 0 and not ERRORS.search(text)
        commands.append({'name': name, 'argv': list(map(str, argv)), 'exit_code': code,
                         'passed': bool(ok), 'seconds': round(time.monotonic() - start, 3),
                         'log_sha256': sha(log)})
        write(output / 'commands.json', commands)
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        return ok

    exports = []
    for preset, folder, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'),
                                            ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
        target = build / folder / filename
        target.parent.mkdir(exist_ok=True)
        ok = run('export_' + folder,
                 [GODOT, '--headless', '--path', ROOT / 'game', '--export-release', preset, target],
                 environment('export_' + folder))
        ok = bool(ok and target.is_file() and target.read_bytes().startswith(magic))
        row = {'platform': preset, 'export_passed': ok, 'path': str(target.relative_to(ROOT)),
               'native_windows': 'NOT_TESTED' if folder == 'windows' else None}
        if ok:
            row.update(sha256=sha(target), bytes=target.stat().st_size)
            scope = output / (folder + '_smoke')
            scope.mkdir()
            env = environment(folder + '_smoke', wine=folder == 'windows')
            env['AYAY_OWNER_PREVIEW_SMOKE_OUTPUT'] = ('Z:' + str(scope).replace('/', '\\')) if folder == 'windows' else str(scope)
            if folder == 'linux':
                target.chmod(0o755)
                argv = [target, '--disable-vsync', '--max-fps', '60']
            else:
                argv = [ROOT / '.tools/wine/usr/bin/wine', target, '--headless', '--fixed-fps', '60']
            ok = run(folder + '_smoke', argv + ['--', '--p06-owner-preview-smoke'], env, 90)
            data = json.loads((scope / 'result.json').read_text()) if (scope / 'result.json').is_file() else {}
            row['runtime_smoke_passed'] = bool(ok and data.get('passed'))
            check_results = {item['name']: item.get('passed') is True for item in data.get('checks', [])}
            fixture_checks = {
                'gabar_training': ['Gabar_actual_complete_body_loaded', 'Gabar_ability_Input_starts'],
                'olezhka_training': ['Oleg_selection_actual_complete_body', 'Oleg_ability_Input_starts'],
                'timka_present': ['present_Timka_selects_own_context_and_body', 'present_disengage_starts_from_Input',
                                  'present_disengage_moves_without_prime_damage'],
                'timka_prime': ['prime_Timka_selects_separate_body_contract', 'prime_cannot_grab_without_vulnerable_target'],
                'ryzhik_training': ['Ryzhik_selects_complete_own_roll_body', 'Ryzhik_roll_starts_from_Input',
                                    'Ryzhik_roll_moves_with_live_collision'],
                'tega_training': ['Tega_selects_complete_environment_body',
                                  'Tega_kick_starts_with_registered_object_Input',
                                  'Tega_moves_real_bench_with_restored_masks'],
                'pasha_training': ['Pasha_selects_complete_moving_shot_body',
                                   'Pasha_moving_shot_starts_from_Input',
                                   'Pasha_moves_and_spends_one_round_with_HUD'],
            }
            row['verified_combat_fixtures'] = [key for key, required in fixture_checks.items()
                                               if data.get('passed') and all(check_results.get(name, False) for name in required)]
            row['runtime_scope'] = 'Linux renderer + Input menu/available fixtures' if folder == 'linux' else 'Actual Windows PE under Wine headless + Input menu/available fixtures'
            row['captures'] = len(list(scope.glob('*.png')))
        exports.append(row)
        write(output / 'exports.json', exports)
        if not ok or not row.get('runtime_smoke_passed'):
            break
    unchanged = before == sources()
    passed = len(exports) == 2 and unchanged and all(e['export_passed'] and e.get('runtime_smoke_passed') for e in exports)
    available_fixtures = sorted(set.intersection(*(set(e.get('verified_combat_fixtures', [])) for e in exports))) if passed else []
    report = {'schema': 1, 'scope': 'LOCAL_OWNER_P06_DEV_PREVIEW_ONLY', 'passed': passed,
              'source_head': head, 'source_unchanged': unchanged, 'phase_approval': False,
              'release_approval': False, 'last_full_PASS': 'P05',
              'available_combat_heroes': sorted({key.split('_', 1)[0] for key in available_fixtures}),
              'available_combat_fixtures': available_fixtures, 'portrait_cast_count': 9,
              'other_combat_heroes': 'Not an approval of campaign combat; available fixtures are measured below',
              'native_windows': 'NOT_TESTED', 'audio_listening': 'NOT_CLAIMED',
              'FPS_acceptance': 'NOT_CLAIMED', 'exports': exports, 'commands': commands}
    write(output / 'preview.json', report)
    print(json.dumps({'passed': passed, 'source_unchanged': unchanged, 'phase_approval': False}))
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
