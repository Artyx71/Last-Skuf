#!/usr/bin/env python3
"""Technical NN sampling of complete generated portrait cells; never reads photographs.
No anatomy editing, synthetic expressions, facial feature compositing, or mirroring.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
ROOT=Path(__file__).resolve().parents[3]
PALETTE=['0b090e','15101a','211b29','352b3d','4c3c56','6c9aaf','75455f','15151e','252332','353244','222936','344255','4c6076','562d37','873e3c','a75c49','c47755','dc956f','efb08b','f6c59f','ece3d5','2b1a1e','6d354b','994a63','bc6573','4e202c','8b3146','bc5260','e8878c','3e94b4','7bd2df','42162d','67243b','963450','c04b66','8b8a87','b3aaa0','d8c9b4','342d24','514234','726046','9b825a','c2a976']
POSES=['neutral','angry','surprise','hurt','catchphrase','neutral_talk','neutral_blink','catchphrase_talk','catchphrase_blink']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(actor):
 source=ROOT/'assets/source_art/characters'/actor;dest=ROOT/'game/assets/art/characters'/actor;dest.mkdir(parents=True,exist_ok=True)
 master=source/'portraits_master_v1.png';image=Image.open(master).convert('RGBA');assert image.width>0 and image.height>0
 assert 0 in image.getchannel('A').getextrema(),'Actual transparent generation is required'
 colors=[tuple(bytes.fromhex(x)) for x in PALETTE];pal=Image.new('P',(1,1));pal.putpalette([c for t in colors for c in t]+list(colors[0])*(256-len(colors)))
 # Locate the actual clear gutters, rather than assume requested generator dimensions.
 alpha=image.getchannel('A').point(lambda a:255 if a>=128 else 0)
 def partitions(axis):
  length=image.width if axis==0 else image.height; occupied=[]
  for n in range(length):
   strip=alpha.crop((n,0,n+1,image.height) if axis==0 else (0,n,image.width,n+1))
   occupied.append(strip.getbbox() is not None)
  runs=[];start=None
  for n,v in enumerate(occupied+[False]):
   if v and start is None:start=n
   if not v and start is not None:runs.append([start,n]);start=None
  # Only wide transparent gutters separate complete drawings; merge small interior holes.
  merged=[]
  for run in runs:
   if merged and run[0]-merged[-1][1]<8:merged[-1][1]=run[1]
   else:merged.append(run)
  assert len(merged)==3,(actor,axis,merged)
  cuts=[0]+[(merged[i][1]+merged[i+1][0])//2 for i in range(2)]+[length]
  return cuts
 xs,ys=partitions(0),partitions(1)
 # Uniform shared scale for every complete portrait, only anchor translations differ.
 boxes=[]
 for i in range(9):
  row,col=divmod(i,3);cell=alpha.crop((xs[col],ys[row],xs[col+1],ys[row+1]));b=cell.getbbox();assert b
  boxes.append((xs[col]+b[0],ys[row]+b[1],xs[col]+b[2],ys[row]+b[3]))
 scale=min(152/max(b[2]-b[0] for b in boxes),152/max(b[3]-b[1] for b in boxes))
 output=Image.new('RGBA',(160*9,160));frames=[]
 for index,pose in enumerate(POSES):
  row,col=divmod(index,3);box=boxes[index]
  cell=image.crop(box);w,h=round(cell.width*scale),round(cell.height*scale)
  native=cell.resize((w,h),Image.Resampling.NEAREST);alpha=native.getchannel('A').point(lambda a:255 if a>=128 else 0)
  native=native.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');native.putalpha(alpha);native.paste((0,0,0,0),(0,0),ImageOps.invert(alpha))
  frame=Image.new('RGBA',(160,160));offset=((160-w)//2,158-h);frame.paste(native,offset);output.paste(frame,(index*160,0))
  frames.append({'id':pose,'rect':[index*160,0,160,160],'source_rect':list(box),'bounds':list(frame.getbbox()),'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
 output.save(dest/'portraits.png');output.save(source/'portraits_native_source.png')
 manifest={'schema':1,'actor_id':actor,'status':'CANDIDATE_REQUIRES_INDEPENDENT_ART_AND_RUNTIME','generation':'built-in image_gen','master':str(master.relative_to(ROOT)),'master_sha256':sha(master),'prompt':str((source/'portrait_prompt.txt').relative_to(ROOT)),'prompt_sha256':sha(source/'portrait_prompt.txt'),'file':'portraits.png','sha256':sha(dest/'portraits.png'),'frame_size':[160,160],'dimensions':list(output.size),'frames':frames,'source_cells':9,'unique_native_drawings':len({x['rgba_sha256'] for x in frames}),'shared_animation_references':{},'static_expressions':POSES[:5],'unused_source_pose_indices':[5,6,7,8],'motion_status':'NOT_APPROVED; pose-wide generated differences; static expression presentation only','packing':{'resize':'NEAREST complete-portrait shared scale, centered x80 baseline158','shared_scale':scale,'source_grid_partition_x':xs,'source_grid_partition_y':ys,'alpha_threshold':128,'raw_reference_read':False,'anatomical_reconstruction':False,'fixed_palette_hex':PALETTE,'opaque_colors_used':len({p[:3] for p in output.get_flattened_data() if p[3]})}}
 (dest/'portraits.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 board=Image.new('RGBA',(480,480),(40,48,55,255))
 for i in range(9):board.alpha_composite(output.crop((i*160,0,(i+1)*160,160)),((i%3)*160,(i//3)*160))
 board.resize((960,960),Image.Resampling.NEAREST).save(source/'portraits_inspection_2x.png')
 print(json.dumps({'actor':actor,'master':sha(master),'native':manifest['sha256'],'unique':manifest['unique_native_drawings'],'status':manifest['status']}))
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('actors',nargs='+');args=parser.parse_args()
 for actor in args.actors:pack(actor)
