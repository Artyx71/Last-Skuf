#!/usr/bin/env python3
"""Bounded Gabar production-controller evidence; never accepts the full P06 phase."""
import argparse,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
from verify_p06_cast import ROOT,GODOT,ERRORS,sha,write,sources

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--output',required=True);parser.add_argument('--headless',action='store_true');parser.add_argument('--movie',action='store_true');parser.add_argument('--build-output');args=parser.parse_args()
 if args.movie and (args.headless or not args.build_output):parser.error('Movie requires native renderer and a new --build-output')
 output=(ROOT/args.output).resolve()
 if output.exists() and any(output.iterdir()):parser.error('Use a fresh evidence directory; inspect prior receipt before retry')
 output.mkdir(parents=True,exist_ok=True)
 build=(ROOT/args.build_output).resolve() if args.build_output else None
 if build:
  if build.exists() and any(build.iterdir()):parser.error('Use a fresh movie output directory')
  build.mkdir(parents=True,exist_ok=True)
 local=ROOT/'.tools/p06-gabar-qa'/hashlib.sha256(str(output).encode()).hexdigest()[:16];local.mkdir(parents=True,exist_ok=True)
 env=os.environ.copy();env.update(AYAY_STORY_SAVE_PATH=str(local/'story.json'),AYAY_DIALOGUE_SAVE_PATH=str(local/'dialogue.json'),AYAY_OPTIONS_PATH=str(local/'options.json'),XDG_CONFIG_HOME=str(local/'config'),XDG_DATA_HOME=str(local/'data'))
 before=sources();write(output/'source_hashes.json',before);commands=[]
 def run(name,cmd,scope_env=None,timeout=180):
  start=time.monotonic()
  try:
   result=subprocess.run(list(map(str,cmd)),cwd=ROOT,env=scope_env or env,capture_output=True,text=True,timeout=timeout);code=result.returncode;text=result.stdout+result.stderr
  except subprocess.TimeoutExpired as error:code=124;text='TIMEOUT\n'+str(error.stdout)+str(error.stderr)
  (output/(name+'.log')).write_text(text+'\nexit_code='+str(code)+'\n')
  item={'name':name,'argv':list(map(str,cmd)),'exit_code':code,'seconds':round(time.monotonic()-start,3),'passed':code==0 and not ERRORS.search(text)};commands.append(item);write(output/'commands.json',commands);print(name,'OK' if item['passed'] else 'FAIL',flush=True);return item['passed']
 def replay(name,movie=False):
  scope=output/name;scope.mkdir();scope_env=env|{'AYAY_P06_GABAR_OUTPUT':str(scope)}
  cmd=[GODOT,'--path',ROOT/'game','--disable-vsync','--max-fps','60']
  if args.headless:cmd+=['--headless','--fixed-fps','60']
  if movie:cmd+=['--write-movie',build/'gabar.avi','--fixed-fps','60']
  cmd+=['--script','res://tests/gabar_combat_replay.gd']
  ok=run(name,cmd,scope_env)
  result=json.loads((scope/'result.json').read_text()) if (scope/'result.json').is_file() else {}
  return bool(ok and result.get('passed') and result.get('actual_input') and ((result.get('renderer')=='headless')==args.headless)),result
 ok,live=replay('live')
 movie_result={};probe={}
 if ok and args.movie:
  ok,movie_result=replay('movie',True)
  ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
  ok=bool(ok and ffmpeg and ffprobe and (build/'gabar.avi').is_file())
  if ok:
   ok=run('encode_movie',[ffmpeg,'-v','error','-n','-i',build/'gabar.avi','-c:a','aac','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',build/'gabar.mp4'])
  if ok:
   cmd=[ffprobe,'-v','error','-show_streams','-show_format','-of','json',build/'gabar.mp4']
   ok=run('probe_movie',cmd)
   if ok:
    probe=json.loads((output/'probe_movie.log').read_text().rsplit('\nexit_code=',1)[0]);write(output/'movie_probe.json',probe)
    ok=any(stream.get('codec_type')=='video' and int(stream.get('nb_frames',0))>=1000 for stream in probe.get('streams',[]))
 unchanged=before==sources();ok=bool(ok and unchanged)
 result={'phase':'P06','scope':'GABAR_PRODUCTION_CONTROLLER_INTEGRATION_ONLY','phase_approval':False,'actor_id':'gabar','passed':ok,'source_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'source_unchanged':unchanged,'renderer':live.get('renderer'),'checks_passed':sum(x['passed'] for x in live.get('checks',[])),'checks_total':len(live.get('checks',[])),'actual_captures':len(list((output/'live').glob('*.png'))),'contacts':len(live.get('contacts',[])),'actual_input':live.get('actual_input',False),'movie_recorded':bool(probe),'engine_recording':str(output/'live/engine_mix.wav') if not args.headless else None,'movie_path':str(build/'gabar.mp4') if probe else None,'movie_audio':'Actual reused accepted cues; no new media and no subjective listening claim','native_windows':'NOT_TESTED','exports':'NOT_REQUESTED_FOR_THIS_CONTROLLER_SUBTASK','combat_abilities':'Gabar only; five other hero bodies/abilities pending','commands':commands}
 result['artifacts']=[{'path':str(p.relative_to(ROOT)),'sha256':sha(p)} for p in sorted(output.rglob('*')) if p.is_file()]
 write(output/'validation.json',result);print(json.dumps({k:result[k] for k in ['passed','scope','checks_passed','checks_total','actual_captures','source_unchanged','movie_recorded']}));return 0 if ok else 1
if __name__=='__main__':sys.exit(main())
