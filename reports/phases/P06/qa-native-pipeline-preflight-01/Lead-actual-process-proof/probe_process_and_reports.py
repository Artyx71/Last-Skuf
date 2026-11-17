from pathlib import Path
import importlib.util,sys,json,subprocess,time,os,signal,hashlib,traceback
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-native-pipeline-preflight-01';P=W/'tools/verify_p06.py'
assert not (O/'own-probe-result.json').exists()
s=importlib.util.spec_from_file_location('frozen_pipeline_under_test',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=O
inputs={'source':str(P),'sha256':hashlib.sha256(P.read_bytes()).hexdigest(),'head':subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip()};(O/'probe-input.json').write_text(json.dumps(inputs,indent=2)+'\n')
# All spawned programs are local Python sleep fixtures. No engine, Controller, Game or existing userstate.
wrapper=O/'orphan_fixture.py';pidfile=O/'fixture-child.json'
wrapper.write_text("import subprocess,sys,json\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)'])\ns=Path('/proc')/str(p.pid)/'stat'\nPath(sys.argv[1]).write_text(json.dumps({'pid':p.pid,'start':s.read_text().rsplit(\")\",1)[1].split()[19]}))\n# Parent exits immediately; child inherits the stage stdout pipe.\n")
start=time.monotonic();thrown=None;ret=None
try:
 ret=m.run_command([sys.executable,str(wrapper),str(pidfile)],O/'orphan-stage.log',.20)
except BaseException as e:
 thrown={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
finally:
 child=json.loads(pidfile.read_text());p=Path('/proc')/str(child['pid'])/'stat';alive=False;before=None
 if p.exists():
  st=p.read_text().rsplit(')',1)[1].split();before={'state':st[0],'ppid':int(st[1]),'start':st[19]};alive=st[19]==child['start'] and st[0]!='Z'
 if alive:os.kill(child['pid'],signal.SIGKILL)
 orphan={'wall_seconds':round(time.monotonic()-start,3),'returned_result':ret,'exception':thrown,'synthetic_child':child,'child_stat_after_runner':before,'synthetic_child_still_running_after_timeout':alive,'own_cleanup_SIGKILL_only_exact_child_start_identity':alive,'Godot_or_controller_used':False}
# Boundary validation probes: nonfinite/duplicates/contradictorynestedexit vs rejectedboolean values.
rows=[]
base={'passed':True,'commands':[{'passed':True,'exit_code':0}],'phase_approval':False,'source_unchanged':True}
texts={
 'valid_current_minimal':json.dumps(base),
 'duplicate_contradictory_pass':'{"passed":false,"passed":true,"commands":[{"passed":true}],"phase_approval":false,"source_unchanged":true}',
 'nonfinite_numeric':json.dumps({**base,'runtime_checks':float('nan')}),
 'contradictory_nested_exit':json.dumps({**base,'commands':[{'passed':True,'exit_code':1}]}),
 'empty_legacy_list':'[]',
 'vacuous_named_legacy_stage':'[{"passed":true}]',
 'string_pass':json.dumps({**base,'passed':'true'})}
for name,text in texts.items():
 p=O/(name+'.json');p.write_text(text+'\n');rows.append({'fixture':name,'accepted':m.valid_report(p),'path':str(p.relative_to(O))})
result={'scope':'INDEPENDENT_PURE_PROCESS_TREE_AND_REPORT_BOUNDARIES_NO_ENGINES','input':inputs,'orphan_probe':orphan,'report_probes':rows,'production_or_state_writes':False}
(O/'own-probe-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'orphan_live':alive,'exception_type':thrown['type'] if thrown else None,'seconds':orphan['wall_seconds'],'report_probes':rows},indent=2))
