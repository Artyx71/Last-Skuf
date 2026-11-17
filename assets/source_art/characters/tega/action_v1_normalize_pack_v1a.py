from pathlib import Path
from PIL import Image
import json,hashlib,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;raw=d/'action_master_v1.png';im=Image.open(raw).convert('RGBA');assert im.size==(1536,1024);mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0);out=im.copy();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert not (d/'action_master_v1a.png').exists();rowcuts=[0]
for boundary in [256,512,768]:
 clear=[y for y in range(boundary-64,boundary+64) if mask.crop((0,y,1536,y+1)).getbbox() is None];assert clear,('No whole-row alpha128 gutter',boundary);rowcuts.append(min(clear,key=lambda y:abs(y-boundary)))
rowcuts.append(1024);ops=[];unchanged=[];accounted=0
for row in range(4):
 band=mask.crop((0,rowcuts[row],1536,rowcuts[row+1]));cuts=[0]
 for boundary in range(192,1536,192):
  clear=[x for x in range(boundary-64,boundary+64) if band.crop((x,0,x+1,band.height)).getbbox() is None];assert clear,('No wholefigure column gutter',row,boundary);cuts.append(min(clear,key=lambda x:abs(x-boundary)))
 cuts.append(1536)
 for col in range(8):
  rect=(cuts[col],rowcuts[row],cuts[col+1],rowcuts[row+1]);region=mask.crop(rect);b=region.getbbox();assert b;box=(cuts[col]+b[0],rowcuts[row]+b[1],cuts[col]+b[2],rowcuts[row]+b[3]);whole=im.crop(box);support=whole.getchannel('A').point(lambda a:255 if a>=128 else 0);accounted+=sum(support.get_flattened_data());original=im.crop((col*192,row*256,(col+1)*192,(row+1)*256));original_count=sum(original.getchannel('A').point(lambda a:255 if a>=128 else 0).get_flattened_data());inside=col*192<box[0] and box[2]<(col+1)*192 and row*256<box[1] and box[3]<(row+1)*256
  if inside and original_count==sum(support.get_flattened_data()):unchanged.append(row*8+col);continue
  scale=min(1.0,184/whole.width,246/whole.height);size=(max(1,int(whole.width*scale)),max(1,int(whole.height*scale)));resized=whole.resize(size,Image.Resampling.NEAREST)
  if scale==1.0 and inside:x=box[0]-col*192;y=box[1]-row*256
  else:x=(192-size[0])//2;y=min(250-size[1],max(3,box[3]-row*256-size[1]))
  cell=Image.new('RGBA',(192,256));cell.paste(resized,(x,y));assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data());out.paste(cell,(col*192,row*256));ops.append({'index':row*8+col,'row':row,'column':col,'clear_row_cuts':rowcuts,'clear_column_cuts':cuts,'complete_source_rect':list(box),'whole_RGBA_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'uniform_NN_scale':scale,'size':size,'placement':[x,y],'resized_RGBA_sha256':hashlib.sha256(resized.tobytes()).hexdigest(),'no_placement_alpha_loss':True})
assert accounted==sum(mask.get_flattened_data()),'All alpha128 support must belong to exactly one whole figure'
for i in unchanged:
 row,col=divmod(i,8);b=(col*192,row*256,(col+1)*192,(row+1)*256);assert im.crop(b).tobytes()==out.crop(b).tobytes()
p=d/'action_master_v1a.png';out.save(p);record={'schema':1,'method':'Whole figures isolated by actual alpha128 clear fullrow/fullcolumn gutters; complete-figure crop/NN scale/translation only, no anatomy/masks/paint/rotation/mirror','raw_sha256':sha(raw),'output_sha256':sha(p),'script_sha256':sha(Path(__file__)),'all_alpha128_support_accounted_before_resize':True,'subthreshold_fringe':'Not opaque support; canonical alpha128 rule preserved','unchanged_raw_cell_indices':unchanged,'operations':ops,'runtime_approval':False,'phase_approval':False};(d/'normalization_v1a.json').write_text(json.dumps(record,indent=2)+'\n');print('Whole-figure normalizations',len(ops),'untouchedcells',len(unchanged),'rowcuts',rowcuts)
s=d/'preview-project/assets/source_art/characters/tega';shutil.copyfile(p,s/p.name);sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as canonical;canonical.ROOT=d/'preview-project';canonical.pack('tega','action','v1a','reference',True)
