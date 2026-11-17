"""Independent extraction from actual QA/runtime records, no engine execution."""
from pathlib import Path
import json,hashlib,math,shutil
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';Q=R/'reports/phases/P06/qa-tega-environment-03';old=R/'reports/phases/P06/qa-tega-environment-02'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda n,d:(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
probes=['qa_tega_callback_geometry.gd','qa_tega_callback_physics.gd','qa_tega_callback_extended.gd','qa_tega_negative_final.gd','qa_tega_actor_wall.gd']
for name in probes:assert sha(Q/name)==sha(old/name)
clean=(Q/'qa_tega_clean_geometry.gd').read_text();assert '_near_foot(' not in clean and 'force_update_transform(' not in clean
base=(Q/'qa_tega_callback_geometry.gd').read_text();assert 'process_physics_priority=1000' in clean.replace(' ','')
d=json.loads((Q/'clean-geometry/result.json').read_text());assert d['passed'] is True and len(d['checks'])==5 and all(c['passed'] is True for c in d['checks'])
a=d['proof']['callback'];b=d['proof']['same_tick_after_Core'];before=a['after_change'];after=b['raw_geometry_after_Core']
assert a['tick']==b['tick']==19 and before['Node_body']==[308,256] and before['PhysicsServer_body']==[308,240]
assert before['direct_current_Node_collide'] is False and before['direct_server_collide'] is True and before['DirectSpaceState_overlap'] is True
assert after['PhysicsServer_body']==after['Node_body']==[308,256] and after['DirectSpaceState_overlap'] is False and after['direct_server_collide'] is False
assert b['actor_delta']==b['prop_delta']==[0,0] and b['jobs']==0
assert a['damage_events']==b['damage_events']==a['receipt_count']==b['receipt_count']==0
assert all(a[k]==b[k] for k in ['source_mask','object_mask','source_exceptions','object_exceptions'])
physics=json.loads((Q/'physics-qualification/result.json').read_text());assert len(physics['checks'])==15 and all(c['passed'] is True for c in physics['checks'])
ra=physics['proofs'][-1]['callback'];rb=physics['proofs'][-1]['same_tick_after_Core']
assert ra['new_action_started'] is True and ra['old_epoch']==6 and ra['new_epoch']==7 and ra['old_action_id']==ra['new_action_id']==1 and ra['jobs']==1
assert ra['tick']==rb['tick']==137 and rb['epoch']==7 and rb['action_id']==1 and rb['action_kind']=='special' and rb['jobs']==1 and rb['job_epochs']==[7] and rb['job_ids']==[1] and rb['authorized'] is True
job=json.loads((Q/'engine-job08-result.json').read_text());order=[v['name'] for v in job['results']];assert order[:2]==['import','clean-geometry'] and all(v['passed'] is True and v['exit_code']==0 for v in job['results'])
counts={name:len(json.loads((Q/name/'result.json').read_text())['checks']) for name in order if name!='import'};assert counts=={'clean-geometry':5,'geometry-closure':8,'physics-qualification':15,'callback-extended':12,'tega-negative':26,'actor-wall':4,'tega':305,'counter-fixed':57,'source-owner-smoke':29} and sum(counts.values())==461
dest=O/'QA08-proof-subset';dest.mkdir(exist_ok=True)
for name in ['qa_tega_clean_geometry.gd','qa_tega_callback_geometry.gd','qa_tega_callback_physics.gd','engine-job08-result.json','post-run08-integrity.json','probe-freeze.json','job08-manifest.json','clean-geometry/result.json','clean-geometry/command.json','clean-geometry/run.log','physics-qualification/result.json']:
 p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Q/name,p)
write('causal-closure-proofs.json',{'source_head':'20cbc322441a80675907bf407f12962778c6c084','clean_callback_only_Node_mutation_no_helper_no_force':True,'same_tick_before_and_after':{'callback':a,'after_Core':b},'clean_first_after_fresh_import':True,'original_five_independent_probes_byte_exact':{p:sha(Q/p) for p in probes},'epoch_replacement':{'callback':ra,'after_Core':rb},'comparative15_ordering_caveat':'Earlier geometry fields precede helper call; runtime_near_foot can synchronize20c. Clean5 supplies non-mutating causal proof.','actual_independent_counts':counts,'actual_assertions':461,'remote_damage_or_duplicate_receipts_observed':False,'reviewer_engine_runs':0})
results=[]
for run,mode in [('headless-06','live'),('native-03','live'),('native-03','movie')]:
 p=W/'reports/phases/P06/tega-environment-01'/run/mode/'result.json';d=json.loads(p.read_text());ts=d['trace'];cs=d['contacts'];objects={x['tick']:x for x in d['object_trace']};assert all(c['passed'] is True for c in d['checks'])
 paths={}
 for mode2 in ['false','true']:
  for direction in ['down','left','right','up']:
   seg='object_hit_'+mode2+'_'+direction;rows=[t for t in ts if t['segment']==seg and t['action_kind']=='special'];start=rows[0]['position'];objstart=objects[rows[0]['tick']]['object'];relative=[objstart[i]-start[i] for i in range(2)]
   errs=[math.dist([objects[t['tick']]['object'][i]-t['position'][i] for i in range(2)],relative) for t in rows if t['tick'] in objects];hits=[c for c in cs if c['segment']==seg]
   assert max(errs)<.02 and len(hits)==1 and hits[0]['damage']==1 and hits[0]['player_action_frame']==1 and not hits[0]['finisher']
   assert list(dict.fromkeys(t['action_frame'] for t in rows))==[0,1,2]
   paths[seg]={'max_relative_error':max(errs),'actor_distance':math.dist(start,rows[-1]['position']),'contact_pose':1}
 fs={c['segment'] for c in cs if c['finisher']};assert len(fs)==24
 for seg in fs:
  hits=[c for c in cs if c['segment']==seg];assert len(hits)==2 and hits[0]['damage']==0 and hits[1]['finisher'] and hits[1]['damage']==1 and hits[1]['lethal'] and hits[1]['player_frame']==1
  last=[t for t in ts if t['segment']==seg][-1];assert last['score']==100 and last['damage_events']==2
 incoming=[c for c in cs if c['segment'].startswith('incoming_')]
 assert len(incoming)==6 and all(c['damage']==1 and c['target_is_player'] for c in incoming)
 mode_pairs=[c for c in d['checks'] if c['name'].startswith('finisher_true_') and c['name'].endswith(':Full_Reduced_identical')]
 assert len(mode_pairs)==12
 nr=[t for t in ts if t['segment']=='reset_new_epoch_same_kind_F'];assert math.dist(nr[0]['position'],nr[-1]['position'])>30 and math.dist(nr[0]['position'],nr[-1]['position'])<=37.81 and nr[-1]['action_kind']=='' and all(t['damage_events']==0 for t in nr)
 side=[t for t in ts if t['segment']=='foot_geometry_sideways_same_instance'];assert max(math.dist(t['position'],side[0]['position']) for t in side)<.0001
 blood=d['clothing_overlay'];assert len(blood)==12 and all(b['ttl']>0 and math.dist(b['actual'],b['expected'])<=3.6 for b in blood)
 assert len(cs)==len({(c['epoch'],c['id'],c['target']) for c in cs})==66
 results.append({'run':run+'/'+mode,'sha256':sha(p),'checks':len(d['checks']),'actor_samples':len(ts),'object_samples':len(d['object_trace']),'unique_Core_contacts':len(cs),'paths':paths,'FIN_cases':24,'FIN_Full_Reduced_pairs':len(mode_pairs),'real_incoming_phase_contacts':len(incoming),'new_epoch_F_completed_distance':math.dist(nr[0]['position'],nr[-1]['position']),'sideways_actor_stays_put':True,'clothing_records':len(blood)})
write('current-runtime-proofs.json',results)
print(json.dumps({'clean5':True,'epoch15':True,'independent_actual':sum(counts.values()),'five_old_probes_exact':True,'runs':[{k:v for k,v in x.items() if k not in ['paths','sha256']} for x in results]}))
