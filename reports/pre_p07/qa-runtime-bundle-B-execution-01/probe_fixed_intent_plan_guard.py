from pathlib import Path
import importlib.util,ast,json,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;S=Q.parent/'qa-runtime-bundle-B-02/source';sys.path.insert(0,str(S/'tools'));sys.path.insert(0,str(S/'tools/tests'))
spec=importlib.util.spec_from_file_location('B_fixed_guard_fixture',S/'tools/tests/test_cold_runtime_bundle.py');t=importlib.util.module_from_spec(spec);spec.loader.exec_module(t)
tree=ast.parse((Q/'wrapper-B02.py.txt').read_text());nodes=[]
for n in ast.walk(tree):
 if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Attribute) and n.value.func.attr=='load_bundle':nodes.append(n)
 if isinstance(n,ast.Assert) and any(isinstance(x,ast.Constant) and x.value=='installed_a' for x in ast.walk(n)):nodes.append(n)
assert len(nodes)==2
rows=[]
for mode in ['valid','protected_changed_after_initial_check']:
 c=t.BundleTests('test_complete_bundle_fresh_process_preserves_authority');c.setUp()
 try:
  plan={'before':c.before,'protected':c.kept};A=c.proof
  with t.RuntimeBundle(c.root).lease() as maintenance:
   assert maintenance.protected(plan['protected'])==plan['protected']
   if mode!='valid':c.state.write_bytes(b'{"TEST_ONLY":"unapproved_authority_change"}')
   ident=maintenance.begin_bundle(t.PAYLOADS,plan['before'],list(plan['protected']),A);ns={'maintenance':maintenance,'ident':ident,'plan':plan,'A':A}
   blocked=False
   try:exec(compile(ast.Module(body=nodes,type_ignores=[]),'exact_common_apply_recovery_guard','exec'),ns)
   except AssertionError:blocked=True
   if not blocked:result=maintenance.finish_bundle(ident)['status']
   else:result='BLOCKED_BEFORE_FIRST_COPY'
   old_runtime=maintenance.protected(t.TARGETS)==c.before
  passed=(not blocked and result=='COMMIT_VERIFIED') if mode=='valid' else blocked and old_runtime and (c.root/t.bundle.MARKER).exists()
  rows.append({'case':mode,'passed':passed,'result':result,'runtime_still_before':old_runtime,'marker_retained':(c.root/t.bundle.MARKER).exists(),'actual_ROOT_installation':False})
 finally:c.tearDown()
out={'scope':'EXACT_FIXED_COMMON_INTENT_GUARD_WITH_DISPOSABLE_B_ONLY','passed':all(x['passed'] for x in rows),'cases':rows,'actual_ROOT_Controller_engine_or_installation_calls':0};(Q/'fixed-intent-plan-guard-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':out['passed'],'cases':len(rows)}))
