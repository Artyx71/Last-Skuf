from pathlib import Path
import os,json,hashlib,subprocess,time,re
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=Path(__file__).parent;BASE=OUT/'isolated';BINARY=(WORK/'.tools/godot/Godot_v4.7.2-stable_linux.x86_64').resolve();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a={str(p.relative_to(BASE/'after')):sha(p) for p in sorted((BASE/'after/game').rglob('*')) if p.is_file()};b={str(p.relative_to(BASE/'before')):sha(p) for p in sorted((BASE/'before/game').rglob('*')) if p.is_file()};assert set(a)==set(b);assert {p for p in a if a[p]!=b[p]}=={'game/scripts/core/combat_lab.gd','game/scripts/systems/combat_system.gd'}
commands=[]
def run(mode,name,args,expected_exit=0):
 profile=OUT/'profiles'/mode/name
 for folder in ['config','data','cache','tmp','runtime','saves','output']:(profile/folder).mkdir(parents=True,exist_ok=True)
 (profile/'runtime').chmod(0o700)
 env={k:v for k,v in os.environ.items() if not k.startswith(('AYAY_','GODOT_')) and k not in ['DISPLAY','WAYLAND_DISPLAY','PULSE_SERVER','PULSE_RUNTIME_PATH','DBUS_SESSION_BUS_ADDRESS']}
 env.update(XDG_CONFIG_HOME=str(profile/'config'),XDG_DATA_HOME=str(profile/'data'),XDG_CACHE_HOME=str(profile/'cache'),XDG_RUNTIME_DIR=str(profile/'runtime'),TMPDIR=str(profile/'tmp'),AYAY_OPTIONS_PATH=str(profile/'saves/options.json'),AYAY_DIALOGUE_SAVE_PATH=str(profile/'saves/dialogue.json'),AYAY_CHAPTER_SAVE_PATH=str(profile/'saves/chapter.json'),AYAY_STORY_SAVE_PATH=str(profile/'saves/story.json'),AYAY_YAKUZA_FINISHER_TEST_OUTPUT=str(profile/'output'))
 argv=[str(BINARY),'--headless','--audio-driver','Dummy','--fixed-fps','60','--path',str(BASE/mode/'game')]+args
 log=OUT/(mode+'-'+name+'.log');start=time.monotonic()
 with log.open('w') as f:r=subprocess.run(argv,cwd=BASE/mode,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=90)
 text=log.read_text();counts=re.findall(r'passed[=:](\d+)\s+failed[=:](\d+)',text)
 item={'name':name,'mode':mode,'argv':argv,'cwd':str(BASE/mode),'exit_code':r.returncode,'expected_exit':expected_exit,'seconds':round(time.monotonic()-start,3),'log':log.name,'log_sha256':sha(log),'isolated_profile':str(profile),'save_paths':{k:env[k] for k in ['AYAY_OPTIONS_PATH','AYAY_DIALOGUE_SAVE_PATH','AYAY_CHAPTER_SAVE_PATH','AYAY_STORY_SAVE_PATH']},'last_reported_counts':list(map(int,counts[-1])) if counts else None}
 commands.append(item);(OUT/'reviewer-commands.json').write_text(json.dumps(commands,indent=2)+'\n');print(json.dumps(item),flush=True)
 assert r.returncode==expected_exit, text[-3000:]
 return item
for mode in ['before','after']:run(mode,'import',['--editor','--quit'])
run('before','yakuza_finisher_authority',['--script','res://tests/yakuza_finisher_authority_test.gd'],expected_exit=1)
run('after','yakuza_finisher_authority',['--script','res://tests/yakuza_finisher_authority_test.gd'])
for name in ['p04g','character_policy_integration','mission']:run('after',name,['--script','res://tests/'+name+'_test.gd'])
print('ISOLATED REVIEW EXECUTION COMPLETE',flush=True)
