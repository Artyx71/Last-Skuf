from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';ev=W/'reports/phases/P06/tega-environment-01/native-01';movie=W/'build/P06/tega-environment-01/tega-environment.mp4'
d=json.loads((ev/'movie/result.json').read_text());selected={};groups={}
def add(t,label):
 n=t['tick']-1
 selected[n]={'trace':t,'label':label}
 return n
for mode in ['false','true']:
 ns=[]
 for direction in ['down','left','right','up']:
  seg='object_hit_'+mode+'_'+direction
  for phase in range(3):
   rows=[t for t in d['trace'] if t['segment']==seg and t['action_kind']=='special' and t['action_frame']==phase]
   if phase==1:
    c=next(c for c in d['contacts'] if c['segment']==seg);t=next(t for t in rows if t['tick']==c['tick'])
   else:t=rows[len(rows)//2]
   ns.append(add(t,seg+':'+str(phase)))
 groups['object_'+mode]=ns
for direction in ['down','left','right','up']:
 ns=[]
 for mode in ['false','true']:
  for category in ['unarmed','blunt','environmental']:
   seg='finisher_'+mode+'_'+category+'_'+direction;c=next(c for c in d['contacts'] if c['segment']==seg and c['finisher']);t=next(t for t in d['trace'] if t['tick']==c['tick']);ns.append(add(t,seg))
 groups['FIN_'+direction]=ns
for direction in ['down','left','right','up']:
 ns=[]
 for b in d['clothing_overlay']:
  if b['direction']==direction:
   t=next(t for t in d['trace'] if t['tick']==b['tick']);ns.append(add(t,'blood_'+direction+':'+str(b['pose'])))
 groups['blood_'+direction]=ns
ns=[]
for c in d['contacts']:
 if c['segment'].startswith('incoming_'):
  t=next(t for t in d['trace'] if t['tick']==c['tick']);ns.append(add(t,c['segment']))
groups['incoming']=ns
indices=sorted(selected);tmp=O/'decode-temporary';tmp.mkdir(exist_ok=True);dest=O/'movie-frames';dest.mkdir(exist_ok=True)
expr='+'.join('eq(n\\,%d)'%n for n in indices);argv=['ffmpeg','-v','error','-threads','1','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(tmp/'frame_%03d.png')]
p=subprocess.run(argv,capture_output=True,text=True);assert p.returncode==0,p.stderr
files=sorted(tmp.glob('frame_*.png'));assert len(files)==len(indices);inventory=[]
for n,p in zip(indices,files):
 f=dest/('frame_%04d.png'%n);p.replace(f);inventory.append({'frame':n,'trace_tick':n+1,'path':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'label':selected[n]['label']})
tmp.rmdir()
for group,ns in groups.items():
 cols=min(len(ns),6);rows=(len(ns)+cols-1)//cols;board=Image.new('RGB',(cols*240,rows*220),(20,25,29));draw=ImageDraw.Draw(board)
 for i,n in enumerate(ns):
  t=selected[n]['trace'];x,y=[int(v*2) for v in t['position']];im=Image.open(dest/('frame_%04d.png'%n));crop=im.crop((x-130,y-145,x+130,y+55)).resize((240,185),Image.Resampling.NEAREST)
  cx=(i%cols)*240;cy=(i//cols)*220;board.paste(crop,(cx,cy+30));draw.text((cx+3,cy+3),'n%d '%n+selected[n]['label'],fill='white')
 board.save(O/(group+'_movie_diagnostic.png'))
probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(movie)],capture_output=True,text=True,check=True)
proof={'movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'ffprobe':json.loads(probe.stdout),'decode_argv':argv,'selected_actual_wholeframes':len(indices),'frames':inventory,'groups':groups,'alignment':'n=tick-1; trace labels are evidence context, actual displayed pixels independently viewed','diagnostics':'Existing movie decoded only; crops/NN resize explicitly reviewer diagnostics; production/evidence unchanged.'}
(O/'movie-proofs.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'movie_sha256':proof['movie_sha256'],'frames':len(indices),'probe':proof['ffprobe']}))
