#!/usr/bin/env python3
"""Independent fresh headroom PCM measurement ONLY. Root serial stage executes; no Godot."""
from pathlib import Path
import hashlib,importlib.util,json,math,re,subprocess,sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent;OUT=Q/'analysis-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
spec=importlib.util.spec_from_file_location('unchanged_QA01_signal_helpers',Q/'signal_helpers.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
def local_tp(x):
 # Diagnostic subset oracle: each50ms block's largest sample neighborhood ±128frames.
 # Uses actual surrounding full-file values, not abrupt zero-padded cropped snippets.
 phases=[]
 for p in range(1,8):
  t=p/8;weights=[]
  for offset in range(-15,17):
   d=t-offset;weights.append((offset,(math.sin(math.pi*d)/(math.pi*d) if d else 1)*(math.sin(math.pi*d/16)/(math.pi*d/16) if d else 1)))
  total=math.fsum(w for _,w in weights);phases.append([(o,w/total) for o,w in weights])
 positions=set()
 for start in range(0,len(x),2205):
  stop=min(len(x),start+2205);peak=max(range(start,stop),key=lambda k:abs(x[k]))
  positions.update(range(max(0,peak-128),min(len(x),peak+129)))
 maximum=max(map(abs,x),default=0)
 for i in sorted(positions):
  for weights in phases:
   value=math.fsum(x[i+offset]*weight for offset,weight in weights if 0<=i+offset<len(x));maximum=max(maximum,abs(value))
 return {'estimated_dBTP':h.db(maximum),'fractional_positions_examined':len(positions)*7,'sample_frames_examined':len(x),'method':'8× finite32tap/DCnormalized Lanczos-sinc over explicitly selected ±128-frame windows around each50ms block max; full-file neighboring context; diagnostic subset NOT a global bound or certified meter'}
def main():
 assert not OUT.exists(),'Preserve prior results; fresh output only'
 for name in ['native-input-freeze.json','source-PCM-reference-freeze.json']:
  for row in read(Q/name)['records']:assert sha(Path(row['path']))==row['sha256'],row['path']
 OUT.mkdir();checks=[]
 def check(ok,label,details=None):checks.append({'label':label,'passed':bool(ok),'details':details})
 native=Q/'native-inputs';data=read(native/'replay/result.json');validation=read(native/'validation.json');receipt=read(native/'root-job/receipt.json');inp=read(native/'root-job/input.json')
 check(receipt['exit_code']==0 and receipt['operation']=='967d7134e2124246bed2f544cf5647fd' and receipt['argv_sha256']==inp['argv_sha256'] and sha(native/'root-job/output.log')==receipt['log_sha256'],'actual freshnative receipt/argv/log0')
 check(validation['source_head']=='0dd1cc4dad9379c457e277969b721fcc23a14fe3' and validation['scope']=='C01_HEADROOM_TARGETED_ONLY' and validation['passed'] is True and validation['source_unchanged_after_import'] is True,'actual exact0dd targeted scope not fresh45')
 check(read(native/'source_hashes_before.json')==read(native/'source_hashes_after.json'),'all1465 freshnative sourcekeys unchanged')
 delta=read(Q/'source-equivalence.json');check(delta['unchanged']==1460 and len(delta['changed'])==5,'explicit old45 proofs reuse with1460unchanged/5expectedkeys')
 bus=(Q/'source/game/default_bus_layout.tres').read_text();check('threshold_db = -5.0' in bus and 'ceiling_db = -3.0' in bus,'actual selected bus threshold−5/ceiling−3')
 check(data['passed'] is True and data['renderer'] in ['X11','Wayland'] and data['actual_input'] is True and len(data['checks'])==61 and all(x['passed'] is True for x in data['checks']),'actual61 new native checks')
 expected={'gabar_training_headroom_unarmed','timka_prime_headroom_blunt','pasha_training_headroom_firearm'}
 check(len(data['route_results'])==3 and {x['segment'] for x in data['route_results']}==expected and len(data['audio_events'])==3,'exact3 new actualCoreInput routes, not45')
 entries=read(Q/'source/game/assets/audio/character_finishers.json')['sfx']
 finisher=[c for c in data['contacts'] if c.get('finisher')];check(len(finisher)==3,'actual3 finisher Core contacts')
 for contact in finisher:
  events=[e for e in data['audio_events'] if (e['segment'],e['cue'],e['tick'],e['epoch'])==(contact['segment'],contact['cue'],contact['tick'],contact['epoch'])];voices=events[0]['streams'] if len(events)==1 else [];entry=entries[contact['cue']]
  check(len(events)==1 and events[0]['source_pose']==1 and len(voices)==1 and voices[0]['path']==entry['path'] and voices[0]['bus']=='SFX' and voices[0]['gain_db']==-2.5 and voices[0]['pitch']==1 and voices[0]['loop']==0,'samecontact actualstream/gain '+contact['segment'])
 for route in data['route_results']:check(route['health']==0 and route['hits']==2 and route['damage_events']==2 and route['kills']==1 and route['score']==100,'actual oncekill/score '+route['segment'])
 decoded={};metrics={}
 for name in ['runtime_mix','solo_cues','stress_mix']:
  meta=data['mixer_captures'][name];path=Path(meta['path']);header,raw,channels,mono=h.decode(path);decoded[name]=(header,channels,mono)
  argv=['/usr/bin/ffmpeg','-hide_banner','-nostdin','-i',str(path),'-af','ebur128=peak=true','-f','null','-'];p=subprocess.run(argv,capture_output=True,text=True,timeout=90);log=OUT/(name+'-ffmpeg.log');log.write_text(p.stdout+p.stderr+'\nexit_code='+str(p.returncode)+'\n');values=re.findall(r'Peak:\s*([-+]?\d+(?:\.\d+)?)\s*dBFS',p.stderr);tp=float(values[-1]) if values else None
  duration=header['frames']/header['rate'];wall=(meta['end_usec']-meta['start_usec'])/1e6;rails=sum(v in [-32768,32767] for v in raw);rows=[{'channel':i,'RMS_dBFS':h.db(h.rms(x)),'DC':math.fsum(x)/len(x),'sample_peak_dBFS':h.db(max(map(abs,x)))} for i,x in enumerate(channels)]
  metric={'path':str(path),'sha256':sha(path),'header':header,'duration_seconds':duration,'monotonic_capture_seconds':wall,'duration_minus_wall_seconds':duration-wall,'channels':rows,'PCM_rail_samples':rails,'truepeak_FFmpeg_dBFS':tp,'FFmpeg_argv':argv,'FFmpeg_exit':p.returncode,'FFmpeg_log_sha256':sha(log)};metrics[name]=metric;write(OUT/(name+'.json'),metric)
  check(header['rate']==44100 and header['width']==2 and header['channels']==2 and meta['driver']=='PulseAudio' and meta['code']==0 and abs(duration-wall)<.12,name+' actual PCM16stereo44100/PulseAudio andduration')
  check(p.returncode==0 and rails==0 and tp is not None and tp<0,name+' unchanged fullscale gate truepeak<0/0rails')
  check(tp is not None and tp<=-1,name+' declared practical margin target≤−1dBTP')
  check(all(abs(x['DC'])<.025 and -60<x['RMS_dBFS']<-1 for x in rows),name+' actual finiteDC/nonempty level')
 old=Q.parent/'closure-01';oldcorr={e['cue']:e for e in read(Q/'prior-QA01/pcm-analysis-01/solo-source-correlations.json')['events']};oldsolo_path=next(Path(r['path']) for r in read(Q/'source-PCM-reference-freeze.json')['records'] if r['path'].endswith('/native-01/replay/solo_cues.wav'));oldheader,_,_,oldmono=h.decode(oldsolo_path)
 accepted_path=next(Path(r['path']) for r in read(Q/'source-PCM-reference-freeze.json')['records'] if r['path'].endswith('audio-c01-signal-review-01/input-freeze.json'));accepted=read(accepted_path);pinned={Path(x['path']).name:x['sha256'] for x in accepted['records'] if x['path'].endswith('.wav')};references={Path(r['path']).name:Path(r['path']) for r in read(Q/'source-PCM-reference-freeze.json')['records'] if r['path'].endswith('.wav') and '/game/assets/audio/character_finishers/' in r['path']}
 comparisons=[];header,channels,mono=decoded['solo_cues'];check(len(data['solo_events'])==20 and {e['cue'] for e in data['solo_events']}==set(entries),'fresh actual20 solo stream identities')
 for event in data['solo_events']:
  cue=event['cue'];path=references[cue+'.wav'];check(sha(path)==pinned[path.name]==entries[cue]['source_sha256'],cue+' actual source stillc69 bytes')
  sourceheader,_,_,source=h.decode(path);corr=h.correlation(source,mono,header['rate'],event['elapsed']);prior=oldcorr[cue];gain_delta=corr['source_projection_gain_db']-prior['source_projection_gain_db']
  oldstart=round(prior['best_start_seconds']*header['rate']);newstart=round(corr['best_start_seconds']*header['rate']);a=oldmono[oldstart:oldstart+len(source)];b=mono[newstart:newstart+len(source)];mean_a=math.fsum(a)/len(a);mean_b=math.fsum(b)/len(b);pair=math.fsum((x-mean_a)*(y-mean_b) for x,y in zip(a,b))/math.sqrt(math.fsum((x-mean_a)**2 for x in a)*math.fsum((y-mean_b)**2 for y in b))
  comparisons.append({'cue':cue,'actual_voice':event,'new':corr,'old':prior,'new_minus_old_source_projection_gain_dB':gain_delta,'old_new_aligned_PCM_NCC':pair})
  check(event['played'] is True and len(event['streams'])==1 and event['streams'][0]['path']==entries[cue]['path'] and event['streams'][0]['gain_db']==-2.5 and event['streams'][0]['format']==3,cue+' actual importedQOA/voicegain')
  check(corr['NCC_fullrate']>=.70,cue+' unchanged sourceNCC≥0.70 gate')
  check(abs(gain_delta)<=.25,cue+' actual quiet source-fit gainchange≤0.25dB',gain_delta)
  check(pair>=.98,cue+' actual old/new alignedsolo waveform NCC≥0.98',pair)
 write(OUT/'solo-old-new-comparisons.json',{'scope':'ACTUAL_SAVED_SOLO_PCM_COMPARISON_NOT_SUBJECTIVE_LISTENING','comparisons':comparisons,'prespecified_source_NCC_min':.70,'prespecified_fit_gain_delta_max_dB':.25,'prespecified_old_new_PCM_NCC_min':.98,'full_normalmix_globalRMS_not_compared':'Different route exposures: old45/110s vs new3/4.5s; not comparable as same soundtrack segment'})
 check(len(data['stress_events'])==8 and all(x['played']==12 and x['active']==12 and x['dropped']==8 for x in data['stress_events']),'actual same8bursts12played/active8dropped')
 for event in data['stress_events']:
  header,_,mono=decoded['stress_mix'];a=int(event['elapsed']*header['rate']);b=min(len(mono),int((event['elapsed']+.35)*header['rate']));check(h.db(h.rms(mono[a:b]))>-60,'actual stress PCMwindow burst'+str(event['burst']))
 oldstress_path=next(Path(r['path']) for r in read(Q/'source-PCM-reference-freeze.json')['records'] if r['path'].endswith('/native-01/replay/stress_mix.wav'));_,_,oldchannels,_=h.decode(oldstress_path)
 local={'old_failed_stress':[local_tp(x) for x in oldchannels],'new_candidate_stress':[local_tp(x) for x in decoded['stress_mix'][1]],'scope':'Diagnostic independent finite-sinc subset; FFmpeg full-file truepeak remains global gate'};write(OUT/'local-8x-truepeak-corroboration.json',local)
 check(all(x['estimated_dBTP']<0 for x in local['new_candidate_stress']),'independent finite-sinc candidate neighborhoods belowfullscale')
 for name in ['native-input-freeze.json','source-PCM-reference-freeze.json']:
  for row in read(Q/name)['records']:check(sha(Path(row['path']))==row['sha256'],'frozen read-only input preserved '+Path(row['path']).name)
 output={'scope':'C01_Q03_INDEPENDENT_FRESH_TARGETED_MIXER_TECHNICAL_CLOSURE_ONLY','passed':all(x['passed'] for x in checks),'checks':checks,'actual_native_checks_audited':61,'actual_new_Core_routes':3,'old45Core_proofs_reused_not_rerun':True,'actual_solo_source_comparisons':20,'actual_stress_bursts':8,'actual_PCM_files':3,'actual_new_engine_invocations_by_this_job':0,'actual_agent_listening':False,'owner_prior_listening_not_claimed_for_new_files':True,'full_C01_or_phase_approval':False,'merge_approval':False,'native_Windows':'NOT_TESTED','hardware_latency_or_FPS':'NOT_MEASURED'};write(OUT/'result.json',output);print(json.dumps({'passed':output['passed'],'checks':len(checks),'failed':[x['label'] for x in checks if not x['passed']]}));return 0 if output['passed'] else 1
if __name__=='__main__':sys.exit(main())
