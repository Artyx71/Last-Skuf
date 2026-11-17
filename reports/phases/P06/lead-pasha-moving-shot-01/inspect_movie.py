from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib,shutil
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';ev=W/'reports/phases/P06/pasha-moving-shot-01/native-03';movie=W/'build/P06/pasha-moving-shot-03/pasha-moving-shot.mp4'
d=json.loads((ev/'movie/result.json').read_text());selected={};groups={}
def add(t,label):
 n=t['tick']-1;selected[n]={'trace':t,'label':label};return n
for dr in ['down','left','right','up']:
 ns=[]
 for phase in range(8):
  rows=[t for t in d['trace'] if t['segment']=='moving_shot_false_'+dr and t['action_kind']=='moving_shot' and t['action_frame']==phase];ns.append(add(rows[len(rows)//2],dr+':shot'+str(phase)))
 groups['moving_'+dr]=ns
ns=[]
for dr in ['down','left','right','up']:
 l=next(l for l in d['launches'] if l['segment']=='moving_shot_true_'+dr);ns.append(add(next(t for t in d['trace'] if t['tick']==l['tick']),'Reduced_launch_'+dr))
groups['Reduced_launches']=ns;ns=[]
for b in d['clothing_overlay']:
 if b['pose']==3:ns.append(add(next(t for t in d['trace'] if t['tick']==b['tick']),'blood_'+b['direction']))
groups['blood_muzzle3']=ns
for mode in ['false','true']:
 ns=[]
 for cat in ['unarmed','blunt','sharp','firearm','environmental']:
  c=next(c for c in d['contacts'] if c['segment']=='finisher_'+mode+'_'+cat+'_up' and c['finisher']);ns.append(add(next(t for t in d['trace'] if t['tick']==c['tick']),mode+':FIN_'+cat))
 groups['FIN_UP_'+mode]=ns
c=next(c for c in d['contacts'] if c['segment']=='shared_clip_shot_then_firearm_finisher' and c['finisher'])
groups['shared_clip_FIN']=[add(next(t for t in d['trace'] if t['tick']==n),'mixed_FIN') for n in [c['tick'],c['tick']+1]]
dest=O/'movie-frames';dest.mkdir(exist_ok=True);temp=O/'decode-tmp';temp.mkdir(exist_ok=True);indices=sorted(selected);expr='+'.join('eq(n\\,%d)'%n for n in indices)
argv=['ffmpeg','-v','error','-threads','1','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(temp/'frame_%03d.png')];p=subprocess.run(argv,capture_output=True,text=True);assert p.returncode==0,p.stderr
files=sorted(temp.glob('frame_*.png'));assert len(files)==len(indices);inventory=[]
for n,p in zip(indices,files):
 f=dest/('frame_%04d.png'%n);p.replace(f);inventory.append({'frame':n,'path':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'label':selected[n]['label']})
temp.rmdir()
for key,ns in groups.items():
 cols=min(len(ns),8);rows=(len(ns)+cols-1)//cols;board=Image.new('RGB',(240*cols,220*rows),(20,24,28));draw=ImageDraw.Draw(board)
 for i,n in enumerate(ns):
  x,y=[int(v*2) for v in selected[n]['trace']['position']];im=Image.open(dest/('frame_%04d.png'%n));crop=im.crop((x-130,y-145,x+130,y+55)).resize((240,185),Image.Resampling.NEAREST);cx=(i%cols)*240;cy=(i//cols)*220;board.paste(crop,(cx,cy+30));draw.text((cx+2,cy+3),'n%d '%n+selected[n]['label'],fill='white')
 board.save(O/(key+'_movie_diagnostic.png'))
probe=json.loads(subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(movie)],capture_output=True,text=True,check=True).stdout)
hud_names=['pasha_after_restart.png','moving_shot_false_up_launch.png','moving_shot_false_up_recovered.png','empty_clip_HUD.png','refill_HUD.png','paused_HUD.png','shared_clip_firearm_finisher.png','incoming_before_launch_true.png'];hud=[];target=O/'native-HUD';target.mkdir(exist_ok=True)
for name in hud_names:
 p=ev/'live'/name;shutil.copyfile(p,target/name);hud.append({'name':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(O/'movie-proofs.json').write_text(json.dumps({'source':'b359747361c6ac76ccfc0cc8ff262c8327cf33e4','movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'ffprobe':probe,'actual_selected_wholeframes':len(inventory),'frames':inventory,'decode_argv':argv,'diagnostics_only_crops_NN':True,'original_movie_unchanged':True,'native_wholeviewport_HUD_images':hud},indent=2)+'\n');print({'frames':len(inventory),'probe':probe,'HUDnative':len(hud)})
