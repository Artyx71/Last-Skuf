from pathlib import Path
from PIL import Image
import json,hashlib
D=Path(__file__).parent
src=D/'action_master_v1.png';out=D/'action_master_v1a.png';assert not out.exists()
im=Image.open(src).convert('RGBA');assert im.size==(1536,1024)
mask=im.getchannel('A').point(lambda a:255 if a>=128 else 0)
result=im.copy();ops=[]
for row in [1,3]:
 # Both complete figures are separated by an actually empty vertical gutter.
 empty=[x for x in range(1110,1180) if mask.crop((x,row*256,x+1,(row+1)*256)).getbbox() is None]
 runs=[]
 for x in empty:
  if not runs or x!=runs[-1][-1]+1:runs.append([x])
  else:runs[-1].append(x)
 run=min(runs,key=lambda xs:abs(sum(xs)/len(xs)-1152));split=run[len(run)//2]
 pair_sum=sum(mask.crop((960,row*256,1344,(row+1)*256)).get_flattened_data());crop_sum=0
 for col,x0,x1 in [(5,960,split),(6,split,1344)]:
  region=im.crop((x0,row*256,x1,(row+1)*256));support=region.getchannel('A').point(lambda a:255 if a>=128 else 0);b=support.getbbox();assert b
  crop_sum+=sum(support.get_flattened_data());whole=region.crop(b)
  scale=min(1.0,184/whole.width,246/whole.height)
  size=(round(whole.width*scale),round(whole.height*scale));figure=whole.resize(size,Image.Resampling.NEAREST)
  if col==5:
   assert scale==1.0;xy=(x0+b[0]-col*192,b[1])
  else:xy=((192-size[0])//2,b[3]-size[1])
  cell=Image.new('RGBA',(192,256));cell.paste(figure,xy)
  assert min(xy)>0 and xy[0]+size[0]<192 and xy[1]+size[1]<256
  assert sum(cell.getchannel('A').get_flattened_data())==sum(figure.getchannel('A').get_flattened_data())
  result.paste(cell,(col*192,row*256))
  ops.append({'row':row,'column':col,'clear_vertical_gutter':run,'split':split,'whole_source_rect':[x0+b[0],row*256+b[1],x0+b[2],row*256+b[3]],'source_whole_rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'uniform_NN_scale':scale,'size':size,'placement':xy,'resized_whole_rgba_sha256':hashlib.sha256(figure.tobytes()).hexdigest(),'no_placement_alpha_loss':True})
 assert pair_sum==crop_sum,'All alpha128 figure pixels accounted; no parts lost/exchanged'
for idx in range(32):
 if idx in [13,14,29,30]:continue
 row,col=divmod(idx,8);box=(col*192,row*256,(col+1)*192,(row+1)*256);assert result.crop(box).tobytes()==im.crop(box).tobytes()
result.save(out)
recipe={'schema':1,'method':'Two complete neighbouring figures isolated by actually clear full-row vertical gutter, wholefigure uniform NEAREST scale/translation only; no mask/anatomy/paint/rotation/mirror','raw_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'operations':ops,'all_other28_source_cells_byte_exact':True,'raw_original_preserved':True,'phase_approval':False,'runtime_approval':False}
(D/'whole_figure_normalization_v1a.json').write_text(json.dumps(recipe,indent=2)+'\n');print(json.dumps({'output_sha256':recipe['output_sha256'],'operations':[(o['row'],o['column'],o['uniform_NN_scale']) for o in ops],'unchanged28':True}))
