from pathlib import Path
import hashlib,json,subprocess,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-full-gate-preflight-01';B=W/'reports/phases/P06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
common=['game/scripts/actors/character_player.gd','game/scripts/actors/character_frames.gd','game/scripts/actors/polish_frames.gd','game/scripts/systems/combat_system.gd','game/scripts/ai/enemy_actor.gd','game/scripts/core/character_lab.gd','game/scripts/systems/character_catalog.gd','game/scripts/systems/character_scene_policy.gd','game/scripts/systems/character_combat_profile.gd','game/resources/characters/catalog.json','game/resources/characters/sandbox_scenes.json','game/resources/characters/combat_profiles.json','game/resources/combat/finishers.json','game/scripts/systems/audio_director.gd']
rows=[
 ('gabar_base','gabar','attempt1/gabar-combat-native-02',['art-preflight/gabar-combat-native-review-v2.json','gameplay-preflight/gabar-controller-preflight-v2.json'],['game/scripts/actors/character_player.gd']),
 ('olezhka_base','olezhka','attempt1/olezhka-combat-native-01',['art-preflight/olezhka-combat-native-review-v1r.json','gameplay-preflight/olezhka-controller-preflight-v1.json'],['game/scripts/actors/character_player.gd']),
 ('oleg_guard','olezhka','guard-feedback-01/native-03',['lead-guard-feedback-01/decision.json','art-guard-feedback-01/decision.json','gameplay-guard-feedback-01/decision.json','qa-guard-feedback-01/decision.json'],['game/scripts/ui/combat_feedback.gd','game/scripts/ui/counter_feedback.gd']),
 ('timka_present','timka','timka-present-01/native-02',['lead-timka-present-01/decision.json','art-timka-present-02/decision.json','gameplay-timka-present-02/decision.json','qa-timka-present-02/decision.json'],['game/scripts/abilities/disengage.gd']),
 ('timka_prime','timka','timka-prime-01/native-03',['lead-timka-prime-02/decision.json','art-timka-prime-02/decision.json','gameplay-timka-prime-01/decision.json','qa-timka-prime-01/decision.json','qa-timka-prime-footer-01/decision.json'],['tools/verify_p06_timka_prime.py']),
 ('ryzhik_roll','ryzhik','ryzhik-roll-01/native-03',['lead-ryzhik-roll-01/decision.json','art-ryzhik-roll-02/decision.json','gameplay-ryzhik-roll-02/decision.json','qa-ryzhik-roll-02/decision.json'],['game/scripts/abilities/ground_roll.gd']),
 ('tega_environment','tega','tega-environment-01/native-03',['lead-tega-environment-03/decision.json','art-tega-environment-03/decision.json','gameplay-tega-environment-03/decision.json','qa-tega-environment-03/decision.json'],['game/scripts/abilities/environment_kick.gd','game/scripts/systems/environment_kick_runtime.gd']),
 ('pasha_moving_shot','pasha','pasha-moving-shot-01/native-03',['lead-pasha-moving-shot-01/decision.json','art-pasha-moving-shot-03/decision.json','gameplay-pasha-moving-shot-03/decision.json','qa-pasha-moving-shot-03/decision.json'],['game/scripts/abilities/moving_shot.gd','game/scripts/systems/moving_shot_runtime.gd','game/scripts/ui/ranged_feedback.gd']),
 ('cast_portrait_dialogue',None,'attempt1/cast-native-02',['art-preflight/runtime-art-preflight_v1.json'],['game/scripts/qa/cast_replay.gd','game/tests/character_dialogue_reload.gd','tools/verify_p06_cast.py'])]
extra_native={'gabar':'attempt1/world-native-02','olezhka':'attempt1/olezhka-world-native-01','timka':'attempt1/timka-world-native-02','ryzhik':'attempt1/ryzhik-world-native-01','tega':'attempt1/tega-world-native-01','pasha':'attempt1/pasha-world-native-01'}
world_review={'gabar':'gabar_world_runtime_preflight_v2.json','olezhka':'olezhka_world_runtime_preflight_v1.json','timka':'timka-world-native-review-v1.json','ryzhik':'ryzhik-world-native-review-v1.json','tega':'tega-world-native-review-v1.json','pasha':'pasha-world-native-review-v1.json'}
refs={};out=[]
def ref(p):
 assert p.is_file(),str(p);k=str(p.relative_to(R));refs[k]={'root_relative_path':k,'sha256':sha(p),'bytes':p.stat().st_size};return {'base':'WORK' if p.is_relative_to(W) else 'ROOT','path':str(p.relative_to(W if p.is_relative_to(W) else R)),'sha256':sha(p)}
for key,actor,native,reviews,extra in rows:
 D=B/native;mapfile=D/'source_hashes.json';m=read(mapfile);assert isinstance(m,dict) and all(isinstance(v,str) and len(v)==64 for v in m.values())
 changed=[k for k,v in m.items() if not (W/k).is_file() or sha(W/k)!=v]
 critical=common+extra if actor else ['game/scripts/ui/cast_viewer.gd','game/scripts/ui/character_portrait.gd','game/scripts/systems/character_dialogue_session.gd','game/scripts/systems/dialogue_director.gd','game/scripts/systems/character_catalog.gd','game/scripts/systems/audio_director.gd','game/scripts/core/options_store.gd','game/project.godot']+extra
 code={k:{'recorded_sha256':m.get(k),'current_sha256':sha(W/k),'exact':m.get(k)==sha(W/k)} for k in critical if (W/k).is_file()}
 aset={k:v for k,v in m.items() if k.startswith('game/assets/art/characters/'+actor+'/')} if actor else {k:v for k,v in m.items() if '/portraits' in k and k.startswith('game/assets/art/')}
 assert aset;assetdiff=[k for k,v in aset.items() if sha(W/k)!=v]
 valid=read(D/'validation.json');rd=[]
 for k in reviews:
  p=B/k
  if not p.exists():p=R/'reports/phases/P06'/k
  d=read(p);rd.append({**ref(p),'status':d.get('status'),'phase_approval':d.get('phase_approval'),'scope':d.get('scope',d.get('review_kind'))})
 entries={n:ref(D/n) for n in ['source_hashes.json','validation.json','commands.json'] if (D/n).exists()}
 results=[]
 for sub in ['live/result.json','movie/result.json','replay/result.json','result.json','process-reload.json']:
  if (D/sub).is_file():results.append(ref(D/sub))
 for p in D.rglob('*.json'):
  if p.name=='result.json' and str(p.relative_to(D)) not in [x['path'].split(native+'/')[-1] for x in results]:results.append(ref(p))
 out.append({'id':key,'actor':actor,'native_directory':'reports/phases/P06/'+native,'accepted_reviews':rd,'native_entries':entries,'result_paths':results,'historical_native_passed':valid.get('passed'),'historical_source_HEAD':valid.get('source_head'),'recorded_source_keys':len(m),'current_exact_recorded_keys':len(m)-len(changed),'changed_recorded_keys':changed,'own_art_keys_checked':len(aset),'own_art_changed':assetdiff,'critical_code_current_comparison':code,'reuse_classification':'EXACT_ART_PIXEL_REUSE_PLUS_EXPLICIT_RUNTIME_DELTA_REVIEW_AND_CURRENT_CONTROLLER_BASELINE_REQUIRED' if any(not v['exact'] for v in code.values()) else 'CRITICAL_CODE_AND_ART_EXACT_IF_ORACLE_TOOLCHAIN_ARGV_ARTIFACT_BINDINGS_ALSO_VALIDATE','old_native_claimed_fresh':False})
for actor,native in extra_native.items():
 D=B/native;m=read(D/'source_hashes.json');k='game/assets/art/characters/'+actor+'/world_sheet.png';assert k in m and sha(W/k)==m[k],(actor,k)
 p=B/'art-preflight'/world_review[actor];d=read(p)
 out.append({'id':actor+'_world','actor':actor,'native_directory':'reports/phases/P06/'+native,'accepted_reviews':[{**ref(p),'status':d.get('status'),'scope':d.get('scope',d.get('review_kind'))}],'native_entries':{n:ref(D/n) for n in ['source_hashes.json','validation.json','commands.json'] if (D/n).is_file()},'WORLD_sheet_exact':True,'WORLD_sha256':m[k],'required_critical_dependencies':['own WORLD atlas/metadata/sockets; relevant CharacterFrames projection/pivot and PixelPresentation code','controller movement physics/authority; accepted continuous all4dir32phases/joins; current controller baseline','Timka contexts additionally depend on prime/present stance mappings, already separately accepted'],'reuse_classification':'REUSE_ACCEPTED_WORLD_PIXELS_AND_RECORDED_TEMPORAL_SCOPE_WITH_EXPLICIT_RUNTIME_EQUIVALENCE_NOT_NEW_FRESH_CAPTURE'})
# Additional aggregate/reuse anchors.
anchors=['lead-character-finisher-audio-01/decision.json','lead-character-finisher-audio-01/source-freeze.json','lead-npc-visual-deferral-01/decision.json','owner-preview-20261116-08/preview.json','owner-preview-20261116-08/source_hashes.json','owner-preview-20261116-08/exports.json','owner-preview-20261116-08/owner-handoff.json','baseline-after-deferral-01/validation.json','baseline-after-deferral-01/regression/validation.json']
for k in anchors:ref(B/k)
put('component-reuse-index.json',{'schema':1,'base':'WORK','rows':out,'anchors':[{'path':k,'sha256':sha(B/k)} for k in anchors],'note':'Statuses are original bounded scope, not invented full component Lead approvals. Any changed critical code requires a real independent equivalence receipt or targeted fresh fallback. Do not discard changed keys silently.'})
put('external-input-bindings.json',{'base':'ROOT','records':list(refs.values())})
print('Indexrows',len(out),'exactcomponentdatarefs',len(refs));print('assetdifferences',[(r['id'],r.get('own_art_changed')) for r in out if r.get('own_art_changed')]);print('changedcodes',[(r['id'],[k for k,v in r.get('critical_code_current_comparison',{}).items() if not v['exact']]) for r in out[:9]])
