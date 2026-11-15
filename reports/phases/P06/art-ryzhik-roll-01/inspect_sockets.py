from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;A=W/'game/assets/art/characters/ryzhik';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[];inventory={}
for kind in ['world','action','finisher','roll']:
 png=A/(kind+'_sheet.png');sp=A/(kind+'.sockets.json');meta=A/(kind+'.json');im=Image.open(png).convert('RGBA');s=json.loads(sp.read_text());m=json.loads(meta.read_text());assert sha(png)==s['sheet_sha256']==m['sha256'];assert len(s['frames'])==len(m['frames'])==32;palette={tuple(x) for x in s['garment_palette']};board=Image.new('RGBA',(384,304),(224,225,216,255));dr=ImageDraw.Draw(board)
 for i,f in enumerate(s['frames']):
  row,col=divmod(i,8);cell=im.crop((col*48,row*64,(col+1)*48,(row+1)*64));assert hashlib.sha256(cell.tobytes()).hexdigest()==f['source_frame_rgba_sha256'];assert i==f['index'];x,y=f['clothing'];px=cell.getpixel((x,y));assert px[3]==255 and px[:3] in palette,(kind,i,px);board.alpha_composite(cell,(col*48,row*76+12));dr.text((col*48,row*76),str(i),fill=(90,25,35,255));sx=col*48+x;sy=row*76+12+y;dr.point((sx,sy),fill=(255,40,180,255));dr.line((sx-2,sy,sx+2,sy),fill=(255,40,180,255));dr.line((sx,sy-2,sx,sy+2),fill=(255,40,180,255));rows.append({'kind':kind,'index':i,'clothing':[x,y],'actualRGBA':px,'garment_palette_match':True,'frame_sha256':f['source_frame_rgba_sha256']})
 board.resize((1536,1216),Image.Resampling.NEAREST).save(O/(kind+'_128socket_inspection_4x.png'))
 for p in [png,sp,meta]:inventory[str(p.relative_to(W))]=sha(p)
expected={'world':'cd3f563b42f035df58f8d3e70344f82cbd6670e112644ef6aee7791ecdec622e','action':'4605ae8dc1f7d5eb0f361cc3fe6d83685d43c970e3eba4922dcbc27eff64aa90','finisher':'04f92049a52484f9e54f9f533978f5d1c71230c0e29f55c55295a6f15b3b9df0','roll':'d2aa67987d14f7c3a80069e6cfd343738ee22c00026065fa1c6f5c003d089d94'}
for kind,h in expected.items():assert sha(A/(kind+'_sheet.png'))==h
(O/'socket_metrics.json').write_text(json.dumps({'schema':1,'source_head':'407f9a1df6c3d8ed110ab908b234fad4750b622d','all128_frame_hashes_and_garment_pixels_verified':True,'sheet_hashes_exact_previous_source_candidates':True,'source_inventory_sha256':inventory,'samples':rows,'visual_acceptance_pending':True,'runtime_approval':False},indent=2)+'\n');print('128 socket/frame/garment hashes verified; ART pending')
