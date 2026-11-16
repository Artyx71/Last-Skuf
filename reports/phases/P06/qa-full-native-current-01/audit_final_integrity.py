"""Run ONLY after canonical receipt and all native/performance work ended.
Read-only production integrity/manifest audit. No Godot, runner, Git/network or media decode.
"""
from pathlib import Path
import hashlib,json,math,re,ast,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/full-native-current-source-01';ID='8e8ab4a27ccd47ebacf5a66dd3b6780c';J=R/'.autopilot/jobs'/ID
# Dependency-free strict JSON, including duplicate/nonfinite/float overflow rejection.
def strict(s):
 def pairs(xs):
  result={}
  for k,v in xs:
   if k in result:raise ValueError('Duplicate '+k)
   result[k]=v
  return result
 def num(s):
  n=float(s)
  if not math.isfinite(n):raise ValueError(s)
  return n
 def bad(s):raise ValueError(s)
 return json.loads(s,object_pairs_hook=pairs,parse_float=num,parse_constant=bad)
def read(p):return strict(p.read_text())
if not (J/'receipt.json').exists():raise SystemExit('NOT READY: canonical receipt missing; no broad scan performed')
state=read(R/'automation/phase_state.json');op=state['autopilot'].get('operation') or {}
if op.get('id')!=ID or not op.get('consumed'):raise SystemExit('NOT READY: exact operation not consumed; parent confirmation required')
if not (P/'validation.json').exists():raise SystemExit('Finished worker lacks aggregate report; inspect failure manually; do not claim success')
cache={}
def sha(p):
 p=p.resolve()
 if p not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
  cache[p]=h.hexdigest()
 return cache[p]
receipt=read(J/'receipt.json');inputrec=read(J/'input.json');before=read(P/'source_hashes_before.json');after=read(P/'source_hashes_after.json');v=read(P/'validation.json');commands=read(P/'commands.json');plan=read(P/'plan.json');errors=re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL:|ObjectDB instances were leaked|resources still in use')
checks={
 'canonical_receipt_exact_operation':receipt.get('operation')==ID==op['id'],
 'canonical_command_hash_exact':receipt.get('argv_sha256')==inputrec.get('argv_sha256')==hashlib.sha256(json.dumps(inputrec['argv']).encode()).hexdigest(),
 'canonical_log_hash_exact':sha(J/'output.log')==receipt.get('log_sha256'),
 'canonical_exit_typed0':type(receipt.get('exit_code')) is int and receipt['exit_code']==0,
 'canonical_operation_consumed':op.get('consumed') is True,
 'expected_all13_completed':len(plan)==len(commands)==13 and v.get('stages_expected')==v.get('stages_completed')==13,
 'aggregate_phase_merge_native_approvals_false':all(v.get(k) is False for k in ['phase_approval','merge_approval','native_acceptance_approval']),
 'aggregate_source_and_HEAD_freeze':before==after and v.get('source_unchanged') is True and v.get('head_unchanged') is True and v.get('source_head')==v.get('head_after')=='beb30f319b2cf86a1799672ed24837c4640a9bee',
 'all_current_frozen_inputs_exist_and_hash_exact':all((W/k).is_file() and sha(W/k)==digest for k,digest in before.items()),
 'source_map_matches_frozen_review_input':before==read(Q/'inputs/source_hashes_before.json'),
}
rows=[];artifacts=[];seen=set()
for i,c in enumerate(commands):
 name=c['name'];folder=P/name;vp=folder/'validation.json';child=read(vp);log=P/'logs'/(name+'.log');text=log.read_text(errors='replace');r={'name':name,'validation_sha256':sha(vp),'checks':{
 'exact_name_and_argv_plan':name==plan[i]['name'] and c['argv']==plan[i]['argv'],
 'typed_exit0':type(c.get('exit_code')) is int and c['exit_code']==0,
 'clean_actual_wrapper_log':sha(log)==c.get('log_sha256') and not errors.search(text) and text.splitlines()[-1]=='exit_code=0',
 'actual_cleanup_no_unexpected_children':bool(c.get('cleanup_events')) and all(e.get('unexpected_live_children') is False and e.get('remaining_live_children')==[] for e in c['cleanup_events']),
 }}
 if isinstance(child,dict):
  cc=child.get('commands',[]);r['checks'].update({'child_phase_approval_false':child.get('phase_approval') is False,'child_sources_unchanged':child.get('source_unchanged',child.get('source_unchanged_after_import')) is True,'nonempty_typed_clean_child_commands':bool(cc) and all(isinstance(x,dict) and type(x.get('exit_code')) is int and x['exit_code']==0 and x.get('passed') is True for x in cc)})
  inventory=child.get('artifacts',[])
 elif isinstance(child,list):
  r['checks']['nonempty_structured_legacy_checks_and_command_rows']=bool(child) and all(isinstance(x,dict) and x.get('passed') is True and isinstance(x.get('name'),str) and (type(x.get('exit_code')) is int and x['exit_code']==0 and isinstance(x.get('log'),str) if 'exit_code' in x else isinstance(x.get('checks'),dict) and bool(x['checks']) and all(z is True for z in x['checks'].values())) for x in child)
  inventory=read(folder/'artifacts.json')
 else:r['checks']['known_child_schema']=False;inventory=[]
 for item in inventory:
  raw=Path(item['path']);path=raw if raw.is_absolute() else W/raw;resolved=path.resolve();record={'stage':name,'path':str(resolved.relative_to(W)) if resolved.is_relative_to(W) else str(resolved),'expected_sha256':item['sha256'],'actual_sha256':sha(path) if path.is_file() else None,'in_WORK':resolved.is_relative_to(W)};record['passed']=record['in_WORK'] and record['actual_sha256']==record['expected_sha256'];artifacts.append(record)
 r['checks']['nonempty_actual_artifact_inventory']=bool(inventory);r['checks']['all_actual_artifact_hashes_match']=all(x['passed'] for x in artifacts if x['stage']==name);r['passed']=all(r['checks'].values());rows.append(r)
checks['all13_raw_integrity_stages_passed']=all(x['passed'] for x in rows)
# Current Game body/data hash dictionary equals independently accepted0dd; verify actual current files too.
old=read(Q/'inputs/old0dd-source_hashes_before.json');game={k:d for k,d in before.items() if k.startswith('game/')};oldgame={k:d for k,d in old.items() if k.startswith('game/')};checks['current_Game_all533_exact_old0dd_and_current_disk']=game==oldgame and len(game)==533 and all(sha(W/k)==d for k,d in game.items())
out={'scope':'ACTUAL_FULL13_RAW_RECEIPT_LOG_SOURCE_AND_ARTIFACT_INTEGRITY_ONLY','checks':checks,'stages':rows,'artifact_records':artifacts,'unique_files_hashed':len(cache),'canonical_receipt':receipt,'canonical_input_sha256':sha(J/'input.json'),'canonical_started_sha256':sha(J/'started.json'),'aggregate_validation_sha256':sha(P/'validation.json'),'passed':all(checks.values()),'phase_approval':False,'actual_Godot_runner_or_Controller_invoked':False}
p=Q/'final-integrity-results.json';assert not p.exists();p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'failed_checks':[k for k,v in checks.items() if not v],'stages':len(rows),'artifacts':len(artifacts),'unique_hashed':len(cache),'stage_failures':[(r['name'],[k for k,v in r['checks'].items() if not v]) for r in rows if not r['passed']]}))
