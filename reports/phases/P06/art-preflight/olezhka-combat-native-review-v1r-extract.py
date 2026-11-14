from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=ROOT/'reports/phases/P06/art-preflight/olezhka-combat-native-review-v1r-diagnostics';BASE=WORK/'reports/phases/P06/attempt1/olezhka-combat-native-01';d=json.loads((BASE/'movie/result.json').read_text());trace={x['tick']:x for x in d['trace']};selected=set();records=[]
for before,after in zip(d['trace'],d['trace'][1:]):
 if before['segment']!=after['segment']:continue
 if before['animation']!=after['animation'] or before['action_frame']!=after['action_frame']:
  if after['segment'].startswith('continuous_run_guard_'):
   selected.update(range(after['tick']-2,after['tick']+4))
for c in d['contacts']:
 if (c['segment'].startswith('counter_') and not c['target_is_player']) or c['segment'].startswith('finisher_'):
  selected.update(range(c['tick']-2,c['tick']+13))
selected={x for x in selected if x in trace};frames={}
cmd=['ffmpeg','-v','error','-i',str(WORK/'build/P06/attempt1/olezhka-combat-native-01/olezhka.avi'),'-vf','scale=640:360:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);i=0;size=640*360*3
# Candidate tick alignment indices for independently checking the expected tick-1 relation.
needed={tick-1+offset for tick in selected for offset in range(-2,3)}
while True:
 raw=p.stdout.read(size)
 if not raw:break
 assert len(raw)==size
 if i in needed:frames[i]=Image.frombytes('RGB',(640,360),raw)
 i+=1
assert p.wait()==0
# Align through in-view exact opaque source pixels, allowing MJPEG colour loss.
folder=WORK/'game/assets/art/characters/olezhka';sheets={k:Image.open(folder/(k+'_sheet.png')).convert('RGBA') for k in ['world','action','finisher']};maps={'world':{'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]},'action':{'hit':[4],'fall':[5,6],'shove':[0,1,2]},'finisher':{'special':[0,7,6]}}
probe=[x for x in d['trace'] if x['segment'].startswith('continuous_run_guard_') and x['animation'].startswith('walk_')][::5][:16];errors={}
for offset in range(-2,3):
 values=[]
 for item in probe:
  idx=item['tick']-1+offset
  if idx not in frames:continue
  state,direction=item['animation'].rsplit('_',1);row=['down','left','right','up'].index(direction);kind=next(k for k,m in maps.items() if state in m);column=maps[kind][state][item['frame']];cell=sheets[kind].crop((column*48,row*64,column*48+48,row*64+64));im=frames[idx];x=round(item['visual_origin'][0])-24;y=round(item['visual_origin'][1])-32
  diff=[]
  for cy in range(64):
   for cx in range(48):
    expected=cell.getpixel((cx,cy))
    if expected[3] and 0<=x+cx<640 and 0<=y+cy<360:
     actual=im.getpixel((x+cx,y+cy));diff.append(sum(abs(actual[c]-expected[c]) for c in range(3))/3)
  values.append(sum(diff)/len(diff))
 errors[offset]=sum(values)/len(values)
offset=min(errors,key=errors.get);assert offset==0,(errors,'Cannot rely on trace/video relation')
for tick in sorted(selected):
 item=trace[tick];im=frames[tick-1];x,y=item['position'];box=(round(x)-60,round(y)-90,round(x)+60,round(y)+15);crop=im.crop(box);name=f'm{tick-1:04}_t{tick:04}.png';crop.save(OUT/name);records.append({'tick':tick,'video_index':tick-1,'segment':item['segment'],'animation':item['animation'],'frame':item['frame'],'action_frame':item['action_frame'],'path':name})
# All UP contact and release ticks, no sampled omission.
for category in ['unarmed','blunt','sharp']:
 c=next(x for x in d['contacts'] if x['segment']==f'finisher_{category}_up' and x['finisher']);ticks=range(c['tick']-1,c['tick']+12);board=Image.new('RGB',(12*240,240),'#202027');dd=ImageDraw.Draw(board)
 for n,tick in enumerate(ticks):
  item=trace[tick];im=frames[tick-1];x,y=item['position'];crop=im.crop((round(x)-60,round(y)-90,round(x)+60,round(y)+15)).resize((240,210),Image.Resampling.NEAREST);board.paste(crop,(n*240,30));dd.text((n*240+3,3),f'{category} t{tick} a{item["action_frame"]} f{item["frame"]}',fill='white')
 board.save(OUT/f'up-{category}-all-hold-release.png')
# Continuous complete pose transitions at root context, sorted time and with source pose labels.
for direction in ['down','left','right','up']:
 segment='continuous_run_guard_'+direction;rows=[x for x in records if x['segment']==segment];board=Image.new('RGB',(12*240,((len(rows)+11)//12)*240),'#202027');dd=ImageDraw.Draw(board)
 for n,item in enumerate(rows):
  im=Image.open(OUT/item['path']).resize((240,210),Image.Resampling.NEAREST);x=n%12*240;y=n//12*240;board.paste(im,(x,y+30));dd.text((x+3,y+3),f't{item["tick"]} {item["animation"]} f{item["frame"]}',fill='white')
 board.save(OUT/f'continuous-{direction}-joins.png')
result={'avi_decoded_frames':i,'command':cmd,'alignment_offset_relative_tick_minus1':offset,'alignment_MAE':errors,'alignment_probes':len(probe),'selected_crops':len(records),'records':records}
(ROOT/'reports/phases/P06/art-preflight/olezhka-combat-native-review-v1r-extraction.json').write_text(json.dumps(result,indent=2)+'\n');print('decoded',i,'selected',len(records),'alignment',errors)
