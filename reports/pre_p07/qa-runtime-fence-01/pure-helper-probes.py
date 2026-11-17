"""Exact AST-extracted candidate helper tests; no Controller/import/worker/network/engine."""
from pathlib import Path
import ast,hashlib,json,tempfile
Q=Path(__file__).resolve().parent;source=Q/'source-snapshot/autopilot/runner.py';raw=source.read_bytes();tree=ast.parse(raw);names={'_runtime_signature','_require_current_runtime'};functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names];assert len(functions)==2
assign=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RUNTIME_FILES' for t in n.targets));runtime_files=ast.literal_eval(assign.value)
class Blocked(RuntimeError):pass
rows=[]
with tempfile.TemporaryDirectory(prefix='qa-runtime-fence-pure-') as tmp:
 A=Path(tmp)/'source';B=Path(tmp)/'other-canonical';A.mkdir();B.mkdir();(A/'.git').mkdir();(B/'.git').mkdir();(A/'autopilot').mkdir();(A/'autopilot/runner.py').write_bytes(raw)
 markerA=A/'.autopilot/HANDOFF_PENDING.json';markerB=B/'.autopilot/HANDOFF_PENDING.json'
 namespace={'Path':Path,'hashlib':hashlib,'ROOT':A,'HANDOFF_PENDING':markerA,'RUNTIME_FILES':runtime_files,'Blocked':Blocked};exec(compile(ast.Module(body=functions,type_ignores=[]),str(source),'exec'),namespace);namespace['_LOADED_RUNTIME']=namespace['_runtime_signature']()
 def probe(name,target,expect_block):
  try:namespace['_require_current_runtime'](target);actual='ADMITTED';error=None
  except Blocked as exc:actual='BLOCKED';error=str(exc)
  rows.append({'name':name,'target_role':'MODULE_ROOT' if target==A else 'OTHER_CANONICAL_SHAPED_ROOT','expected':'BLOCKED' if expect_block else 'ADMITTED','actual':actual,'passed':(actual=='BLOCKED')==expect_block,'error':error})
 probe('valid unchanged module-root control',A,False)
 markerA.parent.mkdir();markerA.write_text('{}');probe('same-root pending blocks',A,True);markerA.unlink()
 path=A/'autopilot/runner.py';path.write_bytes(raw+b'\n# fixture change\n');probe('same-root loaded source change blocks',A,True);path.write_bytes(raw)
 (A/'.git').rmdir();(A/'.git').write_text('gitdir: TEST_ONLY\n');probe('same-root phase worktree blocks',A,True)
 markerB.parent.mkdir();markerB.write_text('{"TEST_ONLY":"INTERRUPTED_INSTALL"}');probe('phase-source library targeting another canonical root with pending install MUST block',B,True)
 (A/'.git').unlink();(A/'.git').mkdir();probe('canonical-source library targeting another canonical root with pending install MUST block',B,True)
 markerB.unlink();path.write_bytes(raw+b'\n# stale fixture runtime\n');probe('changed loaded source library targeting another canonical root MUST block',B,True)
 (B/'.git').rmdir();(B/'.git').write_text('gitdir: TEST_ONLY\n');probe('other target phase worktree remains denied',B,True)
result={'scope':'EXACT_CANDIDATE_HELPERS_PURE_FIXTURE_ONLY','source_sha256':hashlib.sha256(raw).hexdigest(),'method':'Exact two AST function bodies compiled unchanged in explicit temporary namespaces. No Controller import/construction, no child subprocess, no engine or canonical state/Git writes. Integration applicability assessed separately from actual constructor/exclusive source calls.','rows':rows,'passed':all(x['passed'] for x in rows),'Controller_calls':0,'child_processes':0,'network_calls':0,'production_state_writes':0};(Q/'pure-helper-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'cases':len(rows),'failed':[x['name'] for x in rows if not x['passed']]},ensure_ascii=False))
