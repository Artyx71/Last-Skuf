from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=ROOT/'reports/phases/P06/art-preflight/olezhka-combat-native-review-v1r-diagnostics';BASE=WORK/'reports/phases/P06/attempt1/olezhka-combat-native-01';d=json.loads((BASE/'movie/result.json').read_text());trace={x['tick']:x for x in d['trace']}
for family in ['counter','finisher_unarmed','finisher_blunt','finisher_sharp']:
 board=Image.new('RGB',(15*160,4*160),'#202027');draw=ImageDraw.Draw(board)
 for row,direction in enumerate(['down','left','right','up']):
  segment=family+'_'+direction;c=next(x for x in d['contacts'] if x['segment']==segment and not x['target_is_player'] and (x['finisher']==family.startswith('finisher_')))
  for col,tick in enumerate(range(c['tick']-2,c['tick']+13)):
   im=Image.open(OUT/f'm{tick-1:04}_t{tick:04}.png').resize((160,140),Image.Resampling.NEAREST);x=col*160;y=row*160;board.paste(im,(x,y+20));item=trace[tick];draw.text((x+2,y+2),f'{direction} t{tick} a{item["action_frame"]}',fill='white')
 board.save(OUT/(family+'-all-contact-release.png'))
selected={x['tick'] for x in d['trace'] if x['segment'].startswith('reactions_')};cmd=['ffmpeg','-v','error','-i',str(WORK/'build/P06/attempt1/olezhka-combat-native-01/olezhka.avi'),'-vf','scale=640:360:flags=neighbor','-f','rawvideo','-pix_fmt','rgb24','-'];p=subprocess.Popen(cmd,stdout=subprocess.PIPE);size=640*360*3;i=0;frames={}
while True:
 data=p.stdout.read(size)
 if not data:break
 if i+1 in selected:
  t=trace[i+1];x,y=t['position'];im=Image.frombytes('RGB',(640,360),data).crop((round(x)-60,round(y)-90,round(x)+60,round(y)+15));im.save(OUT/f'reaction_m{i:04}_t{i+1:04}.png');frames[i+1]=im
 i+=1
assert p.wait()==0
for direction in ['down','left','right','up']:
 entries=[x for x in d['trace'] if x['segment']=='reactions_'+direction];board=Image.new('RGB',(14*160,((len(entries)+13)//14)*160),'#202027');draw=ImageDraw.Draw(board)
 for n,item in enumerate(entries):
  x=n%14*160;y=n//14*160;board.paste(frames[item['tick']].resize((160,140),Image.Resampling.NEAREST),(x,y+20));draw.text((x+2,y+2),f't{item["tick"]} {item["animation"]} f{item["frame"]}',fill='white')
 board.save(OUT/f'reactions-{direction}-all.png')
print('All contact/release panels and',len(selected),'decoded reaction frames saved')
