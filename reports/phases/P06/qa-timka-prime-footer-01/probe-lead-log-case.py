from pathlib import Path
import ast,json,hashlib,re,shutil,tempfile
O=Path(__file__).resolve().parent;W=O.parents[3]/'.autopilot/worktrees/P06';real=W/'reports/phases/P06/timka-prime-01/native-03';helper=O/'source-snapshot/tools/verify_p06_timka_prime.py';node=next(n for n in ast.parse(helper.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='completed_live_evidence');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();original=json.loads((real/'validation.json').read_text());sources=json.loads((real/'source_hashes.json').read_text());godot=Path(original['commands'][0]['argv'][0]);records=[]
with tempfile.TemporaryDirectory(prefix='log-consistency-only-',dir=O) as tmp:
 root=Path(tmp);folder=root/'reports/native';folder.mkdir(parents=True)
 for e in original['artifacts']:
  source=W/e['path'];relative=source.relative_to(real);dest=folder/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
 report=json.loads((real/'validation.json').read_text());commands=json.loads((folder/'commands.json').read_text());commands[0]['argv'][2]=str(root/'game');report['commands']=commands;(folder/'commands.json').write_text(json.dumps(commands))
 result=json.loads((folder/'live/result.json').read_text())
 for e in result['captures']:e['path']=str(folder/Path(e['path']).relative_to(real))
 (folder/'live/result.json').write_text(json.dumps(result))
 for e in report['artifacts']:
  relative=(W/e['path']).relative_to(real);p=folder/relative;e['path']=str(p.relative_to(root));e['sha256']=sha(p)
 (folder/'validation.json').write_text(json.dumps(report));scope={'Path':Path,'json':json,'ROOT':root,'GODOT':godot,'ERRORS':re.compile(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use'),'sha':sha};exec(compile(ast.Module(body=[node],type_ignores=[]),str(helper),'exec'),scope)
 for name,changed in [('rebased_actual_native03_positive_control',False),('rebound_live_log_last_exit17_but_both_commands_exit0',True)]:
  if changed:
   log=folder/'live.log';text=log.read_text();assert text.rstrip().endswith('exit_code=0');log.write_text(text.rstrip()[:-len('exit_code=0')]+'exit_code=17\n')
   next(e for e in report['artifacts'] if e['path'].endswith('/live.log'))['sha256']=sha(log);(folder/'validation.json').write_text(json.dumps(report))
  try:value=scope['completed_live_evidence'](folder,sources);accepted=True;error=None
  except Exception as e:value=None;accepted=False;error=type(e).__name__+': '+str(e)
  records.append({'case':name,'accepted':accepted,'error':error,'value':value,'validation_command_exit':report['commands'][0]['exit_code'],'bound_command_exit':commands[0]['exit_code'],'log_last_nonempty_line':(folder/'live.log').read_text().strip().splitlines()[-1]})
(O/'log-exit-consistency-results.json').write_text(json.dumps({'schema':1,'scope':'READ_ONLY_FROZEN_HELPER_ON_ROOT_REBASED_ACTUAL_CACHE_ONLY','helper_sha256':sha(helper),'cases':records,'actual_WORK_or_native_evidence_mutated':False,'engine_Git_controller_network_calls':0},indent=2)+'\n');print(json.dumps(records,indent=2))
