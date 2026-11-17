from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();s=json.loads((OUT/'source-snapshot.json').read_text())
extra=['game/scripts/core/input_bindings.gd','game/scripts/actors/yakuza_actor.gd','game/resources/chapters/missed_fight.json','game/tests/character_combat_profile_test.gd']
for name in extra:
 d=OUT/'source-snapshot'/name;assert not d.exists();d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes((WORK/name).read_bytes());s['source_sha256'][name]=sha(d)
(OUT/'source-snapshot.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n')
metrics={'schema':1,'scope':'READONLY_PREIMPLEMENTATION_GAMEPLAY_GAP_AUDIT','new_engine_runs':0,'phase_approval':False,'ART_approval':False,'evidence_sha256':{},'historical_native':{}};evidence=metrics['evidence_sha256']
for name in ['gabar-combat-native-02','olezhka-combat-native-01']:
 b=WORK/'reports/phases/P06/attempt1'/name;v=json.loads((b/'validation.json').read_text());h=json.loads((b/'source_hashes.json').read_text());d=json.loads((b/'live/result.json').read_text());movie=json.loads((b/'movie/result.json').read_text());bad=[]
 for a in v['artifacts']:
  path=WORK/a['path'];assert path.is_file() and sha(path)==a['sha256'];evidence[a['path']]=a['sha256']
 for filename in ['validation.json','source_hashes.json']:
  path=b/filename;evidence[str(path.relative_to(WORK))]=sha(path)
 checks={c['name']:c for c in d['checks']};assert all(c['passed'] for c in checks.values());contacts=d['contacts'];examples=[]
 for defense in d.get('defenses',[]):
  matches=[x for x in contacts if x['segment']==defense['segment'] and not x.get('target_is_player') and x['tick']>defense['tick'] and x['id']!=defense['id']]
  examples.append({'segment':defense['segment'],'incoming_id':defense['id'],'defense_tick':defense['tick'],'defense_damage':defense['damage'],'counter':{k:matches[0][k] for k in ['id','tick','damage','player_action_frame','player_action_elapsed']} if matches else None})
 relevant=['game/scripts/actors/character_player.gd','game/scripts/systems/combat_system.gd','game/tests/'+('gabar_combat_replay.gd' if name.startswith('gabar') else 'olezhka_combat_replay.gd')]
 metrics['historical_native'][name]={'frozen_historical_source_head':v['source_head'],'scope':v['scope'],'live_checks':len(d['checks']),'live_failed':sum(not x['passed'] for x in d['checks']),'movie_checks':len(movie['checks']),'movie_failed':sum(not x['passed'] for x in movie['checks']),'PNG_captures':v['actual_captures'],'contacts':len(contacts),'defenses':len(d.get('defenses',[])),'artifact_hashes_verified':len(v['artifacts']),'evidence_not_rerun':True,'not_tested':d.get('not_tested',[]),'parry_to_counter_examples':examples,'historical_to_audit_source_comparison':{p:{'recorded_sha256':h.get(p),'audit_snapshot_sha256':s['source_sha256'].get(p),'same_bytes':h.get(p)==s['source_sha256'].get(p)} for p in relevant},'selected_check_details':{n:c for n,c in checks.items() if any(key in n for key in ['window_edge_','only_one_simultaneous','no_invulnerability_','parry_has_no_','special_sweeps','special_finite','Full_Reduced','death_cancels','counter_contacts_through','same_tick_reentry','damage_uses_authored'])}}
# Actual already recorded full PNGs, cropped as engineering diagnostics only.
D=OUT/'diagnostics';D.mkdir()
sequences=[('olezhka-defense-counter','olezhka-combat-native-01',['counter_right_guard','counter_right_parry','counter_right_contact','counter_right_recovery']),('gabar-lunge','gabar-combat-native-02',['special_right_windup','special_right_contact','special_right_recovery'])]
for title,run,names in sequences:
 data=json.loads((WORK/'reports/phases/P06/attempt1'/run/'live/result.json').read_text());byname={x['name']:x for x in data['captures']};board=Image.new('RGB',(len(names)*480,420),'#202027');draw=ImageDraw.Draw(board)
 for i,name in enumerate(names):
  p=WORK/'reports/phases/P06/attempt1'/run/'live'/(name+'.png');im=Image.open(p).convert('RGB');assert im.size==(640,360);crop=im.crop((180,150,420,300)).resize((480,300),Image.Resampling.NEAREST);board.paste(crop,(i*480,40));draw.text((i*480+6,5),name,fill='white');draw.text((i*480+6,20),'native tick '+str(byname[name]['tick']),fill='#8fd4be');board.paste(im.crop((0,315,640,360)).resize((480,34),Image.Resampling.NEAREST),(i*480,360))
 board.save(D/(title+'.png'))
# Native CH01 route exists; it does not press finisher, so it cannot prove denial.
p=WORK/'reports/phases/P04/attempt1/native-host-03/engine_replay.json';d=json.loads(p.read_text());evidence[str(p.relative_to(WORK))]=sha(p);snapshot=d['final_snapshot'];metrics['historical_CH01']={'scope':d['scope'],'actual_input':d['actual_input'],'route_warps':d['route_warps'],'passed':d['passed'],'kills':snapshot['kills'],'score':snapshot['score'],'checks':{k:v for k,v in d['checks'].items() if any(x in k for x in ['escape','training','distraction','nonlethal','retry'])},'does_not_exercise_finisher_denial':True}
p=WORK/'reports/phases/P04G/attempt1/technical-final-04/full_replay.json';d=json.loads(p.read_text());evidence[str(p.relative_to(WORK))]=sha(p);metrics['historical_P04G']={'scope':d['scope'],'passed':d['passed'],'checks':len(d['checks']),'failed':sum(not x['passed'] for x in d['checks']),'rendered_evidence_claim':False}
# Runtime availability inventory; existence and schemas are not ART acceptance.
metrics['runtime_asset_inventory']={}
for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha']:
 files={}
 for kind in ['world','action','finisher']:
  for suffix in ['.json','.sockets.json','_sheet.png']:
   p=WORK/'game/assets/art/characters'/actor/(kind+suffix)
   if p.is_file(): files[str(p.relative_to(WORK))]=sha(p);evidence[str(p.relative_to(WORK))]=sha(p)
 metrics['runtime_asset_inventory'][actor]=files
for p in [WORK/'game/assets/art/combat_polish/yakuza_finishers.png',WORK/'reports/phases/P06/art-preflight/timka_finisher_up5_preflight_v3a.json']:
 evidence[str(p.relative_to(WORK))]=sha(p)
metrics['source_drift_after_snapshot']={p:sha(WORK/p) for p,h in s['source_sha256'].items() if sha(WORK/p)!=h};metrics['observed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(OUT/'evidence-analysis.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'native':{n:{k:v[k] for k in ['live_checks','movie_checks','artifact_hashes_verified','contacts','defenses']} for n,v in metrics['historical_native'].items()},'CH01':metrics['historical_CH01'],'source_snapshot_count':len(s['source_sha256']),'source_drift':metrics['source_drift_after_snapshot'],'evidence_count':len(evidence)},ensure_ascii=False,indent=2))
