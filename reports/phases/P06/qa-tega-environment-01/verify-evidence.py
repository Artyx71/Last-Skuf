"""Read-only actual source/artifact/receipt and numeric replay audit; no engines/network."""
from pathlib import Path
import hashlib,json,re,shutil,math,collections,struct
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';N=W/'reports/phases/P06/tega-environment-01/native-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
expected=json.loads((Q/'copy-inputs.json').read_text());native_map=json.loads((N/'source_hashes.json').read_text());assert native_map==expected
v=json.loads((N/'validation.json').read_text());commands=json.loads((N/'commands.json').read_text());art=[]
for a in v['artifacts']:
 p=W/a['path'];assert p.is_file() and p.resolve().is_relative_to(W.resolve());digest=sha(p);assert digest==a['sha256'];art.append(a|{'actual_sha256':digest,'actual_bytes':p.stat().st_size})
assert all(c['exit_code']==0 and c['passed'] is True for c in commands)
for mode in ['live','movie']:
 lines=(N/(mode+'.log')).read_text().splitlines();assert [s for s in lines if s][-1]=='exit_code=0';assert not re.search(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use','\n'.join(lines))
live=json.loads((N/'live/result.json').read_text());movie=json.loads((N/'movie/result.json').read_text());assert len(live['checks'])==424 and len(movie['checks'])==296 and all(c['passed'] is True for j in [live,movie] for c in j['checks'])
paths={Path(c['path']) for c in live['captures']};pngs=set((N/'live').glob('*.png'));assert paths==pngs and len(paths)==128 and len(live['captures'])==128 and all(type(c['code']) is int and c['code']==0 for c in live['captures'])
assert all(p.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' for p in pngs)
mp4=W/'build/P06/tega-environment-01/tega-environment.mp4';assert sha(mp4)=='5546870556a6500ec9c45b8ada00f3ef4fda717e2a46965ec5917695d22c1cb7'
probe=json.loads((N/'movie_probe.json').read_text());video=[s for s in probe['streams'] if s['codec_type']=='video'];assert len(video)==1 and int(video[0]['nb_frames'])==4649
receipt_audit=[]
for parent in sorted((W/'reports/phases/P06/tega-environment-01/controller-receipts').iterdir()):
 p=parent/'receipt.json';j=json.loads(p.read_text());assert sha(parent/'output.log')==j['log_sha256'];receipt_audit.append({'receipt_path':str(p.relative_to(W)),'sha256':sha(p),'operation':j['operation'],'exit_code':j['exit_code'],'log_sha256':j['log_sha256'],'seconds':j['seconds']})
assert any(r['operation']=='fc1f65eaa2e747a2b762eb92b70e613a' and r['exit_code']==0 for r in receipt_audit)
selected=['object_hit_false_right_contact.png','finisher_true_environmental_up_contact.png']
save(Q/'selected-native-images.json',{'scope':'Two actual native PNGs visually inspected for technical integration only; no ART/feel approval','files':[{'path':str((N/'live'/p).relative_to(W)),'sha256':sha(N/'live'/p),'dimensions':struct.unpack('>II',(N/'live'/p).read_bytes()[16:24])} for p in selected]})
for rel in ['validation.json','commands.json','source_hashes.json','movie_probe.json']:
 dest=Q/'author-evidence/native-01'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(N/rel,dest)
for phase in ['headless-01','headless-02','headless-03','headless-04']:
 for rel in ['validation.json','live.log']:
  p=W/'reports/phases/P06/tega-environment-01'/phase/rel
  if p.is_file():dest=Q/'author-evidence'/phase/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
save(Q/'artifact-verification.json',{'scope':'READ_ONLY_REAL_ARTIFACT_REHASH','native_validation_sha256':sha(N/'validation.json'),'source_head':v['source_head'],'source_count':len(native_map),'sources_match_independent_6a_snapshot':True,'artifacts':art,'actual_pngs':len(paths),'movie':{'path':str(mp4.relative_to(W)),'sha256':sha(mp4),'bytes':mp4.stat().st_size,'saved_ffprobe_video_frames':video[0]['nb_frames'],'saved_ffprobe_duration':video[0]['duration'],'independent_video_decode':False},'receipts':receipt_audit,'no_actual_export_or_nativeWindows_claim':True})
analysis=[]
for label,p in [('own-headless',Q/'tega/result.json'),('author-native',N/'live/result.json'),('author-movie',N/'movie/result.json')]:
 j=json.loads(p.read_text());tokens=[(c['epoch'],c['id'],c['target']) for c in j['contacts']];assert len(tokens)==len(set(tokens))==66
 f=[c for c in j['contacts'] if c['finisher']];assert len(f)==24
 counts=collections.Counter(c['segment'].split('_')[1] for c in f);assert counts=={'false':12,'true':12}
 for c in f:
  assert c['player_action_frame']==1 and c['player_frame']==1 and c['damage']==1 and c['lethal'] is True and not c['target_is_player']
  rows=[t for t in j['trace'] if t['segment']==c['segment']];assert rows and rows[-1]['damage_events']==2 and rows[-1]['score']==100
 pair=[c for c in j['checks'] if c['name'].startswith('finisher_') and 'Full_Reduced_identical' in c['name']];assert len(pair)==12 and all(c['passed'] is True for c in pair)
 incoming=[c for c in j['contacts'] if c['segment'].startswith('incoming_')];assert len(incoming)==6 and all(c['target_is_player'] for c in incoming)
 cloth=j['clothing_overlay'];assert len(cloth)==12 and all(c['ttl']>0 and math.dist(c['actual'],c['expected'])<=3.6 for c in cloth)
 audio=[c for c in j['checks'] if c['name'].startswith('foot_callback_')];assert len(audio)==16 and all(c['passed'] is True for c in audio)
 analysis.append({'label':label,'result_sha256':sha(p),'checks':len(j['checks']),'trace_samples':len(j['trace']),'object_samples':len(j['object_trace']),'unique_Core_receipts':len(tokens),'Full_FIN':counts['false'],'Reduced_FIN':counts['true'],'FIN_own_contact_pose1':len(f),'actual_incoming_Core_hurt_fatal_3phase':len(incoming),'all_FIN_final_damage2_score100':True,'FullReduced_equal_outcome_checks':len(pair),'actual_clothing_socket_proofs':len(cloth),'eight_audio_callback_assertion_pairs':len(audio),'selected_FIN_contacts':f,'incoming_contacts':incoming,'clothing_socket_proofs':cloth})
save(Q/'numeric-replay-analysis.json',{'scope':'SAVED_SIGNAL_NUMERIC_GAMEPLAY_PROOFS_NOT_AUDIO_OR_ART_ACCEPTANCE','runs':analysis,'assumptions':'Full/Reduced mode tied to actual frozen replay OptionsStore calls; no separate independent observation hook executed.'})
print('VERIFIED',len(art),'real native artifacts,',len(native_map),'sources,128PNG,4649 saved video frames;3x66 unique contact tokens and3x24 FIN routes')
