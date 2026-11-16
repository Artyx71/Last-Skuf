from pathlib import Path
from PIL import Image
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists(),p;p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assets=sorted(p for p in (W/'game/assets/art/characters').rglob('*') if p.is_file() and p.suffix in ['.png','.json'])
crit=assets+sorted(p for p in (W/'game/assets/art/characters').rglob('*.import'))
for d in ['enemies','combat_polish','yakuza']:
 crit+=sorted(p for p in (W/'game/assets/art'/d).rglob('*') if p.is_file() and p.suffix in ['.png','.json'])
crit+=[W/p for p in ['AGENTS.md','README.md','docs/PROJECT_GATES.md','docs/ART_BIBLE.md','docs/SECURITY_AND_RIGHTS.md','planning/PHASES.md','specs/CHARACTER_EXPANSION_SPEC.md','specs/P06_COMBAT_ACCEPTANCE.md','automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json','automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json','game/scripts/actors/character_frames.gd','game/scripts/actors/character_player.gd','game/scripts/actors/polish_frames.gd','game/scripts/actors/pixel_presentation.gd','game/scripts/actors/player.gd','game/scripts/ai/enemy_actor.gd','game/scripts/core/character_lab.gd','game/scripts/systems/combat_system.gd','game/scripts/systems/character_combat_profile.gd','game/scripts/systems/character_scene_policy.gd','game/scripts/systems/character_catalog.gd','game/resources/characters/catalog.json','game/resources/characters/sandbox_scenes.json','game/resources/characters/combat_profiles.json','game/resources/combat/finishers.json']]
crit+=sorted((W/'game/scripts/abilities').glob('*.gd'));crit=[p for p in sorted(set(crit)) if p.exists()];current={str(p.relative_to(W)):sha(p) for p in crit};write('critical-source-freeze.json',{'reported_HEAD':'fa8693a36eaba56825f02ef74c09bbec38050a35','binding':'exact file bytes, not automatic full HEAD/merge approval','files':current,'private_reference_bytes_or_manifest_copied':False})
checks=[]
for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha']:
 for kind in ['world','action','finisher']+(['roll'] if actor=='ryzhik' else [])+(['moving_shot'] if actor=='pasha' else []):
  base=W/'game/assets/art/characters'/actor;meta=json.loads((base/(kind+'.json')).read_text());im=Image.open(base/meta['file']).convert('RGBA');sock=json.loads((base/(kind+'.sockets.json')).read_text());framechecks=[]
  for i,f in enumerate(meta['frames']):
   x,y,w,h=f['rect'];cell=im.crop((x,y,x+w,y+h));rh=hashlib.sha256(cell.tobytes()).hexdigest();s=sock['frames'][i];pt=s['clothing'];valid=0<=pt[0]<w and 0<=pt[1]<h;opacity=cell.getpixel(tuple(pt))[3] if valid else None
   framechecks.append({'index':i,'direction':f.get('direction'),'column':f.get('column'),'RGBA_SHA':rh,'metadata_RGBA_exact':rh==f.get('rgba_sha256'),'socket_frame_RGBA_exact':rh==s.get('source_frame_rgba_sha256'),'socket':pt,'socket_on_opaque':opacity==255,'bounds':cell.getbbox()})
  checks.append({'actor':actor,'kind':kind,'schema':meta['schema'],'profile':meta.get('layout_profile'),'size':im.size,'dimensions_exact':list(im.size)==meta['dimensions'],'frame_size':meta['frame_size'],'pivot':meta['pivot'],'cells':len(framechecks),'actual_unique_RGBA':len(set(x['RGBA_SHA'] for x in framechecks)),'sheet_SHA':sha(base/meta['file']),'sheet_metadata_SHA_exact':sha(base/meta['file'])==meta['sha256'],'sockets_sheet_SHA_exact':sock['sheet_sha256']==sha(base/meta['file']),'socket_entries':len(sock['frames']),'binary_alpha':set(im.getchannel('A').getdata())<={0,255},'opaque_colors':len({p[:3] for p in im.get_flattened_data() if p[3]}),'animations_source_columns':meta['animations_source_columns'],'all_frame_checks_ok':all(f['metadata_RGBA_exact'] and f['socket_frame_RGBA_exact'] and f['socket_on_opaque'] for f in framechecks),'frames':framechecks})
write('player-pixel-socket-metrics.json',{'sheets':checks,'actual_source_cells':sum(x['cells'] for x in checks),'all_ok':all(x['all_frame_checks_ok'] and x['binary_alpha'] and x['sheet_metadata_SHA_exact'] and x['sockets_sheet_SHA_exact'] for x in checks),'Timka84':sum(x['cells'] for x in checks if x['actor']=='timka'),'scope':'Independent native-source structure and opaque anchor checks; actual garment/socket visual correctness additionally viewed in runtime samples and exact accepted source reused.'})
index=json.loads((R/'reports/phases/P06/lead-full-gate-preflight-01/component-reuse-index.json').read_text());rows=[];refs=[]
for row in index['rows']:
 art=[]
 for ref in row['accepted_reviews']:
  p=(W if ref['base']=='WORK' else R)/ref['path'];actual=sha(p);refs.append(ref|{'current_SHA':actual,'exact':actual==ref['sha256']})
 if 'source_hashes.json' in row.get('native_entries',{}):
  ref=row['native_entries']['source_hashes.json'];p=(W if ref['base']=='WORK' else R)/ref['path'];d=json.loads(p.read_text());prefix='game/assets/art/characters/'+row['actor']+'/' if row.get('actor') else ''
  keys=[k for k in d if (prefix and k.startswith(prefix)) or (row['id']=='cast_portrait_dialogue' and k.startswith('game/assets/art/characters/') and '/portraits.' in k)];art=[{'path':k,'old_SHA':d[k],'current_SHA':current.get(k) or sha(W/k),'exact':d[k]==(current.get(k) or sha(W/k))} for k in keys]
 rows.append({'id':row['id'],'own_art_keys':art,'all_checked_own_art_exact':all(x['exact'] for x in art),'historical_statuses_preserved':[r['status'] for r in row['accepted_reviews']],'historical_native_relabelled_current':False})
write('component-exact-reuse.json',{'rows':rows,'review_refs':refs,'verified_review_count':len(refs),'all_review_SHA_exact':all(x['exact'] for x in refs),'all_checked_actor_art_exact':all(x['all_checked_own_art_exact'] for x in rows),'changed_runtime_code_not_implicitly_accepted':True})
# Local references stay local: record only IDs and approved/actual SHA, never raw/manifest copies.
private=json.loads((R/'assets/references/manifest.json').read_text());ids=['gabar','olezhka','timka','ryzhik','tega','pasha','kaban','ellana','elya','yakuza'];local=[]
for id in ids:
 f=next(f for f in private if f['id']==id);local.append({'actor':id,'approved_SHA':f['sha256'],'actual_SHA':sha(R/f['path']),'exact':sha(R/f['path'])==f['sha256'],'personally_viewed_local_pair':True})
write('local-likeness-reference-check.json',{'pairs':local,'all_correct_reference_SHA_match':all(x['exact'] for x in local),'raw_or_manifest_bytes_copied':False,'raw_uploaded_to_generation':False,'likeness_scope':'Ten fictional/caricatured portrait identities independently visually compared to their own approved local references; no broad release rights approval.'})
print(json.dumps({'critical_files':len(current),'sheets':len(checks),'cells':sum(x['cells'] for x in checks),'all_socket_pixel_checks':all(x['all_frame_checks_ok'] for x in checks),'accepted_reviews_exact':all(x['exact'] for x in refs),'all_actor_art_exact':all(x['all_checked_own_art_exact'] for x in rows),'Timka84':sum(x['cells'] for x in checks if x['actor']=='timka')}))
