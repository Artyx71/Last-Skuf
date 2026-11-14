from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,sys,datetime
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';S=W/'assets/source_art/characters/timka';O=R/'reports/phases/P06/art-preflight';P='timka_world_left7_preflight_v3a';sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest()
paths=['assets/source_art/characters/timka/'+n for n in ['world_master_v1.png','world_native_v1.png','world_master_v2c.png','world_native_v2c.png','world_master_v3a.png','world_native_v3a.png','world_manifest_v3a.json','world_v3a_assembly.json','world_left7_master_v3.png','world_left7_v3_generation_metadata.json','world_left7_v3_prompt.txt','world_v3_references.json','left7_pose_olezhka_reference_16x.png','left7_identity_timka_idle_reference_16x.png','portraits_master_v1.png']]+['assets/source_art/characters/place_actor_pose.py','assets/source_art/characters/pack_actor_sheet.py','assets/source_art/characters/pack_portraits.py','assets/source_art/characters/olezhka/world_native_v2b.png','docs/ART_BIBLE.md','specs/CHARACTER_EXPANSION_SPEC.md'];inventory={p:sha(W/p) for p in paths}
recipe=json.loads((S/'world_v3a_assembly.json').read_text());meta=json.loads((S/'world_left7_v3_generation_metadata.json').read_text());m=json.loads((S/'world_manifest_v3a.json').read_text());figure=Image.open(S/'world_left7_master_v3.png').convert('RGBA');native=Image.open(S/'world_native_v3a.png').convert('RGBA');master=Image.open(S/'world_master_v3a.png').convert('RGBA');oldmaster=Image.open(S/'world_master_v2c.png').convert('RGBA');oldnative=Image.open(S/'world_native_v2c.png').convert('RGBA')
assert sha(S/'world_left7_master_v3.png')==recipe['pose_sha256']==meta['master_sha256'];assert sha(S/'world_master_v3a.png')==recipe['output_sha256']==m['master_sha256']=='c5dd8eac8df1f39e3cbf0e5d61932262d58d91900624c602e334a0bf4400a4d4';assert sha(S/'world_native_v3a.png')==m['sha256']=='aef19877133f41d15e85f4467defa8a7f86a0cc8df163eee52d63f387190e27e'
assert list(figure.size)==meta['actual_canvas']==recipe['pose_canvas']==[1086,1448];assert sha(S/'world_left7_v3_prompt.txt')==meta['prompt_sha256']
for entry in meta['references']:assert sha(W/entry['path'])==entry['sha256']
refrecipe=json.loads((S/'world_v3_references.json').read_text())
for entry in refrecipe['references']:
 if entry['target_cell']!='left7':continue
 source=Image.open(W/entry['source']).convert('RGBA');expected=source.crop(tuple(entry['whole_cell_rect'])).resize((768,1024),Image.Resampling.NEAREST);actual=Image.open(S/entry['file']).convert('RGBA');assert sha(W/entry['source'])==entry['source_sha256'] and sha(S/entry['file'])==entry['sha256'] and expected.tobytes()==actual.tobytes()
bounds=figure.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox();assert list(bounds)==recipe['complete_figure_bounds']==[164,167,931,1263]
resized=figure.crop(bounds).resize(tuple(recipe['resized_complete_figure']),Image.Resampling.NEAREST);assert rgba(resized)==recipe['resized_rgba_sha256'];cell=Image.new('RGBA',(192,256));cell.paste(resized,tuple(recipe['placement']));assert rgba(cell)==recipe['output_cell_rgba_sha256'];assert cell.tobytes()==master.crop((1344,256,1536,512)).tobytes();assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data())
changedsource=[];changednative=[]
for index in range(32):
 row,col=divmod(index,8);sb=(col*192,row*256,(col+1)*192,(row+1)*256);nb=(col*48,row*64,(col+1)*48,(row+1)*64)
 if oldmaster.crop(sb).tobytes()!=master.crop(sb).tobytes():changedsource.append(index)
 if oldnative.crop(nb).tobytes()!=native.crop(nb).tobytes():changednative.append(index)
assert changedsource==changednative==[15]
sys.path.insert(0,str(W/'assets/source_art/characters'));from pack_portraits import PALETTE
colors=[tuple(bytes.fromhex(x)) for x in PALETTE];pal=Image.new('P',(1,1));pal.putpalette([c for color in colors for c in color]+list(colors[0])*(256-len(colors)))
f=m['frames'][15];packed=cell.resize((48,64),Image.Resampling.NEAREST);alpha=packed.getchannel('A').point(lambda a:255 if a>=128 else 0);packed=packed.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');packed.putalpha(alpha);packed.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));expected=Image.new('RGBA',(48,64));expected.paste(packed,tuple(f['translate_native']));actual=native.crop((336,64,384,128));assert expected.tobytes()==actual.tobytes();assert sum(alpha.get_flattened_data())==sum(expected.getchannel('A').get_flattened_data());assert rgba(actual)==f['rgba_sha256']
artifacts=[]
for name,background in [('light',(238,236,225,255)),('dark',(22,27,36,255))]:
 board=Image.new('RGBA',(5*48*8,64*8),background);world1=Image.open(S/'world_native_v1.png').convert('RGBA');ole=Image.open(W/'assets/source_art/characters/olezhka/world_native_v2b.png').convert('RGBA')
 for ci,cell in enumerate([world1.crop((288,64,336,128)),oldnative.crop((336,64,384,128)),actual,world1.crop((0,64,48,128)),ole.crop((336,64,384,128))]):
  comp=Image.new('RGBA',cell.size,background);comp.alpha_composite(cell);board.paste(comp.resize((384,512),Image.Resampling.NEAREST),(ci*384,0))
 path=O/(P+'_'+name+'_counterpart_v2c_v3a_idle_olezhka_8x.png');assert not path.exists();board.save(path);artifacts.append(path.name)
# The complete generated canvas, reduced for inspection without body-part cropping.
path=O/(P+'_raw_complete_canvas_half.png');assert not path.exists();figure.resize((543,724),Image.Resampling.NEAREST).save(path);artifacts.append(path.name)
metrics={'schema':1,'reviewer':'/root/art_timka_recovery','reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'ISOLATED_LEFT7_SOURCE_CELL_ONLY','all32_freshly_reviewed':False,'source_only_acceptance':False,'runtime_approval':False,'phase_approval':False,'native_sha256':sha(S/'world_native_v3a.png'),'master_sha256':sha(S/'world_master_v3a.png'),'raw_pose_sha256':sha(S/'world_left7_master_v3.png'),'raw_pose_canvas':list(figure.size),'alpha128_complete_bounds':list(bounds),'whole_figure_nn_size':recipe['resized_complete_figure'],'placement':recipe['placement'],'resized_alpha_sum_equals_placement':True,'source_changed_indices':changedsource,'native_changed_indices':changednative,'other31_rgba_exact_v2c':True,'left7_exact_native_reconstruction':True,'native_left7_bounds':list(actual.getbbox()),'native_left7_rgba_sha256':rgba(actual),'source_inventory_sha256':inventory,'artifacts':artifacts}
assert all(sha(W/n)==h for n,h in inventory.items());path=O/(P+'_metrics.json');assert not path.exists();path.write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['source_inventory_sha256','artifacts']},indent=2))
