import os,sys,json,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'autopilot'))
from runner import Controller,utc
c=Controller();w=c.root/'.autopilot/worktrees/P06'
with c.exclusive():
 s=c.reconcile();p=s['autopilot']['phases']['P06'];assert p['status']=='IMPLEMENTING' and p['attempts']==1
 op=s['autopilot'].get('operation');assert not op or op.get('consumed')
 old=s['autopilot'].get('active_author');assert not old or old.get('ended_at')
 saved_checkpoint=p.get('checkpoint','P06-resume-existing-work')
 s['autopilot']['active_author']={'pid':os.getpid(),'phase':'P06','attempt':1,'kind':'sole host author with built-in imagegen','safe_retry':False,'started_at':utc(),'worktree':str(w),'checkpoint':saved_checkpoint}
 s['autopilot']['history'].append({'when':utc(),'event':'P06_HOST_AUTHOR_RESUMED','attempt':1,'previous_native':op['id'] if op else None});c.persist(s)
 print('SOLE_HOST_AUTHOR_LEASE_HELD P06 attempt1 pid='+str(os.getpid()),flush=True)
 for line in sys.stdin:
  command=json.loads(line);event=command.get('event')
  s=c.state();p=s['autopilot']['phases']['P06'];a=s['autopilot']['active_author'];assert a['pid']==os.getpid()
  head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=w,text=True).strip()
  if event=='checkpoint':
   p['checkpoint']=command['name'];p['last_commit']=head;a.update(checkpoint=command['name'],updated_at=utc());s['last_commit']=head
   next_hint=command.get('details',{}).get('next_action')
   if isinstance(next_hint,str) and next_hint.strip():s['next_action']=next_hint
   s['autopilot']['history'].append({'when':utc(),'event':'P06_HOST_CHECKPOINT','name':command['name'],'source_head':head,'details':command.get('details',{})});c.persist(s);print('CHECKPOINT_SAVED '+head,flush=True)
  elif event=='release':
   a.update(ended_at=utc(),outcome=command['reason']);p['last_commit']=head;s['last_commit']=head;c.persist(s);print('AUTHOR_LEASE_RELEASED '+head,flush=True);break
  else:raise ValueError('Allowed host events: checkpoint/release only; author cannot issue phase verdict')
 else:
  s=c.state();s['autopilot']['active_author'].update(ended_at=utc(),outcome='INTERRUPTED_NO_BLIND_RETRY');c.persist(s)
