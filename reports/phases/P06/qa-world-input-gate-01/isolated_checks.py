"""Independent QA: corrupt real traces in memory; wrapper/CI only mocked temp roots."""
from pathlib import Path
from unittest.mock import patch
import sys,json,hashlib,copy,tempfile,importlib.util,subprocess,contextlib,io,shutil,time
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=Path(__file__).parent
sys.path.insert(0,str(WORK/'tools'))
from p06_world_input import validate_world_input

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=WORK/'reports/phases/P06/attempt1/timka-world-native-02'
originals={mode:json.loads((source/mode/'result.json').read_text()) for mode in ['live','movie']}
original_hashes={mode:sha(source/mode/'result.json') for mode in originals}
start=time.monotonic();data=copy.deepcopy(originals['live']);moving=[i for i,p in enumerate(data['trace']) if p['input_vector']!=[0,0]];running=[i for i,p in enumerate(data['trace']) if p['run_pressed'] is True];trials=0;misses=[]
for field,indices,loss in [('input_vector',moving,[0,0]),('velocity',moving,[0,0]),('run_pressed',running,False)]:
 for i in indices:
  previous=data['trace'][i][field];data['trace'][i][field]=loss
  result=validate_world_input(data,'timka',84);trials+=1
  if result['passed']:misses.append({'field':field,'index':i})
  data['trace'][i][field]=previous
assert not misses and validate_world_input(data,'timka',84)['passed']
exhaustive={'trials':trials,'moving_samples':len(moving),'run_true_samples':len(running),'unexpected_acceptances':misses,'original_engine_pass_preserved':data['passed'] is True,'restored_data_equal_original':data==originals['live'],'seconds':round(time.monotonic()-start,3),'native_executed':False,'scope':'In-memory one-field-loss injection at every eligible real recorded sample'}
(OUT/'sample_loss_matrix.json').write_text(json.dumps(exhaustive,indent=2)+'\n')
wrapper=load('qa_verify_world_gate',WORK/'tools/verify_p06_world.py');wrapper_cases=[]
cases=[('valid_headless',False,None,None,0),('single_direction_loss',False,'live','input_vector',1),('single_shift_loss',False,'live','run_pressed',1),('single_velocity_loss',False,'live','velocity',1),('continuous_direction_loss',False,'live','continuous',1),('missing_observation',False,'live','missing',1),('original_engine_fail',False,'live','engine_fail',1),('engine_exit_fail',False,'live','exit_fail',1),('source_changed',False,None,'source_changed',1),('valid_movie',True,None,None,0),('movie_only_drop',True,'movie','input_vector',1),('live_drop_skips_movie',True,'live','input_vector',1)]
for name,movie,corrupt_mode,kind,wanted in cases:
 with tempfile.TemporaryDirectory(prefix='qa-p06-world-gate-') as temp:
  root=Path(temp);(root/'game/resources/characters').mkdir(parents=True);(root/'game/resources/characters/catalog.json').write_text(json.dumps({'actors':{'timka':{'role':'playable','speed':84}}}));calls=[]
  def fake_run(argv,**kwargs):
   argv=list(map(str,argv));calls.append(argv)
   if argv[0]=='/qa-fixture/godot-never-executed':
    scope=Path(kwargs['env']['AYAY_P06_WORLD_OUTPUT']);assert scope.is_relative_to(root);mode=scope.name
    d=copy.deepcopy(originals[mode if mode=='movie' else 'live']);d['renderer']='X11' if movie else 'headless'
    if mode==corrupt_mode:
     i=510 if kind=='continuous' else (85 if kind=='run_pressed' else 50)
     if kind in ['input_vector','continuous']:d['trace'][i]['input_vector']=[0,0]
     elif kind=='run_pressed':d['trace'][i]['run_pressed']=False
     elif kind=='velocity':d['trace'][i]['velocity']=[0,0]
     elif kind=='missing':del d['trace'][i]['input_vector']
     elif kind=='engine_fail':d['passed']=False
    (scope/'result.json').write_text(json.dumps(d))
    if '--write-movie' in argv:Path(argv[argv.index('--write-movie')+1]).write_bytes(b'QA mocked movie marker, not a playable recording')
    return subprocess.CompletedProcess(argv,1 if mode==corrupt_mode and kind=='exit_fail' else 0,'QA mocked engine result\n','')
   if argv[0]=='/qa-fixture/ffmpeg-never-executed':Path(argv[-1]).write_bytes(b'QA mocked encode marker');return subprocess.CompletedProcess(argv,0,'','')
   if argv[0]=='/qa-fixture/ffprobe-never-executed':return subprocess.CompletedProcess(argv,0,json.dumps({'streams':[{'codec_type':'video','nb_frames':'750'}]}),'')
   raise AssertionError('Forbidden actual subprocess: '+repr(argv))
  argv=['verify_p06_world.py','--actor','timka','--output','evidence']+(['--movie','--build-output','synthetic-video'] if movie else ['--headless'])
  snapshots=[{'fixture':'same'},{'fixture':'changed' if kind=='source_changed' else 'same'}]
  captured=io.StringIO()
  with patch.object(wrapper,'ROOT',root),patch.object(wrapper,'GODOT',Path('/qa-fixture/godot-never-executed')),patch.object(wrapper,'sources',side_effect=snapshots),patch.object(wrapper.subprocess,'run',side_effect=fake_run),patch.object(wrapper.subprocess,'check_output',return_value='f'*40+'\n'),patch.object(wrapper.shutil,'which',side_effect=lambda x:'/qa-fixture/'+x+'-never-executed'),patch.object(sys,'argv',argv),contextlib.redirect_stdout(captured):
   code=wrapper.main()
  result=json.loads((root/'evidence/validation.json').read_text());assert code==wanted,(name,code,result);assert result['passed']==(wanted==0),(name,result)
  if kind in ['input_vector','run_pressed','velocity','continuous','missing']:assert not result['strict_input_verified']
  if name=='live_drop_skips_movie':assert len(calls)==1
  case_out=OUT/'wrapper-cases'/name;case_out.mkdir(parents=True);shutil.copyfile(root/'evidence/validation.json',case_out/'validation.json');(case_out/'stdout.log').write_text(captured.getvalue())
  for mode,gate in result['strict_input_gates'].items():(case_out/(mode+'-input-gate.json')).write_text(json.dumps(gate,indent=2)+'\n')
  wrapper_cases.append({'case':name,'code':code,'expected_code':wanted,'passed':True,'strict_input_verified':result['strict_input_verified'],'gate_scopes':list(result['strict_input_gates']),'engine_called_modes':[Path(a[a.index('--write-movie')+1]).name if '--write-movie' in a else 'live' for a in calls if a[0]=='/qa-fixture/godot-never-executed'],'production_native_executed':False,'synthetic_fixture':True})
(OUT/'wrapper_wiring.json').write_text(json.dumps(wrapper_cases,indent=2)+'\n')
ci=load('qa_common_verify_gate',WORK/'tools/verify.py');ci_cases=[]
for fail_gate in [False,True]:
 with tempfile.TemporaryDirectory(prefix='qa-p06-world-ci-') as temp:
  root=Path(temp);binary=root/'.tools/godot/Godot_vqa_linux.x86_64';binary.parent.mkdir(parents=True);binary.write_bytes(b'QA fake binary; never executed');(root/'tools').mkdir();(root/'tools/toolchain.lock.json').write_text(json.dumps({'release':'qa','linux_binary_sha256':sha(binary),'godot_version':'qa'}));(root/'game/tests').mkdir(parents=True);(root/'game/tests/character_frames_test.gd').write_text('QA presence marker only');calls=[]
  def fake_ci_run(argv,**kwargs):
   calls.append(list(map(str,argv)));gate='test_p06_world_input.py' in argv;return subprocess.CompletedProcess(argv,1 if gate and fail_gate else 0,'qa.stable.fixture\n' if '--version' in argv else 'QA mocked command\n','FAIL: intentional fixture gate failure\n' if gate and fail_gate else '')
  captured=io.StringIO()
  with patch.object(ci,'ROOT',root),patch.object(ci.subprocess,'run',side_effect=fake_ci_run),patch.object(sys,'argv',['verify.py','--output','ci']),contextlib.redirect_stdout(captured):code=ci.main()
  results=json.loads((root/'ci/validation.json').read_text());gate=next(x for x in results if x['name']=='world_input_gate');assert bool(code)==fail_gate and gate['passed']==(not fail_gate);assert any(a[1:]==['-m','unittest','discover','-s','tools/tests','-p','test_p06_world_input.py'] for a in calls)
  ci_cases.append({'injected_gate_failure':fail_gate,'overall_exit':int(code),'world_input_gate':gate,'command_registered':True,'native_or_other_commands_really_executed':False})
(OUT/'ci_wiring.json').write_text(json.dumps(ci_cases,indent=2)+'\n')
assert {mode:sha(source/mode/'result.json') for mode in originals}==original_hashes
summary={'scope':'INDEPENDENT_ISOLATED_FAULT_AND_WRAPPER_WIRING_TESTS_ONLY','phase_approval':False,'sample_loss_faults_rejected':trials,'wrapper_cases_passed':len(wrapper_cases),'ci_wiring_cases_passed':len(ci_cases),'native_evidence_source_files_unchanged':True,'actual_Godot_Git_network_build_or_executor_invocations':False}
(OUT/'isolated_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
