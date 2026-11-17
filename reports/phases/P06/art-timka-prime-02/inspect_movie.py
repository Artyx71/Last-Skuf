from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;E=W/'reports/phases/P06/timka-prime-01/movie-02';L=W/'reports/phases/P06/timka-prime-01/native-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads((E/'validation.json').read_text());live=json.loads((L/'validation.json').read_text());r=json.loads((E/'movie/result.json').read_text());assert v['passed'] and v['source_unchanged'] and v['source_head']==live['source_head']=='db84b39711181bb93b6ce58ac4bb7a244dee032b';assert v['reused_completed_live']['sha256']==sha(L/'validation.json') and v['reused_completed_live']['captures']==90;assert len(r['checks'])==214 and r['passed'];sources=json.loads((E/'source_hashes.json').read_text());assert sources==json.loads((L/'source_hashes.json').read_text())
for item in v['artifacts']:assert sha(W/item['path'])==item['sha256']
prod=json.loads((O/'native_metrics.json').read_text())['production_source_inventory_sha256'];assert all(sha(W/n)==h for n,h in prod.items());changes={n:{'recorded':h,'current':sha(W/n)} for n,h in sources.items() if sha(W/n)!=h};assert set(changes)<={'tools/verify_p06_timka_prime.py','tools/tests/test_p06_prime_recovery.py'},changes
probe=json.loads((E/'movie_probe.json').read_text());stream=next(s for s in probe['streams'] if s['codec_type']=='video');N=int(stream['nb_frames']);groups=[];wanted=set();graphs=[]
def group(name,picks):
 for p in picks:wanted.add(p['tick']-1)
 groups.append({'name':name,'picks':picks})
for context in ['present','prime']:
 for di in ['down','left','right','up']:
  route=context+'_locomotion_'+di;ts=[t for t in r['trace'] if t['segment']==route];runs=[];run=[]
  for t in ts:
   if t['animation']=='walk_'+di:run.append(t)
   elif run:runs.append(run);run=[]
  if run:runs.append(run)
  movement=max(runs,key=len);trans=[];previous=None;wraps=0
  for t in movement:
   if previous is not None and t['frame']<previous:wraps+=1
   if t['frame']!=previous:trans.append(t)
   previous=t['frame']
  assert wraps>=2 and set(t['frame'] for t in movement)==set(range(4 if context=='present' else 2));picks=[]
  for frame in [0,1]:
   a=[t for t in ts if t['animation']=='idle_'+di and t['frame']==frame and t['tick']<movement[0]['tick']];assert a;picks.append(a[len(a)//2])
  picks+=trans;group(route+'_two_cycles',picks);graphs.append({'route':route,'ticks':[movement[0]['tick'],movement[-1]['tick']],'wraps_independent':wraps,'changes':[{'tick':t['tick'],'frame':t['frame'],'position':t['position']} for t in trans]})
for seg in list(dict.fromkeys(t['segment'] for t in r['trace'])):
 if not (seg.startswith('clinch_') or seg.startswith('V_finisher_') or seg in ['settings_False','settings_True']):continue
 ts=[t for t in r['trace'] if t['segment']==seg];picks=[]
 actions=[t for t in ts if t['action_kind'].startswith('finish_')]
 if not actions:continue
 for phase in range(3):
  a=[t for t in actions if t['action_frame']==phase];assert a,(seg,phase)
  picks.append(a[0] if phase in [0,1] else a[min(3,len(a)-1)])
 group(seg+'_full_action',picks)
 if seg.startswith('clinch_'):
  strike=[t for t in ts if t['animation'].startswith('prime_strike_') and t['action_kind']=='shove'];p=[]
  for phase in range(3):
   a=[t for t in strike if t['action_frame']==phase];assert a;p.append(a[0] if phase in [0,1] else a[min(2,len(a)-1)])
  group(seg+'_earned_heavy_strike',p)
for seg in ['interrupt_clinch_hurt','interrupt_clinch_death']:
 ts=[t for t in r['trace'] if t['segment']==seg];picks=[];last=None
 for t in ts:
  key=t['animation'],t['frame'],t['action_kind']
  if key!=last:picks.append(t);last=key
 group(seg+'_actual_incoming',picks)
# Extra neighbouring real frames establish the movie/physics offset against source pixels.
alignment=[]
for g in groups:
 if not g['name'].endswith('_two_cycles'):continue
 p=next(t for t in g['picks'] if t['animation'].startswith('walk_'))
 alignment.append(p)
 for off in [-2,-1,0,1]:wanted.add(p['tick']+off)
fd=O/'selected_movie_frames';fd.mkdir(exist_ok=True);movie=Path(v['movie_path']);commands=[];frame_index={}
ns=sorted(wanted);assert min(ns)>=0 and max(ns)<N
for batch in range(0,len(ns),40):
 values=ns[batch:batch+40];sub=fd/('batch_'+str(batch//40));sub.mkdir(exist_ok=True);sel='+'.join('eq(n\\,'+str(n)+')' for n in values);cmd=['ffmpeg','-v','error','-n','-i',str(movie),'-vf','select='+sel,'-fps_mode','vfr',str(sub/'frame_%04d.png')];p=subprocess.run(cmd,capture_output=True,text=True);assert p.returncode==0,p.stderr;files=sorted(sub.glob('frame_*.png'));assert len(files)==len(values)
 for n,f in zip(values,files):
  final=fd/('video_n'+str(n).zfill(4)+'.png');assert not final.exists();f.rename(final);frame_index[n]={'path':str(final.relative_to(O)),'sha256':sha(final)}
 sub.rmdir();commands.append({'argv':cmd,'exit_code':p.returncode,'actual_video_n':values})
for g in groups:
 picks=g['picks'];width=192 if g['name'].endswith('_two_cycles') else 288;height=244 if width==192 else 318;board=Image.new('RGB',(len(picks)*width,height),(225,228,220));draw=ImageDraw.Draw(board)
 for i,t in enumerate(picks):
  n=t['tick']-1;im=Image.open(O/frame_index[n]['path']).convert('RGB');x,y=t['position'];box=((round(x)-48)*2,(round(y)-76)*2,(round(x)+48)*2,(round(y)+24)*2) if width==192 else ((round(x)-72)*2,(round(y)-88)*2,(round(x)+72)*2,(round(y)+48)*2);piece=im.crop(box);board.paste(piece,(i*width,44));draw.text((i*width+3,2),t['animation']+' f'+str(t['frame']),fill=(70,30,30));draw.text((i*width+3,17),'tick'+str(t['tick'])+' video n'+str(n),fill=(70,30,30));draw.text((i*width+3,30),str(t['position']),fill=(70,30,30))
 board.save(O/(g['name']+'_MOVIE_ALIGNED.png'))
# Native sprite templates are used only for an objective alignment score, never pasted into footage.
D=W/'game/assets/art/characters/timka';world=Image.open(D/'world_sheet.png').convert('RGBA');scores=[]
for t in alignment:
 di=t['animation'].split('_')[-1];row=['down','left','right','up'].index(di);prime=t['segment'].startswith('prime');col=(6 if prime else 2)+t['frame'];sprite=world.crop((col*48,row*64,col*48+48,row*64+64));x,y=t['visual_origin'];errors={}
 for off in [-2,-1,0,1]:
  im=Image.open(O/frame_index[t['tick']+off]['path']).convert('RGB');tile=im.crop(((round(x)-24)*2,(round(y)-32)*2,(round(x)+24)*2,(round(y)+32)*2));total=0;count=0
  for py in range(64):
   for px in range(48):
    expect=sprite.getpixel((px,py))
    if expect[3]:
     actual=tile.getpixel((px*2+1,py*2+1));total+=sum(abs(expect[k]-actual[k]) for k in range(3));count+=3
  errors[str(off)]=round(total/count,3)
 scores.append({'segment':t['segment'],'tick':t['tick'],'errors_by_video_n_minus_tick':errors})
avg={str(off):round(sum(s['errors_by_video_n_minus_tick'][str(off)] for s in scores)/len(scores),3) for off in [-2,-1,0,1]};assert avg['-1']==min(avg.values()),avg
metrics={'schema':1,'source_head':v['source_head'],'movie_validation_sha256':sha(E/'validation.json'),'live_validation_sha256':sha(L/'validation.json'),'native_movie_source_snapshots_identical':True,'verified_movie_artifacts':len(v['artifacts']),'movie_passed_checks':214,'movie_sha256':sha(movie),'movie_dimensions':[stream['width'],stream['height']],'movie_frames':N,'movie_fps':stream['r_frame_rate'],'movie_seconds':stream['duration'],'selected_real_frames':frame_index,'frames_decoded':len(frame_index),'filmstrip_groups':groups,'eight_routes_recomputed':graphs,'pixel_alignment_scores':scores,'pixel_alignment_mean':avg,'video_frame_mapping':'n=physics_tick-1, verified with native sprite RGB comparisons','current_outside_scope_author_changes':changes,'reviewer_engine_executions':0,'full_phase_approval':False}
(O/'decode_commands.json').write_text(json.dumps(commands,indent=2)+'\n');(O/'movie_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:metrics[k] for k in ['source_head','movie_passed_checks','movie_dimensions','movie_frames','movie_seconds','frames_decoded','pixel_alignment_mean','current_outside_scope_author_changes']}));print('filmstrips',len(groups))
