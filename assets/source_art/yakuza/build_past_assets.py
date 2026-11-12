#!/usr/bin/env python3
"""Pack only the flashback portraits; never rewrites present/world runtime PNG."""
from pathlib import Path
from PIL import Image, ImageOps
from collections import Counter
import hashlib
import json
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'assets/source_art/yakuza'
DEST=ROOT/'game/assets/art/yakuza'
REPORT=ROOT/'reports/phases/P01'
atlas_path=DEST/'atlas.json'
atlas=json.loads(atlas_path.read_text())
master_path=SOURCE/'portraits_past_master_v2.png'
master=Image.open(master_path).convert('RGBA')
assert master.size==(1536,1024)
result=Image.new('RGBA',(800,160))
for index in range(5):
    x,y=(index%3)*512,(index//3)*512
    frame=master.crop((x,y,x+512,y+512))
    frame.putalpha(frame.getchannel('A').point(lambda value:255 if value>=128 else 0))
    frame.paste((0,0,0,0),(0,0),ImageOps.invert(frame.getchannel('A')))
    frame=frame.resize((156,156),Image.Resampling.NEAREST)
    result.paste(frame,(index*160+2,2))
colors=[tuple(bytes.fromhex(c[1:])) for c in atlas['palette']['rgb_hex']]
shared_palette=Image.new('P',(1,1))
shared_palette.putpalette([v for rgb in colors for v in rgb]+list(colors[0])*(256-len(colors)))
quant=result.convert('RGB').quantize(palette=shared_palette,dither=Image.Dither.NONE).convert('RGBA')
quant.putalpha(result.getchannel('A'))
quant.paste((0,0,0,0),(0,0),ImageOps.invert(quant.getchannel('A')))
quant.save(DEST/'portraits_past.png')
quant.save(SOURCE/'portraits_past_native_source.png')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
frames=[]
for index,name in enumerate(atlas['portraits']['expressions']):
    frame=quant.crop((index*160,0,index*160+160,160))
    frames.append({'id':name,'expression':name,'index':index,'rect':[index*160,0,160,160],'origin':[80,160],'bounds':list(frame.getbbox()),'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
atlas['portraits_past']={'file':'portraits_past.png','era':'past_flashback','dimensions':[800,160],'frame_size':[160,160],'columns':5,'rows':1,'expressions':atlas['portraits']['expressions'],'fps':0,'frames':frames,'sha256':sha(DEST/'portraits_past.png'),'status':'DRAFT_REQUIRES_LIKENESS_REVIEW','source':{'master':str(master_path.relative_to(ROOT)),'master_sha256':sha(master_path),'prompt':'assets/source_art/yakuza/past_portrait_prompt.txt','metadata':'assets/source_art/yakuza/past_portrait_generation_metadata.json','cleanup_prompt':'assets/source_art/yakuza/past_cleanup_prompt.txt','cleanup_metadata':'assets/source_art/yakuza/past_cleanup_generation_metadata.json','previous_master':'assets/source_art/yakuza/portraits_past_master_v1.png','recipe':'assets/source_art/yakuza/build_past_assets.py','identity_reference_id':'yakuza','style_reference':'assets/source_art/yakuza/portraits_master_v1.png','mode':'built-in image_gen','alpha_threshold':128,'resize':'NEAREST','palette':'same31 opaque colors as present/world'}}
atlas['review']['known_limitations']=[x for x in atlas['review']['known_limitations'] if 'old-era' not in x]
atlas_path.write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
preview=Image.new('RGBA',quant.size)
pixels=preview.load()
for y in range(preview.height):
    for x in range(preview.width):pixels[x,y]=(45,80,65,255) if (x//16+y//16)%2 else (210,192,150,255)
preview.alpha_composite(quant)
preview.resize((1600,320),Image.Resampling.NEAREST).convert('RGB').save(REPORT/'portraits_past_preview_2x.png')
alpha_values=set(quant.getchannel('A').get_flattened_data())
assert alpha_values=={0,255}
assert all(p==(0,0,0,0) for p in quant.get_flattened_data() if not p[3])
assert len({f['rgba_sha256'] for f in frames})==5
report={'status':'STRUCTURAL_CHECKS_ONLY_NOT_LIKENESS_APPROVAL','file':'portraits_past.png','dimensions':list(quant.size),'alpha_values':sorted(alpha_values),'opaque_colors':len(set(p[:3] for p in quant.get_flattened_data() if p[3])),'sha256':sha(DEST/'portraits_past.png'),'master_alpha_samples':[{'position':list(p),'rgba':list(master.getpixel(p))} for p in [(0,0),(100,10),(500,10),(1300,700)]],'raw_reference_read_by_packer':False}
(REPORT/'art_past_structural_check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
