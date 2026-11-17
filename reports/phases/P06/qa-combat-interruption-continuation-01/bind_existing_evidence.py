from pathlib import Path
import hashlib,json,subprocess,sys
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';Q=Path(__file__).resolve().parent;O=W/'reports/phases/P06/combat-movie-recovery-01';C=O/'combat_baseline';J=R/'.autopilot/jobs/5766e682ba6546a0b4eb0dab35cca6be'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rd(p):return json.loads(p.read_text())
def wr(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks=[]
def ck(ok,label,details=None):checks.append({'name':label,'passed':bool(ok),'details':details})
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip();ck(head=='fa8693a36eaba56825f02ef74c09bbec38050a35','actual current full HEADfa869')
receipt=rd(J/'receipt.json');inp=rd(J/'input.json');ck(receipt['operation']=='5766e682ba6546a0b4eb0dab35cca6be' and receipt['exit_code']==130 and receipt['argv_sha256']==inp['argv_sha256'] and sha(J/'output.log')==receipt['log_sha256']=='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855','actual interrupted receipt130/empty canonical log retained',receipt)
before=rd(O/'source_hashes_before.json');current={str(p.relative_to(W)):sha(p) for folder in ['game','tools','assets/source_audio','assets/source_art/characters'] for p in sorted((W/folder).rglob('*')) if p.is_file() and '.godot' not in p.parts and '__pycache__' not in p.parts};ck(before==current,'actual full current inventory equals interrupted prelaunch inventory',len(current));wr(Q/'current-source-inventory.json',current)
contract=W/'reports/phases/P06/native-continuation-contract-02/contract.json';ck(sha(contract)=='e5ef81ddc24fc12420cc602c403deefe5cb8891961b2e985d85c64e53515a343','actual approved contract02 unchanged');refs=rd(contract)['artifacts'];rehashed=[{'path':r['path'],'sha256':sha(W/r['path']),'expected':r['sha256']} for r in refs];ck(len(refs)==905 and all(x['sha256']==x['expected'] for x in rehashed),'actual905 old proof pins unchanged');wr(Q/'prior-905-binding.json',rehashed)
raw=rd(C/'validation.json');ck(len(raw)==30 and all(x['passed'] is True for x in raw),'actual30 saved completed C5 wrapper rows allPASS (not32)',[x['name'] for x in raw]);ck(not (O/'validation.json').exists() and not (O/'source_hashes_after.json').exists() and not (C/'artifacts.json').exists(),'actual missing final wrapper/sourceafter/artifacts not invented')
results={}
for name in ['full_replay','reduced_replay','movie_replay','linux_export_replay','wine_export_replay']:
 d=rd(C/(name+'.json'));perf=d['performance'];ck(d['passed'] is True and len(d['checks'])==413 and all(x['passed'] is True for x in d['checks']) and len(d['captures'])==218 and perf['samples']==600,'actual completed413checks/218captures/600summary '+name)
 ck((C/(name+'.wav')).is_file() and (C/(name+'.json')).is_file(),'actual completed PCM/trace '+name);results[name]={'report_sha256':sha(C/(name+'.json')),'PCM_sha256':sha(C/(name+'.wav')),'performance':perf,'passed':True,'checks':413,'captures':218}
p04=rd(C/'p04_regression/validation.json');ck(len(p04)==4 and all(x['passed'] is True for x in p04),'actual partial P04 only first4engine rows positive, remaining obligations absent')
clips=[x for x in raw if x['name'].startswith('clip_')];ck(len(clips)==5 and all(x.get('exit_code')==0 and x['passed'] is True for x in clips),'actual five category clip encode commands0')
probe=subprocess.run(['/usr/bin/ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration','-of','json',str(C/'combat_polish.mp4')],capture_output=True,text=True,timeout=30);meta=json.loads(probe.stdout);stream=meta['streams'][0];ck(probe.returncode==0 and int(stream['nb_frames'])==5237 and abs(float(stream['duration'])-87.283333)<.001,'actual completed MP4 container5237frames/87.2833s (metadata, not full decode)',meta)
completed=[]
for p in sorted(C.rglob('*')):
 if p.is_file() and 'p04_regression' not in p.relative_to(C).parts and p.name!='native_p04_regression.log':completed.append({'path':str(p.relative_to(W)),'bytes':p.stat().st_size,'sha256':sha(p)})
for e in rd(C/'exports.json'):
 p=W/e['path'];ck(sha(p)==e['sha256'] and p.stat().st_size==e['bytes'],'actual completed export binding '+e['platform']);completed.append({'path':e['path'],'bytes':e['bytes'],'sha256':sha(p)})
wr(Q/'completed-C5-inventory.json',{'scope':'COMPLETED_C5_ONLY_EXCLUDING_PARTIAL_NESTED_P04_AND_ITS_LOG','records':completed,'count':len(completed)})
ck(all((W/r['path']).is_file() and sha(W/r['path'])==r['sha256'] for r in completed),'completed C5 physical files stable across binding')
ck(subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()==head,'HEAD stable across read-only binding')
wr(Q/'actual-binding-result.json',{'scope':'SHORT_PURE_COMPLETED_EVIDENCE_AND_CONTINUATION_BIND_ONLY','passed':all(x['passed'] for x in checks),'checks':checks,'captured_head':head,'actual_source_keys':len(current),'actual_saved_C5_wrapper_rows':len(raw),'actual_completed_C5_profiles':results,'actual_completed_C5_artifacts':len(completed),'canonical_receipt':receipt,'interruption_cause':'UNKNOWN','phase_approval':False,'engine_invocations':0,'listening_performed':False})
print(json.dumps({'passed':all(x['passed'] for x in checks),'checks':len(checks),'failed':[x for x in checks if not x['passed']],'C5_artifacts':len(completed)},ensure_ascii=False))
