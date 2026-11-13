#!/usr/bin/env python3
"""Inventory actual phase outputs. Review files excluded to avoid circular hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=[f'P{i:02d}' for i in range(9)])
    args = parser.parse_args()
    directory = ROOT / 'reports/phases' / args.phase
    files = [p for p in directory.rglob('*') if p.is_file()
             and p.name not in {'artifacts.json', 'review.md', 'decision.json'}
             and 'private' not in p.parts and 'reviewer' not in p.parts]
    files += [p for p in (ROOT / 'build').rglob('*') if p.is_file()]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    inventory = {'phase': args.phase, 'implementation_commit': commit,
                 'evidence': [{'path': str(p.relative_to(ROOT)), 'bytes': p.stat().st_size,
                               'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}
                              for p in sorted(files)]}
    (directory / 'artifacts.json').write_text(json.dumps(inventory, indent=2) + '\n')
    print(f'Inventoried {len(files)} actual files at {commit}')


if __name__ == '__main__':
    main()
