from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math,collections
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';BASE=WORK/'reports/phases/P06/attempt1/ryzhik-world-native-01';OUT=ROOT/'reports/phases/P06/art-preflight';PFX='ryzhik-world-native-review-v1';D=OUT/(PFX+'-diagnostics');assert not D.exists();D.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();validation=json.loads((BASE/'validation.json').read_text());sources=json.loads((BASE/'source_hashes.json').read_text());sourcebad=[p for p,h in sources.items() if not (WORK/p).is_file() or sha(WORK/p)!=h];artifactbad=[x['path'] for x in validation['artifacts'] if not (WORK/x['path']).is_file() or sha(WORK/x['path'])!=x['sha256']];assert not sourcebad,sourcebad;assert not artifactbad,artifactbad
folder=WORK/'game/assets/art/characters/ryzhik';atlas=Image.open(folder/'world_sheet.png').convert('RGBA');meta=json.loads((folder/'world.json').read_text());assert sha(folder/'world_sheet.png')==meta['sha256']==sha(WORK/meta['source_adoption']['native']);states={'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]};directions=['down','left','right','up'];live=json.loads((BASE/'live/result.json').read_text());movie=json.loads((BASE/'movie/result.json').read_text());checks=[]
def cell_for(item):
 state,direction=item['animation'].rsplit('_',1);row=directions.index(direction);col=states[state][item['frame']];return atlas.crop((col*48,row*64,col*48+48,row*64+64))
def verify_capture(path,item):
 im=Image.open(path).convert('RGB');assert im.size==(640,360);cell=cell_for(item);origin=(round(item['visual_origin'][0])-24,round(item['visual_origin'][1])-32);bad=0;count=0
 for y in range(64):
  for x in range(48):
   pixel=cell.getpixel((x,y))
   if pixel[3]:count+=1;bad+=im.getpixel((origin[0]+x,origin[1]+y))!=pixel[:3]
 return {'path':str(path.relative_to(WORK)),'opaque_pixels':count,'opaque_RGB_mismatches':bad,'animation':item['animation'],'frame':item['frame'],'tick':item['physics_tick']}
for name,item in live['captures'].items():checks.append(verify_capture(BASE/'live'/(name+'.png'),item))
for path in sorted((BASE/'live').glob('transition_*.png')):
 n=int(path.name.split('_')[1]);checks.append(verify_capture(path,live['trace'][n-1]))
assert len(checks)==40 and all(x['opaque_RGB_mismatches']==0 for x in checks)
for row,direction in enumerate(directions):
 board=Image.new('RGB',(8*192,250),'#202027');draw=ImageDraw.Draw(board);entries=[(name,item) for name,item in live['captures'].items() if item['animation'].endswith('_'+direction)];entries.sort(key=lambda x:({'idle':0,'walk':1,'run':2}[x[1]['animation'].rsplit('_',1)[0]],x[1]['frame']))
 for n,(name,item) in enumerate(entries):
  im=Image.open(BASE/'live'/(name+'.png')).convert('RGB');x,y=item['position'];crop=im.crop((round(x)-48,round(y)-74,round(x)+48,round(y)+22)).resize((192,192),Image.Resampling.NEAREST);board.paste(crop,(n*192,35));draw.text((n*192+3,3),name,fill='white')
 board.save(D/f'{direction}-all8-live.png')
board=Image.new('RGB',(4*240,2*240),'#202027');draw=ImageDraw.Draw(board)
for n,path in enumerate(sorted((BASE/'live').glob('transition_*.png'))):
 number=int(path.name.split('_')[1]);item=live['trace'][number-1];im=Image.open(path).convert('RGB');x,y=item['position'];crop=im.crop((round(x)-60,round(y)-90,round(x)+60,round(y)+15)).resize((240,210),Image.Resampling.NEAREST);ox=n%4*240;oy=n//4*240;board.paste(crop,(ox,oy+30));draw.text((ox+3,oy+2),path.stem,fill='white')
board.save(D/'continuous-endpoints-live.png')
# Grid groups are intentionally reset; continuous block is separately delimited.
traces={}
for mode,data in [('live',live),('movie',movie)]:
 trace=data['trace'];gridmax=max(math.hypot(x['visual_origin'][0]-round(x['visual_origin'][0]),x['visual_origin'][1]-round(x['visual_origin'][1])) for x in trace);fractional=sum(math.hypot(x['position'][0]-round(x['position'][0]),x['position'][1]-round(x['position'][1]))>.1 for x in trace);groups=[]
 for item in trace:
  key=(item['sequence'],item['animation'])
  if not groups or groups[-1]['key']!=key:groups.append({'key':key,'samples':[]})
  groups[-1]['samples'].append(item)
 loops=[]
 for g in groups:
  count=len(states[g['key'][1].rsplit('_',1)[0]]);onsets=[];last=None
  for item in g['samples']:
   if item['frame']!=last:onsets.append(item['frame']);last=item['frame']
  assert all(b==(a+1)%count for a,b in zip(onsets,onsets[1:])),(mode,g['key'],onsets)
  loops.append({'group':g['key'],'samples':len(g['samples']),'onsets':onsets})
 continuous=trace[data['continuous_trace_start']:];motion=[]
 for a,b in zip(continuous,continuous[1:]):
  dt=(b['physics_tick']-a['physics_tick'])/60;dist=math.dist(a['position'],b['position']);limit=120*1.44*dt;assert dist<=limit+.001;motion.append({'from_tick':a['physics_tick'],'to_tick':b['physics_tick'],'distance':dist,'maximum_speed_dt':limit})
 traces[mode]={'max_visual_grid_error':gridmax,'fractional_physics_samples':fractional,'groups':loops,'continuous_motion_bounded':True,'continuous_max_step':max(x['distance'] for x in motion)}
metrics={'frozen_source_head':validation['source_head'],'source_entries_verified':len(sources),'source_mismatches':sourcebad,'validation_artifacts_verified':len(validation['artifacts']),'artifact_mismatches':artifactbad,'native_sha256':sha(folder/'world_sheet.png'),'PNG_capture_pixel_comparisons':checks,'traces':traces,'source_inventory_sha256':sources,'native_artifact_inventory_sha256':{x['path']:x['sha256'] for x in validation['artifacts']}}
(OUT/(PFX+'-metrics.json')).write_text(json.dumps(metrics,indent=2)+'\n');print('source/artifacts',len(sources),len(validation['artifacts']),'40PNGs0opaquemismatches','grid/fractional',[(k,v['max_visual_grid_error'],v['fractional_physics_samples']) for k,v in traces.items()])
