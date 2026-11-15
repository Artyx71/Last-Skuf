from pathlib import Path
import runpy,sys,json,shutil,contextlib,io,hashlib
from unittest.mock import patch
from types import SimpleNamespace
Q=Path(__file__).resolve().parent;I=Q/'isolated-project';engine=json.loads((Q/'engine-copy.json').read_text());binary=I/'.tools/godot'/Path(engine['path']).name;binary.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(Q/engine['path'],binary);binary.chmod(0o755)
assert hashlib.sha256(binary.read_bytes()).hexdigest()==engine['sha256']
mod=runpy.run_path(str(I/'tools/verify.py'),run_name='qa_frozen_verify');lock=json.loads((I/'tools/toolchain.lock.json').read_text());summ=[]
for case in ['success','exit_failure','fatal_log_exit_zero']:
 seen=[];out=I/'reports/qa-ci-routing'/case;assert not out.exists()
 def fake_run(argv,**kw):
  argv=[str(a) for a in argv];seen.append(argv)
  text=lock['godot_version']+'.stable.TEST_ONLY\n' if argv[-1]=='--version' else 'TEST_ONLY mocked command result\n'
  code=0
  if 'tools/verify_p06_ryzhik.py' in argv:
   if case=='exit_failure':code=9
   if case=='fatal_log_exit_zero':text='ERROR: TEST_ONLY controlled Ryzhik prime failure\n'
  return SimpleNamespace(returncode=code,stdout=text,stderr='')
 capture=io.StringIO()
 with patch.object(sys,'argv',['tools/verify.py','--output',str(out.relative_to(I))]),patch.object(mod['subprocess'],'run',side_effect=fake_run),contextlib.redirect_stdout(capture):
  status=mod['main']()
 (Q/('ci-'+case+'.log')).write_text(capture.getvalue())
 results=json.loads((out/'validation.json').read_text());target=[r for r in results if r['name']=='ryzhik_roll_controller'];assert len(target)==1
 routed=[a for a in seen if 'tools/verify_p06_ryzhik.py' in a];assert len(routed)==1 and '--headless' in routed[0]
 assert routed[0][routed[0].index('--output')+1]==str(out/'ryzhik_roll_controller')
 assert any('res://tests/ryzhik_roll_layout_test.gd' in a for a in seen)
 expected=case=='success';assert target[0]['passed']==expected and bool(status)==(not expected)
 summ.append({'case':case,'actual_main_return':status,'timka_validation':target[0],'ryzhik_argv':routed[0],'mocked_commands':len(seen),'all_expected':True,'command':seen})
 (Q/('ci-'+case+'-validation.json')).write_text(json.dumps(results,indent=2)+'\n')
(Q/'CI-routing-results.json').write_text(json.dumps({'scope':'FROZEN_COMMON_VERIFY_MAIN_EXECUTED_WITH_ALL_SUBPROCESS_RUN_CALLS_MOCKED','actual_engine_or_remote_CI_run':False,'cases':summ},indent=2)+'\n')
print('PASS3/3 actual common-main routing and failure propagation probes; subprocesses mocked, no engine/GitHubCI executed')
