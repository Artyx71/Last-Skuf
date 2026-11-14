#!/usr/bin/env python3
"""Copy four independently accepted action/finisher rows into a runtime candidate.

Whole reviewed RGBA frames only. This does not approve timing, gameplay or P06.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from pack_actor_sheet import DIRECTIONS, MAPS
from pack_portraits import PALETTE

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_review(path, actor, kind, direction, version):
    """Two actual preserved source-review schemas; neither grants runtime approval."""
    review = json.loads(path.read_text())
    assert review['status'] == f'ACCEPTABLE_{direction.upper()}_{kind.upper()}_DIRECTION_SOURCE_CANDIDATE'
    assert review['direction'] == direction
    report, metrics = path.with_suffix('.md'), path.with_name(path.stem + '_metrics.json')
    if review.get('schema') == 1:
        assert review['actor'] == actor and review['kind'] == kind and review['candidate'] == version
        assert review['scope'].startswith('SOURCE_ONLY_NO_') and review['must_fix_source_findings'] == []
        artifacts = review['review_artifacts_sha256']
        assert sha(report) == artifacts[report.name] and sha(metrics) == artifacts[metrics.name]
        for relative, expected in review['source_inventory_sha256'].items():
            source = (ROOT / relative).resolve()
            assert source.is_relative_to(ROOT) and sha(source) == expected
        return review['accepted_native_sha256'], review['accepted_master_sha256'], sha(report)
    assert 'schema' not in review, 'Unrecognized review schema'
    assert review['source_candidate_accepted'] and review['must_fix'] == []
    assert not review['runtime_approved'] and not review['full_phase_approved']
    assert sha(report) == review['report_sha256'] and sha(metrics) == review['metrics_sha256']
    return review['native_sha256'], review['master_sha256'], sha(report)


def assemble(actor, kind, versions, output_version):
    assert kind in ['action', 'finisher'] and len(versions) == 4
    source = ROOT / 'assets/source_art/characters' / actor
    reviews = ROOT / 'reports/phases/P06/art-preflight'
    dest = ROOT / 'game/assets/art/characters' / actor
    target = dest / f'{kind}_sheet.png'
    assert not target.exists() and not (dest / f'{kind}.json').exists(), 'Preserve existing runtime art/metadata'
    native_copy = source / f'{kind}_native_{output_version}.png'
    assembly = source / f'{kind}_assembly_{output_version}.json'
    assert not native_copy.exists() and not assembly.exists(), 'Use a sibling output version'
    output = Image.new('RGBA', (384, 256))
    frames, references = [], []
    allowed_colors = {tuple(bytes.fromhex(color)) for color in PALETTE}
    for row, (direction, version) in enumerate(zip(DIRECTIONS, versions)):
        native = source / f'{kind}_{direction}_native_{version}.png'
        manifest_path = source / f'{kind}_{direction}_manifest_{version}.json'
        review_path = reviews / f'{actor}_{kind}_{direction}_preflight_{version}.json'
        manifest = json.loads(manifest_path.read_text())
        reviewed_native, reviewed_master, report_sha = verify_review(review_path, actor, kind, direction, version)
        assert manifest['schema'] == 1 and manifest['actor_id'] == actor and manifest['kind'] == kind
        assert manifest['status'] == 'CANDIDATE_NOT_IN_PRODUCTION'
        assert sha(native) == manifest['sha256'] == reviewed_native
        assert sha(ROOT / manifest['master']) == manifest['master_sha256'] == reviewed_master
        assert manifest['directions'] == [direction] and manifest['source_cells'] == len(manifest['frames']) == 8
        assert manifest['frame_size'] == [48, 64] and manifest['pivot'] == [24, 58]
        image = Image.open(native).convert('RGBA')
        assert image.size == (384, 64)
        assert all(pixel[3] in [0, 255] and (not pixel[3] or pixel[:3] in allowed_colors)
                   for pixel in image.get_flattened_data())
        for column in range(8):
            frame = image.crop((column * 48, 0, (column + 1) * 48, 64))
            entry = manifest['frames'][column]
            assert entry['index'] == column and frame.getbbox()
            assert hashlib.sha256(frame.tobytes()).hexdigest() == entry['rgba_sha256']
            frames.append({'direction': direction, 'column': column,
                           'rect': [column * 48, row * 64, 48, 64], 'pivot': [24, 58],
                           'bounds': frame.getbbox(), 'rgba_sha256': entry['rgba_sha256'],
                           'source_native': str(native.relative_to(ROOT)), 'source_frame': entry})
        output.paste(image, (0, row * 64))
        references.append({'direction': direction, 'version': version,
                           'native': str(native.relative_to(ROOT)), 'sha256': sha(native),
                           'manifest': str(manifest_path.relative_to(ROOT)), 'manifest_sha256': sha(manifest_path),
                           'independent_source_review': str(review_path.relative_to(ROOT)),
                           'review_sha256': sha(review_path), 'report_sha256': report_sha,
                           'runtime_approval': False})
    dest.mkdir(parents=True, exist_ok=True)
    output.save(target)
    output.save(native_copy)
    metadata = {'schema': 1, 'actor_id': actor, 'kind': kind,
                'status': 'REVIEWED_SOURCE_CANDIDATE_RUNTIME_PENDING',
                'file': target.name, 'sha256': sha(target), 'frame_size': [48, 64],
                'dimensions': [384, 256], 'pivot': [24, 58], 'directions': DIRECTIONS,
                'source_cells': 32, 'unique_native_drawings': len({f['rgba_sha256'] for f in frames}),
                'frames': frames, 'animations_source_columns': MAPS[kind],
                'animation_reference_count': sum(map(len, MAPS[kind].values())) * 4,
                'assembled_from': references,
                'packing': 'exact RGBA direction rows; no additional scaling/repainting/mirroring',
                'review': {'source_only': True, 'actual_animation': 'PENDING',
                           'contact_alignment': 'PENDING', 'phase_approval': False}}
    text = json.dumps(metadata, ensure_ascii=False, indent=2) + '\n'
    (dest / f'{kind}.json').write_text(text)
    assembly.write_text(text)
    board = Image.new('RGBA', output.size, (36, 48, 44, 255))
    board.alpha_composite(output)
    board.resize((1152, 768), Image.Resampling.NEAREST).save(source / f'{kind}_inspection_{output_version}_3x.png')
    print(json.dumps({'actor': actor, 'kind': kind, 'sha256': sha(target), 'phase_approval': False}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('actor')
    parser.add_argument('kind', choices=['action', 'finisher'])
    parser.add_argument('--versions', nargs=4, required=True, metavar=('DOWN', 'LEFT', 'RIGHT', 'UP'))
    parser.add_argument('--output-version', required=True)
    args = parser.parse_args()
    assemble(args.actor, args.kind, args.versions, args.output_version)
