from pathlib import Path
import sys,json,copy,hashlib,shutil,subprocess
R=Path(__file__).resolve().parents[1];W=R/'.autopilot/worktrees/P07';sys.path.insert(0,str(W/'tools'))
from p07_pacing import analyze,encode_clip,propose_contract,inventory,digest,write
B=W/'reports/pre_p07/pacing-baseline-01';O=W/'reports/pre_p07/pacing-calibration-02';assert not O.exists();O.mkdir()
raw=json.loads((B/'raw.json').read_text());before=json.loads((B/'source_before.json').read_text());current=inventory()
changed={k for k in set(before)|set(current) if before.get(k)!=current.get(k)}
assert changed=={'tools/p07_pacing.py','tools/tests/test_p07_pacing.py'},changed
metrics=analyze(raw);assert metrics['input_accept_ms']['p95']==18.058 and metrics['input_render_ms']['p95']==19.047 and metrics['death_to_control_ms']['max']==16.671
assert metrics['movement_frame_ms']['samples']==958
write(O/'metrics.json',metrics)
checks=[]
for case in ['cross_context','invented_state','invented_death','invented_contact','later_render','wrong_kind','duplicate_id']:
 data=copy.deepcopy(raw)
 if case=='cross_context':
  a=data['requests'][0];b=data['requests'][6]
  for key in ['accepted_usec','accepted_tick','accepted_state','render_usec','render_draw','render_state']:b[key]=copy.deepcopy(a[key])
 elif case=='invented_state':data['requests'][0]['accepted_state']['position'][0]+=10
 elif case=='invented_death':data['requests'][5]['death_usec']-=100
 elif case=='invented_contact':data['requests'][4]['contact_usec']+=100
 elif case=='later_render':data['requests'][0]['render_draw']+=1
 elif case=='wrong_kind':data['requests'][0]['kind']='melee'
 elif case=='duplicate_id':data['requests'][1]['id']=data['requests'][0]['id']
 try:analyze(data)
 except (ValueError,KeyError) as error:checks.append({'case':case,'rejected':True,'reason':str(error)})
 else:raise AssertionError('Malformed raw accepted '+case)
write(O/'negative-binding-checks.json',{'scope':'PURE_OLD_RAW_VALIDATOR_REPRO_NOT_NEW_MEASUREMENT','checks':checks})
encode_clip(O,raw)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(O/'native-camera.mp4')]))
pts=[float(row['best_effort_timestamp_time']) for row in probe['frames']];clip=raw['clip_frames'];assert len(pts)==len(clip)==106
errors=[abs((b['usec']-clip[0]['usec'])/1000000-(a-pts[0])) for a,b in zip(pts,clip)];assert max(errors)<=.0011,max(errors)
write(O/'clip-timing.json',{'frames':len(pts),'PTS_seconds':pts,'raw_capture_usec':[x['usec'] for x in clip],'maximum_PTS_error_ms':max(errors)*1000,'same_original_PNGs':True,'new_Godot_run':False})
contract=propose_contract(raw,metrics,current,digest(B/'raw.json'),digest(O/'metrics.json'))
contract.update(baseline_source_inventory_sha256=before,guard_only_rebase={'changed_source_paths':sorted(changed),'original_measurement_head':'85ca24b0','current_guard_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip(),'new_measurement':False,'measurement_Game_and_GDScript_unchanged':True},hardware_semantics={'viewport':'Window.size, not render texture extent','native_clip_texture':[640,360]})
write(O/'contract.PROPOSED.json',contract)
write(O/'reanalysis.json',{'schema':1,'status':'OLD_BASELINE_REQUALIFIED_NOT_ACCEPTANCE','old_raw_sha256':digest(B/'raw.json'),'old_baseline_operation':'282fa8f7bd9947a5b5ba4e5fcc151f5c','new_engine_runs':0,'measurement_inputs_unchanged':True,'changed_paths':sorted(changed),'controlled_frame_samples':958,'calibration_idle_samples':239,'contract_sha256':digest(O/'contract.PROPOSED.json'),'source_before_sha256':digest(B/'source_before.json')})
shutil.copy2(__file__,O/'execution.py')
print(json.dumps({'status':'REANALYZED_NO_GODOT_RERUN','contract_sha256':digest(O/'contract.PROPOSED.json'),'PTS_max_error_ms':max(errors)*1000}),flush=True)
