from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,math
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/pasha-moving-shot-01/native-01';A=W/'game/assets/art/characters/pasha';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rgba=lambda im:hashlib.sha256(im.tobytes()).hexdigest();v=json.loads((D/'validation.json').read_text());assert sha(D/'validation.json')=='83b917e0fb52bc07e43bfcf23a95dbdc5a2b45d4c2ad6058b27ac7c550f419c4';assert v['passed'] and v['source_unchanged'] and v['source_head']=='fb5ca9bdf0e82e315c08197877e1f39a2a6c4091'
for p,h in json.loads((D/'source_hashes.json').read_text()).items():assert sha(W/p)==h,p
for e in v['artifacts']:assert sha(W/e['path'])==e['sha256'],e['path']
n=json.loads((D/'live/result.json').read_text());m=json.loads((D/'movie/result.json').read_text());assert n['passed'] and m['passed'] and n['renderer']==m['renderer']=='X11';assert len(n['checks'])==573 and len(m['checks'])==385;assert len(n['captures'])==188 and len(n['contacts'])==len(m['contacts'])==104
for result in [n,m]:assert all(c['passed'] for c in result['checks'])
prop=json.loads((R/'reports/phases/P06/art-preflight/pasha_annotation_preflight_01_proposals.json').read_text());adopt=json.loads((W/'reports/phases/P06/pasha-moving-shot-01/annotation-adoption.json').read_text());assert adopt['source_proposal_sha256']=='cf45be352ec9c842ba2f4e8ba42e5a315bbe7f271eb2f37a63f50ef4b9957e37';sourcereview={}
for kind,payload in prop['clothing_proposals'].items():
 image=Image.open(A/(kind+'_sheet.png')).convert('RGBA');s=json.loads((A/(kind+'.sockets.json')).read_text());assert sha(A/(kind+'_sheet.png'))==payload['sheet_sha256']==s['sheet_sha256'];assert sha(A/(kind+'.sockets.json'))==adopt['kinds'][kind]['after_sha256'];rows=[]
 for f in s['frames']:
  i=f['index'];r,c=divmod(i,8);cell=image.crop((c*48,r*64,(c+1)*48,(r+1)*64));ref=payload['frames'][i];assert f['clothing']==ref['proposed_clothing'];assert rgba(cell)==ref['source_frame_rgba_sha256']==f['source_frame_rgba_sha256'];assert list(cell.getpixel(tuple(f['clothing'])))==ref['proposed_pixel_RGBA'];rows.append({'index':i,'clothing':f['clothing'],'RGBA':ref['proposed_pixel_RGBA'],'frame_hash_exact':True})
 sourcereview[kind]=rows
muzzle=json.loads((A/'moving_shot.muzzles.json').read_text());assert {e['direction']:e['muzzle'] for e in muzzle['frames']}=={di:p['native_xy'] for di,p in prop['muzzle_proposals'].items()}
C={c['name']:c for c in n['captures']};used=set();crop=(190,90,470,320)
def board(names,out,cols=3,scale=1):
 cw,ch=280,230;b=Image.new('RGB',(cw*cols,(ch+20)*math.ceil(len(names)/cols)),(23,28,34));d=ImageDraw.Draw(b)
 for i,name in enumerate(names):
  p=Path(C[name]['path']);im=Image.open(p).convert('RGB');assert im.size==(640,360);x=i%cols*cw;y=i//cols*(ch+20);b.paste(im.crop(crop),(x,y+20));d.text((x+1,y+2),name.replace('moving_shot_','SHOT_').replace('finisher_','FIN_'),fill=(240,220,190));used.add(name)
 b.resize((b.width*scale,b.height*scale),Image.Resampling.NEAREST).save(O/out)
for di in ['down','left','right','up']:
 board(['moving_shot_'+mode+'_'+di+'_'+p for mode in ['false','true'] for p in ['windup','launch','recovered']],'native_moving_shot_'+di+'.png')
 board(['clothing_'+di+'_hurt']+['clothing_'+di+'_pose'+str(p) for p in range(8)],'native_actual_blood_'+di+'_all8.png',3,2)
 for cat in ['unarmed','blunt','sharp','firearm','environmental']:
  board(['finisher_'+mode+'_'+cat+'_'+di+'_'+p for mode in ['false','true'] for p in ['windup','contact','corpse']],'native_FIN_'+cat+'_'+di+'.png')
others=[name for name in C if name not in used]
for name in others:Image.open(C[name]['path']).save(O/('native_'+name+'_wholeviewport.png'));used.add(name)
assert used==set(C)
for result in [n,m]:
 fin=[c for c in result['contacts'] if c.get('finisher')];matrix=[c for c in fin if c['segment'].startswith('finisher_')];assert len(fin)==41 and len(matrix)==40 and all(c['player_frame']==1 for c in matrix);assert len(result['clothing_overlay'])==32;assert all(x['actual']==x['expected'] for x in result['clothing_overlay']);assert len(result['launches'])==8 and all(x['source_pose']==3 for x in result['launches'])
metrics={'schema':1,'source_head':v['source_head'],'native_checks':573,'movie_checks':385,'trace_samples_per_run':len(n['trace']),'actual_contacts_per_run':104,'FIN_matrix_contacts_per_run':40,'additional_shared_clip_FIN_contact':1,'actual_clothing_overlay_points_per_run':32,'all128_adopted_source_annotations_exact_proposals':sourcereview,'all4_adopted_muzzles_exact_proposals':muzzle['frames'],'actual_native_captures':C,'actual_native_captures_count':188,'all188_mapped_to_boards_or_wholeviewport':True,'native_clothing_overlay':n['clothing_overlay'],'native_launches':n['launches'],'source_and_artifact_hashes_verified':True,'visual_inspection_pending':True,'phase_approval':False};(O/'native_metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print('188 actual PNG mapped;128adopted anchors +fourmuzzles verified; actual full visual inspection pending')
