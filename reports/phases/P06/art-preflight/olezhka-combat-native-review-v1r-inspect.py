from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,subprocess
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06'
OUT=ROOT/'reports/phases/P06/art-preflight/olezhka-combat-native-review-v1r-diagnostics';assert not OUT.exists();OUT.mkdir()
BASE=WORK/'reports/phases/P06/attempt1/olezhka-combat-native-01';live=json.loads((BASE/'live/result.json').read_text());movie=json.loads((BASE/'movie/result.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((BASE/'source_hashes.json').read_text());source_bad=[p for p,h in source.items() if not (WORK/p).is_file() or sha(WORK/p)!=h]
validation=json.loads((BASE/'validation.json').read_text());art_bad=[x['path'] for x in validation['artifacts'] if not (WORK/x['path']).is_file() or sha(WORK/x['path'])!=x['sha256']]
print('source',len(source),'bad',source_bad,'artifacts',len(validation['artifacts']),'bad',art_bad)
trace={x['tick']:x for x in live['trace']}
for page in range(5):
 captures=live['captures'][page*20:(page+1)*20]
 if not captures:break
 board=Image.new('RGB',(1200,960),'#202027');d=ImageDraw.Draw(board)
 for j,c in enumerate(captures):
  item=trace.get(c['tick'])
  if item is None:
   item=min(live['trace'],key=lambda x:abs(x['tick']-c['tick']))
  x,y=item['position'];im=Image.open(BASE/'live'/Path(c['path']).name).convert('RGB')
  box=(round(x)-60,round(y)-90,round(x)+60,round(y)+15)
  crop=im.crop(box).resize((240,210),Image.Resampling.NEAREST);ox=j%5*240;oy=j//5*240
  board.paste(crop,(ox,oy+30));d.text((ox+3,oy+2),c['name'],fill='white');d.text((ox+3,oy+14),f"tick{c['tick']} {c['animation']} f{c['frame']}",fill='#9ddccc')
 board.save(OUT/f'live-all-{page+1:02}.png')
for kind in ['world','action','finisher']:
 folder=WORK/'game/assets/art/characters/olezhka';im=Image.open(folder/(kind+'_sheet.png')).convert('RGBA');s=json.loads((folder/(kind+'.sockets.json')).read_text());board=Image.new('RGB',(1536,512));d=ImageDraw.Draw(board)
 for idx in range(32):
  r,c=divmod(idx,8);cell=im.crop((c*48,r*64,c*48+48,r*64+64))
  for bg in range(2):
   block=Image.new('RGBA',(48,64),(225,225,225,255) if bg else (24,29,33,255));block.alpha_composite(cell)
   px,py=s['frames'][idx]['clothing'];dd=ImageDraw.Draw(block);dd.line((px-1,py,px+1,py),fill='#00ffff');dd.line((px,py-1,px,py+1),fill='#00ffff')
   board.paste(block.resize((96,128),Image.Resampling.NEAREST).convert('RGB'),((c+bg*8)*96,r*128))
 board.save(OUT/f'{kind}-96-socket-context.png')
metrics={'source_entries':len(source),'source_mismatches':source_bad,'validation_artifacts':len(validation['artifacts']),'artifact_mismatches':art_bad,'live_captures':len(live['captures']),'live_trace':len(live['trace']),'movie_trace':len(movie['trace']),'contacts':len(live['contacts']),'defenses':len(live['defenses']),'diagnostics':{p.name:sha(p) for p in sorted(OUT.glob('*.png'))}}
(ROOT/'reports/phases/P06/art-preflight/olezhka-combat-native-review-v1r-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
