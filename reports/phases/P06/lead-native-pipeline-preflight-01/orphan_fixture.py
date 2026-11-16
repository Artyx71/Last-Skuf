import subprocess,sys,json
from pathlib import Path
p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)'])
s=Path('/proc')/str(p.pid)/'stat'
Path(sys.argv[1]).write_text(json.dumps({'pid':p.pid,'start':s.read_text().rsplit(")",1)[1].split()[19]}))
# Parent exits immediately; child inherits the stage stdout pipe.
