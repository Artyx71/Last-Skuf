from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path('AYAY_SDD_v1.0');work=root/'.autopilot/worktrees/P06';out=root/'reports/phases/P06/lead-timka-present-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sd=work/'assets/source_art/characters/timka';rr=root/'reports/phases/P06/art-preflight';decision=rr/'timka_finisher_supported_v2_source.json';d=json.loads(decision.read_text());assert sha(decision)=='f3f8e29f760dff803500deaa0cb782169bad5c65402ad3547107d3040a870feb';assert d['source_cells']==24 and d['reviewed_cell_indices']==list(range(24)) and d['all_required_cells_freshly_reviewed'] and d['source_only_acceptance'] and not d['runtime_approval'];assert sha(sd/'finisher_native_supported_v2.png')==d['native_sha256']==sha(work/'game/assets/art/characters/timka/finisher_sheet.png');assert sha(sd/'finisher_manifest_supported_v2.json')==d['manifest_sha256'];assert sha(sd/'finisher_master_v4a.png')==d['master_sha256']
for rel,h in d['source_inventory_sha256'].items():assert sha(work/rel)==h,rel
for rel,h in d['review_artifacts_sha256'].items():assert sha(rr/rel)==h,rel
native=Image.open(sd/'finisher_native_v4a.png').convert('RGBA');compact=Image.open(sd/'finisher_native_supported_v2.png').convert('RGBA');assert compact.size==(288,256);mapping=[0,1,2,5,6,7]
def cell(im,index,cols,w=48,h=64):return im.crop((index%cols*w,index//cols*h,index%cols*w+w,index//cols*h+h)).tobytes()
for row in range(4):
 for col,sourcecol in enumerate(mapping):assert cell(compact,row*6+col,6)==cell(native,row*8+sourcecol,8)
prior=Image.open(sd/'finisher_native_supported_v1.png').convert('RGBA');delta=[i for i in range(24) if cell(compact,i,6)!=cell(prior,i,6)];assert delta==[21],delta
master=Image.open(sd/'finisher_master_v4a.png').convert('RGBA');base=Image.open(sd/'finisher_master_v2b.png').convert('RGBA');changed=[i for i in range(32) if cell(master,i,8,192,256)!=cell(base,i,8,192,256)];assert changed==[29]
refs=json.loads((sd/'finisher_up5_v4_references.json').read_text());assert refs['raw_photos_uploaded'] is False
for e in refs['references']:assert e['path'].startswith('assets/source_art/') and sha(work/e['path'])==e['sha256']
gen=json.loads((sd/'finisher_up5_v4_generation.json').read_text());assert sha(work/gen['copied_output'])==gen['sha256'];assert sha(work/gen['prompt'])==gen['prompt_sha256']
for rel in ['finisher_native_supported_v2.png','finisher_manifest_supported_v2.json','finisher_up5_v4_generation.json','finisher_up5_v4_references.json','finisher_up5_v4_prompt.txt','finisher_v4a_assembly.json']:
 t=out/'FIN-source'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(sd/rel,t)
for rel in d['review_artifacts_sha256']:
 t=out/'FIN-source-review'/rel;t.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(rr/rel,t)
shutil.copyfile(decision,out/'FIN-source-review'/decision.name)
anchors=[]
for kind,count,cols in [('world',32,8),('action',28,7)]:
 a=work/f'game/assets/art/characters/timka/{kind}.sockets.json';s=json.loads(a.read_text());png=work/f'game/assets/art/characters/timka/{kind}_sheet.png';im=Image.open(png).convert('RGBA');assert len(s['frames'])==count and s['sheet_sha256']==sha(png)
 for i,e in enumerate(s['frames']):
  x,y=e['clothing'];assert e['index']==i and isinstance(x,int) and isinstance(y,int) and im.getpixel((i%cols*48+x,i//cols*64+y))[3]==255
 anchors.append({'kind':kind,'count':count,'socket_sha256':sha(a),'opaque_integer_points':True})
private=json.loads((root/'assets/references/manifest.json').read_text());assert all(sha(root/i['path'])==i['sha256'] for i in private)
result={'schema':1,'source_ART_SHA256':sha(decision),'source_ART_inputs_verified':len(d['source_inventory_sha256']),'source_ART_review_files_verified':len(d['review_artifacts_sha256']),'adopted_reviewed_native_exact':True,'whole_cell_compaction_checked':24,'mapping':mapping,'changed_compact_indices_vs_prior':delta,'changed_master_indices_vs_v2b':changed,'other23compact_and31master_cells_byte_exact':True,'new_generation_refs':refs,'raw_photos_copied_or_uploaded_by_reviewer':False,'root_private_manifest_count':len(private),'root_private_manifest_sha256':sha(root/'assets/references/manifest.json'),'private_manifest_hash_errors':0,'git_history_or_ignore_tests_rerun':False,'WORLD_ACTION_socket_checks':anchors,'socket_semantic_clothing_not_inferred_from_color':True,'FIN_sockets_or_runtime_approval':False,'prime_approval':False}
(out/'FIN-adoption-provenance-privacy.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'FINcells':24,'compact_delta':delta,'master_delta':changed,'source_refs':2,'private_manifest_count':len(private),'W_A_sockets':60}))
