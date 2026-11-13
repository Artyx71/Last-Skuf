#!/usr/bin/env python3
"""Export pinned native P00 builds and record actual local runtime checks."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / 'reports/phases/P00'
    logs = output / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    binary = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == lock['linux_binary_sha256']
    results = []
    for preset, directory, filename, magic in [('Linux', 'linux', 'last-skuf.x86_64', b'\x7fELF'),
                                                ('Windows', 'windows', 'last-skuf.exe', b'MZ')]:
        target = ROOT / 'build' / directory / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [str(binary), '--headless', '--path', 'game', '--export-release', preset]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=120)
        text = result.stdout + result.stderr
        ok = result.returncode == 0 and target.exists() and target.read_bytes().startswith(magic) and 'ERROR:' not in text
        (logs / f'export_{directory}.log').write_text('$ ' + ' '.join(command) + '\n' + text + f'\nexit_code={result.returncode}\n')
        results.append({'platform': preset, 'export_passed': ok, 'exit_code': result.returncode,
                        'path': str(target.relative_to(ROOT)), 'runtime': 'not tested'})
        if not ok:
            continue
        results[-1]['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        if preset == 'Linux':
            target.chmod(0o755)
            command = [str(target), '--headless', '--quit']
            smoke = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
            text = smoke.stdout + smoke.stderr
            (logs / 'export_linux_smoke.log').write_text(text + f'\nexit_code={smoke.returncode}\n')
            runtime_ok = smoke.returncode == 0 and 'ERROR:' not in text
            results[-1]['runtime'] = 'PASS headless smoke' if runtime_ok else 'FAIL'
            env = dict(os.environ, AYAY_CAPTURE_PATH=str(output / 'export_linux.png'))
            capture = subprocess.run([str(target), '--', '--capture-bootstrap'], cwd=ROOT, env=env,
                                     capture_output=True, text=True, timeout=30)
            text = capture.stdout + capture.stderr
            (logs / 'export_linux_render.log').write_text(text + f'\nexit_code={capture.returncode}\n')
            results[-1]['render_passed'] = capture.returncode == 0 and 'ERROR:' not in text and (output / 'export_linux.png').is_file()
        else:
            results[-1]['runtime'] = 'BLOCKED: Windows host / Wine unavailable'
    (output / 'exports.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps(results, indent=2))
    return not all(r['export_passed'] and r.get('runtime') != 'FAIL' and r.get('render_passed', True) for r in results)


if __name__ == '__main__':
    sys.exit(main())
