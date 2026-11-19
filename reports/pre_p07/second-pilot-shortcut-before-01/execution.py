from pathlib import Path
import os,json,shutil,subprocess,sys,hashlib
R=Path(__file__).resolve().parents[1];W=R/'.autopilot/worktrees/P07'
O=W/'reports/pre_p07/second-pilot-shortcut-before-01';assert not O.exists();O.mkdir()
P=O/'isolated_project/game';shutil.copytree(W/'reports/pre_p07/second-pilot-03/isolated_project/game',P,ignore=shutil.ignore_patterns('.godot','__pycache__'))
old=P/'scripts/ai/room_navigation.gd';assert hashlib.sha256(old.read_bytes()).hexdigest()=='2f418685068a641b024598c18bbee2ae9ff61fbcc03b779b3485e951d6de4c85'
driver=P/'tests/p07_second_pilot.gd';source=driver.read_text();assert source.count('await walking_routes()')==1
source=source.replace('await walking_routes()','# Only targeted old-router diagnostic, no walking claim.').replace('if tick%120==0:','if tick%120==0 or (tick>=180 and tick<216):');driver.write_text(source)
lock=json.loads((W/'tools/toolchain.lock.json').read_text());engine=W/'.tools/godot'/f'Godot_v{lock["release"]}_linux.x86_64'
assert hashlib.sha256(engine.read_bytes()).hexdigest()==lock['linux_binary_sha256']
env=dict(os.environ,XDG_DATA_HOME=str(O/'saves/data'),XDG_CONFIG_HOME=str(O/'saves/config'),XDG_CACHE_HOME=str(O/'saves/cache'),AYAY_P07_SECOND_RESULT=str(O/'result.json'),AYAY_P07_SECOND_CAPTURE=str(O/'captures'),GODOT_SILENCE_ROOT_WARNING='1')
for name,flags in [('import',['--headless','--editor','--quit']),('probe',['--headless','--fixed-fps','60','--script','res://tests/p07_second_pilot.gd'])]:
 argv=[str(engine),'--path',str(P),*flags];run=subprocess.run(argv,env=env,cwd=W,capture_output=True,text=True,timeout=180);log=run.stdout+run.stderr;(O/(name+'.log')).write_text(log)
 assert not any(x in log for x in ['SCRIPT ERROR:','Parse Error:'])
 assert run.returncode==(0 if name=='import' else 1)
d=json.loads((O/'result.json').read_text());rows=d['rows'];traces={x['kind']:x['result']['trace'] for x in rows if x.get('scope')=='targeted_cached_gate_moving_goal'}
assert any(x['reason']=='direct_sweep_clear' for x in traces['patrol'])
proof={'schema':1,'status':'PRE_FIX_ROUTER_OSCILLATION_REPRODUCED_NOT_PASS','old_router_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'consecutive_trace':traces,'candidate_source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip(),'candidate_router_sha256':hashlib.sha256((W/'game/scripts/ai/room_navigation.gd').read_bytes()).hexdigest(),'runtime_only_targeted_diagnostic_not_playthrough':True}
(O/'proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
shutil.copy2(__file__,O/'execution.py')
for script,name,native in [('p07_second_pilot.py','second-pilot-04',True),('p07_navigation_contract.py','navigation-contract-after-shortcut-01',False),('p07_room_pilot.py','room-pilot-after-shortcut-01',True)]:
 argv=[sys.executable,str(W/'tools'/script),'--output',str(W/'reports/pre_p07'/name)]
 if native:argv.append('--native')
 subprocess.run(argv,cwd=W,check=True)
