from pathlib import Path
import os,sys,json,hashlib,subprocess,time,re
R=Path(__file__).resolve().parents[4];W=R/'.autopilot/worktrees/P06';O=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();name=sys.argv[1];out=O/name;assert not out.exists();out.mkdir()
env={k:v for k,v in os.environ.items() if not k.startswith('AYAY_') and k not in ['DISPLAY','WAYLAND_DISPLAY']}
for k,folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state'),('XDG_RUNTIME_DIR','runtime')]:
 p=out/folder;p.mkdir(mode=0o700);env[k]=str(p)
for k,f in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json'),('AYAY_STORY_SAVE_PATH','story.json')]:env[k]=str(out/f)
env['AYAY_TIMKA_LAYOUT_OUTPUT']=str(out);env['AYAY_QA_RGBA_OUTPUT']=str(out)
binary=W/'.tools/godot/Godot_v4.7.2-stable_linux.x86_64';lock=json.loads((W/'tools/toolchain.lock.json').read_text());assert sha(binary)==lock['linux_binary_sha256'];cmd=[str(binary),'--headless','--path',str(O/'isolated-project/game')]
if name=='import':cmd+=['--editor','--quit']
else:cmd+=['--script','res://tests/'+{'frames':'character_frames_test.gd','structural':'timka_layout_test.gd','rgba':'qa_timka_import_rgba.gd'}[name]]
start=time.monotonic();result=subprocess.run(cmd,cwd=O,env=env,capture_output=True,text=True,timeout=45);text=result.stdout+result.stderr;(out/'run.log').write_text(text);record={'argv':cmd,'binary_sha256':sha(binary),'exit_code':result.returncode,'seconds':round(time.monotonic()-start,3),'log_sha256':sha(out/'run.log'),'fatal_log_tokens_absent':not re.search(r'SCRIPT ERROR:|ERROR:|FAIL[: ]|ObjectDB instances were leaked|resources still in use',text),'env_overrides':{k:v for k,v in env.items() if k.startswith('AYAY_') or k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR']},'WORK_project_opened':False};(out/'command.json').write_text(json.dumps(record,indent=2)+'\n');print(text[-4000:]);print(json.dumps(record));raise SystemExit(result.returncode or not record['fatal_log_tokens_absent'])
