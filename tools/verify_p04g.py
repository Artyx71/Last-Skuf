#!/usr/bin/env python3
"""Sequential P04G replay/evidence. Never decides phase/reviewer/listening gates.
Default: actual renderer, Full/Reduced, five finishers x four directions, AI reactions,
pinned stress, real PCM; --movie writes actual MovieMaker AVI and short category clips.
--headless is bounded technical evidence and explicitly cannot satisfy native QA.
"""
from array import array
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import time
import wave
ROOT=Path(__file__).resolve().parents[1]
LOCK=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
GODOT=ROOT/'.tools/godot'/f'Godot_v{LOCK["release"]}_linux.x86_64'
ERRORS=re.compile(r'SCRIPT ERROR:|ERROR:|FAIL:|ObjectDB instances were leaked|resources still in use')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def winpath(p):return 'Z:'+str(p.resolve()).replace('/','\\')
def sources():
 return {str(p.relative_to(ROOT)):sha(p) for directory in ['game','assets/source_art/combat_polish','assets/source_audio/combat_polish'] for p in sorted((ROOT/directory).rglob('*')) if p.is_file() and '.godot' not in p.parts}
def waveform(path):
 try:
  with wave.open(str(path),'rb') as w:
   result={'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'rate':w.getframerate(),'frames':w.getnframes()}
   signal=array('h',w.readframes(w.getnframes()))
  if sys.byteorder!='little':signal.byteswap()
  result.update(duration=result['frames']/result['rate'],peak=max(map(abs,signal),default=0)/32768,rms=math.sqrt(sum(x*x for x in signal)/max(1,len(signal)))/32768,full_scale_samples=sum(abs(x)>=32767 for x in signal),sha256=sha(path))
  return result
 except (OSError,wave.Error,ValueError) as e:return {'error':str(e)}
def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--exports',action='store_true');parser.add_argument('--movie',action='store_true');parser.add_argument('--headless',action='store_true')
 parser.add_argument('--output',required=True);parser.add_argument('--build-output',required=True)
 args=parser.parse_args()
 if args.headless and args.movie:parser.error('--movie requires actual rendering')
 output=(ROOT/args.output).resolve();build=(ROOT/args.build_output).resolve()
 if output.exists() and any(output.iterdir()):parser.error('Immutable evidence: use a NEW empty output directory')
 output.mkdir(parents=True,exist_ok=True);build.mkdir(parents=True,exist_ok=True)
 logs=output/'logs';logs.mkdir()
 local=ROOT/'.tools/p04g-qa'/hashlib.sha256(str(output).encode()).hexdigest()[:16];local.mkdir(parents=True,exist_ok=True)
 for folder in ['config','data']:(local/folder).mkdir(exist_ok=True)
 before=sources();write(output/'source_hashes.json',before)
 results=[]
 def save():write(output/'validation.json',results)
 def check(name,checks,details=None):
  ok=all(checks.values());results.append({'name':name,'passed':ok,'checks':checks,'details':details});save()
  print(name,'PASS' if ok else 'FAIL_OR_BLOCKED',flush=True);return ok
 def env(name,wine=False,reduced=False):
  folder=local/name;folder.mkdir(exist_ok=True)
  convert=winpath if wine else str
  e=dict(os.environ,XDG_CONFIG_HOME=str(local/'config'),XDG_DATA_HOME=str(local/'data'))
  for key,file in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),('AYAY_CHAPTER_SAVE_PATH','chapter.json')]:e[key]=convert(folder/file)
  write(folder/'options.json',{'schema':2,'values':{'reduced_gore':reduced,'decals':not reduced,'shake':0 if reduced else 100,'flashes':not reduced,'reduced_motion':reduced,'vhs':not reduced}})
  if wine:e.update(WINEPREFIX=str(local/'wine-prefix'),WINEARCH='win64',WINEDEBUG='-all',WINEDLLOVERRIDES='winemenubuilder.exe=d;mscoree,mshtml=')
  return e
 def run(name,command,e,timeout=300):
  started=time.monotonic();command=list(map(str,command))
  try:
   p=subprocess.run(command,cwd=ROOT,env=e,capture_output=True,text=True,timeout=timeout)
   text,code=p.stdout+p.stderr,p.returncode
  except subprocess.TimeoutExpired as exc:
   def decode(v):return v.decode(errors='replace') if isinstance(v,bytes) else (v or '')
   text=decode(exc.stdout)+decode(exc.stderr)+'\nTIMEOUT '+str(exc);code=124
  log=logs/(name+'.log')
  selected={k:v for k,v in e.items() if k.startswith('AYAY_') or k in ['XDG_CONFIG_HOME','XDG_DATA_HOME','WINEPREFIX','WINEDEBUG','WINEDLLOVERRIDES']}
  log.write_text('environment='+json.dumps(selected,sort_keys=True)+'\n$ '+shlex.join(command)+'\n'+text+f'\nexit_code={code}\n')
  ok=code==0 and not ERRORS.search(text)
  results.append({'name':name,'passed':bool(ok),'exit_code':code,'log':str(log.relative_to(ROOT)),'elapsed_seconds':time.monotonic()-started});save()
  print(name,'PASS' if ok else 'FAIL_OR_BLOCKED',flush=True);return ok
 def finish():
  check('sources_unchanged',{'exact_hashes':before==sources()})
  write(output/'environment.json',{'os':platform.platform(),'machine':platform.machine(),'cpu':platform.processor(),'scope':'HEADLESS_TECHNICAL_ONLY' if args.headless else 'ACTUAL_RENDERER_REQUESTED','native_windows':'NOT_TESTED; Wine is a separate runtime','listening':'PENDING_ACTUAL_LISTENING; numerical analysis is not artistic acceptance','review':'PENDING_INDEPENDENT_ART_GAMEPLAY_QA_LEAD','author_phase_pass':False,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_hashes_authoritative_for_this_capture':True,'source_dirty':bool(subprocess.check_output(['git','status','--porcelain','--','game','tools','assets'],cwd=ROOT).strip())})
  write(output/'artifacts.json',[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(output.rglob('*')) if p.is_file() and p.name!='artifacts.json'])
  return 0 if all(r['passed'] for r in results) else 1
 check('pinned_engine',{'sha256':sha(GODOT)==LOCK['linux_binary_sha256']})
 # One actual native probe. If display/audio sockets are denied, persist exact failure
 # and STOP native stages. Caller can run the separate --headless technical scope.
 if not args.headless:
  if not run('native_probe',[GODOT,'--path',ROOT/'game','--','--smoke-bootstrap'],env('native_probe'),20):
   write(output/'blocker.json',{'scope':'native renderer/audio; exports/movie/Wine deferred to authorized host','next_command':f'python3 tools/verify_p04g.py --exports --movie --output reports/phases/P04G/attempt1/native-host-01 --build-output build/P04G/native-host-01','headless_command':'python3 tools/verify_p04g.py --headless --output reports/phases/P04G/attempt1/technical-host-01 --build-output build/P04G/technical-host-01','phase_gate':'NOT_DECIDED'})
   return finish()
 def replay(name,command,wine=False,reduced=False,movie=False):
  e=env(name,wine,reduced);convert=winpath if wine else str
  captures=output/(name+'_frames');captures.mkdir()
  result=output/(name+'.json');pcm=output/(name+'.wav')
  for key,path in [('AYAY_P04G_CAPTURE_DIR',captures),('AYAY_P04G_RESULT_PATH',result),('AYAY_P04G_AUDIO_PATH',pcm)]:e[key]=convert(path)
  ok=run(name,command+['--','--open-combat','--p04g-replay'],e,480)
  data=json.loads(result.read_text()) if result.is_file() else {}
  finishes=data.get('finishers',[]);perf=data.get('performance',{})
  checks={'engine_passed':data.get('passed') is True,'twenty_category_direction_cases':len(finishes)==20,'all_earned_stun':data.get('earned_stun_input') is True,'each_two_hits_one_kill_score':bool(finishes) and all(f['hits']==2 and f['kills']==1 and f['score']==100 for f in finishes),'twelve_ai_direction_cases':len(data.get('ai',[]))==12,'stress_600_measured_samples':perf.get('samples',0)>=590,'single_music_player':data.get('audio',{}).get('music_players')==1,'no_audio_leak':data.get('audio',{}).get('active_voices',100)<=12,'movie_diagnostic_exact':perf.get('movie_maker') is movie}
  if not args.headless:
   checks.update(actual_frames=len(list(captures.glob('*.png')))>=195,render_backend=perf.get('rendered') is True,actual_audio_driver=data.get('audio',{}).get('audio_driver')=='Dummy' if movie else data.get('audio',{}).get('audio_driver') not in [None,'Dummy'])
  check(name+'_acceptance',checks)
  signal=waveform(pcm);signal['scope']='actual runtime PCM; numerical only, not listening'+('; accelerated Dummy headless not native audio proof' if args.headless else '')
  write(output/(name+'_signal.json'),signal)
  if not args.headless:check(name+'_signal',{'stereo_pcm16':signal.get('channels')==2 and signal.get('sample_width')==2,'nonempty':signal.get('duration',0)>10 and signal.get('rms',0)>.001,'no_full_scale_clipping':signal.get('full_scale_samples')==0},signal)
  return data
 command=[GODOT,'--path',ROOT/'game']
 if args.headless:command+=['--headless','--fixed-fps','60','--disable-vsync','--max-fps','0']
 full=replay('full_replay',command)
 reduced=replay('reduced_replay',command,reduced=True)
 signature=lambda d:[(f['category'],f['direction'],f['hits'],f['kills'],f['score']) for f in d.get('finishers',[])]
 check('full_reduced_gameplay_invariance',{'nonempty':bool(signature(full)),'same_outcomes':signature(full)==signature(reduced)})
 if args.movie:
  movie=build/'combat_polish.avi'
  data=replay('movie_replay',[GODOT,'--path',ROOT/'game','--write-movie',movie,'--fixed-fps','60'],movie=True)
  ffmpeg=shutil.which('ffmpeg')
  if not ffmpeg:
   candidate=ROOT/'.tools/ci-media/bin/ffmpeg';ffmpeg=str(candidate) if candidate.is_file() else None
  if not check('movie_tools',{'actual_avi':movie.is_file() and movie.stat().st_size>1000,'ffmpeg':bool(ffmpeg)}):return finish()
  run('encode_movie',[ffmpeg,'-v','error','-y','-i',movie,'-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-c:a','aac',output/'combat_polish.mp4'],env('encode_movie'),180)
  for category in ['unarmed','blunt','sharp','firearm','environmental']:
   starts=[c for c in data.get('captures',[]) if c['name']==category+'_right_windup']
   ends=[c for c in data.get('captures',[]) if c['name']==category+'_right_recovery']
   if starts and ends:
    start=max(0,starts[0]['draw_frame']/60-.2);duration=(ends[0]['draw_frame']-starts[0]['draw_frame'])/60+.7
    run('clip_'+category,[ffmpeg,'-v','error','-y','-ss',str(start),'-i',movie,'-t',str(duration),'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',output/(category+'.mp4')],env('clip_'+category))
   else:check('clip_'+category,{'contact_capture_metadata':False})
 if args.exports:
  exports=[]
  for preset,folder,filename,magic in [('Linux','linux','last-skuf.x86_64',b'\x7fELF'),('Windows','windows','last-skuf.exe',b'MZ')]:
   target=build/folder/filename;target.parent.mkdir(exist_ok=True)
   exported=run('export_'+folder,[GODOT,'--headless','--path',ROOT/'game','--export-release',preset,target],env('export_'+folder),180)
   present=target.is_file() and target.read_bytes().startswith(magic)
   check('export_'+folder+'_artifact',{'executable_magic':present})
   row={'platform':preset,'path':str(target.relative_to(ROOT)),'export_clean':exported,'native_windows':'NOT_TESTED' if folder=='windows' else None}
   if present:
    row.update(sha256=sha(target),bytes=target.stat().st_size)
    if folder=='linux':
     target.chmod(0o755);replay('linux_export_replay',[target]+(['--headless','--fixed-fps','60'] if args.headless else []))
    else:
     wine=[ROOT/'.tools/wine/usr/bin/wine',target]
     if args.headless:wine+=['--headless']
     probe=run('wine_probe',wine+['--','--smoke-bootstrap'],env('wine_probe',True),30);row['wine_actual_probe']=probe
     if probe:replay('wine_export_replay',wine,wine=True)
   exports.append(row);write(output/'exports.json',exports)
 if not args.headless:
  regression=[sys.executable,ROOT/'tools/verify_p04.py','--output',output/'p04_regression','--build-output',build/'p04_regression']
  if args.exports:regression+=['--exports']
  if args.movie:regression+=['--movie']
  run('native_p04_regression',regression,env('p04_regression'),1200)
  if args.movie:
   metadata=output/'p04_regression/movie_replay.json'
   data=json.loads(metadata.read_text()) if metadata.is_file() else {}
   check('p04_actual_movie_flag',{'actual_movie_metadata':data.get('frame_timings',{}).get('movie_maker') is True,'actual_mp4':(output/'p04_regression/mission.mp4').is_file()})
 if not args.headless:
  run('detailed_audio',[sys.executable,ROOT/'tools/analyze_p04g_audio.py','--runtime-dir',output,'--output',output/'audio_detailed.json'],env('audio_detailed'),300)
 return finish()
if __name__=='__main__':raise SystemExit(main())
