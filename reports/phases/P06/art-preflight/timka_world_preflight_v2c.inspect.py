import hashlib,json,sys,datetime
from pathlib import Path
from PIL import Image,ImageOps
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-preflight';S=W/'assets/source_art/characters/timka';P='timka_world_preflight_v2c'
sys.path.insert(0,str(W/'assets/source_art/characters'));from pack_portraits import PALETTE
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['assets/source_art/characters/timka/'+n for n in ['world_master_v2c.png','world_native_v2c.png','world_manifest_v2c.json','world_inspection_v2c_3x.png','world_v2_prompt.txt','world_v2_generation_metadata.json','portraits_master_v1.png','portrait_prompt.txt','portrait_generation_metadata.json']]+['assets/source_art/characters/olezhka/world_camera_reference_v2b_4x.png','assets/source_art/characters/olezhka/world_native_v2b.png','assets/source_art/characters/gabar/world_native_v7.png','assets/source_art/characters/pack_actor_sheet.py','assets/source_art/characters/pack_portraits.py','docs/ART_BIBLE.md','docs/CHARACTER_BIBLE.md','specs/CHARACTER_EXPANSION_SPEC.md']
paths += ['assets/source_art/characters/timka/'+name for name in ['world_master_v1.png','world_native_v1.png','world_manifest_v1.json','world_master_v2.png','world_master_v2a.png','world_master_v2b.png','world_v2a_assembly.json','world_v2b_assembly.json','world_v2c_assembly.json']]
paths += ['assets/source_art/characters/replace_actor_cell.py']
inventory={p:sha(W/p) for p in paths}
master=Image.open(S/'world_master_v2c.png').convert('RGBA');native=Image.open(S/'world_native_v2c.png').convert('RGBA');m=json.loads((S/'world_manifest_v2c.json').read_text());meta=json.loads((S/'world_v2_generation_metadata.json').read_text())
assert master.size==(1536,1024) and native.size==(384,256)
assert sha(S/'world_master_v2c.png')==m['master_sha256']=='f9bac4d96378a0e27c138044714f82e00b52e20fbd4f11ba1ca757f7e98c1628'
assert sha(S/'world_master_v2.png')==meta['master_sha256']=='9be3fbc687b8e39ff5c642d43defc2fd3a99060d35cf421b8976d0b4e9e0cc2d'
assert sha(S/'world_native_v2c.png')==m['sha256']=='2be68456eece98cd27310e849e65eafa2e57e5121b6b8ba93d7ab53cfd1527fa'
assert meta['prompt_sha256']==sha(S/'world_v2_prompt.txt')
assert m['directions']==['down','left','right','up'] and m['source_cells']==len(m['frames'])==32 and m['pivot']==[24,58]
pal=Image.new('P',(1,1));colors=[tuple(bytes.fromhex(x)) for x in PALETTE];pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
metrics={'schema':1,'reviewer':'/root/art_timka_recovery','scope':'SOURCE_ONLY_FRESH_INDEPENDENT_REVIEW_AFTER_RESTART','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'master_sha256':sha(S/'world_master_v2c.png'),'native_sha256':sha(S/'world_native_v2c.png'),'native_alpha':sorted(set(native.getchannel('A').get_flattened_data())),'native_opaque_colors':len({p[:3] for p in native.get_flattened_data() if p[3]}),'frames':[],'source_inventory_sha256':inventory,'runtime_tested':False,'full_phase_approval':False,'artifacts':[]}
recon=Image.new('RGBA',native.size);digests=[]
for i,f in enumerate(m['frames']):
 row,col=divmod(i,8);assert f['direction']==m['directions'][row] and f['column']==col and f['source_rect']==[col*192,row*256,(col+1)*192,(row+1)*256]
 src=master.crop(tuple(f['source_rect']));bounds=src.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();cell=src.resize((48,64),Image.Resampling.NEAREST);alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
 cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(alpha);cell.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));out=Image.new('RGBA',(48,64));out.paste(cell,tuple(f['translate_native']));actual=native.crop((col*48,row*64,(col+1)*48,(row+1)*64));digest=hashlib.sha256(actual.tobytes()).hexdigest();digests.append(digest);recon.paste(out,(col*48,row*64))
 assert out.tobytes()==actual.tobytes() and digest==f['rgba_sha256'] and bounds==tuple(f['source_opaque_bounds'])
 assert sum(alpha.get_flattened_data())==sum(out.getchannel('A').get_flattened_data())
 assert bounds[0]>0 and bounds[1]>0 and bounds[2]<192 and bounds[3]<256
 rowanchor=m['frames'][row*8]['translate_native'];assert f['translate_native']==rowanchor
 metrics['frames'].append({'index':i,'direction':f['direction'],'column':col,'source_opaque_bounds':list(bounds),'native_bounds':list(actual.getbbox()),'translate_native':f['translate_native'],'native_rgba_sha256':digest,'exact_nn_palette_alpha_reconstruction':True,'opaque_pixels_lost':0,'source_gutters':[bounds[0],bounds[1],192-bounds[2],256-bounds[3]],'source_native_corners_clear':all(actual.getpixel(p)[3]==0 for p in [(0,0),(47,0),(0,63),(47,63)])})
assert recon.tobytes()==native.tobytes();metrics['all32_exact_reconstruction']=True;metrics['unique_native_drawings']=len(set(digests));assert metrics['unique_native_drawings']==32
for row,d in enumerate(m['directions']):
 strip=native.crop((0,row*64,384,(row+1)*64));board=Image.new('RGBA',(1536,512))
 for j,bg in enumerate([(238,236,225,255),(22,27,36,255)]):
  comp=Image.new('RGBA',strip.size,bg);comp.alpha_composite(strip);board.paste(comp.resize((1536,256),Image.Resampling.NEAREST),(0,j*256))
 name=P+'_'+d+'_light_dark_4x.png';assert not (O/name).exists();board.save(O/name);metrics['artifacts'].append(name)
 # Exact whole-cell gait contacts, no anatomical editing.
 board=Image.new('RGBA',(1536,512),(238,236,225,255))
 for j,col in enumerate([2,4,6,7]):
  cell=native.crop((col*48,row*64,(col+1)*48,(row+1)*64));comp=Image.new('RGBA',(48,64),(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((384,512),Image.Resampling.NEAREST),(j*384,0))
 name=P+'_'+d+'_walk2_walk4_run6_run7_8x.png';assert not (O/name).exists();board.save(O/name);metrics['artifacts'].append(name)
board=Image.new('RGBA',(3*4*48*5,320),(238,236,225,255))
for a,(actor,version) in enumerate([('gabar','v7'),('olezhka','v2b'),('timka','v2c')]):
 im=Image.open(W/f'assets/source_art/characters/{actor}/world_native_{version}.png').convert('RGBA')
 for row in range(4):
  cell=im.crop((0,row*64,48,(row+1)*64));comp=Image.new('RGBA',cell.size,(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((240,320),Image.Resampling.NEAREST),((a*4+row)*240,0))
name=P+'_family_idle_5x.png';assert not (O/name).exists();board.save(O/name);metrics['artifacts'].append(name)

oldmaster=Image.open(S/'world_master_v1.png').convert('RGBA');oldnative=Image.open(S/'world_native_v1.png').convert('RGBA');raw2=Image.open(S/'world_master_v2.png').convert('RGBA')
chain=[]
for version,baseversion,cell in [('v2a','v1',(1,7)),('v2b','v2a',(2,4)),('v2c','v2b',(2,7))]:
 recipe=json.loads((S/('world_'+version+'_assembly.json')).read_text());basepath=S/('world_master_'+baseversion+'.png');targetpath=S/('world_master_'+version+'.png');base=Image.open(basepath).convert('RGBA');target=Image.open(targetpath).convert('RGBA')
 assert sha(basepath)==recipe['base_sha256'] and sha(targetpath)==recipe['output_sha256'] and sha(S/'world_master_v2.png')==recipe['replacement_sha256']
 assert tuple(recipe['changed_cell'])==cell
 for index,entry in enumerate(recipe['cells']):
  row,column=divmod(index,8);box=(column*192,row*256,(column+1)*192,(row+1)*256);expected=(raw2 if (row,column)==cell else base).crop(box).tobytes()
  assert target.crop(box).tobytes()==expected==Image.open(W/entry['source']).convert('RGBA').crop(tuple(entry['rect'])).tobytes()
  assert hashlib.sha256(expected).hexdigest()==entry['rgba_sha256']
 chain.append({'version':version,'base_version':baseversion,'whole_cell':list(cell),'exact32_recipe_cells':True})
changedsource=[];changednative=[]
for index in range(32):
 row,column=divmod(index,8);sourcebox=(column*192,row*256,(column+1)*192,(row+1)*256);nativebox=(column*48,row*64,(column+1)*48,(row+1)*64)
 if oldmaster.crop(sourcebox).tobytes()!=master.crop(sourcebox).tobytes():changedsource.append(index)
 if oldnative.crop(nativebox).tobytes()!=native.crop(nativebox).tobytes():changednative.append(index)
assert changedsource==changednative==[15,20,23]
metrics['whole_cell_assembly_chain']=chain;metrics['changed_source_cells']=changedsource;metrics['changed_native_cells']=changednative;metrics['other29_rgba_exact_v1']=True
# Three exact whole-cell corrections before/after, plus unchanged counterpart.
board=Image.new('RGBA',(4*48*8,3*64*8),(238,236,225,255))
for ri,(row,column,counterpart) in enumerate([(1,7,6),(2,4,2),(2,7,6)]):
 for ci,(image,col) in enumerate([(oldnative,counterpart),(oldnative,column),(native,column),(native,counterpart)]):
  cell=image.crop((col*48,row*64,(col+1)*48,(row+1)*64));comp=Image.new('RGBA',(48,64),(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((384,512),Image.Resampling.NEAREST),(ci*384,ri*512))
name=P+'_three_cells_counterpart_before_after_8x.png';assert not (O/name).exists();board.save(O/name);metrics['artifacts'].append(name)

# Local private photo verification: only checksum is recorded, never pixels or path.
ref=R/'assets/references/characters/timka_ref01.png';ref_sha=sha(ref);assert ref_sha=='63a3a1086570dcc5be30f80e363099b88ff77650385f26cb21ce1fd9097377c0';metrics['private_reference_local_sha256_verified']=ref_sha
assert all(sha(W/p)==h for p,h in inventory.items());metrics['source_inventory_unchanged_after_reconstruction']=True
path=O/(P+'_metrics.json');assert not path.exists();path.write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['frames','source_inventory_sha256']},indent=2))
