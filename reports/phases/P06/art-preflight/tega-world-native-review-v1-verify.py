from pathlib import Path
import json,hashlib,math,collections
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';BASE=WORK/'reports/phases/P06/attempt1/tega-world-native-01';OUT=ROOT/'reports/phases/P06/art-preflight';PFX='tega-world-native-review-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((OUT/(PFX+'-metrics.json')).read_text());meta=json.loads((WORK/'game/assets/art/characters/tega/world.json').read_text());source_review=WORK/meta['source_adoption']['independent_source_review'];assert sha(source_review)==meta['source_adoption']['review_sha256'];review=json.loads(source_review.read_text());assert review['status']=='ACCEPTABLE_FOUR_DIRECTION_SOURCE_CANDIDATE';assert review['native_sha256']==m['native_sha256'];assert sha(WORK/meta['master'])==meta['master_sha256']==review['master_sha256'];assert sha(WORK/meta['source_adoption']['manifest'])==meta['source_adoption']['manifest_sha256'];receipt_path=ROOT/'.autopilot/jobs/19acf1ed4aea41a7b9bc00cb0c732705/receipt.json';receipt=json.loads(receipt_path.read_text());assert receipt['operation']=='19acf1ed4aea41a7b9bc00cb0c732705' and receipt['exit_code']==0;assert sha(receipt_path.with_name('output.log'))==receipt['log_sha256'];m['durable_receipt_verified']=receipt;m['receipt_sha256']=sha(receipt_path);m['adoption_verified']={'source_review_sha256':sha(source_review),'source_manifest_sha256':sha(WORK/meta['source_adoption']['manifest']),'master_sha256':meta['master_sha256'],'runtime_metadata_sha256':sha(WORK/'game/assets/art/characters/tega/world.json')};dirs=['down','left','right','up'];states={'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]};m['foot_source_bounds']={di:[f['bounds'] for f in meta['frames'][row*8:row*8+8]] for row,di in enumerate(dirs)};m['additional_trace_metrics']={}
for mode in ['live','movie']:
 d=json.loads((BASE/mode/'result.json').read_text());trace=d['trace'];groups=[]
 for sample in trace:
  key=(sample['sequence'],sample['animation'])
  if not groups or groups[-1]['key']!=key:groups.append({'key':key,'entries':[]})
  groups[-1]['entries'].append(sample)
 holds=collections.defaultdict(list);residuals=[]
 for group in groups:
  runs=[]
  for item in group['entries']:
   if not runs or runs[-1]['frame']!=item['frame']:runs.append({'frame':item['frame'],'ticks':[]})
   runs[-1]['ticks'].append(item['physics_tick'])
  state=group['key'][1].rsplit('_',1)[0]
  for run in runs[1:-1]:holds[state].append(run['ticks'][-1]-run['ticks'][0]+1)
  for a,b in zip(group['entries'],group['entries'][1:]):
   dt=(b['physics_tick']-a['physics_tick'])/60.0;residuals.append(math.dist([a['position'][j]+b['velocity'][j]*dt for j in range(2)],b['position']))
 gate=json.loads((BASE/mode/'input_gate.json').read_text());assert gate['passed'] and gate['matched_samples']==gate['expected_samples']==672 and not gate['violations'];assert all(item['window_focused'] is True for item in trace)
 m['additional_trace_metrics'][mode]={'full_interior_phase_holds_ticks':{k:sorted(set(v)) for k,v in holds.items()},'maximum_same_segment_velocity_integration_error':max(residuals),'maximum_visual_rounding_distance':max(math.dist([s['position'][0],s['position'][1]-26],s['visual_origin']) for s in trace),'maximum_vertical_rounding':max(abs(s['visual_origin'][1]-(s['position'][1]-26)) for s in trace),'all_672_window_focused_true':True,'manual_keyboard_or_focus_flag_efficacy_approval':False,'strict_input_gate_sha256':sha(BASE/mode/'input_gate.json'),'strict_input_gate':gate}
m['video_sha256']={p.name:sha(p) for p in [WORK/'build/P06/attempt1/tega-world-native-01/world.avi',WORK/'build/P06/attempt1/tega-world-native-01/world.mp4']};(OUT/(PFX+'-metrics.json')).write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m['additional_trace_metrics'],indent=2));print('footbounds',m['foot_source_bounds'])
