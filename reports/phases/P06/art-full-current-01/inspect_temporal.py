from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01';D=O/'temporal';D.mkdir(exist_ok=True);records=[]
base=W/'reports/phases/P06/full-native-current-source-01';stages={k:base/k for k in ['gabar','olezhka','timka_present','timka_prime','ryzhik','tega']};stages['pasha']=W/'reports/phases/P06/pasha-input-diagnostic-01/native'
for stage,path in stages.items():
 val=json.loads((path/'validation.json').read_text());result=json.loads((path/'movie/result.json').read_text());trace=result['trace'];chosen=[]
 def add(label,rows):
  if rows:chosen.append({'label':label,'trace':rows[len(rows)//2]})
 for di in ['down','left','right','up']:
  segment={'gabar':'special_','olezhka':'counter_','timka_present':'disengage_','timka_prime':'clinch_','ryzhik':'walk_roll_walk_','tega':'object_hit_false_','pasha':'moving_shot_false_'}[stage]+di
  signature_kind={'gabar':'special','olezhka':'special','timka_present':'disengage','timka_prime':'finish_unarmed','ryzhik':'roll','tega':'special','pasha':'moving_shot'}[stage]
  seq=[x for x in trace if x['segment']==segment and x.get('action_kind')==signature_kind]
  for frame in range(8 if stage in ['ryzhik','pasha'] else 6 if stage=='timka_present' else 3):
   add(di+':'+str(frame),[x for x in seq if x.get('action_kind') and x.get('frame')==frame])
  if stage in ['gabar','olezhka','timka_prime','tega']:
   prefix='V_finisher_' if stage=='timka_prime' else 'finisher_false_' if stage=='tega' else 'finisher_'
   cats={'gabar':['unarmed','blunt','firearm'],'olezhka':['unarmed','blunt','sharp'],'timka_prime':['unarmed','blunt','environmental'],'tega':['unarmed','blunt','environmental']}[stage]
   for cat in cats:add(di+':FIN_'+cat,[x for x in trace if x['segment']==prefix+cat+'_'+di and x.get('action_kind','').startswith('finish_') and x.get('frame')==1])
 if not chosen:raise RuntimeError(stage+' no selected frames')
 movie=Path(val['movie_path']);out=D/stage;out.mkdir(exist_ok=True);ticks=sorted(set(x['trace']['tick'] for x in chosen));expr='+'.join('eq(n'+chr(92)+','+str(t)+')' for t in ticks)
 # Only actual recorded film; no engine run or synthetic pose render.
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(movie),'-vf','select='+expr,'-fps_mode','passthrough',str(out/'frame-%04d.png')]
 images=sorted(out.glob('frame-*.png'))
 if len(images)!=len(ticks):
  subprocess.run(cmd,check=True);images=sorted(out.glob('frame-*.png'))
 assert len(images)==len(ticks),(stage,len(images),len(ticks))
 for image_path in images:
  with Image.open(image_path) as check_image:check_image.verify()
 tickmap=dict(zip(ticks,images));tiles=[]
 for c in chosen:
  t=c['trace'];im=Image.open(tickmap[t['tick']]).convert('RGB');logical=im.resize((640,360),Image.Resampling.NEAREST);x,y=t['position'];rect=(round(x)-56,round(y)-80,round(x)+56,round(y)+16);tile=logical.crop(rect).resize((224,192),Image.Resampling.NEAREST);tiles.append((c,tile))
 cols=8 if stage in ['ryzhik','pasha'] else 6;rows=math.ceil(len(tiles)/cols);board=Image.new('RGB',(cols*224,rows*228+32),(21,25,32));draw=ImageDraw.Draw(board);draw.text((4,6),'ACTUAL MOVIE '+stage+'; trace ticks, crop follows actor. Floor/target remain real pixels.',fill='white')
 for i,(c,tile) in enumerate(tiles):
  xx=(i%cols)*224;yy=32+(i//cols)*228;board.paste(tile,(xx,yy));t=c['trace'];draw.text((xx+3,yy+194),c['label']+' tick'+str(t['tick']),fill='white');draw.text((xx+3,yy+208),'xy '+','.join(str(round(v,1)) for v in t['position']),fill='white')
 board.save(D/(stage+'-actual-movie.png'));records.append({'stage':stage,'validation':str((path/'validation.json').relative_to(W)),'result':str((path/'movie/result.json').relative_to(W)),'movie_path':str(movie.relative_to(W)),'movie_SHA':hashlib.sha256(movie.read_bytes()).hexdigest(),'actual_selected_frame_count':len(ticks),'decoding_command':cmd,'trace_tick_to_video_n':'Engine fixed60 recording; selected n=trace tick. Stable middle-of-pose samples, not frame callback timing acceptance. Actual decoded pixels personally viewed before verdict.','samples':[{'label':c['label'],'tick':c['trace']['tick'],'animation':c['trace']['animation'],'pose':c['trace']['frame'],'xy':c['trace']['position'],'decoded_file':str(tickmap[c['trace']['tick']].relative_to(O))} for c in chosen]})
(O/'temporal-inspection.json').write_text(json.dumps({'actual_movies':records,'actual_decoded_frames':sum(x['actual_selected_frame_count'] for x in records),'not_claimed':'Not every movie frame manually viewed; timing/once/lifecycle are Gameplay/QA checks, not inferred from montage alone.'},ensure_ascii=False,indent=2)+'\n');print({'movies':len(records),'decoded_frames':sum(x['actual_selected_frame_count'] for x in records)})
