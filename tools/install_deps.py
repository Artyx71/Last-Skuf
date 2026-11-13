#!/usr/bin/env python3
"""User-local locked Godot install. No sudo, paid services, or PATH changes."""
import argparse
import hashlib
import json
import pathlib
import os
import shutil
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
CACHE = ROOT / '.tools/godot'


def download(name):
    spec = LOCK['assets'][name]
    target = CACHE / name
    if not target.exists():
        partial = target.with_suffix('.partial')
        external_cache = os.environ.get('AYAY_ARCHIVE_CACHE')
        source = pathlib.Path(external_cache) / name if external_cache else None
        if source and source.is_file() and source.resolve() != target.resolve():
            with source.open('rb') as stream:
                valid_cache = hashlib.file_digest(stream, 'sha512').hexdigest() == spec['sha512']
            if not valid_cache:
                raise SystemExit('External cache checksum mismatch: ' + name)
            shutil.copyfile(source, partial)
            print('Verified local archive cache:', name)
        else:
            urllib.request.urlretrieve(spec['url'], partial)
        partial.rename(target)
    digest = hashlib.file_digest(target.open('rb'), 'sha512').hexdigest()
    if digest != spec['sha512']:
        raise SystemExit('Checksum mismatch: ' + name)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--templates', action='store_true')
    args = parser.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    release = LOCK['release']
    filename = f'Godot_v{release}_linux.x86_64.zip'
    binary_name = f'Godot_v{release}_linux.x86_64'
    binary = CACHE / binary_name
    with zipfile.ZipFile(download(filename)) as archive:
        if not binary.exists() or hashlib.sha256(binary.read_bytes()).hexdigest() != LOCK['linux_binary_sha256']:
            temporary = binary.with_suffix('.install')
            temporary.write_bytes(archive.read(binary_name))
            temporary.chmod(0o755)
            temporary.replace(binary)
    binary.chmod(0o755)
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == LOCK['linux_binary_sha256']
    print(binary)
    if args.templates:
        directory = CACHE / 'templates'
        directory.mkdir(exist_ok=True)
        with zipfile.ZipFile(download(f'Godot_v{release}_export_templates.tpz')) as archive:
            for name in ['linux_release.x86_64', 'windows_release_x86_64.exe']:
                (directory / name).write_bytes(archive.read('templates/' + name))
        print(directory)


if __name__ == '__main__':
    main()
