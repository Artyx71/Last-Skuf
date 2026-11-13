#!/usr/bin/env python3
"""Feature-only original generated portrait motion; approved base PNG is read-only.
Rest cells are exact RGBA copies. Outside each saved binary ROI, every frame is base-identical.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps,ImageChops
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'assets/source_art/yakuza_portrait_motion'
DEST=ROOT/'game/assets/art/yakuza'
REPORT=ROOT/'reports/phases/P03'
EMOTIONS=['neutral','angry']
STATES=['rest','talk','blink']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
base_path=DEST/'portraits.png'
base_sheet=Image.open(base_path).convert('RGBA')
assert base_sheet.size==(800,160)
approved=json.loads((DEST/'atlas.json').read_text())
colors=[tuple(bytes.fromhex(c[1:])) for c in approved['palette']['rgb_hex']]
palette=Image.new('P',(1,1));palette.putpalette([v for rgb in colors for v in rgb]+list(colors[0])*(256-len(colors)))
master_path=SOURCE/'feature_master_v1.png';master=Image.open(master_path).convert('RGBA')
assert master.size==(1254,1254)
cell=627
masks_spec=json.loads((SOURCE/'feature_masks.json').read_text())
sheet=Image.new('RGBA',(480,320))
manifest={'schema':1,'asset_id':'yakuza_present_portrait_motion_p03_v1','status':'DRAFT_REQUIRES_INDEPENDENT_FEATURE_MOTION_REVIEW','file':'portrait_motion.png','dimensions':[480,320],'frame_size':[160,160],'columns':3,'rows':2,'emotions':EMOTIONS,'states':STATES,'fps':{'talk':8,'blink':8},'blink_duration_seconds':0.125,'blink_interval_seconds':4.0,'motion':'No whole-head bob, scale or face swap; only saved mouth/eyelid masks change','source':{'approved_base':'game/assets/art/yakuza/portraits.png','approved_base_sha256':sha(base_path),'master':str(master_path.relative_to(ROOT)),'master_dimensions':[1254,1254],'generated_cell_dimensions':[627,627],'master_sha256':sha(master_path),'prompt':'assets/source_art/yakuza_portrait_motion/feature_prompt.txt','metadata':'assets/source_art/yakuza_portrait_motion/generation_metadata.json','reference':'assets/source_art/yakuza_portrait_motion/feature_reference_board.png','masks':'assets/source_art/yakuza_portrait_motion/feature_masks.json','recipe':'assets/source_art/yakuza_portrait_motion/build_assets.py','mode':'built-in image_gen precise feature edit; no raw photo'},'palette':{'opaque_colors_available':len(colors),'rgb_hex':approved['palette']['rgb_hex']},'frames':[],'animations':{},'review':{'independent_art':'PENDING','actual_dialogue_motion':'PENDING runtime engineer integration','new_identity_or_global_face_changes':False}}
checks=[]
for row,emotion in enumerate(EMOTIONS):
 base=base_sheet.crop((row*160,0,row*160+160,160))
 for col,state in enumerate(STATES):
  frame=base.copy();mask=Image.new('L',(160,160),0)
  if state!='rest':
   spec=masks_spec[emotion][state]
   for polygon in spec['polygons']:ImageDraw.Draw(mask).polygon([tuple(p) for p in polygon],fill=255)
   generated_col=0 if state=='talk' else 1
   sx,sy=generated_col*cell,row*cell
   generated=master.crop((sx,sy,sx+cell,sy+cell)).resize((160,160),Image.Resampling.NEAREST)
   generated=generated.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA')
   # Feature ROIs are within the original fully opaque face; keep original alpha.
   generated.putalpha(base.getchannel('A'))
   offset=tuple(spec['generated_offset'])
   if offset!=(0,0):
    shifted=base.copy();shifted.paste(generated,offset);generated=shifted
   frame.paste(generated,(0,0),mask)
   mask_path=SOURCE/(emotion+'_'+state+'_mask.png');mask.save(mask_path)
  outside=ImageOps.invert(mask)
  assert ImageChops.multiply(ImageChops.difference(frame,base).convert('RGB'),outside.convert('RGB')).getbbox() is None
  assert frame.getchannel('A').tobytes()==base.getchannel('A').tobytes()
  diff_pixels=sum(a!=b for a,b in zip(frame.get_flattened_data(),base.get_flattened_data()))
  assert diff_pixels==0 if state=='rest' else diff_pixels>=20
  sheet.paste(frame,(col*160,row*160))
  frame_info={'id':emotion+'_'+state,'emotion':emotion,'state':state,'rect':[col*160,row*160,160,160],'origin':[80,160],'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest(),'changed_pixels':diff_pixels,'outside_mask_changed_pixels':0,'alpha_matches_approved_base':True,'mask':None if state=='rest' else str(mask_path.relative_to(ROOT)),'mask_sha256':None if state=='rest' else sha(mask_path),'mask_bounds':None if state=='rest' else list(mask.getbbox())}
  manifest['frames'].append(frame_info)
  checks.append({'id':frame_info['id'],'changed_pixels':diff_pixels,'outside_mask_changes':0,'rest_exact_rgba':frame.tobytes()==base.tobytes() if state=='rest' else None,'alpha_unchanged':True})
 manifest['animations'][emotion]={'rest':{'frame':row*3,'fps':0},'talk':{'frames':[row*3,row*3+1],'fps':8,'loop':True},'blink':{'frames':[row*3,row*3+2,row*3],'fps':8,'loop':False}}
out=DEST/'portrait_motion.png';sheet.save(out);sheet.save(SOURCE/'portrait_motion_native_source.png')
manifest['sha256']=sha(out)
manifest['palette']['opaque_colors_used']=len({p[:3] for p in sheet.get_flattened_data() if p[3]})
assert manifest['palette']['opaque_colors_used']<=31
assert set(sheet.getchannel('A').get_flattened_data())=={0,255}
assert all(p==(0,0,0,0) for p in sheet.get_flattened_data() if not p[3])
(DEST/'portrait_motion_atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
preview=Image.new('RGBA',sheet.size)
p=preview.load()
for y in range(preview.height):
 for x in range(preview.width):p[x,y]=(45,80,65,255) if (x//16+y//16)%2 else (210,192,150,255)
preview.alpha_composite(sheet)
preview.resize((960,640),Image.Resampling.NEAREST).convert('RGB').save(REPORT/'portrait_motion_preview_2x.png')
report={'status':'STRUCTURE_AND_FEATURE_MASK_CHECKS_NOT_INDEPENDENT_REVIEW','dimensions':list(sheet.size),'frame_size':[160,160],'alpha':[0,255],'opaque_colors':manifest['palette']['opaque_colors_used'],'sha256':sha(out),'frames':checks,'approved_base_sha256':sha(base_path),'rest_exact':True,'outside_feature_masks_identical':True,'new_approved_likeness_gate_created':False}
(REPORT/'portrait_structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
