from pathlib import Path
import json,hashlib,shutil,struct
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/owner-preview-20261115-04';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();preview=json.loads((B/'preview.json').read_text());source=json.loads((Q/'copy-inputs-closure.json').read_text());assert preview['passed'] and preview['source_unchanged'] and preview['source_head']=='9b42df871e53758b402108cb7cc00a2e385ab773' and json.loads((B/'source_hashes.json').read_text())==source
fixtures=['gabar_training','olezhka_training','timka_present','timka_prime'];assert preview['available_combat_fixtures']==fixtures and preview['available_combat_heroes']==['gabar','olezhka','timka']
for cmd in preview['commands']:assert cmd['passed'] and cmd['exit_code']==0 and h(B/(cmd['name']+'.log'))==cmd['log_sha256']
for exp in preview['exports']:
 p=W/exp['path'];assert h(p)==exp['sha256'] and p.stat().st_size==exp['bytes'] and exp['verified_combat_fixtures']==fixtures
 with p.open('rb') as f:
  prefix=f.read(64)
  if exp['platform']=='Linux':assert prefix[:4]==b'\x7fELF'
  else:
   assert prefix[:2]==b'MZ';f.seek(struct.unpack_from('<I',prefix,0x3c)[0]);assert f.read(4)==b'PE\0\0' and exp['native_windows']=='NOT_TESTED'
checks={}
for mode,count in [('linux_smoke',29),('windows_smoke',23)]:
 j=json.loads((B/mode/'result.json').read_text());assert j['passed'] and len(j['checks'])==count and all(c['passed'] for c in j['checks']);checks[mode]={'checks':count,'renderer':j['renderer'],'result_sha256':h(B/mode/'result.json')}
hand=json.loads((B/'owner-handoff.json').read_text());friendly=Path(hand['friendly_directory']);assert friendly.resolve()==(W/'build/P06/owner-preview-20261115-04').resolve()
for a in hand['files']:assert h(friendly/a['path'])==a['sha256'] and (friendly/a['path']).stat().st_size==a['bytes']
job=R/'.autopilot/jobs/2cf56a72721c4ec3bcdca03970106115';r=json.loads((job/'receipt.json').read_text());i=json.loads((job/'input.json').read_text());assert r['exit_code']==0 and r['log_sha256']==h(job/'output.log') and r['argv_sha256']==i['argv_sha256']
copies=[]
for name in ['preview.json','exports.json','owner-handoff.json','commands.json','linux_smoke/result.json','windows_smoke/result.json','linux_smoke/timka_prime.png','export_linux.log','export_windows.log','linux_smoke.log','windows_smoke.log']:
 s=B/name;d=Q/'DEV04-addendum'/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s,d);copies.append({'path':str(d.relative_to(Q)),'origin':str(s.relative_to(W)),'sha256':h(d)})
(Q/'DEV04-artifact-verification.json').write_text(json.dumps({'scope':'READONLY_DEV_PREVIEW_ARTIFACT_AND_SAVED_SMOKE_INSPECTION_ONLY','source_head':preview['source_head'],'all_source_inputs_exact':len(source),'exports':preview['exports'],'saved_actual_smokes':checks,'actual_available_combat_fixtures':preview['available_combat_fixtures'],'actual_available_combat_heroes':preview['available_combat_heroes'],'friendly_directory':str(friendly),'friendly_resolved':str(friendly.resolve()),'friendly_files_verified':len(hand['files']),'one_actual_packed_Linux_PNG_visually_inspected':'linux_smoke/timka_prime.png','producer_receipt':r,'actual_log_and_argv_SHA_match':True,'copies':copies,'no_independent_export_or_packed_smoke_rerun':True,'native_windows':'NOT_TESTED','release_approval':False,'phase_approval':False},indent=2)+'\n');print('DEV04 actual1112SourceSHA, ELF/PE SHA+magic, Linux29/Wine23, fixtures4/heroes3 andfriendly7files verified; no rerun')
