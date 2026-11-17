"""Read-only actual A verification. Only operational call is fresh runner status."""
from pathlib import Path
import json, hashlib, stat, ast, subprocess, os
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0')
O=Path(__file__).resolve().parent
A=R/'reports/pre_p07/bootstrap-actual-A-03'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('duplicate key')
  d[k]=v
 return d
def read(p):return json.loads(p.read_bytes(),object_pairs_hook=pairs)
def fp(p):
 if p.is_symlink():raise ValueError('symlink')
 if not p.exists():return None
 s=p.stat()
 assert stat.S_ISREG(s.st_mode) and s.st_nlink==1
 return {'sha256':H(p),'mode':stat.S_IMODE(s.st_mode),'uid':s.st_uid,'gid':s.st_gid}
plan=read(A/'plan.json');assert H(A/'plan.json')=='2075eb9c7e0d5e6b1d39bbac8851b9113125b2a3c492ff66a914d98f1038abbe'
txn=read(A/'transaction.json');assert txn['plan_sha256']==H(A/'plan.json')
expected_approvals={
 'reports/pre_p07/qa-bootstrap-A-execution-01/decision.json':'c9c3f2c90e8cdaef44e646ca5ae36aa9c8784700e7436a15b55b71db62187db4',
 'reports/pre_p07/lead-bootstrap-A-execution-01/decision.json':'2a121bccbe5717952c60bf64e4c63c5a8630d02df94da9809eed9a726ee4d2b4'}
assert {x['path']:x['sha256']for x in txn['approvals']}==expected_approvals
for path,digest in expected_approvals.items():
 assert H(R/path)==digest
 q=read(R/path);assert q['status']=='PASS' and q['actual_A_execution_approved']is True and q['plan_sha256']==txn['plan_sha256']
folder=R/'.autopilot/bootstrap'/txn['id'];intent_blob=(folder/'intent.json').read_bytes();intent=json.loads(intent_blob,object_pairs_hook=pairs);journal=read(folder/'journal.json')
assert journal=={'id':txn['id'],'intent_sha256':hashlib.sha256(intent_blob).hexdigest(),'status':'VERIFIED'}
assert intent['id']==txn['id'] and intent['root']==str(R) and intent['kind']=='BOOTSTRAP_A_NOT_BUNDLE'
assert intent['protected']==plan['protected'] and intent['target']==dict(intent['before'],sha256=plan['target_sha256'])
assert H(folder/'old.py')==intent['before']['sha256']==plan['legacy_sha256']
assert H(folder/'new.py')==intent['target']['sha256']==plan['target_sha256']
assert fp(R/'autopilot/runner.py')==intent['target']
def check_protected():
 bad=[]
 for path,expected in plan['protected'].items():
  p=R
  for part in Path(path).parts:
   p=p/part
   assert not p.is_symlink()
  if fp(p)!=expected:bad.append(path)
 assert not bad,bad
 return len(plan['protected'])
assert check_protected()==337
for n in ['.autopilot/BOOTSTRAP_PENDING.json','.autopilot/HANDOFF_PENDING.json','.autopilot/RUNTIME_BUNDLE_STARTED.json','.autopilot/RUNNING.lock']:
 assert not (R/n).exists() and not (R/n).is_symlink()
lock=(R/'automation/.executor.lock').stat();assert [lock.st_dev,lock.st_ino]==intent['lock']==[59,1118521] and lock.st_nlink==1
text=(R/'autopilot/runner.py').read_text();tree=ast.parse(text);runtime_names=ast.literal_eval(next(x for x in tree.body if isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='RUNTIME_FILES'for t in x.targets)).value)
runtime={n:fp(R/n)for n in runtime_names};assert len(runtime)==10
smoke=read(A/'fresh-smoke.json');assert smoke['runner_sha256']==plan['target_sha256'] and smoke['ROOT']==str(R) and smoke['module_path']==str(R/'autopilot/runner.py')
assert smoke['runtime_signature']=={n:(v['sha256']if v else None)for n,v in runtime.items()}
assert smoke['cli_status_exit_code']==0 and smoke['protected_files_unchanged']==337
before_state=H(R/'automation/phase_state.json')
run=subprocess.run(['/usr/bin/python3','-B',str(R/'autopilot/runner.py'),'status'],cwd=R,capture_output=True)
assert run.returncode==0,run.stderr.decode(errors='replace')
view=json.loads(run.stdout,object_pairs_hook=pairs);assert view==read(A/'fresh-status.json')
assert view['phases']['P06']['merge']['merge_sha']=='f8325212381d67a469b5d9a6dffbf3d244bc9933' and view['phases']['P06']['attempts']==1 and view['phases']['P07']['attempts']==0
assert H(R/'automation/phase_state.json')==before_state and check_protected()==337
state=read(R/'automation/phase_state.json');assert state['attempts']==2
assert read(R/'autopilot/config.json')['stop_after_phase']=='P06'
assert fp(R/'autopilot/runner.py')==intent['target'] and H(folder/'intent.json')==hashlib.sha256(intent_blob).hexdigest()
baseline={'schema':1,'scope':'VERIFIED_POST_A_GUARDED_LEGACY_BASELINE_FOR_FUTURE_B_NOT_B_APPROVAL','transaction':txn['id'],'plan_sha256':txn['plan_sha256'],'runner':intent['target'],'runtime_files':runtime,'full_protected_inventory_path':'reports/pre_p07/bootstrap-actual-A-03/plan.json','full_protected_count':337,'bootstrap_intent_sha256':hashlib.sha256(intent_blob).hexdigest(),'bootstrap_journal_sha256':H(folder/'journal.json'),'lock_identity':{'dev':lock.st_dev,'ino':lock.st_ino},'worker_verify_only':True,'Root_Game_tools_sync':False,'B_rollback_must_preserve_this_guarded_runner':True}
(O/'post-A-runtime-baseline.json').write_text(json.dumps(baseline,indent=2)+'\n')
out={'schema':1,'scope':'INDEPENDENT_ACTUAL_A_POST_INSTALL_READ_ONLY_VERIFICATION','passed':True,'target_sha256':plan['target_sha256'],'runner_mode_octal':oct(intent['target']['mode']),'protected_verified_before_after_status':337,'old_backup_hash_valid':True,'new_backup_hash_valid':True,'journal_status':'VERIFIED','intent_journal_approvals_bound':True,'lock_inode_unchanged':1118521,'pending_and_RUNNING_markers_absent':True,'new_cli_status_exit':run.returncode,'new_cli_status_stdout_sha256':hashlib.sha256(run.stdout).hexdigest(),'new_cli_status_stderr_sha256':hashlib.sha256(run.stderr).hexdigest(),'new_cli_status_semantically_equal_author_fresh_status':True,'canonical_state_byte_unchanged':True,'global_attempts':state['attempts'],'P06_attempts':1,'P07_attempts':0,'P06_merge_sha':view['phases']['P06']['merge']['merge_sha'],'Root_Controller_status_process_calls':1,'direct_Root_Controller_import_or_exclusive_persist_calls':0,'A_apply_calls':0,'engine_or_Git_write_calls':0,'production_file_mutations_by_Lead':0,'private_authority_or_wrapper_bytes_copied':False,'full_C02_B_GameSync_Readiness_P07_approval':False}
(O/'actual-verification.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
