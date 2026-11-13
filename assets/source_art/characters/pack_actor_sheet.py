#!/usr/bin/env python3
"""Whole generated cells -> fixed pixel grid. No photo access/anatomy drawing/rotation.
World/action/finisher layouts are32source cells; shared animation refs are explicit.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image,ImageOps
from pack_portraits import PALETTE
ROOT=Path(__file__).resolve().parents[3]
DIRECTIONS=['down','left','right','up']
MAPS={'world':{'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]},'action':{'shove':[0,1,2],'interact':[3],'hit':[4],'fall':[5,6],'fire':[7]},'finisher':{**{f'finish_{name}':[0,col,6] for col,name in enumerate(['unarmed','blunt','sharp','firearm','environmental'],1)},'special':[0,7,6]}}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pack(actor,kind,version):
 source=ROOT/'assets/source_art/characters'/actor;master=source/f'{kind}_master_{version}.png';im=Image.open(master).convert('RGBA')
 assert im.size==(1536,1024),('Explicit8x4layout required; preserve unexpected output for review',im.size)
 dest=ROOT/'game/assets/art/characters'/actor;dest.mkdir(parents=True,exist_ok=True)
 colors=[tuple(bytes.fromhex(x)) for x in PALETTE];pal=Image.new('P',(1,1));pal.putpalette([c for t in colors for c in t]+list(colors[0])*(256-len(colors)))
 output=Image.new('RGBA',(384,256));frames=[]
 for row,direction in enumerate(DIRECTIONS):
  for col in range(8):
   box=(col*192,row*256,(col+1)*192,(row+1)*256);cell=im.crop(box);a=cell.getchannel('A').point(lambda a:255 if a>=128 else 0);b=a.getbbox();assert b and b[0]>0 and b[1]>0 and b[2]<192 and b[3]<256,(actor,kind,direction,col,'cell boundary/clipping',b)
   cell=cell.resize((48,64),Image.Resampling.NEAREST);alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
   cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(alpha);cell.paste((0,0,0,0),(0,0),ImageOps.invert(alpha))
   bottom=cell.getbbox()[3];dy=58-bottom;frame=Image.new('RGBA',(48,64));frame.paste(cell,(0,dy))
   assert sum(frame.getchannel('A').get_flattened_data())==sum(alpha.get_flattened_data()),'No opaque pixels may be cropped by baseline alignment'
   output.paste(frame,(col*48,row*64));frames.append({'direction':direction,'column':col,'source_rect':list(box),'source_opaque_bounds':list(b),'translate_native':[0,dy],'rect':[col*48,row*64,48,64],'pivot':[24,58],'bounds':list(frame.getbbox()),'rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
 path=dest/f'{kind}_sheet.png';output.save(path);output.save(source/f'{kind}_native_{version}.png')
 manifest={'schema':1,'actor_id':actor,'kind':kind,'status':'CANDIDATE_REQUIRES_INDEPENDENT_ANIMATION_AND_RUNTIME','master':str(master.relative_to(ROOT)),'master_sha256':sha(master),'file':path.name,'sha256':sha(path),'frame_size':[48,64],'dimensions':[384,256],'pivot':[24,58],'directions':DIRECTIONS,'source_cells':32,'unique_native_drawings':len({f['rgba_sha256'] for f in frames}),'frames':frames,'animations_source_columns':MAPS[kind],'animation_reference_count':sum(map(len,MAPS[kind].values()))*4,'packing':{'resize':'one whole192x256cell NEAREST to48x64','horizontal_translation':False,'vertical_alignment':'exclusive sole baseline58','alpha_threshold':128,'palette_hex':PALETTE,'opaque_colors_used':len({p[:3] for p in output.get_flattened_data() if p[3]}),'raw_reference_read':False,'anatomical_reconstruction':False},'review':{'actual_animation':'PENDING','independent_art':'PENDING','contact_alignment':'PENDING'}}
 (dest/f'{kind}.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 board=Image.new('RGBA',output.size,(36,48,44,255));board.alpha_composite(output);board.resize((1152,768),Image.Resampling.NEAREST).save(source/f'{kind}_inspection_{version}_3x.png')
 print(json.dumps({'actor':actor,'kind':kind,'unique_native':manifest['unique_native_drawings'],'native':manifest['sha256'],'status':manifest['status']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('actor');p.add_argument('kind',choices=list(MAPS));p.add_argument('--version',default='v1');args=p.parse_args();pack(args.actor,args.kind,args.version)
