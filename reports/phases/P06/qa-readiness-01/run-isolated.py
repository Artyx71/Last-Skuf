from pathlib import Path
import os,subprocess,json,time,hashlib,re
R=Path(__file__).resolve().parents[4];O=Path(__file__).parent;W=R/'.autopilot/worktrees/P06';P=O/'isolated-project/game';binary=W/'.tools/godot/Godot_v4.7.2-stable_linux.x86_64'
lock=json.loads((W/'tools/toolchain.lock.json').read_text());assert hashlib.sha256(binary.read_bytes()).hexdigest()==lock['linux_binary_sha256']
name=os.sys.argv[1];script=os.sys.argv[2];out=O/name;assert not out.exists();out.mkdir()
env={k:v for k,v in os.environ.items() if not k.startswith('AYAY_') and k not in ['DISPLAY','WAYLAND_DISPLAY']}
for k,folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state')]:
 path=out/folder;path.mkdir();env[k]=str(path)
for k,f in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json'),('AYAY_STORY_SAVE_PATH','story.json')]:env[k]=str(out/f)
env['AYAY_P06_READINESS_OUTPUT']=str(out);env['AYAY_QA_READINESS_OUTPUT']=str(out)
cmd=[str(binary),'--headless','--fixed-fps','60','--path',str(P),'--script','res://tests/'+script]
start=time.monotonic();result=subprocess.run(cmd,cwd=O,env=env,capture_output=True,text=True,timeout=45);text=result.stdout+result.stderr;(out/'run.log').write_text(text)
record={'argv':cmd,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'env_overrides':{k:v for k,v in env.items() if k.startswith('AYAY_') or k.startswith('XDG_')},'display_variables_removed':True,'exit_code':result.returncode,'duration_seconds':round(time.monotonic()-start,3),'log_sha256':hashlib.sha256((out/'run.log').read_bytes()).hexdigest(),'fatal_log_tokens_absent':not re.search(r'SCRIPT ERROR:|ERROR:|FAIL[: ]|ObjectDB instances were leaked|resources still in use',text),'scope':'isolated QA headless readiness; no production WORK cache/save writes'}
(out/'command.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));print(text);raise SystemExit(result.returncode or (not record['fatal_log_tokens_absent']))
