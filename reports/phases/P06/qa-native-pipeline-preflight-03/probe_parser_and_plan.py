"""Read-only exact AST probes. No main, Godot, subprocess, Controller or workers."""
from pathlib import Path
import ast,hashlib,json,math,sys,tempfile,copy
Q=Path(__file__).resolve().parent
R=Q.parents[3]
W=R/'.autopilot/worktrees/P06'
P=Q/'source/tools/verify_p06.py'
tree=ast.parse(P.read_text())
functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
ns={'json':json,'math':math,'sys':sys}
exec(compile(ast.Module(body=[functions[n] for n in ['strict_report','clean_command','valid_report','plan']],type_ignores=[]),str(P),'exec'),ns)
base={'passed':True,'commands':[{'name':'live','argv':['test-only-noengine'],'passed':True,'exit_code':0}],'phase_approval':False,'source_unchanged':True}
old=Q/'inputs/prior18cases.json'
cases=[(x['name'],x['raw_JSON'],x['expected_safe_acceptance']) for x in json.loads(old.read_text())['cases']]
for name,val in [('nested_exp_overflow',{'arr':[{'metric':float('inf')}]}),('phase_true',{'phase_approval':True}),('phase_missing',{}),('source_false',{'source_unchanged':False}),('commands_empty',{'commands':[]})]:
 if name=='phase_missing': v=copy.deepcopy(base);v.pop('phase_approval')
 else:v={**base,**val}
 text=json.dumps(v).replace('Infinity','1e309')
 cases.append((name,text,False))
for name,value in [('blank_name',' '),('blank_log','\t')]:
 row={'name':'live','log':'live.log','passed':True,'exit_code':0};row['name' if name=='blank_name' else 'log']=value
 cases.append((name,json.dumps([row]),False))
for name,argv in [('blank_arg',[' ']),('empty_arg',['']),('numeric_arg',[0]),('mixed_arg',['actual',None]),('bool_arg',[True])]:
 cases.append((name,json.dumps({**base,'commands':[{'name':'live','argv':argv,'passed':True,'exit_code':0}]}),False))
cases += [('finite_boundary',json.dumps(base)[:-1]+',"metric":1e308}',True),('unicode_name',json.dumps([{'name':'проверка','checks':{'реальный':True},'passed':True}]),True),('zero_float',json.dumps(base)[:-1]+',"metric":-0.0}',True),('nested_decoded_duplicate',json.dumps(base)[:-1]+',"meta":{"a":false,"\\u0061":true}}',False)]
rows=[]
with tempfile.TemporaryDirectory(prefix='pure-report-',dir=Q) as tmp:
 for i,(name,text,expected) in enumerate(cases):
  f=Path(tmp)/(str(i)+'.json');f.write_text(text)
  actual=ns['valid_report'](f);rows.append({'name':name,'raw_JSON':text,'expected':expected,'actual':actual,'passed':actual==expected})
# Independently load and rehash the REAL reports, not the author's result booleans.
actual_reports=[]
for x in json.loads((Q/'source/reports/phases/P06/native-pipeline-parser-fix-02/real-report-compatibility.json').read_text()):
 p=Q/'retained-reports'/(x['id']+'.json'); data=p.read_bytes();actual=ns['valid_report'](p);digest=hashlib.sha256(data).hexdigest()
 actual_reports.append({'id':x['id'],'path':x['path'],'actual_sha256':digest,'expected_sha256':x['sha256'],'hash_matches':digest==x['sha256'],'valid':actual,'passed':actual is True and digest==x['sha256']})
# Exact process-owner functions are unchanged from the actually executed 11f proofs.
oldtree=ast.parse((Q/'inputs/fixed11f-verify_p06.py.txt').read_text())
oldfunc={n.name:n for n in oldtree.body if isinstance(n,ast.FunctionDef)}
ownership=[]
for name in ['enable_subreaper','owned_descendants','live_descendants','stop_descendants','run_command']:
 a=ast.dump(functions[name],include_attributes=False);b=ast.dump(oldfunc[name],include_attributes=False)
 ownership.append({'name':name,'exact_AST_unchanged':a==b,'AST_sha256':hashlib.sha256(a.encode()).hexdigest()})
# Pure plan call. Validate every emitted option exists in actual child CLI AST.
plans=[]
for exports,movie,headless in [(False,False,False),(True,True,False),(False,False,True)]:
 stages=ns['plan'](Path('REPORT'),Path('BUILD'),exports,movie,headless); details=[]
 for name,argv,timeout in stages:
  script=W/str(argv[1]);childtree=ast.parse(script.read_text());declared={arg.value for n in ast.walk(childtree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' for arg in n.args if isinstance(arg,ast.Constant) and isinstance(arg.value,str) and arg.value.startswith('--')}
  emitted=[str(a) for a in argv[2:] if str(a).startswith('--')]
  details.append({'name':name,'argv':list(map(str,argv)),'timeout':timeout,'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),'unknown_options':sorted(set(emitted)-declared)})
 plans.append({'exports':exports,'movie':movie,'headless':headless,'stage_count':len(stages),'timeout_sum':sum(t for _,_,t in stages),'stages':details,'passed':len(stages)==(1 if headless else 13) and all(not x['unknown_options'] for x in details)})
summary={'scope':'PURE8E_PARSER_PLAN_AND_EXACT_PROCESS_FUNCTION_EQUIVALENCE','source_sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'parser_cases':rows,'real_report_compatibility':actual_reports,'process_function_equivalence':ownership,'plan_checks':plans,'engines_or_pipeline_or_Controller_invoked':False,'passed':all(x['passed'] for x in rows+actual_reports+plans) and all(x['exact_AST_unchanged'] for x in ownership)}
(Q/'pure-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'parser_cases':len(rows),'parser_failures':[x['name'] for x in rows if not x['passed']],'actual_reports':len(actual_reports),'report_failures':[x['id'] for x in actual_reports if not x['passed']],'process_functions_equal':all(x['exact_AST_unchanged'] for x in ownership),'plans_passed':[x['passed'] for x in plans],'passed':summary['passed']}))
