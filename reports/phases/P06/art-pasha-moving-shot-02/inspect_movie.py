from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0'); W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/pasha-moving-shot-01/native-02';P=W/'build/P06/pasha-moving-shot-02/pasha-moving-shot.mp4'
import sys
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert len(sys.argv)==2;assert sha(P)==sys.argv[1]
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,duration','-of','json',str(P)]))['streams'][0]
j=json.loads((D/'movie/result.json').read_text());T={t['tick']:t for t in j['trace']}; groups={}; selection=set();crop=(190,90,470,320)
def add(name,nums,cols=8,whole=False):
 nums=[max(0,x) for x in nums];groups[name]={'frames':nums,'columns':cols,'whole':whole};selection.update(nums)
for mode in ['false','true']:
 for di in ['down','left','right','up']:
  seg='moving_shot_'+mode+'_'+di;t=[x for x in j['trace'] if x['segment']==seg];a=t[0]['tick'];b=t[-1]['tick'];add('movie_route_'+mode+'_'+di,list(range(a-3,b+2)))
  fs=[x for x in j['contacts'] if x.get('finisher') and x['segment'].startswith('finisher_'+mode+'_') and x['segment'].endswith('_'+di)];assert len(fs)==5
  add('movie_FIN_'+mode+'_'+di,[f['tick']+off for f in fs for off in [-2,-1,0,4,10,17]],6)
for di in ['down','left','right','up']:
 ps=[x for x in j['clothing_overlay'] if x['direction']==di];assert len(ps)==8
 add('movie_blood_'+di,[x['tick']+off for x in ps for off in [-1,0,1]],3)
add('movie_muzzle_launches',[x['tick']+off for x in j['launches'] for off in [-2,-1,0,1]],4)
extra=[x for x in j['contacts'] if x.get('finisher') and not x['segment'].startswith('finisher_')];add('movie_shared_clip_FIN',[extra[0]['tick']+off for off in [-2,-1,0,4,10,17]],6)
for seg in ['finite_clip_and_refill','options_freeze','wall_body_and_bullet','incoming_before_launch_false','incoming_before_launch_true']:
 ts=[x['tick'] for x in j['trace'] if x['segment']==seg];add('movie_whole_'+seg,[ts[0]-1,ts[len(ts)//2]-1,ts[-1]-1],3,True)
def expr(ns):
 if len(ns)==1:return 'eq(n,'+str(ns[0])+')'
 mid=len(ns)//2;return '('+expr(ns[:mid])+'+'+expr(ns[mid:])+')'
ns=sorted(selection);proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(P),'-vf',"select='"+expr(ns)+"',scale=640:360:flags=neighbor",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
frames={}; size=640*360*3
for n in ns:
 raw=proc.stdout.read(size);assert len(raw)==size,(n,len(raw));frames[n]=Image.frombytes('RGB',(640,360),raw)
err=proc.stderr.read();assert proc.wait()==0,err.decode();assert not proc.stdout.read(1)
for name,g in groups.items():
 cw,ch=(640,360) if g['whole'] else (280,230); cols=g['columns'];out=Image.new('RGB',(cw*cols,(ch+18)*math.ceil(len(g['frames'])/cols)),(23,28,34));d=ImageDraw.Draw(out)
 for i,n in enumerate(g['frames']):
  x=i%cols*cw;y=i//cols*(ch+18);im=frames[n] if g['whole'] else frames[n].crop(crop);out.paste(im,(x,y+18));t=T.get(n+1,{});label='n'+str(n)+' '+t.get('animation','pretrace')+' '+str(t.get('frame',''));d.text((x+1,y+2),label,fill=(240,220,190))
 out.save(O/(name+'.png'))
metrics={'schema':1,'source_head':'17b162d9d4320650f7e0422d63c1c2c77882a9d3','movie_sha256':sha(P),'total_video_frames':int(probe['nb_frames']),'duration_seconds':float(probe['duration']),'actual_decoded_unique_frames':len(ns),'selected_video_frames':ns,'groups':groups,'presentation':'Whole original viewport decoded NN to640x360. Detail boards crop x190..469,y90..319, no redraw or anatomy modification. Labels use trace tick=n+1; adjacent frames included for contact observation.','visual_inspection_pending':True,'phase_approval':False}
(O/'movie_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('Created',len(groups),'boards of',len(ns),'unique actual MP4 frames')
