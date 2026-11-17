from pathlib import Path
import os,json,subprocess,time,hashlib,re
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;GAME=OUT/'isolated/game';WORK=ROOT/'.autopilot/worktrees/P06';binary=(WORK/'.tools/godot/Godot_v4.7.2-stable_linux.x86_64').resolve();results=[]
for name in ['import','ai','audio','dialogue','options','story_registry','story_state','character_readiness']:
 p=OUT/'profiles'/name
 for folder in ['config','data','cache','runtime','tmp','saves','output']:(p/folder).mkdir(parents=True,exist_ok=True)
 (p/'runtime').chmod(0o700)
 env={k:v for k,v in os.environ.items() if not k.startswith(('AYAY_','GODOT_')) and k not in ['DISPLAY','WAYLAND_DISPLAY','PULSE_SERVER','PULSE_RUNTIME_PATH','DBUS_SESSION_BUS_ADDRESS']}
 env.update(XDG_CONFIG_HOME=str(p/'config'),XDG_DATA_HOME=str(p/'data'),XDG_CACHE_HOME=str(p/'cache'),XDG_RUNTIME_DIR=str(p/'runtime'),TMPDIR=str(p/'tmp'),AYAY_OPTIONS_PATH=str(p/'saves/options.json'),AYAY_DIALOGUE_SAVE_PATH=str(p/'saves/dialogue.json'),AYAY_CHAPTER_SAVE_PATH=str(p/'saves/chapter.json'),AYAY_STORY_SAVE_PATH=str(p/'saves/story.json'),AYAY_P06_DIALOGUE_SAVE_PATH=str(p/'saves/cast.json'))
 argv=[str(binary),'--headless','--audio-driver','Dummy','--fixed-fps','60','--path',str(GAME)]+(['--editor','--quit'] if name=='import' else ['--script','res://tests/'+name+'_test.gd'])
 start=time.monotonic();log=OUT/('independent-'+name+'.log')
 with log.open('w') as f:proc=subprocess.run(argv,cwd=OUT/'isolated',env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90)
 text=log.read_text();counts=re.findall(r'passed[=:](\d+)\s+failed[=:](\d+)',text);item={'name':name,'argv':argv,'exit_code':proc.returncode,'seconds':round(time.monotonic()-start,3),'log':log.name,'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'profile':str(p),'reported_counts':list(map(int,counts[-1])) if counts else None,'tail':text[-160:]};results.append(item);(OUT/'independent-commands.json').write_text(json.dumps(results,indent=2)+'\n');print(json.dumps(item),flush=True);assert proc.returncode==0,text[-2000:]
print('INDEPENDENT SUBSET COMPLETE',flush=True)
