from pathlib import Path
import json,hashlib,subprocess,importlib.util,ast
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).parent
assert not (O/'own-parser-closure.json').exists()
old=subprocess.check_output(['git','-C',str(W),'show','11f0666d7f9c62896f57a3980c1c4b1d2c9eb1af:tools/verify_p06.py']).decode();new=subprocess.check_output(['git','-C',str(W),'show','8e17546f15a9ca563afbfa0fdd0ac9558f3eed30:tools/verify_p06.py']).decode();p=O/'frozen-8e-verify_p06.py';p.write_text(new)
fnames=['enable_subreaper','owned_descendants','live_descendants','stop_descendants','run_command'];ids=[]
for n in fnames:
 a=next(x for x in ast.parse(old).body if isinstance(x,ast.FunctionDef) and x.name==n);b=next(x for x in ast.parse(new).body if isinstance(x,ast.FunctionDef) and x.name==n);aa=ast.get_source_segment(old,a);bb=ast.get_source_segment(new,b);assert aa==bb;ids.append({'function':n,'source_segment_sha256':hashlib.sha256(aa.encode()).hexdigest(),'exact_to_11f':True})
s=importlib.util.spec_from_file_location('frozen8e_parser_under_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
q=R/'reports/phases/P06/qa-native-pipeline-preflight-02/report-boundary-results.json';cases=json.loads(q.read_text())['cases'];rows=[];D=O/'parser-fixtures';D.mkdir()
for c in cases:
 f=D/(c['name']+'.json');f.write_text(c['raw_JSON']+'\n');actual=m.valid_report(f);assert actual==c['expected_safe_acceptance'],(c['name'],actual);rows.append({'name':c['name'],'expected':c['expected_safe_acceptance'],'actual':actual})
real=[]
for k in ['attempt1/gabar-combat-native-02/validation.json','attempt1/olezhka-combat-native-01/validation.json','guard-feedback-01/native-03/validation.json','timka-present-01/native-02/validation.json','timka-prime-01/native-03/validation.json','ryzhik-roll-01/native-03/validation.json','tega-environment-01/native-03/validation.json','pasha-moving-shot-01/native-03/validation.json','attempt1/cast-native-02/validation.json','character-finisher-audio-01/native-02/validation.json','baseline-after-deferral-01/regression/validation.json','native-baseline-after-deferral-02/validation.json']:
 f=W/'reports/phases/P06'/k;actual=m.valid_report(f);expected=not k.startswith('native-baseline');assert actual==expected;real.append({'path':k,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'expected':expected,'actual':actual})
plan=m.plan(O/'out',O/'build',True,True);assert len(plan)==13 and not any(str(x)=='tools/verify.py' for _,args,_ in plan for x in args)
h=m.plan(O/'headless',O/'build',headless=True);assert len(h)==1 and h[0][0]=='headless_technical_only'
(O/'own-parser-closure.json').write_text(json.dumps({'scope':'DRAFT8E_SOURCE_PARSE_PLAN_CLOSURE_ONLY_NO_GO_PENDING_QA03','source_commit':'8e17546f15a9ca563afbfa0fdd0ac9558f3eed30','source_sha256':hashlib.sha256(new.encode()).hexdigest(),'five_process_functions_exact_to_independently_probed11f':ids,'unchanged_raw_QA02_parser_cases':rows,'real_child_report_format_controls':real,'native_plan_stages':[{'name':n,'argv':list(map(str,a)),'timeout':t} for n,a,t in plan],'headless_plan_separate':True,'source_freeze_main_logic_exact_to11f':ast.get_source_segment(new,next(x for x in ast.parse(new).body if isinstance(x,ast.FunctionDef) and x.name=='main'))==ast.get_source_segment(old,next(x for x in ast.parse(old).body if isinstance(x,ast.FunctionDef) and x.name=='main')),'process_probes_repeated':False,'Game_or_engine_or_controller_mutations':False},indent=2)+'\n')
print('8e own18rawparsercasesPASS,12realformatcontrolsPASS,5processfunctions exactto11f; noGOyet')
