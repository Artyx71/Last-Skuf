import sys,subprocess,json
from pathlib import Path
p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(90)'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
s=(Path('/proc')/str(p.pid)/'stat').read_text().rsplit(')',1)[1].split()[19]
Path(sys.argv[1]).write_text(json.dumps({'pid':p.pid,'start':s}))
sys.exit(7)
