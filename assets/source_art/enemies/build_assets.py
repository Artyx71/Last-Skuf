#!/usr/bin/env python3
"""Pack original image_gen enemy pixel drawings; never reads private photographs.
Pillow13 recipe: .tools/art-venv/bin/python assets/source_art/enemies/build_assets.py
"""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'assets/source_art/enemies'
DEST=ROOT/'game/assets/art/enemies'
REPORT=ROOT/'reports/phases/P02'
ROLES=['patrol','rusher','shooter']
DIRECTIONS=['down','left','right','up']
PALETTE_HEX=[
 '08080d','111019','1b1925','252234','343044','45415a','5c5974','77758c',
 '1e2430','303a4c','45566a','697e90','8fa8b8','c4d6d6',
 '714c4b','a46c5c','c99580','e5bba3',
 '065666','107b8a','20afba','51d3d3','a5f5e7',
 '6a2d20','a9471d','d9651c','ef8b28','ffba55',
 '431d32','6f2b43','9c405a','c85d70','f58691','d6424a','ee5a65',
]
COLORS=[tuple(bytes.fromhex(c)) for c in PALETTE_HEX]
palette=Image.new('P',(1,1))
palette.putpalette([v for rgb in COLORS for v in rgb]+list(COLORS[0])*(256-len(COLORS)))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hard_alpha(im):
 im=im.convert('RGBA')
 im.putalpha(im.getchannel('A').point(lambda a:255 if a>=128 else 0))
 im.paste((0,0,0,0),(0,0),ImageOps.invert(im.getchannel('A')))
 return im
def color_limit(im):
 result=im.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA')
 result.putalpha(im.getchannel('A'))
 result.paste((0,0,0,0),(0,0),ImageOps.invert(result.getchannel('A')))
 return result
def preview(im):
 result=Image.new('RGBA',im.size)
 p=result.load()
 for y in range(im.height):
  for x in range(im.width):p[x,y]=(45,80,65,255) if (x//16+y//16)%2 else (210,192,150,255)
 result.alpha_composite(im)
 return result.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).convert('RGB')
manifest={
 'asset_id':'fictional_security_p02_v1','version':1,'status':'DRAFT_REQUIRES_INDEPENDENT_ART_REVIEW',
 'author':'Codex art production with built-in image_gen; deterministic Pillow13 technical packing',
 'original_designs':True,'identity_references':[],
 'style_reference':{'path':'game/assets/art/yakuza/world_sheet.png','sha256':sha(ROOT/'game/assets/art/yakuza/world_sheet.png'),'role':'approved original project art style/camera/scale only; no identity copying'},
 'dimensions':[384,256],'frame_size':[48,64],'columns':8,'rows':4,'directions':DIRECTIONS,'pivot':[24,58],
 'animations':{'idle':{'columns':[0,1],'fps':3,'loop':True},'walk':{'columns':[2,3,4,5,6,7],'fps':8,'loop':True}},
 'palette':{'opaque_colors_available':len(COLORS),'rgb_hex':['#'+c for c in PALETTE_HEX]},
 'packing':{'alpha_threshold':128,'sample':'NEAREST 192x256 generated cells to48x64 native','palette':'intentional35 opaque colors, nearest RGB, no dither','anchor':'x24 centered silhouette; bottom sole58, no opacity clipping','recipe':'assets/source_art/enemies/build_assets.py'},
 'review':{'independent_art':'PENDING','actual_animation':'PENDING root/gameplay Godot replay','limitations':['Minor pose/helmet-volume jitter may remain between generated walk frames.','Down-view shooter holds pistol diagonally across chest; attack telegraph/muzzle direction must be shown by gameplay code.','No dedicated attack/hurt/death frames requested; pack provides idle/walk for combat prototype.']},
 'archetypes':{}
}
check={'status':'STRUCTURAL_CHECKS_ONLY_NOT_ART_APPROVAL','archetypes':{}}
designs={
 'patrol':'Sturdy protective navy vest, squared shoulders, round opaque helmet, cyan visor/fasteners, baton and belt pouch.',
 'rusher':'Slim agile hooded runner, orange cropped windbreaker and back yoke, narrow mask/visor, light shoes and baton.',
 'shooter':'Angular compact helmet and shoulder armor, crimson chest/back plates, red visor, pistol held with both hands.'}
for role in ROLES:
 master_path=SOURCE/(role+'_master_v1.png')
 master=Image.open(master_path).convert('RGBA')
 assert master.size==(1536,1024)
 sheet=Image.new('RGBA',(384,256))
 frames=[]
 adjustments=[]
 for row,direction in enumerate(DIRECTIONS):
  for col in range(8):
   sx,sy=col*192,row*256
   frame=hard_alpha(master.crop((sx,sy,sx+192,sy+256))).resize((48,64),Image.Resampling.NEAREST)
   box=frame.getbbox()
   assert box is not None
   offset=(24-(box[0]+box[2])//2,58-box[3])
   aligned=Image.new('RGBA',(48,64))
   aligned.paste(frame,offset)
   assert sum(aligned.getchannel('A').get_flattened_data())==sum(frame.getchannel('A').get_flattened_data()), 'opaque pixels clipped'
   aligned=color_limit(aligned)
   box=aligned.getbbox()
   assert 0<box[0]<box[2]<48 and 0<box[1]<box[3]==58
   rect=[col*48,row*64,48,64]
   frames.append({'id':f'{direction}_{col}','direction':direction,'column':col,'animation':'idle' if col<2 else 'walk','rect':rect,'origin':[24,58],'bounds':list(box),'rgba_sha256':hashlib.sha256(aligned.tobytes()).hexdigest()})
   adjustments.append({'direction':direction,'column':col,'source_rect':[sx,sy,192,256],'offset_after_nearest':list(offset)})
   sheet.paste(aligned,(col*48,row*64))
 distinct={direction:len({f['rgba_sha256'] for f in frames if f['direction']==direction and f['column']>=2}) for direction in DIRECTIONS}
 assert all(count>=4 for count in distinct.values())
 assert set(sheet.getchannel('A').get_flattened_data())=={0,255}
 assert all(p==(0,0,0,0) for p in sheet.get_flattened_data() if p[3]==0)
 out_path=DEST/(role+'_sheet.png')
 sheet.save(out_path)
 sheet.save(SOURCE/(role+'_native_source.png'))
 preview(sheet).save(REPORT/(role+'_preview_3x.png'))
 colors=len({p[:3] for p in sheet.get_flattened_data() if p[3]})
 assert colors<=64
 manifest['archetypes'][role]={'file':out_path.name,'dimensions':[384,256],'frame_size':[48,64],'pivot':[24,58],'design':designs[role],'sha256':sha(out_path),'opaque_colors_used':colors,'frames':frames,'source':{'master':str(master_path.relative_to(ROOT)),'master_dimensions':list(master.size),'master_sha256':sha(master_path),'prompt':'assets/source_art/enemies/'+role+'_prompt.txt','metadata':'assets/source_art/enemies/'+role+'_generation_metadata.json','mode':'built-in image_gen','input_reference':'approved original Yakudza pixel sheet only; no photographs'},'packing_adjustments':adjustments}
 check['archetypes'][role]={'file':str(out_path.relative_to(ROOT)),'dimensions':list(sheet.size),'alpha_values':[0,255],'opaque_colors':colors,'frame_count':len(frames),'distinct_walk_frames_by_direction':distinct,'sole_bottoms':[58],'bounds_x':[min(f['bounds'][0] for f in frames),max(f['bounds'][2] for f in frames)],'bounds_y':[min(f['bounds'][1] for f in frames),58],'sha256':sha(out_path),'master_corner_rgba':[list(master.getpixel(p)) for p in [(0,0),(100,10),(500,10)]]}
(DEST/'atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(REPORT/'enemy_art_structural_check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(check,ensure_ascii=False,indent=2))
