from pathlib import Path
import json,hashlib,shutil,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';base=W/'reports/phases/P06/timka-present-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,j):(Q/n).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
freeze=json.loads((Q/'source-freeze.json').read_text());inv=json.loads((Q/'copy-inputs.json').read_text());author=[];copies=[]
for mode in ['native-02','headless-03']:
 p=base/mode/'validation.json';j=json.loads(p.read_text());assert j['passed'] and j['source_unchanged'] and j['source_head']==freeze['frozen_commit']
 for a in j['artifacts']:assert h(W/a['path'])==a['sha256'],a['path']
 src=json.loads((p.parent/'source_hashes.json').read_text());assert src==inv
 assert all(c['passed'] and c['exit_code']==0 for c in j['commands'])
 author.append({'mode':mode,'source_head':j['source_head'],'passed':True,'checks':j['checks'],'pngs':j['actual_captures'],'verified_artifacts':len(j['artifacts']),'all_source_inventory_keys_exact':len(src)})
 for f in [p,p.parent/'source_hashes.json',p.parent/'live/result.json']+([p.parent/'movie/result.json'] if mode=='native-02' else []):
  d=Q/'author-evidence'/f.relative_to(base);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
for name in ['Core_melee_guard_hurt_actual_contact.png','Core_melee_active_fatal_actual_contact.png','projectile_interrupts_actual_step.png']:
 f=base/'native-02/live'/name;d=Q/'author-evidence/native-02/live'/name;shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
save('author-evidence-verification.json',{'author_runs_inspected_not_independent_reruns':author,'byte_exact_copies':copies})
job=R/'.autopilot/jobs/aa48250aa17740bdaf85d444216380c5';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
state=json.loads((R/'.autopilot/STATE.json').read_text());records=[e for e in state.get('history',[]) if 'aa48250aa17740bdaf85d444216380c5' in json.dumps(e)]
save('producer-receipt-verification.json',{'receipt':receipt,'receipt_sha256':h(job/'receipt.json'),'input_sha256':h(job/'input.json'),'actual_log_sha256':h(job/'output.log'),'exit0_argv_and_log_verified':True,'canonical_history_matching_records':records,'consumed_state_limit':'Parent reports completed/consumed; history records inspected here. No Controller call; no old current-operation equality required.'})
expected=['Core_melee_'+phase+'_'+outcome for phase in ['guard','active','recovery'] for outcome in ['hurt','fatal']]+['Core_projectile_during_active'];summ=[]
for label,p in [('independent-original',Q/'present/result.json'),('independent-receipt-observer',Q/'incoming/result.json'),('author-native',base/'native-02/live/result.json'),('author-movie',base/'native-02/movie/result.json')]:
 j=json.loads(p.read_text());assert j['passed'] and all(c['passed'] for c in j['checks']);cs=j['contacts'];assert len(cs)==7 and [c['segment'] for c in cs]==expected
 assert len({(c['epoch'],c['id'],c['target']) for c in cs})==7
 details=[]
 for c in cs:
  seg=c['segment'];fatal=seg.endswith('_fatal');assert c['target_is_player'] and c['damage']==1 and c['lethal']==fatal
  assert c['category']==('firearm' if seg.startswith('Core_projectile') else 'unarmed')
  if not seg.startswith('Core_projectile'):
   check=next(x for x in j['checks'] if x['name']==seg+':live_overlap_receipt_and_damage');d=check['details'];e=d['clock_before_contact'];frame=d['frame_before_contact'];assert d['contact_count']==1 and d['attack_id']==c['id']
   assert (e<.12 and frame==0) if '_guard_' in seg else ((.12<=e<.36 and frame in [1,2,3,4]) if '_active_' in seg else (.36<=e<.54 and frame==5))
   details.append({'segment':seg,'before_clock':e,'before_frame':frame,'contact_tick':c['tick'],'epoch':c['epoch'],'attack_id':c['id'],'fatal':fatal})
  if label=='independent-receipt-observer':
   assert c['qa_actual_receipt_reserved'] and c['qa_actual_receipt_count']==1 and c['qa_damage_events']==1 and c['qa_hits_received']==1
   assert c['qa_health_after']==(0 if fatal else 1) and c['qa_action_after']==('fall' if fatal else 'hit')
   assert c['qa_counter_blocks']==0 and c['qa_score']==0 and c['qa_collision_mask']==1 and c['qa_collision_layer']==2 and c['qa_active_fixture']=='timka_present'
   prev=c['qa_previous_trace'];assert prev['segment']==seg and prev['action_kind']=='disengage' and c['tick']==prev['tick']+1
   e=prev['action_elapsed']+1/60
   if '_guard_' in seg:assert e<.12
   elif '_recovery_' in seg:assert .36<=e<.54
   else:assert .12<=e<.36
 summ.append({'label':label,'result_sha256':h(p),'checks':len(j['checks']),'incoming_contacts':len(cs),'unique_receipts_by_epoch_id_target':7,'phase_details':details,'live_receipt_snapshot_verified':label=='independent-receipt-observer'})
save('incoming-contact-analysis.json',{'recordings':summ,'limits':'Production delivery and bounded interruption evidence only; disabled enemy AI and explicit initial placements before Input, not AI fairness or hardware latency.'})
for key,sha in inv.items():assert h(Q/'isolated-project'/key)==sha,key
save('post-run-integrity.json',{'all_original_copied_inputs_exact':len(inv),'new_isolated_probe_only':'game/tests/qa_timka_incoming_replay.gd','engine_copy_separate':True,'no_WORK_mutation_by_QA':True,'no_canonical_or_controller_mutation_by_QA':True,'later_author_changes':'Allowed after own engine-finished signal. Review remains bound to saved2780 snapshots.'})
movie=Path(json.loads((base/'native-02/validation.json').read_text())['movie_path']);assert movie.is_relative_to(W/'build');p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,timeout=30);assert p.returncode==0
save('actual-movie-container.json',{'path':str(movie.relative_to(W)),'sha256':h(movie),'bytes':movie.stat().st_size,'ffprobe_exit0':True,'probe':json.loads(p.stdout),'limit':'Container verification only; no complete movie/listening/FPS acceptance.'})
print(json.dumps({'author':author,'contact_recordings':len(summ),'each_actual_contacts':7,'input_inventory_exact':len(inv),'receipt_verified':True}))
