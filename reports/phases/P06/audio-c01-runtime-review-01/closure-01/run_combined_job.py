#!/usr/bin/env python3
"""Parent canonical serial Controller ONLY: isolated startup then saved PCM/export audits."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
Q=Path(__file__).resolve().parent;OUT=Q/'combined-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 manifest=read(Q/'combined-job-manifest.json');assert sha(Path(__file__))==manifest['entrypoint_sha256']
 for row in manifest['required_files']:assert sha(Q/row['path'])==row['sha256'],row['path']
 for row in manifest['preserve_historical_inputs']:assert sha(Path(row['path']))==row['sha256'],row['path']
 base=read(Q/'source-freeze.json')
 for row in base['fixture_input_files']:assert sha(Q/'source-binding-fixture'/row['path'])==row['sha256'],row['path']
 assert not OUT.exists(),'Do not overwrite evidence or blindly replay completed partial jobs'
 OUT.mkdir();write(OUT/'start.json',{'scope':manifest['scope'],'entrypoint_sha256':sha(Path(__file__)),'manifest_sha256':sha(Q/'combined-job-manifest.json'),'actual_start':time.time(),'phase_approval':False})
 commands=[]
 for script,timeout in [('run_engine_job.py',600),('run_pcm_analysis.py',450),('analyze_handoff.py',90)]:
  argv=['/usr/bin/python3',str(Q/script)];started=time.monotonic()
  try:
   result=subprocess.run(argv,cwd=manifest['cwd'],capture_output=True,text=True,timeout=timeout);code=result.returncode;text=result.stdout+result.stderr
  except subprocess.TimeoutExpired as ex:code=124;text='TIMEOUT\n'+str(ex.stdout)+str(ex.stderr)
  log=OUT/(script+'.log');log.write_text(text+'\nexit_code='+str(code)+'\n')
  commands.append({'script':script,'argv':argv,'cwd':manifest['cwd'],'exit_code':code,'seconds':round(time.monotonic()-started,3),'log_sha256':sha(log)})
  write(OUT/'commands.json',commands);print(script,code,flush=True)
 components={}
 for name,path in [('startup',Q/'engine-01/result.json'),('actualPCM',Q/'pcm-analysis-01/result.json'),('export_owner_audit',Q/'handoff-analysis-01.json')]:
  result=read(path) if path.exists() else {};components[name]={'path':str(path),'sha256':sha(path) if path.exists() else None,'passed':result.get('passed') is True}
 source=read(Q/'source-negative-results.json')
 passed=all(x['exit_code']==0 for x in commands) and all(x['passed'] for x in components.values()) and source['case_count']==33 and source['all_expected_outcomes'] is True
 stable=all(sha(Q/row['path'])==row['sha256'] for row in manifest['required_files']);passed=passed and stable
 final={'scope':manifest['scope'],'passed':bool(passed),'commands':commands,'components':components,'prepared_code_unchanged':stable,'source_negative_cases':33,'actual_agent_listening':False,'owner_listening_status_separately_recorded':'Owner reported solo/runtime acceptance forP06prototype only; stressnotexplicit','full_C01_or_phase_approval':False,'merge_approval':False,'native_Windows':'NOT_TESTED','hardware_latency_and_FPS':'NOT_MEASURED'}
 write(OUT/'result.json',final);print(json.dumps({'passed':passed,'scope':manifest['scope'],'components':components}));return 0 if passed else 1
if __name__=='__main__':sys.exit(main())
