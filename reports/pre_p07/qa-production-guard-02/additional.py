"""Extra v2 branch probes in temporary Git fixtures only."""
from pathlib import Path
import sys,json,copy,shutil
O=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(O/'isolated-source/tools/tests'));import test_production_readiness as tests
from readiness import require_p07_production,ReadinessBlocked
from runner import Controller,DEFAULT_PHASES,Blocked
rows=[]
def run(name,mutate,expected=False):
 t=tests.ProductionReadinessTests();t.setUp()
 try:
  mutate(t);before=copy.deepcopy(t.state)
  try:result=require_p07_production(t.root,t.state);accepted=True;error=None
  except ReadinessBlocked as e:accepted=False;error=str(e)
  row={'name':name,'expected_acceptance':expected,'accepted':accepted,'state_unchanged':before==t.state,'error':error};row['passed']=accepted==expected and row['state_unchanged'];rows.append(row);assert row['passed'],row
 finally:t.tearDown()
def change(t,scope,key,value):getattr(t,scope)[key]=value;t.publish()
for scope in ['ready','designs']:
 run(scope+':schema_float',lambda t,s=scope:change(t,s,'schema',1.0))
 run(scope+':blank_reviewer',lambda t,s=scope:change(t,s,'reviewer',' \t '))
 run(scope+':numeric_independence',lambda t,s=scope:change(t,s,'independent_of_author',1))
 run(scope+':trimmed_lower_HIGH_OPEN',lambda t,s=scope:change(t,s,'findings',[{'severity':' high \t','status':'OPEN'}]))
 run(scope+':missing_LOW_resolution',lambda t,s=scope:change(t,s,'findings',[{'severity':'LOW'}]))
 run(scope+':normalized_HIGH_VERIFIED_control',lambda t,s=scope:change(t,s,'findings',[{'severity':' high \t','status':'VERIFIED'}]),True)
def leaf_link(t):
 p=t.root/'reports/pre_p07/TEST_ONLY/readiness.json';dest=p.with_name('readiness-actual.json');p.rename(dest);p.symlink_to(dest)
run('same_bytes_internal_decision_leaf_symlink',leaf_link)
def inventory_link(t):
 real=t.root/'planning/input-actual.txt';real.write_text('TEST_ONLY source input');link=real.with_name('input-link.txt');link.symlink_to(real);t.ready['source_inventory_sha256']['planning/input-link.txt']=tests.sha(link);t.publish()
run('same_bytes_internal_inventory_file_symlink',inventory_link)
# Failed resume must preserve an existing worktree/attempt/checkpoint as well.
t=tests.ProductionReadinessTests();t.setUp()
try:
 work=t.root/'.autopilot/worktrees/P07';work.mkdir(parents=True);marker=work/'author-progress.txt';marker.write_text('preserve unfinished test work');t.state['autopilot']['phases']['P07'].update(status='IMPLEMENTING',checkpoint='validation',attempts=1,workspace=str(work));del t.state['autopilot']['production_gates']['readiness'];before=copy.deepcopy(t.state);controller=object.__new__(Controller);controller.root=t.root;controller.phases=DEFAULT_PHASES;controller.state=lambda:t.state;blocked=False
 try:controller.prerequisite('P07')
 except Blocked:blocked=True
 passed=blocked and before==t.state and marker.read_text()=='preserve unfinished test work';rows.append({'name':'resume_missing_gate_blocks_without_reset','passed':passed,'state_unchanged':before==t.state,'workspace_marker_preserved':True});assert passed
finally:t.tearDown()
(O/'additional-results.json').write_text(json.dumps({'schema':1,'scope':'ISOLATED_TEMP_ONLY','cases':rows,'passed':all(r['passed'] for r in rows)},indent=2)+'\n');print(json.dumps(rows,indent=2))
