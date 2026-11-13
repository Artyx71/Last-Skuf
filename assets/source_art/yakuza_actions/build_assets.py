#!/usr/bin/env python3
"""Pack generated Yakudza action drawings; approved P01 files are read-only inputs."""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'assets/source_art/yakuza_actions'
DEST=ROOT/'game/assets/art/yakuza'
REPORT=ROOT/'reports/phases/P02'
DIRECTIONS=['down','left','right','up']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
# Existing approved atlas is only READ; its palette preserves exact character colors.
approved=json.loads((DEST/'atlas.json').read_text())
colors=[tuple(bytes.fromhex(c[1:])) for c in approved['palette']['rgb_hex']]
palette=Image.new('P',(1,1))
palette.putpalette([v for color in colors for v in color]+list(colors[0])*(256-len(colors)))
master_path=SOURCE/'actions_master_v2.png'
master=Image.open(master_path).convert('RGBA')
assert master.size==(1536,1024)
sheet=Image.new('RGBA',(384,256))
frames=[]
adjustments=[]
for row,direction in enumerate(DIRECTIONS):
 for col in range(8):
  sx,sy=col*192,row*256
  image=master.crop((sx,sy,sx+192,sy+256))
  image.putalpha(image.getchannel('A').point(lambda a:255 if a>=128 else 0))
  image.paste((0,0,0,0),(0,0),ImageOps.invert(image.getchannel('A')))
  master_bounds=image.getbbox()
  assert master_bounds and 0<master_bounds[0]<master_bounds[2]<192 and 0<master_bounds[1]<master_bounds[3]<256, 'source pose touches cell edge'
  image=image.resize((48,64),Image.Resampling.NEAREST)
  box=image.getbbox()
  offset=(24-(box[0]+box[2])//2,58-box[3])
  aligned=Image.new('RGBA',(48,64));aligned.paste(image,offset)
  assert sum(aligned.getchannel('A').get_flattened_data())==sum(image.getchannel('A').get_flattened_data()), 'opaque pixels clipped'
  limited=aligned.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA')
  limited.putalpha(aligned.getchannel('A'))
  limited.paste((0,0,0,0),(0,0),ImageOps.invert(limited.getchannel('A')))
  box=limited.getbbox()
  assert 0<box[0]<box[2]<48 and 0<box[1]<box[3]==58
  action='melee' if col<=2 else 'hit' if col<=4 else 'death'
  frames.append({'id':f'{action}_{direction}_{col}','direction':direction,'column':col,'animation':action,'rect':[col*48,row*64,48,64],'origin':[24,58],'bounds':list(box),'rgba_sha256':hashlib.sha256(limited.tobytes()).hexdigest()})
  adjustments.append({'direction':direction,'column':col,'source_rect':[sx,sy,192,256],'source_bounds':list(master_bounds),'offset_after_nearest':list(offset)})
  sheet.paste(limited,(col*48,row*64))
out_path=DEST/'action_sheet.png'
sheet.save(out_path)
sheet.save(SOURCE/'actions_native_source.png')
assert set(sheet.getchannel('A').get_flattened_data())=={0,255}
assert all(p==(0,0,0,0) for p in sheet.get_flattened_data() if p[3]==0)
used_colors=len({p[:3] for p in sheet.get_flattened_data() if p[3]})
assert used_colors<=31
unique={direction:len({f['rgba_sha256'] for f in frames if f['direction']==direction}) for direction in DIRECTIONS}
assert all(count==8 for count in unique.values())
manifest={'asset_id':'yakuza_p02_actions_v1','version':1,'status':'DRAFT_REQUIRES_INDEPENDENT_ACTION_REVIEW','file':'action_sheet.png','dimensions':[384,256],'frame_size':[48,64],'columns':8,'rows':4,'directions':DIRECTIONS,'pivot':[24,58],'palette':{'opaque_colors_used':used_colors,'source':'read-only approved atlas.json shared palette','rgb_hex':approved['palette']['rgb_hex']},'animations':{'melee':{'description':'Weak short right-hand shove, phone held in left hand','columns':[0,1,2],'fps':12,'loop':False,'contact_column':1},'hit':{'columns':[3,4],'fps':12,'loop':False},'death':{'description':'Three fall stages; column7 lying still','columns':[5,6,7],'fps':12,'loop':False,'hold_final_column':7}},'frames':frames,'sha256':sha(out_path),'source':{'mode':'built-in image_gen then targeted built-in edit','master':str(master_path.relative_to(ROOT)),'master_sha256':sha(master_path),'original_master':'assets/source_art/yakuza_actions/actions_master_v1.png','prompts':['assets/source_art/yakuza_actions/action_prompt.txt','assets/source_art/yakuza_actions/cleanup_prompt.txt'],'metadata':['assets/source_art/yakuza_actions/generation_metadata.json','assets/source_art/yakuza_actions/cleanup_metadata.json'],'recipe':'assets/source_art/yakuza_actions/build_assets.py','references':[{'path':str(path.relative_to(ROOT)),'sha256':sha(path),'role':'approved original project artwork, identity/style/scale'} for path in [DEST/'world_sheet.png',DEST/'portraits.png']],'private_photo_input':False},'packing':{'alpha_threshold':128,'sample':'NEAREST','palette':'same31 colors as approved P01; nearest RGB, no dithering','pose_adjustments':adjustments},'review':{'independent_art':'PENDING','actual_animation':'PENDING root/gameplay Godot replay','known_limitations':['Phone may be partially occluded behind near arm in right-facing shove contact pose.','Generator slightly varies body/hair volume; left fall poses were redrawn more compactly to avoid source clipping.','Fall animation has only3 key poses; code should hold the final lying frame.']}}
manifest['animation_timing_rationale']='Matches combat_player.gd runtime12FPS; three fall poses fit automatic retry250ms. Nonloop and final fallen hold until reset.'
(DEST/'actions_atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
background=Image.new('RGBA',sheet.size)
p=background.load()
for y in range(background.height):
 for x in range(background.width):p[x,y]=(45,80,65,255) if (x//16+y//16)%2 else (210,192,150,255)
background.alpha_composite(sheet)
background.resize((1152,768),Image.Resampling.NEAREST).convert('RGB').save(REPORT/'yakuza_action_preview_3x.png')
check={'status':'STRUCTURAL_CHECKS_ONLY_NOT_ACTION_ART_APPROVAL','file':str(out_path.relative_to(ROOT)),'dimensions':list(sheet.size),'alpha_values':[0,255],'opaque_colors':used_colors,'frame_count':len(frames),'unique_frames_by_direction':unique,'sole_bottoms':[58],'bounds_x':[min(f['bounds'][0] for f in frames),max(f['bounds'][2] for f in frames)],'bounds_y':[min(f['bounds'][1] for f in frames),58],'sha256':sha(out_path),'source_cell_edges_clear':True,'opaque_pixels_clipped_during_packing':False,'master_corner_rgba':[list(master.getpixel(p)) for p in [(0,0),(100,10),(500,10)]]}
(REPORT/'yakuza_action_structural_check.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(check,ensure_ascii=False,indent=2))
