from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';SRC=WORK/'assets/source_art/characters/ryzhik';OUT=ROOT/'reports/phases/P06/art-preflight';PFX='ryzhik_world_preflight_v2d';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest();old=Image.open(SRC/'world_master_v1.png').convert('RGBA');final=Image.open(SRC/'world_master_v2d.png').convert('RGBA');stages=[]
for version in ['v2a','v2b','v2c','v2d']:
 data=json.loads((SRC/f'world_{version}_assembly.json').read_text());base=Image.open(WORK/data['base']).convert('RGBA');pose=Image.open(WORK/data['pose']).convert('RGBA');reference=Image.open(WORK/data['reference']).convert('RGBA');assert sha(WORK/data['base'])==data['base_sha256'];assert sha(WORK/data['pose'])==data['pose_sha256'];assert sha(WORK/data['reference'])==data['reference_sha256'];bounds=pose.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox();assert list(bounds)==data['complete_figure_bounds'];rr,rc=data['reference_cell'];ref=reference.crop((rc*192,rr*256,(rc+1)*192,(rr+1)*256));refb=ref.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox();assert list(refb)==data['reference_bounds'];height=refb[3]-refb[1];scale=height/(bounds[3]-bounds[1]);width=round((bounds[2]-bounds[0])*scale);assert abs(scale-data['uniform_scale'])<1e-12 and [width,height]==data['resized_complete_figure'];resized=pose.crop(bounds).resize((width,height),Image.Resampling.NEAREST);assert rgba(resized)==data['resized_rgba_sha256'];cell=Image.new('RGBA',(192,256));cell.paste(resized,tuple(data['placement']));assert rgba(cell)==data['output_cell_rgba_sha256'];assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data());row,col=data['changed_cell'];rebuilt=base.copy();rebuilt.paste(cell,(col*192,row*256));actual=Image.open(SRC/f'world_master_{version}.png').convert('RGBA');assert rebuilt.tobytes()==actual.tobytes();assert sha(SRC/f'world_master_{version}.png')==data['output_sha256'];changed=[]
 for index in range(32):
  r,c=divmod(index,8);box=(c*192,r*256,(c+1)*192,(r+1)*256)
  if actual.crop(box).tobytes()!=base.crop(box).tobytes():changed.append(index)
 assert changed==[row*8+col];stages.append({'version':version,'changed':changed,'canvas':pose.size,'support_bounds':bounds,'resize':[width,height],'placement':data['placement'],'source_exact_reconstruction':True,'other31_exact':True,'resized_alpha_placement_loss':0})
changed=[]
for index in range(32):
 row,col=divmod(index,8);box=(col*192,row*256,(col+1)*192,(row+1)*256)
 if old.crop(box).tobytes()!=final.crop(box).tobytes():changed.append(index)
assert changed==[12,15,20,23]
# Verify fullcell source reference NN4 mappings independently from provenance.
refs=json.loads((SRC/'world_isolated_v2_references.json').read_text());print('reference schema',type(refs).__name__,str(refs)[:700])
metrics=json.loads((OUT/f'{PFX}_metrics.json').read_text());metrics.update(whole_figure_stages=stages,final_changed_from_v1=changed,other28_source_exact=True)
# Common complete-cell comparison own A, previous B, final B, own idle per side/contact.
for row,direction in [(1,'left'),(2,'right')]:
 board=Image.new('RGB',(4*384,2*550),'#eeeeee');draw=ImageDraw.Draw(board)
 for group,(a,b) in enumerate([(2,4),(6,7)]):
  for col,(version,c) in enumerate([('v1',a),('v1',b),('v2d',b),('v1',0)]):
   im=Image.open(SRC/f'world_native_{version}.png').convert('RGBA');cell=im.crop((c*48,row*64,c*48+48,row*64+64));bg=Image.new('RGBA',(48,64),'#eeeeee');bg.alpha_composite(cell);board.paste(bg.resize((384,512),Image.Resampling.NEAREST).convert('RGB'),(col*384,group*550+25));draw.text((col*384+4,group*550+5),f'{direction} {version} col{c}',fill='black')
 board.save(OUT/f'{PFX}_{direction}_before_after_family.png')
(OUT/f'{PFX}_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('4normalized stages exact; changed final',changed)
