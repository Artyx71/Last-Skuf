#!/usr/bin/env python3
"""Independent C01 offline source signal audit. No Godot, integration or listening."""
from pathlib import Path
import array,ast,cmath,csv,hashlib,json,math,os,re,statistics,subprocess,sys,time,wave,itertools
Q=Path(__file__).resolve().parent
FROZEN=json.loads((Q/'input-freeze.json').read_text())
C=Path(FROZEN['candidate_directory'])
ROOT=Q.parents[3]
WORK=ROOT/'.autopilot/worktrees/P06'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,value):p.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def db(value):return 20*math.log10(max(float(value),1e-12))
def cosine(a,b):
 den=math.sqrt(sum(v*v for v in a)*sum(v*v for v in b))
 return sum(x*y for x,y in zip(a,b))/den if den else 0.0

def fft(values):
 n=len(values);bits=n.bit_length()-1
 out=[0j]*n
 for i,v in enumerate(values):
  j=0;k=i
  for _ in range(bits):j=(j<<1)|(k&1);k>>=1
  out[j]=complex(v)
 step=2
 while step<=n:
  half=step//2;tw=[cmath.exp(-2j*math.pi*k/step) for k in range(half)]
  for start in range(0,n,step):
   for k in range(half):
    a=out[start+k];b=out[start+k+half]*tw[k];out[start+k]=a+b;out[start+k+half]=a-b
  step*=2
 return out

def spectrum(signal,rate):
 nfft=4096;hop=1024
 starts=list(range(0,max(1,len(signal)-nfft+1),hop))
 tail=max(0,len(signal)-nfft)
 if tail not in starts:starts.append(tail)
 window=[.5-.5*math.cos(2*math.pi*i/(nfft-1)) for i in range(nfft)]
 power=[0.0]*(nfft//2+1)
 for start in starts:
  values=[(signal[start+i] if start+i<len(signal) else 0.0)*window[i] for i in range(nfft)]
  f=fft(values)
  for k in range(1,len(power)):power[k]+=abs(f[k])**2
 total=sum(power);freq=[k*rate/nfft for k in range(len(power))]
 centroid=sum(f*p for f,p in zip(freq,power))/max(total,1e-30)
 bandwidth=math.sqrt(sum((f-centroid)**2*p for f,p in zip(freq,power))/max(total,1e-30))
 roll=0.0;acc=0.0
 for f,p in zip(freq,power):
  acc+=p
  if acc>=.85*total:roll=f;break
 bands=[0.0]*32
 for f,p in zip(freq[1:],power[1:]):
  if f<20:continue
  b=max(0,min(31,int(math.log(f/20)/math.log((rate/2)/20)*32)))
  bands[b]+=p
 norm=sum(bands)
 bins=[v/max(norm,1e-30) for v in bands]
 positive=power[1:]
 flat=math.exp(sum(math.log(max(v,1e-30)) for v in positive)/len(positive))/(sum(positive)/len(positive)+1e-30)
 return {'method':'4096-point Hann STFT,1024hop,last fullwindow retained,32 logarithmic bands20Hz..Nyquist','windows':len(starts),'centroid_hz':centroid,'bandwidth_hz':bandwidth,'rolloff85_hz':roll,'flatness':flat,'normalized_log_band_power32':bins}

POLYPHASE={}
def true_peak_estimate(signal,factor=8,radius=16):
 key=(factor,radius)
 if key not in POLYPHASE:
  phases=[]
  for phase in range(1,factor):
   t=phase/factor;items=[]
   for offset in range(-radius+1,radius+1):
    d=t-offset
    sinc=math.sin(math.pi*d)/(math.pi*d) if d else 1.0
    lanczos=math.sin(math.pi*d/radius)/(math.pi*d/radius) if d else 1.0
    items.append((offset,sinc*lanczos))
   scale=sum(v for _,v in items);phases.append([(i,v/scale) for i,v in items])
  POLYPHASE[key]=phases
 peak=max(map(abs,signal),default=0.0);length=len(signal)
 for i in range(-radius,length+radius):
  for phase in POLYPHASE[key]:
   value=0.0
   for offset,weight in phase:
    k=i+offset
    if 0<=k<length:value+=signal[k]*weight
   peak=max(peak,abs(value))
 return {'peak':peak,'dbtp_estimate':db(peak),'method':'8x finite bandlimited Lanczos-windowed sinc;32taps per fractionalphase,DCnormalized,zero-padded edges; estimate not certified meter'}

def envelope(signal,rate):
 energy=sum(v*v for v in signal);acc=0.0;quantiles={};targets=[.1,.5,.9,.99]
 for i,v in enumerate(signal):
  acc+=v*v
  for t in targets:
   if t not in quantiles and acc>=t*energy:quantiles[t]=i/rate
 absolute=[]
 for b in range(64):
  a=round(b*.005*rate);z=round((b+1)*.005*rate);chunk=signal[a:z]
  absolute.append(math.sqrt(sum(v*v for v in chunk)/max(1,len(chunk))))
 normalized=[]
 for b in range(64):
  a=round(b*len(signal)/64);z=round((b+1)*len(signal)/64);chunk=signal[a:z]
  normalized.append(math.sqrt(sum(v*v for v in chunk)/max(1,len(chunk))))
 return {'absolute5ms_RMS64_to320ms':absolute,'time_normalized_RMS64':normalized,'energy_quantiles_seconds':{str(k):quantiles.get(k) for k in targets},'energy_time_centroid_seconds':sum(i/rate*v*v for i,v in enumerate(signal))/max(energy,1e-30),'peak_time_seconds':max(range(len(signal)),key=lambda i:abs(signal[i]))/rate}

def silence(signal,rate):
 threshold=10**(-70/20);block=round(.005*rate);runs=[];opened=None
 for a in range(0,len(signal),block):
  chunk=signal[a:a+block];quiet=math.sqrt(sum(x*x for x in chunk)/len(chunk))<=threshold
  if quiet and opened is None:opened=a
  if not quiet and opened is not None:runs.append([opened/rate,a/rate]);opened=None
 if opened is not None:runs.append([opened/rate,len(signal)/rate])
 internal=[b-a for a,b in runs if a>0 and b<len(signal)/rate]
 return {'threshold_dbfs':-70,'window_seconds':block/rate,'runs':runs,'max_internal_seconds':max(internal,default=0),'all_silent':all(abs(v)<=threshold for v in signal)}

def ffmpeg_measure(path,out,ffmpeg):
 dec=subprocess.run([ffmpeg,'-v','error','-i',str(path),'-map','0:a:0','-acodec','pcm_f32le','-f','f32le','pipe:1'],capture_output=True,timeout=30)
 if dec.returncode:raise ValueError('FFmpeg decode failed: '+dec.stderr.decode(errors='replace'))
 values=array.array('f');values.frombytes(dec.stdout)
 if sys.byteorder!='little':values.byteswap()
 run=subprocess.run([ffmpeg,'-hide_banner','-nostats','-i',str(path),'-af','ebur128=peak=true','-f','null','-'],capture_output=True,text=True,timeout=30)
 (out/(path.stem+'-ffmpeg.log')).write_text(run.stdout+run.stderr+'\nexit_code='+str(run.returncode)+'\n')
 if run.returncode:raise ValueError('FFmpeg ebur128 failed')
 peaks=re.findall(r'Peak:\s+(-?[\d.]+) dBFS',run.stderr);integrated=re.findall(r'I:\s+(-?[\d.]+) LUFS',run.stderr)
 return values,{'true_peak_dbfs':float(peaks[-1]) if peaks else None,'integrated_lufs_informational':float(integrated[-1]) if integrated else None,'LUFS_not_gated_short_SFX_acceptance':True,'log_sha256':sha(out/(path.stem+'-ffmpeg.log'))}

def analyze(path,out,ffmpeg):
 with wave.open(str(path),'rb') as w:
  h={'channels':w.getnchannels(),'rate':w.getframerate(),'sample_width':w.getsampwidth(),'frames':w.getnframes(),'compression':w.getcomptype()};raw=w.readframes(w.getnframes());extra=w.readframes(1)
 if h['sample_width']!=2 or h['channels']!=1 or h['compression']!='NONE':raise ValueError('Expected monoPCM16 source')
 pcm=array.array('h');pcm.frombytes(raw)
 if sys.byteorder!='little':pcm.byteswap()
 if not pcm or len(raw)!=h['frames']*2 or extra:raise ValueError('Incomplete/empty PCM')
 x=[v/32768.0 for v in pcm];decoded,levels=ffmpeg_measure(path,out,ffmpeg)
 decoder_exact=len(decoded)==len(x) and all(a==b for a,b in zip(x,decoded))
 peak=max(map(abs,x));rms=math.sqrt(sum(v*v for v in x)/len(x));dc=sum(x)/len(x)
 rail_pos=sum(v==32767 for v in pcm);rail_neg=sum(v==-32768 for v in pcm)
 endpoint=max(abs(v) for v in x[:2]+x[-2:]);tail=x[-round(.005*h['rate']):]
 quiet_tail_rms=math.sqrt(sum(v*v for v in tail)/len(tail));silent=silence(x,h['rate']);tp=true_peak_estimate(x);sp=spectrum(x,h['rate']);en=envelope(x,h['rate'])
 longest_plateau=0;run=0;previous=None
 for v in pcm:
  run=run+1 if v==previous and abs(v)>=max(1,round(.98*peak*32768)) else 1
  if abs(v)>=max(1,round(.98*peak*32768)):longest_plateau=max(longest_plateau,run)
  previous=v
 checks={'44100Hz':h['rate']==44100,'mono_pcm16':h['channels']==1 and h['sample_width']==2,'complete_finite_decoded_samples':decoder_exact and all(math.isfinite(v) for v in decoded),'single_shot_duration_25ms_to2s':.025<=len(x)/h['rate']<=2,'nonempty_energy_above_minus60dBFS':db(rms)>-60,'no_positive_or_negative_PCMrail':rail_pos==rail_neg==0,'no_float_fullscale_clipping':all(abs(v)<1 for v in decoded),'DC_under_existing025guard':abs(dc)<.025,'quiet_endpoints_under001':endpoint<.01,'final5ms_RMS_under_minus40dBFS':db(quiet_tail_rms)<-40,'no_internal_dropout_over150ms':silent['max_internal_seconds']<=.15,'not_entirely_silent':not silent['all_silent'],'own8x_truepeak_below_minus1dBTP':tp['dbtp_estimate']<-1,'ffmpeg_truepeak_below_fullscale':levels['true_peak_dbfs'] is not None and levels['true_peak_dbfs']<0,'no_flat_top_at_peak_8samples':longest_plateau<8}
 return {'path':str(path),'sha256':sha(path),'header':h,'duration_seconds':len(x)/h['rate'],'sample_peak':peak,'sample_peak_dbfs':db(peak),'RMS_dbfs':db(rms),'crest_factor_db':db(peak)-db(rms),'DC_signed':dc,'positive_PCMrails':rail_pos,'negative_PCMrails':rail_neg,'endpoint_first2_last2_peak':endpoint,'final5ms_RMS_dbfs':db(quiet_tail_rms),'max_equal_peak_plateau_samples':longest_plateau,'zero_crossing_rate':sum((a<0)!=(b<0) for a,b in zip(x,x[1:]))/max(1,len(x)-1),'silence':silent,'true_peak_estimate':tp,'ffmpeg':levels,'spectrum':sp,'envelope':en,'checks':checks,'passed':all(checks.values())}

def main():
 marker=Q/'job-start.json'
 if marker.exists():raise SystemExit('Already started/interrupted job: inspect receipt/evidence, never blindly replay')
 records=FROZEN['records'];assert all(sha(r['path'])==r['sha256'] for r in records),'Frozen input changed'
 write(marker,{'pid':os.getpid(),'started_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'entrypoint_sha256':sha(Path(__file__)),'scope':'SIGNAL_ONLY_NO_GODOT_NO_LISTENING','phase_approval':False})
 out=Q/'analysis-01';out.mkdir(exist_ok=False);ffmpeg=next(r['path'] for r in records if r.get('tool') and Path(r['path']).name=='ffmpeg')
 catalog=json.loads((Q/'inputs/catalog.json').read_text());manifest=json.loads((Q/'inputs/candidate_manifest.json').read_text());provenance=json.loads((Q/'inputs/candidate-provenance.json').read_text());legacy=json.loads((Q/'inputs/legacy-combat-polish.json').read_text());lp=json.loads((Q/'inputs/legacy-provenance.json').read_text());recipe=(Q/'inputs/render.py').read_text();tree=ast.parse(recipe)
 assignments={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['STYLES','WEAPONS']}
 styles=assignments['STYLES'];profiles={};expected={}
 for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha']:
  context='athletic_prime' if actor=='timka' else 'training';cats=catalog['actors'][actor]['equipment_by_context'][context]
  for cat in cats:
   cue='finish_'+actor+('_prime' if actor=='timka' else '')+'_'+cat;expected[cue]=(actor,context,cat)
  s=styles[actor];profiles[actor]={'declared_intent_NOT_listened':s['intent'],'duration':s['duration'],'thump_timing_decay_only':[[v[0],v[2]] for v in s['thumps']],'cloth_timing_decay_only':[[v[0],v[1]] for v in s['cloth']],'thump_frequencies':[v[1] for v in s['thumps']]}
 imports=[]
 for node in ast.walk(tree):
  if isinstance(node,ast.Import):imports.extend(a.name.split('.')[0] for a in node.names)
  if isinstance(node,ast.ImportFrom):imports.append(node.module.split('.')[0])
 allowed={'argparse','array','hashlib','json','math','random','sys','wave','pathlib'}
 wave_modes=[ast.literal_eval(n.args[1]) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and isinstance(n.func.value,ast.Name) and n.func.value.id=='wave' and n.func.attr=='open']
 readings=[ast.unparse(n) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ['read_text','read_bytes']]
 corechecks={'exact20_catalog_routes':len(expected)==20 and set(manifest['sfx'])==set(expected),'actor_counts_3_3_3_3_3_5':{a:sum(e[0]==a for e in expected.values()) for a in profiles}==dict(zip(profiles,[3,3,3,3,3,5])),'no_Timka_present_or_excluded_prime':all(e[1]=='athletic_prime' and e[2] in ['unarmed','blunt','environmental'] for e in expected.values() if e[0]=='timka'),'recipe_SHA_matches_provenance':sha(Q/'inputs/render.py')==provenance['recipe_sha256'],'catalog_SHA_matches_provenance':sha(Q/'inputs/catalog.json')==provenance['catalog_sha256'],'stdlib_imports_only':set(imports)<=allowed,'recipe_opens_audio_for_write_only':wave_modes==['wb'],'six_non_pitch_gain_only_timing_profiles':len({json.dumps([p['thump_timing_decay_only'],p['cloth_timing_decay_only']],sort_keys=True) for p in profiles.values()})==6}
 for cue,(actor,context,category) in expected.items():
  entry=manifest['sfx'][cue];assert entry['actor_id']==actor and entry['context']==context and entry['category']==category
  name=entry['path'];assert Path(name).name==name and name==cue+'.wav' and not (C/name).is_symlink()
  assert sha(C/name)==provenance['assets'][cue]['sha256'];assert entry['bus']=='SFX' and isinstance(entry['gain_db'],(int,float)) and math.isfinite(entry['gain_db'])
 for cat in ['unarmed','blunt','sharp','firearm','environmental']:
  cue='finish_'+cat;path=WORK/'game'/legacy['sfx'][cue]['path'].removeprefix('res://');assert sha(path)==lp['assets'][cue]['sha256']
 corechecks['legacy5_filebytes_and_routes_retained']=True
 assets={}
 for cue in sorted(expected):
  item=analyze(C/manifest['sfx'][cue]['path'],out,ffmpeg);item['actor_id'],item['context'],item['category']=expected[cue];assets[cue]=item
  write(out/(cue+'.json'),item);print(cue,'PASS_SIGNAL' if item['passed'] else 'FAIL_SIGNAL',flush=True)
 corechecks['20_distinct_PCM_assets']=len({a['sha256'] for a in assets.values()})==20
 legacy_hashes={r['sha256'] for r in records if r.get('legacy_yakuza')};corechecks['new20_not_relabelled_old5_bytes']=not any(a['sha256'] in legacy_hashes for a in assets.values())
 pairs=[]
 for (name,a),(other,b) in itertools.combinations(assets.items(),2):
  if a['category']!=b['category'] or a['actor_id']==b['actor_id']:continue
  rhythm=cosine(a['envelope']['time_normalized_RMS64'],b['envelope']['time_normalized_RMS64']);bands=cosine(a['spectrum']['normalized_log_band_power32'],b['spectrum']['normalized_log_band_power32'])
  pairs.append({'a':name,'b':other,'category':a['category'],'time_normalized_envelope_cosine':rhythm,'fixed5ms_envelope_cosine':cosine(a['envelope']['absolute5ms_RMS64_to320ms'],b['envelope']['absolute5ms_RMS64_to320ms']),'logband32_cosine':bands,'energy_centroid_difference_ms':1000*abs(a['envelope']['energy_time_centroid_seconds']-b['envelope']['energy_time_centroid_seconds']),'spectral_centroid_difference_hz':abs(a['spectrum']['centroid_hz']-b['spectrum']['centroid_hz']),'RMS_difference_db':abs(a['RMS_dbfs']-b['RMS_dbfs']),'similar_descriptor_review_flag_NOT_perceptual_verdict':rhythm>.985 and bands>.985})
 write(out/'profile-comparisons.json',{'scope':'MEASURED_RHYTHM_SPECTRAL_DESCRIPTORS_NOT_PERCEPTUAL_IDENTITY','recipe_profiles':profiles,'common_category_crosshero_pairs':pairs,'audible_individuality':'NOT_ASSESSED_NO_LISTENING','near_descriptor_flags_are_listening_priorities_not_quality_or_identity_verdicts':True})
 # Reproduce the inspected pure procedural recipe ONLY under this fresh QA folder.
 reproduction=Q/'recipe-reproduction-01';run=subprocess.run([sys.executable,str(Q/'inputs/render.py'),'--catalog',str(Q/'inputs/catalog.json'),'--output',str(reproduction)],cwd=Q,capture_output=True,text=True,timeout=60)
 (out/'recipe-reproduction.log').write_text(run.stdout+run.stderr+'\nexit_code='+str(run.returncode)+'\n');equal=run.returncode==0 and all(sha(reproduction/manifest['sfx'][cue]['path'])==assets[cue]['sha256'] for cue in assets)
 corechecks['all20_byteexact_from_copied_math_recipe']=equal
 write(out/'recipe-audit.json',{'imports':imports,'wave_open_modes':wave_modes,'read_operations_reviewed':readings,'recipe_sha256':sha(Q/'inputs/render.py'),'reproduced20_wave_bytes_exact':equal,'reproduction_only_in_QA_output':True,'no_external_recordings_or_voices_referenced_by_inspected_recipe':True,'not_universal_copyright_or_originality_certificate':True})
 with (out/'asset-summary.csv').open('w',newline='') as f:
  columns=['cue','actor','category','duration_seconds','RMS_dbfs','sample_peak_dbfs','truepeak8x_dBTP','truepeak_ffmpeg_dBFS','DC','endpoint_peak','spectral_centroid_hz','energy_centroid_ms','passed'];writer=csv.writer(f);writer.writerow(columns)
  for cue,a in assets.items():writer.writerow([cue,a['actor_id'],a['category'],a['duration_seconds'],a['RMS_dbfs'],a['sample_peak_dbfs'],a['true_peak_estimate']['dbtp_estimate'],a['ffmpeg']['true_peak_dbfs'],a['DC_signed'],a['endpoint_first2_last2_peak'],a['spectrum']['centroid_hz'],a['envelope']['energy_time_centroid_seconds']*1000,a['passed']])
 unchanged=all(sha(r['path'])==r['sha256'] for r in records)
 allpassed=all(corechecks.values()) and all(a['passed'] for a in assets.values()) and unchanged
 result={'schema':1,'scope':'C01_OFFLINE_SOURCE_SIGNAL_ONLY','status':'PASS_SIGNAL_ONLY' if allpassed else 'FAIL_SIGNAL_OR_CONTRACT','passed':allpassed,'checks':corechecks,'asset_count':len(assets),'asset_checks':{cue:a['checks'] for cue,a in assets.items()},'original_candidate_recipe_catalog_legacy_and_tool_inputs_unchanged':unchanged,'measured_profile_differences':'See actual38pair rhythm/band descriptors, not only SHA; no listening-based identity verdict','same_category_pairs':len(pairs),'artistic_acceptance':{'status':'ARTISTIC_NOT_LISTENED','actual_listening_performed':False,'audio_listening_tool_found':False,'music_or_sound_quality_not_approved':True},'runtime_status':'NOT_GODOT_INTEGRATED_NOT_TESTED','full_audio_acceptance':'BLOCKED_PENDING_ARTISTIC_LISTENING_AND_ACTUAL_ENGINE_MIXER_EVIDENCE','loop_join_and_music_transition':'N/A new20drysingle-shots; prior music gates not superseded','phase_approval':False,'full_phase_approval':False,'merge_approval':False,'new_borrowed_recording_claim_scope':'Inspected math-only recipe reproduced all20bytes; no external recordings referenced; no universal originality certificate','actual_no_Game_Godot_controller_Git_network_or_installation_calls':True}
 write(out/'result.json',result);write(Q/'job-result.json',{'scope':result['scope'],'status':result['status'],'exit_code':0 if allpassed else 1,'inputs_unchanged':unchanged,'result_sha256':sha(out/'result.json'),'no_listening_or_runtime_approval':True});print(result['status'],'assets',len(assets),'pairs',len(pairs),'ARTISTIC_NOT_LISTENED;NOT_GODOT_INTEGRATED',flush=True)
 return 0 if allpassed else 1
if __name__=='__main__':raise SystemExit(main())
