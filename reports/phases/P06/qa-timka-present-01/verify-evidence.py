from pathlib import Path
import json,hashlib,shutil,subprocess,math,ast
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';base=W/'reports/phases/P06/timka-present-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,j):(Q/n).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
freeze=json.loads((Q/'source-freeze.json').read_text());inv=json.loads((Q/'copy-inputs.json').read_text());copies=[];summaries=[]
for mode in ['native-01','headless-02']:
 p=base/mode/'validation.json';j=json.loads(p.read_text());assert j['passed'] and j['source_unchanged']
 if mode=='native-01':assert j['source_head']==freeze['frozen_commit']
 for a in j['artifacts']:
  assert h(W/a['path'])==a['sha256'],a['path']
 source=json.loads((p.parent/'source_hashes.json').read_text());matched=[]
 for key,sha in freeze['files_sha256'].items():
  if mode=='native-01':assert source[key]==sha,key
  if source.get(key)==sha:matched.append(key)
 summaries.append({'mode':mode,'passed':j['passed'],'source_head':j['source_head'],'source_unchanged':j['source_unchanged'],'checks':j['checks'],'captures':j['actual_captures'],'verified_artifacts':len(j['artifacts']),'source_matches_13_keys':matched})
 for f in [p,p.parent/'source_hashes.json',p.parent/'live/result.json']+([p.parent/'movie/result.json'] if mode=='native-01' else []):
  d=Q/'author-evidence'/f.relative_to(base);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
for name in ['native-01/live/disengage_down_phase2.png','native-01/live/wall_stops_backward_step.png','native-01/live/present_ready_after_restart.png','headless-01/validation.json','headless-01/live/result.json']:
 f=base/name;d=Q/'author-evidence'/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
save('author-evidence-verification.json',{'summaries':summaries,'byte_exact_copies':copies,'old_failure_preserved':True})
job=R/'.autopilot/jobs/02171a295d694f9abc8ceefac80f13c6';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
save('producer-receipt-verification.json',{'receipt':receipt,'receipt_sha256':h(job/'receipt.json'),'input_sha256':h(job/'input.json'),'actual_log_sha256':h(job/'output.log'),'exit0_and_hashes_verified':True,'consumed':'Consumed receipt reported by parent; operation-independent durable completion/log verified here; no Controller mutation.'})
summary=[]
for label,p in [('independent-headless',Q/'present/result.json'),('author-native',base/'native-01/live/result.json'),('author-movie',base/'native-01/movie/result.json')]:
 j=json.loads(p.read_text());checked=0;directions={'down':(0,1),'left':(-1,0),'right':(1,0),'up':(0,-1)};groups=[]
 for direction,vec in directions.items():
  seq=[t for t in j['trace'] if t['segment']=='disengage_'+direction and t['action_kind']=='disengage'];assert seq
  start=seq[0]['position'];seen=[]
  for t in seq:
   e=t['action_elapsed'];expected=0 if e<.12 else (1+min(3,math.floor((e-.12)*4/.24)) if e<.36 else 5)
   assert t['action_frame']==expected and t['frame']==expected,(label,direction,t)
   assert t['animation']=='disengage_'+direction and t['damage_events']==0 and t['score']==0
   progress=max(0,min(.24,e-.12))*140;desired=[start[0]-vec[0]*progress,start[1]-vec[1]*progress]
   assert math.dist(desired,t['position'])<.03,(label,direction,e,desired,t['position'])
   if expected not in seen:seen.append(expected)
   checked+=1
  assert seen==[0,1,2,3,4,5];groups.append({'direction':direction,'checked_samples':len(seq),'six_phases':seen})
 summary.append({'label':label,'source_sha256':h(p),'all_trace_samples':len(j['trace']),'checked_disengage_samples':checked,'directions':groups,'incoming_core_contacts':len(j['contacts'])})
save('actual-trace-analysis.json',{'checks':summary,'method':'Read actual per-tick trace; recompute authored frame/animation/33.6px path from finite actor elapsed clock. No independent native replay or hardware-input claim.'})
for key,sha in inv.items():assert h(Q/'isolated-project'/key)==sha,key
save('post-run-integrity.json',{'original_isolated_inputs_exact_after_metadata_adversaries':len(inv),'qa_work_mutations':False,'qa_canonical_state_mutations':False,'new_isolated_file':'game/tests/qa_timka_negative.gd','work_code_basis':'Frozen snapshots verified before author fixes; later WORK changes are allowed and not silently represented as reviewed.'})
verify=(Q/'code-freeze/tools/verify.py').read_text();ast.parse(verify);assert 'tools/verify_p06_timka_present.py' not in verify
save('CI-registration-finding.json',{'id':'TP-Q01','severity':'MEDIUM','frozen_verify_sha256':h(Q/'code-freeze/tools/verify.py'),'timka_present_wrapper_registered':False,'existing_wrappers_present':all(s in verify for s in ['verify_p06_gabar.py','verify_p06_olezhka.py','verify_p06_counter_feedback.py']),'scope':'Static actual common-verifier source inspection; no remote CI executed.'})
movie=W/'build/P06/timka-present-01/timka-present.mp4';p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,timeout=30);assert p.returncode==0
save('actual-movie-container.json',{'path':str(movie.relative_to(W)),'bytes':movie.stat().st_size,'sha256':h(movie),'ffprobe_exit0':True,'probe':json.loads(p.stdout),'limit':'Container verification only; no listening, performance or complete visual approval.'})
print(json.dumps({'author_summaries':[{k:v for k,v in s.items() if k!='source_matches_13_keys'} for s in summaries],'trace_samples':[{k:s[k] for k in ['label','checked_disengage_samples','incoming_core_contacts']} for s in summary],'copied_source_integrity':len(inv),'receipt_verified':True}))
