from pathlib import Path
from array import array
import json,wave,math
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';stats=json.loads((O/'solo-source-correlation-proofs.json').read_text())['events'];manifest=json.loads((W/'game/assets/audio/character_finishers.json').read_text())['sfx'];ys={}
for ver in ['native-01','native-02']:
 p=W/'reports/phases/P06/character-finisher-audio-01'/ver/'replay/solo_cues.wav'
 with wave.open(str(p)) as f:a=array('h',f.readframes(f.getnframes()));assert f.getnchannels()==2
 ys[ver]=[(a[i]+a[i+1])/2 for i in range(0,len(a),2)]
rows=[]
for cue,e in manifest.items():
 with wave.open(str(W/'game'/e['path'].removeprefix('res://'))) as f:x=array('h',f.readframes(f.getnframes()))
 n=len(x);xm=math.fsum(x)/n;xc=[v-xm for v in x];xx=math.fsum(v*v for v in xc);clips={};gains={}
 for ver in ys:
  d=next(r for r in stats if r['native']==ver and r['cue']==cue);i=round(d['capture_start_seconds']*44100);y=ys[ver][i:i+n];ym=math.fsum(y)/n;yc=[v-ym for v in y];clips[ver]=yc;gains[ver]=math.fsum(a*b for a,b in zip(xc,yc))/xx
 a,b=clips.values();ncc=math.fsum(x*y for x,y in zip(a,b))/math.sqrt(math.fsum(v*v for v in a)*math.fsum(v*v for v in b));delta=20*math.log10(gains['native-02']/gains['native-01']);assert ncc>.98 and abs(delta)<.25,(cue,ncc,delta)
 rows.append({'cue':cue,'actual_old_new_solo_NCC':ncc,'new_minus_old_source_projection_gain_dB':delta})
(O/'quiet-pair-proofs.json').write_text(json.dumps({'scope':'CONTENT_SIGNAL_CONTINUITY_WITH_OWNER_HEARD_OLD_SOLO_NOT_NEW_LISTENING','pairs':rows,'all20_gain_delta_abs_lt_0_25dB':True,'new_stress_hearing':False},indent=2)+'\n')
print('20quietpairsPASS minNCC',min(r['actual_old_new_solo_NCC'] for r in rows),'maxabsdB',max(abs(r['new_minus_old_source_projection_gain_dB']) for r in rows))
