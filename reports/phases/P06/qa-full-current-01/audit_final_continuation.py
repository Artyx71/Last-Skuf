"""Read-only final QA aggregation: existing actual evidence, no engine or state mutation."""
from pathlib import Path
import hashlib,json,math,struct,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';Q=Path(__file__).resolve().parent;N=W/'reports/phases/P06/combat-interruption-continuation-01';C=W/'reports/phases/P06/combat-movie-recovery-01/combat_baseline';P=N/'p04_regression';J=R/'.autopilot/jobs/69b305de0c5c4e65a1fa90433c4c7e97'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks=[]
def ck(ok,label,detail=None):checks.append({'name':label,'passed':bool(ok),'detail':detail})
def host(p):return Path(str(p)[2:].replace(chr(92),'/')) if str(p).startswith('Z:') else Path(p)
def png(p):
 with host(p).open('rb') as f:b=f.read(24)
 assert b[:8]==b'\x89PNG\r\n\x1a\n' and b[12:16]==b'IHDR';w,h=struct.unpack('>II',b[16:24]);assert w>0 and h>0
 return [w,h]
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip();ck(head=='fa8693a36eaba56825f02ef74c09bbec38050a35','current reviewed source HEADfa869',head)
before=rd(N/'source_hashes_before.json');after=rd(N/'source_hashes_after.json');current={str(p.relative_to(W)):sha(p) for folder in ['game','tools','assets/source_audio','assets/source_art/characters'] for p in sorted((W/folder).rglob('*')) if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}
ck(before==after==current and len(current)==1456,'actual1456 full source before/after/current exact');wr(Q/'reviewed-source-inventory.json',current)
receipt=rd(J/'receipt.json');inp=rd(J/'input.json');ck(receipt['exit_code']==0 and receipt['operation']=='69b305de0c5c4e65a1fa90433c4c7e97' and receipt['argv_sha256']==inp['argv_sha256'] and receipt['log_sha256']==sha(J/'output.log'),'actual terminal canonical0 receipt/argv/log')
v=rd(N/'validation.json');ck(v['passed'] is True and v['phase_approval'] is False and v['merge_approval'] is False and v['source_head']==head and v['source_unchanged'] is True and all(type(x) is bool and x for x in v['checks'].values()),'actual continuation complete technical scope only')
commands=rd(N/'commands.json');ck(len(commands)==2 and all(type(c['exit_code']) is int and c['exit_code']==0 and c['passed'] is True and c['descendant_cleanup']['remaining_live_children']==[] and c['descendant_cleanup']['unexpected_live_children'] is False for c in commands),'actual two existing commands0 with empty owned-child cleanup')
for command in commands:
 log=N/'logs'/(command['name']+'.log');ck(log.is_file() and sha(log)==command['log_sha256'],'actual command log SHA '+command['name'])
prior=R/'reports/phases/P06/qa-combat-interruption-continuation-01';contract=W/'reports/phases/P06/native-continuation-contract-02/contract.json';refs=rd(contract)['artifacts'];ck(len(refs)==905 and all(sha(W/x['path'])==x['sha256'] for x in refs),'actual905 retained reference pins still exact')
completed=rd(prior/'completed-C5-inventory.json')['records'];ck(len(completed)==1131 and all(sha(W/x['path'])==x['sha256'] for x in completed),'actual1131 completed C5 artifact pins still exact; partialnestedP04 excluded')
oldreceipt=R/'.autopilot/jobs/5766e682ba6546a0b4eb0dab35cca6be/receipt.json';ck(rd(oldreceipt)['exit_code']==130 and sha(oldreceipt)==v['original130_receipt_preserved']['sha256'],'original130 receipt unchanged; cause UNKNOWN')
composed=rd(N/'composed13.json');ck(composed['passed'] is True and len(composed['stages'])==13 and len({x['name'] for x in composed['stages']})==13 and all(x['passed'] is True for x in composed['stages']) and composed['phase_approval'] is False and composed['retained_proof_scope_explicit'] is True and composed['old_failures_and_interruptions_unchanged'] is True,'composed13 technical union positive, not one fresh run nor phasePASS')
p04v=rd(P/'validation.json');ck(len(p04v)==24 and all(isinstance(x['name'],str) and x['name'].strip() and x['passed'] is True and (type(x['exit_code']) is int and x['exit_code']==0 if 'exit_code' in x else isinstance(x.get('checks'),dict) and bool(x['checks']) and all(type(t) is bool and t for t in x['checks'].values())) for x in p04v),'actual exact24 typed P04 rows allPASS')
p04modes={}
for name in ['engine_replay','reduced_visual_replay','movie_replay','linux_export_replay','windows_export_replay']:
 d=rd(P/(name+'.json'));deaths=d['deaths'];ck(d['passed'] is True and d['actual_input'] is True and d['route_warps']==0 and len(d['checks'])==59 and all(type(t) is bool and t for t in d['checks'].values()),'actual P04Input/no warp/59 true '+name)
 ck(len(deaths)==10 and all(x['actual_ai_death'] is True and x['damage_events']==1 and x['latency_ms']<1000 and x['reset_actions']==x['reset_bullets']==x['reset_kills']==0 for x in deaths),'actual10AIdeaths/oncehit/retry<1s/reset zero '+name)
 ck(len(d['captures'])==9 and all(x['error']==0 and png(x['path']) for x in d['captures']),'actual9captured PNG '+name)
 ck(d['final_snapshot']['state']=='complete' and d['final_snapshot']['kills']==0 and d['final_snapshot']['shots_fired']==0 and d['final_snapshot']['score']==1000,'actual weakYakuza/nonlethal completion+once score '+name)
 p04modes[name]={'checks':59,'actual_AI_deaths':10,'max_retry_ms':max(x['latency_ms'] for x in deaths),'PNG':9,'source_report_sha256':sha(P/(name+'.json')),'movie_maker':d['frame_timings']['movie_maker'],'rendered_status':d['capture_status'],'audio_driver':d['audio']['audio_driver']}
ck(p04modes['movie_replay']['movie_maker'] is True and (P/'mission.mp4').is_file(),'actual P04Movie flag and actual MP4')
export_rows=[]
for e in rd(P/'exports.json'):
 p=W/e['path'];first=p.open('rb').read(4);ck(sha(p)==e['sha256'] and p.stat().st_size==e['bytes'] and first.startswith(b'\x7fELF' if e['platform']=='Linux' else b'MZ'),'actual P04 exported artifact SHA/size/magic '+e['platform']);export_rows.append({**e,'actual_magic':first.hex()})
ck(len(export_rows)==2 and {x['platform'] for x in export_rows}=={'Linux','Windows'},'actual Linux and PE/Wine, nativeWindows not claimed')
audio=rd(N/'audio_detailed.json');expected={'full_replay','reduced_replay','movie_replay','linux_export_replay','wine_export_replay'}
ck(audio['status']=='PASS_SIGNAL_AND_RETAINED_RUNTIME' and len(audio['checks'])==29 and all(x['passed'] is True and type(x['passed']) is bool for x in audio['checks']) and set(audio['runtime_expected_names'])==expected and {Path(x).stem for x in audio['runtime']}==expected,'actual numeric29 complete exactfive saved C5 profiles')
numeric={}
for name,row in audio['runtime'].items():
 wav=W/row['path'];trace=wav.with_suffix('.json');ck(sha(wav)==row['sha256'] and sha(trace)==row['trace_sha256'] and row['signal']['clipped_samples']==0 and math.isfinite(row['loudness']['true_peak_dbfs']) and row['loudness']['true_peak_dbfs']<0 and all(type(t) is bool and t for t in row['checks'].values()),'actual five PCM/trace hashes +nonclipping numerical '+name);numeric[name]={'true_peak_dbfs':row['loudness']['true_peak_dbfs'],'rails':row['signal']['clipped_samples'],'duration':row['signal']['duration_seconds'],'rate':row['signal']['sample_rate'],'driver':row['driver']}
# Reuse earlier independent engine and adversarial reviews through explicit immutable proof hashes.
proof_names=['qa-full-native-current-01','qa-guard-feedback-01','qa-timka-present-02','qa-timka-prime-01','qa-timka-prime-footer-01','qa-ryzhik-roll-02','qa-tega-environment-03','qa-pasha-moving-shot-03','qa-baseline-coverage-after-deferral-01','qa-pasha-input-diagnostic-01','qa-cast-stateful-preflight-01','qa-composed-native13-02','qa-combat-interruption-continuation-01','qa-c01-tail02-signal-02']
proofs=[]
for name in proof_names:
 p=R/'reports/phases/P06'/name;d=rd(p/'decision.json');proofs.append({'directory':str(p),'decision_sha256':sha(p/'decision.json'),'artifact_manifest_sha256':sha(p/'artifacts.json'),'FINAL_HASHES_sha256':sha(p/'FINAL_HASHES.json'),'status':d.get('status',d.get('verdict')),'scope':d.get('scope')})
ck(rd(R/'reports/phases/P06/qa-c01-tail02-signal-02/decision.json')['verdict']=='PASS_SIGNAL_ONLY','own actual C01215 numeric closure retained, not listening')
baseline=W/'reports/phases/P06/baseline-after-deferral-01/regression/validation.json';b=rd(baseline);ck(len(b)==49 and all(x['passed'] is True and x['exit_code']==0 for x in b),'actual49local common regression commands positive; reused, not currentGitHubCI')
coverage_names={x['name'] for x in b};ck({'privacy','ai','restart','contact_timing','options','p04g','character_finisher_audio_source','character_finisher_audio','character_combat_profile','character_scene_policy','character_policy_integration','character_frames','character_readiness','character_lab_isolation','character_finisher_audio_contacts'}<=coverage_names,'actual common coverage includes negative/resource/policy/restart/options/contact/C01 runtime')
privacy=R/'reports/phases/P06/final-private11-audit-04/validation.json';pr=rd(privacy);ck(sha(privacy)=='69f2dad9fe7c895a4b24ff4514b29cc01da20cd8af02acfcd1d49df9d1a6ed9a' and pr['passed'] is True and len(pr['checks'])==35 and all(x['passed'] is True for x in pr['checks']) and pr['validated_current_raw_files']==11 and pr['additional_raw_identity_matches']==0,'actual35 bounded private11 identity privacy audit onfa869')
pj=R/'.autopilot/jobs/6da99186ef7b4761897725747642d845';prec=rd(pj/'receipt.json');ck(prec['exit_code']==0 and sha(pj/'output.log')==prec['log_sha256'],'actual privacy canonical0/loghash');privacy_summary={k:pr[k] for k in ['scope','WORK_HEAD','reference_records','validated_current_raw_files','shared_reachable_object_ids','ROOT_index_entries','WORK_index_entries','additional_raw_identity_matches','not_proven']};privacy_summary['report_sha256']=sha(privacy)
art=R/'reports/phases/P06/art-full-current-01/decision.json';gameplay=R/'reports/phases/P06/gameplay-full-current-01/decision.json';ad=rd(art);gd=rd(gameplay);ck(sha(art)=='e084b0e5f5d347d4e6d63ea8a3258d63c2e2b586670a3daefb823727cac30439' and ad['ART_scope_approval'] is True and ad['must_fix']==[],'actual independent fullART scope positive with no mustfix; separate from QA');ck(sha(gameplay)=='e43c34229072421e1e27f23e73b9cb5166260ac648d2ebcbd86684751c7b2121' and gd['gameplay_domain_approval'] is True and gd['must_fix']==[],'actual independent fullGameplay domain positive with no mustfix; separate from QA')
deferral=W/'automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json';ck(sha(deferral)=='58abd098c446842d8f2ae8ccb8859757f218afe64714ec1780197eb432a9923a','exact owner C09 visual-only deferral; retained baseline gates unchanged')
ck(subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()==head,'source HEAD still stable at end of readonlyaudit')
result={'scope':'INDEPENDENT_FULL_P06_QA_DOMAIN_FINAL_ACTUAL_EVIDENCE_AGGREGATION','passed':all(x['passed'] for x in checks),'checks':checks,'source_head':head,'source_keys':len(current),'canonical_completion':receipt,'P04_actual_profiles':p04modes,'P04_actual_exports':export_rows,'C5_five_numeric':numeric,'component_proofs':proofs,'privacy_bounded_summary':privacy_summary,'composed13':composed,'new_engine_invocations':0,'new_numeric_rerenders':0,'phase_approval':False,'merge_approval':False,'listening_performed':False}
wr(Q/'actual-final-audit.json',result);print(json.dumps({'passed':result['passed'],'checks':len(checks),'failed':[x for x in checks if not x['passed']]},ensure_ascii=False))
