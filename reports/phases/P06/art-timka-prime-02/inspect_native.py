from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;E=W/'reports/phases/P06/timka-prime-01/native-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads((E/'validation.json').read_text());r=json.loads((E/'live/result.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']=='db84b39711181bb93b6ce58ac4bb7a244dee032b';assert len(r['checks'])==304 and r['passed'] and len(r['captures'])==90
for a in v['artifacts']:assert sha(W/a['path'])==a['sha256']
old=json.loads((O.parent/'art-timka-prime-01/decision.json').read_text());production=old['production_source_inventory_sha256'];assert all(sha(W/n)==h for n,h in production.items());trace={t['tick']:t for t in r['trace']};routes=[]
for context in ['present','prime']:
 for di in ['down','left','right','up']:
  route=context+'_locomotion_'+di;caps=[c for c in r['captures'] if c['name'].startswith(route)];count=6 if context=='present' else 4;assert len(caps)==count
  names=['stance0','stance1']+['walk_frame'+str(f) for f in range(4 if context=='present' else 2)]
  cs=[next(c for c in caps if c['name']==route+'_'+n) for n in names]
  for c in cs:
   frame=int(c['name'][-1]);anim=('idle_' if '_stance' in c['name'] else 'walk_')+di;assert c['animation']==anim and c['frame']==frame
  ts=[t for t in r['trace'] if t['segment']==route];runs=[];run=[]
  for t in ts:
   if t['animation']=='walk_'+di:run.append(t)
   elif run:runs.append(run);run=[]
  if run:runs.append(run)
  movement=max(runs,key=len);observed=[];wraps=0;before=None
  for t in movement:
   f=t['frame']
   if before is not None and f<before:wraps+=1
   if before!=f:observed.append({'tick':t['tick'],'frame':f,'position':t['position']})
   before=f
  assert wraps>=2 and set(t['frame'] for t in movement)==set(range(4 if context=='present' else 2))
  item={'route':route,'capture_animations_frames':[(c['name'],c['animation'],c['frame']) for c in cs],'longest_real_walk_records':len(movement),'walk_tick_start':movement[0]['tick'],'walk_tick_end':movement[-1]['tick'],'observed_wraps_independent':wraps,'frame_transition_graph':observed};routes.append(item)
  board=Image.new('RGB',(count*288,342),(225,228,220));draw=ImageDraw.Draw(board)
  for i,c in enumerate(cs):
   t=trace.get(c['tick']) or min(r['trace'],key=lambda x:abs(x['tick']-c['tick']));x,y=t['position'];im=Image.open(c['path']).convert('RGB');assert im.size==(640,360);piece=im.crop((round(x)-48,round(y)-76,round(x)+48,round(y)+24)).resize((288,300),Image.Resampling.NEAREST);board.paste(piece,(i*288,40));draw.text((i*288+4,2),c['animation']+' f'+str(c['frame']),fill=(70,30,30));draw.text((i*288+4,18),'tick'+str(c['tick'])+' '+names[i],fill=(70,30,30))
  board.save(O/(route+'_native_complete.png'))
# Finisher native camera crops keep both full participant figures and environment.
finisher=[]
for seg in dict.fromkeys(c['name'].rsplit('_',1)[0] for c in r['captures'] if c['name'].startswith('clinch_') or c['name'].startswith('V_finisher_')):
 cs=[next(c for c in r['captures'] if c['name']==seg+'_'+suffix) for suffix in ['guard','contact','recovery']];assert [c['frame'] for c in cs]==[0,1,2];finisher.append({'segment':seg,'captures':[(c['name'],c['animation'],c['frame'],c['tick']) for c in cs]});board=Image.new('RGB',(3*432,454),(225,228,220));draw=ImageDraw.Draw(board)
 for i,c in enumerate(cs):
  t=trace.get(c['tick']) or min(r['trace'],key=lambda x:abs(x['tick']-c['tick']));x,y=t['position'];im=Image.open(c['path']).convert('RGB');piece=im.crop((round(x)-72,round(y)-88,round(x)+72,round(y)+48)).resize((432,408),Image.Resampling.NEAREST);board.paste(piece,(i*432,44));draw.text((i*432+4,2),c['animation']+' f'+str(c['frame']),fill=(70,30,30));draw.text((i*432+4,18),'tick'+str(c['tick'])+' '+c['name'],fill=(70,30,30))
 board.save(O/(seg+'_native_complete.png'))
metrics={'schema':1,'source_head':v['source_head'],'native_validation_sha256':sha(E/'validation.json'),'all_native_artifacts_verified':len(v['artifacts']),'source_art_controller_exact_previous_candidate':True,'production_source_inventory_sha256':production,'native_passed_checks':304,'captures':90,'locomotion_captures_verified':40,'real_walk_routes':routes,'full_two_cycles_every_route':True,'finisher_clip_sequences':finisher,'contact_records':len(r['contacts']),'movie_acceptance':'PENDING_COMPLETE_MOVIE02','full_phase_approval':False}
(O/'native_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({'native_artifacts_verified':len(v['artifacts']),'real_walk_cycles':[(i['route'],i['observed_wraps_independent']) for i in routes],'finisher_clips':len(finisher),'movie':'PENDING'}))
