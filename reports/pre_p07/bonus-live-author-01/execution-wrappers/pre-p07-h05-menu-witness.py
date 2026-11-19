import json,os,shutil,subprocess,sys,hashlib
from pathlib import Path
r=Path.cwd();w=r/'.autopilot/worktrees/P07';mode=sys.argv[1];assert mode in ['before','after'];out=w/('reports/pre_p07/bonus-menu-witness-'+mode+'-01');assert not out.exists();out.mkdir(parents=True)
project=out/'isolated_project/game';shutil.copytree(w/'reports/pre_p07/bonus-live-adapter-01/isolated_project/game',project)
inputs={}
if mode=='after':
 for rel in ['game/scripts/story/story_service.gd','game/scripts/core/bootstrap.gd']:
  src=w/rel;dst=project/Path(rel).relative_to('game');shutil.copyfile(src,dst);inputs[rel]=hashlib.sha256(src.read_bytes()).hexdigest()
probe=r/'reports/pre_p07/lead-bonus-live-01/replay_menu_probe.gd';assert hashlib.sha256(probe.read_bytes()).hexdigest()=='504bae58b634bd3cbcbfd9bce97564597422aaccc7861537de3fa981276f11a3';shutil.copyfile(probe,project/'tests/replay_menu_probe.gd');shutil.copyfile(probe,out/'replay_menu_probe.gd')
isolate=out/'isolated_saves';isolate.mkdir();env=dict(os.environ,XDG_DATA_HOME=str(isolate/'data'),XDG_CONFIG_HOME=str(isolate/'config'),XDG_CACHE_HOME=str(isolate/'cache'),AYAY_STORY_SAVE_PATH=str(isolate/'story.json'),AYAY_BP_PROFILE=str(isolate/'profiles'),AYAY_BP_RESULT=str(out/'witness.json'),GODOT_SILENCE_ROOT_WARNING='1')
lock=json.loads((w/'tools/toolchain.lock.json').read_text());engine=w/'.tools/godot'/f'Godot_v{lock["release"]}_linux.x86_64';argv=[str(engine),'--path',str(project),'--headless','--script','res://tests/replay_menu_probe.gd'];p=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=90);(out/'witness.log').write_text(p.stdout+p.stderr);(out/'execution.json').write_text(json.dumps({'mode':mode,'argv':argv,'exit_code':p.returncode,'runtime_overlay':inputs,'meaning':'TARGETED_LEAD_PROBE_NOT_FULL_ADAPTER_ACCEPTANCE'},indent=2)+'\n');print(p.stdout+p.stderr,flush=True);raise SystemExit(p.returncode)
