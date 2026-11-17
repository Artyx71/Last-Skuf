from pathlib import Path
from PIL import Image,ImageOps,ImageChops,ImageDraw
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';S=W/'assets/source_art/characters/timka';O=R/'reports/phases/P06/art-preflight';P='timka_action_preflight_v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((S/'action_manifest_v1.json').read_text());master=Image.open(S/'action_master_v1.png').convert('RGBA');native=Image.open(S/'action_native_v1.png').convert('RGBA');world=Image.open(S/'world_native_v4c.png').convert('RGBA');portrait=Image.open(S/'portraits_master_v1.png').convert('RGBA')
assert sha(S/'action_master_v1.png')==m['master_sha256']=='4bfe7cb768e1116ac0bdf1cba34a1d32b9b95ce5889a5708320e5d42dd0ad31c'
assert sha(S/'action_native_v1.png')==m['sha256']=='f1ee3175061b38be572af39d050131bc4e1462fe6ee5e7b31a1a3319e0266117'
assert master.size==(1536,1024) and native.size==(384,256)
colors=[tuple(bytes.fromhex(x)) for x in m['packing']['palette_hex']];pal=Image.new('P',(1,1));pal.putpalette([c for t in colors for c in t]+list(colors[0])*(256-len(colors)))
frames=[];recon=Image.new('RGBA',native.size);artifacts=[]
for row,direction in enumerate(m['directions']):
 dy=m['frames'][row*8]['translate_native'][1]
 for col in range(8):
  f=m['frames'][row*8+col];cell=master.crop(tuple(f['source_rect']));ab=cell.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();reduced=cell.resize((48,64),Image.Resampling.NEAREST);alpha=reduced.getchannel('A').point(lambda a:255 if a>=128 else 0);reduced=reduced.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');reduced.putalpha(alpha);reduced.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));packed=Image.new('RGBA',(48,64));packed.paste(reduced,(0,dy));actual=native.crop((col*48,row*64,(col+1)*48,(row+1)*64));h=hashlib.sha256(actual.tobytes()).hexdigest();assert packed.tobytes()==actual.tobytes() and h==f['rgba_sha256'];assert f['translate_native']==[0,dy];assert sum(alpha.get_flattened_data())==sum(packed.getchannel('A').get_flattened_data());assert list(ab)==f['source_opaque_bounds'];recon.paste(packed,(col*48,row*64));bb=actual.getbbox();a=actual.getchannel('A');edge=sum(a.crop((0,0,1,64)).get_flattened_data())//255+sum(a.crop((47,0,48,64)).get_flattened_data())//255+sum(a.crop((0,0,48,1)).get_flattened_data())//255+sum(a.crop((0,63,48,64)).get_flattened_data())//255
  frames.append({'index':row*8+col,'direction':direction,'column':col,'source_bounds_alpha128':list(ab),'source_min_gutter_alpha128':min(ab[0],ab[1],192-ab[2],256-ab[3]),'native_bounds':list(bb),'native_boundary_opaque_pixels':edge,'rgba_sha256':h,'whole_cell_reconstruction_exact':True,'opaque_alpha_preserved':True,'row_constant_dy':dy})
 for bgname,bg in [('light',(225,222,213,255)),('dark',(26,33,32,255))]:
  board=Image.new('RGBA',(48*10,80),bg);draw=ImageDraw.Draw(board)
  for j in range(10):
   c=world.crop((j*48,row*64,(j+1)*48,(row+1)*64)) if j<2 else native.crop(((j-2)*48,row*64,(j-1)*48,row*64+64));board.alpha_composite(c,(j*48,16));draw.text((j*48+2,2),'W'+str(j) if j<2 else 'A'+str(j-2),fill=(100,100,100))
  n=P+'_'+direction+'_'+bgname+'_world_compare_4x.png';board.resize((1920,320),Image.Resampling.NEAREST).save(O/n);artifacts.append(n)
 # Whole-cell ordered diagnostic poses; no runtime claim.
 for seq,cols in [('shove',[0,1,2]),('reaction',[4,5,6])]:
  seqframes=[]
  for col in cols:
   cell=native.crop((col*48,row*64,(col+1)*48,row*64+64));canvas=Image.new('RGBA',(48,64),(34,44,40,255));canvas.alpha_composite(cell);seqframes.append(canvas.resize((288,384),Image.Resampling.NEAREST).convert('RGB'))
  n=P+'_'+direction+'_'+seq+'_SOURCE_ONLY.gif';seqframes[0].save(O/n,save_all=True,append_images=seqframes[1:],duration=350,loop=0);artifacts.append(n)
assert recon.tobytes()==native.tobytes()
refs=json.loads((S/'action_v1_references.json').read_text());refchecks=[]
for x in refs['references']:
 assert sha(W/x['path'])==x['sha256'];refchecks.append(x)
ref=Image.open(W/refs['reference']).convert('RGBA');assert ref.tobytes()==world.resize((1536,1024),Image.Resampling.NEAREST).tobytes()
assert sha(S/'action_v1_prompt.txt')==refs['prompt_sha256'];assert sha(S/'world_native_v4c.png')==refs['source_sha256']
result={'schema':1,'reviewer':'/root/art_timka_recovery','actor_id':'timka','kind':'action','scope':'SOURCE_ONLY','runtime_approval':False,'full_phase_approval':False,'phase_approval':False,'master_sha256':sha(S/'action_master_v1.png'),'native_sha256':sha(S/'action_native_v1.png'),'source_dimensions':list(master.size),'native_dimensions':list(native.size),'binary_native_alpha':sorted(set(native.getchannel('A').get_flattened_data())),'opaque_native_colors':len({v[:3] for v in native.get_flattened_data() if v[3]}),'unique_native_cells':len({f['rgba_sha256'] for f in frames}),'all32_reconstructed_exact':True,'palette_subset':all(v[:3] in colors for v in native.get_flattened_data() if v[3]),'source_reference_NN4_exact':True,'reference_checks':refchecks,'frames':frames,'native_boundary_cells':[f['index'] for f in frames if f['native_boundary_opaque_pixels']],'source_gutters_under_requested16':[f['index'] for f in frames if f['source_min_gutter_alpha128']<16],'diagnostic_artifacts':artifacts,'actual_runtime_or_contact_test':False}
(O/(P+'_metrics.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['unique_native_cells','binary_native_alpha','opaque_native_colors','native_boundary_cells','source_gutters_under_requested16','diagnostic_artifacts']}))
