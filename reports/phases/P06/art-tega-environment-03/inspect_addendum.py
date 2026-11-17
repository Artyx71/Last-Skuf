from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/tega-environment-01/native-03';P=W/'reports/phases/P06/tega-environment-01/native-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();head='20cbc322441a80675907bf407f12962778c6c084'
def write(name,v):(O/name).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
v=json.loads((D/'validation.json').read_text());assert sha(D/'validation.json')=='57da4543532eb476fc066fd026637fe2fc8742a027e6dd029421fb8d0ff72946';assert sha(D/'source_hashes.json')=='ad485e36292ef14131ec1cbb02390aa1a66ec0b34fc57bbcf83c41e448f89c23';assert v['source_head']==head and v['source_unchanged'] and v['passed'];old=json.loads((P/'source_hashes.json').read_text());new=json.loads((D/'source_hashes.json').read_text())
for k,h in new.items():assert sha(W/k)==h,k
for a in v['artifacts']:assert sha(W/a['path'])==a['sha256'],a['path']
delta={k:{'before':old.get(k),'after':new.get(k)} for k in sorted(old.keys()|new.keys()) if old.get(k)!=new.get(k)};assert len(delta)==2
n=json.loads((D/'live/result.json').read_text());m=json.loads((D/'movie/result.json').read_text());assert len(n['checks'])==433 and len(m['checks'])==305
for result in [n,m]:assert result['passed'] and result['actual_input'] and result['renderer']=='X11' and all(x['passed'] for x in result['checks']) and len(result['contacts'])==66 and len(result['trace'])==4792 and len(result['clothing_overlay'])==12
pngs={}
for c in n['captures']:
 p=Path(c['path']);h=sha(p);oldp=P/'live'/p.name;assert h==sha(oldp);pngs[str(p.relative_to(W))]={'sha256':h,'old_corresponding_path':str(oldp.relative_to(W)),'rgba_file_exact':True}
assert len(pngs)==128
art={k:h for k,h in new.items() if k.startswith('game/assets/art/characters/tega/') or k.startswith('game/scripts/actors/')};assert all(old.get(k)==h for k,h in art.items())
write('source_delta_metrics.json',{'schema':1,'source_head':head,'previous_art_source':'c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd','source_binding_count':len(new),'changed_paths':delta,'art_socket_actor_script_bindings_unchanged':art,'all128_fresh_nativePNG_byteexact_to_accepted02':pngs,'all_current_source_and_validation_hashes_verified':True,'native_checks':433,'movie_checks':305,'actual_contacts_per_run':66,'visual_inspection_pending':True,'phase_approval':False})
movie=W/'build/P06/tega-environment-03/tega-environment.mp4';assert sha(movie)=='59c65f1c654ef84cfd79bbbb51090980ac879c544c5e23281f284dffa402fa60';probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(movie)]));s=next(x for x in probe['streams'] if x['codec_type']=='video');assert int(s['nb_frames'])==4810 and s['avg_frame_rate']=='60/1'
select=set();routes={};orders={}
for mode in ['false','true']:
 for di in ['down','left','right','up']:
  seg='object_hit_'+mode+'_'+di;tr=[x for x in m['trace'] if x['segment']==seg and x['action_kind']=='special'];a=tr[0]['tick']-3;b=tr[-1]['tick']+5;routes[seg]=list(range(a,b+1,2));select.update(routes[seg]);ph=[]
  for x in tr:
   if not ph or ph[-1]!=x['action_frame']:ph.append(x['action_frame'])
  assert ph==[0,1,2];orders[seg]=ph
for c in m['contacts']:
 if c.get('finisher'):select.update(c['tick']+d for d in [-2,-1,0,2,9])
for c in m['clothing_overlay']:select.update(c['tick']+d for d in [-1,0,1])
select.update([0,4809]);select=sorted(select);terms=['eq(n,%d)'%x for x in select]
def bal(a):
 if len(a)==1:return a[0]
 mid=len(a)//2;return '('+bal(a[:mid])+'+'+bal(a[mid:])+')'
cmd=['ffmpeg','-v','error','-i',str(movie),'-vf',"select='"+bal(terms)+"',scale=640:360:flags=neighbor",'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'];raw=subprocess.check_output(cmd);fb=640*360*3;assert len(raw)==fb*len(select);frames={n:Image.frombytes('RGB',(640,360),raw[i*fb:(i+1)*fb]) for i,n in enumerate(select)}
def board(ns,name,cols=7,crop=(170,120,390,315)):
 cw,ch=crop[2]-crop[0],crop[3]-crop[1];im=Image.new('RGB',(cw*cols,(ch+16)*math.ceil(len(ns)/cols)),(24,29,35));d=ImageDraw.Draw(im)
 for i,n in enumerate(ns):
  x=i%cols*cw;y=i//cols*(ch+16);im.paste(frames[n].crop(crop),(x,y+16));d.text((x+2,y+2),'actual movie n='+str(n),fill=(255,220,180))
 im.save(O/name)
for seg,ns in routes.items():board(ns,'movie_'+seg+'_continuous30fps.png')
for di in ['down','left','right','up']:
 cs=[c for c in m['contacts'] if c.get('finisher') and c['segment'].endswith('_'+di)];board([c['tick']+d for c in cs for d in [-2,-1,0,2,9]],'movie_FIN_'+di+'.png',5)
 bs=[c for c in m['clothing_overlay'] if c['direction']==di];board([c['tick']+d for c in bs for d in [-1,0,1]],'movie_blood_'+di+'.png',3)
board([0,4809],'movie_initial_final_fullviewport.png',2,(0,0,640,360))
write('movie_metrics.json',{'schema':1,'source_head':head,'actual_video_sha256':sha(movie),'video_frames':4810,'video_duration_seconds':s['duration'],'video_original_size':[s['width'],s['height']],'diagnostic_size':[640,360],'resize':'wholeviewport nearest-neighbor, crop review boards only','selected_actual_video_frame_indices':select,'selected_count':len(select),'routes':routes,'observed_live_special_orders':orders,'real_clothing_overlay_movie':m['clothing_overlay'],'decode_command':cmd,'individual_decoded_PNG_cache_saved':False,'all_4810_frames_watched':False,'visual_inspection_pending':True,'phase_approval':False})
print('hashes verified;128 PNG byteexact; selected actualvideo frames',len(select),'boards17; inspection pending')
