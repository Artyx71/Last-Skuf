#!/usr/bin/env python3
"""Prepare whole generated figures for an atlas; never draw or edit anatomy.

Preserve contained cells exactly. Translate other complete poses minimally into
the requested gutters. Explicitly permitted overwide figures receive one uniform
whole-figure NEAREST fit, preserving their support bottom. Raw masters survive.
This is source preparation, not independent art or runtime acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgba(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('actor')
    parser.add_argument('kind', choices=['action', 'finisher'])
    parser.add_argument('--version', required=True)
    parser.add_argument('--output-version', required=True)
    parser.add_argument('--margin', type=int, default=16)
    parser.add_argument('--allow-uniform-fit-cells', type=int, nargs='*', default=[])
    args = parser.parse_args()
    assert 1 <= args.margin <= 32
    assert all(0 <= cell < 32 for cell in args.allow_uniform_fit_cells)
    folder = (ROOT / 'assets/source_art/characters' / args.actor).resolve()
    assert folder.is_relative_to(ROOT / 'assets/source_art/characters')
    source = folder / f'{args.kind}_master_{args.version}.png'
    target = folder / f'{args.kind}_master_{args.output_version}.png'
    recipe = folder / f'{args.kind}_{args.output_version}_assembly.json'
    assert not target.exists() and not recipe.exists()
    image = Image.open(source).convert('RGBA')
    assert image.size == (1536, 1024)
    output = image.copy()
    entries = []
    for index in range(32):
        row, col = divmod(index, 8)
        box = (col * 192, row * 256, (col + 1) * 192, (row + 1) * 256)
        cell = image.crop(box)
        support = cell.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
        bounds = support.getbbox()
        assert bounds
        left, top, right, bottom = bounds
        width, height = right - left, bottom - top
        max_width, max_height = 192 - 2 * args.margin, 256 - 2 * args.margin
        scale = min(1.0, max_width / width, max_height / height)
        if scale < 1.0:
            assert index in args.allow_uniform_fit_cells, (index, 'Uniform fit requires explicit cell authorization')
            new_width = max(1, round(width * scale))
            new_height = max(1, round(height * scale))
            complete = cell.crop(bounds).resize((new_width, new_height), Image.Resampling.NEAREST)
            dest_x = (192 - new_width) // 2
            dest_y = max(args.margin, min(bottom - new_height, 256 - args.margin - new_height))
            fitted = Image.new('RGBA', (192, 256))
            fitted.paste(complete, (dest_x, dest_y))
            assert sum(fitted.getchannel('A').get_flattened_data()) == sum(complete.getchannel('A').get_flattened_data())
            operation = 'uniform complete alpha-support rectangle NEAREST fit; no anatomy edits'
            detail = {'uniform_scale': scale, 'resized_complete_figure': [new_width, new_height],
                      'resized_rgba_sha256': rgba(complete), 'placement': [dest_x, dest_y],
                      'subthreshold_alpha_outside_support': 'discarded consistently with packing alpha128'}
        else:
            dx = max(args.margin - left, min(0, 192 - args.margin - right))
            dy = max(args.margin - top, min(0, 256 - args.margin - bottom))
            if dx == dy == 0:
                fitted = cell
            else:
                fitted = Image.new('RGBA', (192, 256))
                fitted.paste(cell, (dx, dy))
            assert sum(a >= 128 for a in fitted.getchannel('A').get_flattened_data()) == sum(a >= 128 for a in cell.getchannel('A').get_flattened_data())
            assert fitted.crop((left + dx, top + dy, right + dx, bottom + dy)).tobytes() == cell.crop(bounds).tobytes()
            operation = 'byte-exact' if dx == dy == 0 else 'whole figure translation only'
            detail = {'translation': [dx, dy], 'support_rgba_preserved_exact': True}
        after = fitted.getchannel('A').point(lambda a: 255 if a >= 128 else 0).getbbox()
        assert after and min(after[0], after[1], 192 - after[2], 256 - after[3]) >= args.margin
        output.paste(fitted, box[:2])
        entries.append({'cell': index, 'source_bounds': list(bounds), 'output_bounds': list(after),
                        'source_cell_rgba_sha256': rgba(cell), 'output_cell_rgba_sha256': rgba(fitted),
                        'operation': operation, **detail})
    output.save(target)
    data = {'schema': 1, 'actor_id': args.actor, 'kind': args.kind,
            'source': str(source.relative_to(ROOT)), 'source_sha256': sha(source),
            'output': str(target.relative_to(ROOT)), 'output_sha256': sha(target),
            'margin_source_pixels': args.margin, 'support_alpha_threshold': 128,
            'anatomical_editing': False, 'painting': False, 'mirroring': False,
            'uniform_fit_cells_explicitly_permitted': args.allow_uniform_fit_cells,
            'entries': entries, 'status': 'CANDIDATE_REQUIRES_INDEPENDENT_ART', 'phase_approval': False}
    recipe.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps({'output': str(target.relative_to(ROOT)), 'sha256': sha(target),
                      'changed_cells': [e['cell'] for e in entries if e['operation'] != 'byte-exact']}))


if __name__ == '__main__':
    main()
