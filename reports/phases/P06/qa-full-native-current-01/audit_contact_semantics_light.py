"""Recompute saved Core/HUD invariants from completed native replays; no simulation or heavy media work."""
from pathlib import Path
import json,hashlib,collections,math
Q=Path(__file__).resolve().parent;W=Q.parents[3]/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/full-native-current-source-01'
commands=json.loads((P/'commands.json').read_text());rows=[]
for command in commands:
 name=command['name'];r={'name':name,'modes':[]}
 for mode in ['live','movie']:
  p=P/name/mode/'result.json'
  if not p.is_file():continue
  d=json.loads(p.read_text());contacts=d.get('contacts',[]);out=[x for x in contacts if x.get('finisher') and not x.get('target_is_player')];keys=[(x.get('epoch'),x.get('id'),x.get('target')) for x in contacts];dupes=[k for k,n in collections.Counter(keys).items() if n>1];equalities=[]
  for x in d.get('checks',[]):
   detail=x.get('details',{})
   if 'Full' in detail and 'Reduced' in detail:equalities.append({'name':x['name'],'Full':detail['Full'],'Reduced':detail['Reduced'],'equal':detail['Full']==detail['Reduced']})
   elif ('Full_Reduced' in x['name'] or 'Full_Reduced' in x['name'].replace(' ','_')):
    pair=detail.get('results',detail.get('outcomes'))
    if isinstance(pair,list) and len(pair)==2:equalities.append({'name':x['name'],'Full':pair[0],'Reduced':pair[1],'equal':pair[0]==pair[1]})
  checks={'Core_contact_identity_once':not dupes,'outgoing_FIN_pose1':all(x.get('player_frame')==1 for x in out),'actual_FullReduced_numeric_pairs_equal':all(x['equal'] for x in equalities)}
  model_checks=[]
  if name=='counter_feedback':
   obs=d['observations'];model_checks=[{'name':'every_saved_HUD_model_display_equal','passed':all(o['model']==o['displayed'] for o in obs)},{'name':'every_visible_actual_bar_5px_above_arena','passed':all(not o['visible'] or o['bar_rect'][3]==5 and o['bar_rect'][1]+o['bar_rect'][3]<=62 for o in obs)},{'name':'open_window_necessary_real_clock_frame_health_conditions','passed':all(not o['window_open'] or o['action']=='special' and o['frame']==0 and o['health']>0 and .06-1e-8<=o['clock']<=.26+1e-8 for o in obs)},{'name':'HUD_progress_clamped_finite','passed':all(math.isfinite(o['model']['progress']) and 0<=o['model']['progress']<=1 for o in obs)}];checks.update({x['name']:x['passed'] for x in model_checks})
  r['modes'].append({'mode':mode,'source_result_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'Core_contacts':len(contacts),'outgoing_FIN':len(out),'incoming_Core':sum(x.get('target_is_player') is True for x in contacts),'unique_earned_FIN_category_direction':sorted(set((x.get('category'),x.get('direction')) for x in out)),'duplicate_contact_keys':dupes,'FullReduced_numeric_pairs':equalities,'HUD_observations':len(d.get('observations',[])),'checks':checks,'passed':all(checks.values())})
 if r['modes']:rows.append(r)
result={'scope':'RECOMPUTED_SAVED_EVENT_AND_HUD_INVARIANTS_NOT_NEW_ENGINE_EXECUTION','stages':rows,'completed_prefix':len(commands),'passed':all(m['passed'] for s in rows for m in s['modes']),'no_game_execution_or_heavy_analysis':True};out=Q/('semantic-prefix-%02d.json'%len(commands));assert not out.exists();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'stages':len(rows),'passed':result['passed'],'failures':[(s['name'],m['mode'],[k for k,v in m['checks'].items() if not v]) for s in rows for m in s['modes'] if not m['passed']]}))
