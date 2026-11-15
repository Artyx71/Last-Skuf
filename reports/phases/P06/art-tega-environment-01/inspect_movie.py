from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/tega-environment-01/native-01';movie=W/'build/P06/tega-environment-01/tega-environment.mp4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(movie)=='5546870556a6500ec9c45b8ada00f3ef4fda717e2a46965ec5917695d22c1cb7';j=json.loads((D/'movie/result.json').read_text());v=json.loads((D/'validation.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']=='6a0224e016e53e13ddb1e6fde747b66e7f75447b';assert sha(D/'validation.json')=='b384f746cfb75d0dc9f373e7871712048973465277d41968dc585db603c41d13'
for p,h in json.loads((D/'source_hashes.json').read_text()).items():assert sha(W/p)==h,p
for a in v['artifacts']:assert sha(W/a['path'])==a['sha256'],a['path']
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]));s=[s for s in probe['streams'] if s['codec_type']=='video'][0];total=int(s['nb_frames']);assert total==4649 and s['avg_frame_rate']=='60/1'
select=set(range(0,total,120))|{total-1};routes={}
for mode in ['false','true']:
 for di in ['down','left','right','up']:
  seg='object_hit_'+mode+'_'+di;tr=[x for x in j['trace'] if x['segment']==seg];routes[seg]=list(range(tr[0]['tick'],tr[-1]['tick']+1));select.update(routes[seg])
for c in j['contacts']:select.update(c['tick']+d for d in [-2,-1,0,1,2,3,6,9])
for b in j['clothing_overlay']:select.update(b['tick']+d for d in [-1,0,1])
select=sorted(n for n in select if 0<=n<total);groups=[]
for n in select:
 if not groups or n>groups[-1][-1]+1:groups.append([n])
 else:groups[-1].append(n)
terms=[('between(n,%d,%d)'%(g[0],g[-1])) if len(g)>1 else ('eq(n,%d)'%g[0]) for g in groups]
def bal(a):
 if len(a)==1:return a[0]
 mid=len(a)//2;return '('+bal(a[:mid])+'+'+bal(a[mid:])+')'
cmd=['ffmpeg','-v','error','-i',str(movie),'-vf',"select='"+bal(terms)+"',scale=640:360:flags=neighbor",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'];raw=subprocess.check_output(cmd);fb=640*360*3;assert len(raw)==len(select)*fb;frames={};out=O/'movie_selected';out.mkdir(exist_ok=True)
for i,n in enumerate(select):
 im=Image.frombytes('RGB',(640,360),raw[i*fb:(i+1)*fb]);im.save(out/('frame_%04d.png'%n));frames[n]=im
crop=(170,120,390,315)
def board(ns,name,cols=7,crop=crop):
 cw,ch=crop[2]-crop[0],crop[3]-crop[1];b=Image.new('RGB',(cw*cols,(ch+16)*math.ceil(len(ns)/cols)),(24,29,35));d=ImageDraw.Draw(b)
 for i,n in enumerate(ns):
  x=i%cols*cw;y=i//cols*(ch+16);b.paste(frames[n].crop(crop),(x,y+16));d.text((x+2,y+2),'movie n='+str(n),fill=(255,220,180))
 b.save(O/name)
for seg,ns in routes.items():board(ns[::2],'movie_'+seg+'_30fps.png')
for di in ['down','left','right','up']:
 cs=[c for c in j['contacts'] if c.get('finisher') and c['segment'].endswith('_'+di)];board([c['tick']+d for c in cs for d in [-2,0,2,9]],'movie_FIN_'+di+'.png',4)
 bs=[b for b in j['clothing_overlay'] if b['direction']==di];board([b['tick']+d for b in bs for d in [-1,0,1]],'movie_blood_'+di+'.png',3)
board(list(range(0,total,120))+[total-1],'movie_whole_recording_2sec.png',5,(0,0,640,360))
cs=[c for c in j['contacts'] if c['target_is_player'] and c['segment'].startswith('incoming')];board([c['tick']+d for c in cs for d in [-2,0,2,9]],'movie_incoming.png',4)
metrics={'source_head':v['source_head'],'video_sha256':sha(movie),'video_frames':total,'duration':s['duration'],'video_size':[s['width'],s['height']],'diagnostic_size':[640,360],'diagnostic_resize':'wholeviewport nearest-neighbor','selected_actual_video_frames':select,'selected_count':len(select),'routes':routes,'command':cmd,'verified_all_validation_and_source_hashes':True,'visual_inspection_pending':True,'audio_listening_performed':False,'phase_approval':False};(O/'movie_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('Decoded',len(select),'actual frames; visual inspection pending')
