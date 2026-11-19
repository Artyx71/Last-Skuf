#!/usr/bin/env python3
"""Demonstrate current AI routing capability in an isolated real Godot project."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def inventory():return {str(p.relative_to(ROOT)):digest(p) for p in sorted((ROOT/'game').rglob('*')) if p.is_file() and '.godot' not in p.parts}

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();out=args.output.resolve()
 if out.exists():raise SystemExit('Use a new diagnostic output directory')
 before=inventory();out.mkdir(parents=True);project=out/'isolated_project/game'
 shutil.copytree(ROOT/'game',project,ignore=shutil.ignore_patterns('.godot','__pycache__'))
 fixture=project/'tests/fixtures';fixture.mkdir(parents=True,exist_ok=True)
 source=ROOT/'tools/fixtures/p07_navigation_baseline.gd';driver=project/'tests/p07_navigation_baseline.gd';shutil.copy2(source,driver)
 base=json.loads((ROOT/'game/resources/combat/prototype.json').read_text())
 border=[[0,0,640,16],[0,344,640,16],[0,0,16,360],[624,0,16,360]]
 obstacle=[[256,96,16,160],[384,96,16,160],[256,240,144,16]]
 for layout in ['open','u_obstacle']:
  for kind in ['patrol','rusher','shooter']:
   config=json.loads(json.dumps(base));config.update(player_spawn=[-1024,-1024],exit=[-4096,-4096,16,16],walls=border+(obstacle if layout=='u_obstacle' else []),spawns=[{'kind':kind,'position':[320,208],'patrol_end':[320,288]}])
   write(fixture/f'p07_nav_{layout}_{kind}.json',config)
 lock=json.loads((ROOT/'tools/toolchain.lock.json').read_text());engine=ROOT/'.tools/godot'/f'Godot_v{lock["release"]}_linux.x86_64';assert digest(engine)==lock['linux_binary_sha256']
 env=dict(os.environ);env.update(XDG_DATA_HOME=str(out/'isolated_saves/data'),XDG_CONFIG_HOME=str(out/'isolated_saves/config'),XDG_CACHE_HOME=str(out/'isolated_saves/cache'),AYAY_P07_NAV_BASELINE_OUTPUT=str(out/'engine_result.json'),GODOT_SILENCE_ROOT_WARNING='1')
 runs=[]
 for name,flags in [('import',['--headless','--editor','--path',str(project),'--quit']),('diagnostic',['--headless','--fixed-fps','60','--path',str(project),'--script','res://tests/p07_navigation_baseline.gd'])]:
  argv=[str(engine),*flags];run=subprocess.run(argv,env=env,cwd=ROOT,capture_output=True,text=True,timeout=90);log=run.stdout+run.stderr;(out/(name+'.log')).write_text(log+'\nexit_code='+str(run.returncode)+'\n');runs.append({'name':name,'argv':argv,'exit_code':run.returncode})
  if run.returncode or any(s in log for s in ['SCRIPT ERROR:','Parse Error:','ERROR:']):raise SystemExit('Diagnostic prerequisite failed: '+name+'; inspect preserved log')
 data=json.loads((out/'engine_result.json').read_text());after=inventory();assert before==after
 valid=data['diagnostic_valid'] is True
 write(out/'source_before.json',before);write(out/'source_after.json',after)
 result={'schema':1,'scope':'READINESS_H02_EXISTING_AI_CAPABILITY_BASELINE_ONLY','diagnostic_completed':valid,'classification':'DEMONSTRATED_MULTIROOM_ROUTING_GAP' if valid and data['u_obstacle_unreached']==3 else 'INSPECT_DIAGNOSTIC','open_controls_reached':sum(r['goal_reached'] for r in data['rows'] if r['layout']=='open'),'U_route_unreached':data['u_obstacle_unreached'],'actual_engine_runs':runs,'source_unchanged':True,'engine_sha256':digest(engine),'driver_sha256':digest(source),'real_collision_AI_reused':True,'P06_PASS_reopened':False,'navigation_ready_for_P07':False,'FPS_hardware_latency_or_playthrough_claim':False}
 write(out/'validation.json',result);print(json.dumps(result),flush=True);return 0 if valid else 1
if __name__=='__main__':sys.exit(main())
