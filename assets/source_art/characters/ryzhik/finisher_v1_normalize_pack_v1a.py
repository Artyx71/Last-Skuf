from pathlib import Path
from PIL import Image
import hashlib,json,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;raw=d/'finisher_master_v1.png';im=Image.open(raw).convert('RGBA');out=im.copy();ops=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (d/'finisher_master_v1a.png').exists()
for row in range(4):
 strip=im.crop((0,row*256,1536,(row+1)*256));a=strip.getchannel('A').point(lambda x:255 if x>=128 else 0);cuts=[0]
 for i in range(1,8):
  clear=[x for x in range(i*192-60,i*192+60) if a.crop((x,0,x+1,256)).getbbox() is None];assert clear,('No unambiguous wholefigure gutter',row,i)
  cuts.append(min(clear,key=lambda x:abs(x-i*192)))
 cuts.append(1536);assert cuts==sorted(cuts)
 for col in range(8):
  region=strip.crop((cuts[col],0,cuts[col+1],256));bbox=region.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox();assert bbox
  rect=(cuts[col]+bbox[0],bbox[1],cuts[col]+bbox[2],bbox[3]);whole=strip.crop(rect)
  original=im.crop((col*192,row*256,(col+1)*192,(row+1)*256));cellbounds=original.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox()
  # Keep only when complete own figure is within cell and cell has no neighbour.
  if rect[0]>col*192 and rect[2]<(col+1)*192 and rect[1]>0 and rect[3]<256 and sum(original.getchannel('A').point(lambda x:255 if x>=128 else 0).get_flattened_data())==sum(whole.getchannel('A').point(lambda x:255 if x>=128 else 0).get_flattened_data()):continue
  scale=min(1.0,184/whole.width,246/whole.height);size=(max(1,int(whole.width*scale)),max(1,int(whole.height*scale)));resized=whole.resize(size,Image.Resampling.NEAREST);x=(192-size[0])//2;y=min(250-size[1],max(3,rect[3]-size[1]));cell=Image.new('RGBA',(192,256));cell.paste(resized,(x,y));assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data());out.paste(cell,(col*192,row*256));ops.append({'row':row,'col':col,'cuts':cuts,'complete_source_rect':list(rect),'whole_rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'scale':scale,'size':size,'placement':[x,y],'placement_alpha_loss':False})
path=d/'finisher_master_v1a.png';out.save(path);report={'schema':1,'raw_sha256':sha(raw),'output_sha256':sha(path),'script_sha256':sha(Path(__file__)),'method':'Entire figures isolated only by actual fullrow clear vertical gutters; uniform NN scale/translation; no anatomy/masks/painting/rotation/mirror','operations':ops,'other_cells_byte_exact':32-len(ops),'phase_approval':False,'runtime_approval':False};(d/'normalization_v1a.json').write_text(json.dumps(report,indent=2)+'\n');print('NORMALIZED',len(ops),'whole figures')
s=d/'preview-project/assets/source_art/characters/ryzhik';shutil.copyfile(path,s/path.name);sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as p;p.ROOT=d/'preview-project';p.pack('ryzhik','finisher','v1a','reference',True)
