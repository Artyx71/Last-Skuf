#!/usr/bin/env python3
"""P06 bounded portrait/dialogue evidence; never accepts the complete character phase."""
import argparse,hashlib,json,os,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
GODOT=ROOT/'.tools/godot'/f'Godot_v{LOCK["release"]}_linux.x86_64'
ERRORS=re.compile(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sources():
 return {str(p.relative_to(ROOT)):sha(p) for folder in ['game','tools','assets/source_art/characters'] for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts}
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);parser.add_argument('--headless',action='store_true');parser.add_argument('--large-text',action='store_true');args=parser.parse_args()
 output=(ROOT/args.output).resolve()
 if output.exists() and any(output.iterdir()):parser.error('Evidence output must be new and empty; inspect old receipt before retry')
 output.mkdir(parents=True,exist_ok=True)
 local=ROOT/'.tools/p06-cast-qa'/hashlib.sha256(str(output).encode()).hexdigest()[:16];local.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env.update(AYAY_STORY_SAVE_PATH=str(local/'story.json'),AYAY_DIALOGUE_SAVE_PATH=str(local/'campaign-dialogue.json'),AYAY_P06_DIALOGUE_SAVE_PATH=str(local/'cast-dialogue.json'),AYAY_OPTIONS_PATH=str(local/'options.json'),AYAY_P06_CAST_OUTPUT=str(output),XDG_CONFIG_HOME=str(local/'config'),XDG_DATA_HOME=str(local/'data'))
 before=sources();write(output/'source_hashes.json',before)
 receipts=[]
 def run(label,cmd,timeout=100):
  started=time.monotonic()
  try:r=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=env,capture_output=True,text=True,timeout=timeout);code=r.returncode;text=r.stdout+r.stderr
  except subprocess.TimeoutExpired as ex:
   code=124;text='TIMEOUT\n'+str(ex.stdout)+str(ex.stderr)
  (output/(label+'.log')).write_text(text+'\nexit_code='+str(code)+'\n')
  entry={'name':label,'exit_code':code,'passed':code==0 and not ERRORS.search(text),'seconds':round(time.monotonic()-started,3),'argv':list(map(str,cmd))};receipts.append(entry);write(output/'commands.json',receipts);print(label,'OK' if entry['passed'] else 'FAIL',flush=True);return entry['passed']
 native=[GODOT,'--path',ROOT/'game','--disable-vsync','--max-fps','60']
 if args.headless:native+=['--headless']
 extra=['--','--open-cast','--p06-cast-replay']+(['--p06-cast-large-text'] if args.large_text else [])
 ok=run('cast-replay',native+extra)
 result=json.loads((output/'result.json').read_text()) if (output/'result.json').exists() else {}
 ok=bool(ok and result.get('passed') and result.get('actual_input') and ((result.get('renderer')=='headless')==args.headless))
 if ok:ok=run('process-reload',[GODOT,'--headless','--path',ROOT/'game','--script','res://tests/character_dialogue_reload.gd'])
 restored=json.loads((output/'process-reload.json').read_text()) if (output/'process-reload.json').exists() else {}
 ok=bool(ok and restored.get('passed') and before==sources())
 summary={'phase':'P06','scope':'PORTRAIT_DIALOGUE_SUBTASK_ONLY','passed':ok,'phase_approval':False,'renderer':result.get('renderer'),'actual_new_process_reload':restored.get('passed',False),'checks_passed':sum(x['passed'] for x in result.get('checks',[])),'checks_total':len(result.get('checks',[])),'captures':len(list(output.glob('*.png'))),'source_unchanged':before==sources(),'commands':receipts,'audio':'Existing accepted shared fictional bleep; no new media; agent listening not claimed','native_windows':'NOT_TESTED','source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()}
 summary['artifacts']=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(output.iterdir()) if p.is_file()]
 write(output/'validation.json',summary);print(json.dumps({k:summary[k] for k in ['passed','scope','checks_passed','checks_total','captures','source_unchanged']}));return 0 if ok else 1
if __name__=='__main__':sys.exit(main())
