#!/usr/bin/env python3
"""PREPARED ONLY: parent Root.stage executes serial isolated C01 startup probes.
Never invokes a Controller, Git, network, or actual WORK editor/project.
"""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
Q=Path(__file__).resolve().parent
OUT=Q/'engine-01';SCRATCH=Q/'engine-scratch-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def inventory(folder):return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}
def main():
 manifest=read(Q/'engine-job-manifest.json')
 assert sha(Path(__file__))==manifest['entrypoint_sha256']
 for item in manifest['required_files']:assert sha(Q/item['path'])==item['sha256'],item['path']
 binary=Path(manifest['Godot']['path']);assert sha(binary)==manifest['Godot']['sha256']
 expected={x['path']:x['sha256'] for x in read(Q/'engine-source-game-inventory.json')['files']}
 source=Q/'engine-source-game';assert inventory(source)==expected
 assert not OUT.exists() and not SCRATCH.exists(),'Fresh outputs only; preserve prior attempt'
 OUT.mkdir();SCRATCH.mkdir();write(OUT/'start.json',{'scope':'C01_INDEPENDENT_ISOLATED_STARTUP_ONLY','author_source':manifest['author_source'],'entrypoint_sha256':sha(Path(__file__)),'phase_approval':False,'listening':False,'mixer_PCM':False})
 commands=[];observations=[];all_ok=True
 errors=re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL |instances were leaked|resources still in use')
 def run(label,argv,cwd,env,timeout):
  started=time.monotonic()
  try:
   result=subprocess.run(list(map(str,argv)),cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
   code=result.returncode;content=result.stdout+result.stderr
  except subprocess.TimeoutExpired as ex:
   code=124;content='TIMEOUT\n'+str(ex.stdout)+str(ex.stderr)
  log=OUT/(label+'.log');log.write_text(content+'\nexit_code='+str(code)+'\n')
  clean=not errors.search(content)
  row={'label':label,'argv':list(map(str,argv)),'cwd':str(cwd),'exit_code':code,'clean_error_gate':clean,'seconds':round(time.monotonic()-started,3),'log_sha256':sha(log),'passed':code==0 and clean}
  commands.append(row);write(OUT/'commands.json',commands);print(label,'PASS' if row['passed'] else 'FAIL',flush=True)
  return row['passed']
 for mode in ['valid','base_collision','polish_collision']:
  case=SCRATCH/mode;game=case/'game';shutil.copytree(source,game)
  for name in ['qa_c01_registry.gd','qa_c01_startup.gd']:shutil.copyfile(Q/'probes'/name,game/'tests'/name)
  if mode!='valid':
   filename='manifest.json' if mode=='base_collision' else 'combat_polish.json'
   path=game/'assets/audio'/filename;data=read(path)
   data['sfx']['finish_gabar_unarmed']={'path':'res://assets/audio/combat_polish/finish_unarmed.wav','bus':'SFX','gain_db':0.0}
   write(path,data)
  before=inventory(game);profile=case/'profile';profile.mkdir()
  env=os.environ.copy();env.update(XDG_CONFIG_HOME=str(profile/'config'),XDG_DATA_HOME=str(profile/'data'),XDG_CACHE_HOME=str(profile/'cache'),AYAY_STORY_SAVE_PATH=str(profile/'story.json'),AYAY_DIALOGUE_SAVE_PATH=str(profile/'dialogue.json'),AYAY_P06_DIALOGUE_SAVE_PATH=str(profile/'cast.json'),AYAY_OPTIONS_PATH=str(profile/'options.json'),AYAY_C01_QA_MODE='valid' if mode=='valid' else 'reject')
  okay=run(mode+'-fresh-import',[binary,'--headless','--path',game,'--editor','--import'],case,env,100)
  if mode=='valid' and okay:
   registry_output=OUT/'registry.json';env['AYAY_C01_QA_OUTPUT']=str(registry_output)
   okay=run('registry-negatives',[binary,'--headless','--path',game,'--script','res://tests/qa_c01_registry.gd'],case,env,45) and okay
   data=read(registry_output) if registry_output.exists() else {}
   registry_ok=len(data.get('checks',[]))==23 and all(x.get('passed') is True for x in data.get('checks',[]))
   observations.append({'label':'registry23actualchecks','passed':registry_ok});okay=okay and registry_ok
  if okay:
   output=OUT/(mode+'-startup.json');env['AYAY_C01_QA_OUTPUT']=str(output)
   okay=run(mode+'-startup',[binary,'--headless','--path',game,'--script','res://tests/qa_c01_startup.gd'],case,env,45) and okay
   data=read(output) if output.exists() else {}
   startup_ok=data.get('passed') is True and len(data.get('checks',[]))==(5 if mode=='valid' else 3) and all(x.get('passed') is True for x in data.get('checks',[]))
   observations.append({'label':mode+'startup_actual_assertions','passed':startup_ok});okay=okay and startup_ok
  after=inventory(game)
  stable=all(after.get(p)==h for p,h in before.items() if not p.endswith(('.import','.uid')))
  newfiles={p for p in after if p not in before};metadata_only=all(p.endswith(('.import','.uid')) for p in newfiles)
  observations.append({'label':mode+'-isolated-source-stable','passed':stable and metadata_only,'sidecar_changes':[p for p in after if after.get(p)!=before.get(p) and p.endswith(('.import','.uid'))],'unexpected_new_files':sorted(p for p in newfiles if not p.endswith(('.import','.uid')))})
  all_ok=all_ok and okay and stable and metadata_only
 source_stable=inventory(source)==expected;all_ok=all_ok and source_stable and all(x['passed'] for x in observations)
 result={'scope':'INDEPENDENT_C01_ISOLATED_REGISTRY_STARTUP_ONLY','author_source':manifest['author_source'],'passed':bool(all_ok),'commands':commands,'observations':observations,'frozen_game_source_unchanged':source_stable,'WORK_mutations':False,'actual_native_renderer':False,'actual_mixer_PCM':False,'actual_listening':False,'phase_approval':False,'merge_approval':False}
 write(OUT/'result.json',result);print(json.dumps({'passed':all_ok,'commands':len(commands),'scope':result['scope']}));return 0 if all_ok else 1
if __name__=='__main__':sys.exit(main())
