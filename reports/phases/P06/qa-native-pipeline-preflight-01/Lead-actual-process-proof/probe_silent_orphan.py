from pathlib import Path
import importlib.util,subprocess,sys,json,time,os,signal
O=Path(__file__).parent;s=importlib.util.spec_from_file_location('frozen454e_pipeline',O/'frozen-454e-verify_p06.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);m.ROOT=O
assert not (O/'silent-orphan-result.json').exists()
f=O/'silent_orphan_fixture.py';pidfile=O/'silent-child.json';f.write_text("import sys,subprocess,json\nfrom pathlib import Path\np=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\ns=(Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]\nPath(sys.argv[1]).write_text(json.dumps({'pid':p.pid,'start':s}))\n")
a=time.monotonic();ret=m.run_command([sys.executable,str(f),str(pidfile)],O/'silent-orphan-stage.log',1)
c=json.loads(pidfile.read_text());p=Path('/proc')/str(c['pid'])/'stat';t=p.read_text().rsplit(')',1)[1].split();alive=t[19]==c['start'] and t[0]!='Z'
if alive:os.kill(c['pid'],signal.SIGKILL)
d={'scope':'PURE_PYTHON_NO_ENGINE_NO_STATE','run_command':ret,'wall_seconds':time.monotonic()-a,'own_child':c,'child_ppid_after_success':int(t[1]),'child_still_running_after_reported_PASS':alive,'exact_own_child_cleanup_SIGKILL':alive}
(O/'silent-orphan-result.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
