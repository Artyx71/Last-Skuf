from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess,io,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/ryzhik-roll-01/native-01';movie=W/'build/P06/ryzhik-roll-01/ryzhik-roll.mp4';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(movie)=='593364901e16d7780f4319a852c6d2f85cbf5e9d49306e994b8a5c512430ce63';j=json.loads((D/'movie/result.json').read_text());probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]));stream=[s for s in probe['streams'] if s['codec_type']=='video'][0];assert int(stream['nb_frames'])==2215;assert stream['avg_frame_rate']=='60/1';select=set(range(0,2215,120))|{2214};routes={}
for di in ['down','left','right','up']:
 tr=[x for x in j['trace'] if x['segment']=='walk_roll_walk_'+di and x['action_kind']=='roll'];a=tr[0]['tick']-3;b=tr[-1]['tick']+4;routes[di]=list(range(a,b+1));select.update(range(a,b+1))
for c in j['contacts']:
 if c.get('finisher') or c['target_is_player']:select.update(c['tick']+d for d in [-2,-1,0,1,2,3,6,9])
# Also cover both Full and Reduced roll states and finite resume.
for segment in ['settings_false','settings_true','options_pause']:
 tr=[x for x in j['trace'] if x['segment']==segment and x['action_kind']=='roll'];select.update(x['tick'] for x in tr[::3])
select=sorted(n for n in select if 0<=n<2215);groups=[]
for n in select:
 if not groups or n>groups[-1][-1]+1:groups.append([n])
 else:groups[-1].append(n)
terms=[('between(n,%d,%d)'%(g[0],g[-1])) if len(g)>1 else ('eq(n,%d)'%g[0]) for g in groups]
def balanced(a):
 if len(a)==1:return a[0]
 mid=len(a)//2;return '('+balanced(a[:mid])+'+'+balanced(a[mid:])+')'
expr=balanced(terms);cmd=['ffmpeg','-v','error','-i',str(movie),'-vf',"select='"+expr+"',scale=640:360:flags=neighbor",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'];raw=subprocess.check_output(cmd);framebytes=640*360*3;assert len(raw)==len(select)*framebytes;decoded={};outdir=O/'movie_selected';outdir.mkdir(exist_ok=True)
for i,n in enumerate(select):
 im=Image.frombytes('RGB',(640,360),raw[i*framebytes:(i+1)*framebytes]);im.save(outdir/('frame_%04d.png'%n));decoded[n]=im
crop=(160,110,410,312)
def board(ns,path,cols=6,scale=1,crop=crop):
 w=crop[2]-crop[0];h=crop[3]-crop[1]+16;b=Image.new('RGB',(w*cols,h*math.ceil(len(ns)/cols)),(24,29,35));dr=ImageDraw.Draw(b)
 for i,n in enumerate(ns):
  x=i%cols*w;y=i//cols*h;b.paste(decoded[n].crop(crop),(x,y+16));dr.text((x+1,y+1),'video n='+str(n),fill=(255,225,195))
 b.resize((b.width*scale,b.height*scale),Image.Resampling.NEAREST).save(O/path)
for di,ns in routes.items():board(ns[::2],'movie_roll_'+di+'_continuous_30fps.png',7)
board(list(range(0,2215,120))+[2214],'movie_whole_recording_2sec_samples.png',5,crop=(0,0,640,360))
for di in ['down','left','right','up']:
 cs=[c for c in j['contacts'] if c.get('finisher') and c['segment'].endswith('_'+di)];ns=[c['tick']+delta for c in cs for delta in [-2,0,2,9]];board(ns,'movie_FIN_'+di+'_contacts_reactions.png',4)
metrics={'schema':1,'source_head':'407f9a1df6c3d8ed110ab908b234fad4750b622d','movie_sha256':sha(movie),'original_video_size':[int(stream['width']),int(stream['height'])],'diagnostic_decode_size':[640,360],'diagnostic_rescale':'Exact wholeviewport nearest-neighbor 1/2; original movie1280x720 remains hash-bound','video_frames':int(stream['nb_frames']),'video_duration':stream['duration'],'video_rate':stream['avg_frame_rate'],'selected_actual_video_frames':select,'selected_count':len(select),'raw_decoder_argv':cmd,'selection_basis':'Actual movie physical trace ticks with surrounding frames; visual alignment still requires inspection; no source-animation reconstruction','decoded_original_viewports_sha256':{str(p.relative_to(O)):sha(p) for p in sorted(outdir.glob('*.png'))},'visual_acceptance_pending':True,'audio_listening_performed':False,'full_phase_approval':False};(O/'movie_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['selected_actual_video_frames','decoded_original_viewports_sha256','raw_decoder_argv']}))
