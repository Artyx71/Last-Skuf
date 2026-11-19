"""Private apply-flow condition using actual B methods, disposable TEST_ONLY root."""
from pathlib import Path
import importlib.util,json,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;S=Q.parent/'qa-runtime-bundle-B-02/source';sys.path.insert(0,str(S/'tools'));sys.path.insert(0,str(S/'tools/tests'))
spec=importlib.util.spec_from_file_location('B_execution_fixture',S/'tools/tests/test_cold_runtime_bundle.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
c=t.BundleTests('test_complete_bundle_fresh_process_preserves_authority');c.setUp()
try:
 root=c.root;approved_protected=c.kept;before=c.before
 with t.RuntimeBundle(root).lease() as maintenance:
  assert maintenance.protected(approved_protected)==approved_protected
  # Fault: unknown protected authority change after the wrapper's initial plan
  # check and before begin_bundle snapshots its own preconditions.
  c.state.write_bytes(b'{"TEST_ONLY":"new_unapproved_authority_after_plan_check"}')
  ident=maintenance.begin_bundle(t.PAYLOADS,before,list(approved_protected),c.proof)
  _,intent=maintenance.load_bundle(ident)
  intent_equals_approved=intent['protected']==approved_protected
  result=maintenance.finish_bundle(ident)
  final_plan_match=maintenance.protected(approved_protected)==approved_protected
 out={'scope':'PRIVATE_APPLY_FLOW_PREBEGIN_DRIFT_TEST_ONLY_NOT_B_COMPONENT_DEFECT','initial_plan_protected_check_passed':True,'new_intent_protected_equals_approved_plan':intent_equals_approved,'actual_B_method_return':result['status'],'all_seven_targets_installed':all(t.fs.sha((root/k).read_bytes())==v for k,v in t.TARGETS.items()),'HANDOFF_marker_remaining':(root/t.bundle.MARKER).exists(),'wrapper_final_plan_protected_check_would_pass':final_plan_match,'missing_wrapper_guard':'apply branch never compares newly created intent against approved before/protected/A plan before finish; finish/rollback branches do compare','actual_ROOT_Controller_engine_or_installation_calls':0}
 (Q/'apply-intent-binding-counterexample.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
finally:c.tearDown()
