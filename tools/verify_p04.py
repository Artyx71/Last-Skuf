#!/usr/bin/env python3
"""P04 engine evidence. Use a FRESH output directory; never decides a phase gate.

Default requires a real renderer/mixer and saves actual frames. --headless records
real controller/AI/save behavior only; captures/listening remain explicitly BLOCKED.
Use --exports for fresh Linux/Windows artifacts and actual platform runtime probes.
"""
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import struct
import subprocess
import sys
import time
import wave

ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
GODOT=ROOT/'.tools/godot'/f'Godot_v{LOCK["release"]}_linux.x86_64'
ERRORS=re.compile(r'SCRIPT ERROR:|ERROR:|FAIL:|\bFAILED\b')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def game_sources():
 return {str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'game').rglob('*')) if p.is_file() and '.godot' not in p.parts}
def winpath(p): return 'Z:'+str(p.resolve()).replace('/','\\')

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',default='reports/phases/P04/attempt1/technical')
 parser.add_argument('--headless',action='store_true')
 parser.add_argument('--exports',action='store_true')
 parser.add_argument('--movie',action='store_true')
 parser.add_argument('--build-output',default='build/P04')
 args=parser.parse_args()
 if args.headless and args.movie: parser.error('--movie requires the real renderer')
 output=(ROOT/args.output).resolve(); output.mkdir(parents=True,exist_ok=True)
 if (output/'validation.json').exists(): parser.error('Evidence already exists; use a fresh --output')
 build=(ROOT/args.build_output).resolve();build.mkdir(parents=True,exist_ok=True)
 logs=output/'logs';logs.mkdir(exist_ok=True)
 local=ROOT/'.tools/p04-qa'/hashlib.sha256(str(output).encode()).hexdigest()[:12]
 local.mkdir(parents=True,exist_ok=True)
 config=local/'config';data=local/'data';config.mkdir();data.mkdir()
 before=game_sources();write(output/'source_hashes.json',before)
 results=[]
 def save(): write(output/'validation.json',results)
 def run(name,command,env,timeout=180):
  start=time.monotonic()
  try:
   p=subprocess.run(list(map(str,command)),cwd=ROOT,env=env,capture_output=True,text=True,timeout=timeout)
   text,code=p.stdout+p.stderr,p.returncode
  except subprocess.TimeoutExpired as error:
   text=str(error);code=124
  log=logs/(name+'.log')
  selected={k:v for k,v in env.items() if k.startswith('AYAY_') or k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','WINEPREFIX','WINEDEBUG','WINEDLLOVERRIDES']}
  log.write_text('environment='+json.dumps(selected,sort_keys=True)+'\n$ '+shlex.join(list(map(str,command)))+'\n'+text+f'\nexit_code={code}\n')
  ok=code==0 and not ERRORS.search(text)
  results.append({'name':name,'passed':ok,'exit_code':code,'log':str(log.relative_to(ROOT)),'elapsed_seconds':round(time.monotonic()-start,3)})
  save();print(name,'PASS' if ok else 'FAIL_OR_BLOCKED',flush=True)
  return ok
 def check(name,checks,details=None):
  results.append({'name':name,'passed':all(checks.values()),'checks':checks,'details':details});save()
  print(name,'PASS' if all(checks.values()) else 'FAIL_OR_BLOCKED',flush=True)
 def environment(name,wine=False,preferences=None):
  folder=local/name;folder.mkdir()
  convert=winpath if wine else str
  env=dict(os.environ,XDG_CONFIG_HOME=str(config),XDG_DATA_HOME=str(data))
  for key,filename in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json')]:env[key]=convert(folder/filename)
  if preferences:write(folder/'options.json',{'schema':1,'values':preferences})
  if wine:
   # Never mutate the shared cache prefix or owner settings.
   env.update(WINEPREFIX=str(local/'wine-prefix'),WINEARCH='win64',WINEDEBUG='-all',WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
  return env
 def waveform(path):
  try:
   with wave.open(str(path),'rb') as w:
    row={'sample_rate':w.getframerate(),'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'frames':w.getnframes()}
    samples=array('h',w.readframes(w.getnframes()))
   if sys.byteorder!='little':samples.byteswap()
   row.update(duration=row['frames']/row['sample_rate'],peak=max(map(abs,samples))/32768,rms=math.sqrt(sum(v*v for v in samples)/len(samples))/32768,full_scale_samples=sum(abs(v)>=32767 for v in samples))
   return row
  except (OSError,wave.Error,ValueError) as e:return {'error':str(e)}
 def replay(name,command,wine=False,preferences=None,movie=False):
  env=environment(name,wine,preferences)
  captures=output/(name+'_frames');captures.mkdir()
  paths={'AYAY_P04_RESULT_PATH':output/(name+'.json'),'AYAY_P04_AUDIO_PATH':output/(name+'.wav'),'AYAY_P04_CAPTURE_DIR':captures}
  for key,p in paths.items():env[key]=winpath(p) if wine else str(p)
  ok=run(name,command+['--','--open-mission','--p04-replay'],env,240)
  report=json.loads(paths['AYAY_P04_RESULT_PATH'].read_text()) if paths['AYAY_P04_RESULT_PATH'].is_file() else {}
  deaths=report.get('deaths',[]);audio=report.get('audio',{})
  checks={'engine_passed':report.get('passed') is True,'actual_input_no_route_warps':report.get('actual_input') is True and report.get('route_warps')==0,'ten_ai_deaths':len(deaths)==10 and all(d['actual_ai_death'] for d in deaths),'retry_under_1s':bool(deaths) and max(d['latency_ms'] for d in deaths)<1000,'zero_kills':report.get('final_snapshot',{}).get('kills')==0,'durable_once_completion':report.get('progress',{}).get('completion_events')==1,'correct_original_score':audio.get('music_id')=='MISSED_FIGHT_BACK_DOOR','one_mixer_player':audio.get('music_players')==1 and audio.get('stem_starts')==2}
  if not args.headless:
   checks['actual_rendered_captures']=len(report.get('captures',[]))>=9 and all(Path(r['path']).is_file() for r in report['captures']) if not wine else len(list(captures.glob('*.png')))>=9
   checks['expected_audio_driver']=audio.get('audio_driver')=='Dummy' if movie else audio.get('audio_driver') not in [None,'Dummy']
  check(name+'_acceptance',checks,{'capture_status':report.get('capture_status'),'scope':report.get('scope')})
  signal=waveform(paths['AYAY_P04_AUDIO_PATH'])
  signal['scope']='Numeric signal analysis only; '+('Dummy mixer, no realtime audio device or rendering' if args.headless else 'actual runtime mixer capture; no listening claim')
  write(output/(name+'_waveform.json'),signal)
  check(name+'_signal',{'pcm16_stereo':signal.get('channels')==2 and signal.get('sample_width')==2,'nonempty':signal.get('duration',0)>40 and signal.get('rms',0)>.001,'no_full_scale_clipping':signal.get('full_scale_samples')==0},signal)
  return ok
 check('pinned_engine',{'sha256':sha(GODOT)==LOCK['linux_binary_sha256']})
 native=[GODOT]+(['--headless'] if args.headless else [])+['--path',ROOT/'game']
 replay('engine_replay',native)
 replay('reduced_visual_replay',native,preferences={'reduced_gore':True,'vhs':False,'reduced_motion':True,'text_scale':1.25})
 if args.movie:
  movie=build/'missed_fight.avi'
  replay('movie_replay',[GODOT,'--path',ROOT/'game','--write-movie',movie,'--fixed-fps','60'],movie=True)
  run('encode_movie',['ffmpeg','-v','error','-y','-i',movie,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-c:a','aac',output/'mission.mp4'],environment('encode_movie'))
 if args.exports:
  exports=[]
  for preset,folder,filename,magic in [('Linux','linux','last-skuf.x86_64',b'\x7fELF'),('Windows','windows','last-skuf.exe',b'MZ')]:
   target=build/folder/filename;target.parent.mkdir(exist_ok=True)
   exported=run('export_'+folder,[GODOT,'--headless','--path',ROOT/'game','--export-release',preset,target],environment('export_'+folder))
   present=target.is_file() and target.read_bytes().startswith(magic)
   check('export_'+folder+'_artifact',{'executable_magic':present})
   row={'platform':preset,'path':str(target.relative_to(ROOT)),'export_log_clean':exported,'artifact_present':present,'native_windows':'NOT_TESTED_UNAVAILABLE' if folder=='windows' else None}
   if present:
    row.update(sha256=sha(target),bytes=target.stat().st_size)
    if folder=='linux':
     target.chmod(0o755)
     replay('linux_export_replay',[target]+(['--headless'] if args.headless else []))
    else:
     command=[ROOT/'.tools/wine/usr/bin/wine',target]+(['--headless'] if args.headless else [])
     # Probe before long replay: Wine's server requires sockets unavailable in restricted executors.
     probe=run('windows_wine_probe',command+['--quit'],environment('windows_probe',True),30)
     row['wine_probe_passed']=probe
     if probe:replay('windows_export_replay',command,wine=True)
   exports.append(row);write(output/'exports.json',exports)
 check('sources_unchanged',{'hashes_match':before==game_sources()})
 write(output/'environment.json',{'platform':platform.platform(),'scope':'Headless technical execution only' if args.headless else 'Native renderer requested','listening':'PENDING_ACTUAL_HUMAN_LISTENING','independent_lead':'PENDING_CONTROLLER_READ_ONLY_REVIEW','git_base':subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,capture_output=True,text=True).stdout.strip(),'uncommitted_sources':True,'phase_gate':'NOT_DECIDED_BY_AUTHOR'})
 write(output/'artifacts.json',[{'path':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(output.rglob('*')) if p.is_file() and p.name!='artifacts.json'])
 return 0 if all(r['passed'] for r in results) else 1

if __name__=='__main__':raise SystemExit(main())
