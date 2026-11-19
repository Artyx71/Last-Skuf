#!/usr/bin/env python3
"""Fresh isolated Godot import/native art surface; never a chapter playthrough."""
import argparse
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
from p07_room_pilot import ROOT, digest, inventory, write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve()
    if out.exists():
        raise SystemExit('Fresh evidence directory required')
    out.mkdir(parents=True)
    before = inventory()
    for source in sorted((ROOT / 'assets/source_art/the_titan/bench_press_v1').iterdir()):
        if source.is_file():
            before[str(source.relative_to(ROOT))] = digest(source)
    write(out / 'source-before.json', before)
    project = out / 'isolated_project/game'
    shutil.copytree(ROOT / 'game', project, ignore=shutil.ignore_patterns('.godot', '__pycache__'))
    assert all(digest(project / Path(k).relative_to('game')) == v for k, v in before.items() if k.startswith('game/'))
    lock = json.loads((ROOT / 'tools/toolchain.lock.json').read_text())
    engine = ROOT / '.tools/godot' / f'Godot_v{lock["release"]}_linux.x86_64'
    assert digest(engine) == lock['linux_binary_sha256']
    isolate = out / 'isolated_saves'
    env = dict(os.environ, XDG_DATA_HOME=str(isolate / 'data'), XDG_CONFIG_HOME=str(isolate / 'config'),
               XDG_CACHE_HOME=str(isolate / 'cache'), AYAY_STORY_SAVE_PATH=str(isolate / 'story.json'),
               AYAY_TITAN_PROP_CAPTURE=str(out / 'native.png'), GODOT_SILENCE_ROOT_WARNING='1')
    stages = [('import', ['--headless', '--editor', '--quit'], 60),
              ('native', ['--disable-vsync', '--max-fps', '60', 'res://scenes/qa/titan_prop_preview.tscn'], 30)]
    runs = []
    for name, flags, timeout in stages:
        argv = [str(engine), '--path', str(project), *flags]
        try:
            p = subprocess.run(argv, cwd=ROOT, env=env, capture_output=True, text=True, timeout=timeout)
            code, log = p.returncode, p.stdout + p.stderr
        except subprocess.TimeoutExpired as error:
            decoded = lambda value: value.decode(errors='replace') if isinstance(value, bytes) else value or ''
            code, log = None, decoded(error.stdout) + decoded(error.stderr) + '\nTIMEOUT\n'
        (out / f'{name}.log').write_text(log)
        good = code == 0 and not any(s in log for s in ['SCRIPT ERROR:', 'Parse Error:', 'ERROR:'])
        runs.append({'stage':name, 'argv':argv, 'timeout':timeout, 'exit_code':code, 'passed':good})
        write(out / 'runs.json', runs)
        if not good:
            break
    after = {key:digest(ROOT / key) for key in before}
    write(out / 'source-after.json', after)
    image = out / 'native.png'
    size = None
    if image.exists():
        blob = image.read_bytes()
        assert blob[:8] == b'\x89PNG\r\n\x1a\n'
        size = list(struct.unpack('>II', blob[16:24]))
    passed = len(runs) == 2 and all(r['passed'] for r in runs) and before == after and size == [640, 360]
    result = {'scope':'CH02_PROP_ART_SURFACE_ONLY', 'passed':passed, 'runs':runs,
              'capture_size':size, 'capture_sha256':digest(image) if image.exists() else None,
              'engine_sha256':digest(engine), 'source_unchanged':before == after,
              'artistic_acceptance_or_chapter_playthrough':False}
    write(out / 'validation.json', result)
    print(json.dumps(result), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
