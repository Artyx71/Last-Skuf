from pathlib import Path
import ast,hashlib,json,tempfile
Q=Path(__file__).resolve().parent;p=Q/'source-snapshot/autopilot/runner.py';raw=p.read_bytes();tree=ast.parse(raw);fns=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in {'_runtime_signature','_require_current_runtime'}];files=ast.literal_eval(next(n.value for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='RUNTIME_FILES' for t in n.targets)))
class Blocked(RuntimeError):pass
rows=[]
with tempfile.TemporaryDirectory(prefix='qa-runtime-fence02-boundary-') as tmp:
 A=Path(tmp)/'source';B=Path(tmp)/'library';A.mkdir();B.mkdir();(A/'autopilot').mkdir();(A/'autopilot/runner.py').write_bytes(raw);ma=A/'.autopilot/HANDOFF_PENDING.json';mb=B/'.autopilot/HANDOFF_PENDING.json';ma.parent.mkdir();mb.parent.mkdir()
 ns={'ROOT':A,'Path':Path,'hashlib':hashlib,'HANDOFF_PENDING':ma,'RUNTIME_FILES':files,'Blocked':Blocked};exec(compile(ast.Module(body=fns,type_ignores=[]),str(p),'exec'),ns);ns['_LOADED_RUNTIME']=ns['_runtime_signature']()
 def case(name,target,block):
  try:ns['_require_current_runtime'](target);actual=False;reason=None
  except Blocked as exc:actual=True;reason=str(exc)
  rows.append({'name':name,'expected_blocked':block,'actual_blocked':actual,'passed':actual==block,'reason':reason})
 case('bare library fixture remains allowed',B,False)
 ma.write_text('broken JSON deliberately: existence must be sufficient');case('source pending fences otherwise clean custom fixture',B,True);ma.unlink()
 mb.symlink_to(B/'missing-journal');case('dangling target pending marker blocks',B,True);mb.unlink()
 ma.symlink_to(A/'missing-journal');case('dangling source pending marker blocks custom fixture',B,True);ma.unlink()
 (B/'autopilot').mkdir();entry=B/'autopilot/runner.py';entry.write_bytes(raw);case('other installed runtime cannot be borrowed',B,True);entry.unlink()
 entry.symlink_to(B/'missing-runner');case('dangling installed runtime cannot be borrowed',B,True);entry.unlink()
 (A/'autopilot/runner.py').write_bytes(raw+b'\n# changed\n');case('loaded source mutation blocks custom fixture',B,True);(A/'autopilot/runner.py').write_bytes(raw)
 alias=Path(tmp)/'alias';alias.symlink_to(A,target_is_directory=True);case('resolved same-root alias preserves valid admission',alias,False)
result={'scope':'PURE_EXACT_FIXED_HELPER_BOUNDARY_CONTROLS_ONLY','source_sha256':hashlib.sha256(raw).hexdigest(),'cases':rows,'passed':all(x['passed'] for x in rows),'Controller_calls':0,'process_calls':0,'engine_calls':0,'production_state_writes':0};(Q/'pure-boundary-results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'cases':len(rows),'failed':[x['name'] for x in rows if not x['passed']]}))
