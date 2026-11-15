"""Actual native03 read-only control + ROOT-only portable corruption fixtures. No engine."""
from pathlib import Path
import sys,json,hashlib,runpy,shutil,tempfile
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';sys.path.insert(0,str(Q/'isolated-project/tools'));mod=runpy.run_path(str(Q/'cache-fix-candidate-02/tools/verify_p06_timka_prime.py'),run_name='qa_frozen_final_recovery');G=mod['completed_live_evidence'].__globals__;source=json.loads((Q/'copy-inputs-accepted.json').read_text());live=W/'reports/phases/P06/timka-prime-01/native-03';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();results=[]
G['ROOT']=W;G['GODOT']=W/'.tools/godot'/Path(json.loads((Q/'engine-copy.json').read_text())['path']).name
assert json.loads((live/'source_hashes.json').read_text())==source
value=mod['completed_live_evidence'](live,source);results.append({'case':'actual_native03_positive_readonly','accepted':True,'value':value})
for label,path in [('old_native02_source_stale',W/'reports/phases/P06/timka-prime-01/native-02'),('original_native01_incomplete',W/'reports/phases/P06/timka-prime-01/native-01')]:
 try:value=mod['completed_live_evidence'](path,source);accepted=True;error=None
 except Exception as e:accepted=False;error=type(e).__name__+': '+str(e)
 assert not accepted;results.append({'case':label,'accepted':accepted,'error':error})
temporary=Q/'temporary-fixtures';temporary.mkdir(exist_ok=True)
for case in ['portable_positive','changed_PNG_bytes','contradictory_failed_commands','wrong_result_scope','capture_alias_duplicate','summary_counts_inflated','typed_commands_contradiction']:
 with tempfile.TemporaryDirectory(dir=temporary) as tmp:
  root=Path(tmp);folder=root/'reports/native';shutil.copytree(live,folder);G['ROOT']=root
  report=json.loads((folder/'validation.json').read_text());command=report['commands'][0];command['argv'][command['argv'].index('--path')+1]=str(root/'game');(folder/'commands.json').write_text(json.dumps(report['commands']))
  data=json.loads((folder/'live/result.json').read_text())
  for c in data['captures']:c['path']=str(folder/Path(c['path']).relative_to(live))
  (folder/'live/result.json').write_text(json.dumps(data))
  report['artifacts']=[{'path':str(p.relative_to(root)),'sha256':sha(p)} for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='validation.json']
  def rebind(p):
   for a in report['artifacts']:
    if root/a['path']==p:a['sha256']=sha(p)
  if case=='changed_PNG_bytes':
   p=folder/'live'/Path(data['captures'][0]['path']).name;p.write_bytes(p.read_bytes()+b'TEST_ONLY_changed')
  if case in ['contradictory_failed_commands','typed_commands_contradiction']:
   p=folder/'commands.json';records=json.loads(p.read_text());records[0]['passed']=False if case=='contradictory_failed_commands' else 1;records[0]['exit_code']=9 if case=='contradictory_failed_commands' else False;p.write_text(json.dumps(records));rebind(p)
  if case=='wrong_result_scope':data['scope']='WRONG_COMPONENT';data['phase_approval']=True
  if case=='capture_alias_duplicate':data['captures'].append(data['captures'][0]);report['actual_captures']+=1
  if case in ['wrong_result_scope','capture_alias_duplicate']:
   p=folder/'live/result.json';p.write_text(json.dumps(data));rebind(p)
  if case=='summary_counts_inflated':report['checks']=[{'passed':999,'total':999}]
  (folder/'validation.json').write_text(json.dumps(report))
  try:value=mod['completed_live_evidence'](folder,source);accepted=True;error=None
  except Exception as e:value=None;accepted=False;error=type(e).__name__+': '+str(e)
  assert accepted==(case=='portable_positive'),(case,accepted,error);results.append({'case':case,'accepted':accepted,'error':error,'control_is_explicit_path_rebased_copy_of_real_native03':True,'engine_invoked':False})
(Q/'real-recovery-probes.json').write_text(json.dumps({'scope':'ACTUAL_NATIVE03_READONLY_PLUS_ROOT_ISOLATED_CORRUPTION_FIXTURES','helper_sha256':sha(Q/'cache-fix-candidate-02/tools/verify_p06_timka_prime.py'),'source_map_sha256':sha(Q/'copy-inputs-accepted.json'),'native03_validation_sha256':sha(live/'validation.json'),'no_actual_native_or_WORK_artifact_mutation':True,'cases':results},indent=2)+'\n');print('PASS10/10 recoverycontrols: actual+portablepositive, stale/incomplete and6realdata corruptionfixtures reject; noengine')
