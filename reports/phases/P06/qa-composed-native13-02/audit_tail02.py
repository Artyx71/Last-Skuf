#!/usr/bin/env python3
"""Independent read-only completed tail02 audit. No game/worker/network calls."""
from pathlib import Path
import hashlib,json,struct,sys
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';N=W/'reports/phases/P06/native-remaining5-02';Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
checks=[]
def ck(ok,label,details=None):checks.append({'name':label,'passed':bool(ok),'details':details})
def png(p):
 if str(p).startswith('Z:'):p=Path(str(p)[2:].replace(chr(92),'/'))
 with p.open('rb') as f:b=f.read(24)
 assert b[:8]==b'\x89PNG\r\n\x1a\n' and b[12:16]==b'IHDR';a,c=struct.unpack('>II',b[16:24]);assert a>0 and c>0
 return [a,c]
J=R/'.autopilot/jobs/311fdc08f73e43169295d6a2d67786b0';receipt=read(J/'receipt.json');inp=read(J/'input.json')
ck(receipt['exit_code']==1 and receipt['argv_sha256']==inp['argv_sha256'] and sha(J/'output.log')==receipt['log_sha256'],'actual failed outer canonical receipt/argv/log',receipt)
v=read(N/'validation.json');before=read(N/'source_hashes_before.json');after=read(N/'source_hashes_after.json');ck(before==after,'actual before/after source freeze equality',len(before));ck(v['source_head']==v['head_after']=='263e888afc9875ebf887267c0dd734b70897f344','actual captured HEAD stable263')
ck(v['passed'] is False and v['phase_approval'] is False and v['merge_approval'] is False and v['original_failed_attempt_rewritten'] is False,'honest FAIL/no phase/no old failure rewrite')
contract=W/'reports/phases/P06/native-continuation-contract-02/contract.json';c=read(contract);approval=R/'reports/phases/P06/lead-cast-continuation-preflight-01/decision.json';ck(sha(contract)==v['contract_sha256']==v['final_binding_hashes']['contract'] and sha(approval)==v['approval_sha256']==v['final_binding_hashes']['approval'],'exact frozen contract02 and independent approval retained')
refs=[]
for row in c['artifacts']:
 p=W/row['path'];actual=sha(p);refs.append({'path':row['path'],'sha256':actual,'matches':actual==row['sha256']})
ck(len(refs)==905 and all(x['matches'] for x in refs),'actual905 prior proof artifacts unchanged')
write(Q/'contract-reference-rehash.json',refs)
source=[]
for key,digest in before.items():
 p=W/key;actual=sha(p);source.append({'path':key,'recorded':digest,'current':actual,'unchanged':actual==digest})
changes=[x for x in source if not x['unchanged']];ck({x['path'] for x in changes}=={'tools/verify_p04.py','tools/verify_p04g.py'},'postreceipt source changes restricted to two future movie launchers',changes);ck(all(x['unchanged'] for x in source if x['path'].startswith('game/')),'all recorded Game runtime/art/QA files byteexact263 at audit')
write(Q/'recorded-source-current-comparison.json',source)
summary={'canonical':receipt,'cast':{},'npc':{},'combat':{},'source_keys':len(source),'source_postreceipt_changes':changes,'contract_references':len(refs)}
for mode in ['cast','cast_large_text']:
 folder=N/mode;d=read(folder/'result.json');mv=read(folder/'validation.json');tr=d['viewing_trace'];groups=[tr[i:i+4] for i in range(0,len(tr),4)];full=[]
 ck(d['passed'] is True and d['actual_input'] is True and len(d['checks'])==328 and all(x['passed'] is True for x in d['checks']) and d['renderer']=='X11',mode+' actual328 native assertions')
 ck(len(tr)==180 and len(groups)==45,mode+'180 snapshots/45groups')
 for i,g in enumerate(groups):
  a,b,c1,z=g;identity=lambda x:(x['actor'],x['line_id'],x['line_index'],x['emotion'])
  ck([x['phase'] for x in g]==['before_reveal','after_reveal','before_advance','after_advance'] and identity(a)==identity(b)==identity(c1) and all(x['active'] and x['emotion']==x['expected_emotion'] for x in [a,b,c1]) and all(x['visible_count']>=x['text_length'] and x['body_visible']>=x['text_length'] for x in [b,c1]) and (not z['active'] or z['line_index']==a['line_index']+1),mode+' actual state-aware oneadvance '+str(i))
  if a['visible_count']>=a['text_length']:full.append(a)
 files=[]
 for row in mv['artifacts']:
  p=W/row['path'];ck(sha(p)==row['sha256'],mode+' artifact binding '+p.name)
  if p.suffix=='.png':files.append({'path':str(p),'sha256':sha(p),'dimensions':png(p)})
 reload=read(folder/'process-reload.json');ck(mv['actual_new_process_reload'] is True and reload.get('passed') is True and all(x['passed'] is True and x['exit_code']==0 for x in mv['commands']),mode+' separate actual reload process clean')
 ck(len(files)==45,mode+'45 actual nonempty PNG headers')
 summary['cast'][mode]={'checks':len(d['checks']),'snapshots':len(tr),'groups':len(groups),'already_full_beforeReveal':len(full),'already_full_records':full,'PNG':files,'reload':reload}
d=read(N/'npc_baseline/result.json');ck(d['passed'] is True and d['actual_input'] is True and d['renderer']=='X11' and len(d['checks'])==204 and all(x['passed'] is True for x in d['checks']),'actualNPC204 Input baseline assertions')
ck(len(d['cases'])==14 and len(d['captures'])==42 and len(d['Full_Reduced_signatures'])==7 and d['deferred_C09_style_implemented'] is False,'actual14 supplemental cases/7pairs/42captures; no deferred style claim')
caseproof=[]
for case in d['cases']:
 contacts=[e for e in d['contacts'] if e['segment']==case['segment']];captures=[e for e in d['captures'] if e['name'].startswith(case['segment']+'_')];signature=case['signature'];trace=[x for x in d['trace'] if x['segment']==case['segment']]
 ck(len(contacts)==2 and contacts[0]['finisher'] is False and contacts[0]['damage']==0 and contacts[0]['npc_state']=='stunned' and contacts[1]['finisher'] is True and contacts[1]['lethal'] is True and contacts[1]['damage']==1 and contacts[1]['npc_frame']==1 and contacts[1]['npc_state']=='dead' and len({(e['epoch'],e['id'],e['target']) for e in contacts})==2,'NPC actual earnedstun→oneFIN contact '+case['segment'])
 ck(signature[:5]==[0,2,1,100,2] and signature[-1]=='dead' and d['Full_Reduced_signatures'][case['archetype']+':'+case['category']]==signature,'NPC actual once outcome/FullReduced equality '+case['segment'])
 images=[{'name':e['name'],'sha256':sha(Path(e['path'])),'dimensions':png(Path(e['path'])),'frame':e['npc_frame'],'state':e['npc_state']} for e in captures];ck(len(images)==3,'NPC three actual captures '+case['segment']);caseproof.append({'case':case,'contacts':contacts,'captures':images,'trace_samples':len(trace)})
summary['npc']={'checks':204,'cases':caseproof,'trace_samples':len(d['trace']),'contacts':len(d['contacts']),'probe_sha256':read(N/'npc_baseline/validation.json')['probe_sha256']}
B=N/'combat_baseline';validation=read(B/'validation.json');failed=[x for x in validation if x['passed'] is not True];movie=next(x for x in validation if x['name']=='movie_replay');ck(movie['exit_code']==124 and not (B/'movie_replay.json').exists() and not (B/'movie_replay.wav').exists(),'actual bounded Movie124 incomplete, missing result/WAV retained')
cmdline=next(line for line in (B/'logs/movie_replay.log').read_text().splitlines() if line.startswith('$ '));ck('--write-movie' in cmdline and '--fixed-fps' in cmdline and '--disable-vsync' not in cmdline and '--max-fps' not in cmdline,'actual failed Movie command omitted physical launch flags; cause unestablished',cmdline)
summary['combat']['failed_wrapper_rows']=failed;summary['combat']['movie_partial_PNG']=len(list((B/'movie_replay_frames').glob('*.png')));summary['combat']['movie_actual_command']=cmdline
summary['combat']['positive_modes']={}
for mode in ['full_replay','reduced_replay','linux_export_replay','wine_export_replay']:
 d=read(B/(mode+'.json'));p=d['performance'];fin=d['finishers'];ai=d['ai'];captures=d['captures']
 ck(d['passed'] is True and len(d['checks'])==413 and all(x['passed'] is True for x in d['checks']),mode+'413 actual assertions')
 ck(len(fin)==20 and len({(x['category'],x['direction']) for x in fin})==20 and all(x['hits']==2 and x['kills']==1 and x['score']==100 and len(x['events'])==2 and x['events'][0]['finisher'] is False and x['events'][1]['finisher'] is True and x['events'][1]['lethal'] is True and x['source_frame']==x['target_frame']==1 for x in fin),mode+'20 actual category/direction earned contact outcomes')
 ck(len(ai)==12 and len({(x['kind'],x['direction']) for x in ai})==12 and all(x['player_hits']==1 for x in ai),mode+'12 actualAI kind/direction attacks')
 ck(len(captures)==218 and all(x['code']==0 and png(Path(x['path'])) for x in captures),mode+'218 actualPNG headers')
 ck(p['samples']==600 and p['movie_maker'] is False and p['rendered'] is True and p['measurement']=='monotonic real process-frame intervals, not forced simulation delta' and 0<p['p50_ms']<=p['p95_ms']<=p['p99_ms'],'actual nonMovie600 wallframe summary '+mode,p)
 summary['combat']['positive_modes'][mode]={'checks':413,'PNG':218,'finishers':20,'AI':12,'performance':p,'audio_driver':d['audio']['audio_driver']}
ck([(x['category'],x['direction'],x['hits'],x['kills'],x['score']) for x in read(B/'full_replay.json')['finishers']]==[(x['category'],x['direction'],x['hits'],x['kills'],x['score']) for x in read(B/'reduced_replay.json')['finishers']],'actualFullReduced outcome invariance recomputed')
exports=[]
for row in read(B/'exports.json'):
 p=W/row['path'];expected=b'\x7fELF' if row['platform']=='Linux' else b'MZ';magic=p.open('rb').read(4);actual=sha(p);ck(actual==row['sha256'] and p.stat().st_size==row['bytes'] and magic.startswith(expected),'actual exported artifact bytes/magic '+row['platform']);exports.append({**row,'actual_sha256':actual,'actual_magic':magic.hex()})
summary['combat']['actual_exports']=exports
p04=read(B/'p04_regression/validation.json');ck(len(p04)==24 and all(x['passed'] is True for x in p04),'nestedactualP04 all24rows inclMovie/exports/audio positive');summary['combat']['nested_P04_rows']=[{'name':x['name'],'passed':x['passed']} for x in p04]
audio=read(B/'audio_detailed.json');summary['combat']['detailed_audio_failed']={k:v for k,v in audio['checks'].items() if not v} if isinstance(audio['checks'],dict) else [x for x in audio['checks'] if not x['passed']]
# Bind every wrapper-declared actual artifact, retaining failed partial video separately.
artifacts=read(B/'artifacts.json');bad=[]
for row in artifacts:
 p=W/row['path']
 if not p.exists() or sha(p)!=row['sha256'] or p.stat().st_size!=row['bytes']:bad.append(row['path'])
ck(not bad,'actual combat artifact inventory rehashed',{'count':len(artifacts),'bad':bad});summary['combat']['artifacts_rehashed']=len(artifacts)
write(Q/'actual-tail02-audit.json',{'scope':'READONLY_ACTUAL_TAIL02_AUDIT_NOT_PHASE_ACCEPTANCE','passed_audit':all(x['passed'] for x in checks),'checks':checks,'summary':summary,'fresh_runtime_invocations':0,'native_Windows':'NOT_TESTED_WINE_SEPARATE','agent_listening':False,'performance_limit':'Actual source/command/600-summary and capture proof verified; raw individual interval samples not retained, so percentiles not independently recomputed; single host fixture only'})
print(json.dumps({'audit_checks':len(checks),'passed':all(x['passed'] for x in checks),'failed':[x for x in checks if not x['passed']],'combat_failure_rows':[x['name'] for x in failed]},ensure_ascii=False))
