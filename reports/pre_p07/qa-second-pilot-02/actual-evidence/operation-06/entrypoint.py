from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parents[1];W=R/'.autopilot/worktrees/P07'
for script,name,native in [('p07_second_pilot.py','second-pilot-06',True),('p07_navigation_contract.py','navigation-contract-after-shortcut-01',False),('p07_room_pilot.py','room-pilot-after-shortcut-01',True)]:
 argv=[sys.executable,str(W/'tools'/script),'--output',str(W/'reports/pre_p07'/name)]
 if native:argv.append('--native')
 subprocess.run(argv,cwd=W,check=True)
