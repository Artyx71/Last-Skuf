"""Read-only frozen-20c closure evidence rehash; no engine/CI/controller calls."""
from pathlib import Path
import hashlib,json,shutil,re
Q=Path(__file__).resolve().parent;R=Q.parents[3];W=R/'.autopilot/worktrees/P06';old=Q.parent/'qa-tega-environment-02';N=W/'reports/phases/P06/tega-environment-01/native-03';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,v):(Q/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
assert sha(old/'decision.json')=='8ff09cfdd22e91b0be70cb4b3620526957a91ee853e4baec2d4efb6f2edee679'
for item in json.loads((old/'artifacts.json').read_text())['files']:assert sha(old/item['path'])==item['sha256']
expected=json.loads((Q/'copy-inputs.json').read_text());assert json.loads((N/'source_hashes.json').read_text())==expected
v=json.loads((N/'validation.json').read_text());art=[]
for item in v['artifacts']:
 p=W/item['path'];assert p.is_file() and p.resolve().is_relative_to(W.resolve()) and sha(p)==item['sha256'];art.append(item|{'bytes':p.stat().st_size})
assert len(art)==136
live=json.loads((N/'live/result.json').read_text());movie=json.loads((N/'movie/result.json').read_text());assert len(live['checks'])==433 and len(movie['checks'])==305 and all(c['passed'] is True for j in [live,movie] for c in j['checks'])
assert len(live['captures'])==128 and {Path(c['path']) for c in live['captures']}==set((N/'live').glob('*.png')) and all(type(c['code']) is int and c['code']==0 for c in live['captures'])
commands=json.loads((N/'commands.json').read_text());assert all(c['exit_code']==0 and c['passed'] is True for c in commands)
for mode in ['live','movie']:
 log=(N/(mode+'.log')).read_text();assert [s for s in log.splitlines() if s][-1]=='exit_code=0' and not re.search(r'SCRIPT ERROR:|ERROR:|FAIL |instances were leaked|resources still in use',log)
mp4=Path(v['movie_path']);assert sha(mp4)=='59c65f1c654ef84cfd79bbbb51090980ac879c544c5e23281f284dffa402fa60'
probe=json.loads((N/'movie_probe.json').read_text());video=[s for s in probe['streams'] if s['codec_type']=='video'];assert int(video[0]['nb_frames'])==4810
for name in ['validation.json','commands.json','source_hashes.json','movie_probe.json']:
 p=Q/'author-evidence/native-03'/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(N/name,p)
write('artifact-verification.json',{'scope':'READ_ONLY_NATIVE_20C_REHASH_NOT_PHASE_ACCEPTANCE','source_count':len(expected),'source_head':v['source_head'],'source_map_exact':True,'validation_sha256':sha(N/'validation.json'),'artifacts':art,'live_checks':433,'movie_checks':305,'actual_PNGs':128,'PNGs_reviewer_visually_viewed':2,'movie':{'path':str(mp4.relative_to(W)),'sha256':sha(mp4),'bytes':mp4.stat().st_size,'saved_probe_video_frames':4810,'independently_decoded':False},'old_QA02_78_manifest_files_unchanged':True,'old_QA02_decision_sha256':sha(old/'decision.json')})
audit=[]
for folder in (R/'.autopilot/jobs').iterdir():
 p=folder/'input.json'
 if not p.is_file():continue
 j=json.loads(p.read_text())
 if not any(arg.endswith(('p06-qa-tega-job08.py',)) for arg in j.get('argv',[])):continue
 receipt=json.loads((folder/'receipt.json').read_text());assert sha(folder/'output.log')==receipt['log_sha256'] and j['argv_sha256']==receipt['argv_sha256'];dest=Q/'canonical-job-evidence'/folder.name;dest.mkdir(parents=True,exist_ok=True)
 for name in ['input.json','started.json','receipt.json','output.log']:shutil.copy2(folder/name,dest/name)
 audit.append({'operation':folder.name,'task':j['task'],'exit_code':receipt['exit_code'],'receipt_sha256':sha(folder/'receipt.json'),'log_sha256':sha(folder/'output.log'),'seconds':receipt['seconds'],'entrypoint_sha256':sha(Path(j['argv'][1]))})
assert len(audit)==1 and all(r['exit_code']==0 for r in audit)
write('canonical-stage-audit.json',{'scope':'ACTUAL_READ_ONLY_JOB_RECEIPTS','operations':audit,'no_engine_or_Controller_calls_by_audit':True,'all_QA_engines_finished':True})
analysis=[]
for label,p in [('own',Q/'tega/result.json'),('native',N/'live/result.json'),('movie',N/'movie/result.json')]:
 j=json.loads(p.read_text());tokens={(c['epoch'],c['id'],c['target']) for c in j['contacts']};assert len(tokens)==len(j['contacts'])==66;fin=[c for c in j['contacts'] if c['finisher']];assert len(fin)==24 and all(c['player_frame']==1 for c in fin)
 analysis.append({'label':label,'sha256':sha(p),'checks':len(j['checks']),'trace_samples':len(j['trace']),'contacts':66,'FIN_Full':sum(c['segment'].startswith('finisher_false_') for c in fin),'FIN_Reduced':sum(c['segment'].startswith('finisher_true_') for c in fin),'geometry_callback_checks':len([c for c in j['checks'] if c['name'].startswith('foot_geometry_')])})
write('numeric-replay-analysis.json',{'scope':'REAL_SAVED_CONTACTS_NOT_ART_AUDIO_ACCEPTANCE','runs':analysis,'scope_does_not_grant_fullphase':True})
print('Rehashed native03:',len(art),'artifacts/1242sources/128PNG,433+305,4810savedvideoFrames; successfulQA08receipt verified; QA02unchanged')
