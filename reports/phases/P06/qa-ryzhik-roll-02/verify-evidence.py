from pathlib import Path
import json,hashlib,math,shutil,subprocess
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/ryzhik-roll-01/native-03';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();inv=json.loads((Q/'copy-inputs-final.json').read_text());v=json.loads((B/'validation.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']=='8ad1729984321fbd646e96bbe9762a8c4cca689e' and json.loads((B/'source_hashes.json').read_text())==inv
for a in v['artifacts']:assert h(W/a['path'])==a['sha256'],a['path']
assert all(c['passed'] and c['exit_code']==0 for c in v['commands']);analyses=[];sockets=json.loads((Q/'isolated-project/game/assets/art/characters/ryzhik/roll.sockets.json').read_text())['frames']
for name,p in [('independent-original',Q/'roll/result.json'),('independent-mode-observer',Q/'roll-observer/result.json'),('author-live',B/'live/result.json'),('author-movie',B/'movie/result.json')]:
 j=json.loads(p.read_text());assert j['passed'] and all(c['passed'] for c in j['checks']);fin=[c for c in j['contacts'] if c['finisher']];assert len(fin)==24 and len(j['contacts'])==61 and len({(c['epoch'],c['id'],c['target']) for c in j['contacts']})==61
 for reduced in [False,True]:
  for category in ['unarmed','blunt','environmental']:
   for direction in ['down','left','right','up']:
    segment='finisher_'+str(reduced).lower()+'_'+category+'_'+direction;cs=[c for c in fin if c['segment']==segment];assert len(cs)==1 and cs[0]['player_frame']==1 and cs[0]['player_animation']=='finish_'+category+'_'+direction and cs[0]['lethal']
    for suffix in [':NPC_dead_contact_then_once_reward',':NPC_own_corpse2',':no_repeat_damage_score_or_job']:
     assert next(c for c in j['checks'] if c['name']==segment+suffix)['passed']
 comparisons=[c for c in j['checks'] if c['name'].endswith(':Full_Reduced_same_once_health_score')];assert len(comparisons)==12
 for c in comparisons:assert c['details']['Full']==c['details']['Reduced']==[0,2,100,2,1,0]
 overlays=j['clothing_overlay'];assert len(overlays)==8
 for i,o in enumerate(overlays):
  assert o['animation']=='roll_up' and o['frame']==o['source_column']==i and o['clothing_socket']==sockets[24+i]['clothing'] and o['remaining_ttl']>0 and math.dist(o['world_anchor'],o['live_decal_at'])<=3.2
  if i:assert o['remaining_ttl']<overlays[i-1]['remaining_ttl'] and o['tick']>overlays[i-1]['tick']
 blood=[c for c in j['contacts'] if c['segment']=='persistent_blood_UP_roll'];assert len(blood)==1 and blood[0]['target_is_player'] and not blood[0]['lethal']
 if name=='independent-mode-observer':
  assert all(c['qa_receipt_reserved'] for c in j['contacts'])
  for c in fin:
   actual=c['segment'].startswith('finisher_true_');assert c['qa_actual_reduced_mode']==c['qa_impact_reduced_mode']==actual and c['qa_NPC_palette_bound'] and c['qa_NPC_contact_frame']==1 and c['qa_NPC_state']=='dead' and c['qa_NPC_health']==0
 analyses.append({'recording':name,'result_sha256':h(p),'checks':len(j['checks']),'contacts':61,'unique_Core_tokens':True,'FIN_Full':12,'FIN_Reduced':12,'paired_outcomes':12,'NPC_contact1_corpse2_assertions_passed':24,'live_blood_UP_overlays':overlays,'actualmode_palette_and_receipts_observed':name=='independent-mode-observer'})
(Q/'mode-contact-overlay-analysis.json').write_text(json.dumps({'scope':'ACTUAL_FIN_MODES_CONTACTS_CORPSES_AND_LIVE_CLOTHING_ATTACHMENT','recordings':analyses,'anchor_tolerance':'Existing3.2worldpx bound permits one180px/s physics-tick effect-follow delay; no zero-lag assertion.'},indent=2)+'\n')
job=R/'.autopilot/jobs/f528286cc19148e4a96bf6248afb0f61';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256'];copies=[]
for f in [B/'validation.json',B/'commands.json']:
 d=Q/'author-evidence'/f.name;d.parent.mkdir(exist_ok=True);shutil.copyfile(f,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(f.relative_to(W)),'sha256':h(d)})
movie=Path(v['movie_path']);p=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,timeout=30);assert p.returncode==0
(Q/'artifact-verification.json').write_text(json.dumps({'source_head':v['source_head'],'source_inventory_count':len(inv),'checks':v['checks'],'actual_PNG':v['actual_captures'],'artifact_SHA_verified':len(v['artifacts']),'receipt':receipt,'receipt_SHA':h(job/'receipt.json'),'actual_log_and_argv_match':True,'copies':copies,'movie_path':str(movie.relative_to(W)),'movie_SHA':h(movie),'movie_bytes':movie.stat().st_size,'ffprobe':json.loads(p.stdout),'not_listening_hostFPS_or_nativeWindows_acceptance':True},indent=2)+'\n')
for k,sha in inv.items():assert h(Q/'isolated-project'/k)==sha,k
old=Q.parent/'qa-ryzhik-roll-01';assert all(h(old/k)==s for k,s in json.loads((old/'FINAL_HASHES.json').read_text()).items());(Q/'post-run-integrity.json').write_text(json.dumps({'original_isolated_inputs_exact':len(inv),'prior407QA_FINAL_HASHES_unchanged':True,'only_extra_QA_scripts':['game/tests/qa_roll_negative.gd','game/tests/qa_roll_mode_observer.gd'],'WORK_Git_controller_network_mutations_by_QA':False,'own_engine_processes_remaining':0},indent=2)+'\n');obs=json.loads((Q/'roll-observer/result.json').read_text());(Q/'observer-selected-proof.json').write_text(json.dumps({'scope':'ADDITIONAL_ACTUALMODE_NPCPALETTE_RECEIPT_PROOF','full_local_raw_result_SHA':h(Q/'roll-observer/result.json'),'full_raw_repeated_trace_not_portable':True,'checks':len(obs['checks']),'contacts':obs['contacts'],'clothing_overlay':obs['clothing_overlay']},indent=2)+'\n');print(json.dumps({'recordings':len(analyses),'each_contacts':61,'each_FIN_modes':[12,12],'each_pairs':12,'each_blood_poses':8,'native':v['checks'],'PNG':v['actual_captures'],'artifacts':len(v['artifacts']),'source_exact':len(inv),'receipt0':True}))
