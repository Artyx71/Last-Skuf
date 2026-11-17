"""Independent read-only raw source/media/receipt rollforward audit, no engines/network."""
from pathlib import Path
import json,hashlib,shutil,re,math
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';old=Q.parent/'qa-pasha-moving-shot-02';N=W/'reports/phases/P06/pasha-moving-shot-01/native-03';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):(Q/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert sha(old/'decision.json')=='df738eccceb687724d8a16e963b49d2f96fb2d9a1d89e2848e198078c590a4ff'
for item in json.loads((old/'artifacts.json').read_text())['files']:assert sha(old/item['path'])==item['sha256']
current=json.loads((Q/'copy-inputs.json').read_text());prior=json.loads((old/'copy-inputs-final.json').read_text());assert len(current)==1314 and {k for k in current if current[k]!=prior[k]}=={'game/scripts/ui/ranged_feedback.gd'}
assert json.loads((N/'source_hashes.json').read_text())==current
v=json.loads((N/'validation.json').read_text());assert v['passed'] is True and v['source_unchanged'] is True and v['source_head']=='b359747361c6ac76ccfc0cc8ff262c8327cf33e4';assert sha(N/'validation.json')=='d3be7675604c3a0cafb3f5b48491ed019ce346f647b823eef66ef2bc049d6917';art=[]
for item in v['artifacts']:
 p=W/item['path'];assert p.resolve().is_relative_to(W.resolve()) and p.is_file() and sha(p)==item['sha256'];art.append(item|{'bytes':p.stat().st_size})
assert len(art)==196
live=json.loads((N/'live/result.json').read_text());movie=json.loads((N/'movie/result.json').read_text());assert len(live['checks'])==581 and len(movie['checks'])==393 and all(c['passed'] is True for j in [live,movie] for c in j['checks']);assert len(live['captures'])==188 and all(type(c['code']) is int and c['code']==0 for c in live['captures']) and {Path(c['path']) for c in live['captures']}==set((N/'live').glob('*.png'))
for mode in ['live','movie']:
 text=(N/(mode+'.log')).read_text();assert [line for line in text.splitlines() if line][-1]=='exit_code=0' and not re.search(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use',text)
mp4=Path(v['movie_path']);assert sha(mp4)=='bacc356864061fd5d902fa2a38150c73e9de9199547d3bb5ee0425330ffaa446';probe=json.loads((N/'movie_probe.json').read_text());video=[s for s in probe['streams'] if s['codec_type']=='video'][0];assert int(video['nb_frames'])==5661
for name in ['validation.json','commands.json','source_hashes.json','movie_probe.json']:
 dest=Q/'author-evidence/native-03'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(N/name,dest)
for name in ['empty_clip_HUD.png','refill_HUD.png']:shutil.copy2(N/'live'/name,Q/'author-evidence/native-03'/name)
write('native-artifact-verification.json',{'scope':'ACTUAL_REHASH_NOT_FULL_PHASE_ACCEPTANCE','source_count':1314,'source_head':v['source_head'],'source_inventory_exact':True,'artifacts':art,'artifact_count':len(art),'actual_native_PNGs':188,'native_checks':581,'movie_checks':393,'PNGs_actually_viewed_by_QA':2,'mp4':{'path':str(mp4.relative_to(W)),'sha256':sha(mp4),'bytes':mp4.stat().st_size,'saved_probe_video_frames':5661,'saved_probe_video_duration':video['duration'],'independent_decode':False},'oldQA02all153portablefiles_unchanged':True})
P=W/'reports/phases/P06/pasha-moving-shot-01/hud-preflight-01';pv=json.loads((P/'validation.json').read_text());assert pv['passed'] is True and pv['source_unchanged'] is True and pv['source_head']==v['source_head'];assert json.loads((P/'source_hashes.json').read_text())==current
for item in pv['artifacts']:assert sha(W/item['path'])==item['sha256']
pj=json.loads((P/'result.json').read_text());assert len(pj['checks'])==18 and all(c['passed'] is True for c in pj['checks']);samples=pj['samples'];assert len(samples)==9 and all(s['opaque_NPC_pixels_under_meter']==0 and s['meter']==[380.0,49.0,144.0,2.0] for s in samples)
for name in ['validation.json','result.json','source_hashes.json']:
 dest=Q/'author-evidence/HUD-preflight'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(P/name,dest)
write('HUD-preflight-verification.json',{'scope':'ACTUAL_NINE_FIXTURE_VIEWS_ONLY_NOT_ALL_POSSIBLE_NPC_POSITIONS','checks':18,'actualPNG9':len(list(P.glob('*.png'))),'source_map_exact1314':True,'all_meter_opaque_NPC_pixel_counts_zero':True,'samples':samples,'validation_sha256':sha(P/'validation.json'),'no_new_viewer_engine_executed_by_QA':True})
art_decision=R/'reports/phases/P06/art-pasha-moving-shot-03/decision.json';ad=json.loads(art_decision.read_text());assert ad['status']=='PASS_COMPONENT' and ad['source_head']==v['source_head'] and sha(art_decision)=='bc5241ca31ff1b790ec98692324e8e2fcc1c2dfe49a2140ae6711ae0aaebf1f0';shutil.copy2(art_decision,Q/'author-evidence/ART03-decision.json')
analysis=[]
for label,p in [('own-b359',Q/'Pasha/result.json'),('native-b359',N/'live/result.json'),('movie-b359',N/'movie/result.json')]:
 j=json.loads(p.read_text());tokens=[(c['epoch'],c['id'],c['target']) for c in j['contacts']];assert len(tokens)==len(set(tokens))==105;fin=[c for c in j['contacts'] if c['finisher']];matrix=[c for c in fin if c['segment'].startswith('finisher_')];assert len(fin)==41 and len(matrix)==40 and sum(c['segment'].startswith('finisher_false_') for c in matrix)==20 and sum(c['segment'].startswith('finisher_true_') for c in matrix)==20 and all(c['player_frame']==1 for c in fin)
 assert len(j['launches'])==len(j['costs'])==8 and all(l['source_pose']==3 for l in j['launches']) and all(c['pose']==3 and c['reason']=='moving_shot' and c['ammo']==3 for c in j['costs']);assert len(j['clothing_overlay'])==32 and all(math.dist(c['actual'],c['expected'])<=3.6 for c in j['clothing_overlay'])
 analysis.append({'label':label,'sha256':sha(p),'trace_samples':len(j['trace']),'ammo_samples':len(j['ammo_trace']),'contacts':105,'FIN40matrix_plus1sharedclip':41,'matrix_Full':20,'matrix_Reduced':20,'launch_cost_pose3pairs':8,'clothing_actual_poseproofs':32})
write('numeric-replay-analysis.json',{'scope':'RAW_SAVED_CONTACT_COST_CLOTHING_COUNTS_NOT_AUDIO_OR_FPS_ACCEPTANCE','runs':analysis})
receipts=[]
for folder in (R/'.autopilot/jobs').iterdir():
 p=folder/'input.json'
 if not p.is_file():continue
 j=json.loads(p.read_text())
 if not any(arg.endswith('qa-pasha-moving-shot-03/run-isolated-ui-rollforward.py') for arg in j.get('argv',[])):continue
 receipt=json.loads((folder/'receipt.json').read_text());assert receipt['exit_code']==0 and sha(folder/'output.log')==receipt['log_sha256'];dest=Q/'canonical-job-evidence'/folder.name;dest.mkdir(parents=True,exist_ok=True)
 for name in ['input.json','started.json','receipt.json','output.log']:shutil.copy2(folder/name,dest/name)
 receipts.append({'operation':folder.name,'exit_code':0,'receipt_sha256':sha(folder/'receipt.json'),'log_sha256':sha(folder/'output.log'),'seconds':receipt['seconds']})
assert len(receipts)==1;write('canonical-stage-audit.json',{'scope':'ACTUAL_COMPLETED_OWN_QA_JOB_ONLY','jobs':receipts,'all_QA_engines_finished':True,'no_Controller_invocation_by_reviewer':True})
print('Verified b359 source1314/native196artifacts/188PNG/581+393, actual9HUDstateszeroopaque, own393+24+16; QA02unchanged')
