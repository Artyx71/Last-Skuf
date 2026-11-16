from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01';D=O/'edges';D.mkdir(exist_ok=True);rec=[]
def crop(cap,trace,base):
 p=Path(cap['path']);im=Image.open(p).convert('RGB').resize((640,360),Image.Resampling.NEAREST);t=min(trace,key=lambda x:abs(x['tick']-cap['tick']));x,y=t['position'];box=(round(x)-64,round(y)-86,round(x)+64,round(y)+20);rec.append({'capture':str(p.relative_to(W)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'capture_tick':cap['tick'],'nearest_trace_tick':t['tick'],'box':box});return im.crop(box).resize((256,212),Image.Resampling.NEAREST)
p=W/'reports/phases/P06/pasha-input-diagnostic-01/native';r=json.loads((p/'live/result.json').read_text());dirs=['down','left','right','up'];cats=['unarmed','blunt','sharp','firearm','environmental']
for mode in ['false','true']:
 b=Image.new('RGB',(1280,4*236+30),(21,25,32));d=ImageDraw.Draw(b);d.text((3,6),'FRESH PASHA all5 FIN contact / reduced='+mode,fill='white')
 for row,di in enumerate(dirs):
  for col,cat in enumerate(cats):
   cap=next(x for x in r['captures'] if x['name']=='finisher_'+mode+'_'+cat+'_'+di+'_contact');im=crop(cap,r['trace'],p);xx=col*256;yy=30+row*236;b.paste(im,(xx,yy));d.text((xx+3,yy+214),di+' '+cat,fill='white')
 b.save(D/('pasha-FIN-reduced-'+mode+'.png'))
b=Image.new('RGB',(8*200,4*192+30),(21,25,32));d=ImageDraw.Draw(b);d.text((3,6),'FRESH PASHA clothing/moving-shot real blood poses 0..7',fill='white')
for row,di in enumerate(dirs):
 for col in range(8):
  cap=next(x for x in r['captures'] if x['name']=='clothing_'+di+'_pose'+str(col));im=crop(cap,r['trace'],p).resize((200,166),Image.Resampling.NEAREST);xx=col*200;yy=30+row*192;b.paste(im,(xx,yy));d.text((xx+3,yy+169),di+' pose'+str(col),fill='white')
b.save(D/'pasha-clothing32.png')
p=W/'reports/phases/P06/full-native-current-source-01/timka_prime';r=json.loads((p/'live/result.json').read_text());b=Image.new('RGB',(6*256,4*236+30),(21,25,32));d=ImageDraw.Draw(b);d.text((3,6),'FRESH TIMKA present/prime stance and actual drawn strides',fill='white')
for row,di in enumerate(dirs):
 labels=['present_locomotion_'+di+'_stance0','prime_locomotion_'+di+'_stance0','present_locomotion_'+di+'_walk_frame0','prime_locomotion_'+di+'_walk_frame0','present_locomotion_'+di+'_walk_frame1','prime_locomotion_'+di+'_walk_frame1']
 for col,label in enumerate(labels):
  cap=next(x for x in r['captures'] if x['name']==label);im=crop(cap,r['trace'],p);xx=col*256;yy=30+row*236;b.paste(im,(xx,yy));d.text((xx+3,yy+214),('PRESENT' if 'present' in label else 'PRIME')+' '+di+(' stance' if 'stance' in label else ' walk'+label[-1]),fill='white')
b.save(D/'timka-contexts.png')
(O/'edge-inspection.json').write_text(json.dumps({'actual_capture_samples':rec,'not_claimed':'No new gameplay runs. Not all628 body cells displayed under blood; all source anchors bound and accepted component overlays reused by exact bytes.'},ensure_ascii=False,indent=2)+'\n');print({'captures':len(rec)})
