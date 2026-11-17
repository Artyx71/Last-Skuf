"""TEST_ONLY: execute coordinator main with mocked children/HEAD/inventory; no engines."""
from pathlib import Path
import sys,types,json,hashlib,tempfile,contextlib,io
sys.dont_write_bytecode=True
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-native-continuation-preflight-01';O.mkdir(exist_ok=True)
sys.path.insert(0,str(W/'tools'));import verify_p06 as original_pipeline
source=(O/'frozen-742-coordinator.py.txt').read_text();assert hashlib.sha256(source.encode()).hexdigest()=='8100208ff8e3fba1010c0461cc1c1bddf2aee59b30e8428b3be82bb8bb354ddf'
results=[]
for mode in ['valid_control','contract_mutation','approval_mutation']:
 with tempfile.TemporaryDirectory(prefix='TEST_ONLY_',dir=O) as td:
  root=Path(td);ns={'__name__':'TEST_ONLY_MODULE'};exec(compile(source,str(W/'tools/continue_p06_native.py'),'exec'),ns);ns['ROOT']=root
  def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v))
  def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
  reusable={'passed':True,'commands':[{'passed':True,'exit_code':0,'name':'TEST_ONLY','argv':['TEST_ONLY']}],'phase_approval':False,'source_unchanged':True}
  put(root/'before.json',{});put(root/'after.json',{});put(root/'parent.json',{'passed':False,'commands':[{'name':n,'passed':True,'exit_code':0} for n in ns['REUSED']]+[{'name':'pasha','passed':False,'exit_code':1}]});put(root/'child.json',reusable)
  rows=[]
  for reduced in ['false','true']:
   for direction,vector in [('down',[0.,1.]),('left',[-1.,0.]),('right',[1.,0.]),('up',[0.,-1.])]:
    segment='moving_shot_'+reduced+'_'+direction
    rows.extend([{'segment':segment,'tick':i,'run_pressed':True,'input_vector':vector} for i in range(32)])
  put(root/'trace.json',{'ammo_trace':rows,'trace':rows});(root/'artifact.txt').write_text('TEST_ONLY immutable artifact')
  contract={'old_sources_before':'before.json','old_sources_after':'after.json','source_changes':{},'artifacts':[{'path':'artifact.txt','sha256':sha(root/'artifact.txt')}],'old_validation':'parent.json','reused_stages':[{'name':n,'report':'child.json'} for n in ns['REUSED']],'pasha_validations':['child.json'],'pasha_traces':['trace.json'],'Pasha_original_cause':'UNKNOWN'};put(root/'contract.json',contract);contract_before=sha(root/'contract.json')
  put(root/'approval.json',{'status':'PASS_COMPONENT_EXECUTION_ONLY','contract_sha256':contract_before,'phase_approval':False});approval_before=sha(root/'approval.json');engine=root/'.tools/godot/Godot_vTEST_ONLY_linux.x86_64';engine.parent.mkdir(parents=True);engine.write_text('TEST_ONLY not executable');put(root/'tools/toolchain.lock.json',{'release':'TEST_ONLY','linux_binary_sha256':sha(engine)})
  def fake_run(argv,log,timeout):
   log.parent.mkdir(parents=True,exist_ok=True);log.write_text('TEST_ONLY mocked successful child; no process started\n')
   if argv[0]=='TEST_ONLY':
    name=argv[1];put(root/'out'/name/'validation.json',reusable)
    if name==ns['TAIL'][-1]:
     if mode=='contract_mutation':put(root/'contract.json',contract|{'Pasha_original_cause':'TEST_ONLY_MUTATED_AFTER_APPROVAL'})
     if mode=='approval_mutation':put(root/'approval.json',{'status':'FAIL_COMPONENT','contract_sha256':contract_before,'phase_approval':False})
   return {'passed':True,'exit_code':0,'argv':list(map(str,argv)),'seconds':0,'name':'TEST_ONLY'}
  ns['pipeline']=types.SimpleNamespace(strict_report=original_pipeline.strict_report,sha=sha,inventory=lambda:{},valid_report=original_pipeline.valid_report,write=put,plan=lambda *a,**k:[(n,['TEST_ONLY',n],1) for n in ns['TAIL']],run_command=fake_run)
  ns['subprocess']=types.SimpleNamespace(check_output=lambda *a,**k:'TEST_ONLY_FROZEN_HEAD\n');prior=sys.argv;sys.argv=['TEST_ONLY','--contract','contract.json','--approval',str(root/'approval.json'),'--approval-sha256',approval_before,'--output','out','--build-output','build'];buf=io.StringIO()
  try:
   with contextlib.redirect_stdout(buf):code=ns['main']()
  finally:sys.argv=prior
  summary=json.loads((root/'out/validation.json').read_text());results.append({'mode':mode,'actual_unmodified_coordinator_exit':code,'composed_summary_passed':summary['passed'],'summary_stages':len(summary['stages']),'contract_before':contract_before,'contract_after':sha(root/'contract.json'),'approval_before':approval_before,'approval_after':sha(root/'approval.json'),'summary_contract_SHA':summary['contract_sha256'],'summary_approval_SHA':summary['approval_sha256'],'mock_child_calls_only':True,'actual_engine_or_Git_or_process_started':False,'stdout':buf.getvalue()})
assert results[0]['actual_unmodified_coordinator_exit']==0 and results[0]['composed_summary_passed']
assert all(x['actual_unmodified_coordinator_exit']==0 and x['composed_summary_passed'] for x in results[1:])
(O/'contract-approval-drift-counterexample.json').write_text(json.dumps({'schema':1,'scope':'PURE_TEST_ONLY_UNMODIFIED_COORDINATOR_MAIN_WITH_MOCKED_CHILD_EXECUTION','candidate_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'results':results,'product_or_engine_test_claim':False},indent=2)+'\n');print(json.dumps(results,indent=2))
