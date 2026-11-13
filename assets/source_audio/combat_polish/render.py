#!/usr/bin/env python3
"""Original dry impact DSP. No samples, voice cloning, external API or music edits."""
from pathlib import Path
import wave,math,random,array,hashlib,json
ROOT=Path(__file__).resolve().parents[3];SRC=Path(__file__).parent
OUT=ROOT/'game/assets/audio/combat_polish';OUT.mkdir(exist_ok=True)
CATEGORIES=['unarmed','blunt','sharp','firearm','environmental']
FREQ=[115,74,340,52,92]
entries={};metrics={}
for ci,category in enumerate(CATEGORIES):
 for si,surface in enumerate(['body','concrete','metal','finish']):
  id='finish_'+category if si==3 else 'impact_'+category+'_'+surface
  rate=44100;duration=[.17,.21,.28,.34][si];n=int(duration*rate)
  rng=random.Random(407+ci*31+si);samples=array.array('h');previous=0
  for i in range(n):
   t=i/rate;noise=rng.uniform(-1,1);previous=previous*.72+noise*.28
   envelope=min(1,t/.002)*(1-t/duration)**3
   body=math.sin(2*math.pi*(FREQ[ci]*t+24*(1-math.exp(-18*t))/18))*math.exp(-22*t)
   ring=math.sin(2*math.pi*(630+ci*103)*t)*math.exp(-11*t) if si==2 else 0
   scrape=(noise-previous)*math.exp(-12*t) if ci==2 else previous
   snap=noise*math.exp(-120*t) if ci==3 else noise*.08
   value=(body*.48+scrape*.38+ring*.28+snap*.32)*envelope*.64
   samples.append(round(max(-.95,min(.95,value))*32767))
  path=SRC/(id+'.wav')
  with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(samples.tobytes())
  (OUT/path.name).write_bytes(path.read_bytes())
  entries[id]={'path':'res://assets/audio/combat_polish/'+path.name,'bus':'SFX','gain_db':-2.5}
  metrics[id]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'duration':duration,'peak':max(map(abs,samples))/32768,'rms':math.sqrt(sum(v*v for v in samples)/n)/32768,'full_scale_samples':sum(abs(v)>=32767 for v in samples)}
manifest=ROOT/'game/assets/audio/combat_polish.json';manifest.write_text(json.dumps({'schema':1,'sfx':entries},indent=2)+'\n')
(SRC/'provenance.json').write_text(json.dumps({'method':'original deterministic Python DSP; seeded noise plus damped sinusoids; no external recordings','license':'Original project-owned sound design; artistic listening PENDING','recipe_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'assets':metrics,'listening':'NOT_PERFORMED; numeric metrics are not listening'},indent=2)+'\n')
