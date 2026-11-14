import sys,json,hashlib
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]/'.autopilot/worktrees/P06'
actor,version,outversion=sys.argv[1:];assert actor in ['tega','pasha']
folder=root/'assets/source_art/characters'/actor
source=folder/f'world_master_{version}.png';dest=folder/f'world_master_{outversion}.png';recipe=folder/f'world_{outversion}_assembly.json'
assert not dest.exists() and not recipe.exists()
image=Image.open(source).convert('RGBA');assert image.size==(1536,1024)
output=image.copy();entries=[];rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for index in range(32):
 row,col=divmod(index,8);rect=(col*192,row*256,(col+1)*192,(row+1)*256);cell=image.crop(rect)
 bounds=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert bounds
 left,top,right,bottom=bounds;assert right-left<=160 and bottom-top<=224,(index,'Only translations permitted, whole figure too large',bounds)
 dx=max(16-left,min(0,176-right));dy=max(16-top,min(0,240-bottom))
 if dx==dy==0:shifted=cell
 else:
  shifted=Image.new('RGBA',(192,256));shifted.paste(cell,(dx,dy))
 assert sum(a>=128 for a in shifted.getchannel('A').get_flattened_data())==sum(a>=128 for a in cell.getchannel('A').get_flattened_data())
 shifted_bounds=shifted.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert min(shifted_bounds[0],shifted_bounds[1],192-shifted_bounds[2],256-shifted_bounds[3])>=16
 assert shifted.crop((left+dx,top+dy,right+dx,bottom+dy)).tobytes()==cell.crop(bounds).tobytes()
 output.paste(shifted,rect[:2]);entries.append({'cell':index,'source_bounds':list(bounds),'translation':[dx,dy],'output_bounds':list(shifted_bounds),'source_cell_rgba_sha256':rgba(cell),'output_cell_rgba_sha256':rgba(shifted),'support_RGBA_byte_exact':True,'opaque_pixel_count_preserved':True})
output.save(dest)
recipe.write_text(json.dumps({'schema':1,'actor_id':actor,'kind':'world','source':str(source.relative_to(root)),'source_sha256':sha(source),'output':str(dest.relative_to(root)),'output_sha256':sha(dest),'operation':'minimum complete-figure translations solely for source gutter16 containment, no rescale/mirror/bodypart edits/painting','not_per_frame_sole_anchor':'packer keeps fixed column0 reference58 per row; no exclusive sole58 alignment; varying foot bottoms retained for actual native review','support_alpha_threshold':128,'subthreshold_alpha_outside_source_support':'may be discarded consistently with native pack alpha128; no source-support RGBA changes','changed_cells':[e['cell'] for e in entries if e['translation']!=[0,0]],'entries':entries,'phase_approval':False,'status':'CANDIDATE_REQUIRES_FRESH_ALL32_SOURCE_AND_NATIVE_REVIEW'},indent=2)+'\n')
print(json.dumps({'actor':actor,'master_sha256':sha(dest),'translated_cells':[e['cell'] for e in entries if e['translation']!=[0,0]]}))
