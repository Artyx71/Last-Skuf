from pathlib import Path
from PIL import Image,ImageDraw,ImageOps
import json,hashlib,collections
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';SRC=WORK/'assets/source_art/characters/ryzhik';OUT=ROOT/'reports/phases/P06/art-preflight';PFX='ryzhik_world_preflight_v2d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();meta=json.loads((SRC/'world_manifest_v2d.json').read_text());raw=Image.open(SRC/'world_master_v2d.png').convert('RGBA');native=Image.open(SRC/'world_native_v2d.png').convert('RGBA');palette=[tuple(bytes.fromhex(x)) for x in meta['packing']['palette_hex']];p=Image.new('P',(1,1));p.putpalette([v for c in palette for v in c]+list(palette[0])*(256-len(palette)));metrics={'master_sha256':sha(SRC/'world_master_v2d.png'),'native_sha256':sha(SRC/'world_native_v2d.png'),'frames':[]}
assert meta['master_sha256']==metrics['master_sha256'];assert meta['sha256']==metrics['native_sha256']
for row,direction in enumerate(['down','left','right','up']):
 board=Image.new('RGB',(1536,256),'#24262c')
 for col in range(8):
  f=meta['frames'][row*8+col];cell=native.crop((col*48,row*64,col*48+48,row*64+64));sample=raw.crop(tuple(f['source_rect'])).resize((48,64),Image.Resampling.NEAREST);alpha=sample.getchannel('A').point(lambda x:255 if x>=meta['packing']['alpha_threshold'] else 0);sample=sample.convert('RGB').quantize(palette=p,dither=Image.Dither.NONE).convert('RGBA');sample.putalpha(alpha);sample.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));rebuilt=Image.new('RGBA',(48,64));rebuilt.paste(sample,tuple(f['translate_native']));assert rebuilt.tobytes()==cell.tobytes();assert sum(rebuilt.getchannel('A').get_flattened_data())==sum(alpha.get_flattened_data());assert hashlib.sha256(cell.tobytes()).hexdigest()==f['rgba_sha256'];metrics['frames'].append({'row':direction,'column':col,'bounds':cell.getbbox(),'translate':f['translate_native'],'source_bounds':f['source_opaque_bounds'],'rgba_sha256':f['rgba_sha256'],'opaque_loss':0})
  for bg in range(2):
   b=Image.new('RGBA',(48,64),(230,230,230,255) if bg else (22,26,30,255));b.alpha_composite(cell);board.paste(b.resize((192,256),Image.Resampling.NEAREST).convert('RGB'),(col*192,bg*0)) if False else None
  # Eight on dark then same8 onlight along one strip.
  for bg in range(2):
   b=Image.new('RGBA',(48,64),(230,230,230,255) if bg else (22,26,30,255));b.alpha_composite(cell);board.paste(b.resize((96,128),Image.Resampling.NEAREST).convert('RGB'),(col*192+bg*96,20))
   ImageDraw.Draw(board).text((col*192+2,2),str(col),fill='white')
 board.save(OUT/f'{PFX}_{direction}_light_dark.png')
 if direction in ['left','right']:
  board=Image.new('RGB',(1536,1060),'#eeeeee');draw=ImageDraw.Draw(board)
  for j,col in enumerate([2,4,6,7]):
   cell=native.crop((col*48,row*64,col*48+48,row*64+64));b=Image.new('RGBA',(48,64),(230,230,230,255));b.alpha_composite(cell);board.paste(b.resize((384,512),Image.Resampling.NEAREST).convert('RGB'),(j*384,30));source=raw.crop((col*192,row*256,col*192+192,row*256+256));b=Image.new('RGBA',(192,256),(230,230,230,255));b.alpha_composite(source);board.paste(b.resize((384,512),Image.Resampling.NEAREST).convert('RGB'),(j*384,548));draw.text((j*384+5,5),f'{direction} native col{col}',fill='black')
  board.save(OUT/f'{PFX}_{direction}_gait_fullcells.png')
metrics.update(unique_native=len(set(f['rgba_sha256'] for f in metrics['frames'])),native_alpha=sorted(set(native.getchannel('A').get_flattened_data())),opaque_colors=len({p[:3] for p in native.get_flattened_data() if p[3]}));(OUT/f'{PFX}_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('32 exact zero-loss reconstruction; unique',metrics['unique_native'])
