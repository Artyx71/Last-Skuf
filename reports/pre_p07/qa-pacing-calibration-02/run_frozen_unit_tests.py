from pathlib import Path
import ast,json,math,hashlib,tempfile,unittest,io
O=Path(__file__).resolve().parent
ns={'json':json,'math':math,'hashlib':hashlib,'Path':Path,'digest':lambda p:hashlib.sha256(p.read_bytes()).hexdigest(),'tempfile':tempfile,'unittest':unittest}
a=ast.parse((O/'final-source-df/autopilot/readiness.py').read_text());exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.FunctionDef)and n.name=='strict_json'],type_ignores=[]),'frozen-house','exec'),ns)
a=ast.parse((O/'final-source-df/tools/p07_pacing.py').read_text());nodes=[n for n in a.body if isinstance(n,ast.FunctionDef)and n.name not in ['main','encode_clip']or isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='CONTEXTS'for t in n.targets)];exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-df7a','exec'),ns)
a=ast.parse((O/'final-source-df/tools/tests/test_p07_pacing.py').read_text());exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,ast.ClassDef)],type_ignores=[]),'frozen-test','exec'),ns)
buf=io.StringIO();result=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ns['PacingValidation']));(O/'frozen-unit-tests.log').write_text(buf.getvalue());(O/'frozen-unit-tests.json').write_text(json.dumps({'scope':'FROZEN_PURE_TEMPFILE_UNIT_TESTS_NO_ENGINE','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'passed':result.wasSuccessful()},indent=2)+'\n');print(buf.getvalue());assert result.wasSuccessful()
