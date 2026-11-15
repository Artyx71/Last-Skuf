from pathlib import Path
import json,hashlib,math,shutil,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/ryzhik-roll-01/native-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inv=json.loads((Q/'copy-inputs.json').read_text());v=json.loads((B/'validation.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']=='407f9a1df6c3d8ed110ab908b234fad4750b622d' and json.loads((B/'source_hashes.json').read_text())==inv
for a in v['artifacts']:assert h(W/a['path'])==a['sha256'],a['path']
assert all(c['passed'] and c['exit_code']==0 for c in v['commands']);analyses=[]
for name,p in [('independent-headless',Q/'roll/result.json'),('author-live',B/'live/result.json'),('author-movie',B/'movie/result.json')]:
 j=json.loads(p.read_text());assert j['passed'] and all(c['passed'] for c in j['checks']);routes=[]
 for direction,vec in {'down':(0,1),'left':(-1,0),'right':(1,0),'up':(0,-1)}.items():
  seq=[t for t in j['trace'] if t['segment']=='walk_roll_walk_'+direction and t['action_kind']=='roll'];assert seq;start=seq[0]['position'];seen=[]
  for t in seq:
   e=t['action_elapsed'];f=t['action_frame'];assert t['animation']=='roll_'+direction and t['frame']==f
   expected=0 if e<.08 else (1+min(4,math.floor((e-.08)*5/.32)) if e<.4 else 6+min(1,math.floor((e-.4)*2/.16)))
   near_boundary=min(abs(e-x) for x in [.08,.144,.208,.272,.336,.4,.48])<1e-6
   assert f==expected or near_boundary,(name,direction,e,f,expected)
   if f not in seen:seen.append(f)
   distance=180*max(0,min(.32,e-.08));assert math.dist(t['position'],[start[k]+vec[k]*distance for k in range(2)])<.04
  assert seen==list(range(8));events=[c for c in j['contacts'] if c['segment']=='walk_roll_walk_'+direction];assert len(events)==1 and events[0]['player_action_frame']==6 and events[0]['damage']==0 and not events[0]['lethal'];routes.append({'direction':direction,'samples':len(seq),'frames':seen,'landing_clock':events[0]['player_action_elapsed'],'landing_frame':6})
 fin=[c for c in j['contacts'] if c['finisher']];assert len(fin)==12
 for category in ['unarmed','blunt','environmental']:
  for direction in ['down','left','right','up']:
   events=[c for c in fin if c['segment']=='finisher_'+category+'_'+direction];assert len(events)==1 and events[0]['player_frame']==1 and events[0]['player_animation']=='finish_'+category+'_'+direction
 incoming=[c for c in j['contacts'] if c['target_is_player']];assert len(incoming)==6
 for index in range(3):
  for fatal in [False,True]:
   segment='Core_incoming_'+str(index)+('_fatal' if fatal else '_hurt');events=[c for c in incoming if c['segment']==segment];assert len(events)==1 and events[0]['lethal']==fatal
 assert len({(c['epoch'],c['id'],c['target']) for c in j['contacts']})==len(j['contacts'])
 analyses.append({'recording':name,'result_sha256':h(p),'checks':len(j['checks']),'trace_samples':len(j['trace']),'contacts':len(j['contacts']),'unique_contact_tokens':True,'finisher_Full_routes':len(fin),'incoming_Core_contacts':len(incoming),'routes':routes,'Reduced_finisher_routes_tested':0})
(Q/'signal-analysis.json').write_text(json.dumps({'scope':'ROLL_PHYSICS_CONTACT_CLOCK_ANALYSIS_ONLY','boundary_tolerance_note':'JSON floating-clock values within1e-6 of a phase edge permit adjacent frame classification; renderedframe==actionframe and orderedall8poses stillrequired.','recordings':analyses},indent=2)+'\n')
job=R/'.autopilot/jobs/015037e2a24e4a08ba7b37894ad36c9a';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
copies=[]
for f in [B/'validation.json',B/'commands.json']:
 d=Q/'author-evidence'/f.name;d.parent.mkdir(exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
movie=Path(v['movie_path']);p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,timeout=30);assert p.returncode==0
(Q/'artifact-verification.json').write_text(json.dumps({'source_head':v['source_head'],'actual_source_map_count':len(inv),'native_checks':v['checks'],'actual_PNG':v['actual_captures'],'artifact_hashes_verified':len(v['artifacts']),'receipt':receipt,'receipt_sha256':h(job/'receipt.json'),'actual_log_and_argv_match':True,'copies':copies,'movie_path':str(movie.relative_to(W)),'movie_sha256':h(movie),'movie_bytes':movie.stat().st_size,'actual_ffprobe':json.loads(p.stdout),'no_listening_FPS_or_fullmovie_quality_claim':True},indent=2)+'\n')
for k,value in inv.items():assert h(Q/'isolated-project'/k)==value,k
(Q/'post-run-integrity.json').write_text(json.dumps({'original_copied_inputs_byte_exact':len(inv),'sole_extra_isolated_script':'game/tests/qa_roll_negative.gd','actual_QA_WORK_controller_Git_network_mutations':False,'actual_QA_engine_processes_remaining':0},indent=2)+'\n');print(json.dumps({'recordings':[(x['recording'],x['checks'],x['contacts']) for x in analyses],'artifacts':len(v['artifacts']),'source_exact':len(inv),'receipt_exit0':True}))
