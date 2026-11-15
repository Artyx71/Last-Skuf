#!/usr/bin/env python3
"""Original deterministic dry finisher sound candidates; no samples or voices.

Renders source WAV only. Does not install assets, approve sound or modify Godot.
"""
import argparse,array,hashlib,json,math,random,sys,wave
from pathlib import Path
RATE=44100
STYLES={
 'gabar':{'duration':.22,'intent':'tight power contact and short knuckle follow-through','thumps':[(0,95,.037,1),(.027,155,.012,.24)],'cloth':[(.009,.022,.16)],'ring':.05},
 'olezhka':{'duration':.24,'intent':'controlled joint/contact accent and clean cloth release','thumps':[(0,138,.027,.85),(.014,210,.014,.12)],'cloth':[(.002,.012,.26),(.055,.034,.13)],'ring':.035},
 'timka':{'duration':.31,'intent':'prime-only heavy grapple contact with cloth strain; present has none','thumps':[(0,62,.065,1.1),(.024,103,.029,.2)],'cloth':[(0,.038,.26),(.062,.052,.2)],'ring':.025},
 'ryzhik':{'duration':.27,'intent':'compact acrobatic contact and sweeping fabric release','thumps':[(0,154,.026,.8)],'cloth':[(.001,.017,.16),(.021,.062,.3),(.081,.023,.13)],'ring':.06},
 'tega':{'duration':.29,'intent':'dull improvised contact and loose material rattle','thumps':[(0,78,.048,1),(.043,122,.021,.15)],'cloth':[(.004,.031,.14),(.083,.039,.15)],'ring':.16},
 'pasha':{'duration':.21,'intent':'fast dry contact with uneven cloth and mechanism ticks','thumps':[(0,126,.024,.8),(.018,238,.008,.13)],'cloth':[(.002,.008,.22),(.029,.013,.18),(.067,.016,.11)],'ring':.07},
}
WEAPONS={
 'unarmed':{'body':1,'crack':.14,'edge':0,'resonances':[]},
 'blunt':{'body':1.12,'crack':.22,'edge':.02,'resonances':[(381,.045,.13),(927,.024,.06)]},
 'sharp':{'body':.55,'crack':.10,'edge':.42,'resonances':[(1830,.011,.035)]},
 'firearm':{'body':.78,'crack':.95,'edge':.05,'resonances':[(112,.039,.26),(2110,.013,.08)]},
 'environmental':{'body':1.15,'crack':.27,'edge':.05,'resonances':[(187,.063,.20),(463,.039,.13),(1147,.018,.05)]},
}
def packet(t,delay,decay):
 u=t-delay
 return 0.0 if u<0 else (1-math.exp(-u/.0007))*math.exp(-u/decay)
def render(actor,category):
 s=STYLES[actor];weapon=WEAPONS[category];duration=s['duration'];n=round(duration*RATE)
 rng=random.Random(int.from_bytes(hashlib.sha256((actor+'/'+category).encode()).digest()[:8],'little'))
 values=[];low=0.0;older=0.0;dc=0.0
 for i in range(n):
  t=i/RATE;white=rng.uniform(-1,1);low=.82*low+.18*white;high=white-low
  v=0.0
  for delay,freq,decay,gain in s['thumps']:
   u=max(0,t-delay);phase=2*math.pi*(freq*u+freq*.33*(1-math.exp(-u*45))/45)
   v+=weapon['body']*gain*packet(t,delay,decay)*math.sin(phase)
  for delay,decay,gain in s['cloth']:
   v+=gain*packet(t,delay,decay)*(high*.58+low*.42)
  v+=weapon['crack']*packet(t,0,.0075)*(white*.8+low*.2)
  v+=weapon['edge']*packet(t,.001,.036)*high*(.7+.3*math.sin(2*math.pi*43*t))
  for freq,decay,gain in weapon['resonances']:
   v+=(gain+s['ring']*.22)*packet(t,0,decay)*math.sin(2*math.pi*freq*t)
  # Gentle DC blocker and explicit short release; no clipped hard limiting.
  filtered=v-older+.995*dc;older=v;dc=filtered
  fade=min(1,t/.0015)*min(1,(duration-t)/.012)
  values.append(filtered*max(0,fade))
 peak=max(abs(v) for v in values);assert peak>0
 signal=[round(v/peak*.55*32767) for v in values];signal[0]=signal[-1]=0
 pcm=array.array('h',signal)
 if sys.byteorder!='little':pcm.byteswap()
 return pcm,{'duration_seconds':n/RATE,'peak_dbfs':20*math.log10(max(map(abs,signal))/32768),'rms_dbfs':20*math.log10(math.sqrt(sum(v*v for v in signal)/n)/32768),'dc':sum(signal)/n/32768,'pcm_full_scale_samples':sum(abs(v)>=32767 for v in signal),'endpoint_samples':[signal[0],signal[-1]]}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--catalog',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 assert not a.output.exists(),'Use a fresh candidate output; preserve previous renders'
 catalog=json.loads(a.catalog.read_text());actors=catalog['actors'];a.output.mkdir(parents=True);entries={};proofs={};matrix=[]
 for actor,style in STYLES.items():
  context='athletic_prime' if actor=='timka' else 'training'
  categories=actors[actor]['equipment_by_context'][context]
  for category in categories:
   assert category in WEAPONS
   cue='finish_'+actor+('_prime' if actor=='timka' else '')+'_'+category
   samples,stats=render(actor,category);path=a.output/(cue+'.wav')
   with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(samples.tobytes())
   entries[cue]={'path':path.name,'bus':'SFX','gain_db':-2.5,'actor_id':actor,'context':context,'category':category,'intent':style['intent']};proofs[cue]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'signal_quick_measurements':stats};matrix.append([actor,context,category,cue])
 assert len(entries)==20 and len({v['sha256'] for v in proofs.values()})==20
 manifest={'schema':1,'status':'ACTUAL_SOURCE_CANDIDATES_NOT_YET_GODOT_INTEGRATED','sample_rate':RATE,'channels':1,'sample_width':2,'sfx':entries,'actor_context_category_matrix':matrix,'yakuza_baseline':'Original five finish_* cues already present; not rerendered or relabelled by this recipe','timka_present':'No finisher cue or prime grant','artistic_acceptance':'NOT_LISTENED_NOT_ACCEPTED','technical_signal_review':'Full independent decode/truepeak/loudness/runtime QA pending; quick PCM measurements are not listening'}
 (a.output/'candidate_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(a.output/'provenance.json').write_text(json.dumps({'schema':1,'method':'Original deterministic procedural sound design; distinct hero transient/cloth topology plus category physical resonators; no recordings/samples/voice synthesis/external API','recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'catalog_sha256':hashlib.sha256(a.catalog.read_bytes()).hexdigest(),'styles':STYLES,'weapon_layers':WEAPONS,'assets':proofs,'listening':'NOT_PERFORMED','phase_approval':False},ensure_ascii=False,indent=2)+'\n');print('ACTUAL_WAV_CANDIDATES',len(entries),'PCM16mono44100; no artistic/runtime approval')
if __name__=='__main__':main()
