from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/ryzhik-roll-01/native-02';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();v=json.loads((D/'validation.json').read_text());n=json.loads((D/'live/result.json').read_text());assert not v['passed'] and v['source_unchanged'] and v['source_head']=='8c10ff285fea6dff214ebb309ed625aea7e62925';assert len(n['captures'])==120 and len(n['checks'])==418 and all(x['passed'] for x in n['checks']);assert len(n['contacts'])==60
commands=json.loads((D/'commands.json').read_text());assert commands[0]['name']=='live' and commands[0]['exit_code']==0 and commands[1]['name']=='movie' and commands[1]['exit_code']==124
for a in v['artifacts']:assert sha(W/a['path'])==a['sha256'],a['path']
source_differences=[]
for path,h in json.loads((D/'source_hashes.json').read_text()).items():
 if sha(W/path)!=h:source_differences.append(path)
assert all(x in ['game/tests/ryzhik_roll_replay.gd','tools/qa_p06_ryzhik_roll.py'] for x in source_differences),source_differences
captures={x['name']:x for x in n['captures']};crop=(160,110,410,312)
def board(names,out,cols=3,scale=2):
 ims=[Image.open(Path(captures[name]['path'])).convert('RGBA') for name in names];b=Image.new('RGBA',((crop[2]-crop[0])*cols,(crop[3]-crop[1]+16)*math.ceil(len(ims)/cols)),(24,29,35,255));draw=ImageDraw.Draw(b)
 for i,(name,im) in enumerate(zip(names,ims)):
  x=(i%cols)*250;y=(i//cols)*218;b.paste(im.crop(crop),(x,y+16));draw.text((x+2,y+2),name.replace('walk_roll_walk_','').replace('finisher_',''),fill=(255,220,180,255))
 b.resize((b.width*scale,b.height*scale),Image.Resampling.NEAREST).save(O/out)
for di in ['down','left','right','up']:
 names=['walk_roll_walk_'+di+'_'+x for x in ['world_before']+['roll'+str(i) for i in range(8)]+['world_after']];board(names,'native_roll_'+di+'_continuous_route.png',5,1)
 for cat in ['unarmed','blunt','environmental']:
  for reduced in ['false','true']:board(['finisher_'+reduced+'_'+cat+'_'+di+'_'+phase for phase in ['windup','contact','corpse_recovery']],'native_FIN_'+reduced+'_'+cat+'_'+di+'.png',3,2)
board([x for x in captures if x.startswith('Core_incoming')],'native_incoming6.png',3,2)
Image.open(D/'live/wall_blocks_roll.png').save(O/'native_wall_full_viewport.png');Image.open(D/'live/ryzhik_ready_after_restart.png').save(O/'native_restart_full_viewport.png')
metrics={'source_head':v['source_head'],'native_checks':len(n['checks']),'movie_checks':0,'movie_complete':False,'movie_exit124':True,'current_source_differences_after_frozen_live':source_differences,'native_captures':len(captures),'actual_contacts_per_run':len(n['contacts']),'all_validation_source_and_evidence_hashes_verified':True,'roll_routes':{},'contacts':n['contacts'],'runtime_visual_review_pending':True,'full_phase_approval':False}
for di in ['down','left','right','up']:
 trace=[x for x in n['trace'] if x['segment']=='walk_roll_walk_'+di];roll=[x for x in trace if x['action_kind']=='roll'];seen=[]
 for x in roll:
  if not seen or seen[-1]!=x['frame']:seen.append(x['frame'])
 assert seen==list(range(8));jumps=[math.dist(a['position'],b['position']) for a,b in zip(trace,trace[1:])];assert max(jumps)<=3.01;metrics['roll_routes'][di]={'seen_frames':seen,'start_position':roll[0]['position'],'last_roll_position':roll[-1]['position'],'max_tick_distance':max(jumps),'sampled_ticks':len(roll),'source_frame_capture_ticks':[captures['walk_roll_walk_'+di+'_roll'+str(i)]['tick'] for i in range(8)]}
(O/'native_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['contacts','roll_routes']}))
