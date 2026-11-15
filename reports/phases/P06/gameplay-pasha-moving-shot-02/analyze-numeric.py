from pathlib import Path
import json,math
O=Path(__file__).parent;P=Path(json.loads((O/'source-bindings.json').read_text())['canonical_native']);metrics={}
for run in ['live','movie']:
 d=json.loads((P/run/'result.json').read_text());out={'checks':len(d['checks']),'contacts':len(d['contacts']),'trace_samples':len(d['trace']),'clothing_anchors':len(d['clothing_overlay']),'moving_routes':{},'resources':{},'finishers':{}}
 tokens=[(c['epoch'],c['id'],c['target']) for c in d['contacts']];assert len(tokens)==len(set(tokens));out['unique_contact_tokens']=len(set(tokens))
 for s in dict.fromkeys(x['segment'] for x in d['trace']):
  a=[x for x in d['trace'] if x['segment']==s];am=[x for x in d['ammo_trace'] if x['segment']==s];cs=[c for c in d['contacts'] if c['segment']==s]
  if s.startswith('moving_shot_'):
   shots=[x for x in a if x['action_kind']=='moving_shot'];poses=[]
   for x in shots:
    if not poses or poses[-1]['pose']!=x['action_frame']:poses.append({'pose':x['action_frame'],'clock':x['action_elapsed'],'tick':x['tick']})
   steps=[math.dist(x['position'],y['position'])/max(1,y['tick']-x['tick']) for x,y in zip(shots,shots[1:])];costs=[c for c in d['costs'] if c['segment']==s];launch=[c for c in d['launches'] if c['segment']==s]
   assert [p['pose'] for p in poses]==list(range(8)) and len(costs)==len(launch)==len(cs)==1 and costs[0]['pose']==launch[0]['source_pose']==3 and costs[0]['tick']==launch[0]['tick']
   assert max(steps)<=3.001 and cs[0]['damage']==1
   out['moving_routes'][s]={'poses':poses,'max_step_per_physics_tick':max(steps),'action_displacement':math.dist(shots[0]['position'],shots[-1]['position']),'first_animation_after_action':next(x['animation'] for x in a if x['tick']>shots[-1]['tick']),'contact_clock':cs[0]['player_action_elapsed'],'contact_pose':cs[0]['player_frame'],'contact_epoch':cs[0]['epoch'],'launch_tick':launch[0]['tick'],'hit_tick':cs[0]['tick'],'one_cost_on_pose3':True}
  elif s in ['actual_RMB_held_trigger','finite_clip_and_refill','shared_clip_shot_then_firearm_finisher']:
   drops=[{'tick':y['tick'],'before':x['ammo'],'after':y['ammo']} for x,y in zip(am,am[1:]) if y['ammo']<x['ammo']]
   out['resources'][s]={'ammo_drops':drops,'minimum':min(x['ammo'] for x in am),'maximum':max(x['ammo'] for x in am),'contacts':cs}
  elif s.startswith('finisher_'):
   fs=[c for c in cs if c['finisher']];assert len(cs)==2 and len(fs)==1 and fs[0]['player_frame']==1 and fs[0]['damage']==1 and max(x['score'] for x in a)==100
   out['finishers'][s]={'contact_count':2,'FIN_count':1,'FIN_pose':1,'max_score':100,'FIN_animation':fs[0]['player_animation'],'max_damage_events':max(x['damage_events'] for x in a)}
 assert len(out['finishers'])==40
 assert len(out['resources']['actual_RMB_held_trigger']['ammo_drops'])==2 and len(out['resources']['finite_clip_and_refill']['ammo_drops'])==4 and len(out['resources']['shared_clip_shot_then_firearm_finisher']['ammo_drops'])==2
 metrics[run]=out
(O/'numeric-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('numeric route/resource/40FIN metrics verified in live and movie')
