from pathlib import Path
import json,hashlib,subprocess,shutil,struct
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/owner-preview-20261115-03';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head='f66995892c8fdf8782e389a76c8ff05d628714d0';prior='2780e9e2a8e177e88b892d6abe91d9e141bf04de';changed=subprocess.check_output(['git','diff','--name-only',prior+'..'+head,'--','game'],cwd=W,text=True).splitlines();assert changed==['game/scripts/qa/owner_preview_smoke.gd']
inv=json.loads((Q/'copy-inputs.json').read_text());actual=json.loads((B/'source_hashes.json').read_text());assert actual.keys()==inv.keys();diff=[k for k in actual if actual[k]!=inv[k]];assert diff==changed
smoke=subprocess.check_output(['git','show',head+':'+changed[0]],cwd=W);assert hashlib.sha256(smoke).hexdigest()==actual[changed[0]]
d=Q/'dev03-addendum';d.mkdir(exist_ok=True);(d/'owner_preview_smoke.gd').write_bytes(smoke)
preview=json.loads((B/'preview.json').read_text());assert preview['passed'] and preview['source_unchanged'] and preview['source_head']==head
for c in preview['commands']:
 assert c['passed'] and c['exit_code']==0 and h(B/(c['name']+'.log'))==c['log_sha256']
exports=[]
for e in preview['exports']:
 p=W/e['path'];assert h(p)==e['sha256'] and p.stat().st_size==e['bytes'];b=p.read_bytes()
 if e['platform']=='Linux':assert b[:4]==b'\x7fELF'
 else:assert b[:2]==b'MZ' and b[struct.unpack_from('<I',b,0x3c)[0]:][:4]==b'PE\0\0'
 exports.append(e)
checkcounts={}
for mode,count in [('linux_smoke',26),('windows_smoke',21)]:
 j=json.loads((B/mode/'result.json').read_text());assert j['passed'] and len(j['checks'])==count and all(c['passed'] for c in j['checks']);checkcounts[mode]=count
 for check in ['present_Timka_selects_own_context_and_body','present_disengage_starts_from_Input','present_disengage_moves_without_prime_damage','unready_prime_preserves_present_context']:assert any(c['name']==check and c['passed'] for c in j['checks'])
hand=json.loads((B/'owner-handoff.json').read_text());friendly=Path(hand['friendly_directory']);target=W/'build/P06/owner-preview-20261115-03';assert friendly.resolve()==target.resolve()
for a in hand['files']:assert h(friendly/a['path'])==a['sha256'] and (friendly/a['path']).stat().st_size==a['bytes']
copies=[]
for name in ['preview.json','exports.json','owner-handoff.json','commands.json','linux_smoke/result.json','windows_smoke/result.json','linux_smoke/timka_present.png','export_linux.log','export_windows.log','linux_smoke.log','windows_smoke.log']:
 s=B/name;p=d/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s,p);copies.append({'path':str(p.relative_to(Q)),'origin':str(s.relative_to(W)),'sha256':h(p)})
job=R/'.autopilot/jobs/738b87f6a425418fbffa06d62e9d8cb9';receipt=json.loads((job/'receipt.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log')
(Q/'dev03-artifact-verification.json').write_text(json.dumps({'scope':'READ_ONLY_DEV03_ARTIFACT_AND_SAVED_SMOKE_INSPECTION_ONLY','source_head':head,'changes_from_reviewed2780_game':changed,'source_inventory_diff':diff,'source_inventory_count':len(actual),'exports':exports,'actual_saved_smoke_counts':checkcounts,'friendly_files_verified':len(hand['files']),'friendly_resolves_to':str(friendly.resolve()),'selected_actual_linux_png_visually_inspected':'linux_smoke/timka_present.png','producer_receipt':receipt,'producer_actual_log_sha256':h(job/'output.log'),'copies':copies,'no_independent_export_or_packed_runtime_rerun':True,'native_windows':'NOT_TESTED','phase_approval':False,'release_approval':False,'metadata_note':{'severity':'LOW','path':'preview.json/available_combat_heroes','actual':preview['available_combat_heroes'],'issue':'Saved preview list omits Timka present despite actual26/21 smoke and handoff new_feature. Requires explicit metadata erratum; does not invalidate binary/runtime observations.'}},ensure_ascii=False,indent=2)+'\n')
print('Verified DEV03 f669 game delta1/source1108, ELF+PE SHA, Linux26/Wine21 saved smoke, friendly7files, receipt log; no rerun/no nativeWindows claim')
