from pathlib import Path
from PIL import Image
from collections import deque
import json,hashlib,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;old_dir=d.parent/'moving-shot-v1';raw=d/'up_fullposes_master_v2.png';old=old_dir/'moving_shot_master_v1.png';im=Image.open(raw).convert('RGBA');mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0);data=bytes(mask.get_flattened_data());width,height=im.size;seen=bytearray(width*height);components=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for start,alpha in enumerate(data):
 if not alpha or seen[start]:continue
 q=deque([start]);seen[start]=1;x0=x1=start%width;y0=y1=start//width;area=0
 while q:
  i=q.popleft();x=i%width;y=i//width;area+=1;x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
  for j in ([i-1] if x else [])+([i+1] if x+1<width else [])+([i-width] if y else [])+([i+width] if y+1<height else []):
   if data[j] and not seen[j]:seen[j]=1;q.append(j)
 components.append({'area':area,'box':[x0,y0,x1+1,y1+1]})
assert len(components)==6 and sum(c['area'] for c in components)*255==sum(data)
figures=sorted([dict(c,components=[c.copy()]) for c in components if c['area']>1000],key=lambda c:c['box'][0]);assert len(figures)==5
for c in components:
 if c['area']>1000:continue
 b=c['box'];owners=[g for g in figures if g['box'][0]<=b[0] and g['box'][1]<=b[1] and g['box'][2]>=b[2] and g['box'][3]>=b[3]];assert len(owners)==1,'Tiny component must be inside exactly one whole figure rectangle, never discarded';owners[0]['area']+=c['area'];owners[0]['components'].append(c)
base=Image.open(old).convert('RGBA');assert base.size==(1536,1024);out=base.copy();layout=json.loads((old_dir/'preview-project/assets/source_art/characters/pasha/moving_shot_manifest_v1.json').read_text());operations=[]
for n,figure in enumerate(figures):
 index=26+n;col=index%8;box=figure['box'];assert sum(mask.crop(box).get_flattened_data())//255==figure['area'],'Whole rectangle cannot contain neighbour pixels';assert box[0]>0 and box[1]>0 and box[2]<width and box[3]<height
 whole=im.crop(box);reference=layout['frames'][index]['source_opaque_bounds'];target_height=reference[3]-reference[1];scale=min(target_height/whole.height,176/whole.width,224/whole.height);size=(round(whole.width*scale),round(whole.height*scale));x=round((reference[0]+reference[2]-size[0])/2);y=reference[3]-size[1];small=whole.resize(size,Image.Resampling.NEAREST);cell=Image.new('RGBA',(192,256));assert x>0 and y>0 and x+size[0]<192 and y+size[1]<256;cell.paste(small,(x,y));assert sum(cell.getchannel('A').get_flattened_data())==sum(small.getchannel('A').get_flattened_data());out.paste(cell,(col*192,3*256));operations.append({'index':index,'new_whole_rectangle':box,'all_support_inside_pure_rectangle':figure['area'],'whole_rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'uniform_NN_scale':scale,'size':size,'placement':[x,y],'reference_old_bounds':reference,'no_placement_alpha_loss':True})
unchanged=[i for i in range(32) if i not in range(26,31)]
for i in unchanged:
 row,col=divmod(i,8);box=(col*192,row*256,(col+1)*192,(row+1)*256);assert base.crop(box).tobytes()==out.crop(box).tobytes()
master=d/'moving_shot_master_v2a.png';assert not master.exists();out.save(master)
record={'schema':1,'method':'Five entirely NEW image_gen whole UP poses replace26..30. Whole rectangular crops + uniform NN/translation ONLY, no bodypart painting/masks/rotation/mirroring. All6 raw support components retained in5whole figures; tinyhair insidefirstfigure bbox retained. Other27rawcells exact.','raw_size':list(im.size),'new_raw_sha256':sha(raw),'old_master_sha256':sha(old),'master_sha256':sha(master),'script_sha256':sha(Path(__file__)),'all_raw_support_components':components,'whole5_figure_groups':figures,'operations':operations,'unchanged_raw_cell_indices':unchanged,'old_replaced_poses_preserved_in_original_raw':True,'runtime_approval':False,'phase_approval':False};(d/'assembly_v2a.json').write_text(json.dumps(record,indent=2)+'\n')
s=d/'preview-project/assets/source_art/characters/pasha';s.mkdir(parents=True,exist_ok=False);shutil.copyfile(master,s/master.name);sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as canonical;canonical.ROOT=d/'preview-project';canonical.MAPS['moving_shot']={'moving_shot':list(range(8))};canonical.pack('pasha','moving_shot','v2a','reference',True);print('27exact rawcells;5new complete UPfigures, originalfailed sheet preserved')
