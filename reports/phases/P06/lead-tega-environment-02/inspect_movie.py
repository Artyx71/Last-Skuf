from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';movie=W/'build/P06/tega-environment-02/tega-environment.mp4'
d=json.loads((W/'reports/phases/P06/tega-environment-01/native-02/movie/result.json').read_text());selected={};groups={}
def add(t,label):
 n=t['tick']-1;selected[n]={'trace':t,'label':label};return n
for dr in ['down','left','right','up']:
 ns=[]
 for phase in range(3):
  rows=[t for t in d['trace'] if t['segment']=='object_hit_false_'+dr and t['action_kind']=='special' and t['action_frame']==phase];ns.append(add(rows[len(rows)//2],dr+':special'+str(phase)))
 groups['object_'+dr]=ns
ns=[]
for dr in ['down','left','right','up']:
 c=next(c for c in d['contacts'] if c['segment']=='finisher_false_unarmed_'+dr and c['finisher']);ns.append(add(next(t for t in d['trace'] if t['tick']==c['tick']),'finisher_'+dr))
groups['FIN']=ns;ns=[]
for b in d['clothing_overlay']:
 if b['pose']==1:ns.append(add(next(t for t in d['trace'] if t['tick']==b['tick']),'blood_'+b['direction']))
groups['blood']=ns
dest=O/'movie-frames';dest.mkdir(exist_ok=True);temp=O/'decode-tmp';temp.mkdir(exist_ok=True);indices=sorted(selected);expr='+'.join('eq(n\\,%d)'%n for n in indices)
argv=['ffmpeg','-v','error','-threads','1','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(temp/'frame_%03d.png')];p=subprocess.run(argv,capture_output=True,text=True);assert p.returncode==0,p.stderr
frames=sorted(temp.glob('frame_*.png'));assert len(frames)==len(indices);items=[]
for n,p in zip(indices,frames):
 f=dest/('frame_%04d.png'%n);p.replace(f);items.append({'frame':n,'path':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'label':selected[n]['label']})
temp.rmdir()
for key,ns in groups.items():
 board=Image.new('RGB',(240*len(ns),220),(20,24,28));draw=ImageDraw.Draw(board)
 for i,n in enumerate(ns):
  x,y=[int(v*2) for v in selected[n]['trace']['position']];im=Image.open(dest/('frame_%04d.png'%n));crop=im.crop((x-130,y-145,x+130,y+55)).resize((240,185),Image.Resampling.NEAREST);board.paste(crop,(i*240,30));draw.text((i*240+2,3),'n%d '%n+selected[n]['label'],fill='white')
 board.save(O/(key+'_movie_diagnostic.png'))
probe=json.loads(subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(movie)],capture_output=True,text=True,check=True).stdout)
(O/'movie-proofs.json').write_text(json.dumps({'source':'c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd','movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'ffprobe':probe,'actual_selected_wholeframes':len(items),'frames':items,'decode_argv':argv,'diagnostics_only_crops_NN':True,'original_movie_unchanged':True},indent=2)+'\n');print(probe)
