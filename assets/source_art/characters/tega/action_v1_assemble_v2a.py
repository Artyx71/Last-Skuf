from pathlib import Path
from PIL import Image
from collections import deque
import json,hashlib,sys,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;raw=d/'action_master_v1.png';replacement=d.parent/'action-left-fire-v2/left_fire_master_v2.png';im=Image.open(raw).convert('RGBA');mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0);data=bytes(mask.get_flattened_data());width,height=im.size;assert (width,height)==(1536,1024);seen=bytearray(width*height);components=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
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
assert not (d/'action_master_v2a.png').exists();out=im.copy();ops=[];unchanged=[];replaced=[]
for row in range(4):
 for col in range(8):
  old=slots[(row,col)];box=old['box'];support_count=sum(mask.crop(box).get_flattened_data())//255;original=im.crop((col*192,row*256,(col+1)*192,(row+1)*256));original_support=sum(original.getchannel('A').point(lambda a:255 if a>=128 else 0).get_flattened_data())//255
  if (row,col)==(1,7):
   figure=Image.open(replacement).convert('RGBA');b=figure.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert b and b[0]>0 and b[1]>0 and b[2]<figure.width and b[3]<figure.height;whole=figure.crop(b);ref=slots[(1,0)]['box'];scale=min((ref[3]-ref[1])/whole.height,176/whole.width,224/whole.height);size=(round(whole.width*scale),round(whole.height*scale));x=(192-size[0])//2;y=ref[3]-256-size[1];replaced.append({'index':15,'old_component_box':box,'contaminated_old_bbox_extra_support':support_count-old['area'],'old_figure_NOT_cropped_or_masked':True,'new_complete_figure_bounds':list(b),'source_sha256':sha(replacement)})
  else:
   assert support_count==old['area'],('No neighbour pixels allowed in complete rectangular crop',row,col,support_count-old['area']);inside=col*192<box[0] and box[2]<(col+1)*192 and row*256<box[1] and box[3]<(row+1)*256
   if inside and original_support==old['area']:unchanged.append(row*8+col);continue
   whole=im.crop(box);scale=min(1.0,184/whole.width,246/whole.height);size=(max(1,int(whole.width*scale)),max(1,int(whole.height*scale)))
   if scale==1.0 and inside:x=box[0]-col*192;y=box[1]-row*256
   else:x=(192-size[0])//2;y=min(250-size[1],max(3,box[3]-row*256-size[1]))
  resized=whole.resize(size,Image.Resampling.NEAREST);cell=Image.new('RGBA',(192,256));assert x>0 and y>0 and x+size[0]<192 and y+size[1]<256;cell.paste(resized,(x,y));assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data());out.paste(cell,(col*192,row*256));ops.append({'index':row*8+col,'row':row,'column':col,'whole_figure_rectangle_from_old_raw':box if (row,col)!=(1,7) else None,'old_support_area':old['area'],'whole_RGBA_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'uniform_NN_scale':scale,'size':size,'placement':[x,y],'resized_RGBA_sha256':hashlib.sha256(resized.tobytes()).hexdigest(),'no_placement_alpha_loss':True})
for i in unchanged:
 row,col=divmod(i,8);b=(col*192,row*256,(col+1)*192,(row+1)*256);assert im.crop(b).tobytes()==out.crop(b).tobytes()
p=d/'action_master_v2a.png';out.save(p);record={'schema':1,'method':'Whole rectangular figure crops only; support components used ONLY as bbox analysis, never image masks. All31 retained complete rectangles contain exactly their own full support; contaminatedLEFT7 replaced by entirely new image_gen fullpose. Uniform NN/translation only; no bodypart editing/painting/mirroring/rotation.','support_alpha_threshold':128,'raw_sha256':sha(raw),'new_left_fire_sha256':sha(replacement),'master_sha256':sha(p),'script_sha256':sha(Path(__file__)),'all32_raw_support_components':components,'all_raw_support_accounted':True,'unchanged_raw_cell_indices':unchanged,'operations':ops,'replaced_whole_figures':replaced,'all31_original_figures_retained_whole':True,'runtime_approval':False,'phase_approval':False};(d/'assembly_v2a.json').write_text(json.dumps(record,indent=2)+'\n');s=d/'preview-project/assets/source_art/characters/tega';shutil.copyfile(p,s/p.name);sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as canonical;canonical.ROOT=d/'preview-project';canonical.pack('tega','action','v2a','reference',True);print('Rawcellsunchanged',len(unchanged),'whole technicalnormalizations+one newfigure',len(ops))
