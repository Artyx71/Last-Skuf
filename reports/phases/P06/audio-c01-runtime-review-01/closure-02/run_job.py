#!/usr/bin/env python3
"""Prepared PURE offline saved-PCM/export closure; parent serial stage ONLY, no Godot."""
from pathlib import Path
import hashlib,json,subprocess,time,sys
Q=Path(__file__).resolve().parent;OUT=Q/'job-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 m=read(Q/'job-manifest.json');assert sha(Path(__file__))==m['entrypoint_sha256']
 for r in m['required_files']:assert sha(Q/r['path'])==r['sha256'],r['path']
 for r in m['preserved_historical']:assert sha(Path(r['path']))==r['sha256'],r['path']
 assert not OUT.exists(),'Fresh outputs; do not replay completed job or overwrite results';OUT.mkdir();commands=[]
 write(OUT/'start.json',{'scope':m['scope'],'entrypoint_sha256':sha(Path(__file__)),'manifest_sha256':sha(Q/'job-manifest.json'),'time':time.time()})
 for script,timeout in [('run_fresh_pcm.py',420),('audit_fresh_exports.py',60)]:
  argv=['/usr/bin/python3',str(Q/script)];started=time.monotonic()
  try:r=subprocess.run(argv,cwd=m['cwd'],capture_output=True,text=True,timeout=timeout);code=r.returncode;text=r.stdout+r.stderr
  except subprocess.TimeoutExpired as ex:code=124;text='TIMEOUT\n'+str(ex.stdout)+str(ex.stderr)
  log=OUT/(script+'.log');log.write_text(text+'\nexit_code='+str(code)+'\n');commands.append({'script':script,'argv':argv,'exit_code':code,'seconds':round(time.monotonic()-started,3),'log_sha256':sha(log)});write(OUT/'commands.json',commands);print(script,code,flush=True)
 components={}
 for n,p in [('freshPCM',Q/'analysis-01/result.json'),('DEV08',Q/'export-audit-01.json')]:
  j=read(p) if p.exists() else {};components[n]={'path':str(p),'sha256':sha(p) if p.exists() else None,'passed':j.get('passed') is True}
 stable=all(sha(Q/r['path'])==r['sha256'] for r in m['required_files']);passed=stable and all(x['exit_code']==0 for x in commands) and all(x['passed'] for x in components.values());write(OUT/'result.json',{'scope':m['scope'],'passed':passed,'components':components,'commands':commands,'frozen_inputs_unchanged':stable,'actual_Godot_run':False,'actual_agent_listening':False,'full_phase_approval':False,'merge_approval':False});print(json.dumps({'passed':passed,'components':components}));return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
