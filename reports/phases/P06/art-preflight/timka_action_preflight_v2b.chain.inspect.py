from pathlib import Path
from PIL import Image,ImageDraw
from collections import Counter
import hashlib,json
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';S=W/'assets/source_art/characters/timka';O=R/'reports/phases/P06/art-preflight';P='timka_action_preflight_v2b';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest();rect=lambda i:((i%8)*192,(i//8)*256,(i%8+1)*192,(i//8+1)*256)
a=json.loads((S/'action_v2a_assembly.json').read_text());b=json.loads((S/'action_v2b_assembly.json').read_text());v1=Image.open(W/a['base']).convert('RGBA');v2=Image.open(W/a['replacement']).convert('RGBA');v2a=Image.open(S/'action_master_v2a.png').convert('RGBA');v2b=Image.open(S/'action_master_v2b.png').convert('RGBA');assert sha(W/a['base'])==a['base_sha256'] and sha(W/a['replacement'])==a['replacement_sha256'];assert sha(S/'action_master_v2a.png')==a['output_sha256']==b['source_sha256'];assert sha(S/'action_master_v2b.png')==b['output_sha256'];out=Image.new('RGBA',(1536,1024));selected=[]
for e in a['entries']:
 i=e['cell'];im=Image.open(W/e['source']).convert('RGBA');cell=im.crop(tuple(e['source_rect']));assert rgba(cell)==e['rgba_sha256'] and cell.tobytes()==v2a.crop(rect(i)).tobytes();assert cell.tobytes()==(v2 if i in [6,14,22,29,30] else v1).crop(rect(i)).tobytes();out.paste(cell,rect(i)[:2]);selected.append(i)
assert out.tobytes()==v2a.tobytes() and selected==list(range(32));assert [i for i in range(32) if v1.crop(rect(i)).tobytes()!=v2a.crop(rect(i)).tobytes()]==[6,14,22,29,30]
rebuild=Image.new('RGBA',(1536,1024));details=[]
for e in b['entries']:
 i=e['cell'];cell=v2a.crop(rect(i));support=cell.getchannel('A').point(lambda x:255 if x>=128 else 0);box=support.getbbox();l,t,r,bt=box;width,height=r-l,bt-t;scale=min(1.,160/width,224/height);assert rgba(cell)==e['source_cell_rgba_sha256'] and list(box)==e['source_bounds'];oldsum=sum(x>=128 for x in cell.getchannel('A').get_flattened_data())
 if scale<1:
  assert i in [6,14,22,30] and abs(scale-e['uniform_scale'])<1e-12;size=(max(1,round(width*scale)),max(1,round(height*scale)));complete=cell.crop(box).resize(size,Image.Resampling.NEAREST);x=(192-size[0])//2;y=max(16,min(bt-size[1],240-size[1]));prepared=Image.new('RGBA',(192,256));prepared.paste(complete,(x,y));assert list(size)==e['resized_complete_figure'] and rgba(complete)==e['resized_rgba_sha256'] and [x,y]==e['placement'];assert sum(prepared.getchannel('A').get_flattened_data())==sum(complete.getchannel('A').get_flattened_data());op='uniform_fit'
 else:
  dx=max(16-l,min(0,176-r));dy=max(16-t,min(0,240-bt));prepared=cell if dx==dy==0 else Image.new('RGBA',(192,256))
  if dx or dy:prepared.paste(cell,(dx,dy))
  assert [dx,dy]==e['translation'];assert prepared.crop((l+dx,t+dy,r+dx,bt+dy)).tobytes()==cell.crop(box).tobytes();assert sum(x>=128 for x in prepared.getchannel('A').get_flattened_data())==oldsum;op='translation' if dx or dy else 'byte_exact'
 bounds=prepared.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox();assert list(bounds)==e['output_bounds'] and rgba(prepared)==e['output_cell_rgba_sha256'];assert min(bounds[0],bounds[1],192-bounds[2],256-bounds[3])>=16;assert prepared.tobytes()==v2b.crop(rect(i)).tobytes();rebuild.paste(prepared,rect(i)[:2]);details.append({'cell':i,'independent_operation':op,'independent_scale':scale,'independent_source_support_pixels':oldsum,'independent_output_support_pixels':sum(x>=128 for x in prepared.getchannel('A').get_flattened_data()),'independent_output_rgba_sha256':rgba(prepared),'recipe_matches':True})
assert rebuild.tobytes()==v2b.tobytes();meta=json.loads((S/'action_v2_generation_metadata.json').read_text());assert meta['master_sha256']==sha(S/'action_master_v2.png') and meta['prompt_sha256']==sha(S/'action_v2_prompt.txt');assert all(sha(W/e['path'])==e['sha256'] for e in meta['references']);assert meta['private_photo_uploaded'] is False
# Source pose sequences at exact relative scale. Every view contains full cells.
a_native=Image.open(S/'action_native_v2b.png').convert('RGBA');old=Image.open(S/'action_native_v1.png').convert('RGBA');world=Image.open(S/'world_native_v4c.png').convert('RGBA');board=Image.new('RGBA',(48*8,80*4),(222,219,211,255));draw=ImageDraw.Draw(board)
for row in range(4):
 for j,col in enumerate(['W',0,1,2,'W',4,5,6]):
  im=world if col=='W' else a_native;c=0 if col=='W' else col;board.alpha_composite(im.crop((c*48,row*64,(c+1)*48,(row+1)*64)),(j*48,row*80+16));draw.text((j*48+2,row*80+2),str(col),fill=(70,70,70))
n=P+'_ordered_SOURCE_ONLY_sequences_4x.png';board.resize((1536,1280),Image.Resampling.NEAREST).save(O/n)
# Old/current death comparison preserves full cells and identical diagnostic scale.
deaths=Image.new('RGBA',(48*4,80*4),(222,219,211,255));draw=ImageDraw.Draw(deaths)
for row in range(4):
 for j,(im,col,label) in enumerate([(world,0,'WORLD'),(a_native,5,'FALL'),(old,6,'OLD6'),(a_native,6,'NEW6')]):
  deaths.alpha_composite(im.crop((col*48,row*64,(col+1)*48,(row+1)*64)),(j*48,row*80+16));draw.text((j*48+2,row*80+2),label,fill=(70,70,70))
n2=P+'_wholecell_death_world_comparison_6x.png';deaths.resize((1152,1920),Image.Resampling.NEAREST).save(O/n2)
metrics=O/(P+'_metrics.json');m=json.loads(metrics.read_text());m['chain_independently_reconstructed_exact']=True;m['v2a_generated_replacements']=[6,14,22,29,30];m['v2a_other27_source_cells_exact_v1']=True;m['v2b_operation_counts']=dict(Counter(e['independent_operation'] for e in details));m['v2b_wholefigure_chain_checks']=details;m['source_cells_changed_v1_to_v2b']=[i for i in range(32) if v1.crop(rect(i)).tobytes()!=v2b.crop(rect(i)).tobytes()];m['native_cells_changed_v1_to_v2b']=[i for i in range(32) if old.crop(((i%8)*48,(i//8)*64,(i%8+1)*48,(i//8+1)*64)).tobytes()!=a_native.crop(((i%8)*48,(i//8)*64,(i%8+1)*48,(i//8+1)*64)).tobytes()];m['diagnostic_artifacts'] += [n,n2];metrics.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'operations':m['v2b_operation_counts'],'source_changed':m['source_cells_changed_v1_to_v2b'],'native_changed':m['native_cells_changed_v1_to_v2b'],'uniform_fits':[{k:e[k] for k in ['cell','independent_scale','independent_source_support_pixels','independent_output_support_pixels']} for e in details if e['independent_operation']=='uniform_fit']}))
