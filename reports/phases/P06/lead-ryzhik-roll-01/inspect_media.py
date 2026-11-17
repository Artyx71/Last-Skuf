"""Decode actual existing movie and build explicitly labelled reviewer crops."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, subprocess, hashlib
OUT=Path(__file__).parent;ROOT=OUT.parents[3];WORK=ROOT/'.autopilot/worktrees/P06'
movie=WORK/'build/P06/ryzhik-roll-03/ryzhik-roll.mp4';ev=WORK/'reports/phases/P06/ryzhik-roll-01/native-03'
d=json.loads((ev/'movie/result.json').read_text());selected={};groups={}
for direction in ['down','left','right','up']:
 seq=[]
 for frame in range(8):
  matches=[t for t in d['trace'] if t['segment']=='walk_roll_walk_'+direction and t['action_kind']=='roll' and t['action_frame']==frame]
  t=matches[len(matches)//2];selected[t['tick']]=t;seq.append(t['tick'])
 groups['roll_'+direction]=seq
groups['blood_UP']=[o['tick'] for o in d['clothing_overlay']]
for n in groups['blood_UP']:selected[n]=next(t for t in d['trace'] if t['tick']==n)
for mode in ['false','true']:
 seq=[]
 for direction in ['down','left','right','up']:
  c=next(c for c in d['contacts'] if c['segment']=='finisher_'+mode+'_unarmed_'+direction and c['finisher'])
  n=c['tick']+1;selected[n]=next(t for t in d['trace'] if t['tick']==n);seq.append(n)
 groups['FIN_unarmed_'+mode]=seq
decoded=OUT/'decoded';decoded.mkdir(exist_ok=True)
indices=sorted(selected);expr='+'.join('eq(n\\,%d)'%n for n in indices)
argv=['ffmpeg','-v','error','-threads','1','-i',str(movie),'-vf','select='+expr,'-fps_mode','vfr','-threads','1',str(decoded/'frame_%03d.png')]
run=subprocess.run(argv,capture_output=True,text=True);assert run.returncode==0,run.stderr
files=sorted(decoded.glob('frame_*.png'));assert len(files)==len(indices)
inventory=[]
for n,p in zip(indices,files):
 final=decoded/('frame_%04d.png'%n)
 # use unique names in a separate directory to avoid rename collisions
 final=OUT/'movie-frames'/final.name;final.parent.mkdir(exist_ok=True);p.replace(final)
 inventory.append({'frame':n,'path':str(final.relative_to(OUT)),'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'position':selected[n]['position'],'animation':selected[n]['animation'],'phase':selected[n]['action_frame']})
byindex={x['frame']:OUT/x['path'] for x in inventory}
for group,ns in groups.items():
 board=Image.new('RGB',(240*len(ns),260),(20,24,29));draw=ImageDraw.Draw(board)
 for col,n in enumerate(ns):
  im=Image.open(byindex[n]).convert('RGB');x,y=selected[n]['position'];cx,cy=int(x*2),int(y*2)
  crop=im.crop((cx-90,cy-142,cx+90,cy+38)).resize((240,240),Image.Resampling.NEAREST)
  board.paste(crop,(col*240,20));draw.text((col*240+3,3),'n%d %s:%d'%(n,selected[n]['animation'],selected[n]['action_frame']),fill='white')
 board.save(OUT/(group+'_movie_diagnostic.png'))
probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(movie)],capture_output=True,text=True,check=True)
report={'actual_movie_sha256':hashlib.sha256(movie.read_bytes()).hexdigest(),'ffprobe':json.loads(probe.stdout),'decode_argv':argv,'decoded_actual_frames':len(inventory),'frames':inventory,'groups':groups,'diagnostics':'Crops/nearest scaling for visual review only; original selected whole frames preserved; no source/runtime/evidence modification.'}
(OUT/'movie-proofs.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frames':len(inventory),'movie_sha256':report['actual_movie_sha256'],'probe':report['ffprobe']}))
