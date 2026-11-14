#!/usr/bin/env python3
"""P04 decoded assets, silence/loudness/loops/transitions and actual runtime PCM QA.

Reuses P03's signal primitives. Metrics never approve musical quality or listening.
"""
from array import array
import argparse
import json
import math
from pathlib import Path
import sys
from audio_qa import (POLICY,basic_checks,decode,event_windows,loudness,metrics,mix,sha)

ROOT=Path(__file__).resolve().parents[1]

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',default='reports/phases/P04/attempt1/audio_signal_detailed.json')
 parser.add_argument('--runtime-name',action='append',choices=['engine_replay','reduced_visual_replay','movie_replay','linux_export_replay','windows_export_replay'])
 parser.add_argument('--runtime-dir',help='Fresh completed verify_p04.py output, analyzed without modifying it')
 args=parser.parse_args();target=(ROOT/args.output).resolve()
 if not target.is_relative_to(ROOT) or target.is_relative_to(ROOT/'assets/references'):parser.error('Unsafe output')
 if target.exists():parser.error('Use a fresh --output; prior evidence is immutable')
 result={'scope':'Decoded numerical analysis only; actual runtime PCM is separately identified. No listening or musical-quality verdict.',
  'policy':POLICY,'listening':'PENDING_ACTUAL_LISTENER','checks':[],'files':[],'mixes':{},'transitions':[],'runtimes':[]}
 def check(name,checks,details=None):result['checks'].append({'name':name,'passed':all(checks.values()),'checks':checks,'details':details})
 music=json.loads((ROOT/'game/resources/chapters/missed_fight_music.json').read_text())['music'];stems={}
 files=[(ROOT/'game'/s['path'].removeprefix('res://'),'stem',s['id']) for s in music['stems']]
 files += [(ROOT/'game/assets/audio/sfx/missed_fight_door.ogg','cue',None)]
 files += [(p,'source',None) for p in sorted((ROOT/'assets/source_audio/missed_fight').rglob('*.wav'))]
 for path,kind,name in files:
  signal,rate=decode(path);stats=metrics(signal,rate);levels=loudness(path);checks=basic_checks(stats)
  checks['native_stereo_48k']=rate==music['sample_rate']
  checks['true_peak_below_full_scale']=levels['true_peak_dbfs'] is not None and levels['true_peak_dbfs']<0
  looping=kind=='stem' or path.parent.name=='masters'
  if looping:
   checks.update(exact_loop_frames=stats['frames']==music['loop_frames'],bounded_loop_join=stats['boundary_step']<POLICY['loop_join_limit'])
   low,high=POLICY['music_loudness_guard_lufs'];checks['broad_loudness_guard']=levels['integrated_lufs'] is not None and low<levels['integrated_lufs']<high
  else:checks['bounded_cue_duration']=.025<=stats['duration_seconds']<=2
  if kind=='stem':stems[name]=signal
  check(str(path.relative_to(ROOT)),checks)
  result['files'].append({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'kind':kind,'signal':stats,'loudness':levels})
 for state,gains in dict(music['profiles'],UNITY={n:1 for n in stems}).items():
  stats=metrics(mix(stems,gains),music['sample_rate']);checks=basic_checks(stats)
  checks.update(headroom=stats['sample_peak']<POLICY['mix_peak_limit'],bounded_loop_join=stats['boundary_step']<POLICY['loop_join_limit'],no_internal_dropout=stats['max_internal_silence_seconds']<=POLICY['mix_internal_silence_limit_seconds'])
  check('profile_'+state,checks);result['mixes'][state]=stats
 sr=music['sample_rate'];count=music['loop_frames']
 for before,a in music['profiles'].items():
  for after,b in music['profiles'].items():
   if before==after:continue
   probes=[]
   for beat in [0,7,16]:
    offset=int(beat*60/music['bpm']*sr);last=[sum(stems[n][((offset-1)%count)*2+c]*a[n] for n in stems) for c in range(2)]
    peak=0.;step=0.;energy=0.
    for frame in range(int(sr*.55)):
     elapsed=frame/sr;gains={n:a[n]+max(-elapsed*1.9,min(elapsed*1.9,b[n]-a[n])) for n in stems}
     values=[sum(stems[n][((offset+frame)%count)*2+c]*gains[n] for n in stems) for c in range(2)]
     peak=max(peak,*map(abs,values));step=max(step,*(abs(values[c]-last[c]) for c in range(2)));energy+=sum(v*v for v in values);last=values
    probes.append({'beat_offset':beat,'peak':peak,'max_step':step,'rms':math.sqrt(energy/(int(sr*.55)*2))})
   check('transition_'+before+'_'+after,{'headroom':all(p['peak']<.98 for p in probes),'bounded_step':all(p['max_step']<.5 for p in probes),'nonempty':all(p['rms']>.001 for p in probes)})
   result['transitions'].append({'from':before,'to':after,'signal_probes':probes,'scope':'Offline continuous-gain probes, not actual listening or runtime proof'})
 if args.runtime_dir:
  folder=(ROOT/args.runtime_dir).resolve()
  if not folder.is_relative_to(ROOT) or folder.is_relative_to(ROOT/'assets/references'):parser.error('Unsafe runtime path')
  for name in (args.runtime_name or ['engine_replay','reduced_visual_replay','movie_replay','linux_export_replay','windows_export_replay']):
   report=folder/(name+'.json');pcm=folder/(name+'.wav')
   if not report.exists() or not pcm.exists():
    check(name,{'actual_report_and_pcm_present':False});continue
   data=json.loads(report.read_text());signal,rate=decode(pcm);stats=metrics(signal,rate);checks=basic_checks(stats)
   checks.update(real_replay=data.get('passed') is True,nonempty_duration=stats['duration_seconds']>40,no_internal_dropout=stats['max_internal_silence_seconds']<=.2)
   audio=data['audio'];origin=audio['clock']-stats['duration_seconds']
   # Approximate clock-to-PCM alignment; mixer buffer/scheduling latency is not an acoustic measurement.
   events=[{'sample_time_seconds':e['clock']-origin,'state':e['state']} for e in audio['events'] if e['kind']=='commit' and e['clock']>=origin]
   windows=event_windows(signal,rate,events)
   loops=[];boundary=math.ceil(max(0,origin)/music['loop_seconds'])*music['loop_seconds']
   while boundary<audio['clock']:
    if boundary>origin:loops.append({'sample_time_seconds':boundary-origin})
    boundary+=music['loop_seconds']
   loop_windows=event_windows(signal,rate,loops)
   checks['runtime_transition_windows']=bool(windows) and all(w['in_capture'] and w['max_step']<.5 for w in windows)
   checks['runtime_loop_windows']=bool(loop_windows) and all(w['in_capture'] and w['max_step']<.5 for w in loop_windows)
   check(name,checks)
   result['runtimes'].append({'name':name,'report_sha256':sha(report),'pcm_sha256':sha(pcm),'audio_driver':audio['audio_driver'],'signal':stats,'loudness':loudness(pcm),'clock_to_pcm_origin_estimate':origin,'alignment_limit':'Approximate mix clock/record duration; not sample-accurate acoustic latency','transition_windows':windows,'loop_windows':loop_windows})
 result['passed']=all(r['passed'] for r in result['checks']);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'signal_passed':result['passed'],'checks':len(result['checks']),'files':len(result['files']),'mixes':len(result['mixes']),'directed_transitions':len(result['transitions']),'runtimes':len(result['runtimes']),'listening':result['listening']}))
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
