from pathlib import Path
import hashlib,json,subprocess,re
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P07';O=R/'reports/pre_p07/qa-second-pilot-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def copy(p,d):
 d.parent.mkdir(parents=True,exist_ok=True)
 if d.exists():assert d.read_bytes()==p.read_bytes()
 else:d.write_bytes(p.read_bytes())
def save(n,x):
 p=O/n;assert not p.exists();p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
refs=[]
def record(p,d):
 copy(p,O/d);refs.append({'origin':str(p.relative_to(R)),'copy':d,'sha256':sha(p),'bytes':p.stat().st_size})
summary={}
contexts=['yakuza','gabar_training','olezhka_training','timka_present','timka_prime','ryzhik_training','tega_training','pasha_training']
for dirname in ['second-pilot-06','navigation-contract-after-shortcut-01','room-pilot-after-shortcut-01']:
 d=W/'reports/pre_p07'/dirname;b=j(d/'source_before.json');a=j(d/'source_after.json');assert b==a and len(b)==(535 if dirname=='navigation-contract-after-shortcut-01' else 613)
 mismatches=[n for n,h in a.items()if not(W/n).is_file() or sha(W/n)!=h];assert not mismatches
 summary[dirname]={'source_count':len(b),'before_after_exact':True,'current_source_exact':True,'modes':{}}
 for p in sorted(d.iterdir()):
  if p.is_file() and p.suffix in ['.json','.log']:record(p,'actual-evidence/'+dirname+'/'+p.name)
 for fn in ['pilot-result.json','native-result.json','engine_result.json','room-result.json']:
  p=d/fn
  if not p.exists():continue
  x=j(p);cs=x['checks'];vals=list(cs.values()) if isinstance(cs,dict)else[c['passed']for c in cs]
  assert vals and all(v is True for v in vals)
  if isinstance(cs,list):assert x['passed']==len(cs) and x['failed']==0
  z={'actual_checks':len(vals),'all_typed_true':True}
  if dirname=='second-pilot-06':
   rr=[row for row in x['rows']if 'context'in row];assert len(rr)==8 and sorted(row['context']for row in rr)==sorted(contexts)
   assert all(row['stage']=='complete'and row['completions']==1 for row in rr)
   assert x['completed_Input_routes']==8
   for c in cs:
    if c['check'].endswith('/continuous_collision_clearance'):assert c['details']['overlap']is False and c['details']['jump']is False and not c['details']['first_failures']
   z|={'unique_complete_once_contexts':contexts,'walk_no_run_checks':sum(c['check'].endswith('/Input_walk_mode_no_run')for c in cs),'own_ability_checks':sum(c['check'].endswith('/own_ability_real_wall_clearance')for c in cs),'AI_cache_cases':[{k:v for k,v in row.items()if k!='result'}|{'result':{k:v for k,v in row['result'].items()if k!='trace'}}for row in x['rows']if'kind'in row],'display_backend':x['display_backend'],'window_no_focus_flag':x['window_no_focus_flag'],'wall_frame_summary_reported_not_independently_recomputed':x['wall_frame_ms']}
   assert z['walk_no_run_checks']==8 and z['own_ability_checks']==7
  if dirname=='room-pilot-after-shortcut-01'and fn=='native-result.json':
   assert x['passed']is True and x['actual_input']is True and x['route_warps']==0 and len(x['deaths'])==10
   assert x['progress']['completion_events']==1
   z|={'route_warps':0,'actual_input':True,'deaths':len(x['deaths']),'completion_events':1,'captures':len(x['captures'])}
   for c in x['captures']:
    p=Path(c['path']);assert c['error']==0 and p.is_file();refs.append({'origin':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size,'retained_in_place':True})
  summary[dirname]['modes'][fn]=z
 for p in sorted((d/'native-captures').glob('*.png')):record(p,'actual-evidence/'+dirname+'/native-captures/'+p.name)
 for p in d.glob('*.log'):
  text=p.read_text();assert not any(s in text for s in ['SCRIPT ERROR','Parse Error','ERROR:'])
# Prove the old cache loop and its actual isolated source, without executing engines.
d=W/'reports/pre_p07/second-pilot-shortcut-before-01'
for n in ['execution.py','proof.json','result.json','probe.log','import.log']:record(d/n,'actual-evidence/second-pilot-shortcut-before-01/'+n)
# Critical connected sources; no generated cache or complete game tree in portable evidence.
for n in ['game/scripts/ai/room_navigation.gd','game/scripts/ai/room_navigation_host.gd','game/scripts/actors/enemy_actor.gd','game/scripts/actors/yakuza_actor.gd','game/scripts/actors/character_player.gd','game/scripts/systems/character_scene_policy.gd','game/resources/characters/catalog.json','tools/p07_second_pilot.py','tools/fixtures/p07_second_pilot.gd','tools/fixtures/p07_second_pilot_host.gd','tools/p07_navigation_contract.py','tools/fixtures/p07_navigation_contract.gd','tools/p07_room_pilot.py']:
 record(W/n,'final-source/'+n)
# Durable terminal receipt + exact invocation/log; input.json is immutable submission, not consumption authority.
d=R/'.autopilot/jobs/0105c9c807cd4e9d8103f36fe0a0075e';receipt=j(d/'receipt.json');inp=j(d/'input.json');assert receipt['exit_code']==0 and sha(d/'output.log')==receipt['log_sha256'] and inp['argv_sha256']==receipt['argv_sha256']
for n in ['input.json','receipt.json','output.log']:record(d/n,'actual-evidence/operation-06/'+n)
record(R/'.tools/pre-p07-second-pilot06-job.py','actual-evidence/operation-06/entrypoint.py')
state=j(R/'automation/phase_state.json');op=state['autopilot']['operation'];assert op['id']==receipt['operation']and op['consumed']is True and op['exit_code']==0
save('canonical-terminal-observation.json',{'operation':op,'active_phase':state['active_phase'],'status':state['status'],'phase_attempts':state['attempts'],'authority':'automation/phase_state.json (selected read-only observation; not a replacement authority)'})
summary['terminal']={'receipt':receipt,'canonical_consumed':True,'engine_runs_by_reviewer':0}
summary['source_head_observed']=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()
summary['router_sha256']=sha(W/'game/scripts/ai/room_navigation.gd')
assert summary['router_sha256']=='f9f23f82d9219bbd39037fce5a3d65ff0bfc271ebaf6ab8e4199c108451d8697'
save('final-evidence-audit.json',summary);save('bound-input-inventory.json',{'schema':1,'records':refs})
print(json.dumps({'summary':summary,'bound_records':len(refs)},ensure_ascii=False)[:1500])
