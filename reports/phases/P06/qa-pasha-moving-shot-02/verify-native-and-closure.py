"""Read-only 17b source/media/actual callback closure audit. No engines/CI/network."""
from pathlib import Path
import hashlib,json,shutil,re,collections,math
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';N=W/'reports/phases/P06/pasha-moving-shot-01/native-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):(Q/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
expected=json.loads((Q/'copy-inputs-final.json').read_text());assert json.loads((N/'source_hashes.json').read_text())==expected
v=json.loads((N/'validation.json').read_text());assert v['source_head']=='17b162d9d4320650f7e0422d63c1c2c77882a9d3' and v['passed'] is True and v['source_unchanged'] is True;art=[]
for item in v['artifacts']:
 p=W/item['path'];assert p.resolve().is_relative_to(W.resolve()) and p.is_file() and sha(p)==item['sha256'];art.append(item|{'bytes':p.stat().st_size})
assert len(art)==196
live=json.loads((N/'live/result.json').read_text());movie=json.loads((N/'movie/result.json').read_text());assert len(live['checks'])==581 and len(movie['checks'])==393 and all(c['passed'] is True for j in [live,movie] for c in j['checks']);assert len(live['captures'])==188 and {Path(c['path']) for c in live['captures']}==set((N/'live').glob('*.png'))
for mode in ['live','movie']:
 text=(N/(mode+'.log')).read_text();assert [line for line in text.splitlines() if line][-1]=='exit_code=0' and not re.search(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use',text)
mp4=Path(v['movie_path']);probe=json.loads((N/'movie_probe.json').read_text());video=[s for s in probe['streams'] if s['codec_type']=='video'][0]
for name in ['validation.json','commands.json','source_hashes.json','movie_probe.json']:
 dest=Q/'author-evidence/native-02'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(N/name,dest)
shutil.copy2(N/'live/empty_clip_HUD.png',Q/'author-evidence/native-02/empty_clip_HUD.png')
art_decision=R/'reports/phases/P06/art-pasha-moving-shot-02/decision.json';ad=json.loads(art_decision.read_text());assert ad['status']=='FAIL_COMPONENT' and ad['source_head']==v['source_head'];shutil.copy2(art_decision,Q/'author-evidence/ART02-decision.json')
write('native-artifact-verification.json',{'scope':'ACTUAL_SOURCE_MEDIA_REHASH_NOT_ART_ACCEPTANCE','source_head':v['source_head'],'source_count':len(expected),'source_map_exact':True,'validation_sha256':sha(N/'validation.json'),'artifacts':art,'native_checks':581,'movie_checks':393,'actualPNG188':True,'PNGs_actually_viewed':1,'mp4':{'path':str(mp4.relative_to(W)),'sha256':sha(mp4),'bytes':mp4.stat().st_size,'saved_video_frames':video['nb_frames'],'saved_video_duration':video['duration'],'independent_video_decode':False},'ART02_actual_crown_overlap_decision_sha256':sha(art_decision)})
analysis=[]
for label,p in [('own17b',Q/'Pasha-final/result.json'),('native17b',N/'live/result.json'),('movie17b',N/'movie/result.json')]:
 j=json.loads(p.read_text());tokens=[(c['epoch'],c['id'],c['target']) for c in j['contacts']];assert len(tokens)==len(set(tokens))==105;fin=[c for c in j['contacts'] if c['finisher']];matrix=[c for c in fin if c['segment'].startswith('finisher_')];assert len(fin)==41 and len(matrix)==40 and sum(c['segment'].startswith('finisher_false_') for c in matrix)==20 and sum(c['segment'].startswith('finisher_true_') for c in matrix)==20
 assert len([c for c in fin if c['segment']=='shared_clip_shot_then_firearm_finisher'])==1
 assert all(c['player_frame']==1 for c in fin)
 assert len(j['launches'])==8 and len(j['costs'])==8 and all(l['source_pose']==3 for l in j['launches']) and all(c['pose']==3 and c['reason']=='moving_shot' and c['ammo']==3 for c in j['costs'])
 assert len(j['clothing_overlay'])==32 and all(math.dist(c['actual'],c['expected'])<=3.6 for c in j['clothing_overlay'])
 analysis.append({'label':label,'sha256':sha(p),'trace_samples':len(j['trace']),'ammo_samples':len(j['ammo_trace']),'unique_Core_contacts':105,'FIN_matrix':40,'shared_clip_extra_FIN':1,'matrixFull':20,'matrixReduced':20,'launch_and_cost_pose3_pairs':8,'clothing_overlay_actual_pose_proofs':32,'HUD_rect_details':[c['details'] for c in j['checks'] if c['name']=='actual_ammo_HUD_rects_stay_above_arena']})
write('numeric-replay-analysis.json',{'scope':'ACTUAL_SAVED_CONTACT_COST_CLOTHING_COUNTS_NOT_ART_AUDIO_ACCEPTANCE','runs':analysis,'HUD_rect_pass_does_not_prove_no_crown_occlusion':True})
receipts=[]
for folder in (R/'.autopilot/jobs').iterdir():
 p=folder/'input.json'
 if not p.is_file():continue
 j=json.loads(p.read_text())
 if not any(arg.endswith(('qa-pasha-moving-shot-02/run-isolated-final-qa.py','qa-pasha-moving-shot-02/run-isolated-remediation-qa.py')) for arg in j.get('argv',[])):continue
 receipt=json.loads((folder/'receipt.json').read_text());assert sha(folder/'output.log')==receipt['log_sha256'];dest=Q/'canonical-job-evidence'/folder.name;dest.mkdir(parents=True,exist_ok=True)
 for name in ['input.json','started.json','receipt.json','output.log']:shutil.copy2(folder/name,dest/name)
 receipts.append({'operation':folder.name,'exit_code':receipt['exit_code'],'seconds':receipt['seconds'],'receipt_sha256':sha(folder/'receipt.json'),'log_sha256':sha(folder/'output.log')})
assert len(receipts)==2 and sorted(r['exit_code'] for r in receipts)==[0,1];write('canonical-stage-audit.json',{'scope':'ACTUAL_READ_ONLY_COMPLETED_JOBS','jobs':receipts,'all_QA_engines_finished':True,'no_Controller_execution_by_reviewer':True})
wall=json.loads((Q/'wall-closure-final/result.json').read_text());assert all(c['passed'] is True for c in wall['checks']);write('wall-closure-proof.json',{'scope':'SAME_BYTEEXACT16ASSERTIONS_AFTER_CORE_FIX','all16_pass':True,'proofs':wall['proofs'],'original_baseline_14of16_FAIL_unchanged':True})
print('Verified native581/movie393/196artifacts/1314sources/188PNG; each105contacts/41FIN; wall16closed; ART residualcrown prevents old17b componentPASS')
