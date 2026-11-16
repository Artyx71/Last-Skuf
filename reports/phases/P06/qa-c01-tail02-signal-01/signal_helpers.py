#!/usr/bin/env python3
"""Independent actual saved engine PCM analysis. No Godot, playback, hearing or Game writes."""
from pathlib import Path
from array import array
import cmath,hashlib,json,math,re,subprocess,sys,time,wave
Q=Path(__file__).resolve().parent;OUT=Q/'pcm-analysis-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def db(x):return 20*math.log10(x) if x>0 else -160.0
def rms(x):return math.sqrt(math.fsum(v*v for v in x)/max(1,len(x)))
def decode(p):
 with wave.open(str(p),'rb') as f:
  header={'channels':f.getnchannels(),'width':f.getsampwidth(),'rate':f.getframerate(),'frames':f.getnframes(),'compression':f.getcomptype()};b=f.readframes(f.getnframes())
 assert header['width']==2 and header['compression']=='NONE'
 raw=array('h');raw.frombytes(b)
 if sys.byteorder!='little':raw.byteswap()
 assert len(raw)==header['channels']*header['frames']
 channels=[array('f',(v/32768.0 for v in raw[i::header['channels']])) for i in range(header['channels'])]
 mono=array('f',(math.fsum(values)/len(values) for values in zip(*channels)))
 return header,raw,channels,mono

def fft(values,inverse=False):
 a=list(map(complex,values));n=len(a);j=0
 for i in range(1,n):
  bit=n>>1
  while j&bit:j^=bit;bit>>=1
  j^=bit
  if i<j:a[i],a[j]=a[j],a[i]
 length=2
 while length<=n:
  step=cmath.exp((2j if inverse else -2j)*math.pi/length)
  for start in range(0,n,length):
   w=1+0j
   for k in range(length//2):
    u=a[start+k];v=a[start+k+length//2]*w
    a[start+k]=u+v;a[start+k+length//2]=u-v;w*=step
  length*=2
 return [v/n for v in a] if inverse else a

def down4(x):return [math.fsum(x[i:i+4])/4 for i in range(0,len(x)-3,4)]
def correlation(source,observed,rate,elapsed):
 # Search ±120ms around actual monotonic cue timestamp. Mixer block delay is measured, not presumed zero.
 begin=max(0,int((elapsed-.12)*rate));end=min(len(observed),int((elapsed+len(source)/rate+.15)*rate))
 segment=observed[begin:end];x=down4(source);y=down4(segment);n=len(x)
 assert n>0 and len(y)>=n
 mean=math.fsum(x)/n;x=[v-mean for v in x];energy=math.fsum(v*v for v in x)
 size=1
 while size<len(x)+len(y)-1:size*=2
 xf=fft(list(reversed(x))+[0.0]*(size-n));yf=fft(y+[0.0]*(size-len(y)));conv=fft([a*b for a,b in zip(xf,yf)],True)
 sums=[0.0];squares=[0.0]
 for v in y:sums.append(sums[-1]+v);squares.append(squares[-1]+v*v)
 best=(-2.0,0)
 for lag in range(len(y)-n+1):
  variance=max(0.0,squares[lag+n]-squares[lag]-(sums[lag+n]-sums[lag])**2/n)
  value=conv[lag+n-1].real/math.sqrt(energy*variance) if energy>0 and variance>1e-25 else 0.0
  if value>best[0]:best=(value,lag)
 # Full44.1kHz refinement avoids decimation-phase artefacts, especially noisy high-band Ryzhik cues.
 source_mean=math.fsum(source)/len(source);centered=[v-source_mean for v in source];sx=math.fsum(v*v for v in centered);full=(-2.0,0,0.0)
 candidate=begin+best[1]*4
 for absolute in range(max(0,candidate-16),min(len(observed)-len(source),candidate+16)+1):
  observed_part=observed[absolute:absolute+len(source)];sy=math.fsum(observed_part);sy2=math.fsum(v*v for v in observed_part)-sy*sy/len(source)
  dot=math.fsum(a*b for a,b in zip(centered,observed_part));value=dot/math.sqrt(sx*sy2) if sx>0 and sy2>1e-25 else 0.0
  if value>full[0]:full=(value,absolute,dot/sx if sx else 0.0)
 return {'NCC_fullrate':full[0],'NCC_coarse_down4':best[0],'best_start_seconds':full[1]/rate,'relative_to_reported_cue_ms':1000*(full[1]/rate-elapsed),'source_projection_gain_db':db(abs(full[2])),'observed_window_RMS_dbFS':db(rms(segment)),'search_window_seconds':[begin/rate,end/rate]}

def main():
 assert not OUT.exists(),'Fresh outputs only; preserve failed/successful analysis'
 freeze=read(Q/'native-input-freeze.json')
 for row in freeze['records']:assert sha(Path(row['path']))==row['sha256'],row['path']
 OUT.mkdir();checks=[]
 def check(ok,label,details=None):checks.append({'label':label,'passed':bool(ok),'details':details})
 native=Q/'native-inputs';result=read(native/'replay/result.json');validation=read(native/'validation.json')
 receipt=read(native/'root-job/receipt.json');inp=read(native/'root-job/input.json')
 check(receipt['exit_code']==0 and receipt['operation']==freeze['native_operation'] and receipt['argv_sha256']==inp['argv_sha256'] and sha(native/'root-job/output.log')==receipt['log_sha256'],'actual canonical native exit0/argv/log receipt')
 before=read(native/'source_hashes_before.json');after=read(native/'source_hashes_after.json')
 check(before==after and len(before)==1465,'actual all1465 native source keys unchanged')
 check(validation['source_head']==freeze['source_head'] and validation['passed'] is True and validation['source_unchanged_after_import'] is True,'native validation exactf615/no changedsource')
 check(result['renderer'] in ['X11','Wayland'] and result['passed'] is True and result['actual_input'] is True and all(x['passed'] is True for x in result['checks']),'actual native result positive +all518checks')
 check(len(result['checks'])==518 and len(result['route_results'])==45 and len(result['audio_events'])==45,'actual518/45routes/45events counts')
 check(len(list((native/'replay').glob('*.png')))==45,'45 actual bound PNGfiles')
 check((native/'contact_replay.log').read_text().rstrip().splitlines()[-1]=='exit_code=0','actual replay log final exit0')
 manifest=read(Q/'engine-source-game/assets/audio/character_finishers.json');entries=manifest['sfx'];polish=read(Q/'engine-source-game/assets/audio/combat_polish.json')['sfx'];allentries={**polish,**entries}
 accepted=read(Q/'source-binding-fixture/reports/phases/P06/audio-c01-signal-review-01/input-freeze.json');pinned={Path(x['path']).name:x['sha256'] for x in accepted['records'] if x['path'].endswith('.wav')}
 sources={};source_formats={}
 for cue,entry in entries.items():
  p=Q/'source-binding-fixture/game/assets/audio/character_finishers'/(cue+'.wav');check(sha(p)==pinned[p.name]==entry['source_sha256'],cue+' actual source bytes signal-pinned')
  header,raw,channels,mono=decode(p);sources[cue]=mono;source_formats[cue]=header
 finisher_contacts=[x for x in result['contacts'] if x.get('finisher')]
 check(len(finisher_contacts)==45,'actual45 finisher Core contacts')
 for contact in finisher_contacts:
  hits=[e for e in result['audio_events'] if (e['segment'],e['tick'],e['epoch'],e['cue'])==(contact['segment'],contact['tick'],contact['epoch'],contact['cue'])]
  streams=hits[0]['streams'] if len(hits)==1 else []
  entry=allentries[contact['cue']];gain=entry.get('gain_db',0)-(5 if contact['segment'].endswith('_reduced') else 0)
  check(len(hits)==1 and hits[0]['source_pose']==1 and len(streams)==1 and streams[0]['path']==entry['path'] and streams[0]['bus']==entry['bus'] and streams[0]['gain_db']==gain and streams[0]['pitch']==1 and streams[0]['loop']==0,'actual sameclock contact/ownstream/bus/gain '+contact['segment'])
 for route in result['route_results']:
  check(route['health']==0 and route['hits']==2 and route['damage_events']==2 and route['kills']==1 and route['score']==100 and len(route['audio_events'])==1,'actual earned stun+once kill/score '+route['segment'])
 profiles={};decoded={};ffmpeg=Path('/usr/bin/ffmpeg')
 for name in ['runtime_mix','solo_cues','stress_mix']:
  path=Path(result['mixer_captures'][name]['path']);meta=result['mixer_captures'][name]
  header,raw,channels,mono=decode(path);decoded[name]=(header,channels,mono)
  assert header['rate']==44100,'Current native44100 expected; future resample requires separately frozen implementation'
  duration=header['frames']/header['rate'];wall=(meta['end_usec']-meta['start_usec'])/1e6
  argv=[str(ffmpeg),'-hide_banner','-nostdin','-i',str(path),'-af','ebur128=peak=true','-f','null','-']
  proc=subprocess.run(argv,capture_output=True,text=True,timeout=90);log=OUT/(name+'-ffmpeg.log');log.write_text(proc.stdout+proc.stderr+'\nexit_code='+str(proc.returncode)+'\n')
  peaks=re.findall(r'Peak:\s*([-+]?\d+(?:\.\d+)?)\s*dBFS',proc.stderr);truepeak=float(peaks[-1]) if peaks else None
  channel_rows=[]
  for i,x in enumerate(channels):
   windows=[db(rms(x[start:start+2205])) for start in range(0,len(x),2205)]
   channel_rows.append({'channel':i,'RMS_dBFS':db(rms(x)),'DC':math.fsum(x)/len(x),'sample_peak_dBFS':db(max(abs(v) for v in x)),'windows50ms_RMS_dBFS':windows,'min50ms_RMS_dBFS':min(windows),'max50ms_RMS_dBFS':max(windows)})
  rails=sum(v in [-32768,32767] for v in raw)
  metric={'path':str(path),'sha256':sha(path),'header':header,'duration_seconds':duration,'reported_wall_capture_seconds':wall,'duration_minus_wall_seconds':duration-wall,'channel_metrics':channel_rows,'PCM_rail_samples':rails,'ffmpeg_truepeak_dBFS':truepeak,'ffmpeg_command':argv,'ffmpeg_exit':proc.returncode,'ffmpeg_log_sha256':sha(log),'endpoints_not_gated':'continuous music/intentional recording boundaries; dry-source quiet endpoint gate does not apply to this mix'}
  profiles[name]=metric;write(OUT/(name+'.json'),metric)
  check(header['channels']==2 and header['width']==2 and meta['driver']!='Dummy' and meta['mix_rate']==header['rate'] and meta['code']==0,name+' actual stereo44100 PCM16 realdriver')
  check(abs(duration-wall)<.12,name+' real sampleduration vs monotoniccapture ±120ms',{'difference_seconds':duration-wall})
  check(rails==0 and truepeak is not None and truepeak<0 and proc.returncode==0,name+' no PCMrails/no fullscale truepeak')
  check(all(abs(row['DC'])<.025 and -60<row['RMS_dBFS']<-1 for row in channel_rows),name+' finite DC and nonempty level')
 solo=[];header,channels,mono=decoded['solo_cues']
 check(len(result['solo_events'])==20 and {e['cue'] for e in result['solo_events']}==set(entries),'actual20 solo entries exactroute set')
 for event in result['solo_events']:
  cue=event['cue'];source=sources[cue];corr=correlation(source,mono,header['rate'],event['elapsed']);solo.append({'cue':cue,'actual_event':event,**corr})
  check(event['played'] is True and len(event['streams'])==1 and event['streams'][0]['path']==entries[cue]['path'] and event['streams'][0]['format']==3 and event['streams'][0]['gain_db']==-2.5,cue+' actual solo QOA voice+accepted gain')
  check(corr['NCC_fullrate']>=.70,cue+' actual soloPCM/source NCC >=0.70 (not hearing)',corr)
 write(OUT/'solo-source-correlations.json',{'scope':'ACTUAL_QOA_IMPORTED_SOLO_VS_ACCEPTED_RAW_PCM_SIGNAL_NOT_LISTENING','method':'FFT lag search down4 ±120ms then exact44100Hz normalized correlation refinement ±16samples; offset is mixer capture alignment, NOT input-action latency','NCC_acceptance_threshold_declared_before_execution':.70,'no_assertion_of_bitexact_imported_PCM_QOA_is_lossy':True,'events':solo})
 h,ch,mono=decoded['runtime_mix'];events=[]
 for event in result['audio_events']:
  start=max(0,int((event['capture_elapsed']-.03)*h['rate']));end=min(len(mono),int((event['capture_elapsed']+.35)*h['rate']))
  energy=db(rms(mono[start:end]));events.append({'segment':event['segment'],'cue':event['cue'],'capture_elapsed':event['capture_elapsed'],'window_RMS_dBFS':energy})
  check(energy>-70,'actual runtime PCM eventwindow nonempty '+event['segment'])
 write(OUT/'runtime-event-energy.json',{'scope':'ACTUAL_PCM_WINDOWS_WITH_MUSIC_NOT_ISOLATED_SOURCE_IDENTIFICATION','events':events,'legacy5_not_claimed_isolated_solo_source_correlation':True})
 check(len(result['stress_events'])==8 and all(e['active']==12 and e['played']==12 and e['dropped']==8 for e in result['stress_events']),'actual eight bursts bounded12played/12active/8drops')
 stress_windows=[];h,ch,mono=decoded['stress_mix']
 for event in result['stress_events']:
  a=max(0,int(event['elapsed']*h['rate']));b=min(len(mono),int((event['elapsed']+.35)*h['rate']));level=db(rms(mono[a:b]));stress_windows.append({'burst':event['burst'],'RMS_dBFS':level});check(level>-60,'stressburst actual PCM nonempty '+str(event['burst']))
 write(OUT/'stress-windows.json',{'actual_windows':stress_windows,'voice_ceiling_verified_from_actual_event_records_not_inferred_from_waveform':True})
 for row in freeze['records']:check(sha(Path(row['path']))==row['sha256'],'native frozen input unchanged '+Path(row['path']).name)
 all_ok=all(x['passed'] for x in checks)
 output={'scope':'INDEPENDENT_C01_ACTUAL_RUNTIME_PCM_SIGNAL_ONLY_NOT_LISTENING','passed':all_ok,'checks':checks,'counts':{'checks':len(checks),'native_checks_audited':518,'actual_finisher_contacts':45,'actual_solo_source_correlations':len(solo),'stress_bursts':8,'actual_mix_WAV':3},'native_source_head':freeze['source_head'],'source_binding_actual_source_candidates':20,'QOA_lossy_import_explicit':True,'PCM_mix_analysis':True,'actual_listening':False,'artistic_approval':False,'full_C01_approval':False,'phase_approval':False,'merge_approval':False,'physical_hardware_latency':'NOT_MEASURED; capture offsets/outputlatency are not input-action latency','native_Windows':'NOT_TESTED','FPS':'NOT_MEASURED'}
 write(OUT/'result.json',output);print(json.dumps({'passed':all_ok,'checks':len(checks),'failed':[x['label'] for x in checks if not x['passed']]}));return 0 if all_ok else 1
if __name__=='__main__':sys.exit(main())
