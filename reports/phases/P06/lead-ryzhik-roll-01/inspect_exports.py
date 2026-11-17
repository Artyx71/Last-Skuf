from pathlib import Path
import json,hashlib,subprocess,re,struct,shutil
from PIL import Image
OUT=Path(__file__).parent;ROOT=OUT.parents[3];WORK=ROOT/'.autopilot/worktrees/P06'
EV=WORK/'reports/phases/P06/owner-preview-20261115-05';FRIEND=ROOT/'build/P06_DEV_20261115_05'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
preview=json.loads((EV/'preview.json').read_text());exports=json.loads((EV/'exports.json').read_text());handoff=json.loads((EV/'owner-handoff.json').read_text())
assert preview['source_head']=='8ad1729984321fbd646e96bbe9762a8c4cca689e' and preview['passed'] is True and preview['phase_approval'] is False
assert sha(EV/'source_hashes.json')=='c9e6966c9521697ad3d4d12dde3681457a5b82220ce388d56f1631836efd1958'
assert (EV/'source_hashes.json').read_bytes()==(WORK/'reports/phases/P06/ryzhik-roll-01/native-03/source_hashes.json').read_bytes()
expected={'gabar_training','olezhka_training','ryzhik_training','timka_present','timka_prime'}
records=[]
for entry in exports:
 p=WORK/entry['path'];assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'];assert entry['export_passed'] is True and entry['runtime_smoke_passed'] is True
 assert set(entry['verified_combat_fixtures'])==expected
 with p.open('rb') as stream:
  header=stream.read(64)
  if entry['platform']=='Linux':assert header[:4]==b'\x7fELF';signature='ELF'
  else:
   assert header[:2]==b'MZ';stream.seek(struct.unpack_from('<I',header,60)[0]);assert stream.read(4)==b'PE\0\0';signature='PE'
 mode='linux' if entry['platform']=='Linux' else 'windows';d=json.loads((EV/(mode+'_smoke/result.json')).read_text());assert d['passed'] is True and d['phase_approval'] is False and d['full_combat_approval'] is False
 assert all(c['passed'] is True for c in d['checks']);assert d['renderer']==('X11' if mode=='linux' else 'headless')
 assert len(d['checks'])==(33 if mode=='linux' else 26)
 for cap in d['captures']:
  im=Image.open(cap);assert im.size==(640,360)
 records.append({'platform':entry['platform'],'sha256':entry['sha256'],'bytes':entry['bytes'],'signature':signature,'smoke_checks':len(d['checks']),'actual_PNG':len(d['captures']),'renderer':d['renderer'],'verified_fixtures':sorted(expected),'independent_engine_rerun':False})
for c in preview['commands']:
 p=EV/(c['name']+'.log');assert c['exit_code']==0 and c['passed'] is True and sha(p)==c['log_sha256']
 assert next(s for s in reversed(p.read_text().splitlines()) if s.strip())=='exit_code=0'
 assert not any(s in p.read_text() for s in ['SCRIPT ERROR','Parse Error','ERROR:'])
 if c['name'].startswith('export_'):
  stored=re.findall(r'Storing File: ([^\x1b\r\n]+)',p.read_text());assert stored and not any('/references/' in s or '/private/' in s or '.zip' in s for s in stored)
assert (FRIEND/'BUILD_MANIFEST.json').read_bytes()==(EV/'owner-handoff.json').read_bytes()
for e in handoff['files']:
 p=FRIEND/e['path'];assert p.is_file() and not p.is_symlink() and sha(p)==e['sha256'] and p.stat().st_size==e['bytes']
assert len(handoff['files'])==7
assert not FRIEND.is_symlink() and all(not p.is_symlink() for p in FRIEND.rglob('*'))
assert subprocess.run(['bash','-n',str(FRIEND/'PLAY_LINUX.sh')],capture_output=True).returncode==0
cmd=(FRIEND/'PLAY_WINDOWS.cmd').read_bytes();assert cmd.count(b'\r\n')==10 and b'profile\\windows' in cmd and b'--open-character-combat' in cmd
assert 'profile/linux' in (FRIEND/'PLAY_LINUX.sh').read_text()
job=ROOT/'.autopilot/jobs/aaafe45b97414c9aae22c3e991a7c9d3';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==sha(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
dest=OUT/'DEV05-evidence';dest.mkdir(exist_ok=True)
for name in ['preview.json','exports.json','owner-handoff.json','commands.json','linux_smoke/result.json','windows_smoke/result.json']:
 target=dest/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(EV/name,target)
for name in ['input.json','receipt.json','output.log']:shutil.copyfile(job/name,dest/('producer-'+name))
bindings=json.loads((OUT/'external-reference-bindings.json').read_text())
for parent in [EV,FRIEND]:
 for p in parent.rglob('*'):
  if p.is_file():bindings['references'].append({'root_relative_path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size})
(OUT/'external-reference-bindings.json').write_text(json.dumps(bindings,indent=2)+'\n')
proof={'source_head':preview['source_head'],'native03_exact_source_inventory_reused':True,'builds':records,'friendly_standalone_files_verified':7,'friendly_manifest_sha256':sha(FRIEND/'BUILD_MANIFEST.json'),'per_platform_profile_paths':True,'launcher_execution_by_reviewer':False,'actual_export_logs_no_private_reference_paths':True,'complete_pack_content_privacy_parser_performed':False,'producer_receipt':receipt,'native_Windows':'NOT_TESTED','release_approval':False,'linux_Ryzhik_PNG_viewed':True,'engine_rerun':False}
(OUT/'DEV05-proofs.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
