from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/tega-environment-01/native-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();n=json.loads((D/'live/result.json').read_text());assert n['passed'] and n['actual_input'] and n['renderer']=='X11';assert len(n['captures'])==128 and all(x['passed'] for x in n['checks']);C={x['name']:x for x in n['captures']};used=[]
def board(names,out,cols=3,scale=1):
 crop=(160,105,420,325);cw,ch=260,220;b=Image.new('RGB',(cw*cols,(ch+20)*math.ceil(len(names)/cols)),(24,29,35));d=ImageDraw.Draw(b)
 for i,name in enumerate(names):
  p=Path(C[name]['path']);im=Image.open(p).convert('RGB');assert im.size==(640,360);x=(i%cols)*cw;y=(i//cols)*(ch+20);b.paste(im.crop(crop),(x,y+20));d.text((x+2,y+2),name.replace('finisher_','FIN_').replace('object_hit_','OBJ_'),fill=(255,220,180));used.append(name)
 b.resize((b.width*scale,b.height*scale),Image.Resampling.NEAREST).save(O/out)
for di in ['down','left','right','up']:
 board(['object_hit_'+mode+'_'+di+'_'+p for mode in ['false','true'] for p in ['world','windup','contact','recovered']],f'native_object_{di}.png',4)
 board(['clothing_'+di+'_'+p for p in ['real_hurt','special0','special1','special2']],f'native_blood_{di}.png',4,2)
 for cat in ['unarmed','blunt','environmental']:
  board(['finisher_'+mode+'_'+cat+'_'+di+'_'+p for mode in ['false','true'] for p in ['windup','contact','corpse']],f'native_FIN_{cat}_{di}.png',3)
board([x for x in C if x.startswith('incoming_')],'native_incoming6.png',3)
for name in ['wall_stops_object','tega_after_restart']:
 Image.open(C[name]['path']).save(O/('native_'+name+'_full.png'));used.append(name)
assert set(used)==set(C)
fin=[x for x in n['contacts'] if x.get('finisher')];assert len(fin)==24 and all(x['player_action_frame']==1 for x in fin)
objecthits=[x for x in n['contacts'] if x['segment'].startswith('object_hit')];assert len(objecthits)==8 and all(x['player_action_frame']==1 for x in objecthits)
metrics={'source_head':'6a0224e016e53e13ddb1e6fde747b66e7f75447b','checks':len(n['checks']),'actual_trace_samples':len(n['trace']),'actual_contacts':len(n['contacts']),'captured_count':len(C),'all_captures_on_diagnostic_boards':True,'visual_inspection_pending':True,'finisher_contacts':fin,'object_contacts':objecthits,'clothing_overlay':n['clothing_overlay'],'bindings':{str(p.relative_to(W)):sha(p) for p in [D/'live/result.json']+[Path(c['path']) for c in C.values()]},'phase_approval':False}
(O/'native_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('128 actual captures mapped; runtime visual inspection pending')
