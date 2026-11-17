#!/usr/bin/env python3
"""Independent QA job. Execute only via parent's exclusive canonical stage, never parallel engines."""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0')
W=R/'.autopilot/worktrees/P06';Q=R/'reports/phases/P06/qa-tega-environment-02';S=Q/'isolated-project'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def inspect_inputs(root,expected):
 return {rel:sha(root/rel) if (root/rel).is_file() else 'MISSING' for rel in expected}
def main():
 marker=Q/'engine-job06-start.json'
 if marker.exists():raise SystemExit('Consumed or interrupted QA job: inspect existing evidence; never replay automatically')
 expected=json.loads((Q/'copy-inputs.json').read_text());engine=json.loads((Q/'engine-copy.json').read_text());binary=Q/engine['path']
 assert sha(binary)==engine['sha256']
 assert inspect_inputs(W,expected)==expected,'WORK source changed before QA'
 assert inspect_inputs(S,expected)==expected,'isolated copy changed before QA'
 probes={'qa_tega_callback_geometry.gd': 'd3d0c304ff5ed558768b0382c0883548c6024e89bcb12a429076095618468885', 'qa_tega_callback_extended.gd': '4bd22729a1c8de503e2459eb48fae6dcd6d8ac7cb5968b90f239bca4a17cc064', 'qa_tega_negative_final.gd': '7c71947d47a74cb755cbd95cb9a358670257af4e5d00575bfbb63c70c0be6b41', 'qa_tega_actor_wall.gd': '121234fca28942d1b4c514a06c550979961dd2842e1b25d310f6f37241cffa27'}
 for name,digest in probes.items():
  assert sha(Q/name)==digest and sha(S/'game/tests'/name)==digest, 'QA probe input changed: '+name
 write(Q/'probe-freeze.json',probes)
 write(marker,{'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'pid':os.getpid(),'frozen_head':'c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd','scope':'INDEPENDENT_ISOLATED_TEGA_TECHNICAL_QA_ONLY','source_count':len(expected),'entrypoint_sha256':sha(Path(__file__)),'sequential':True,'WORK_engine_used':False,'phase_approval':False})
 cases=[('import',None),('geometry-closure','qa_tega_callback_geometry.gd'),('callback-extended','qa_tega_callback_extended.gd'),('tega-negative','qa_tega_negative_final.gd'),('actor-wall','qa_tega_actor_wall.gd'),('tega','tega_environment_replay.gd'),('counter-fixed','olezhka_feedback_replay.gd'),('source-owner-smoke','BOOTSTRAP_SMOKE')]
 results=[]
 for name,script in cases:
  out=Q/name
  assert not out.exists(),'fresh result dir required: '+str(out)
  out.mkdir()
  env={k:v for k,v in os.environ.items() if not k.startswith('AYAY_') and k not in ['DISPLAY','WAYLAND_DISPLAY']}
  for key,folder in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache'),('XDG_STATE_HOME','state'),('XDG_RUNTIME_DIR','runtime')]:
   p=out/folder;p.mkdir(mode=0o700);env[key]=str(p)
  for key,f in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json'),('AYAY_STORY_SAVE_PATH','story.json')]:env[key]=str(out/f)
  for key in ['AYAY_P06_TEGA_OUTPUT','AYAY_P06_RYZHIK_LAYOUT_OUTPUT','AYAY_P06_RYZHIK_OUTPUT','AYAY_P06_TIMKA_PRIME_OUTPUT','AYAY_P06_COUNTER_OUTPUT','AYAY_P06_TIMKA_PRESENT_OUTPUT','AYAY_P06_GABAR_OUTPUT','AYAY_P06_OLEZHKA_OUTPUT','AYAY_P06_READINESS_OUTPUT','AYAY_TIMKA_LAYOUT_OUTPUT','AYAY_YAKUZA_FINISHER_TEST_OUTPUT']:env[key]=str(out)
  env['AYAY_OWNER_PREVIEW_SMOKE_OUTPUT']=str(out);env['AYAY_TIMING_RESULT']=str(out/'result.json');env['AYAY_P04G_TEST_RESULT']=str(out/'result.json')
  argv=[str(binary),'--headless','--path',str(S/'game')]
  if script is None:argv+=['--editor','--quit']
  elif script=='BOOTSTRAP_SMOKE':argv+=['--fixed-fps','60','--','--p06-owner-preview-smoke']
  else:argv+=['--fixed-fps','60','--script','res://tests/'+script]
  started=time.monotonic()
  try:
   run=subprocess.run(argv,cwd=Q,env=env,capture_output=True,text=True,timeout=180 if script is None else 120)
   code=run.returncode;log=run.stdout+run.stderr
  except subprocess.TimeoutExpired as ex:
   code=124;log='TIMEOUT\n'+str(ex.stdout)+'\n'+str(ex.stderr)
  (out/'run.log').write_text(log+'\nexit_code='+str(code)+'\n')
  clean=not re.search(r'SCRIPT ERROR:|ERROR:|FAIL[: ]|instances were leaked|resources still in use',log)
  match=re.findall(r'RESULT[^\n]*\bpassed=(\d+)\s+failed=(\d+)',log)
  if name=='counter-fixed':
   counter=re.findall(r'P06_COUNTER_FEEDBACK (\d+)/(\d+) passed',log)
   if counter:match=[(counter[-1][0],str(int(counter[-1][1])-int(counter[-1][0])))]
  passed=code==0 and clean and (script is None or bool(match and int(match[-1][0])>0 and int(match[-1][1])==0))
  details=None
  if (out/'result.json').exists():
   data=json.loads((out/'result.json').read_text());checks=data.get('checks')
   if checks is not None:
    details={'checks_total':len(checks),'checks_passed':sum(c.get('passed') is True for c in checks)}
    passed=passed and bool(checks) and all(c.get('passed') is True for c in checks)
   passed=passed and data.get('passed') is True
  record={'name':name,'argv':argv,'exit_code':code,'passed':passed,'seconds':round(time.monotonic()-started,3),'fatal_log_tokens_absent':clean,'result_counts':match[-1] if match else None,'json_counts':details,'log_sha256':sha(out/'run.log'),'env_overrides':{k:v for k,v in env.items() if k.startswith('AYAY_') or k.startswith('XDG_')},'WORK_project_or_binary_executed':False}
  write(out/'command.json',record);results.append(record);write(Q/'engine-job06-commands.json',results)
  print(json.dumps({k:record[k] for k in ['name','exit_code','passed','seconds','result_counts']}),flush=True)
  if script is None and not passed:break
 after=inspect_inputs(S,expected);live=inspect_inputs(W,expected)
 integrity={'copy_inputs_unchanged':after==expected,'WORK_inputs_unchanged':live==expected,'copy_differences':{k:{'expected':expected[k],'actual':v} for k,v in after.items() if expected[k]!=v},'WORK_differences':{k:{'expected':expected[k],'actual':v} for k,v in live.items() if expected[k]!=v},'engine_sha256':sha(binary),'all_engine_processes_waited':True,'QA_probe_inputs_unchanged':all(sha(Q/name)==digest and sha(S/'game/tests'/name)==digest for name,digest in probes.items()),'no_work_or_controller_mutations':True}
 write(Q/'post-run06-integrity.json',integrity)
 passed=all(r['passed'] for r in results) and len(results)==len(cases) and integrity['copy_inputs_unchanged'] and integrity['WORK_inputs_unchanged'] and integrity['QA_probe_inputs_unchanged']
 write(Q/'engine-job06-result.json',{'scope':'INDEPENDENT_ISOLATED_TEGA_ENGINE_QA_ONLY','passed':passed,'phase_approval':False,'results':[{k:r[k] for k in ['name','passed','exit_code','result_counts']} for r in results],'integrity':integrity,'not_tested':['native Windows','hardware FPS/input latency','subjective audio','full P06','publication/merge']})
 print('ALL_ISOLATED_QA_ENGINES_FINISHED',flush=True)
 return 0 if passed else 1
if __name__=='__main__':raise SystemExit(main())
