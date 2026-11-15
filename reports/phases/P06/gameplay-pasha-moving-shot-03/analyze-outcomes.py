from pathlib import Path
import json
O=Path(__file__).parent;B=json.loads((O/'source-bindings.json').read_text());P=Path(B['canonical_native']);out={}
for run in ['live','movie']:
 d=json.loads((P/run/'result.json').read_text());m={};samples=d['trace'];ammo=d['ammo_trace']
 assert all(c['passed'] for c in d['checks'])
 for s in dict.fromkeys(x['segment'] for x in samples):
  a=[x for x in samples if x['segment']==s];am=[x for x in ammo if x['segment']==s];cs=[c for c in d['contacts'] if c['segment']==s]
  if s.startswith('finisher_'):
   m[s]={'contacts':[(c['category'],c['damage'],c['finisher'],c['player_frame']) for c in cs],'max_score':max(x['score'] for x in a),'max_damage_events':max(x['damage_events'] for x in a),'min_ammo':min(x['ammo'] for x in am)}
   assert m[s]['max_score']==100 and m[s]['max_damage_events']==2
   assert m[s]['min_ammo']==(3 if '_firearm_' in s else 4)
 pairs=[]
 for s,v in m.items():
  if s.startswith('finisher_false_'):
   other=s.replace('finisher_false_','finisher_true_');assert v==m[other];pairs.append([s,other,v])
 assert len(pairs)==20
 positives={}
 for s in ['incoming_before_launch_false','incoming_before_launch_true']:
  cs=[c for c in d['contacts'] if c['segment']==s];am=[x for x in ammo if x['segment']==s]
  assert len(cs)==1 and cs[0]['target_is_player'] and cs[0]['damage']==1
  assert min(x['ammo'] for x in am)==4 and max(x['bullets'] for x in am)==0
  positives[s]={'real_incoming_contact':cs[0],'ammo4_no_bullets':True}
 for s in ['before_contact_cancel','before_contact_revoke','before_contact_reopen','before_contact_replace_policy','before_contact_hurt','before_contact_death']:
  cs=[c for c in d['contacts'] if c['segment']==s];am=[x for x in ammo if x['segment']==s]
  assert not cs and min(x['ammo'] for x in am)==4 and max(x['bullets'] for x in am)==0
  positives[s]={'no_outgoing_contacts':True,'ammo4_no_bullets':True}
 out[run]={'Full_Reduced_20_FIN_pairs_derived_from_raw_contacts_score_ammo':pairs,'incoming_and_prelaunch_cancel_raw':positives,'all_checks_true':len(d['checks'])}
(O/'independent-outcomes.json').write_text(json.dumps(out,indent=2)+'\n');print('Independent20 FIN modepairs and liveincoming/cancel outcomes verified in both runs')
