"""Exact private-wrapper AST admission nodes, disposable plans/approvals only."""
from pathlib import Path
from types import SimpleNamespace
import ast,hashlib,json,tempfile
Q=Path(__file__).resolve().parent;wrapper=Q/'wrapper-A03.py.txt';tree=ast.parse(wrapper.read_text());block=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and isinstance(n.test,ast.Compare) and isinstance(n.test.left,ast.Attribute) and n.test.left.attr=='action').orelse
# Execute only existing plan/approval admission nodes, never source/build/Bootstrap/root operations.
names={'plan_blob','plan_sha','plan','approvals','approval_blobs'}
def assignment(n):return isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in names for t in n.targets)
selected=[n for n in block if assignment(n) or isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='role' or isinstance(n,ast.Assert) and any(isinstance(x,ast.Constant) and isinstance(x.value,str) and ('plan SHA required' in x.value or 'changed after' in x.value) for x in ast.walk(n))]
assert len(selected)==9,len(selected)
rows=[]
for mode in ['valid','wrong_requested_planSHA','plan_drift_after_parse','approval_drift_after_parse','FAIL_approval','wrong_approval_planSHA','false_execution_flag']:
 with tempfile.TemporaryDirectory(prefix='qa-bootstrap-execution-') as tmp:
  r=Path(tmp);plan=r/'plan.json';plan.write_text('{"TEST_ONLY":"approved_plan"}');blob=plan.read_bytes();digest=hashlib.sha256(blob).hexdigest()
  for role in ['qa','lead']:
   f=r/f'reports/pre_p07/{role}-bootstrap-A-execution-01/decision.json';f.parent.mkdir(parents=True);data={'status':'PASS','actual_A_execution_approved':True,'plan_sha256':digest,'TEST_ONLY_role':role}
   if role=='qa':
    if mode=='FAIL_approval':data['status']='FAIL'
    if mode=='wrong_approval_planSHA':data['plan_sha256']='0'*64
    if mode=='false_execution_flag':data['actual_A_execution_approved']=False
   f.write_text(json.dumps(data))
  def parse(raw):
   value=json.loads(raw)
   if mode=='plan_drift_after_parse' and raw==blob:plan.write_text('{"TEST_ONLY":"unapproved_changed_plan"}')
   if mode=='approval_drift_after_parse' and value.get('TEST_ONLY_role')=='qa':
    f=r/'reports/pre_p07/qa-bootstrap-A-execution-01/decision.json';f.write_text(json.dumps(dict(value,status='FAIL',actual_A_execution_approved=False)))
   return value
  ns={'R':r,'PLAN':plan,'Path':Path,'hashlib':hashlib,'args':SimpleNamespace(expected_plan_sha='0'*64 if mode=='wrong_requested_planSHA' else digest),'parsejson':parse}
  error=None
  try:exec(compile(ast.Module(body=selected,type_ignores=[]),str(wrapper),'exec'),ns);admitted=True
  except AssertionError as exc:admitted=False;error=str(exc)
  rows.append({'case':mode,'admitted':admitted,'expected_admitted':mode=='valid','passed':admitted==(mode=='valid'),'error':error})
result={'scope':'EXACT_PRIVATE_WRAPPER_ADMISSION_NODES_TEMP_FIXTURES_NO_INSTALL','wrapper_sha256':hashlib.sha256(wrapper.read_bytes()).hexdigest(),'cases':rows,'passed':all(x['passed'] for x in rows),'actual_ROOT_Bootstrap_Controller_engine_process_calls':0};(Q/'final-approval-binding-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'cases':len(rows),'failed':[x['case'] for x in rows if not x['passed']]}))
