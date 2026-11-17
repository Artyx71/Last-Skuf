"""Pure frozen function on actual historical input and ROOT-only real-data copies."""
from pathlib import Path
import ast,json,hashlib,re,shutil,tempfile
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';real=W/'reports/phases/P06/timka-prime-01/native-03';helper=Q/'source-snapshot/tools/verify_p06_timka_prime.py';node=next(n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='completed_live_evidence');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original=json.loads((real/'validation.json').read_text());recorded=json.loads((real/'source_hashes.json').read_text());current=json.loads((Q/'source-map-current.json').read_text());godot=Path(original['commands'][0]['argv'][0]);scope={'Path':Path,'json':json,'ROOT':W,'GODOT':godot,'ERRORS':re.compile(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use'),'sha':sha};exec(compile(ast.Module(body=[node],type_ignores=[]),str(helper),'exec'),scope);records=[]
for name,sources,expected in [('actual_untouched_native03_recorded589_positive',recorded,True),('current_c193_source_map_rejects_historical_native03',current,False)]:
 try:value=scope['completed_live_evidence'](real,sources);accepted=True;error=None
 except Exception as e:value=None;accepted=False;error=type(e).__name__+': '+str(e)
 assert accepted==expected;records.append({'case':name,'accepted':accepted,'error':error,'actual_native03_readonly':True})
for name,footer,expected in [('exact0_control','exit_code=0',True),('nonzero17','exit_code=17',False),('missing',None,False),('prefix','prefix exit_code=0',False),('zero00','exit_code=00',False),('leading_space',' exit_code=0',False),('trailing_comment','exit_code=0 then failed',False),('zero_followed_blank_lines','exit_code=0\n\n   \n',True)]:
 with tempfile.TemporaryDirectory(dir=Q/'temporary-fixtures') as tmp:
  root=Path(tmp);folder=root/'reports/native';folder.mkdir(parents=True)
  for e in original['artifacts']:
   s=W/e['path'];d=folder/s.relative_to(real);d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s,d)
  report=json.loads((real/'validation.json').read_text());commands=json.loads((folder/'commands.json').read_text());commands[0]['argv'][2]=str(root/'game');report['commands']=commands;(folder/'commands.json').write_text(json.dumps(commands));result=json.loads((folder/'live/result.json').read_text())
  for e in result['captures']:e['path']=str(folder/Path(e['path']).relative_to(real))
  (folder/'live/result.json').write_text(json.dumps(result));log=folder/'live.log';text=log.read_text();assert text.rstrip().endswith('exit_code=0');prefix=text.rstrip()[:-len('exit_code=0')];log.write_text(prefix+('' if footer is None else footer+'\n'))
  for e in report['artifacts']:
   p=folder/(W/e['path']).relative_to(real);e['path']=str(p.relative_to(root));e['sha256']=sha(p)
  (folder/'validation.json').write_text(json.dumps(report));scope['ROOT']=root
  try:value=scope['completed_live_evidence'](folder,recorded);accepted=True;error=None
  except Exception as e:value=None;accepted=False;error=type(e).__name__+': '+str(e)
  assert accepted==expected,(name,accepted,error)
  records.append({'case':name,'accepted':accepted,'error':error,'validation_receipt_exit':report['commands'][0]['exit_code'],'bound_receipt_exit':commands[0]['exit_code'],'log_footer':footer,'path_rebased_actual_cache_copy_only':True})
(Q/'footer-matrix-results.json').write_text(json.dumps({'scope':'PURE_FOOTER_CLOSURE_ON_ACTUAL_RECORDING_AND_ROOT_REBASED_CORRUPTION_FIXTURES','helper_sha256':sha(helper),'native03_validation_sha256':sha(real/'validation.json'),'native03_source_commit':'589907497d184d27a0f5183e8f0291dd7dd36b3e','current_code_commit':'c193119deac0e5d65655e0cd97ced7fdf596eb6c','current_source_map_sha256':sha(Q/'source-map-current.json'),'cases':records,'actual_WORK_artifact_mutation':False,'engine_controller_network_invocations':0},indent=2)+'\n');print('PASS10/10 actual/historical/stale/footer matrix controls; no engine')
