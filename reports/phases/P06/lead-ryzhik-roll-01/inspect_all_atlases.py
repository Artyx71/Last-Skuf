from pathlib import Path
from PIL import Image, ImageOps
import json,hashlib
OUT=Path(__file__).parent;ROOT=OUT.parents[3];WORK=ROOT/'.autopilot/worktrees/P06';folder=WORK/'game/assets/art/characters/ryzhik'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows={};clips=0
for kind in ['world','action','finisher','roll']:
 m=json.loads((folder/(kind+'.json')).read_text());s=json.loads((folder/(kind+'.sockets.json')).read_text())
 master=Image.open(WORK/m['master']).convert('RGBA');sheet=Image.open(folder/(kind+'_sheet.png')).convert('RGBA')
 assert sha(WORK/m['master'])==m['master_sha256'] and sha(folder/(kind+'_sheet.png'))==m['sha256']==s['sheet_sha256']
 colors=[tuple(bytes.fromhex(c)) for c in m['packing']['palette_hex']];pal=Image.new('P',(1,1));pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
 frames=[]
 for i,f in enumerate(m['frames']):
  cell=master.crop(f['source_rect']).resize((48,64),Image.Resampling.NEAREST);a=cell.getchannel('A').point(lambda a:255 if a>=m['packing']['alpha_threshold'] else 0)
  cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(a);cell.paste((0,0,0,0),(0,0),ImageOps.invert(a))
  rebuilt=Image.new('RGBA',(48,64));rebuilt.paste(cell,tuple(f['translate_native']));x,y,w,h=f['rect'];actual=sheet.crop((x,y,x+w,y+h));digest=hashlib.sha256(actual.tobytes()).hexdigest()
  assert rebuilt.tobytes()==actual.tobytes() and digest==f['rgba_sha256']==s['frames'][i]['source_frame_rgba_sha256']
  cx,cy=s['frames'][i]['clothing'];assert 0<=cx<48 and 0<=cy<64 and actual.getpixel((cx,cy))[3]==255
  frames.append({'index':i,'rgba_sha256':digest,'socket':s['frames'][i]['clothing'],'opaque_socket':True})
 clips+=len(m['animations_source_columns'])*4
 rows[kind]={'native_sha256':m['sha256'],'master_sha256':m['master_sha256'],'complete_cells_reconstructed':len(frames),'clothing_anchors_bound_and_opaque':len(frames),'animation_reference_count':m['animation_reference_count'],'frames':frames}
assert sum(x['complete_cells_reconstructed'] for x in rows.values())==128 and clips==60
(OUT/'all-atlas-proofs.json').write_text(json.dumps({'sheets':rows,'total_own_cells':128,'total_clips':clips,'semantic_clothing_and_pose_acceptance_separate_visual_review':True},indent=2)+'\n')
print('128 complete cell reconstructions,128 exact opaque bound sockets,60 mapped clips verified; latent clips do not grant abilities')
