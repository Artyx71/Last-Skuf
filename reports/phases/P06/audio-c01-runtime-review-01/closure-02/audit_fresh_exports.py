from pathlib import Path
import hashlib,json,sys
Q=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
def main():
 out=Q/'export-audit-01.json';assert not out.exists()
 frozen=read(Q/'export-input-freeze.json');checks=[]
 def check(ok,label):checks.append({'label':label,'passed':bool(ok)})
 for x in frozen['records']:check(sha(Path(x['path']))==x['sha256'],'actual exportinput preserved '+Path(x['path']).name)
 e=Q/'export-inputs';n=read(Q/'native-inputs/source_hashes_after.json');s=read(e/'source_hashes.json');common=set(n)&set(s);omitted=sorted(set(n)-set(s));diff=sorted(k for k in common if n[k]!=s[k])
 check(len(n)==1465 and len(s)==1363 and len(common)==1363 and not diff and not(set(s)-set(n)),'actual DEV08/native02 common1363sources allsame0dd')
 check(len(omitted)==102 and all(k.startswith('reports/phases/P06/audio-c01-signal-review-01/') or k.startswith('assets/source_audio/character_finishers/') for k in omitted),'explicit102archive/source_audio domain omissions; no Game omission')
 preview=read(e/'preview.json');commands=read(e/'commands.json');receipt=read(e/'root-job/receipt.json');inp=read(e/'root-job/input.json')
 check(receipt['operation']==frozen['operation'] and receipt['exit_code']==0 and receipt['argv_sha256']==inp['argv_sha256'] and sha(e/'root-job/output.log')==receipt['log_sha256'],'actual DEV08 canonical receipt/argv/log0')
 check(preview['source_head']=='0dd1cc4dad9379c457e277969b721fcc23a14fe3' and preview['source_unchanged'] is True and preview['passed'] is True and preview['phase_approval'] is False,'actual DEV08 exact0dd/prototype/unchanged')
 check(len(commands)==4 and preview['commands']==commands,'actual four export/smoke commands')
 for row in commands:
  log=e/(row['name']+'.log');check(row['exit_code']==0 and row['passed'] is True and sha(log)==row['log_sha256'] and log.read_text().rstrip().splitlines()[-1]=='exit_code=0','actual logreceipt '+row['name'])
 for platform,count in [('linux',81),('windows',72)]:
  result=read(e/(platform+'_smoke/result.json'));rows=result['checks'];check(len(rows)==count and result['passed'] is True and all(x['passed'] is True for x in rows),platform+' actual'+str(count)+' checks')
  check(sum(x['name'].startswith('exported_stream:') for x in rows)==20 and sum(x['name'].startswith('exported_playback_binding:') for x in rows)==20,platform+' actual20streams/20voicebindings')
 for row in read(e/'exports.json'):
  p=Path(frozen['work_root'])/row['path']
  with p.open('rb') as f:header=f.read(4096)
  valid=header[:4]==b'\x7fELF' if row['platform']=='Linux' else header[:2]==b'MZ' and header[int.from_bytes(header[60:64],'little'):][:4]==b'PE\x00\x00'
  check(valid and sha(p)==row['sha256'] and p.stat().st_size==row['bytes'] and row['runtime_smoke_passed'] is True,row['platform']+' actual packedbinary/SHA+recordedsmoke')
 check(len(list((e/'linux_smoke').glob('*.png')))==9,'nine actual nativeLinux PNG')
 output={'scope':'INDEPENDENT_READONLY_DEV08_HEADROOM_EXPORT_AUDIT_NOT_RERUN','passed':all(x['passed'] for x in checks),'checks':checks,'native_source_keys':len(n),'export_source_keys':len(s),'common_unchanged':len(common),'explicit_native_only102':omitted,'actual_new_export_or_engine_run_here':False,'native_Windows':'NOT_TESTED: actualPE/Wineheadless only','owner_prior_listening':'Originalf615solo/runtime prototypeacceptance remainshistorical; no claim ownerheardfresh0ddmix','full_phase_approval':False,'release_approval':False};out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'passed':output['passed'],'checks':len(checks)}));return 0 if output['passed'] else 1
if __name__=='__main__':sys.exit(main())
