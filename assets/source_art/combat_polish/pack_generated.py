"""Technical packing of original image_gen drawings, without anatomy reconstruction.

Some generated weapons cross nominal cell edges. Connected-component bounds recover
the complete drawing instead of silently clipping at that artificial boundary.
ImageMagick labels alpha; Pillow only crops, samples NN, anchors and maps palettes.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).parent / 'attempt2'
SCALE = {'yakuza': .24, 'patrol': .245, 'rusher': .24, 'shooter': .22}
CACHE = {}
INPUTS = {}
PACKING = {}
SOCKETS = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def master(name, kind):
    if name in CACHE:
        return CACHE[name]
    path = SOURCE / (name + '_master.png')
    INPUTS[str(path.relative_to(ROOT))] = sha(path)
    image = Image.open(path).convert('RGBA')
    assert image.size == (1536, 1024)
    alpha = image.getchannel('A').point(lambda a: 255 if a >= 128 else 0)
    assert alpha.getpixel((0, 0)) == 0, 'Matte is not transparent; request a real generator edit'
    text = subprocess.check_output(['magick', str(path), '-alpha', 'extract', '-threshold', '50%',
        '-define', 'connected-components:verbose=true', '-connected-components', '8', 'null:'], text=True)
    pattern = re.compile(r'^\s*(\d+): (\d+)x(\d+)\+(\d+)\+(\d+) ([\d.]+),([\d.]+) (\d+) srgb\(255,255,255\)', re.M)
    bodies = []
    for match in pattern.finditer(text):
        _label, width, height, x, y, cx, cy, count = match.groups()
        if int(count) < 3000:
            continue
        bodies.append((int(float(cy) // 256), int(float(cx) // 192),
            (int(x), int(y), int(x)+int(width), int(y)+int(height)), int(count)))
    assert len(bodies) == 32 and len({(r, c) for r, c, _, _ in bodies}) == 32
    palette_path = ROOT / 'game/assets/art' / ('yakuza/atlas.json' if kind == 'yakuza' else 'enemies/atlas.json')
    INPUTS[str(palette_path.relative_to(ROOT))] = sha(palette_path)
    colors = json.loads(palette_path.read_text())['palette']['rgb_hex'] + ['#ffe4a3', '#936241', '#ce9a62']
    palette = Image.new('P', (1, 1))
    rgb = [tuple(bytes.fromhex(color[1:])) for color in colors]
    palette.putpalette([v for color in rgb for v in color] + list(rgb[0]) * (256-len(rgb)))
    result = {}
    coverage = 0
    details = []
    for row, column, box, component_area in bodies:
        crop = image.crop(box)
        mask = alpha.crop(box)
        area = sum(mask.histogram()[1:])
        assert area >= component_area
        coverage += area
        crop.putalpha(mask)
        width, height = (round(crop.width*SCALE[kind]), round(crop.height*SCALE[kind]))
        assert width <= 46 and height <= 56, (name, row, column, width, height)
        crop = crop.resize((width, height), Image.Resampling.NEAREST)
        # Retain nominal torso origin where possible; only clamp the full drawing
        # into the padded cell when an extended weapon requires a small adjustment.
        nominal = 24 + round((box[0]-(column*192+96))*SCALE[kind])
        x = min(max(1, nominal), 47-width)
        y = 58-height
        aligned = Image.new('RGBA', (48, 64))
        aligned.alpha_composite(crop, (x, y))
        assert sum(aligned.getchannel('A').histogram()[1:]) == sum(crop.getchannel('A').histogram()[1:])
        limited = aligned.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE).convert('RGBA')
        limited.putalpha(aligned.getchannel('A'))
        limited.paste((0, 0, 0, 0), (0, 0), ImageOps.invert(limited.getchannel('A')))
        result[row, column] = limited
        details.append({'row': row, 'column': column, 'source_bounds': box,
            'source_component_pixels': component_area, 'source_crop_opaque_pixels': area,
            'uniform_scale_for_character': SCALE[kind], 'native_offset': [x, y],
            'nominal_x': nominal, 'native_bounds': limited.getbbox()})
    assert coverage == sum(alpha.histogram()[1:]), 'Every thresholded source pixel must be retained once'
    PACKING[name] = {'master_sha256': sha(path), 'source_opaque_pixels': coverage,
        'all_opaque_pixels_assigned_once': True, 'drawings': details}
    CACHE[name] = result
    return result


def pose(kind, direction, state, frame, reaction=False):
    if kind == 'yakuza':
        index = ['unarmed', 'blunt', 'sharp', 'firearm', 'environmental'].index(state)*3+frame
        name, column = ('yakuza_part1', index) if index < 8 else ('yakuza_part2', index-8)
        return master(name, kind)[direction, column].copy()
    states = ['telegraph', 'attack', 'recovery', 'hurt', 'stun', 'knockdown', 'death', 'finisher_reaction']
    if reaction:
        # Separate restrained/contact/fallen action paths use real drawn anatomy.
        # Final corpses are intentionally shared; these are not 528 unique designs.
        state, frame = ([('finisher_reaction', 0),
            {'unarmed': ('hurt', 1), 'blunt': ('death', 0), 'sharp': ('finisher_reaction', 1),
             'firearm': ('hurt', 0), 'environmental': ('knockdown', 0)}[state], ('death', 2)])[frame]
    name = f'{kind}_key{frame}' + ('_clean' if kind == 'patrol' and frame == 0 else '')
    return master(name, kind)[direction, states.index(state)].copy()


def clothing_socket(image, prone):
    """Author-selected torso zone, snapped to an actual opaque clothing pixel.

    Full pose silhouette is the mask; wounds never float at a standing offset once
    a body lies down. Final native boards are still subject to visual review.
    """
    desired = (26, 49) if prone else (24, 35)
    pixels = image.load()
    candidates = [(x, y) for y in range(max(1, desired[1]-7), min(63, desired[1]+8))
        for x in range(max(1, desired[0]-9), min(47, desired[0]+10))
        if pixels[x, y][3] and max(pixels[x, y][:3])-min(pixels[x, y][:3]) < 65
        and max(pixels[x, y][:3]) < 140]
    assert candidates, 'No clothing at authored socket'
    return min(candidates, key=lambda p: (p[0]-desired[0])**2+(p[1]-desired[1])**2)
