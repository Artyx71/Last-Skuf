#!/usr/bin/env python3
"""Decode P04 audio and measure actual samples. Never a listening verdict."""
from array import array
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',default='reports/phases/P04/attempt1/audio_signal.json')
 args=parser.parse_args();target=ROOT/args.output
 if target.exists():parser.error('Use a fresh --output; prior evidence is immutable')
 music=json.loads((ROOT/'game/resources/chapters/missed_fight_music.json').read_text())['music']
 files=[ROOT/'game'/s['path'].removeprefix('res://') for s in music['stems']]+[ROOT/'game/assets/audio/sfx/missed_fight_door.ogg']
 decoded={};rows=[]
 for p in files:
  data=subprocess.run(['ffmpeg','-v','error','-i',p,'-f','f32le','-ac','2','-ar','48000','pipe:1'],capture_output=True,check=True).stdout
  samples=array('f');samples.frombytes(data)
  if sys.byteorder!='little':samples.byteswap()
  frames=len(samples)//2;peak=max(map(abs,samples));rms=math.sqrt(sum(x*x for x in samples)/len(samples))
  seam=max(abs(samples[c]-samples[-2+c]) for c in range(2))
  row={'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'decoded_frames':frames,'sample_rate':48000,'channels':2,'peak':peak,'rms':rms,'full_scale_samples':sum(abs(x)>=1 for x in samples),'seam_step':seam,'seam_is_loop':p.parent.name=='music'}
  checks={'nonempty_pcm':frames>20000 and rms>.001,'no_clipping':peak<.98,'finite_samples':all(math.isfinite(x) for x in samples)}
  if p.parent.name=='music':
   checks['exact_loop_frames']=frames==music['loop_frames'];checks['bounded_loop_seam']=seam<.08
   decoded[p.stem.removeprefix('missed_fight_')]=samples
  row['checks']=checks;row['passed']=all(checks.values());rows.append(row)
 mixes=[]
 for state,gains in dict(music['profiles'],UNITY={n:1 for n in decoded}).items():
  mix=[sum(decoded[name][i]*gain for name,gain in gains.items()) for i in range(len(next(iter(decoded.values()))))]
  peak=max(map(abs,mix));rms=math.sqrt(sum(x*x for x in mix)/len(mix));mixes.append({'state':state,'peak':peak,'rms':rms,'passed':peak<.98 and rms>.001})
 result={'scope':'Numerical decoded signal QA only. No actual listening, headphones/speakers or musical-quality acceptance. Runtime capture is a separate artifact.','listening':'PENDING_ACTUAL_LISTENER','decoder':subprocess.run(['ffmpeg','-version'],capture_output=True,text=True).stdout.splitlines()[0],'files':rows,'mixes':mixes,'passed':all(r['passed'] for r in rows+mixes)}
 target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'signal_passed':result['passed'],'files':len(rows),'mixes':len(mixes),'listening':result['listening']}))
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
