"""Reproduce the preserved unused A02 wrapper loop on fake approvals only."""
from pathlib import Path
import ast,json,hashlib,tempfile
Q=Path(__file__).resolve().parent;wrapper=Q/'wrapper-A02-before-approval-binding.py.txt';tree=ast.parse(wrapper.read_text());loop=next(n for n in ast.walk(tree) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='role')
with tempfile.TemporaryDirectory(prefix='qa-old-approval-') as tmp:
 root=Path(tmp);expected='71ac28dac5327aa6a40dca0fb15395053f6175b7caa8611eeb57dc24cf188245'
 for role in ['qa','lead']:
  f=root/f'reports/pre_p07/{role}-bootstrap-A-execution-01/decision.json';f.parent.mkdir(parents=True);f.write_text(json.dumps({'status':'PASS','actual_A_execution_approved':True,'plan_sha256':expected}))
 def readjson(p):
  data=json.loads(p.read_text());p.write_text(json.dumps(dict(data,status='FAIL',actual_A_execution_approved=False)));return data
 ns={'R':root,'readjson':readjson,'sha':lambda p:hashlib.sha256(p.read_bytes()).hexdigest(),'plan_sha':expected,'approvals':[]};exec(compile(ast.Module(body=[loop],type_ignores=[]),str(wrapper),'exec'),ns)
 assert all(json.loads((root/x['path']).read_text())['status']=='FAIL' for x in ns['approvals'])
 print('Preserved A02 counterexample: loop admits while recorded files are FAIL. No actualRoot actions.')
