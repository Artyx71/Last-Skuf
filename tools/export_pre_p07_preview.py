#!/usr/bin/env python3
"""Build a local PRE-P07 preview from an isolated source copy using the proven exporter."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from p07_room_pilot import ROOT, digest, inventory, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--build-output', type=Path, required=True)
    args = parser.parse_args()
    out, build = args.output.resolve(), args.build_output.resolve()
    if out.exists() or build.exists():
        raise SystemExit('Preserve previous previews; use fresh output/build directories')
    before = inventory()
    out.mkdir(parents=True)
    write(out / 'source_before.json', before)
    project = out / 'isolated_project'
    for folder in ['game', 'tools']:
        shutil.copytree(ROOT / folder, project / folder,
                        ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    (project / '.tools').symlink_to((ROOT / '.tools').resolve(), target_is_directory=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = project / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    runs = []
    export_report = 'pre-p07-export-' + hashlib.sha256(str(out).encode()).hexdigest()[:16]

    def run(name, argv, env, timeout=240):
        process = subprocess.run(list(map(str, argv)), cwd=project, env=env,
                                 capture_output=True, text=True, timeout=timeout)
        text = process.stdout + process.stderr
        (out / f'{name}.log').write_text(text + f'\nexit_code={process.returncode}\n')
        ok = process.returncode == 0 and not any(x in text for x in ['SCRIPT ERROR:', 'Parse Error:'])
        runs.append({'name': name, 'argv': list(map(str, argv)), 'exit_code': process.returncode, 'passed': ok})
        write(out / 'runs.json', runs)
        if not ok:
            raise RuntimeError(f'{name} failed; inspect preserved log')

    env = dict(os.environ)
    home = out / 'isolated_saves/import'
    env.update(XDG_CONFIG_HOME=str(home / 'config'), XDG_DATA_HOME=str(home / 'data'),
               XDG_CACHE_HOME=str(home / 'cache'))
    run('import', [engine, '--headless', '--editor', '--path', project / 'game', '--quit'], env)
    # Existing exporter owns the same export/runtime checks used for P06 DEV.
    # Its old P06/P05 labels are historical; the outer manifest is the PRE-P07 scope.
    run('exports-and-character-input', [sys.executable, project / 'tools/export_p06_preview.py',
        '--output', export_report, '--build-output', 'build'], env)
    raw = json.loads((project / export_report / 'preview.json').read_text())
    assert raw['passed'] and raw['source_unchanged'] and len(raw['exports']) == 2
    checks = []
    for platform, folder, filename in [('Linux', 'linux', 'last-skuf.x86_64'),
                                       ('Windows', 'windows', 'last-skuf.exe')]:
        target = project / 'build' / folder / filename
        row = next(x for x in raw['exports'] if x['platform'] == platform)
        assert row['sha256'] == digest(target) and row['runtime_smoke_passed'] is True
        probe = project / export_report / (folder + '_smoke/result.json')
        actual = json.loads(probe.read_text())
        expected_checks = 72 if folder == 'windows' else 81
        assert actual['passed'] is True and len(actual['checks']) == expected_checks
        assert all(check['passed'] is True for check in actual['checks'])
        home = out / 'isolated_saves' / folder
        env = dict(os.environ)
        env.update(XDG_CONFIG_HOME=str(home / 'config'), XDG_DATA_HOME=str(home / 'data'),
                   XDG_CACHE_HOME=str(home / 'cache'))
        convert = (lambda p: 'Z:' + str(p).replace('/', '\\')) if folder == 'windows' else str
        for variable, name in [('AYAY_OPTIONS_PATH', 'options.json'),
                               ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                               ('AYAY_P06_DIALOGUE_SAVE_PATH', 'cast.json'),
                               ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json'),
                               ('AYAY_STORY_SAVE_PATH', 'story.json')]:
            home.mkdir(parents=True, exist_ok=True)
            env[variable] = convert(home / name)
        if folder == 'windows':
            env.update(WINEPREFIX=str(project / '.tools/owner-preview' / export_report / 'wine-prefix'),
                       WINEARCH='win64', WINEDEBUG='-all',
                       WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
            command = [project / '.tools/wine/usr/bin/wine', target]
        else:
            command = [target]
        run(folder + '-chapter-smoke', command + ['--headless', '--', '--open-mission', '--p04-smoke'], env, 45)
        assert 'P04_SMOKE passed=true' in (out / f'{folder}-chapter-smoke.log').read_text()
        checks.append({'platform': platform, 'sha256': row['sha256'], 'bytes': target.stat().st_size,
                       'runtime_checks': expected_checks, 'common_input_checks': 72,
                       'capture_checks': expected_checks - 72, 'chapter_smoke': True,
                       'runtime': 'Linux native' if folder == 'linux' else 'Windows PE under Wine',
                       'native_windows': 'NOT_TESTED' if folder == 'windows' else None})
    assert before == inventory()
    # Create the owner-facing folder only after both actual binaries pass.
    build.mkdir(parents=True)
    for folder, filename in [('linux', 'last-skuf.x86_64'), ('windows', 'last-skuf.exe')]:
        (build / folder).mkdir()
        shutil.copy2(project / 'build' / folder / filename, build / folder / filename)
    launcher = (ROOT / 'tools/preview_launchers/PLAY_LINUX.sh').read_text()
    (build / 'PLAY_LINUX.sh').write_text(launcher)
    (build / 'PLAY_LINUX.sh').chmod(0o755)
    shutil.copy2(ROOT / 'tools/preview_launchers/PLAY_WINDOWS.cmd', build / 'PLAY_WINDOWS.cmd')
    (build / 'README_RU.txt').write_text('PRE-P07 local DEV preview. P06 accepted; P07 campaign production not accepted.\n'
        'Main menu: Enter CH01 with room navigation, F5 character combat, F6 cast.\n'
        'Only CH01 is a playable story chapter; CH11 specification is not a playable level.\n'
        'Separate profile; earlier DEV09 and user saves preserved. Windows runtime checked under Wine only.\n')
    result = {'schema': 1, 'scope': 'LOCAL_PRE_P07_DEV_PREVIEW_ONLY', 'passed': True,
              'source_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
              'last_full_PASS': 'P06', 'source_game_and_tools_unchanged': before == inventory(),
              'build': str(build), 'exports': checks, 'phase_or_release_approval': False,
              'full_H02_Readiness_or_P07_approval': False, 'new_audio_listening_FPS_claim': False,
              'legacy_export_report': str(project / export_report / 'preview.json'),
              'legacy_helper_label_note': 'Raw helper P06/P05 scope labels are not phase decisions'}
    write(out / 'validation.json', result)
    write(build / 'build_manifest.json', result)
    write(out / 'source_after.json', inventory())
    print(json.dumps(result), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
