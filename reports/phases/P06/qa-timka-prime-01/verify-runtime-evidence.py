from pathlib import Path
import json,hashlib,math,shutil
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/timka-prime-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,j):(Q/n).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
sets=[('independent-original',Q/'prime/result.json'),('independent-observer',Q/'prime-observer/result.json'),('author-native03',B/'native-03/live/result.json'),('author-movie03',B/'movie-03/movie/result.json')];analyses=[]
for label,p in sets:
 j=json.loads(p.read_text());assert j['passed'] and all(c['passed'] for c in j['checks']);routes=[]
 for context,speed,nframes,count in [('present',84,4,70),('prime',118,2,50)]:
  for direction,vec in {'down':(0,1),'left':(-1,0),'right':(1,0),'up':(0,-1)}.items():
   name=context+'_locomotion_'+direction;seq=[t for t in j['trace'] if t['segment']==name];runs=[];run=[]
   for t in seq:
    if t['animation']=='walk_'+direction and t['action_kind']=='':run.append(t)
    else:
     if run:runs.append(run)
     run=[]
   if run:runs.append(run)
   best=max(runs,key=len);assert len(best)>=count,(label,name,len(best))
   observed=[];wraps=0;previous=None
   for t in best:
    assert math.dist(t['velocity'],[vec[0]*speed,vec[1]*speed])<.02,(label,name,t)
    if t['frame'] not in observed:observed.append(t['frame'])
    if previous:
     if t['frame']<previous['frame']:wraps+=1
     ticks=t['tick']-previous['tick'];assert ticks>0
     actual=[t['position'][a]-previous['position'][a] for a in range(2)];assert math.dist(actual,[vec[a]*speed*ticks/60 for a in range(2)])<.03,(label,name,actual,ticks)
    previous=t
   assert observed==list(range(nframes)) and wraps>=2,(label,name,observed,wraps)
   routes.append({'route':name,'samples':len(best),'speed':speed,'all_frames':observed,'wraps':wraps})
 cs=j['contacts'];assert len(cs)==49 and len({(c['epoch'],c['id'],c['target']) for c in cs})==49
 fins=[c for c in cs if c['finisher']];assert len(fins)==18
 for direction in ['down','left','right','up']:
  events=[c for c in fins if c['segment']=='clinch_'+direction];assert len(events)==1;c=events[0]
  assert c['player_animation']=='special_'+direction and c['player_frame']==1 and .48<=c['player_action_elapsed']<.60
 for category in ['unarmed','blunt','environmental']:
  for direction in ['down','left','right','up']:
   events=[c for c in fins if c['segment']=='V_finisher_'+category+'_'+direction];assert len(events)==1 and events[0]['player_animation']=='finish_'+category+'_'+direction and events[0]['player_frame']==1
 incoming=[c for c in cs if c['target_is_player']];assert len(incoming)==2 and {c['segment'] for c in incoming}=={'interrupt_clinch_hurt','interrupt_clinch_death'}
 if label=='independent-observer':
  assert all(c['qa_receipt_reserved'] and c['qa_prepared_matches'] for c in cs)
  heavy=[c for c in cs if not c['finisher'] and not c['target_is_player']];assert len(heavy)==29
  for c in heavy:
   assert c['damage']==0 and c['strong'] and c['qa_target_health']==1 and c['qa_target_hits']==1 and abs(c['qa_target_stun']-1.25)<1e-6 and abs(math.hypot(*c['qa_target_impulse'])-85)<1e-3 and c['player_frame']==1
  for c in fins:
   d=c['qa_definition'];assert c['qa_job_committed'] and c['qa_pose_kind']=='finisher' and c['qa_target_frame']==1 and c['qa_target_state']=='dead' and c['qa_target_health']==0 and c['qa_target_hits']==2 and c['qa_actual_score']==100 and c['qa_actual_kills']==1
   assert [d[k] for k in ['windup','active','recovery']]==[.48,.12,.38] and d['scene_context']=='athletic_prime' and d['character_id']=='timka'
   if c['segment'].startswith('clinch_'):assert c['qa_pose_original_column']==7 and c['qa_actual_ability_uses']==1 and c['qa_actual_cooldown']>0
   elif c['segment'].startswith('V_finisher_'):assert c['qa_pose_original_column']=={'unarmed':1,'blunt':2,'environmental':5}[c['qa_job_category']]
 analyses.append({'label':label,'result_sha256':h(p),'assertions':len(j['checks']),'trace_samples':len(j['trace']),'contacts':len(cs),'finisher_contacts':len(fins),'incoming_interrupts':len(incoming),'routes':routes,'live_receipts_and_impulse_observed':label=='independent-observer'})
save('runtime-signal-analysis.json',{'recordings':analyses,'scope':'FINITE_CLOCK_CONTACT_AND_LOCOMOTION_TRACE_ANALYSIS_ONLY','not_physical_input_or_FPS_or_ART_quality':True})
inv=json.loads((Q/'copy-inputs-accepted.json').read_text());author=[];copies=[]
for mode in ['native-03','movie-03']:
 p=B/mode/'validation.json';j=json.loads(p.read_text());assert j['passed'] and j['source_unchanged'] and j['source_head']=='589907497d184d27a0f5183e8f0291dd7dd36b3e' and json.loads((p.parent/'source_hashes.json').read_text())==inv
 for a in j['artifacts']:assert h(W/a['path'])==a['sha256'],a['path']
 assert all(c['passed'] and c['exit_code']==0 for c in j['commands'])
 author.append({'mode':mode,'validation_sha256':h(p),'checks':j['checks'],'actual_PNGs':j['actual_captures'],'artifact_hashes_verified':len(j['artifacts']),'source_inventory_exact':len(inv)})
 for f in [p,p.parent/'commands.json']:
  d=Q/'author-evidence'/f.relative_to(B);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
 if mode=='movie-03':assert j['reused_completed_live']['sha256']==h(B/'native-03/validation.json')
receipts=[]
for op in ['3c1b568018f34fcfa3bebb77a0293a37','e130daa4d2be4f7bacb825578ab92feb','7ad76d5b23004f738ebd3cfa07c92fc9']:
 job=R/'.autopilot/jobs'/op;r=json.loads((job/'receipt.json').read_text());i=json.loads((job/'input.json').read_text());assert r['exit_code']==0 and r['log_sha256']==h(job/'output.log') and r['argv_sha256']==i['argv_sha256'];receipts.append({'receipt':r,'receipt_sha256':h(job/'receipt.json'),'actual_argv_and_output_log_hash_match':True})
old=json.loads((Q/'superseded-3a9ff-interruption/audit.json').read_text());oldjob=R/'.autopilot/jobs'/old['operation'];assert h(oldjob/'receipt.json')==old['receipt_sha256']
for a in old['partial_movie_files']:assert h(W/a['path'])==a['sha256']
closure=json.loads((Q/'copy-inputs-closure.json').read_text())
for k,v in closure.items():assert h(Q/'isolated-final'/k)==v,k
save('author-evidence-verification.json',{'author_runs_not_independent_reruns':author,'copies':copies,'receipts':receipts,'old_exit130_receipt_and_partialAVI_unchanged':True,'original_isolated_inputs_after_all_probes_exact':len(closure),'production_code_and_art_unchanged_by_QA':True,'counter_test_only_closure_commit':'9b42df871e53758b402108cb7cc00a2e385ab773'})
print(json.dumps({'recordings':len(analyses),'each_routes_verified':8,'each_contacts':49,'observedheavy0damage85impulse':29,'finisher_contacts_each':18,'author':author,'receipts_verified':len(receipts),'all1112copy_inputs_exact':True}))
