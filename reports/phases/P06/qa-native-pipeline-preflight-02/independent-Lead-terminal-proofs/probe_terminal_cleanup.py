from pathlib import Path
import importlib.util,sys,json,subprocess,time,hashlib,os,signal
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).parent;src=subprocess.check_output(['git','-C',str(W),'show','11f0666d7f9c62896f57a3980c1c4b1d2c9eb1af:tools/verify_p06.py']);p=O/'frozen-11f-verify_p06.py';p.write_bytes(src)
s=importlib.util.spec_from_file_location('fix11f_under_test',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=O
assert not (O/'own-terminal-cleanup-proofs.json').exists()
rows=[]
for name,redirect,code,expected_exit in [('pipe_parent_exit0',False,0,124),('silent_parent_exit0',True,0,0),('silent_parent_exit7',True,7,7)]:
 case=O/name;case.mkdir();pidfile=case/'child.json';f=case/'wrapper.py';opts=',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL' if redirect else ''
 f.write_text("import sys,subprocess,json\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)']"+opts+")\ns=(Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]\nPath(sys.argv[1]).write_text(json.dumps({'pid':p.pid,'start':s}))\nsys.exit("+str(code)+")\n")
 start=time.monotonic();record=m.run_command([sys.executable,str(f),str(pidfile)],case/'stage.log',.2);child=json.loads(pidfile.read_text());stat=Path('/proc')/str(child['pid'])/'stat';live=False
 if stat.exists():
  parts=stat.read_text().rsplit(')',1)[1].split();live=parts[19]==child['start'] and parts[0]!='Z'
 if live:os.kill(child['pid'],signal.SIGKILL)
 assert not live and record['passed'] is False and record['exit_code']==expected_exit and record['descendant_cleanup']['remaining_live_children']==[],(name,record,live)
 rows.append({'case':name,'record':record,'seconds':time.monotonic()-start,'own_child_identity':child,'child_live_after_runner':live,'emergency_own_cleanup_needed':live})
control=m.run_command([sys.executable,'-c','print("ordinaryfixture")'],O/'positive.log',1);assert control['passed'] and not control['descendant_cleanup']['remaining_live_children']
(O/'own-terminal-cleanup-proofs.json').write_text(json.dumps({'scope':'SEPARATE_FIX11_CLOSURE_DRAFT_ONLY_NO_NATIVE_PERMISSION','commit':'11f0666d7f9c62896f57a3980c1c4b1d2c9eb1af','source_sha256':hashlib.sha256(src).hexdigest(),'negative_cases':rows,'valid_control':control,'engine_or_Game_or_state_mutations':False,'formal_QA2_and_Lead_final_pending':True},indent=2)+'\n')
print('11f3terminalorphanPASS inclnonzero, ordinarycontrolPASS; no childrenleft')
