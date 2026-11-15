from pathlib import Path
import hashlib,json,sys
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def main():
 out=Q/'handoff-analysis-01.json';assert not out.exists()
 freeze=read(Q/'handoff-input-freeze.json');checks=[]
 def check(ok,label):checks.append({'label':label,'passed':bool(ok)})
 for row in freeze['records']:check(sha(Path(row['path']))==row['sha256'],'actual inputSHA '+Path(row['path']).name)
 root=Q/'handoff-inputs';e=root/'export';preview=read(e/'preview.json');exports=read(e/'exports.json');commands=read(e/'commands.json');handoff=read(e/'owner-handoff.json')
 receipt=read(root/'root-export-job/receipt.json');inp=read(root/'root-export-job/input.json')
 native_map=read(Q/'native-inputs/source_hashes_after.json');export_map=read(e/'source_hashes.json');delta={key for key in set(native_map)|set(export_map) if native_map.get(key)!=export_map.get(key)}
 check(delta=={'game/export_presets.cfg','game/scripts/qa/owner_preview_smoke.gd'},'actual source-map f615→5403 exactly exportfilter/smoke delta only')
 check(receipt['operation']==freeze['export_operation'] and receipt['exit_code']==0 and receipt['argv_sha256']==inp['argv_sha256'] and sha(root/'root-export-job/output.log')==receipt['log_sha256'],'actual canonical exportjob receipt/argv/log0')
 check(preview['source_head']=='5403faa837a32e0fd370bb374eace120c9c4426b' and preview['passed'] is True and preview['source_unchanged'] is True and preview['phase_approval'] is False,'DEV07 exact5403 source/unchanged/no phase')
 check(len(commands)==4 and preview['commands']==commands,'four actual commands equal previewrecords')
 for row in commands:
  log=e/(row['name']+'.log');check(row['exit_code']==0 and row['passed'] is True and sha(log)==row['log_sha256'] and log.read_text().rstrip().splitlines()[-1]=='exit_code=0','actual export/smoke command log0 '+row['name'])
 for platform,count,renderer in [('linux',81,'X11'),('windows',72,'headless')]:
  result=read(e/(platform+'_smoke/result.json'));rows=result['checks']
  check(len(rows)==count and all(x['passed'] is True for x in rows) and result['passed'] is True,platform+' actual '+str(count)+'checks')
  check(sum(x['name'].startswith('exported_stream:') for x in rows)==20 and sum(x['name'].startswith('exported_playback_binding:') for x in rows)==20,platform+' actual twenty importedstreams/twenty voicebindings')
  check(len(result['captures'])==(9 if platform=='linux' else 0),platform+' actual capturecount')
 for exported in exports:
  path=Path(freeze['work_root'])/exported['path'];header=path.read_bytes()[:4096]
  isbinary=header[:4]==b'\x7fELF' if exported['platform']=='Linux' else header[:2]==b'MZ' and header[int.from_bytes(header[60:64],'little'):][:4]==b'PE\x00\x00'
  check(isbinary and sha(path)==exported['sha256'] and path.stat().st_size==exported['bytes'] and exported['export_passed'] is True and exported['runtime_smoke_passed'] is True,exported['platform']+' actual packed executable/header/SHA and recorded smoke')
 check(len(list((e/'linux_smoke').glob('*.png')))==9,'nine actual exportedLinux PNGfiles')
 check(handoff['friendly_is_standalone_copy'] is True and handoff['source_head']==preview['source_head'] and handoff['native_windows']=='NOT_TESTED','actual standalone local handoff scoped no nativeWindows claim')
 owner=read(root/'owner-listening-acceptance.json')
 check(owner['owner_exact_answer']=='Прослушал, принимаю для прототипа P06' and owner['artistic_audio_status']=='OWNER_ACCEPTED_FOR_PROTOTYPE' and owner['owner_listening_reported'] is True and owner['agent_listening_performed'] is False,'owner reported prototype-only artistic acceptance distinctfromagent')
 check(set(owner['requested_listening'])=={'solo_cues.wav','runtime_mix.wav'} and owner['listened_stress_mix']=='NOT_EXPLICITLY_REPORTED' and owner['full_P06_approval'] is False and owner['commercial_release_approval'] is False,'owner listening scope exactly solo/runtime, stressnotexplicit/no phase orrelease')
 for item in owner['evidence']:check(sha(Path(freeze['work_root'])/item['path'])==item['sha256'],'owner exact bound audio/result '+Path(item['path']).name)
 result={'scope':'READONLY_ACTUAL_DEV07_EXPORT_AUDIT_AND_OWNER_REPORTED_LISTENING_ONLY','passed':all(x['passed'] for x in checks),'checks':checks,'actual_agent_playback_or_Godot_run_here':False,'agent_listening':False,'owner_artistic_report':'ACCEPTED_P06_PROTOTYPE_SOLO_AND_RUNTIME_ONLY','stress_artistic_listening':'NOT_EXPLICIT','native_Windows':'NOT_TESTED; actual WindowsPE underWineheadless only','full_phase_approval':False,'release_approval':False}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'scope':result['scope'],'passed':result['passed'],'checks':len(checks)}));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
