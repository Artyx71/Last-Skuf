#!/usr/bin/env python3
"""Whole eight-pose world/action/finisher source -> native source inspection.
No anatomy editing, perspective transform, repainting, mirroring or photographs.
One uniform master scale and a fixed standing anchor can preserve foot depth.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
from pack_portraits import PALETTE
ROOT=Path(__file__).resolve().parents[3]
def pack(actor,direction,version,output_version=None,native_width=48,anchor='sole',kind='world'):
 assert kind in ['world','action','finisher']
 assert anchor!='idle' or kind=='world','Use a single standing reference pose for action/finisher rows'
 source=ROOT/'assets/source_art/characters'/actor;master=source/f'{kind}_{direction}_master_{version}.png';im=Image.open(master).convert('RGBA');assert im.size==(1536,1024)
 output_version=output_version or version
 assert native_width in [45,48,54] # whole-cell uniform15/128,1/8,9/64; no stretch
 native_size=(native_width,native_width*4//3);dx=(48-native_width)//2
 pal=Image.new('P',(1,1));colors=[tuple(bytes.fromhex(c)) for c in PALETTE];pal.putpalette([c for t in colors for c in t]+list(colors[0])*(256-len(colors)))
 cells=[];boxes=[];source_bounds=[]
 for index in range(8):
  row,col=divmod(index,4);box=(col*384,row*512,(col+1)*384,(row+1)*512);whole=im.crop(box)
  bounds=whole.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
  assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<384 and bounds[3]<512,(kind,direction,index,'cell boundary/clipping',bounds)
  cell=whole.resize(native_size,Image.Resampling.NEAREST)
  alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0);cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(alpha);cell.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));assert cell.getbbox()
  cells.append(cell);boxes.append(box);source_bounds.append(bounds)
 # Fixed anchor keeps original authored body/head position through depth strides.
 # Longest shoe need not coincide with standing origin on every contact pose.
 fixed_dy=58-max(cells[i].getbbox()[3] for i in ([0] if anchor=='reference' else [0,1]))
 out=Image.new('RGBA',(384,64));frames=[]
 for index,cell in enumerate(cells):
  dy=fixed_dy if anchor in ['idle','reference'] else 58-cell.getbbox()[3]
  frame=Image.new('RGBA',(48,64));frame.paste(cell,(dx,dy));assert sum(frame.getchannel('A').get_flattened_data())==sum(cell.getchannel('A').get_flattened_data()),'No opaque crop by whole-cell placement'
  out.paste(frame,(index*48,0));frames.append({'index':index,'source_rect':boxes[index],'source_opaque_bounds':source_bounds[index],'translate_native':[dx,dy],'translate_y':dy,'bounds':frame.getbbox(),'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
 path=source/f'{kind}_{direction}_native_{output_version}.png';out.save(path)
 bg=Image.new('RGBA',out.size,(36,48,44,255));bg.alpha_composite(out);bg.resize((1536,256),Image.Resampling.NEAREST).save(source/f'{kind}_{direction}_inspection_{output_version}_4x.png')
 manifest={'schema':1,'status':'CANDIDATE_NOT_IN_PRODUCTION','actor_id':actor,'kind':kind,'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'master':str(master.relative_to(ROOT)),'master_sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'source_cells':8,'directions':[direction],'frame_size':[48,64],'pivot':[24,58],'frames':frames,'packing':{'whole_cell_nearest':list(native_size),'uniform_scale':native_width/384,'horizontal_translation':dx,'vertical_alignment':anchor,'standing_anchor_y':58,'fixed_dy':fixed_dy if anchor in ['idle','reference'] else None,'palette_colors':len(PALETTE),'alpha_threshold':128,'anatomical_reconstruction':False,'mirroring':False,'opaque_crop':False}}
 (source/f'{kind}_{direction}_manifest_{output_version}.json').write_text(json.dumps(manifest,indent=2)+'\n');print(actor,kind,direction,output_version,manifest['sha256'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('actor');p.add_argument('direction',choices=['down','left','right','up']);p.add_argument('--version',required=True);p.add_argument('--output-version');p.add_argument('--native-width',type=int,default=48,choices=[45,48,54]);p.add_argument('--anchor',default='sole',choices=['sole','idle','reference']);p.add_argument('--kind',default='world',choices=['world','action','finisher']);args=p.parse_args();pack(args.actor,args.direction,args.version,args.output_version,args.native_width,args.anchor,args.kind)
