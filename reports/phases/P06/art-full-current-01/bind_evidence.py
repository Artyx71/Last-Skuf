from pathlib import Path
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
critical=json.loads((O/'critical-source-freeze.json').read_text())['files'];files=set();corpora=[]
base=W/'reports/phases/P06/full-native-current-source-01'
for stage in ['gabar','olezhka','counter_feedback','timka_present','timka_prime','ryzhik','tega']:
 corpora.append((stage,base/stage))
corpora+=[('pasha',W/'reports/phases/P06/pasha-input-diagnostic-01/native'),('cast',W/'reports/phases/P06/native-remaining5-02/cast'),('cast_large_text',W/'reports/phases/P06/native-remaining5-02/cast_large_text'),('npc_baseline',W/'reports/phases/P06/native-remaining5-02/npc_baseline'),('fresh_combat_C5',W/'reports/phases/P06/combat-movie-recovery-01/combat_baseline')]
source=[];results=[]
for name,p in corpora:
 sf=p/'source_hashes.json';files.add(sf);data=json.loads(sf.read_text());intersection=[k for k in critical if k in data and k.startswith('game/')];diff=[{'path':k,'evidence_SHA':data[k],'current_SHA':critical[k]} for k in intersection if data[k]!=critical[k]];source.append({'corpus':name,'source_inventory':str(sf.relative_to(W)),'critical_shared_game_keys_checked':len(intersection),'changed_critical_game_keys':diff,'all_shared_critical_exact':not diff})
 for n in ['validation.json','commands.json','result.json','live/result.json','movie/result.json','full_replay.json','reduced_replay.json','movie_replay.json','linux_export_replay.json','wine_export_replay.json']:
  q=p/n
  if q.exists():files.add(q)
 v=p/'validation.json';d=json.loads(v.read_text());results.append({'corpus':name,'validation':str(v.relative_to(W)),'scope':d.get('scope') if isinstance(d,dict) else 'Completed individual C5 child modes only; outer interrupted130','passed':d.get('passed') if isinstance(d,dict) else all(x.get('passed',False) for x in d),'reported_source_HEAD':d.get('source_head') if isinstance(d,dict) else None})
for jsonfile,key,subkey in [('cast-pixel-comparison.json','captures','path'),('edge-inspection.json','actual_capture_samples','capture'),('baseline-inspection.json','actual_native_samples','path'),('baseline-inspection.json','supplement_samples','path')]:
 d=json.loads((O/jsonfile).read_text())
 for f in d[key]:files.add(W/f[subkey])
for d in json.loads((O/'temporal-inspection.json').read_text())['actual_movies']:files.add(W/d['movie_path'])
B=W/'reports/phases/P06/combat-movie-recovery-01/combat_baseline';files.add(B/'combat_polish.mp4');files.update(B.glob('*.mp4'));files.add(B/'p04_regression/engine_replay.json');files.add(B/'p04_regression/validation.json')
for n in ['intro','washroom','complete']:files.add(B/'p04_regression/engine_replay_frames'/f'{n}.png')
for n in ['native_probe.log','full_replay.log','reduced_replay.log','movie_replay.log','encode_movie.log','linux_export_replay.log','wine_export_replay.log']:files.add(B/'logs'/n)
for n in ['lead-full-review-preparation-01/component-review-crossrefs.json','lead-full-review-preparation-01/acceptance-checklist.json','lead-full-gate-preflight-01/component-reuse-index.json','lead-full-review-carry-forward-02/carry-forward.json']:files.add(R/'reports/phases/P06'/n)
# Original accepted references: all37, preserve original bounded scopes.
for f in json.loads((O/'component-exact-reuse.json').read_text())['review_refs']:files.add((W if f['base']=='WORK' else R)/f['path'])
write('current-corpus-critical-source-binding.json',{'current_reported_HEAD':'fa8693a36eaba56825f02ef74c09bbec38050a35','corpora':source,'all_compared_game_critical_keys_exact':all(x['all_shared_critical_exact'] for x in source),'source_only_preflight_or_old_component_native_not_relabelled_fresh':True})
write('actual-evidence-freeze.json',{'files':[{'base':'WORK' if p.is_relative_to(W) else 'ROOT','path':str(p.relative_to(W) if p.is_relative_to(W) else p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)],'corpora':results,'outer_exit130':{'source':'ROOT canonical receipt5766e682ba6546a0b4eb0dab35cca6be message; not represented as completed outer validator','completed_C5_modes_independently_read':True,'whole_job_PASS':False,'cause':'UNKNOWN','reviewer_signals_or_cleanup':False},'private_raw_or_manifest_bytes_copied':False})
r=json.loads((O/'component-exact-reuse.json').read_text());old=next(x for x in r['rows'] if x['id']=='timka_world');latest=next(x for x in r['rows'] if x['id']=='timka_prime');bad=[x for x in old['own_art_keys'] if not x['exact']];write('component-reuse-resolution.json',{'single_old_metadata_delta':bad,'reason':'Owner-approved Timka schema2/84 metadata supersedes old schema1 world.json. WORLD PNG remains exact. Latest accepted Timka prime/present context component binds current compact WORLD/ACTION/FIN assets and sockets exactly; fresh current corpus independently inspected.','latest_Timka_prime_all_own_art_exact':latest['all_checked_own_art_exact'],'latest_Timka_prime_art_keys':len(latest['own_art_keys']),'all_other_rows_own_art_exact':all(x['all_checked_own_art_exact'] for x in r['rows'] if x['id']!='timka_world'),'not_a_runtime_equivalence_claim_from_old_metadata_alone':True})
write('decode-interruption-observation.json',{'first_attempt_normal_error':'Installed FFmpeg removed old -vsync flag; own script corrected to -fps_mode passthrough. No engine involved.','second_attempt_exit':143,'scope':'Owned Python/FFmpeg review decoding only;6movie boards completed, all7frame sets existed. No kill/stop/cleanup requested by reviewer. CauseUNKNOWN.','bounded_resume':'Verified all184 existing decoded PNGs with Pillow.verify; completed final Pasha board and binding JSON without rerunning captured gameplay.','completed_C5_fresh_movie_decoding_afterwards':'60actual frames, exit0','production_effect':None})
print(json.dumps({'evidence_files':len(files),'critical_source_comparison_all_exact':all(x['all_shared_critical_exact'] for x in source),'changed_corpora':[(x['corpus'],x['changed_critical_game_keys']) for x in source if not x['all_shared_critical_exact']]}))
