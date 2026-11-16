#!/usr/bin/env python3
"""Prepared independent offline actual-PCM audit. Execute only through ROOT serial stage.
No Godot, playback, Controller, network, Game/source writes or hearing claims.
"""
from pathlib import Path
import hashlib, importlib.util, json, math, re, subprocess, sys
sys.dont_write_bytecode=True
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 def pairs(rows):
  out={}
  for k,v in rows:
   if k in out: raise ValueError('duplicate JSON key '+k)
   out[k]=v
  return out
 def finite(v):
  x=float(v)
  if not math.isfinite(x):raise ValueError('nonfinite JSON')
  return x
 return json.loads(p.read_text(),object_pairs_hook=pairs,parse_float=finite,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def main():
 manifest=read(Q/'job-manifest.json');OUT=Q/'analysis-01'
 assert not OUT.exists(),'Fresh output only; never overwrite evidence'
 assert sha(Path(__file__))==manifest['entrypoint_sha256']
 for row in manifest['inputs']:assert sha(Path(row['path']))==row['sha256'],row['path']
 OUT.mkdir();checks=[]
 def check(ok,label,details=None):checks.append({'label':label,'passed':bool(ok),'details':details})
 spec=importlib.util.spec_from_file_location('unchanged_signal_helpers',Q/'signal_helpers.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
 paths={k:Path(v) for k,v in manifest['paths'].items()};native=paths['native'];prior=paths['prior'];W=paths['work'];job=paths['canonical_job']
 receipt=read(job/'receipt.json');inp=read(job/'input.json')
 check(receipt['operation']=='311fdc08f73e43169295d6a2d67786b0' and type(receipt['exit_code']) is int and receipt['exit_code']==1 and receipt['argv_sha256']==inp['argv_sha256'] and sha(job/'output.log')==receipt['log_sha256'],'actual failed outer tail receipt1 retained; own C01 stage separately gated')
 data=read(native/'replay/result.json');validation=read(native/'validation.json')
 check(validation['source_head']=='263e888afc9875ebf887267c0dd734b70897f344' and validation['scope']=='C01_HEADROOM_TARGETED_ONLY' and validation['passed'] is True and validation['headless'] is False and validation['source_unchanged_after_import'] is True and validation['phase_approval'] is False,'actual exact263 C01 targeted native validation; not fresh45 or fullphase')
 before=read(native/'source_hashes_before.json');after=read(native/'source_hashes_after.json');check(before==after,'all recorded C01 stage source keys unchanged',len(before))
 cmds=read(native/'commands.json');check(len(cmds)==1 and cmds[0]['name']=='contact_replay' and type(cmds[0]['exit_code']) is int and cmds[0]['exit_code']==0 and cmds[0]['passed'] is True and '--headless' not in cmds[0]['argv'] and '--write-movie' not in cmds[0]['argv'],'actual one nonMovie native command exit0')
 check((native/'contact_replay.log').read_text().rstrip().splitlines()[-1]=='exit_code=0','actual C01 native log final exit0')
 source_checks=read(native/'source_binding.json');check(len(source_checks)==80 and all(x['passed'] is True for x in source_checks),'actual80 C01 source binding checks')
 bus=(W/'game/default_bus_layout.tres').read_text();check('threshold_db = -5.0' in bus and 'ceiling_db = -3.0' in bus,'actual unchanged reviewed limiter threshold−5 / ceiling−3')
 check(data['passed'] is True and data['scope']=='C01_HEADROOM_TARGETED_ONLY' and data['renderer'] in ['X11','Wayland'] and data['actual_input'] is True and data['phase_approval'] is False and data['listening_performed'] is False and len(data['checks'])==61 and all(x['passed'] is True for x in data['checks']),'actual61 native checks and explicit no listening / phase acceptance')
 expected={'gabar_training_headroom_unarmed','timka_prime_headroom_blunt','pasha_training_headroom_firearm'}
 check(len(data['route_results'])==3 and {x['segment'] for x in data['route_results']}==expected and len(data['audio_events'])==3,'exact3 actualCoreInput routes only')
 entries=read(W/'game/assets/audio/character_finishers.json')['sfx'];check(len(entries)==20,'actual20 current source cue entries')
 contacts=[x for x in data['contacts'] if x.get('finisher')];check(len(contacts)==3,'actual3 finisher Core contacts')
 for c in contacts:
  events=[e for e in data['audio_events'] if (e['segment'],e['cue'],e['tick'],e['epoch'])==(c['segment'],c['cue'],c['tick'],c['epoch'])];voices=events[0]['streams'] if len(events)==1 else [];entry=entries[c['cue']]
  check(len(events)==1 and events[0]['source_pose']==1 and len(voices)==1 and voices[0]['path']==entry['path'] and voices[0]['bus']=='SFX' and voices[0]['gain_db']==-2.5 and voices[0]['pitch']==1 and voices[0]['loop']==0,'same Core contact cue/epoch/tick/pose1 and actual stream '+c['segment'])
 for r in data['route_results']:check(r['health']==0 and r['hits']==2 and r['damage_events']==2 and r['kills']==1 and r['score']==100 and isinstance(r['audio_events'],list) and len(r['audio_events'])==1 and r['audio_events']==[e for e in data['audio_events'] if e['segment']==r['segment']],'actual once damage/kill/score/audio '+r['segment'])
 decoded={};metrics={}
 for name in ['runtime_mix','solo_cues','stress_mix']:
  meta=data['mixer_captures'][name];p=native/'replay'/(name+'.wav');check(Path(meta['path'])==p,'actual recording path '+name)
  header,raw,channels,mono=h.decode(p);decoded[name]=(header,channels,mono)
  argv=['/usr/bin/ffmpeg','-hide_banner','-nostdin','-i',str(p),'-af','ebur128=peak=true','-f','null','-'];proc=subprocess.run(argv,capture_output=True,text=True,timeout=90)
  log=OUT/(name+'-ffmpeg.log');log.write_text(proc.stdout+proc.stderr+'\nexit_code='+str(proc.returncode)+'\n');values=re.findall(r'Peak:\s*([-+]?\d+(?:\.\d+)?)\s*dBFS',proc.stderr);tp=float(values[-1]) if values else None
  duration=header['frames']/header['rate'];wall=(meta['end_usec']-meta['start_usec'])/1e6;rails=sum(v in [-32768,32767] for v in raw)
  rows=[{'channel':i,'RMS_dBFS':h.db(h.rms(x)),'DC':math.fsum(x)/len(x),'sample_peak_dBFS':h.db(max(map(abs,x)))} for i,x in enumerate(channels)]
  m={'path':str(p),'sha256':sha(p),'header':header,'duration_seconds':duration,'monotonic_capture_seconds':wall,'duration_minus_wall_seconds':duration-wall,'channels':rows,'PCM_rail_samples':rails,'truepeak_FFmpeg_dBFS':tp,'FFmpeg_argv':argv,'FFmpeg_exit':proc.returncode,'FFmpeg_log_sha256':sha(log)};metrics[name]=m;write(OUT/(name+'.json'),m)
  check(header['rate']==44100 and header['width']==2 and header['channels']==2 and meta['driver']=='PulseAudio' and meta['code']==0 and meta['mix_rate']==44100 and abs(duration-wall)<.12,name+' real PCM16 stereo44100/PulseAudio duration')
  check(proc.returncode==0 and rails==0 and tp is not None and tp<0,name+' retained fullscale truepeak<0 / 0rails')
  check(tp is not None and tp<=-1,name+' retained practical headroom≤−1dBTP')
  check(all(math.isfinite(x['DC']) and abs(x['DC'])<.025 and -60<x['RMS_dBFS']<-1 for x in rows),name+' actual nonempty finite DC/RMS')
 accepted=read(paths['accepted_freeze']);pinned={Path(x['path']).name:x['sha256'] for x in accepted['records'] if x['path'].endswith('.wav')}
 oldcorr={e['cue']:e['new'] for e in read(prior/'analysis-01/solo-old-new-comparisons.json')['comparisons']}
 oldheader,_,_,oldmono=h.decode(paths['old_solo']);header,_,mono=decoded['solo_cues'];check(oldheader['rate']==header['rate']==44100,'actual old/current solo sample rates equal')
 check(len(data['solo_events'])==20 and {e['cue'] for e in data['solo_events']}==set(entries),'actual20 unique complete solo cues')
 comparisons=[]
 for e in data['solo_events']:
  cue=e['cue'];entry=entries[cue];p=W/'game'/entry['path'].removeprefix('res://');check(sha(p)==pinned[p.name]==entry['source_sha256'],cue+' actual c69 raw source identity')
  sourceheader,_,_,source=h.decode(p);check(sourceheader['rate']==44100 and sourceheader['channels']==1,cue+' actual source format')
  corr=h.correlation(source,mono,header['rate'],e['elapsed']);previous=oldcorr[cue];gain_delta=corr['source_projection_gain_db']-previous['source_projection_gain_db']
  a0=round(previous['best_start_seconds']*header['rate']);b0=round(corr['best_start_seconds']*header['rate']);a=oldmono[a0:a0+len(source)];b=mono[b0:b0+len(source)];assert len(a)==len(b)==len(source)>0
  ma=math.fsum(a)/len(a);mb=math.fsum(b)/len(b);pair=math.fsum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(math.fsum((x-ma)**2 for x in a)*math.fsum((y-mb)**2 for y in b))
  comparisons.append({'cue':cue,'actual_voice':e,'new':corr,'old_accepted_0dd':previous,'gain_delta_dB':gain_delta,'old_new_aligned_PCM_NCC':pair})
  voices=e['streams'];check(e['played'] is True and len(voices)==1 and voices[0]['path']==entry['path'] and voices[0]['bus']=='SFX' and voices[0]['gain_db']==-2.5 and voices[0]['format']==3 and voices[0]['pitch']==1 and voices[0]['loop']==0,cue+' actual solo QOA/stream/bus/gain')
  check(corr['NCC_fullrate']>=.70,cue+' unchanged source NCC≥0.70')
  check(abs(gain_delta)<=.25,cue+' unchanged quiet fit gain difference≤0.25dB',gain_delta)
  check(pair>=.98,cue+' unchanged quiet aligned PCM NCC≥0.98',pair)
 write(OUT/'solo-comparisons.json',{'scope':'ACTUAL_SAVED_PCM_SIGNAL_ONLY_NOT_LISTENING','comparisons':comparisons,'timing_offset':'Mixer block alignment, NOT input or hardware latency','global_normal_RMS_comparison':'Not compared: different route/music exposures'})
 check(len(data['stress_events'])==8 and all(e['played']==12 and e['active']==12 and e['dropped']==8 for e in data['stress_events']),'actual8×20 attempts /12 active /8 dropped')
 for e in data['stress_events']:
  rate=decoded['stress_mix'][0]['rate'];mono=decoded['stress_mix'][2];a=int(e['elapsed']*rate);b=min(len(mono),int((e['elapsed']+.35)*rate));check(b>a and h.db(h.rms(mono[a:b]))>-60,'actual nonempty stress energy window '+str(e['burst']))
 for e in data['audio_events']:
  rate=decoded['runtime_mix'][0]['rate'];mono=decoded['runtime_mix'][2];a=max(0,int((e['capture_elapsed']-.03)*rate));b=min(len(mono),int((e['capture_elapsed']+.35)*rate));check(b>a and h.db(h.rms(mono[a:b]))>-70,'actual normal music/cue energy window '+e['cue'])
 for row in manifest['inputs']:check(sha(Path(row['path']))==row['sha256'],'input bytes preserved '+row['label'])
 check(sha(Path(__file__))==manifest['entrypoint_sha256'],'entrypoint bytes preserved')
 result={'scope':'C01_TAIL02_THREE_ACTUAL_MIXER_PCM_SIGNAL_ONLY','passed':all(x['passed'] for x in checks),'checks':checks,'metrics':metrics,'source_head':validation['source_head'],'actual_Core_Input_routes':3,'actual_native_checks':61,'actual_solo_source_comparisons':20,'actual_stress_bursts':8,'prior45_Core_proof_reused_not_rerun':True,'engine_invocations':0,'agent_listening':False,'owner_prior_prototype_acceptance_historical_only':True,'phase_approval':False,'merge_approval':False,'native_Windows':'NOT_TESTED','FPS_or_hardware_latency':'NOT_MEASURED'}
 write(OUT/'result.json',result);print(json.dumps({'passed':result['passed'],'checks':len(checks),'failed':[x['label'] for x in checks if not x['passed']]}));return 0 if result['passed'] else 1
if __name__=='__main__':sys.exit(main())
