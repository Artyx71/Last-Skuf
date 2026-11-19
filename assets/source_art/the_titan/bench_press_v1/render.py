#!/usr/bin/env python3
"""Original native-grid drawing. Generated concept is not an input image."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / 'game/assets/art/the_titan'
PAL = ['#10141f', '#191e2b', '#262d3c', '#384252', '#4f5b68', '#788a91',
       '#afbcaf', '#d9d3b2', '#4b334e', '#70455e', '#aa5979', '#795641',
       '#ab7c4e', '#d5aa6d']
im = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
d = ImageDraw.Draw(im)

# Floor shadows and steel feet have hard native edges, just like the P04 props.
for box in [(25, 15, 40, 83), (87, 15, 102, 83), (48, 110, 81, 119)]:
    d.rectangle(box, fill=PAL[0])
for x in (27, 89):
    d.rectangle((x, 14, x+11, 78), fill=PAL[1])
    d.rectangle((x+2, 16, x+8, 75), fill=PAL[3])
    d.line((x+2, 17, x+2, 74), fill=PAL[5])
    d.rectangle((x-3, 75, x+14, 81), fill=PAL[1])
    d.rectangle((x-1, 76, x+12, 79), fill=PAL[4])
    for bolt in (x, x+10):
        d.rectangle((bolt, 77, bolt+1, 78), fill=PAL[6])
    d.rectangle((x-1, 13, x+10, 20), fill=PAL[1])
    d.rectangle((x+1, 14, x+8, 17), fill=PAL[6])
    d.line((x+2, 18, x+7, 18), fill=PAL[4])
    d.rectangle((x-1, 33, x+9, 39), fill=PAL[1])
    d.line((x, 34, x+7, 34), fill=PAL[6])

d.rectangle((35, 61, 93, 67), fill=PAL[1])
d.rectangle((37, 62, 91, 65), fill=PAL[4])
d.line((38, 62, 90, 62), fill=PAL[5])
d.rectangle((60, 92, 68, 115), fill=PAL[1])
d.rectangle((62, 93, 65, 114), fill=PAL[4])
d.rectangle((49, 111, 79, 117), fill=PAL[1])
d.rectangle((51, 112, 77, 115), fill=PAL[4])
for x in (53, 74):
    d.rectangle((x, 113, x+1, 114), fill=PAL[6])

# Two distinct upholstered pads, seams, and deliberately placed wear marks.
for top, bottom in [(41, 94), (97, 108)]:
    d.rectangle((50, top, 77, bottom), fill=PAL[0])
    d.rectangle((52, top-1, 75, bottom+1), fill=PAL[0])
    d.rectangle((52, top, 75, bottom), fill=PAL[8])
    d.rectangle((53, top+1, 74, bottom-1), fill=PAL[9])
    d.line((53, top+2, 74, top+2), fill=PAL[10])
    d.line((53, top+2, 53, bottom-2), fill=PAL[10])
    d.line((55, bottom-1, 74, bottom-1), fill=PAL[8])
for box in [(54, 47, 57, 48), (56, 46, 59, 47), (71, 67, 73, 69),
            (54, 85, 55, 89), (55, 89, 59, 90), (70, 101, 73, 102)]:
    d.rectangle(box, fill=PAL[8])

# Horizontal bar with discrete grip knurling, collars and separately readable plates.
d.rectangle((7, 29, 119, 36), fill=PAL[0])
d.rectangle((8, 30, 118, 34), fill=PAL[4])
d.line((9, 30, 117, 30), fill=PAL[6])
d.line((10, 31, 116, 31), fill=PAL[5])
for x in list(range(42, 53, 3))+list(range(75, 86, 3)):
    d.line((x, 31, x, 33), fill=PAL[4])
for left in (11, 100):
    for x, top, bottom in [(left, 22, 43), (left+5, 18, 47), (left+10, 20, 45)]:
        d.rectangle((x, top, x+5, bottom), fill=PAL[0])
        d.rectangle((x+1, top+1, x+4, bottom-1), fill=PAL[2])
        d.line((x+1, top+2, x+1, bottom-2), fill=PAL[4])
        d.line((x+2, top+2, x+4, top+2), fill=PAL[5])
    d.rectangle((left+7, 25, left+8, 27), fill=PAL[3])
for x in (29, 95):
    d.rectangle((x, 27, x+3, 38), fill=PAL[11])
    d.rectangle((x, 28, x+2, 35), fill=PAL[12])
    d.line((x, 28, x, 34), fill=PAL[13])

colors = im.getcolors(im.width*im.height)
assert {c[3] for _, c in colors} == {0, 255}
assert len(colors) <= len(PAL)+1 and im.getbbox() == (7, 13, 120, 120)
OUT.mkdir(parents=True, exist_ok=True)
target = OUT / 'bench_press.png'
im.save(target)
metadata = {
    'status': 'CANDIDATE_PENDING_ART_REVIEW_NOT_COMPLETE_CHAPTER',
    'authoring': 'Original explicit integer pixel drawing; no image editing, resampling or input image',
    'concept': 'generated-source.png retained as a design sketch only',
    'source': str(Path(__file__).relative_to(ROOT)),
    'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'file': str(target.relative_to(ROOT)),
    'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'size': [128, 128], 'palette': PAL, 'RGBA_colors': len(colors),
    'alpha': [0, 255], 'anchor': [64, 64], 'proposed_footprint': [128, 128],
    'collision_or_environment_ability_implemented': False,
    'actual_native_Godot_capture': False, 'independent_ART_review': 'PENDING',
}
(HERE / 'native-sprite.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(metadata, ensure_ascii=False))
