from pathlib import Path
import json,subprocess,hashlib
root=Path('AYAY_SDD_v1.0');w=root/'.autopilot/worktrees/P06';out=root/'reports/phases/P06/lead-timka-prime-01';r=w/'reports/phases/P06/timka-prime-01';d=json.loads((r/'movie-03/movie/result.json').read_text());trace=d['trace'];selected=[]
for context in ['present','prime']:
 rows=[x for x in trace if x['segment']==context+'_locomotion_right' and x['animation']=='walk_right'];groups=[]
 for x in rows:
  if not groups or x['tick']!=groups[-1][-1]['tick']+1:groups.append([])
  groups[-1].append(x)
 rows=max(groups,key=len);seen=set();wrap=0;prev=0
 for x in rows:
  if x['frame']<prev:wrap+=1
  key=(wrap,x['frame']);prev=x['frame']
  if key not in seen and wrap<2:selected.append((x['tick']-1,context+'_walk_cycle'+str(wrap)+'_f'+str(x['frame'])));seen.add(key)
for segment in ['clinch_down','clinch_up','V_finisher_environmental_up','settings_false','settings_true']:
 e=next(x for x in d['contacts'] if x['segment']==segment and x['finisher']);selected.append((e['tick']-1,segment+'_contact'))
 if segment=='clinch_down':
  selected.append((e['tick']-2,'clinch_down_precontact'));rec=next(x for x in trace if x['segment']==segment and x['action_kind']=='finish_unarmed' and x['action_frame']==2);selected.append((rec['tick']-1,'clinch_down_recovery'))
for e in d['contacts']:
 if e['target_is_player']:selected.append((e['tick']-1,e['segment']+'_incoming'))
selected=sorted(dict(selected).items());movie=Path(json.loads((r/'movie-03/validation.json').read_text())['movie_path']);probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,duration,nb_read_frames,avg_frame_rate','-of','json',str(movie)],capture_output=True,text=True,check=True);pd=json.loads(probe.stdout);actual=int(pd['streams'][0]['nb_read_frames']);assert all(n<actual for n,_ in selected)
frames=out/'diagnostics/movie03-keyframes';frames.mkdir(parents=True);expr='+'.join('eq(n\\,%d)'%n for n,_ in selected);cmd=['ffmpeg','-v','error','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(frames/'frame_%02d.png')];p=subprocess.run(cmd,capture_output=True,text=True,check=True);paths=sorted(frames.glob('*.png'));assert len(paths)==len(selected)
(out/'own-movie03-decode.json').write_text(json.dumps({'schema':1,'movie_ROOT_relative':str(movie.relative_to(root.resolve())),'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'probe':pd,'ffmpeg_argv':cmd,'exit_code':p.returncode,'selected_original_frames':[{'file':str(p.relative_to(out)),'zero_based_n':n,'PTS_seconds':n/60,'reason':reason,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p,(n,reason) in zip(paths,selected)],'timing_rule':'n=physics tick-1 validated byART on sameGDScript; selected actualimages inspected, not hardwarelatency','whole_film_visual_review_claimed':False,'preserve_original_no_pad_or_trim':True,'diagnostic_correction':'Earlier ownprobe incorrectly assumed oldMovie02 3600count; actual03 count is3599, both originalmedia unchanged.'},indent=2)+'\n');print(json.dumps({'selected_frames':len(paths),'actual_count':actual,'selection':selected},indent=2))
