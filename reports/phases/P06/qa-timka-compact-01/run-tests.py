from pathlib import Path
import os,subprocess,time,json,hashlib,re,sys
R=Path(__file__).resolve().parents[4];W=R/'.autopilot/worktrees/P06';O=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();name=sys.argv[1];dest=O/name;assert not dest.exists();dest.mkdir()
env={k:v for k,v in os.environ.items() if not k.startswith('AYAY_') and k not in ['DISPLAY','WAYLAND_DISPLAY']};env['PYTHONDONTWRITEBYTECODE']='1';env['TMPDIR']=str(O/'tmp')
for key,folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state'),('XDG_RUNTIME_DIR','runtime')]:
 p=dest/folder;p.mkdir(mode=0o700);env[key]=str(p)
for key,f in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json'),('AYAY_STORY_SAVE_PATH','story.json')]:env[key]=str(dest/f)
env['AYAY_TIMKA_LAYOUT_OUTPUT']=str(dest)
if name=='structural':cmd=[str(W/'.tools/godot/Godot_v4.7.2-stable_linux.x86_64'),'--headless','--path',str(O/'isolated-project/game'),'--script','res://tests/timka_layout_test.gd']
elif name=='adopter':cmd=[str(W/'.tools/art-venv/bin/python'),'-m','unittest','discover','-s',str(W/'assets/source_art/characters'),'-p','test_timka_supported.py','-v']
else:raise ValueError(name)
start=time.monotonic();p=subprocess.run(cmd,cwd=O,env=env,capture_output=True,text=True,timeout=45);text=p.stdout+p.stderr;(dest/'run.log').write_text(text);record={'argv':cmd,'exit_code':p.returncode,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(dest/'run.log'),'env_overrides':{k:v for k,v in env.items() if k.startswith('AYAY_') or k in ['TMPDIR','PYTHONDONTWRITEBYTECODE','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR']},'fatal_log_tokens_absent':not re.search(r'SCRIPT ERROR:|ERROR:|FAIL[: ]|ObjectDB instances were leaked|resources still in use',text),'production_runtime_opened_or_migrated':False};(dest/'command.json').write_text(json.dumps(record,indent=2)+'\n');print(text);print(json.dumps(record));raise SystemExit(p.returncode or not record['fatal_log_tokens_absent'])
