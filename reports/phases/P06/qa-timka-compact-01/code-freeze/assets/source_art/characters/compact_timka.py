#!/usr/bin/env python3
"""Owner-approved whole-cell compaction. Source candidates only; no art approval.

Discarded columns remain in immutable original masters/manifests. WORLD keeps
its original PNG bytes. Other sheets only repack complete decoded RGBA cells.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image
from pack_actor_sheet import DIRECTIONS, MAPS

ROOT = Path(__file__).resolve().parents[3]
PROFILE = 'timka_supported_v1'
SOURCE_COLUMNS = {'world': list(range(8)), 'action': list(range(7)),
                  'finisher': [0, 1, 2, 5, 6, 7]}
COMPACT_MAPS = {
    'world': MAPS['world'],
    'action': {k: v for k, v in MAPS['action'].items() if k != 'fire'},
    'finisher': {'finish_unarmed': [0, 1, 4], 'finish_blunt': [0, 2, 4],
                 'finish_environmental': [0, 3, 4], 'special': [0, 5, 4]},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(manifest, image):
    require(isinstance(manifest, dict), 'Metadata must be an object')
    kind = manifest.get('kind')
    require(isinstance(kind, str) and kind in SOURCE_COLUMNS and manifest.get('actor_id') == 'timka', 'Unknown actor/kind')
    require(type(manifest.get('schema')) is int and manifest['schema'] == 2 and manifest.get('layout_profile') == PROFILE, 'Unknown schema/profile')
    columns = SOURCE_COLUMNS[kind]
    width, count = len(columns), len(columns) * 4
    require(image.size == (width * 48, 256), 'Wrong image size')
    def numbers(value, expected):
        return isinstance(value, list) and value == expected and all(type(x) is int for x in value)
    require(numbers(manifest.get('dimensions'), [width * 48, 256]), 'Wrong dimensions')
    require(type(manifest.get('columns_per_direction')) is int and manifest['columns_per_direction'] == width, 'Wrong column count')
    require(type(manifest.get('source_cells')) is int and manifest['source_cells'] == count, 'Wrong cell count')
    require(isinstance(manifest.get('frames'), list) and len(manifest['frames']) == count, 'Missing/extra cells')
    require(numbers(manifest.get('source_column_mapping'), columns), 'Wrong original-column mapping')
    actual_map = manifest.get('animations_source_columns')
    require(isinstance(actual_map, dict) and set(actual_map) == set(COMPACT_MAPS[kind]), 'Unsupported clips')
    require(all(numbers(actual_map[k], v) for k, v in COMPACT_MAPS[kind].items()), 'Wrong animation mapping')
    require(manifest.get('directions') == DIRECTIONS, 'Wrong directions')
    require(numbers(manifest.get('frame_size'), [48, 64]) and numbers(manifest.get('pivot'), [24, 58]), 'Wrong frame/pivot')
    require(type(manifest.get('master_source_cells')) is int and manifest['master_source_cells'] == 32, 'Original source budget must remain explicit')
    require(manifest.get('animation_reference_count') == sum(map(len, COMPACT_MAPS[kind].values())) * 4, 'Wrong reference count')
    for index, frame in enumerate(manifest['frames']):
        row, col = divmod(index, width)
        require(isinstance(frame, dict), 'Cell must be an object')
        require(numbers([frame.get('index'), frame.get('column'), frame.get('source_column')], [index, col, columns[col]]) and frame.get('direction') == DIRECTIONS[row], 'Wrong cell index/column/direction')
        rect = [col * 48, row * 64, 48, 64]
        require(numbers(frame.get('rect'), rect) and numbers(frame.get('pivot'), [24, 58]), 'Wrong cell bounds/pivot')
        cell = image.crop((rect[0], rect[1], rect[0] + 48, rect[1] + 64))
        require(hashlib.sha256(cell.tobytes()).hexdigest() == frame.get('rgba_sha256'), 'Cell RGBA differs')
    require(type(manifest.get('unique_native_drawings')) is int and manifest['unique_native_drawings'] == len({f['rgba_sha256'] for f in manifest['frames']}), 'Wrong unique drawing count')


def compact(kind, base_version, output_version):
    decision = ROOT / 'automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json'
    approved = json.loads(decision.read_text())
    assert approved['status'] == 'APPROVED' and approved['profile'] == PROFILE
    source = ROOT / 'assets/source_art/characters/timka'
    old_png = source / f'{kind}_native_{base_version}.png'
    old_json = source / f'{kind}_manifest_{base_version}.json'
    original = json.loads(old_json.read_text())
    assert original['schema'] == 1 and original['actor_id'] == 'timka' and original['kind'] == kind
    assert original['sha256'] == sha(old_png)
    assert original['master_sha256'] == sha(ROOT / original['master'])
    assert original['source_cells'] == len(original['frames']) == 32
    assert original['animations_source_columns'] == MAPS[kind]
    image = Image.open(old_png).convert('RGBA')
    assert image.size == (384, 256)
    selected = SOURCE_COLUMNS[kind]
    output = Image.new('RGBA', (len(selected) * 48, 256))
    frames = []
    for row in range(4):
        for old_col in range(8):
            old_frame = original['frames'][row * 8 + old_col]
            assert old_frame['direction'] == DIRECTIONS[row] and old_frame['column'] == old_col
            assert old_frame['rect'] == [old_col * 48, row * 64, 48, 64]
            cell = image.crop((old_col * 48, row * 64, old_col * 48 + 48, row * 64 + 64))
            assert hashlib.sha256(cell.tobytes()).hexdigest() == old_frame['rgba_sha256']
            if old_col not in selected:
                continue
            col = selected.index(old_col)
            frame = copy.deepcopy(old_frame)
            frame.update(index=len(frames), column=col, source_column=old_col,
                         rect=[col * 48, row * 64, 48, 64])
            frames.append(frame)
            output.paste(cell, (col * 48, row * 64))
    png = source / f'{kind}_native_{output_version}.png'
    metadata = source / f'{kind}_manifest_{output_version}.json'
    assert not png.exists() and not metadata.exists(), 'Preserve prior candidates; use a new version'
    manifest = copy.deepcopy(original)
    manifest.update(schema=2, layout_profile=PROFILE, columns_per_direction=len(selected),
                    source_column_mapping=selected, source_cells=len(frames), frames=frames,
                    master_source_cells=32, dimensions=[len(selected) * 48, 256],
                    animations_source_columns=COMPACT_MAPS[kind], file=png.name,
                    status='CANDIDATE_SOURCE_NOT_IN_RUNTIME')
    manifest['animation_reference_count'] = sum(map(len, COMPACT_MAPS[kind].values())) * 4
    manifest['unique_native_drawings'] = len({f['rgba_sha256'] for f in frames})
    manifest['source_compaction'] = {
        'input_native': str(old_png.relative_to(ROOT)), 'input_native_sha256': sha(old_png),
        'input_manifest': str(old_json.relative_to(ROOT)), 'input_manifest_sha256': sha(old_json),
        'script': str(Path(__file__).resolve().relative_to(ROOT)), 'script_sha256': sha(Path(__file__)),
        'owner_decision': str(decision.relative_to(ROOT)), 'owner_decision_sha256': sha(decision),
        'discarded_source_columns': [c for c in range(8) if c not in selected],
        'whole_cell_RGBA_unchanged': True, 'anatomical_edit': False,
        'fresh_independent_source_review': 'PENDING_ALL_REQUIRED_CELLS',
    }
    if kind == 'world':
        shutil.copyfile(old_png, png)
        assert sha(png) == sha(old_png), 'WORLD PNG must remain byte-exact'
    else:
        output.save(png)
    manifest['sha256'] = sha(png)
    validate(manifest, Image.open(png).convert('RGBA'))
    metadata.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'kind': kind, 'cells': len(frames), 'sha256': sha(png),
                      'status': manifest['status'], 'runtime_approval': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('kind', choices=SOURCE_COLUMNS)
    parser.add_argument('--base-version', required=True)
    parser.add_argument('--output-version', required=True)
    args = parser.parse_args()
    compact(args.kind, args.base_version, args.output_version)
