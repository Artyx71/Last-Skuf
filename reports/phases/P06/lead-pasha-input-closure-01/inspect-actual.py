"""Read actual saved evidence only. No engine, source/Git/state mutation."""
from pathlib import Path
import json,hashlib,math,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-pasha-input-closure-01';B=W/'reports/phases/P06/pasha-input-diagnostic-01';OLD=W/'reports/phases/P06/full-native-current-source-01/pasha'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,o):(O/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
previous=read(OLD/'movie/result.json');old_names=[x['name'] for x in previous['checks']];rows=[];bindings=[];modes=[]
for name,rel,count in [('headless','headless/live',401),('live','native/live',589),('movie','native/movie',401)]:
 p=B/rel/'result.json';v=read(p);assert v['passed'] is True and len(v['checks'])==count and all(x['passed'] is True for x in v['checks']);names=[x['name'] for x in v['checks']];assert len(set(names))==len(names);assert all(n in names for n in old_names)
 for reduced in [False,True]:
  for direction,vector,initial in [('down',[0,1],[380,200]),('left',[-1,0],[300,240]),('right',[1,0],[300,240]),('up',[0,-1],[380,270])]:
   seg=f'moving_shot_{str(reduced).lower()}_{direction}';t=[x for x in v['trace'] if x['segment']==seg];a=[x for x in v['ammo_trace'] if x['segment']==seg];assert len(a)==len(t)==32;assert [x['tick'] for x in a]==[x['tick'] for x in t];assert [x['tick'] for x in a]==list(range(a[0]['tick'],a[0]['tick']+32));assert all(x['run_pressed'] is True and x['input_vector']==vector for x in a);assert math.dist(initial,t[-1]['position'])==96;assert t[-1]['animation']=='run_'+direction and t[-1]['action_kind']==''
   phases=[]
   for x in t:
    if x['action_kind']=='moving_shot' and x['action_frame'] not in phases:phases.append(x['action_frame'])
   assert phases==list(range(8));contact=[x for x in v['contacts'] if x['segment']==seg];cost=[x for x in v['costs'] if x['segment']==seg];launch=[x for x in v['launches'] if x['segment']==seg];assert len(contact)==len(cost)==len(launch)==1 and cost[0]['pose']==launch[0]['source_pose']==3
   rows.append({'mode':name,'segment':seg,'input_samples':len(a),'unique_monotonic_consecutive_ticks':True,'tick_first':a[0]['tick'],'tick_last':a[-1]['tick'],'raw_input_vector_matches':True,'run_true':True,'last_position':t[-1]['position'],'displacement':96,'last_animation':t[-1]['animation'],'poses':phases,'contacts':1,'costs':1,'launches':1,'focus_values':sorted(set(x['window_focused'] for x in a)),'no_focus_values':sorted(set(x['window_no_focus'] for x in a))})
 assert len(v['contacts'])==105
 modes.append({'mode':name,'actual_checks':count,'legacy393names_present':True,'actual_contact_records':105,'focus_events':v['input_focus_events'],'no_focus_requested':v['movie_window_no_focus_requested']});bindings.append({'base':'WORK','path':str(p.relative_to(W)),'sha256':sha(p),'bytes':p.stat().st_size})
put('own-actual-numeric-proofs.json',{'schema':1,'status':'ACTUAL_DATA_VERIFIED_NOT_FULLPHASE_APPROVAL','modes':modes,'movement_routes':rows,'held_records_total':sum(x['input_samples'] for x in rows),'empty_input_intervals':0,'all_tick_scope_exact':True,'cause_of_old_failure':'UNKNOWN','NO_FOCUS_global_efficacy_proven':False,'old_failed_record_overwritten':False})
a=read(OLD/'source_hashes.json');b=read(B/'native/source_hashes.json');changed=[k for k in a if a[k]!=b.get(k)];assert changed==['game/tests/pasha_moving_shot_replay.gd'] and set(a)==set(b)
put('recorded-source-delta.json',{'schema':1,'old_source_records':len(a),'new_source_records':len(b),'changed':[{'path':p,'before':a[p],'after':b[p]} for p in changed],'source_files_added':[],'scope':'Actual recorded source maps; other1367 exact. Raw renderer frozen651; new guard-only change must be separately reviewed, never called freshGPU.'})
for operation in ['c0d32773dff14eac9a082e5eb50c50ef','2d814544cdc44d8c880d9caa426d74b6']:
 j=R/'.autopilot/jobs'/operation;inp=read(j/'input.json');rec=read(j/'receipt.json');assert rec['operation']==operation and rec['argv_sha256']==inp['argv_sha256'] and rec['exit_code']==0 and rec['log_sha256']==sha(j/'output.log')
 for n in ['input.json','receipt.json','output.log']:bindings.append({'base':'ROOT','path':str((j/n).relative_to(R)),'sha256':sha(j/n),'bytes':(j/n).stat().st_size})
for p in [B/'headless/validation.json',B/'native/validation.json',B/'headless/commands.json',B/'native/commands.json',B/'native/source_hashes.json',OLD/'source_hashes.json',W/'build/P06/pasha-input-diagnostic-01/pasha-moving-shot.mp4']:
 bindings.append({'base':'WORK','path':str(p.relative_to(W)),'sha256':sha(p),'bytes':p.stat().st_size})
put('actual-reference-bindings.json',{'schema':1,'files':bindings});print(json.dumps({'passed':True,'routes':len(rows),'held_records':768,'raw_contact_records_permode':105,'source_delta':changed,'references':len(bindings)}))
