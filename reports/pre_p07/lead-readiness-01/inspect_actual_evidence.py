from pathlib import Path
import json,hashlib,subprocess,array,math,struct,collections
ROOT=Path(__file__).resolve().parents[3];WORK=ROOT/'.autopilot/worktrees/P06';OUT=Path(__file__).parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();evidence={};metrics={'scope':'INDEPENDENT_PRODUCTION_READINESS_EVIDENCE_INSPECTION','phase_approval':False}
def record(p):
 p=Path(p);evidence[str(p.relative_to(WORK)) if p.is_relative_to(WORK) else str(p)]=sha(p);return json.loads(p.read_text()) if p.suffix=='.json' else None
preview=record(WORK/'reports/phases/P06/owner-preview-20261115-01/preview.json');metrics['current_packaged_preview']={'source_head_label':preview['source_head'],'scope':preview['scope'],'exports':[]}
for x in preview['exports']:
 p=WORK/x['path'];assert p.stat().st_size==x['bytes'] and sha(p)==x['sha256'];record(p)
 with p.open('rb') as f:
  head=f.read(4096)
 if x['platform']=='Linux':assert head[:4]==b'\x7fELF';magic='ELF64' if head[4]==2 else 'ELF32'
 else:offset=struct.unpack_from('<I',head,0x3c)[0];assert head[:2]==b'MZ' and head[offset:offset+4]==b'PE\0\0';magic='PE_AMD64' if struct.unpack_from('<H',head,offset+4)[0]==0x8664 else 'PE'
 metrics['current_packaged_preview']['exports'].append({'platform':x['platform'],'sha256':sha(p),'bytes':p.stat().st_size,'magic':magic,'run_scope':x['runtime_scope']})
for c in preview['commands']:
 p=WORK/'reports/phases/P06/owner-preview-20261115-01'/(c['name']+'.log');assert sha(p)==c['log_sha256'];record(p)
for mode,count in [('linux_smoke',22),('windows_smoke',18)]:
 p=WORK/'reports/phases/P06/owner-preview-20261115-01'/mode/'result.json';d=record(p);assert len(d['checks'])==count and d['passed'] and all(x['passed'] for x in d['checks']);assert d['renderer']==('X11' if mode.startswith('linux') else 'headless');metrics['current_packaged_preview'][mode]={'checks':count,'failed':0,'renderer':d['renderer'],'scope':d['scope'],'captures':len(d['captures']),'full_combat_approval':d['full_combat_approval']}
 for file in d['captures']:record(Path(file))
history=record(WORK/'reports/pre_p07/production-readiness-01/historical-evidence.json');metrics['historical_P04G_performance']={}
for x in history:
 p=WORK/x['copied'];original=Path(x['source']);assert sha(p)==x['sha256'];assert original.is_file() and sha(original)==x['sha256'];d=record(p);record(original);perf=d['performance'];assert perf['samples']==600 and perf['rendered'] and not perf['movie_maker'];metrics['historical_P04G_performance'][p.stem]=perf
for p in [WORK/'reports/phases/P05/decision.json',WORK/'reports/phases/P05/review.md',WORK/'reports/phases/P04G/lead-attempt3/accepted/decision.json',WORK/'reports/phases/P04G/lead-attempt3/accepted/review.md',WORK/'reports/phases/P04G/lead-attempt3/accepted/human-listening-verification.json']:record(p)
runtime=record(WORK/'game/resources/story/registry.json');design=record(WORK/'planning/CAMPAIGN_PRODUCTION_REGISTRY.json');assert len(runtime['chapters'])==21 and len(runtime['secrets'])==5 and len(design['main_chapters'])==21 and len(design['secret_missions'])==7;playable=[c['id'] for c in runtime['chapters'] if c.get('availability')=='playable'];assert playable==['CH01_THE_MISSED_FIGHT'];metrics['story_and_design']={'canonical_main':21,'canonical_defined_secrets':5,'production_main_slots':21,'production_secret_slots':7,'runtime_playable':playable,'runtime_planned':20,'production_main_lead_approved':sum(bool(c.get('lead_approved')) for c in design['main_chapters']),'design_status_counts':dict(collections.Counter(c['design_status'] for c in design['main_chapters'])),'proposed_optional_ids':[c['id'] for c in design['secret_missions'] if c.get('story_status','').startswith('PROPOSED')],'target_minutes':design['target_first_play_minutes'],'duration_status':design['duration_status']}
# Decode the real two prototype music packages + category combat SFX. No hearing claim.
packages=[record(WORK/'game/assets/audio/manifest.json'),record(WORK/'game/resources/chapters/missed_fight_music.json')];polish=record(WORK/'game/assets/audio/combat_polish.json');audiofiles=sorted({s['path'] for p in packages for s in p['music']['stems']}|{x['path'] for x in polish['sfx'].values()});signal=[]
for res in audiofiles:
 p=WORK/'game'/res.removeprefix('res://');record(p);probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=codec_name,sample_rate,channels,duration','-of','json',str(p)]));stream=probe['streams'][0];raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-f','f32le','-acodec','pcm_f32le','-']);values=array.array('f');values.frombytes(raw);assert values;peak=max(abs(v) for v in values);signal.append({'path':str(p.relative_to(WORK)),'sha256':sha(p),'codec':stream['codec_name'],'sample_rate':int(stream['sample_rate']),'channels':stream['channels'],'decoded_sample_values':len(values),'decoded_seconds':len(values)/(int(stream['sample_rate'])*stream['channels']),'peak':peak,'peak_dBFS':20*math.log10(peak) if peak else None,'RMS':math.sqrt(sum(v*v for v in values)/len(values)),'fullscale_or_over_samples':sum(abs(v)>=1 for v in values),'silent_entire_file':peak==0})
metrics['audio_signal_only']={'decoded_files':len(signal),'music_themes':[p['music']['id'] for p in packages],'music_states':[list(p['music']['profiles']) for p in packages],'cue_ids':list(polish['sfx']),'clips':signal,'subjective_listening_performed':False,'quality_or_new_artistic_acceptance':False}
# Observe actual runtime sheets and accepted compact state without granting ART approval.
metrics['runtime_character_art']={}
for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha']:
 kinds={}
 for kind in ['world','action','finisher']:
  p=WORK/'game/assets/art/characters'/actor/(kind+'.json')
  if p.exists():
   d=record(p);image=p.with_name(kind+'_sheet.png');record(image);assert sha(image)==d['sha256'];kinds[kind]={'source_cells':d.get('source_cells'),'schema':d.get('schema'),'sheet_sha256':sha(image),'sockets_present':p.with_name(kind+'.sockets.json').exists()}
 metrics['runtime_character_art'][actor]=kinds
metrics['evidence_sha256']=evidence;(OUT/'evidence-inspection.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'preview':metrics['current_packaged_preview'],'story':metrics['story_and_design'],'audio':{'decoded_files':len(signal),'fullscale_or_over_samples':sum(x['fullscale_or_over_samples'] for x in signal),'whole_silent_files':sum(x['silent_entire_file'] for x in signal)},'evidence_hashes':len(evidence)},ensure_ascii=False,indent=2))
