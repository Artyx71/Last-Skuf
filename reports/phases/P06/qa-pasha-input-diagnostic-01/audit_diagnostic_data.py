"""Independent saved-data audit. No Godot/runner/Controller/replay execution."""
from pathlib import Path
import json,hashlib,collections,math,struct
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/pasha-input-diagnostic-01';OLD=R/'reports/phases/P06/qa-full-native-current-01';D={'down':[0,1],'left':[-1,0],'right':[1,0],'up':[0,-1]};START={'down':[380,200],'left':[300,240],'right':[300,240],'up':[380,270]}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
oldmovie=read(W/'reports/phases/P06/full-native-current-source-01/pasha/movie/result.json');oldnative=read(W/'reports/phases/P06/full-native-current-source-01/pasha/live/result.json');oldnames={mode:collections.Counter(x['name'] for x in d['checks']) for mode,d in [('headless',oldmovie),('native',oldnative),('movie',oldmovie)]};reports=[];retained=[]
for mode,folder in [('headless',P/'headless/live'),('native',P/'native/live'),('movie',P/'native/movie')]:
 p=folder/'result.json';d=read(p);routes=[]
 for reduced in ['false','true']:
  for direction,vec in D.items():
   seg='moving_shot_'+reduced+'_'+direction;inp=[x for x in d['ammo_trace'] if x['segment']==seg];trace=[x for x in d['trace'] if x['segment']==seg];ticks=[x.get('tick') for x in inp];phases=[]
   for t in trace:
    if t['action_kind']=='moving_shot' and t['action_frame'] not in phases:phases.append(t['action_frame'])
   contacts=[x for x in d['contacts'] if x['segment']==seg];costs=[x for x in d['costs'] if x['segment']==seg];launch=[x for x in d['launches'] if x['segment']==seg];start=START[direction];distance=math.dist(start,trace[-1]['position']) if trace else 0;noTeleport=all(math.dist(a['position'],b['position'])<=180*(b['tick']-a['tick'])/60+.01 for a,b in zip(trace,trace[1:]));checks={
   'nonempty32actualInputobservations':len(inp)==32,
   'segment_and_monotonic_unique_int_ticks':bool(inp) and all(x['segment']==seg and type(x.get('tick')) is int for x in inp) and all(b>a for a,b in zip(ticks,ticks[1:])),
   'actual_direction_vector_every_sample':all(isinstance(x.get('input_vector'),list) and len(x['input_vector'])==2 and all(type(y) in [int,float] and math.isfinite(y) for y in x['input_vector']) and math.dist(x['input_vector'],vec)<1e-8 for x in inp),
   'actual_run_boolean_true_every_sample':all(x.get('run_pressed') is True for x in inp),
   'Input_ticks_exact_correspond_trace':ticks==[x['tick'] for x in trace],
   'Window_flags_typed_and_mode_bound':all(type(x.get('window_focused')) is bool and x.get('window_no_focus') is (mode=='movie') for x in inp),
   'all8orderedphases':phases==list(range(8)),
   'ends_held_run_and_action_finished':bool(trace) and trace[-1]['animation']=='run_'+direction and trace[-1]['action_kind']=='',
   'distance96_and_no_teleport':abs(distance-96)<1e-5 and noTeleport,
   'velocity180everyrecord':all(math.dist(t['velocity'],[180*vec[0],180*vec[1]])<1e-5 for t in trace),
   'once_launch_cost_contact':len(launch)==len(costs)==len(contacts)==1,
   'single_source_pose3_current_authority_and_cost':len(launch)==1 and launch[0]['source_pose']==3 and launch[0]['authority']['actor_id']=='pasha' and launch[0]['authority']['fixture_id']=='pasha_training' and costs[0]['pose']==3 and costs[0]['ammo']==3 and costs[0]['tick']==launch[0]['tick'] and costs[0]['epoch']==launch[0]['epoch'],
   'actual_one_lethal_damage_no_score_ammo3':len(contacts)==1 and contacts[0]['damage']==1 and contacts[0]['lethal'] is True and not contacts[0]['target_is_player'] and trace[-1]['score']==0 and inp[-1]['ammo']==3,
   }
   routes.append({'segment':seg,'checks':checks,'passed':all(checks.values()),'samples':len(inp),'first_tick':ticks[0] if inp else None,'last_tick':ticks[-1] if inp else None,'distance':distance,'end_position':trace[-1]['position'],'last_animation':trace[-1]['animation'],'observed_focus_values':sorted(set(x['window_focused'] for x in inp))})
   retained.append({'mode':mode,'segment':seg,'Input_samples':inp,'actual_physics_trace':trace,'contacts':contacts,'launch':launch,'cost':costs})
 nameCounter=collections.Counter(x['name'] for x in d['checks']);newNames=nameCounter-oldnames[mode];removed=oldnames[mode]-nameCounter;oldchecks=[x for x in d['checks'] if oldnames[mode][x['name']]];contactkeys=[(x.get('epoch'),x.get('id'),x.get('target')) for x in d['contacts']];outfin=[x for x in d['contacts'] if x.get('finisher') and not x.get('target_is_player')];basechecks={'all_original393_or581checks_present_and_pass':not removed and len(oldchecks)==sum(oldnames[mode].values()) and all(x['passed'] is True for x in oldchecks),'exact8new_input_checks':sum(newNames.values())==8 and all(name.endswith(':actual_Input_vector_and_run_remain_held') and n==1 for name,n in newNames.items()),'all_actual401_or589checks_true':len(d['checks'])==(589 if mode=='native' else 401) and all(x['passed'] is True for x in d['checks']),'Core_once_unique_keys':len(contactkeys)==len(set(contactkeys)),'all_outgoing_FIN_player_pose1':all(x.get('player_frame')==1 for x in outfin),'movie_no_focus_requested_only_movie':d.get('movie_window_no_focus_requested') is (mode=='movie')}
 reports.append({'mode':mode,'source_path':str(p.relative_to(W)),'source_sha256':sha(p),'checks':basechecks,'routes':routes,'all_checks_passed':all(basechecks.values()) and all(x['passed'] for x in routes),'source_actual_checks':len(d['checks']),'Core_receipts':len(contactkeys),'outgoing_FIN':len(outfin),'incoming_Core':sum(x.get('target_is_player') is True for x in d['contacts']),'captures':len(d['captures']),'focus_events':d.get('input_focus_events'),'new_check_names':dict(newNames),'old_check_names_sha256':hashlib.sha256(json.dumps(sorted(oldnames[mode].items())).encode()).hexdigest()})
(Q/'held-records-and-route-proofs.json').write_text(json.dumps(retained,indent=2)+'\n');result={'scope':'INDEPENDENT_RAW3MODE_RECOMPUTATION_NO_ENGINE','reports':reports,'held_observations':sum(x['samples'] for m in reports for x in m['routes']),'all_passed':all(x['all_checks_passed'] for x in reports),'past_failure_causality':'NOT_ESTABLISHED','Window_NO_FOCUS_is_request_and_observed_flag_not_guarantee':True,'no_retrospective_OS_or_physical_keyboard_claim':True};out=Q/'diagnostic-data-results.json';assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'modes':len(reports),'actual_held_observations':result['held_observations'],'all_passed':result['all_passed'],'failures':[(m['mode'],[k for k,v in m['checks'].items() if not v],[(x['segment'],[k for k,v in x['checks'].items() if not v]) for x in m['routes'] if not x['passed']]) for m in reports if not m['all_checks_passed']]}))
