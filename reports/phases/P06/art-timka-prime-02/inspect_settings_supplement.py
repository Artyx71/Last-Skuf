from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;E=W/'reports/phases/P06/timka-prime-01/movie-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((O/'movie_metrics.json').read_text());r=json.loads((E/'movie/result.json').read_text());groups=[];ns=set()
for seg in dict.fromkeys(t['segment'] for t in r['trace']):
 if not seg.startswith('settings_'):continue
 a=[t for t in r['trace'] if t['segment']==seg and t['action_kind'].startswith('finish_')];picks=[]
 for phase in range(3):
  matches=[t for t in a if t['action_frame']==phase];assert matches;picks.append(matches[0] if phase in [0,1] else matches[min(3,len(matches)-1)])
 groups.append({'name':seg+'_full_action','picks':picks});ns.update(p['tick']-1 for p in picks)
assert len(groups)==2;fd=O/'selected_movie_frames';sub=fd/'settings_batch';sub.mkdir(exist_ok=True);values=sorted(ns);sel='+'.join('eq(n\\,'+str(n)+')' for n in values);cmd=['ffmpeg','-v','error','-n','-i',str(W/'build/P06/timka-prime-02/timka-prime.mp4'),'-vf','select='+sel,'-fps_mode','vfr',str(sub/'frame_%04d.png')];p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr;files=sorted(sub.glob('frame_*.png'));assert len(files)==len(values)
for n,f in zip(values,files):
 final=fd/('video_n'+str(n).zfill(4)+'.png');assert not final.exists();f.rename(final);m['selected_real_frames'][str(n)]={'path':str(final.relative_to(O)),'sha256':sha(final)}
sub.rmdir()
for g in groups:
 board=Image.new('RGB',(len(g['picks'])*288,318),(225,228,220));draw=ImageDraw.Draw(board)
 for i,t in enumerate(g['picks']):
  n=t['tick']-1;im=Image.open(O/m['selected_real_frames'][str(n)]['path']).convert('RGB');x,y=t['position'];piece=im.crop(((round(x)-72)*2,(round(y)-88)*2,(round(x)+72)*2,(round(y)+48)*2));board.paste(piece,(i*288,44));draw.text((i*288+3,2),t['animation']+' f'+str(t['frame']),fill=(70,30,30));draw.text((i*288+3,17),'tick'+str(t['tick'])+' video n'+str(n),fill=(70,30,30));draw.text((i*288+3,30),g['name'],fill=(70,30,30))
 board.save(O/(g['name']+'_MOVIE_ALIGNED.png'))
m['frames_decoded']=len(m['selected_real_frames']);m['filmstrip_groups']+=groups;(O/'movie_metrics.json').write_text(json.dumps(m,indent=2)+'\n');commands=json.loads((O/'decode_commands.json').read_text());commands.append({'argv':cmd,'exit_code':p.returncode,'actual_video_n':values,'scope':'Supplement: actual lowercase GDScript Boolean segment names'});(O/'decode_commands.json').write_text(json.dumps(commands,indent=2)+'\n');print('Added2settingsfilmstrips6realframes; total '+str(m['frames_decoded']))
