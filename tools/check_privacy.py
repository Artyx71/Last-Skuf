#!/usr/bin/env python3
"""Check git index and reachable history for raw references, bundles and secrets."""
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True).stdout


def main():
    errors = []
    probes = ['assets/references/characters/yakuza_ref01.png', 'bundle.zip', '.env',
              '.env.local', '.secrets/token', '.tools/test', 'reports/phases/P01/private/test.png']
    for path in probes:
        result = subprocess.run(['git', 'check-ignore', '--no-index', '-q', path], cwd=ROOT)
        if result.returncode != 0:
            errors.append('Not ignored: ' + path)
    index = git('ls-files', '-z').decode().split('\0')
    history = git('rev-list', '--objects', '--all').decode().splitlines()
    paths = index + [line.partition(' ')[2] for line in history]
    for path in paths:
        p = pathlib.PurePosixPath(path)
        if ('references' in p.parts or p.suffix.lower() in {'.zip', '.pem', '.key'}
                or p.name == '.env' or p.name.startswith('.env.') or '.secrets' in p.parts):
            errors.append('Sensitive tracked path: ' + path)
    # Catch reference photos renamed before staging; compare Git blob hashes too.
    manifest = ROOT / 'assets/references/manifest.json'
    hashes = set()
    reference_sha256 = set()
    if manifest.exists():
        for item in json.loads(manifest.read_text()):
            reference_sha256.add(item['sha256'])
            path = ROOT / item['path']
            if path.is_file():
                hashes.add(hashlib.sha1(b'blob ' + str(path.stat().st_size).encode() + b'\0' + path.read_bytes()).hexdigest())
                reference_sha256.add(hashlib.sha256(path.read_bytes()).hexdigest())
    blobs = {line.split()[1] for line in git('ls-files', '--stage').decode().splitlines()}
    blobs.update(line.partition(' ')[0] for line in history)
    if hashes & blobs:
        errors.append('Raw reference content exists in Git')
    # Manifest hashes also cover the original private photo if the local file was
    # subsequently replaced. Stream all reachable/index objects, including renamed blobs.
    process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    try:
        for oid in sorted(blobs):
            process.stdin.write((oid + '\n').encode()); process.stdin.flush()
            header = process.stdout.readline().decode().split()
            if len(header) != 3:
                errors.append('Unable to inspect Git object ' + oid); break
            size = int(header[2]); digest = hashlib.sha256()
            remaining = size
            while remaining:
                chunk = process.stdout.read(min(remaining, 1024 * 1024))
                if not chunk: raise RuntimeError('Truncated Git object stream')
                digest.update(chunk); remaining -= len(chunk)
            process.stdout.read(1)
            if header[1] == 'blob' and digest.hexdigest() in reference_sha256:
                errors.append('Manifest/private reference content in Git object ' + oid)
    finally:
        process.stdin.close(); process.stdout.close(); process.wait()
    print(f'privacy probes={len(probes)} tracked={len([p for p in index if p])} errors={len(errors)}')
    for error in errors:
        print('FAIL:', error)
    return bool(errors)


if __name__ == '__main__':
    sys.exit(main())
