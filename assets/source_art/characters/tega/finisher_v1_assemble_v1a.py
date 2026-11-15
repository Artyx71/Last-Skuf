from pathlib import Path
from PIL import Image
from collections import deque
import json,hashlib,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;raw=d/'finisher_master_v1.png';replacement=d.parent/'action-left-fire-v2/left_fire_master_v2.png';im=Image.open(raw).convert('RGBA');mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0);data=bytes(mask.get_flattened_data());width,height=im.size;assert (width,height)==(1536,1024);seen=bytearray(width*height);components=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Analysis finds complete rectangles only. NO silhouette/component masks are
# pasted or edited; contaminated rectangle LEFT7 is explicitly NOT reused.
for start,alpha in enumerate(data):
 if not alpha or seen[start]:continue
 q=deque([start]);seen[start]=1;x0=x1=start%width;y0=y1=start//width;area=0
 while q:
  i=q.popleft();x=i%width;y=i//width;area+=1;x0=min(x0,x);x1=max(x1,x);y0=min(y0,y);y1=max(y1,y)
  for j in ([i-1] if x else [])+([i+1] if x+1<width else [])+([i-width] if y else [])+([i+width] if y+1<height else []):
   if data[j] and not seen[j]:seen[j]=1;q.append(j)
 components.append({'area':area,'box':[x0,y0,x1+1,y1+1]})
assert len(components)==32,('Complete32figures required; no discarded components',len(components));assert sum(c['area'] for c in components)*255==sum(data)
slots={}
for c in components:
 x0,y0,x1,y1=c['box'];key=(int((y0+y1-1)/2)//256,int((x0+x1-1)/2)//192);assert key not in slots;slots[key]=c
assert set(slots)=={(row,col) for row in range(4) for col in range(8)}

out=im.copy();ops=[];unchanged=[]
for (row,col),c in sorted(slots.items()):
 box=c['box'];assert sum(mask.crop(box).get_flattened_data())//255==c['area'],('Neighbour pixels in rectangle',row,col)
 cellbox=(col*192,row*256,(col+1)*192,(row+1)*256);original=im.crop(cellbox)
 inside=cellbox[0]<box[0] and box[2]<cellbox[2] and cellbox[1]<box[1] and box[3]<cellbox[3]
 if inside and sum(original.getchannel('A').point(lambda a:255 if a>=128 else 0).get_flattened_data())//255==c['area']:
  unchanged.append(row*8+col);continue
 whole=im.crop(box);scale=min(1.0,184/whole.width,246/whole.height);size=(int(whole.width*scale),int(whole.height*scale));small=whole.resize(size,Image.Resampling.NEAREST)
 x=(192-size[0])//2;y=min(250-size[1],max(3,box[3]-row*256-size[1]))
 cell=Image.new('RGBA',(192,256));cell.paste(small,(x,y));assert x>0 and y>0 and x+size[0]<192 and y+size[1]<256
 assert sum(cell.getchannel('A').get_flattened_data())==sum(small.getchannel('A').get_flattened_data())
 out.paste(cell,(col*192,row*256));ops.append({'index':row*8+col,'whole_rectangle':box,'uniform_NN_scale':scale,'size':size,'placement':[x,y],'whole_rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'no_placement_alpha_loss':True})
for i in unchanged:
 row,col=divmod(i,8);box=(col*192,row*256,(col+1)*192,(row+1)*256);assert out.crop(box).tobytes()==im.crop(box).tobytes()
master=d/'finisher_master_v1a.png';assert not master.exists();out.save(master)
(d/'assembly_v1a.json').write_text(json.dumps({'schema':1,'method':'Complete rectangular RGBA figures only. Components used only to locate whole pure rectangles; all32 raw support components retained. No silhouette masks, anatomy editing, painting, rotation or mirroring.','raw_sha256':sha(raw),'master_sha256':sha(master),'script_sha256':sha(Path(__file__)),'all32_raw_components':components,'unchanged_raw_cells':unchanged,'operations':ops,'runtime_approval':False,'phase_approval':False},indent=2)+'\n')
source=d/'preview-project/assets/source_art/characters/tega';shutil.copyfile(master,source/master.name);sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as canonical;canonical.ROOT=d/'preview-project';canonical.pack('tega','finisher','v1a','reference',True);print('Exact raw cells',len(unchanged),'whole figure fits',len(ops))
