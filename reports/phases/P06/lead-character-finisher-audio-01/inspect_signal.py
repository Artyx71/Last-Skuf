from pathlib import Path
from array import array
import math,wave,json,hashlib,subprocess,re,sys,importlib.util,io
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-character-finisher-audio-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def db(x):return 20*math.log10(x) if x>0 else -180.
def dec(p):
 with wave.open(str(p),'rb') as f:
  h={'channels':f.getnchannels(),'rate':f.getframerate(),'width':f.getsampwidth(),'frames':f.getnframes(),'compression':f.getcomptype()};a=array('h',f.readframes(f.getnframes()))
 assert h['width']==2 and h['compression']=='NONE'
 if sys.byteorder!='little':a.byteswap()
 return h,a
manifest=json.loads((W/'game/assets/audio/character_finishers.json').read_text());entries=manifest['sfx'];assert len(entries)==20
expected={'gabar':['unarmed','blunt','firearm'],'olezhka':['unarmed','blunt','sharp'],'timka':['unarmed','blunt','environmental'],'ryzhik':['unarmed','blunt','environmental'],'tega':['unarmed','blunt','environmental'],'pasha':['unarmed','blunt','sharp','firearm','environmental']}
keys={'finish_'+a+('_prime' if a=='timka' else '')+'_'+c for a,cs in expected.items() for c in cs};assert keys==set(entries)
# Import math-only recipe read-only; main does not run. Independently rebuild WAV bytes in memory.
spec=importlib.util.spec_from_file_location('reviewed_c01_recipe',W/'assets/source_audio/character_finishers/render.py');recipe=importlib.util.module_from_spec(spec);spec.loader.exec_module(recipe)
source_stats=[];sources={}
for cue,e in sorted(entries.items()):
 p=W/'game'/e['path'].removeprefix('res://');src=W/'assets/source_audio/character_finishers'/p.name;assert p.read_bytes()==src.read_bytes();assert sha(p)==e['source_sha256']
 assert e['bus']=='SFX' and e['gain_db']==-2.5
 h,a=dec(p);assert h['channels']==1 and h['rate']==44100
 duration=h['frames']/h['rate'];rms=math.sqrt(math.fsum(v*v for v in a)/len(a))/32768;peak=max(map(abs,a))/32768
 assert 0.02<duration<2 and peak>0 and not any(v in [-32768,32767] for v in a) and a[0]==a[-1]==0
 rebuilt,_=recipe.render(e['actor_id'],e['category']);b=io.BytesIO()
 with wave.open(b,'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(44100);f.writeframes(rebuilt.tobytes())
 assert b.getvalue()==p.read_bytes()
 sources[cue]=list(a)
 source_stats.append({'cue':cue,'sha256':sha(p),'seconds':duration,'sample_peak_dBFS':db(peak),'RMS_dBFS':db(rms),'DC':math.fsum(a)/len(a)/32768,'rail_samples':0,'endpoints':[a[0],a[-1]],'recipe_memory_WAV_byte_exact':True})
put('source-signal-proofs.json',{'scope':'RAW_SOURCE_SIGNAL_NOT_LISTENING','source_WAV':source_stats,'exact_routes':expected,'voice_samples_or_external_generator_used_by_Lead':False})
refs=[]
def ref(p):refs.append({'path':str(p),'sha256':sha(p),'bytes':p.stat().st_size})
mix_stats=[];run_stats=[];decoded={}
for version,count,routes in [('native-01',518,45),('native-02',61,3)]:
 dpath=W/'reports/phases/P06/character-finisher-audio-01'/version;result=json.loads((dpath/'replay/result.json').read_text());assert result['passed'] is True and result['actual_input'] is True and len(result['checks'])==count and all(x['passed'] is True for x in result['checks'])
 assert len(result['route_results'])==routes and len(result['audio_events'])==routes
 before=json.loads((dpath/'source_hashes_before.json').read_text());after=json.loads((dpath/'source_hashes_after.json').read_text());assert before==after and len(before)==1465
 fs=[c for c in result['contacts'] if c.get('finisher')];assert len(fs)==routes
 for e in result['audio_events']:
  match=[c for c in fs if (c['tick'],c['epoch'],c['cue'])==(e['tick'],e['epoch'],e['cue'])];assert len(match)==1 and e['source_pose']==1 and len(e['streams'])==1
  stream=e['streams'][0];entry=entries.get(e['cue']) or json.loads((W/'game/assets/audio/combat_polish.json').read_text())['sfx'][e['cue']]
  assert stream['path']==entry['path'] and stream['bus']==entry['bus'] and stream['pitch']==1 and stream['loop']==0
  assert abs(stream['gain_db']-(entry.get('gain_db',0)-(5 if e['segment'].endswith('_reduced') else 0)))<1e-6
 for r in result['route_results']: assert r['health']==0 and r['hits']==2 and r['damage_events']==2 and r['score']==100 and r['kills']==1 and len(r['audio_events'])==1
 assert len(result['solo_events'])==20 and {e['cue'] for e in result['solo_events']}==keys
 assert len(result['stress_events'])==8 and all(e['active']==12 and e['played']==12 and e['dropped']==8 for e in result['stress_events'])
 run_stats.append({'native':version,'actual_checks':count,'actual_routes':routes,'contacts_same_Core_tick_source_pose1':routes,'once_outcomes_checked':routes,'solo_cues':20,'stress_8_bursts_12_active_8_dropped':True,'source_before_after1465_exact':True})
 for n,meta in result['mixer_captures'].items():
  p=Path(meta['path']);ref(p);h,a=dec(p);assert h['channels']==2 and h['rate']==44100 and meta['driver']=='PulseAudio' and meta['code']==0
  dur=h['frames']/h['rate'];wall=(meta['end_usec']-meta['start_usec'])/1e6;assert abs(dur-wall)<.12
  rms=math.sqrt(math.fsum(v*v for v in a)/len(a))/32768;rails=sum(v in [-32768,32767] for v in a)
  cmd=['ffmpeg','-hide_banner','-nostdin','-i',str(p),'-af','ebur128=peak=true','-f','null','-'];x=subprocess.run(cmd,capture_output=True,text=True,timeout=60);assert x.returncode==0
  log=O/(version+'-'+n+'-R128.log');log.write_text(x.stderr+'\nexit_code=0\n');tp=float(re.findall(r'Peak:\s*([-+]?\d+(?:\.\d+)?)\s*dBFS',x.stderr)[-1])
  # Separate 4x floating resample peak: mathematical reconstruction, never audio output.
  cmd2=['ffmpeg','-v','error','-nostdin','-i',str(p),'-af','aresample=176400','-f','f64le','-'];proc=subprocess.Popen(cmd2,stdout=subprocess.PIPE,stderr=subprocess.PIPE);overpeak=0.
  while True:
   b=proc.stdout.read(1048576)
   if not b:break
   values=array('d',b)
   if sys.byteorder!='little':values.byteswap()
   overpeak=max(overpeak,max(map(abs,values),default=0))
  err=proc.stderr.read();assert proc.wait()==0,err
  windows=[];stride=882*2
  for i in range(0,len(a),stride):
   z=a[i:i+stride];windows.append(db(math.sqrt(math.fsum(v*v for v in z)/len(z))/32768))
  row={'native':version,'capture':n,'sha256':sha(p),'header':h,'seconds':dur,'wall_seconds':wall,'sample_peak_dBFS':db(max(map(abs,a))/32768),'R128_truepeak_dBFS_rounded_0_1':tp,'independent_4x_swr_float_peak_dBFS':db(overpeak),'RMS_dBFS':db(rms),'rail_samples':rails,'DC':math.fsum(a)/len(a)/32768,'silent_20ms_windows_below_minus70dB':sum(v< -70 for v in windows),'windows20ms':len(windows),'R128_argv':cmd,'resample_peak_argv':cmd2,'heard':False}
  mix_stats.append(row);print(version,n,'TP',tp,'4x',round(db(overpeak),4),'rails',rails,flush=True)
  if version=='native-02': assert rails==0 and tp<0 and db(overpeak)<0
  if n=='solo_cues':decoded[version]=(h,list((a[2*i]+a[2*i+1])/2 for i in range(h['frames'])),result['solo_events'])
 ref(dpath/'replay/result.json');ref(dpath/'validation.json');ref(dpath/'source_hashes_before.json');ref(dpath/'source_hashes_after.json')
put('runtime-contact-proofs.json',run_stats);put('mixer-signal-proofs.json',{'scope':'ACTUAL_PCM_SIGNAL_ANALYSIS_NOT_HEARING','captures':mix_stats,'old_stress_failure_retained':True,'new_captures_subjectively_listened':False})
# Independent NCC: sparse stride8 coarse phase search, full-rate refinement +/-16 samples.
# Measures source identity in isolated recordings, not perceptual identity or input latency.
correlations=[]
for version,(h,y,events) in decoded.items():
 for ev in events:
  x=sources[ev['cue']];n=len(x);mean=math.fsum(x)/n;xc=[v-mean for v in x];ex=math.fsum(v*v for v in xc)
  center=round(ev['elapsed']*h['rate']);best=(-2,0)
  # Coarse index windows50ms around actual event; sparse samples are same phase for each trial.
  for start in range(max(0,center-5292),min(len(y)-n,center+6615),8):
   xs=xc[::8];ys=y[start:start+n:8];sm=math.fsum(ys);ey=math.fsum(v*v for v in ys)-sm*sm/len(ys);dot=math.fsum(a*b for a,b in zip(xs,ys));es=math.fsum(v*v for v in xs)
   c=dot/math.sqrt(es*ey) if ey>0 else -1
   if c>best[0]:best=(c,start)
  full=(-2,0)
  for start in range(max(0,best[1]-16),min(len(y)-n,best[1]+16)+1):
   yy=y[start:start+n];sm=math.fsum(yy);ey=math.fsum(v*v for v in yy)-sm*sm/n;dot=math.fsum(a*b for a,b in zip(xc,yy));c=dot/math.sqrt(ex*ey) if ey>0 else -1
   if c>full[0]:full=(c,start)
  assert full[0]>.90,(version,ev['cue'],full)
  correlations.append({'native':version,'cue':ev['cue'],'NCC_fullrate':full[0],'capture_start_seconds':full[1]/h['rate'],'relative_to_monotonic_cue_ms':1000*(full[1]/h['rate']-ev['elapsed']),'hearing':False,'input_latency_measurement':False})
 print('NCC',version,'20 cues',flush=True)
put('solo-source-correlation-proofs.json',{'method':'Independent sparse stride8 lag search then full44100Hz NCC refinement; actual isolated QOA stream vs sourcePCM; not listening and not input latency','events':correlations})
put('signal-input-references.json',{'records':refs})
print('OWN_SIGNAL_AND_ROUTE_CHECKS_COMPLETE')
