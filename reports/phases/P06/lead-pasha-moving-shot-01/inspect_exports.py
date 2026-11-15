from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,struct,re,shutil
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';E=W/'reports/phases/P06/owner-preview-20261115-06';F=R/'build/P06_DEV_20261115_06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preview=json.loads((E/'preview.json').read_text());exports=json.loads((E/'exports.json').read_text());handoff=json.loads((E/'owner-handoff.json').read_text())
assert preview['source_head']=='b359747361c6ac76ccfc0cc8ff262c8327cf33e4' and preview['passed'] is True and preview['phase_approval'] is False
assert (E/'source_hashes.json').read_bytes()==(W/'reports/phases/P06/pasha-moving-shot-01/native-03/source_hashes.json').read_bytes()
expected={'gabar_training','olezhka_training','timka_present','timka_prime','ryzhik_training','tega_training','pasha_training'};rows=[]
for e in exports:
 p=W/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'] and e['export_passed'] is True and e['runtime_smoke_passed'] is True and set(e['verified_combat_fixtures'])==expected
 with p.open('rb') as stream:
  b=stream.read(64)
  if e['platform']=='Linux':assert b[:4]==b'\x7fELF';signature='ELF'
  else:assert b[:2]==b'MZ';stream.seek(struct.unpack_from('<I',b,60)[0]);assert stream.read(4)==b'PE\0\0';signature='PE'
 mode='linux' if e['platform']=='Linux' else 'windows';d=json.loads((E/(mode+'_smoke/result.json')).read_text());assert d['passed'] is True and d['phase_approval'] is False and d['full_combat_approval'] is False and all(c['passed'] is True for c in d['checks'])
 assert d['renderer']==('X11' if mode=='linux' else 'headless') and len(d['checks'])==(40 if mode=='linux' else 31)
 for cap in d['captures']:assert Image.open(cap).size==(640,360)
 rows.append({'platform':e['platform'],'binary_sha256':e['sha256'],'bytes':e['bytes'],'header':signature,'actual_smoke_checks':len(d['checks']),'actual_PNG':len(d['captures']),'renderer':d['renderer'],'fixtures_verified':sorted(expected),'Lead_engine_rerun':False})
for c in preview['commands']:
 p=E/(c['name']+'.log');text=p.read_text();assert c['exit_code']==0 and c['passed'] is True and sha(p)==c['log_sha256'] and next(s for s in reversed(text.splitlines()) if s.strip())=='exit_code=0'
 assert not any(s in text for s in ['SCRIPT ERROR','Parse Error','ERROR:'])
 if c['name'].startswith('export_'):
  stored=re.findall(r'Storing File: ([^\x1b\r\n]+)',text);assert stored and not any('/references/' in s or '/private/' in s or '.zip' in s for s in stored)
assert (F/'BUILD_MANIFEST.json').read_bytes()==(E/'owner-handoff.json').read_bytes() and not F.is_symlink()
for e in handoff['files']:
 p=F/e['path'];assert p.is_file() and not p.is_symlink() and sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
assert len(handoff['files'])==7
assert subprocess.run(['bash','-n',str(F/'PLAY_LINUX.sh')],capture_output=True).returncode==0
assert 'profile/linux' in (F/'PLAY_LINUX.sh').read_text();cmd=(F/'PLAY_WINDOWS.cmd').read_bytes();assert cmd.count(b'\r\n')==10 and b'profile\\windows' in cmd and b'--open-character-combat' in cmd
j=R/'.autopilot/jobs/12ad28c4d60f49bbaec7a0a8e1cb2472';rec=json.loads((j/'receipt.json').read_text());inp=json.loads((j/'input.json').read_text());assert rec['exit_code']==0 and rec['log_sha256']==sha(j/'output.log') and rec['argv_sha256']==inp['argv_sha256']
dest=O/'DEV06-evidence';dest.mkdir(exist_ok=True)
for name in ['preview.json','exports.json','owner-handoff.json','commands.json','linux_smoke/result.json','windows_smoke/result.json']:
 p=dest/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(E/name,p)
for name in ['input.json','receipt.json','output.log']:shutil.copyfile(j/name,dest/('producer-'+name))
refs=[]
for p in E.rglob('*'):
 if p.is_file():refs.append({'root_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
for e in handoff['files']+[{'path':'BUILD_MANIFEST.json'}]:
 p=F/e['path'];refs.append({'root_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
(O/'DEV06-reference-bindings.json').write_text(json.dumps(refs,indent=2)+'\n')
(O/'DEV06-proofs.json').write_text(json.dumps({'source_head':preview['source_head'],'native03_source_map_byteexact':True,'actual_exports':rows,'standalone_copy_files_verified':7,'standalone_manifest_sha256':sha(F/'BUILD_MANIFEST.json'),'separate_per_platform_profiles_in_launchers':True,'existing_user_profiles_not_read_or_modified':True,'bash_syntax_only_checked':True,'launcher_execution_by_Lead':False,'export_logs_no_raw_reference_private_paths':True,'full_binary_PCK_privacy_parser_performed':False,'producer_receipt':rec,'native_Windows':'NOT_TESTED','release_approval':False,'new_full_combat_export_approval':False},indent=2)+'\n')
print(rows)
