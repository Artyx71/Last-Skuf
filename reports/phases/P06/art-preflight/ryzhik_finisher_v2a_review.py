from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';D=R/'.tools/art-pending/ryzhik/finisher-signature-v2';B=D.parent/'finisher-v1';P=D/'preview-project/assets/source_art/characters/ryzhik';O=Path(__file__).resolve().parent;prefix='ryzhik_finisher_v2a_';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest();q=json.loads((D/'assembly_v2a.json').read_text());gen=json.loads((D/'generation.json').read_text());raw=Image.open(D/'signature_three_master_v2.png').convert('RGBA');base=Image.open(B/'finisher_master_v1a.png').convert('RGBA');master=Image.open(D/'finisher_master_v2a.png').convert('RGBA');im=Image.open(P/'finisher_native_v2a.png').convert('RGBA');oldnative=Image.open(B/'preview-project/assets/source_art/characters/ryzhik/finisher_native_v1a.png').convert('RGBA');m=json.loads((P/'finisher_manifest_v2a.json').read_text());assert sha(D/'signature_three_master_v2.png')==q['raw_sha256']==gen['sha256'];assert sha(B/'finisher_master_v1a.png')==q['base_sha256'];assert sha(D/'finisher_master_v2a.png')==q['output_sha256']==sha(P/'finisher_master_v2a.png');assert sha(D/'assemble_v2a.py')==q['script_sha256'];assert sha(W/'assets/source_art/characters/pack_actor_sheet.py')==q['canonical_packer_sha256'];assert sha(D/'prompt.txt')==gen['prompt_sha256']
for r in gen['references']:assert sha(Path(r['path']))==r['sha256']
rebuilt=base.copy()
for i,row in enumerate([1,2,3]):
 op=q['operations'][i];slot=raw.crop((i*512,0,(i+1)*512,1024));b=slot.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert list(b)==op['complete_support_bounds_in_slot'];whole=slot.crop(b);assert rgba(whole)==op['complete_rgba_sha256'];scale=min(176/whole.width,208/whole.height);size=(round(whole.width*scale),round(whole.height*scale));resized=whole.resize(size,Image.Resampling.NEAREST);assert scale==op['scale'] and list(size)==op['resized_size'] and rgba(resized)==op['resized_rgba_sha256'];old=base.crop((7*192,row*256,8*192,(row+1)*256));ob=old.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();xy=((192-size[0])//2,ob[3]-size[1]);assert list(xy)==op['placement'];cell=Image.new('RGBA',(192,256));cell.paste(resized,xy);assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data());rebuilt.paste(cell,(7*192,row*256))
assert rebuilt.tobytes()==master.tobytes();unchanged=[]
for idx in range(32):
 row,col=divmod(idx,8)
 if idx not in [15,23,31]:
  box=(col*192,row*256,(col+1)*192,(row+1)*256);assert base.crop(box).tobytes()==master.crop(box).tobytes();assert oldnative.crop((col*48,row*64,(col+1)*48,(row+1)*64)).tobytes()==im.crop((col*48,row*64,(col+1)*48,(row+1)*64)).tobytes();unchanged.append(idx)
assert m['sha256']==sha(P/'finisher_native_v2a.png')==q['native_sha256']=='e2f6422ece4b7baabd4ae1712df01354e38c3ef6f2d6ad1d9c44904601b0fd8a';colors=[tuple(bytes.fromhex(c)) for c in m['packing']['palette_hex']];pal=Image.new('P',(1,1));pal.putpalette([x for c in colors for x in c]+list(colors[0])*(256-len(colors)));rep=Image.new('RGBA',(384,256));frames=[];world=Image.open(W/'game/assets/art/characters/ryzhik/world_sheet.png').convert('RGBA')
for row,di in enumerate(['down','left','right','up']):
 ref=master.crop((0,row*256,192,(row+1)*256)).resize((48,64),Image.Resampling.NEAREST);dy=58-ref.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()[3]
 for col in range(8):
  piece=master.crop((col*192,row*256,(col+1)*192,(row+1)*256));small=piece.resize((48,64),Image.Resampling.NEAREST);a=small.getchannel('A').point(lambda v:255 if v>=128 else 0);small=small.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');small.putalpha(a);small.paste((0,0,0,0),(0,0),ImageOps.invert(a));final=Image.new('RGBA',(48,64));final.paste(small,(0,dy));assert sum(final.getchannel('A').get_flattened_data())==sum(a.get_flattened_data());rep.paste(final,(col*48,row*64));f=m['frames'][row*8+col];assert rgba(final)==f['rgba_sha256'];frames.append({'index':row*8+col,'bounds':list(final.getbbox()),'rgba_sha256':rgba(final)})
assert rep.tobytes()==im.tobytes()
def board(cells,labels,name,scale=6,bg=(225,228,220,255)):
 out=Image.new('RGBA',(len(cells)*48,78),bg);d=ImageDraw.Draw(out)
 for i,(c,label) in enumerate(zip(cells,labels)):out.alpha_composite(c,(i*48,14));d.text((i*48+1,2),label,fill=(120,40,40,255) if bg[0]>128 else (235,225,215,255))
 out.resize((out.width*scale,out.height*scale),Image.Resampling.NEAREST).save(O/(prefix+name))
for row,di in enumerate(['down','left','right','up']):
 cells=[im.crop((c*48,row*64,(c+1)*48,(row+1)*64)) for c in range(8)];own=world.crop((0,row*64,48,(row+1)*64));old=oldnative.crop((7*48,row*64,8*48,(row+1)*64))
 board([own]+cells,['WORLD0']+[str(i) for i in range(8)],di+'_family_all8.png',5)
 board(cells,[str(i) for i in range(8)],di+'_dark_all8.png',5,(30,36,43,255))
 for name,cols in m['animations_source_columns'].items():board([cells[c] for c in cols],[str(c) for c in cols],di+'_'+name+'_SOURCE_ONLY.png',6,(30,36,43,255))
 board([own,cells[0],old,cells[7],cells[6]],['WORLD','FIN0','v1a7','v2a7','FIN6'],di+'_signature_family_detail.png',8)
 for kind,cell in [('WORLD0',own),('FIN0',cells[0]),('NEW7',cells[7])]:
  scale=12;grid=Image.new('RGBA',(48*scale+42,64*scale+28),(235,235,225,255));background=Image.new('RGBA',(48,64),(225,228,220,255));background.alpha_composite(cell);grid.alpha_composite(background.resize((48*scale,64*scale),Image.Resampling.NEAREST),(42,28));draw=ImageDraw.Draw(grid)
  for y in range(0,64,2):draw.text((2,28+y*scale),str(y),fill=(70,30,30,255))
  for x in range(0,48,4):draw.text((42+x*scale,2),str(x),fill=(70,30,30,255))
  grid.save(O/(prefix+di+'_'+kind+'_wholecell_coordinate.png'))
metrics={'schema':1,'raw_sha256':sha(D/'signature_three_master_v2.png'),'master_sha256':sha(D/'finisher_master_v2a.png'),'native_sha256':sha(P/'finisher_native_v2a.png'),'manifest_sha256':sha(P/'finisher_manifest_v2a.json'),'three_whole_pose_assembly_reconstructed_exact':True,'other29_master_RGBA_exact':True,'other29_native_RGBA_exact':True,'unchanged_indices':unchanged,'native32_repack_exact':True,'frame_metrics':frames,'native_edge_touching_indices':[f['index'] for f in frames if f['bounds'][0]==0 or f['bounds'][1]==0 or f['bounds'][2]==48 or f['bounds'][3]==64],'runtime_approval':False,'phase_approval':False}
(O/(prefix+'metrics.json')).write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['unchanged_indices','frame_metrics']}))
