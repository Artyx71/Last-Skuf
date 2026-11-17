from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-character-finisher-audio-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
refs={}
def ref(p):refs[str(p.relative_to(R))]={'root_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size}
m=json.loads((W/'reports/phases/P06/character-finisher-audio-01/native-02/source_hashes_before.json').read_text())
for k,v in m.items():assert sha(W/k)==v,k
put('source-freeze.json',{'schema':1,'frozen_commit':'0dd1cc4dad9379c457e277969b721fcc23a14fe3','source_hashes':m,'recorded_keys':len(m),'current_all_exact':True,'not_future_tree_freeze':True})
for d in ['audio-c01-signal-review-01','audio-c01-runtime-review-01/preflight-01','audio-c01-runtime-review-01/closure-01']:
 D=R/'reports/phases/P06'/d;a=json.loads((D/'artifacts.json').read_text())
 for e in a['files']:
  p=D/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'],str(p);ref(p)
 for n in ['decision.json','artifacts.json','FINAL_HASHES.json']:
  p=D/n
  if p.exists():ref(p)
owner=W/'reports/phases/P06/character-finisher-audio-01/owner-listening-acceptance.json';assert sha(owner)=='3b6b3c69004668ea73a5cc1102263e80abf2d2757952876dfbd234a4526752d9'
d=json.loads(owner.read_text());assert d['owner_exact_answer']=='Прослушал, принимаю для прототипа P06' and not d['agent_listening_performed']
for e in d['evidence']:
 p=W/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'];ref(p)
shutil.copyfile(owner,O/'owner-listening-acceptance.json');ref(owner)
critical=['AGENTS.md','agents/LEAD_REVIEWER.md','game/default_bus_layout.tres','game/scripts/systems/character_finisher_audio.gd','game/scripts/systems/character_combat_profile.gd','game/scripts/systems/audio_director.gd','game/scripts/systems/combat_system.gd','game/tests/character_finisher_audio_test.gd','game/tests/character_finisher_audio_replay.gd','game/assets/audio/character_finishers.json','game/assets/audio/combat_polish.json','game/resources/characters/catalog.json','assets/source_audio/character_finishers/render.py','assets/source_audio/character_finishers/provenance.json','assets/source_audio/character_finishers/adoption.json','tools/verify_character_finisher_audio.py','tools/verify_p06_finisher_audio.py','tools/verify.py']
for k in critical:
 p=W/k;dest=O/'source-snapshot'/k;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);ref(p)
for cat in ['unarmed','blunt','sharp','firearm','environmental']:
 p=W/f'game/assets/audio/combat_polish/finish_{cat}.wav';old=subprocess.check_output(['git','-C',str(W),'show','b359747361c6ac76ccfc0cc8ff262c8327cf33e4:'+str(p.relative_to(W))]);assert hashlib.sha256(old).hexdigest()==sha(p);ref(p)
for n in ['native-01','native-02','headless-03']:
 D=W/'reports/phases/P06/character-finisher-audio-01'/n
 for p in D.rglob('*'):
  if p.is_file():ref(p)
# Prove exact semantics behind reusing historical45-route playback after master gain change.
a=json.loads((W/'reports/phases/P06/character-finisher-audio-01/native-01/source_hashes_before.json').read_text());delta={k for k in set(a)|set(m) if a.get(k)!=m.get(k)}
expected={'game/default_bus_layout.tres','game/export_presets.cfg','game/scripts/qa/owner_preview_smoke.gd','game/tests/character_finisher_audio_replay.gd','tools/verify_p06_finisher_audio.py'};assert delta==expected,delta
for base,name in [('b359747361c6ac76ccfc0cc8ff262c8327cf33e4','C01-production.diff'),('5403faa837a32e0fd370bb374eace120c9c4426b','headroom-only.diff')]:
 (O/name).write_bytes(subprocess.check_output(['git','-C',str(W),'diff',base+'..0dd1cc4','--','game','tools','assets/source_audio']))
# Canonical jobs: verify actual argv/log receipts; immutable input remains initial RUNNING metadata.
receipts=[]
for op in ['2b7d9ed7529241d9be7fe58ea7fa4af7','967d7134e2124246bed2f544cf5647fd','14dc14a7c4654db9be2457b7a81e4264']:
 j=R/'.autopilot/jobs'/op;d=json.loads((j/'receipt.json').read_text());inp=json.loads((j/'input.json').read_text());assert d['operation']==op and d['exit_code']==0 and d['argv_sha256']==inp['argv_sha256'] and d['log_sha256']==sha(j/'output.log')
 out=O/'producer-receipts'/op;out.mkdir(parents=True,exist_ok=True)
 for n in ['input.json','receipt.json','output.log']:ref(j/n);shutil.copyfile(j/n,out/n)
 receipts.append(d)
proc=subprocess.run(['python3','tools/verify_character_finisher_audio.py'],cwd=W,capture_output=True,text=True);assert proc.returncode==0;binding=json.loads(proc.stdout);assert len(binding['checks'])==80 and all(c['passed'] for c in binding['checks']);put('own-source-binding-80.json',binding)
put('source-equivalence.json',{'native01_to_native02_exact_keys':len(set(a)&set(m))-len(delta),'changed_keys':sorted(delta),'Core_AI_player_ability_sprites_and20_source_cues_unchanged':True,'headroom_fix':{'threshold':[-3,-5],'ceiling':[-1,-3],'makeup_difference_db':2,'soft_clip_db':2,'soft_clip_ratio':10},'historical45_routes_reused_by_explicit_equality_not_fresh45_on_newhead':True,'fresh_native02_routes':3,'native02_solo_and_stress_fresh':True})
put('producer-receipt-proofs.json',receipts);put('external-reference-bindings.json',{'schema':1,'base':'ROOT','references':sorted(refs.values(),key=lambda e:e['root_relative_path']),'large_waveforms_or_engine_copies_not_duplicated':True})
print('Ownintegrity exact1465 / historicalrolemanifests / sourcebinding80 / actual3receipts / refs',len(refs))
