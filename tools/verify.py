#!/usr/bin/env python3
"""Reproducible P00 validation with per-command exit codes and actual logs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--references', action='store_true', help='Local private manifest check (not in public CI)')
    parser.add_argument('--capture', action='store_true', help='Real desktop renderer required')
    parser.add_argument('--output', default='reports/phases/P00')
    args = parser.parse_args()
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    (output / 'logs').mkdir(exist_ok=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    binary = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    if not binary.is_file():
        raise SystemExit('Run python3 tools/install_deps.py first')
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == lock['linux_binary_sha256']
    base = [str(binary), '--headless', '--path', 'game']
    commands = [('privacy', [sys.executable, 'tools/check_privacy.py']),
                ('version', [str(binary), '--version']),
                ('import', base + ['--editor', '--quit']),
                ('smoke', base + ['--quit']),
                ('integration', base + ['--script', 'res://tests/bootstrap_test.gd'])]
    if args.references:
        commands.insert(0, ('references', [sys.executable, 'tools/validate_pack.py']))
    if (ROOT / 'game/assets/art/yakuza/world_sheet.png').is_file():
        commands.extend([
            ('art_structure', base + ['--script', 'res://tests/art_structure_test.gd']),
            ('movement', base + ['--script', 'res://tests/movement_test.gd']),
        ])
    if (ROOT / 'game/scenes/world/combat_lab.tscn').is_file():
        commands.extend((name, base + ['--script', f'res://tests/{name}_test.gd'])
                        for name in ['combat_art', 'combat', 'ai', 'restart', 'contact_timing'])
    env = dict(os.environ)
    env['AYAY_CAPTURE_PATH'] = str(output / 'bootstrap.png')
    if args.capture:
        commands.append(('render', [str(binary), '--path', 'game', '--', '--capture-bootstrap']))
    results = []
    for name, command in commands:
        try:
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, timeout=90)
            text = result.stdout + result.stderr
            code = result.returncode
        except subprocess.TimeoutExpired as error:
            text, code = str(error), 124
        # Godot may exit zero after a parse error: logs are part of the gate.
        ok = code == 0 and not any(token in text for token in ['SCRIPT ERROR:', 'ERROR:', 'FAIL:'])
        if name == 'version':
            ok = ok and text.startswith(lock['godot_version'] + '.stable.')
        log = output / 'logs' / (name + '.log')
        log.write_text('$ ' + ' '.join(command) + '\n' + text + f'\nexit_code={code}\n')
        results.append({'name': name, 'exit_code': code, 'passed': ok, 'log': str(log.relative_to(ROOT))})
        print(name, 'PASS' if ok else 'FAIL', 'exit', code)
    (output / 'validation.json').write_text(json.dumps(results, indent=2) + '\n')
    return not all(r['passed'] for r in results)


if __name__ == '__main__':
    sys.exit(main())
