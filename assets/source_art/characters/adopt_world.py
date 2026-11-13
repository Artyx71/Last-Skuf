#!/usr/bin/env python3
"""Copy an independently reviewed whole world atlas without changing its pixels.

Source approval permits runtime inspection, not combat/phase acceptance.
The original candidate, rejected versions and independent reports are retained.
"""
import argparse
import copy
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adopt(actor, version, review_path):
    source = ROOT / 'assets/source_art/characters' / actor
    native = source / f'world_native_{version}.png'
    manifest_path = source / f'world_manifest_{version}.json'
    review_path = (ROOT / review_path).resolve()
    assert review_path.is_relative_to(ROOT / 'reports/phases/P06/art-preflight')
    review = json.loads(review_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    assert review['status'] == 'ACCEPTABLE_FOUR_DIRECTION_SOURCE_CANDIDATE'
    assert review['actor_id'] == actor and review['source_only_acceptance']
    assert review['all32_freshly_reviewed'] and not review['must_fix']
    assert not review['runtime_approved'] and not review['full_phase_approved']
    assert sha(review_path.with_suffix('.md')) == review['report_sha256']
    assert sha(review_path.with_name(review_path.stem + '_metrics.json')) == review['metrics_sha256']
    assert manifest['schema'] == 1 and manifest['actor_id'] == actor and manifest['kind'] == 'world'
    assert manifest['status'] == 'CANDIDATE_SOURCE_NOT_IN_RUNTIME'
    assert sha(native) == manifest['sha256'] == review['native_sha256']
    assert sha(ROOT / manifest['master']) == manifest['master_sha256'] == review['master_sha256']
    assert manifest['directions'] == ['down', 'left', 'right', 'up']
    assert manifest['frame_size'] == [48, 64] and manifest['pivot'] == [24, 58]
    assert manifest['animations_source_columns'] == {'idle': [0, 1], 'walk': [2, 3, 4, 5], 'run': [6, 7]}
    assert manifest['source_cells'] == len(manifest['frames']) == 32
    image = Image.open(native).convert('RGBA')
    assert image.size == (384, 256)
    for index, frame in enumerate(manifest['frames']):
        row, column = divmod(index, 8)
        assert frame['direction'] == manifest['directions'][row] and frame['column'] == column
        assert frame['rect'] == [column * 48, row * 64, 48, 64]
        cell = image.crop((column * 48, row * 64, column * 48 + 48, row * 64 + 64))
        assert hashlib.sha256(cell.tobytes()).hexdigest() == frame['rgba_sha256']
    destination = ROOT / 'game/assets/art/characters' / actor
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / 'world_sheet.png'
    assert not target.exists(), 'Preserve any existing runtime atlas; explicit version migration required'
    assert not (destination / 'world.json').exists(), 'Preserve existing runtime metadata'
    output = copy.deepcopy(manifest)
    output.update(file=target.name, status='SOURCE_ACCEPTED_RUNTIME_VALIDATION_PENDING')
    output['source_adoption'] = {
        'native': str(native.relative_to(ROOT)), 'sha256': sha(native),
        'manifest': str(manifest_path.relative_to(ROOT)), 'manifest_sha256': sha(manifest_path),
        'independent_source_review': str(review_path.relative_to(ROOT)),
        'review_sha256': sha(review_path), 'report_sha256': review['report_sha256'],
        'packing': 'exact file copy; no pixel changes',
    }
    output['review'] = {'independent_source_art': review['status'], 'actual_animation': 'PENDING',
                        'runtime_approval': False, 'phase_approval': False}
    shutil.copyfile(native, target)
    assert sha(target) == sha(native)
    (destination / 'world.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'actor': actor, 'sha256': sha(target), 'source_review': sha(review_path),
                      'runtime_approval': False, 'phase_approval': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('actor')
    parser.add_argument('--version', required=True)
    parser.add_argument('--review', required=True)
    args = parser.parse_args()
    adopt(args.actor, args.version, args.review)
