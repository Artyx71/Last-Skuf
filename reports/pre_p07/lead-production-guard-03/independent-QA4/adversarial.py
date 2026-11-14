"""Independent malicious/malformed fixtures. No production state is opened."""
from pathlib import Path
import sys,tempfile,json,copy,shutil
O=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(O/'isolated-source/tools/tests'));import test_production_readiness as tests
from readiness import require_p07_production,ReadinessBlocked
from runner import Controller,DEFAULT_PHASES
rows=[]
def evaluate(t):
 before=copy.deepcopy(t.state)
 try:r=require_p07_production(t.root,t.state);out={'accepted':True,'result':r}
 except Exception as e:out={'accepted':False,'error_type':type(e).__name__,'error':str(e)}
 out['state_unchanged']=t.state==before
 return out

def case(name,fn):
 t=tests.ProductionReadinessTests();t.setUp()
 try:row={'name':name,'scope':'TEMP_GIT_TEST_ONLY'};row.update(fn(t));rows.append(row)
 finally:t.tearDown()

def untracked_dir_link(t):
 with tempfile.TemporaryDirectory(prefix='outside-game-',dir=O/'tmp') as td:
  external=Path(td);(external/'unreviewed.gd').write_text('TEST_ONLY unreviewed source reachable via game symlink\n');link=t.root/'game/untracked_link';link.symlink_to(external,target_is_directory=True);t.publish();out=evaluate(t);out.update({'unreviewed_resource_is_readable':(link/'unreviewed.gd').read_text().startswith('TEST_ONLY'),'link_is_not_in_inventory':'game/untracked_link/unreviewed.gd' not in t.ready['source_inventory_sha256'],'expected':'BLOCK_UNTRACKED_PRODUCTION_SYMLINK'});return out
case('untracked_game_directory_symlink_with_unreviewed_source',untracked_dir_link)

def escaped_report_base(t):
 with tempfile.TemporaryDirectory(prefix='outside-repo-report-',dir=O/'tmp') as td:
  outside=Path(td)/'pre_p07';folder=t.root/'reports/pre_p07';shutil.move(str(folder),outside);folder.symlink_to(outside,target_is_directory=True);out=evaluate(t);out.update({'decision_resolves_outside_fixture_repository':not (folder/'TEST_ONLY/readiness.json').resolve().is_relative_to(t.root),'expected':'BLOCK_ESCAPED_REPORT_EVIDENCE'});return out
case('reports_pre_p07_prefix_symlink_escapes_repository',escaped_report_base)

def findings(t,value):
 t.ready['findings']=[{'severity':value,'status':'OPEN'}];t.publish();return evaluate(t)|{'severity':value,'expected':'BLOCK_MALFORMED_OR_OPEN_HIGH_FINDING'}
for value in ['HIGH ',None,{'priority':'HIGH'}]:case('malformed_finding_severity_'+str(value),lambda t,v=value:findings(t,v))

def boolean_schema(t):t.ready['schema']=True;t.publish();return evaluate(t)|{'expected':'BLOCK_UNKNOWN_BOOLEAN_SCHEMA'}
case('boolean_decision_schema',boolean_schema)

def correct_high(t):t.ready['findings']=[{'severity':'HIGH','status':'OPEN'}];t.publish();return evaluate(t)|{'expected':'BLOCK_OPEN_HIGH_CONTROL'}
case('exact_HIGH_open_control',correct_high)

def symlink_mds(t):
 path=t.root/'planning/CH21.md';path.unlink();path.symlink_to(t.root/'planning/CH20.md');h=tests.sha(path);t.designs['mission_specs']['CH21']['sha256']=h;t.designs['source_inventory_sha256']['planning/CH21.md']=h;t.publish();return evaluate(t)|{'expected':'BLOCK_DUPLICATED_MDS_SYMLINK'}
case('same_MDS_via_symlink_control',symlink_mds)

def escaped_inventory(t):
 t.ready['source_inventory_sha256']['../outside']='0'*64;t.publish();return evaluate(t)|{'expected':'BLOCK_ESCAPED_INVENTORY_PATH'}
case('direct_inventory_escape_control',escaped_inventory)

def resume(t):
 workspace=t.root/'.autopilot/worktrees/P07';(workspace/'game').mkdir(parents=True);(workspace/'game/combat.gd').write_text('AUTHORIZED_P07_WORK_IN_PROGRESS_TEST_ONLY\n');record=t.state['autopilot']['phases']['P07'];record.update(status='IMPLEMENTING',checkpoint='validation',attempts=1,workspace=str(workspace));before=copy.deepcopy(t.state);controller=object.__new__(Controller);controller.root=t.root;controller.phases=DEFAULT_PHASES;controller.state=lambda:t.state
 try:controller.prerequisite('P07');accepted=True;error=None
 except Exception as e:accepted=False;error=repr(e)
 return {'accepted':accepted,'error':error,'state_unchanged':before==t.state,'expected':'ALLOW_VALID_FROZEN_ROOT_WITH_P07_WORKSPACE_PROGRESS_NO_RESET'}
case('legitimate_P07_worktree_progress_resume_control',resume)
(O/'adversarial-results.json').write_text(json.dumps({'schema':1,'records':rows,'real_controller_state_or_GitHub_actions':False},indent=2)+'\n');print(json.dumps(rows,indent=2))
