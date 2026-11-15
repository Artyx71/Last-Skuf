from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess
W=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0/.autopilot/worktrees/P06');O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();E=W/'reports/phases/P06/timka-present-01/native-01';D=W/'game/assets/art/characters/timka';v=json.loads((E/'validation.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']=='69ffc58c7ff2dedd773bd58b137553c3666ad1da';sources=json.loads((E/'source_hashes.json').read_text());assert all(sha(W/n)==h for n,h in sources.items())
for a in v['artifacts']:assert sha(W/a['path'])==a['sha256']
metrics={'source_head':v['source_head'],'validation_passed':True,'recorded_source_bindings_verified':len(sources),'validation_artifact_bindings_verified':len(v['artifacts']),'clothing_frames':{},'native_captures':[],'movie_frames':[]}
for kind in ['world','action']:
 s=json.loads((D/(kind+'.sockets.json')).read_text());m=json.loads((D/(kind+'.json')).read_text());im=Image.open(D/(kind+'_sheet.png')).convert('RGBA');assert s['sheet_sha256']==m['sha256']==sha(D/(kind+'_sheet.png'));assert s['layout_profile']==m['layout_profile']=='timka_supported_v1';assert s['source_column_mapping']==m['source_column_mapping'];assert s['source_cells']==m['source_cells']==len(s['frames']);pal=set(tuple(c) for c in s['garment_palette']);points=[]
 for f,mf in zip(s['frames'],m['frames']):
  i=f['index'];r,c=divmod(i,m['columns_per_direction']);assert f['direction']==mf['direction'] and f['column']==mf['column']==c and f['source_column']==mf['source_column'];piece=im.crop((48*c,64*r,48*c+48,64*r+64));assert hashlib.sha256(piece.tobytes()).hexdigest()==f['source_frame_rgba_sha256']==mf['rgba_sha256'];x,y=f['clothing'];assert all(type(z)==int for z in [x,y]) and 0<=x<48 and 0<=y<64;px=piece.getpixel((x,y));assert px[3]==255;points.append({'index':i,'direction':f['direction'],'column':c,'clothing':[x,y],'rgba':list(px),'in_initial_candidate_palette':px[:3] in pal})
  # Original complete frame kept intact; point identified by a ring outside centre pixel.
  show=Image.new('RGBA',(48,76),(225,228,220,255));show.alpha_composite(piece,(0,12));show=show.resize((288,456),Image.Resampling.NEAREST);draw=ImageDraw.Draw(show);draw.text((4,2),kind+' '+str(i)+' '+str([x,y]),fill=(110,45,45,255));sx=x*6+3;sy=(y+12)*6+3;draw.ellipse((sx-11,sy-11,sx+11,sy+11),outline=(15,175,205,255),width=2);show.save(O/(kind+'_socket_'+str(i).zfill(2)+'.png'))
 metrics['clothing_frames'][kind]=points
r=json.loads((E/'live/result.json').read_text());movie=json.loads((E/'movie/result.json').read_text());assert r['passed'] and movie['passed'];metrics['live_checks']=len(r['checks']);metrics['movie_checks']=len(movie['checks']);metrics['live_trace_records']=len(r['trace']);metrics['movie_trace_records']=len(movie['trace'])
for capture in r['captures']:
 p=Path(capture['path']);assert p.is_file() and Image.open(p).size==(640,360);metrics['native_captures'].append({'path':str(p.relative_to(W)),'sha256':sha(p),'tick':capture['tick'],'animation':capture['animation'],'frame':capture['frame']})
# Independently decode real recording; sample transitions at every first4-direction action frame,
# plus frame-before/after cancellations, hurt and fall. Numbering is video n, no unverified physics mapping claim.
frames=set(range(5,45))
for seg in ['disengage_left','disengage_right','disengage_up','wall','interrupt_hurt','interrupt_death','pause']:
 a=[t for t in movie['trace'] if t['segment']==seg];last=None
 for i,t in enumerate(a):
  key=(t['animation'],t['frame'],t['action_kind'])
  if key!=last:
   for n in [t['tick']-1,t['tick'],t['tick']+1,t['tick']+2]:
    if 0<=n<904:frames.add(n)
   last=key
 for n in [a[-1]['tick']-1,a[-1]['tick'],a[-1]['tick']+1]:
  if n<904:frames.add(n)
fd=O/'movie_frames';fd.mkdir(exist_ok=True);moviepath=W/'build/P06/timka-present-01/timka-present.mp4';selection='+'.join('eq(n\\,'+str(n)+')' for n in sorted(frames));cmd=['ffmpeg','-v','error','-n','-i',str(moviepath),'-fps_mode','vfr',str(fd/'frame_%04d.png')];run=subprocess.run(cmd,capture_output=True,text=True);assert run.returncode==0,run.stderr
files=sorted(fd.glob('frame_*.png'));assert len(files)==904
for n,p in enumerate(files):metrics['movie_frames'].append({'video_frame_n':n,'path':str(p.relative_to(O)),'sha256':sha(p)})
(O/'decode_command.json').write_text(json.dumps({'argv':cmd,'exit_code':run.returncode,'movie_path':str(moviepath.relative_to(W)),'movie_sha256':sha(moviepath),'selected_frames':sorted(frames),'frames_written':len(files),'no_runtime_execution':True},indent=2)+'\n')
(O/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({'verified_sources':len(sources),'verified_artifacts':len(v['artifacts']),'clothing_points':sum(len(x) for x in metrics['clothing_frames'].values()),'captures':len(r['captures']),'actual_movie_frames':len(files),'movie_sha256':sha(moviepath)}))
