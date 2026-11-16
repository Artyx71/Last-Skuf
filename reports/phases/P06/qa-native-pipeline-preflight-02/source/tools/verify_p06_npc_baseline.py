#!/usr/bin/env python3
"""Native shared NPC category supplement; no new P08 art or phase acceptance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from verify_p06_cast import ROOT, GODOT, sha, sources, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = (ROOT / args.output).resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Use fresh evidence; never overwrite a previous attempt')
    output.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    if sha(GODOT) != lock['linux_binary_sha256']:
        parser.error('Pinned engine hash mismatch')
    before = sources()
    write(output / 'source_hashes.json', before)
    local = ROOT / '.tools/p06-npc-baseline' / hashlib.sha256(str(output).encode()).hexdigest()[:16]
    if local.exists():
        parser.error('Scratch project already exists; inspect preserved attempt')
    local.mkdir(parents=True)
    game = local / 'game'
    shutil.copytree(ROOT / 'game', game, ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    probe = ROOT / 'tools/probes/p06_npc_category_baseline.gd'
    shutil.copyfile(probe, game / 'tests/qa_npc_baseline_supplement.gd')
    env = os.environ.copy()
    for key, filename in [('XDG_CONFIG_HOME', 'config'), ('XDG_DATA_HOME', 'data'),
                          ('AYAY_OPTIONS_PATH', 'options.json'), ('AYAY_STORY_SAVE_PATH', 'story.json'),
                          ('AYAY_DIALOGUE_SAVE_PATH', 'dialogue.json'),
                          ('AYAY_P06_DIALOGUE_SAVE_PATH', 'cast.json'), ('AYAY_CHAPTER_SAVE_PATH', 'chapter.json')]:
        env[key] = str(local / filename)
    env['AYAY_NPC_BASELINE_OUTPUT'] = str(output)
    commands = []
    errors = re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL:|instances were leaked|resources still in use')
    for name, argv, timeout in [
        ('fresh_import', [GODOT, '--headless', '--path', game, '--editor', '--import'], 120),
        ('native_pairs', [GODOT, '--path', game, '--disable-vsync', '--max-fps', '60',
                          '--script', 'res://tests/qa_npc_baseline_supplement.gd'], 210),
    ]:
        started = time.monotonic()
        try:
            result = subprocess.run(list(map(str, argv)), cwd=ROOT, env=env,
                                    capture_output=True, text=True, timeout=timeout)
            code, text = result.returncode, result.stdout + result.stderr
        except subprocess.TimeoutExpired as error:
            code, text = 124, 'TIMEOUT\n' + str(error.stdout) + str(error.stderr)
        log = output / (name + '.log')
        log.write_text(text + '\nexit_code=' + str(code) + '\n')
        passed = code == 0 and not errors.search(text)
        commands.append({'name': name, 'argv': list(map(str, argv)), 'passed': bool(passed),
                         'exit_code': code, 'seconds': time.monotonic() - started, 'log_sha256': sha(log)})
        write(output / 'commands.json', commands)
        if not passed:
            break
    path = output / 'result.json'
    live = json.loads(path.read_text()) if path.is_file() else {}
    rows, cases, contacts = live.get('checks', []), live.get('cases', []), live.get('contacts', [])
    finishes = [x for x in contacts if x.get('finisher')]
    checks = {
        'two_clean_commands': len(commands) == 2 and all(x['passed'] for x in commands),
        'actual_native_Input': live.get('passed') is True and live.get('actual_input') is True
                              and live.get('renderer') in ['X11', 'Wayland'],
        'baseline_scope_only': live.get('scope') == 'P06_BASELINE_SHARED_NPC_CATEGORY_SUPPLEMENT_ONLY'
                              and live.get('deferred_C09_style_implemented') is False,
        'all_204_assertions': len(rows) == 204 and all(x.get('passed') is True for x in rows),
        'fourteen_cases': len(cases) == 14,
        'fourteen_atomic_contacts': len(finishes) == 14 and all(x.get('npc_frame') == 1 and x.get('player_frame') == 1 for x in finishes),
        'actual_42_PNG': len(list(output.glob('*.png'))) == 42 and len(live.get('captures', [])) == 42,
        'sources_unchanged': before == sources(),
    }
    summary = {'schema': 1, 'scope': 'P06_SHARED_NPC_BASELINE_NATIVE_ONLY', 'phase_approval': False,
               'passed': all(checks.values()), 'checks': checks, 'commands': commands,
               'source_unchanged': checks['sources_unchanged'], 'probe_sha256': sha(probe),
               'FPS': 'NOT_MEASURED', 'native_windows': 'NOT_TESTED', 'listening': 'NOT_CLAIMED'}
    write(output / 'validation.json', summary)
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0 if summary['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
