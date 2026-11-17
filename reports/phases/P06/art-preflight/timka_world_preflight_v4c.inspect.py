from pathlib import Path
from PIL import Image,ImageOps
import hashlib,json,datetime,sys
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';S=W/'assets/source_art/characters/timka';O=R/'reports/phases/P06/art-preflight';P='timka_world_preflight_v4c';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest()
names=['world_master_v1.png','world_native_v1.png','world_master_v3b.png','world_native_v3b.png','world_master_v4a.png','world_native_v4a.png','world_master_v4b.png','world_native_v4b.png','world_master_v4c.png','world_native_v4c.png','world_manifest_v4c.json','world_v4a_assembly.json','world_v4b_assembly.json','world_v4c_assembly.json','world_left7_master_v3.png','world_right4_master_v3.png','world_left7_master_v4.png','world_right4_master_v4.png','world_right7_master_v4.png','world_left7_v4_generation_metadata.json','world_right4_v4_generation_metadata.json','world_right7_v4_generation_metadata.json','world_left7_v4_prompt.txt','world_right4_v4_prompt.txt','world_right7_v4_prompt.txt','world_v4_family_references.json','world_right7_v4_references.json','left6_timka_family_source_reference_4x.png','right2_timka_family_source_reference_4x.png','right6_timka_family_source_reference_4x.png','right7_pose_olezhka_source_reference_4x.png','portraits_master_v1.png','portrait_generation_metadata.json']
paths=['assets/source_art/characters/timka/'+n for n in names]+['assets/source_art/characters/olezhka/world_native_v2b.png','assets/source_art/characters/olezhka/world_manifest_v2b.json','assets/source_art/characters/olezhka/world_master_v2.png','assets/source_art/characters/gabar/world_native_v7.png','assets/source_art/characters/place_actor_pose.py','assets/source_art/characters/pack_actor_sheet.py','assets/source_art/characters/pack_portraits.py','docs/ART_BIBLE.md','docs/CHARACTER_BIBLE.md','specs/CHARACTER_EXPANSION_SPEC.md'];inventory={n:sha(W/n) for n in paths}
master=Image.open(S/'world_master_v4c.png').convert('RGBA');native=Image.open(S/'world_native_v4c.png').convert('RGBA');manifest=json.loads((S/'world_manifest_v4c.json').read_text());originalmaster=Image.open(S/'world_master_v1.png').convert('RGBA');originalnative=Image.open(S/'world_native_v1.png').convert('RGBA')
assert master.size==(1536,1024) and native.size==(384,256);assert sha(S/'world_master_v4c.png')==manifest['master_sha256']=='79ab1a0ebd2e06e4793d83c8ed1d2f336f502d37228f3df1e8fb590ff8c114c0';assert sha(S/'world_native_v4c.png')==manifest['sha256']=='8e505380e88fb538988310a364c6b16a135cb69b94d136fe00307c8a49a99cea'
chain=[]
for version,basename,poseid,row,col in [('v4a','v3b','left7',1,7),('v4b','v4a','right4',2,4),('v4c','v4b','right7',2,7)]:
 recipe=json.loads((S/('world_'+version+'_assembly.json')).read_text());meta=json.loads((S/('world_'+poseid+'_v4_generation_metadata.json')).read_text());rawpath=S/('world_'+poseid+'_master_v4.png');raw=Image.open(rawpath).convert('RGBA');base=Image.open(S/('world_master_'+basename+'.png')).convert('RGBA');target=Image.open(S/('world_master_'+version+'.png')).convert('RGBA')
 assert sha(rawpath)==meta['master_sha256']==recipe['pose_sha256'];assert sha(S/('world_'+poseid+'_v4_prompt.txt'))==meta['prompt_sha256'];assert sha(S/('world_master_'+basename+'.png'))==recipe['base_sha256'];assert sha(S/('world_master_'+version+'.png'))==recipe['output_sha256'];assert list(raw.size)==recipe['pose_canvas']==meta['actual_canvas'];assert recipe['changed_cell']==[row,col]
 for ref in meta['references']:assert sha(W/ref['path'])==ref['sha256']
 bounds=raw.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert list(bounds)==recipe['complete_figure_bounds'];resized=raw.crop(bounds).resize(tuple(recipe['resized_complete_figure']),Image.Resampling.NEAREST);assert rgba(resized)==recipe['resized_rgba_sha256'];cell=Image.new('RGBA',(192,256));cell.paste(resized,tuple(recipe['placement']));assert rgba(cell)==recipe['output_cell_rgba_sha256'] and sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data())
 changed=[]
 for index in range(32):
  rr,cc=divmod(index,8);box=(cc*192,rr*256,(cc+1)*192,(rr+1)*256)
  if target.crop(box).tobytes()!=base.crop(box).tobytes():changed.append(index)
  if index==row*8+col:assert target.crop(box).tobytes()==cell.tobytes()
 assert changed==[row*8+col]
 chain.append({'version':version,'base':basename,'raw_pose':str(rawpath.relative_to(W)),'changed_cell':[row,col],'complete_alpha128_bounds':list(bounds),'uniform_nn_size':recipe['resized_complete_figure'],'placement':recipe['placement'],'source_cell_exact':True,'other31_exact_previous':True,'resized_alpha_preserved_during_placement':True})
# Reconstruct all current whole-cell generation references, not their filenames.
family=json.loads((S/'world_v4_family_references.json').read_text())
for ref in family['references']:
 expected=originalmaster.crop(tuple(ref['whole_cell_rect'])).resize((768,1024),Image.Resampling.NEAREST);actual=Image.open(S/ref['file']).convert('RGBA');assert ref['source_sha256']==sha(S/'world_master_v1.png') and ref['sha256']==sha(S/ref['file']) and expected.tobytes()==actual.tobytes()
ref=json.loads((S/'world_right7_v4_references.json').read_text());ole_manifest=json.loads((W/'assets/source_art/characters/olezhka/world_manifest_v2b.json').read_text());assert ref['source']==ole_manifest['master'];assert sha(W/ref['source'])==ref['source_sha256']==ole_manifest['master_sha256'];expected=Image.open(W/ref['source']).convert('RGBA').crop(tuple(ref['whole_cell_rect'])).resize((768,1024),Image.Resampling.NEAREST);actual=Image.open(S/ref['file']).convert('RGBA');assert sha(S/ref['file'])==ref['sha256'] and expected.tobytes()==actual.tobytes()
changedsource=[];changednative=[]
for index in range(32):
 row,col=divmod(index,8);sb=(col*192,row*256,(col+1)*192,(row+1)*256);nb=(col*48,row*64,(col+1)*48,(row+1)*64)
 if master.crop(sb).tobytes()!=originalmaster.crop(sb).tobytes():changedsource.append(index)
 if native.crop(nb).tobytes()!=originalnative.crop(nb).tobytes():changednative.append(index)
assert changedsource==changednative==[15,20,23]
sys.path.insert(0,str(W/'assets/source_art/characters'));from pack_portraits import PALETTE
colors=[tuple(bytes.fromhex(c)) for c in PALETTE];pal=Image.new('P',(1,1));pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)));reconstructed=Image.new('RGBA',native.size);frames=[];digests=[]
assert manifest['directions']==['down','left','right','up'] and manifest['source_cells']==len(manifest['frames'])==32 and manifest['pivot']==[24,58]
for index,frame in enumerate(manifest['frames']):
 row,col=divmod(index,8);assert frame['direction']==manifest['directions'][row] and frame['column']==col and frame['source_rect']==[col*192,row*256,(col+1)*192,(row+1)*256];source=master.crop(tuple(frame['source_rect']));bounds=source.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert bounds and list(bounds)==frame['source_opaque_bounds'] and bounds[0]>0 and bounds[1]>0 and bounds[2]<192 and bounds[3]<256
 cell=source.resize((48,64),Image.Resampling.NEAREST);alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0);cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(alpha);cell.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));out=Image.new('RGBA',(48,64));out.paste(cell,tuple(frame['translate_native']));actual=native.crop((col*48,row*64,(col+1)*48,(row+1)*64));assert out.tobytes()==actual.tobytes() and rgba(actual)==frame['rgba_sha256'];assert sum(alpha.get_flattened_data())==sum(out.getchannel('A').get_flattened_data());assert frame['translate_native']==manifest['frames'][row*8]['translate_native'];reconstructed.paste(out,(col*48,row*64));digests.append(rgba(actual));frames.append({'index':index,'direction':frame['direction'],'column':col,'source_bounds':list(bounds),'native_bounds':list(actual.getbbox()),'translate_native':frame['translate_native'],'native_rgba_sha256':rgba(actual),'exact_reconstruction':True,'opaque_placement_loss':0})
assert reconstructed.tobytes()==native.tobytes() and len(set(digests))==32
artifacts=[]
for row,direction in enumerate(manifest['directions']):
 strip=native.crop((0,row*64,384,(row+1)*64));board=Image.new('RGBA',(1536,512))
 for j,bg in enumerate([(238,236,225,255),(22,27,36,255)]):
  comp=Image.new('RGBA',strip.size,bg);comp.alpha_composite(strip);board.paste(comp.resize((1536,256),Image.Resampling.NEAREST),(0,j*256))
 name=P+'_'+direction+'_light_dark_4x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
 board=Image.new('RGBA',(4*48*8,64*8),(238,236,225,255))
 for ci,col in enumerate([2,4,6,7]):
  cell=native.crop((col*48,row*64,(col+1)*48,(row+1)*64));comp=Image.new('RGBA',(48,64),(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((384,512),Image.Resampling.NEAREST),(ci*384,0))
 name=P+'_'+direction+'_walk2_walk4_run6_run7_8x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
board=Image.new('RGBA',(3*4*48*5,320),(238,236,225,255))
for ai,(actor,version) in enumerate([('gabar','v7'),('olezhka','v2b'),('timka','v4c')]):
 im=Image.open(W/f'assets/source_art/characters/{actor}/world_native_{version}.png').convert('RGBA')
 for row in range(4):
  cell=im.crop((0,row*64,48,(row+1)*64));comp=Image.new('RGBA',(48,64),(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((240,320),Image.Resampling.NEAREST),((ai*4+row)*240,0))
name=P+'_family_idles_5x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
board=Image.new('RGBA',(4*48*8,3*64*8),(238,236,225,255))
for ri,(row,target,reference) in enumerate([(1,7,6),(2,4,2),(2,7,6)]):
 for ci,(im,col) in enumerate([(originalnative,reference),(originalnative,target),(native,target),(native,reference)]):
  cell=im.crop((col*48,row*64,(col+1)*48,(row+1)*64));comp=Image.new('RGBA',(48,64),(238,236,225,255));comp.alpha_composite(cell);board.paste(comp.resize((384,512),Image.Resampling.NEAREST),(ci*384,ri*512))
name=P+'_three_cells_counterpart_v1_final_8x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
metrics={'schema':1,'reviewer':'/root/art_timka_recovery','scope':'FULL_WORLD_SOURCE_CANDIDATE_FRESH32_REVIEW_ONLY','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'master_sha256':sha(S/'world_master_v4c.png'),'native_sha256':sha(S/'world_native_v4c.png'),'native_alpha':sorted(set(native.getchannel('A').get_flattened_data())),'native_opaque_colors':len({q[:3] for q in native.get_flattened_data() if q[3]}),'all32_exact_nn_palette_alpha_reconstruction':True,'unique_native_drawings':len(set(digests)),'changed_source_indices_vs_original':changedsource,'changed_native_indices_vs_original':changednative,'other29_source_native_rgba_exact_original':True,'current_three_whole_figure_chains':chain,'generation_reference_reconstruction_verified':True,'frames':frames,'source_inventory_sha256':inventory,'artifacts':artifacts,'runtime_tested':False,'phase_approval':False};assert all(sha(W/n)==h for n,h in inventory.items());metrics['source_inventory_unchanged_after_reconstruction']=True;path=O/(P+'_metrics.json');assert not path.exists();path.write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['frames','source_inventory_sha256','artifacts']},indent=2))
