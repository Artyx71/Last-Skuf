from pathlib import Path
import json,hashlib,shutil,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-full-gate-preflight-01';B=W/'reports/phases/P06'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
refs=read(O/'external-input-bindings.json')['records'];uni={x['root_relative_path']:x for x in refs}
def snap(p,label):
 d=O/'evidence-snapshot'/label;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,d);k=str(p.relative_to(R));uni[k]={'root_relative_path':k,'sha256':sha(p),'bytes':p.stat().st_size};return {'path':k,'sha256':sha(p)}
# Actual49, not only author count.
D=B/'baseline-after-deferral-01';summary=read(D/'validation.json');a=read(D/'source_hashes_before.json');z=read(D/'source_hashes_after.json');assert a==z and summary['passed'] is True and summary['commands_total']==49
suites=read(D/'regression/validation.json');assert len(suites)==49 and all(x['passed'] is True and x['exit_code']==0 for x in suites)
for x in suites:
 p=W/x['log'];t=p.read_text();assert t.rstrip().splitlines()[-1]=='exit_code=0' and not any(s in t for s in ['SCRIPT ERROR:','ERROR:','FAIL:','ObjectDB instances were leaked','resources still in use']);snap(p,'baseline49/logs/'+p.name)
for n in ['validation.json','source_hashes_before.json','source_hashes_after.json','regression/validation.json']:snap(D/n,'baseline49/'+n)
# Snapshot oldfailed and latestcompleted packets separately. Never overwrite oldFAIL with newclosure.
for ver in ['01','02']:
 D=B/('native-baseline-after-deferral-'+ver)
 for n in ['validation.json','full_replay.json','reduced_replay.json','source_hashes.json','audio_detailed.json','environment.json','p04_regression/validation.json']:
  if (D/n).is_file():snap(D/n,'native'+ver+'/'+n)
 for p in (D/'logs').glob('*.log'):snap(p,'native'+ver+'/logs/'+p.name)
D=B/'native-baseline-after-deferral-02';native=read(D/'validation.json');assert [x['name'] for x in native if not x['passed']]==['detailed_audio']
assert [x['name'] for x in read(B/'native-baseline-after-deferral-01/validation.json') if x.get('exit_code')==124]==['full_replay']
raw={}
for n in ['full_replay','reduced_replay']:
 d=read(D/(n+'.json'));assert d['passed'] is True and len(d['checks'])==413 and all(x['passed'] for x in d['checks']) and len(d['captures'])==218
 assert len(d['finishers'])==20 and len(d['ai'])==12 and d['performance']['samples']==600 and d['performance']['movie_maker'] is False
 raw[n]={'checks':413,'PNG':218,'FIN':20,'natural_AI_direction_cases':12,'performance':d['performance']}
oldfailed=read(D/'audio_detailed.json');assert [x['name'] for x in oldfailed['checks'] if not x['passed']]==['five_fresh_runtime_captures']
C=B/'audio-runtime-scope-closure-01';cl=read(C/'validation.json');assert cl['passed'] is True
for p in C.iterdir():
 if p.is_file():snap(p,'audio-scope-closure/'+p.name)
newaudio=read(C/'audio_detailed.json');assert all(x['passed'] for x in newaudio['checks'])
# Actualindependent7-pairresult, not promisedcounts.
Q=R/'reports/phases/P06/qa-baseline-coverage-after-deferral-01';n=read(Q/'supplement-01/result.json');assert n['passed'] and n['actual_input'] and len(n['cases'])==14 and len(n['checks'])==204 and all(x['passed'] for x in n['checks']) and len(n['captures'])==42
for k in ['factorized-coverage-proof.json','source-freeze.json','supplement-01/result.json','supplement-01/commands.json','independent-supplement-recheck.json','independent-runtime-scope-selector-results.json']:
 if (Q/k).is_file():snap(Q/k,'NPC-seven-pairs/'+k)
# Verify canonical producer inputs and actual logs for every supplied execution.
ops=['0dfb4296e9e74d2d8699e0e4622d37b2','0c81d8ef1a014d3a8215e61f33ba605a','eff2bf83ff07439898dd292821486bb3','fbf98588596a4b78885be613548e323d'];receipts=[]
for op in ops:
 D=R/'.autopilot/jobs'/op;r=read(D/'receipt.json');i=read(D/'input.json');assert r['argv_sha256']==i['argv_sha256'] and r['log_sha256']==sha(D/'output.log')
 for k in ['receipt.json','input.json','output.log']:snap(D/k,'receipts/'+op+'/'+k)
 receipts.append(r)
assert [x['exit_code'] for x in receipts]==[0,1,0,0]
# Currentruntimeisstill exact0dd; latehelpersaredeclaredchanges, not Gamechanges.
f=read(R/'reports/phases/P06/lead-character-finisher-audio-01/source-freeze.json');delta=[k for k,v in f['source_hashes'].items() if sha(W/k)!=v];assert delta==['tools/analyze_p04g_audio.py','tools/verify.py','tools/verify_p04.py','tools/verify_p04g.py']
put('current-facts.json',{'WORK_head_at_snapshot':subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip(),'Game_assets_SourceAudio_exact0dd':True,'recorded0dd_source_keys':1465,'recorded_changed_only_helpers':delta,'headless49_actual_pass':True,'native01_Full_timeout_preserved':True,'native02_actual':raw,'native02_outer_exit1_due_only_to_capture_scope_gate':True,'pure_scope_closure_exit0_not_oldjobPASS':True,'NPC_supplement_actual_cases':14,'NPC_supplement_actual_assertions':204,'NPC_supplement_actualPNG':42,'independent_QA_final_fullgate_review':'PENDING_AT_PREFLIGHT','actual_Lead_engines_run':0,'new_full_verifier_implemented_or_accepted_by_this_review':False,'canonical_receipts':receipts})
put('external-input-bindings.json',{'base':'ROOT','records':list(uni.values()),'binding_to_exact_snapshots_not_future_modified_reports':True})
print('EVIDENCE_SNAPSHOT_COMPLETE refs',len(uni),'currentnewnativeFullReduced413+413, oldjobexit1+pureclosure0, NPC204actual')
