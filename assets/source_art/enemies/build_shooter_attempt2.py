#!/usr/bin/env python3
"""ART-P02-02: replace four generated idle poses, preserve other28 frames exactly.
No whole-figure resize. Lower-leg pixel redraw shortens new UP idle shins3rows;
helmet/upper torso/armor masses and boot pixels are translated intact, never scaled.
"""
from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'assets/source_art/enemies'
DEST=ROOT/'game/assets/art/enemies'
REPORT=ROOT/'reports/phases/P02/attempt2'
DIRECTIONS=['down','left','right','up']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
atlas_path=DEST/'atlas.json'
atlas=json.loads(atlas_path.read_text())
before_path=REPORT/'shooter_before.png'
before=Image.open(before_path).convert('RGBA')
master_path=SOURCE/'shooter_master_v2.png'
master=Image.open(master_path).convert('RGBA')
assert master.size==(1536,1024)
colors=[tuple(bytes.fromhex(c[1:])) for c in atlas['palette']['rgb_hex']]
palette=Image.new('P',(1,1));palette.putpalette([v for rgb in colors for v in rgb]+list(colors[0])*(256-len(colors)))
after=before.copy()
patches=[]
for row in [0,3]:
 for col in [0,1]:
  sx,sy=col*192,row*256
  frame=master.crop((sx,sy,sx+192,sy+256))
  frame.putalpha(frame.getchannel('A').point(lambda a:255 if a>=128 else 0))
  frame.paste((0,0,0,0),(0,0),ImageOps.invert(frame.getchannel('A')))
  frame=frame.resize((48,64),Image.Resampling.NEAREST)
  bounds=frame.getbbox();offset=(24-(bounds[0]+bounds[2])//2,58-bounds[3])
  aligned=Image.new('RGBA',(48,64));aligned.paste(frame,offset)
  assert sum(aligned.getchannel('A').get_flattened_data())==sum(frame.getchannel('A').get_flattened_data())
  if row==3:
   # Deliberate anatomical correction at the shins/knees, not uniform scaling:
   # preserve boot/sole rows49..63 and shift intact torso/thigh rows0..45 down3.
   # The3removed rows46..48 are excess lower-leg height in the generated pose.
   redrawn=Image.new('RGBA',(48,64))
   redrawn.paste(aligned.crop((0,0,48,46)),(0,3))
   redrawn.paste(aligned.crop((0,49,48,64)),(0,49))
   aligned=redrawn
  limited=aligned.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA')
  limited.putalpha(aligned.getchannel('A'));limited.paste((0,0,0,0),(0,0),ImageOps.invert(limited.getchannel('A')))
  after.paste(limited,(col*48,row*64))
  patches.append({'direction':DIRECTIONS[row],'column':col,'generated_source_rect':[sx,sy,192,256],'offset_after_nearest':list(offset),'lower_leg_redraw':{'deleted_excess_shin_rows':[46,47,48],'intact_upper_hierarchy_shift':[0,3],'boots_preserved_rows':[49,63]} if row==3 else None})
frames=[];changed=[]
for row,direction in enumerate(DIRECTIONS):
 for col in range(8):
  rect=[col*48,row*64,48,64]
  f=after.crop((rect[0],rect[1],rect[0]+48,rect[1]+64))
  old=before.crop((rect[0],rect[1],rect[0]+48,rect[1]+64))
  if f.tobytes()!=old.tobytes():changed.append([row,col])
  b=f.getbbox();assert b and 0<b[0]<b[2]<48 and 0<b[1]<b[3]==58
  frames.append({'id':f'{direction}_{col}','direction':direction,'column':col,'animation':'idle' if col<2 else 'walk','rect':rect,'origin':[24,58],'bounds':list(b),'rgba_sha256':hashlib.sha256(f.tobytes()).hexdigest()})
assert changed==[[0,0],[0,1],[3,0],[3,1]],changed
assert set(after.getchannel('A').get_flattened_data())=={0,255}
assert all(p==(0,0,0,0) for p in after.get_flattened_data() if not p[3])
assert len({p[:3] for p in after.get_flattened_data() if p[3]})<=64
out=DEST/'shooter_sheet.png';after.save(out)
after.save(SOURCE/'shooter_native_source.png')
after.save(SOURCE/'shooter_pose_redraw_attempt2.png')
after.save(REPORT/'shooter_after.png')
old_shooter=atlas['archetypes']['shooter']
old_shooter['sha256']=sha(out)
old_shooter['frames']=frames
old_shooter['opaque_colors_used']=len({p[:3] for p in after.get_flattened_data() if p[3]})
old_shooter['source']['master']='assets/source_art/enemies/shooter_master_v2.png'
old_shooter['source']['master_sha256']=sha(master_path)
old_shooter['source']['original_master']='assets/source_art/enemies/shooter_master_v1.png'
old_shooter['source']['mode']='built-in precise image_gen edit + selected4cells + native anatomical lower-leg redraw'
old_shooter['source']['prompt']='assets/source_art/enemies/shooter_continuity_prompt.txt'
old_shooter['source']['metadata']='assets/source_art/enemies/shooter_continuity_generation_metadata.json'
old_shooter['source']['recipe']='assets/source_art/enemies/build_shooter_attempt2.py'
old_shooter['source']['recipe_scope']='four down/up idle cells only; other28 native frames byte-identical to FAIL source1786633'
old_shooter['source']['redraw_native']='assets/source_art/enemies/shooter_pose_redraw_attempt2.png'
old_shooter['continuity_fix']={'ticket':'ART-P02-02','status':'DRAFT_REQUIRES_INDEPENDENT_REVIEW','redraws':patches,'whole_figure_resize':False,'unchanged_frames':28}
patch_by_key={(p['direction'],p['column']):p for p in patches}
for adjustment in old_shooter['packing_adjustments']:
 key=(adjustment['direction'],adjustment['column'])
 adjustment['source_master']='assets/source_art/enemies/shooter_master_v2.png' if key in patch_by_key else 'assets/source_art/enemies/shooter_master_v1.png'
 if key in patch_by_key:
  patch=patch_by_key[key]
  adjustment['offset_after_nearest']=patch['offset_after_nearest']
  adjustment['lower_leg_redraw']=patch['lower_leg_redraw']
atlas_path.write_text(json.dumps(atlas,ensure_ascii=False,indent=2)+'\n')
checks={}
for row in [0,3]:
 direction=DIRECTIONS[row]
 oldtop=[];newtop=[]
 for col in range(8):
  oldtop.append(before.crop((col*48,row*64,col*48+48,row*64+64)).getbbox()[1])
  newtop.append(after.crop((col*48,row*64,col*48+48,row*64+64)).getbbox()[1])
 assert abs(newtop[0]-newtop[2])<=2
 checks[direction]={'before_top_y':oldtop,'after_top_y':newtop,'before_idle_to_walk_jump':abs(oldtop[0]-oldtop[2]),'after_idle_to_walk_jump':abs(newtop[0]-newtop[2])}
report={'ticket':'ART-P02-02','status':'STRUCTURAL_CHECK_ONLY_PENDING_REAL_ANIMATION_REVIEW','sha256':sha(out),'dimensions':[384,256],'alpha':[0,255],'colors':old_shooter['opaque_colors_used'],'changed_cells':changed,'unchanged_native_frames':28,'whole_figure_resize':False,'head_top_metrics':checks}
(REPORT/'shooter_structure.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
# Before/after4x comparison: down idle0/walk2; up idle0/walk2, exact same anchor.
preview=Image.new('RGBA',(192,256),(36,40,53,255))
for version,image in enumerate([before,after]):
 for row_index,row in enumerate([0,3]):
  for col_index,col in enumerate([0,2]):
   f=image.crop((col*48,row*64,col*48+48,row*64+64))
   preview.alpha_composite(f,((version*2+col_index)*48,row_index*128))
preview.resize((768,1024),Image.Resampling.NEAREST).convert('RGB').save(REPORT/'shooter_before_after_4x.png')
print(json.dumps(report,indent=2))
