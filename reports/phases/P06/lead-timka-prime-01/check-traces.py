from pathlib import Path
import json,math
O=Path(__file__).resolve().parent;ROOT=O.parents[3];W=ROOT/'.autopilot/worktrees/P06';base=W/'reports/phases/P06/timka-prime-01';summary={};allcontacts=0
for label,path in [('native03',base/'native-03/live/result.json'),('movie03',base/'movie-03/movie/result.json'),('QA_prime',ROOT/'reports/phases/P06/qa-timka-prime-01/prime/result.json'),('QA_observed',ROOT/'reports/phases/P06/qa-timka-prime-01/prime-observer/result.json')]:
 d=json.loads(path.read_text());assert d['passed'] and all(c['passed'] for c in d['checks']);trace=d['trace'];contacts=d['contacts'];assert len(contacts)==49;allcontacts+=len(contacts);routes=[]
 for ctx,speed,count in [('present',84,4),('prime',118,2)]:
  for direction in ['down','left','right','up']:
   rows=[x for x in trace if x['segment']==f'{ctx}_locomotion_{direction}'];idle=[x for x in rows if x['animation']==f'idle_{direction}'];assert {x['frame'] for x in idle}=={0,1}
   walk=[x for x in rows if x['animation']==f'walk_{direction}'];groups=[]
   for x in walk:
    if not groups or x['tick']!=groups[-1][-1]['tick']+1:groups.append([])
    groups[-1].append(x)
   longest=max(groups,key=len);assert {x['frame'] for x in longest}==set(range(count));wraps=sum(a['frame']>b['frame'] for a,b in zip(longest,longest[1:]));assert wraps>=2,(label,ctx,direction,wraps)
   errors=[abs(math.dist(a['position'],b['position'])-speed/60) for a,b in zip(longest,longest[1:])];assert max(errors)<.002
   routes.append({'context':ctx,'direction':direction,'walk_frames':sorted({x['frame'] for x in longest}),'wraps':wraps,'max_tick_motion_error_px':max(errors)})
 jobs=[]
 for prefix in ['clinch_','V_finisher_unarmed_','V_finisher_blunt_','V_finisher_environmental_']:
  for direction in ['down','left','right','up']:
   seg=prefix+direction;c=[x for x in contacts if x['segment']==seg and not x['target_is_player']];assert len(c)==2 and c[0]['damage']==0 and not c[0]['finisher'] and c[1]['damage']==1 and c[1]['finisher'] and c[1]['lethal'];assert all(x['player_action_frame']==1 for x in c);assert c[0]['player_animation']==f'prime_strike_{direction}';assert c[1]['player_animation']==(('special_' if prefix=='clinch_' else prefix.replace('V_finisher_','finish_'))+direction)
   if prefix=='clinch_':assert c[1]['category']=='unarmed'
   jobs.append({'segment':seg,'heavy_tick':c[0]['tick'],'finisher_tick':c[1]['tick'],'finisher_animation':c[1]['player_animation'],'damage':[0,1]})
 out=[x for x in contacts if not x['target_is_player']];inc=[x for x in contacts if x['target_is_player']];assert len(out)==47 and all(x['player_action_frame']==1 for x in out) and len(inc)==2
 if label=='QA_observed':
  for e in out:
   assert e['qa_receipt_reserved'] and e['qa_prepared_matches']
   if e['finisher']:assert e['qa_job_committed'] and e['qa_target_health']==0 and e['qa_actual_kills']==1 and e['qa_actual_score']==100 and e['qa_target_frame']==1 and e['qa_target_state']=='dead'
  for e in [x for x in out if x['segment'].startswith('clinch_') and x['finisher']]:assert e['qa_pose_original_column']==7 and e['qa_prepared_fixture']=='timka_prime' and e['qa_job_category']=='unarmed'
 summary[label]={'checks':len(d['checks']),'trace_samples':len(trace),'routes':routes,'sixteen_F_V_jobs':jobs,'outgoing_contacts':len(out),'incoming_contacts':len(inc),'incoming_segments':[x['segment'] for x in inc]}
(O/'independent-trace-analysis.json').write_text(json.dumps({'schema':1,'scope':'OWN_NUMERIC_RECOMPUTATION_OF_ACTUAL_SAVED_RUNS_NOT_ENGINE_RERUN','runs':summary,'contacts_recomputed':allcontacts,'trace_samples_recomputed':sum(x['trace_samples'] for x in summary.values()),'eight_route_cycles_correct_each_run':True,'once_and_authority_QA_raw_events_checked':True},indent=2)+'\n');print(json.dumps({'runs':len(summary),'samples':sum(x['trace_samples'] for x in summary.values()),'contacts':allcontacts,'routes_verified':32,'F_V_pairs_verified':64}))
