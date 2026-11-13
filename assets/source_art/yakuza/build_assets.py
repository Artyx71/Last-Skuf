#!/usr/bin/env python3
"""Deterministic technical packing of generated pixel drawings; never reads raw photos.
Run with Pillow13: .tools/art-venv/bin/python assets/source_art/yakuza/build_assets.py
Only nearest-neighbor sampling, generated alpha cleanup, palette reduction and atlas packing.
"""
from pathlib import Path
import hashlib
import json
from collections import Counter
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / 'assets/source_art/yakuza'
DEST = ROOT / 'game/assets/art/yakuza'
REPORT = ROOT / 'reports/phases/P01'
DEST.mkdir(parents=True, exist_ok=True)
REPORT.mkdir(parents=True, exist_ok=True)
EMOTIONS = ['neutral', 'angry', 'surprised', 'hurt', 'catchphrase']
DIRECTIONS = ['down', 'left', 'right', 'up']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def hard_alpha(image):
    result = image.convert('RGBA')
    result.putalpha(result.getchannel('A').point(lambda a: 255 if a >= 128 else 0))
    result.paste((0,0,0,0), (0,0), ImageOps.invert(result.getchannel('A')))
    return result

portraits = Image.new('RGBA', (800,160))
portrait_master = Image.open(SOURCE/'portraits_master_v1.png')
assert portrait_master.size == (1536,1024)
for index, emotion in enumerate(EMOTIONS):
    sx, sy = (index % 3)*512, (index//3)*512
    frame = hard_alpha(portrait_master.crop((sx,sy,sx+512,sy+512)))
    frame = frame.resize((156,156), Image.Resampling.NEAREST)
    portraits.paste(frame, (index*160+2,2))

world = Image.new('RGBA', (384,256))
world_master = Image.open(SOURCE/'world_master_v1.png')
assert world_master.size == (1536,1024)
packing = []
for row, direction in enumerate(DIRECTIONS):
    for col in range(8):
        sx, sy = col*192, row*256
        frame = hard_alpha(world_master.crop((sx,sy,sx+192,sy+256)))
        frame = frame.resize((48,64), Image.Resampling.NEAREST)
        # The generator placed up-view phone on its right. Mirroring this row
        # puts the phone in the same anatomical left hand as down/side views.
        if direction == 'up':
            frame = ImageOps.mirror(frame)
        box = frame.getbbox()
        assert box is not None
        # Keep the fixed engine anchor at center-x24, sole-bottom58.
        offset = (24-(box[0]+box[2])//2,58-box[3])
        aligned = Image.new('RGBA',(48,64))
        aligned.paste(frame,offset)
        assert sum(aligned.getchannel('A').get_flattened_data()) == sum(frame.getchannel('A').get_flattened_data()), 'cropped opaque pixels'
        world.paste(aligned,(col*48,row*64))
        packing.append({'direction':direction,'column':col,'source_rect':[sx,sy,192,256], 'mirror_x':direction=='up','offset_after_nearest':list(offset)})

# Deliberate shared production palette. Adaptive quantization was tried first,
# but dark clothing dominated it and erased the phone cyan and bruise purple.
# These 31 opaque colors preserve those important character/readability cues.
PALETTE_HEX = [
    '0b090e','15101a','211b29','352b3d','4c3c56','6c9aaf','75455f',
    '15151e','252332','353244','222936','344255','4c6076',
    '562d37','873e3c','a75c49','c47755','dc956f','efb08b','f6c59f',
    'ece3d5','2b1a1e','6d354b','994a63','bc6573',
    '4e202c','8b3146','bc5260','e8878c','3e94b4','7bd2df',
]
PALETTE_RGB = [tuple(bytes.fromhex(color)) for color in PALETTE_HEX]
palette_image = Image.new('P',(1,1))
flat_palette = [channel for rgb in PALETTE_RGB for channel in rgb]
palette_image.putpalette(flat_palette + list(PALETTE_RGB[0]) * (256-len(PALETTE_RGB)))

def apply_palette(image):
    result = image.convert('RGB').quantize(palette=palette_image,dither=Image.Dither.NONE).convert('RGBA')
    result.putalpha(image.getchannel('A'))
    result.paste((0,0,0,0),(0,0),ImageOps.invert(result.getchannel('A')))
    return result
portraits, world = apply_palette(portraits), apply_palette(world)
portraits.save(DEST/'portraits.png')
world.save(DEST/'world_sheet.png')
portraits.save(SOURCE/'portraits_native_source.png')
world.save(SOURCE/'world_native_source.png')

# Visual evidence on two opaque backgrounds exposes alpha halos/matte.
def preview(image, scale):
    checker=Image.new('RGBA',image.size)
    pixels=checker.load()
    for y in range(image.height):
        for x in range(image.width):
            pixels[x,y]=(45,80,65,255) if (x//16+y//16)%2 else (210,192,150,255)
    checker.alpha_composite(image)
    return checker.resize((image.width*scale,image.height*scale),Image.Resampling.NEAREST).convert('RGB')
preview(portraits,2).save(REPORT/'portraits_preview_2x.png')
preview(world,3).save(REPORT/'world_preview_3x.png')

palette=sorted(set(p[:3] for im in (portraits,world) for p in im.get_flattened_data() if p[3]))
def frame_info(image,rect,pivot):
    x,y,w,h=rect
    frame=image.crop((x,y,x+w,y+h))
    return {'rect':rect,'origin':pivot,'bounds':list(frame.getbbox()),'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()}
frames=[]
for row,direction in enumerate(DIRECTIONS):
    for col in range(8):
        info=frame_info(world,[col*48,row*64,48,64],[24,58]); info.update({'id':f'{direction}_{col}','direction':direction,'column':col,'animation':'idle' if col<2 else 'walk'})
        frames.append(info)
portrait_frames=[]
for col,emotion in enumerate(EMOTIONS):
    info=frame_info(portraits,[col*160,0,160,160],[80,160]);info.update({'id':emotion,'expression':emotion,'index':col})
    portrait_frames.append(info)
manifest={
 'asset_id':'yakuza_p01_v1', 'version':1, 'status':'DRAFT_REQUIRES_LIKENESS_REVIEW',
 'author':'Codex art production using built-in image_gen; technical packing by Pillow13',
 'source':{'reference_id':'yakuza','reference_private_path':'assets/references/characters/yakuza_ref01.png','generation':'built-in image_gen','authorization':'Owner explicitly authorized image_gen with supplied photographs in the active session. No public distribution approval implied.','masters':[{'path':str(p.relative_to(ROOT)), 'sha256':sha(p)} for p in [SOURCE/'portraits_master_v1.png',SOURCE/'world_master_v1.png']], 'prompts':['assets/source_art/yakuza/portrait_prompt.txt','assets/source_art/yakuza/world_prompt.txt'],'recipe':'assets/source_art/yakuza/build_assets.py'},
 'palette':{'opaque_colors':len(palette),'transparent_colors':1,'rgb_hex':['#%02x%02x%02x'%p for p in palette]},
 'portraits':{'file':'portraits.png','dimensions':[800,160],'frame_size':[160,160],'columns':5,'rows':1,'expressions':EMOTIONS,'fps':0,'frames':portrait_frames,'sha256':sha(DEST/'portraits.png'),'native_size_rationale':'160px preserves hair silhouette, eye relationships, jaw and moles while fitting a 640x360 dialogue UI. 2px transparent cell inset prevents edge clipping.'},
 'world':{'file':'world_sheet.png','dimensions':[384,256],'frame_size':[48,64],'columns':8,'rows':4,'directions':DIRECTIONS,'pivot':[24,58],'animations':{'idle':{'columns':[0,1],'fps':3,'loop':True},'walk':{'columns':[2,3,4,5,6,7],'fps':8,'loop':True}},'frames':frames,'sha256':sha(DEST/'world_sheet.png')},
 'packing':{'alpha_threshold':128,'resize_filter':'NEAREST','shared_palette_method':'31 intentionally selected opaque colors; nearest RGB, no dither','up_row_mirrored_for_phone_hand':True,'world_frame_adjustments':packing},
 'review':{'human_likeness':'PENDING','independent_art_review':'PENDING','in_engine':'PENDING root integration','known_limitations':['Image generation masters have soft alpha fringe and off-grid color variation; native exports clean alpha and use one fixed pixel grid and shared palette.','Generated walk poses may show hair/volume jitter; require animation and likeness inspection.','World sprite represents present-era body; past/flashback portraits are a separate atlas entry.','No talk frames; five required expressions are included.']}
}
if (DEST/'atlas.json').exists():
    previous = json.loads((DEST/'atlas.json').read_text())
    if 'portraits_past' in previous:
        manifest['portraits_past'] = previous['portraits_past']
(DEST/'atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
structure={'status':'STRUCTURAL_CHECKS_ONLY_NOT_LIKENESS_APPROVAL','assets':[]}
for file,image in [('portraits.png',portraits),('world_sheet.png',world)]:
    alpha=set(image.getchannel('A').get_flattened_data())
    assert alpha=={0,255}
    assert all(p==(0,0,0,0) for p in image.get_flattened_data() if p[3]==0)
    opaque_count=sum(p[3]==255 for p in image.get_flattened_data())
    structure['assets'].append({'file':file,'dimensions':list(image.size),'mode':image.mode,'alpha_values':sorted(alpha),'opaque_pixels':opaque_count,'opaque_colors':len(set(p[:3] for p in image.get_flattened_data() if p[3])),'sha256':sha(DEST/file)})
assert all(frame['bounds'][3] == 58 for frame in frames)
assert len({f['rgba_sha256'] for f in frames}) == 32
structure['world_frame_count']=32
structure['unique_world_frames']=32
structure['portrait_expression_count']=5
structure['sole_baseline_y_exclusive']=58
structure['palette_opaque_colors']=len(palette)
structure['raw_reference_read_by_packer']=False
(REPORT/'art_structural_check.json').write_text(json.dumps(structure,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(structure,ensure_ascii=False,indent=2))
