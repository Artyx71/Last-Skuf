from pathlib import Path
import json,hashlib,subprocess,shutil,wave
from array import array
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-character-finisher-audio-01';Q=R/'reports/phases/P06/audio-c01-runtime-review-01/closure-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert sha(Q/'decision.json')=='eed5a827352d31cb7a830d2c3cc056e785ca75895c1170899bc30b511c505ba8'
qd=read(Q/'decision.json');assert qd['status']=='PASS_COMPONENT' and qd['mandatory_open_findings']==[] and qd['source_runtime_and_actual_DEV08']=='0dd1cc4dad9379c457e277969b721fcc23a14fe3'
refs=read(O/'external-reference-bindings.json');unique={e['root_relative_path']:e for e in refs['references']}
def ref(p):unique[str(p.relative_to(R))]={'root_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}
for e in read(Q/'artifacts.json')['files']:
 p=Q/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'],str(p);ref(p)
for n in ['decision.json','artifacts.json','FINAL_HASHES.json']:ref(Q/n)
for n,h in read(Q/'FINAL_HASHES.json').items():
 # Finalhash format keys are actual relative file paths.
 if isinstance(h,str) and len(h)==64:assert sha(Q/n)==h,n
out=O/'independent-QA02';out.mkdir(exist_ok=True)
for n in ['decision.json','review.md','artifacts.json','FINAL_HASHES.json']:shutil.copyfile(Q/n,out/n)
job=R/'.autopilot/jobs/44134ae147ee4e39b41aae0b80d3685d';rec=read(job/'receipt.json');inp=read(job/'input.json');assert rec['exit_code']==0 and rec['argv_sha256']==inp['argv_sha256'] and rec['log_sha256']==sha(job/'output.log')
for n in ['input.json','receipt.json','output.log']:
 ref(job/n);dest=O/'producer-receipts'/'44134ae147ee4e39b41aae0b80d3685d';dest.mkdir(exist_ok=True);shutil.copyfile(job/n,dest/n)
for e in read(O/'DEV08-reference-bindings.json'):unique[e['root_relative_path']]=e
for e in read(O/'signal-input-references.json')['records']:ref(Path(e['path']))
f=read(O/'source-freeze.json');assert len(f['source_hashes'])==1465
for k,v in f['source_hashes'].items():assert sha(W/k)==v,k
assert subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip()==f['frozen_commit']
# Independently recheck exact actual old/new stereo sample windows, not only mono correlation.
data={}
for ver in ['native-01','native-02']:
 p=W/'reports/phases/P06/character-finisher-audio-01'/ver/'replay/solo_cues.wav'
 with wave.open(str(p)) as w: assert w.getnchannels()==2 and w.getsampwidth()==2;data[ver]=array('h',w.readframes(w.getnframes()))
rows=[];corr=read(O/'solo-source-correlation-proofs.json')['events'];entries=read(W/'game/assets/audio/character_finishers.json')['sfx']
for cue,e in entries.items():
 with wave.open(str(W/'game'/e['path'].removeprefix('res://'))) as w:n=w.getnframes()
 windows=[]
 for ver in data:
  event=next(x for x in corr if x['native']==ver and x['cue']==cue);i=round(event['capture_start_seconds']*44100);windows.append(data[ver][2*i:2*(i+n)])
 assert windows[0]==windows[1] and len(windows[0])==2*n,cue;rows.append({'cue':cue,'stereo_PCM16_samples_per_segment':2*n,'aligned_actual_samples_equal':True})
put('direct-stereo-pair-proofs.json',{'scope':'EXACT_PLAYED_SOURCE_DURATION_SEGMENTS_NOT_WHOLE_WAV_AND_NOT_LISTENING','pairs':rows})
for e in unique.values():
 p=R/e['root_relative_path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'],str(p)
refs['references']=sorted(unique.values(),key=lambda e:e['root_relative_path']);put('external-reference-bindings.json',refs)
put('final-rehash.json',{'source_HEAD':f['frozen_commit'],'source_keys_exact':1465,'QA02_portable_files_rehashed':110,'external_immutable_references_rehashed':len(unique),'historical_preflight_and_QA01_FAIL_unchanged':True,'actual_final_QA02_receipt':rec,'engine_runs_by_Lead':0,'WORK_or_controller_writes':0})
s=(O/'review-DRAFT.md').read_text();s=s.replace('# C01 finisher audio — independent Lead review (DRAFT; waiting immutable QA02)','# C01 finisher audio — independent Lead component review');s=s.replace("Proposed disposition: PASS_COMPONENT for the P06 prototype's individual finisher cues and captured runtime paths, frozen `0dd1cc4dad9379c457e277969b721fcc23a14fe3`. The final decision must bind QA closure02 after its independent verdict is immutable. This draft grants no approval.","**PASS_COMPONENT** for the P06 prototype's individual finisher cues and captured runtime paths, frozen `0dd1cc4dad9379c457e277969b721fcc23a14fe3`. Independent QA02 is immutable PASS_COMPONENT `eed5a827…`; I read its decision/review/raw results and independently verified all110 portable files and the actual canonical44134ae receipt/log/argv. It records199 PCM checks,49 export checks and20 direct stereo sample comparisons. My own independent analysis below corroborates it. This grants bounded prototype C01/DEV08 component acceptance only, with the owner's historical artistic scope preserved.")
s=s.replace('Final prototype component acceptance remains conditional on reading immutable independent QA02.','Independent QA02 closes C01-Q03 without changing its original gate; my own distinct PCM analyses and direct20 stereo sample-window equality also pass. No mandatory C01 finding remains within this scope.')
(O/'review.md').write_text(s);(O/'review-DRAFT.md').unlink()
put('findings-closure.json',{'schema':1,'new_must_fix_findings':[],'closed':[{'id':'C01-P01','status':'CLOSED','proof':'Actual registry23 and valid/collision startup11 assertions; both collisions reject with ready_assets=false/audio_children0. Actualdirector rejects beforemerge.'},{'id':'C01-P02','status':'CLOSED','proof':'Pinned source verifier80 control,33independent tempcases correct, actual importedstreambinding and20own memoryrerender hashes/NCC identity; direct20old/newstereo windows exact.'},{'id':'C01-Q03','status':'CLOSED_IN_CAPTURED_PROTOCOL','proof':'Oldstress+0.1dBTP/4xswr+.0900 preserved. Newnative02 realstress−1.7dBTP/4xswr−1.7073,0rails. Same gate<0 plusQAtarget≤−1 passes; no source/speed truncation.','scope_limit':'Eight actual12voice bursts, not exhaustive allfuture simultaneouscontentmixes.'}], 'owner_artistic_acceptance':'Historicalf615solo/runtime prototype only','new_stress_or_new_capture_subjective_listening':'NOT_CLAIMED','C09_and_full_phase_gates_unchanged':True})
put('metrics.json',{'schema':1,'recorded_current_source_keys':1465,'actual_raw_WAV_decoded_by_Lead':25,'new_WAV_memory_rerender_byteexact':20,'legacy_WAV_byteexact_to_prior_source':5,'own_source_binding_control_checks':80,'historical_source_negative_cases_read':33,'historical_QA_startup_import_commands_read':7,'historical_QA_registry_startup_assertions_read':34,'historical_native01':{'checks':518,'actual_Input_FIN_routes':45,'not_claimed_fresh_at_newHEAD':True},'actual_native02':{'checks':61,'actual_Input_FIN_routes':3,'solo':20,'overload_bursts':8,'voices_perburst':12,'drops_perburst':8},'Lead_actual_PCM_files_analysed':6,'Lead_solo_source_correlations':40,'minimum_source_NCC':min(x['NCC_fullrate'] for x in corr),'Lead_aligned_old_new_stereo_segments_exact':20,'current_stress_R128_truepeak_dBFS':-1.7,'current_stress_independent4x_float_peak_dBFS':next(x['independent_4x_swr_float_peak_dBFS'] for x in read(O/'mixer-signal-proofs.json')['captures'] if x['native']=='native-02' and x['capture']=='stress_mix'),'QA02_actual_independent_offline_checks':{'PCM':199,'DEV08':49,'extra_integer_stereo_equality':20},'DEV08':{'Linux_renderer':81,'PNG':9,'WindowsPE_Wine_headless':72,'native_Windows':'NOT_TESTED','standalone_files_exact':7},'Lead_contact_PNG_personally_viewed':3,'Lead_engines_run':0,'agent_listening':False})
flags={k:False for k in ['phase_approval','full_P06_approval','P07_approval','readiness_approval','merge_approval','release_approval','publication_approval','ROOT_installation_approval','new_C09_ART_or_runtime_approval','agent_artistic_approval','agent_listening_performed','new_capture_subjective_listening_claim','native_Windows_approval','FPS_approval','hardware_latency_approval','all_future_mix_combinations_approval']}
# Inventory only reviewer-owned compact data; canonical large WAV/binaries stay external.
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['artifacts.json','decision.json','FINAL_HASHES.json']:
  assert not p.is_symlink();files.append({'path':str(p.relative_to(O)),'bytes':p.stat().st_size,'sha256':sha(p)})
put('artifacts.json',{'schema':1,'base':'manifest directory','files':files,'external_reference_manifest':'external-reference-bindings.json','external_reference_sha256':sha(O/'external-reference-bindings.json'),'WAV_or_binaries_or_engine_project_copied':False,'raw_photo_copied':False})
put('decision.json',{'schema':1,'role':'INDEPENDENT_LEAD','status':'PASS_COMPONENT','scope':'C01 individual finisher audio bounded P06 prototype integration/headroom/actual captured routes and local DEV08 packaged smoke','frozen_commit':f['frozen_commit'],'C01_bounded_prototype_component_approval':True,'runtime_technical_approval':True,'DEV08_local_packaged_smoke_approval':True,'owner_original_content_artistic_acceptance':{'record_sha256':'3b6b3c69004668ea73a5cc1102263e80abf2d2757952876dfbd234a4526752d9','scope':'Original f615 solo/runtime for P06 prototype only','new_stress_listening':False},'QA02_decision_sha256':sha(Q/'decision.json'),'signal_source_review_sha256':'c69fe500f8374fa25430e743fb39f6f8a9c251a9a8ee5d0ac7a5cde6c572c84c','prior_QA01_FAIL_preserved_sha256':'658f4ef87158b1689f18ea0f51a4d5d1360b6a1ca30ffe93478e250491eec2a6',**flags,'unbounded_final_audio_acceptance':False,'new_must_fix_findings':[],'phase_attempt_consumed':False,'P06_state':'IMPLEMENTING','P06_attempt':1,'last_full_PASS':'P05 / PR10','next_authorized_work':'Continue remaining mandatory C09 and other P06 work; full verifier/ROOT handoff/full independent phase Lead/required CI and readiness/MDS remain mandatory.','proofs':{n:sha(O/n) for n in ['review.md','metrics.json','findings-closure.json','artifacts.json','source-freeze.json','external-reference-bindings.json','final-rehash.json']},'reviewer_engine_runs':0,'WORK_or_controller_mutations':0})
put('FINAL_HASHES.json',{n:sha(O/n) for n in ['decision.json','review.md','artifacts.json','metrics.json','findings-closure.json','external-reference-bindings.json']})
for e in files:assert sha(O/e['path'])==e['sha256'],e['path']
print(json.dumps({'status':'PASS_COMPONENT','portable_files':len(files),'bytes':sum(e['bytes'] for e in files),'external_refs':len(unique),'hashes':read(O/'FINAL_HASHES.json')},indent=2))
