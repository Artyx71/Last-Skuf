#!/usr/bin/env python3
"""Prepared independent native NPC category supplement; parent Root serial Controller only."""
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess,sys,time
Q=Path(__file__).resolve().parent;OUT=Q/'supplement-01';SCRATCH=Q/'supplement-scratch-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def inventory(folder):return {p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}
def main():
 m=read(Q/'supplement-job-manifest.json');assert sha(Path(__file__))==m['entrypoint_sha256']
 for r in m['required_files']:assert sha(Q/r['path'])==r['sha256'],r['path']
 expected={r['path']:r['sha256'] for r in read(Q/'snapshot-inventory.json')['files']};assert inventory(Q/'snapshot-game')==expected
 binary=Path(m['Godot']['path']);assert sha(binary)==m['Godot']['sha256']
 assert not OUT.exists() and not SCRATCH.exists(),'New outputs only; preserve failed jobs'
 OUT.mkdir();SCRATCH.mkdir();game=SCRATCH/'game';shutil.copytree(Q/'snapshot-game',game);shutil.copyfile(Q/'probes/npc_category_baseline.gd',game/'tests/qa_npc_baseline_supplement.gd')
 before=inventory(game);profile=SCRATCH/'profiles';profile.mkdir();env=os.environ.copy();env.update(XDG_CONFIG_HOME=str(profile/'config'),XDG_DATA_HOME=str(profile/'data'),XDG_CACHE_HOME=str(profile/'cache'),AYAY_OPTIONS_PATH=str(profile/'options.json'),AYAY_STORY_SAVE_PATH=str(profile/'story.json'),AYAY_DIALOGUE_SAVE_PATH=str(profile/'dialogue.json'),AYAY_P06_DIALOGUE_SAVE_PATH=str(profile/'cast.json'),AYAY_CHAPTER_SAVE_PATH=str(profile/'chapter.json'),AYAY_NPC_BASELINE_OUTPUT=str(OUT))
 commands=[];error=re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL |FAIL:|instances were leaked|resources still in use')
 def run(label,argv,timeout):
  start=time.monotonic()
  try:r=subprocess.run(list(map(str,argv)),cwd=SCRATCH,env=env,capture_output=True,text=True,timeout=timeout);code=r.returncode;text=r.stdout+r.stderr
  except subprocess.TimeoutExpired as ex:code=124;text='TIMEOUT\n'+str(ex.stdout)+str(ex.stderr)
  log=OUT/(label+'.log');log.write_text(text+'\nexit_code='+str(code)+'\n');passed=code==0 and not error.search(text);commands.append({'name':label,'argv':list(map(str,argv)),'exit_code':code,'passed':bool(passed),'seconds':round(time.monotonic()-start,3),'log_sha256':sha(log)});write(OUT/'commands.json',commands);print(label,'PASS' if passed else 'FAIL',flush=True);return passed
 ok=run('fresh-import',[binary,'--headless','--path',game,'--editor','--import'],120)
 if ok:ok=run('native-seven-pair',[binary,'--path',game,'--disable-vsync','--max-fps','60','--script','res://tests/qa_npc_baseline_supplement.gd'],210)
 result=read(OUT/'result.json') if (OUT/'result.json').exists() else {};checks=[]
 def check(value,label):checks.append({'label':label,'passed':bool(value)})
 check(result.get('scope')=='P06_BASELINE_SHARED_NPC_CATEGORY_SUPPLEMENT_ONLY' and result.get('passed') is True and result.get('actual_input') is True and result.get('phase_approval') is False and result.get('deferred_C09_style_implemented') is False,'exact supplemental baseline/no deferred art claim')
 check(result.get('renderer') in ['X11','Wayland'],'actual native renderer, no headless acceptance')
 rows=result.get('checks',[]);check(len(rows)==204 and all(x.get('passed') is True for x in rows),'actual204 native assertions')
 pairs={('rusher','unarmed'),('rusher','sharp'),('rusher','firearm'),('shooter','unarmed'),('shooter','blunt'),('shooter','firearm'),('shooter','environmental')};cases=result.get('cases',[])
 check(len(cases)==14 and {(x.get('archetype'),x.get('category'),x.get('mode')) for x in cases}=={(a,b,mode) for a,b in pairs for mode in ['full','reduced']},'actual exactlyseven missingpairs×FullReduced')
 contacts=[x for x in result.get('contacts',[]) if x.get('finisher')];check(len(contacts)==14 and all(x.get('npc_frame')==1 and x.get('player_frame')==1 and x.get('npc_state')=='dead' for x in contacts),'actual14 paired contact1 receipts')
 captures=result.get('captures',[]);check(len(captures)==42 and len(list(OUT.glob('*.png')))==42 and all(x.get('code')==0 for x in captures),'actual42 native PNG phases0/1/2')
 check(len({x.get('path') for x in captures})==42 and all(Path(x['path']).is_file() for x in captures),'unique actual capturepaths')
 for row in cases:
  mode=row['mode'];category=row['category'];segment=row['segment'];signed=row.get('signature',[]);check(signed==[0,2,1,100,2,1 if category=='firearm' else 0,0,'dead'],'once damage/score/ammo/no incoming '+segment)
 after=inventory(game);stable=all(after.get(p)==h for p,h in before.items() if not p.endswith(('.uid','.import')));new=set(after)-set(before);check(stable and all(p.endswith(('.uid','.import')) for p in new),'isolated production source unchanged; only import metadata generated')
 check(inventory(Q/'snapshot-game')==expected,'original frozen snapshot unchanged')
 passed=bool(ok and all(c['passed'] for c in checks));summary={'scope':'INDEPENDENT_P06_BASELINE_NPC_SUPPLEMENT_ONLY','passed':passed,'checks':checks,'commands':commands,'new_art_or_Game_WORK_mutation':False,'phase_approval':False,'deferred_P08_style_approval':False,'FPS':'NOT_MEASURED; separate existing nativeP04G workload','hardware_latency':'NOT_MEASURED scriptedEngineInputonly','actual_agent_listening':False,'native_windows':'NOT_TESTED','source_game_inventory_sha256':sha(Q/'snapshot-inventory.json'),'test_probe_sha256':sha(Q/'probes/npc_category_baseline.gd')}
 summary['artifacts']=[{'path':p.relative_to(Q).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(OUT.rglob('*')) if p.is_file()]
 write(OUT/'validation.json',summary);print(json.dumps({'passed':passed,'checks':len(checks),'case_count':len(cases),'captures':len(captures)}));return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
