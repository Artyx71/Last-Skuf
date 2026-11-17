#!/usr/bin/env python3
"""Real combat sandbox lifecycle plus fresh-process CH01 viewing restore only."""
import argparse,hashlib,json,os,subprocess,sys,time
from pathlib import Path
from verify_p06_cast import ROOT,GODOT,ERRORS,sha,write,sources

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
 output=(ROOT/args.output).resolve()
 if output.exists() and any(output.iterdir()):parser.error('Use fresh evidence; preserve prior receipt')
 output.mkdir(parents=True,exist_ok=True)
 local=ROOT/'.tools/p06-lab-isolation-qa'/hashlib.sha256(str(output).encode()).hexdigest()[:16];local.mkdir(parents=True,exist_ok=True)
 env=os.environ|{'AYAY_STORY_SAVE_PATH':str(local/'story.json'),'AYAY_DIALOGUE_SAVE_PATH':str(local/'dialogue.json'),'AYAY_OPTIONS_PATH':str(local/'options.json'),'AYAY_P06_COMBAT_ISOLATION_OUTPUT':str(output),'AYAY_P06_CAST_OUTPUT':str(output),'XDG_CONFIG_HOME':str(local/'config'),'XDG_DATA_HOME':str(local/'data')}
 before=sources();write(output/'source_hashes.json',before);commands=[]
 for name,script in [('sandbox','res://tests/character_lab_isolation_test.gd'),('process-reload','res://tests/character_dialogue_reload.gd')]:
  argv=[str(GODOT),'--headless','--fixed-fps','60','--path',str(ROOT/'game'),'--script',script];started=time.monotonic()
  try:
   result=subprocess.run(argv,cwd=ROOT,env=env,capture_output=True,text=True,timeout=60);code=result.returncode;text=result.stdout+result.stderr
  except subprocess.TimeoutExpired as error:code=124;text='TIMEOUT\n'+str(error.stdout)+str(error.stderr)
  (output/(name+'.log')).write_text(text+'\nexit_code='+str(code)+'\n')
  entry={'name':name,'argv':argv,'exit_code':code,'passed':code==0 and not ERRORS.search(text),'seconds':round(time.monotonic()-started,3)};commands.append(entry);write(output/'commands.json',commands);print(name,'OK' if entry['passed'] else 'FAIL',flush=True)
  if not entry['passed']:break
 result=json.loads((output/'result.json').read_text()) if (output/'result.json').is_file() else {}
 reload=json.loads((output/'process-reload.json').read_text()) if (output/'process-reload.json').is_file() else {}
 unchanged=before==sources();ok=unchanged and len(commands)==2 and all(c['passed'] for c in commands) and result.get('passed') and reload.get('passed') and reload.get('actual_new_process')
 report={'scope':'COMBAT_SANDBOX_CAMPAIGN_VIEW_ISOLATION_AND_FRESH_PROCESS_RESTORE_ONLY','phase_approval':False,'passed':bool(ok),'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_unchanged':unchanged,'checks_passed':sum(c['passed'] for c in result.get('checks',[])),'checks_total':len(result.get('checks',[])),'actual_new_process_reload':reload.get('passed',False),'commands':commands,'artifacts':[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(output.rglob('*')) if p.is_file()]}
 write(output/'validation.json',report);print(json.dumps({k:report[k] for k in ['passed','checks_passed','checks_total','source_unchanged','actual_new_process_reload']}));return 0 if ok else 1
if __name__=='__main__':sys.exit(main())
