"""TEST_ONLY fixtures: no Godot/renderer/controller/process execution."""
from pathlib import Path
import sys,json,hashlib,tempfile
Q=Path(__file__).resolve().parent;(Q/'temporary-fixtures').mkdir(exist_ok=True);tempfile.tempdir=str(Q/'temporary-fixtures');sys.path.insert(0,str(Q/'isolated-project/tools'));sys.path.insert(0,str(Q/'code-freeze-final/tools/tests'));import test_p06_prime_recovery as test
results=[]
for name in ['baseline_toy','contradictory_failed_commands_file','wrong_result_scope','duplicate_capture_aliases','summary_count_mismatch']:
 t=test.CompletedLiveRecoveryTest();t.setUp()
 try:
  def rebind(relative):
   for a in t.report['artifacts']:
    if a['path']==str((t.folder/relative).relative_to(t.root)):a['sha256']=test.replay.sha(t.folder/relative)
  if name=='contradictory_failed_commands_file':
   t.write('commands.json',[{'name':'live','passed':False,'exit_code':9,'argv':t.report['commands'][0]['argv']}]);rebind('commands.json')
  if name=='wrong_result_scope':
   data=json.loads((t.folder/'live/result.json').read_text());data['scope']='GABAR_DIFFERENT_COMPONENT';data['phase_approval']=True;t.write('live/result.json',data);rebind('live/result.json')
  if name=='duplicate_capture_aliases':
   data=json.loads((t.folder/'live/result.json').read_text());data['captures']*=2;t.report['actual_captures']=2;t.write('live/result.json',data);rebind('live/result.json')
  if name=='summary_count_mismatch':t.report['checks']=[{'passed':999,'total':999}]
  t.save_report()
  try:value=t.validate();accepted=True;error=None
  except Exception as exc:value=None;accepted=False;error=repr(exc)
  results.append({'case':name,'accepted':accepted,'return':value,'error':error,'TOY_FIXTURE_NOT_NATIVE':True})
 finally:t.doCleanups()
(Q/'cache-consistency-probes.json').write_text(json.dumps({'scope':'TEST_ONLY_PURE_HELPER_CONSISTENCY_PROBES','source_sha256':hashlib.sha256((Q/'code-freeze-final/tools/verify_p06_timka_prime.py').read_bytes()).hexdigest(),'actual_native_or_engine_executed':False,'results':results},indent=2)+'\n');print(json.dumps([{'case':r['case'],'accepted':r['accepted']} for r in results]))
