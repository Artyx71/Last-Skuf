from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess,math,collections
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';BASE=WORK/'reports/phases/P06/attempt1/tega-world-native-01';OUT=ROOT/'reports/phases/P06/art-preflight';PFX='tega-world-native-review-v1';D=OUT/(PFX+'-diagnostics');movie=json.loads((BASE/'movie/result.json').read_text());trace=movie['trace'];bytick={x['physics_tick']:x for x in trace};atlas=Image.open(WORK/'game/assets/art/characters/tega/world_sheet.png').convert('RGBA');states={'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]};directions=['down','left','right','up'];cells={}
for direction in directions:
 row=directions.index(direction)
 for state,cols in states.items():
  for frame,col in enumerate(cols):
   cell=atlas.crop((col*48,row*64,col*48+48,row*64+64));cells[(state+'_'+direction,frame)]=[(x,y,cell.getpixel((x,y))[:3]) for y in range(64) for x in range(48) if cell.getpixel((x,y))[3]]
probes=trace[::32][:21];wanted={p['physics_tick']-1+offset for p in probes for offset in range(-3,4)};fullprobes={};crops={};frame_records=[];counts=collections.Counter();classifier=[];command=['ffmpeg','-v','error','-i',str(WORK/'build/P06/attempt1/tega-world-native-01/world.avi'),'-vf','scale=640:360:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-'];proc=subprocess.Popen(command,stdout=subprocess.PIPE);index=0;size=640*360*3
while True:
 raw=proc.stdout.read(size)
 if not raw:break
 assert len(raw)==size
 im=Image.frombytes('RGB',(640,360),raw)
 if index in wanted:fullprobes[index]=im
 tick=index+1;item=bytick.get(tick);nearest=item or min(trace,key=lambda p:abs(p['physics_tick']-tick));x,y=nearest['position'];crop=im.crop((round(x)-48,round(y)-75,round(x)+48,round(y)+25));crops[tick]=crop
 if item:
  ox=round(item['visual_origin'][0])-24;oy=round(item['visual_origin'][1])-32;state,direction=item['animation'].rsplit('_',1);scores={}
  for phase in range(len(states[state])):
   values=[sum(abs(im.getpixel((ox+x,oy+y))[c]-rgb[c]) for c in range(3))/3 for x,y,rgb in cells[(item['animation'],phase)]];scores[phase]=sum(values)/len(values)
  best=min(scores,key=scores.get);classifier.append({'tick':tick,'expected':item['frame'],'best':best,'animation':item['animation'],'scores':scores});counts['matched_best']+=best==item['frame']
 frame_records.append({'video_index':index,'physics_tick_assuming_alignment':tick,'actual_trace_sample':item is not None,'rgb640x360_sha256':hashlib.sha256(raw).hexdigest()});index+=1
assert proc.wait()==0
errors={}
for offset in range(-3,4):
 scores=[]
 for item in probes:
  im=fullprobes[item['physics_tick']-1+offset];ox=round(item['visual_origin'][0])-24;oy=round(item['visual_origin'][1])-32;pixels=cells[(item['animation'],item['frame'])];scores.append(sum(sum(abs(im.getpixel((ox+x,oy+y))[c]-rgb[c]) for c in range(3))/3 for x,y,rgb in pixels)/len(pixels))
 errors[offset]=sum(scores)/len(scores)
offset=min(errors,key=errors.get);assert offset==0,errors
# Chronological phase onsets from actual traced frames, grouped by sequence/state.
groups=[]
for item in trace:
 key=(item['sequence'],item['animation'])
 if not groups or groups[-1]['key']!=key:groups.append({'key':key,'entries':[]})
 groups[-1]['entries'].append(item)
onset_records=[]
for i,g in enumerate(groups):
 entries=[];last=None
 for item in g['entries']:
  if item['frame']!=last:entries.append(item);last=item['frame']
 board=Image.new('RGB',(max(1,len(entries))*192,250),'#202027');draw=ImageDraw.Draw(board)
 for j,item in enumerate(entries):
  tick=item['physics_tick'];board.paste(crops[tick].resize((192,200),Image.Resampling.NEAREST),(j*192,40));draw.text((j*192+3,4),f'{g["key"][0]} {item["animation"]}',fill='white');draw.text((j*192+3,18),f't{tick} f{item["frame"]}',fill='#8fd4be');onset_records.append({'group':g['key'],'tick':tick,'frame':item['frame']})
 board.save(D/f'group-{i+1:02}-{g["key"][0]}-{g["key"][1]}.png')
# Uninterrupted joins include every neighbouring actual video frame; stars mark untraced gaps.
continuous=trace[movie['continuous_trace_start']:];joins=[]
for a,b in zip(continuous,continuous[1:]):
 if a['animation']!=b['animation']:
  ticks=list(range(a['physics_tick']-3,b['physics_tick']+4));board=Image.new('RGB',(len(ticks)*192,250),'#202027');draw=ImageDraw.Draw(board)
  for j,tick in enumerate(ticks):
   item=bytick.get(tick);board.paste(crops[tick].resize((192,200),Image.Resampling.NEAREST),(j*192,40));draw.text((j*192+3,4),f't{tick}'+(' *' if item is None else ''),fill='white');draw.text((j*192+3,18),item['animation'] if item else 'nearest root crop only',fill='#8fd4be')
  name=f'join-{len(joins)+1:02}-{a["animation"]}-to-{b["animation"]}.png';board.save(D/name);joins.append({'from':a['animation'],'to':b['animation'],'last_tick':a['physics_tick'],'first_tick':b['physics_tick'],'decoded_ticks':ticks,'diagnostic':name})
# Explicit repeated side run cycles and unaltered DOWN/UP stride projection.
for direction in directions:
 entries=[p for p in trace if p['sequence']=='grid' and p['animation']=='run_'+direction][:20];board=Image.new('RGB',(10*192,2*250),'#202027');draw=ImageDraw.Draw(board)
 for j,item in enumerate(entries):
  x=j%10*192;y=j//10*250;board.paste(crops[item['physics_tick']].resize((192,200),Image.Resampling.NEAREST),(x,y+40));draw.text((x+3,y+4),f'{direction} t{item["physics_tick"]} f{item["frame"]}',fill='white')
 board.save(D/f'{direction}-run20-consecutive.png')
res={'decoded_AVI_frames':index,'decode_command':command,'canonical_size':[640,360],'alignment_offset_relative_tick_minus1':offset,'alignment_probe_count':len(probes),'alignment_MAE':errors,'actual_trace_samples_classified':len(classifier),'expected_phase_best_matches':counts['matched_best'],'classifier_mismatches':[x for x in classifier if x['best']!=x['expected']],'all_classification':classifier,'frame_inventory':frame_records,'phase_onsets':onset_records,'joins':joins,'decode_audio':False}
(OUT/(PFX+'-extraction.json')).write_text(json.dumps(res,indent=2)+'\n');print(json.dumps({'decoded':index,'alignment':errors,'classified':len(classifier),'best_matches':counts['matched_best'],'mismatches':len(res['classifier_mismatches']),'groups':len(groups),'onsets':len(onset_records),'joins':len(joins)}))
