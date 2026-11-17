"""Independent raw numeric/atlas inspection; no Godot invocation."""
from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,math,ast,copy
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda n,d:(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
paths=[R/'reports/phases/P06/qa-pasha-moving-shot-03/Pasha/result.json',W/'reports/phases/P06/pasha-moving-shot-01/native-03/live/result.json',W/'reports/phases/P06/pasha-moving-shot-01/native-03/movie/result.json']
proofs=[]
muzzle_map={e['direction']:e['muzzle'] for e in json.loads((W/'game/assets/art/characters/pasha/moving_shot.muzzles.json').read_text())['frames']}
for p in paths:
 d=json.loads(p.read_text());ts=d['trace'];ats=d['ammo_trace'];cs=d['contacts'];assert d['phase_approval'] is False and d['actual_input'] is True and all(c['passed'] is True for c in d['checks'])
 assert len(cs)==len({(c['epoch'],c['id'],c['target']) for c in cs})==105
 routes={}
 for mode in ['false','true']:
  for direction in ['down','left','right','up']:
   seg='moving_shot_'+mode+'_'+direction;rows=[t for t in ts if t['segment']==seg];action=[t for t in rows if t['action_kind']=='moving_shot'];poses=list(dict.fromkeys(t['action_frame'] for t in action));assert poses==list(range(8))
   maxstep=max(math.dist(a['position'],b['position'])/(b['tick']-a['tick']) for a,b in zip(rows,rows[1:]) if b['tick']>a['tick']);assert maxstep<=3.01
   launches=[x for x in d['launches'] if x['segment']==seg];costs=[x for x in d['costs'] if x['segment']==seg];hits=[c for c in cs if c['segment']==seg]
   assert len(launches)==len(costs)==len(hits)==1
   l,c=launches[0],costs[0];assert l['tick']==c['tick'] and l['source_pose']==c['pose']==3 and l['epoch']==c['epoch'] and l['job_id']==c['id'] and c['ammo']==3
   h=hits[0];assert h['damage']==1 and not h['finisher'] and h['lethal']
   launchrow=next(t for t in action if t['tick']==l['tick']);assert launchrow['action_frame']==3 and abs(launchrow['action_elapsed']-.116666666666667)<1e-8
   expected_muzzle=[launchrow['visual_origin'][i]-[24,32][i]+muzzle_map[direction][i] for i in range(2)]
   assert math.dist(expected_muzzle,l['muzzle'])<.001
   assert rows[-1]['animation']=='run_'+direction and rows[-1]['score']==0 and rows[-1]['damage_events']==1
   routes[seg]={'ordered_poses':poses,'max_px_per_tick':maxstep,'launch_clock':launchrow['action_elapsed'],'launch_cost_same_tick':l['tick'],'bullet_impact_source_pose':h['player_action_frame'],'bullet_impact_clock':h['player_action_elapsed'],'visual_muzzle':l['muzzle'],'one_cost':True}
 for a in ats:
  hud=a['hud'];assert hud['ammo']==a['ammo'] and abs(hud['cooldown']-a['cooldown'])<1e-8 and abs(hud['refill']-a['refill']/.9)<1e-8 and hud['clip']==4
 clip=[a for a in ats if a['segment']=='finite_clip_and_refill'];mins=min(a['ammo'] for a in clip);assert mins==0 and max(a['ammo'] for a in clip)==4 and clip[-1]['ammo']==4
 drops=[(a['ammo'],b['ammo']) for a,b in zip(clip,clip[1:]) if b['ammo']<a['ammo']];assert drops==[(4,3),(3,2),(2,1),(1,0)]
 fs=sorted({c['segment'] for c in cs if c['segment'].startswith('finisher_') and c['finisher']});assert len(fs)==40
 outcomes={}
 for seg in fs:
  hits=[c for c in cs if c['segment']==seg];assert len(hits)==2 and hits[0]['damage']==0 and not hits[0]['finisher'] and hits[1]['finisher'] and hits[1]['damage']==1 and hits[1]['lethal'] and hits[1]['player_frame']==1
  last=[t for t in ts if t['segment']==seg][-1];assert last['damage_events']==2 and last['score']==100
  ammo=min(a['ammo'] for a in ats if a['segment']==seg);expected=3 if '_firearm_' in seg else 4;assert ammo==expected
  mode,category,direction=seg.removeprefix('finisher_').split('_');outcomes[(mode,category,direction)]=[hits[1]['damage'],hits[1]['category'],last['damage_events'],last['score'],ammo]
 for cat in ['unarmed','blunt','sharp','firearm','environmental']:
  for dr in ['down','left','right','up']:assert outcomes[('false',cat,dr)]==outcomes[('true',cat,dr)]
 mixed=[a for a in ats if a['segment']=='shared_clip_shot_then_firearm_finisher'];assert min(a['ammo'] for a in mixed)==2
 mixed_hits=[c for c in cs if c['segment']=='shared_clip_shot_then_firearm_finisher'];assert len(mixed_hits)==2 and mixed_hits[-1]['finisher'] and mixed_hits[-1]['damage']==1
 blood=d['clothing_overlay'];assert len(blood)==32 and {(b['direction'],b['pose']) for b in blood}=={(dr,f) for dr in ['down','left','right','up'] for f in range(8)};assert all(math.dist(b['actual'],b['expected'])<.001 for b in blood)
 for mode in ['false','true']:
  incoming=[c for c in cs if c['segment']=='incoming_before_launch_'+mode];assert len(incoming)==1 and incoming[0]['target_is_player']
 proofs.append({'path':str(p.relative_to(R)),'result_sha256':sha(p),'checks':len(d['checks']),'actor_samples':len(ts),'ammo_HUD_samples_exact':len(ats),'unique_Core_contacts':len(cs),'primary_routes':routes,'finite_clip_drops':drops,'matrix_FIN_cases':40,'Full_Reduced_pairs':20,'additional_shared_clip_FIN':1,'shared_clip_min_ammo':2,'blood_poses_exact':32})
write('numeric-proofs.json',proofs)
folder=W/'game/assets/art/characters/pasha';sheets={};clips=0
for kind in ['world','action','finisher','moving_shot']:
 m=json.loads((folder/(kind+'.json')).read_text());s=json.loads((folder/(kind+'.sockets.json')).read_text());im=Image.open(W/m['master']).convert('RGBA');native=Image.open(folder/(kind+'_sheet.png')).convert('RGBA');assert sha(W/m['master'])==m['master_sha256'] and sha(folder/(kind+'_sheet.png'))==m['sha256']==s['sheet_sha256']
 colors=[tuple(bytes.fromhex(c)) for c in m['packing']['palette_hex']];pal=Image.new('P',(1,1));pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)));cells=[]
 for i,f in enumerate(m['frames']):
  cell=im.crop(f['source_rect']).resize((48,64),Image.Resampling.NEAREST);a=cell.getchannel('A').point(lambda v:255 if v>=m['packing']['alpha_threshold'] else 0);cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(a);cell.paste((0,0,0,0),(0,0),ImageOps.invert(a));rebuilt=Image.new('RGBA',(48,64));rebuilt.paste(cell,tuple(f['translate_native']));x,y,w,h=f['rect'];actual=native.crop((x,y,x+w,y+h));digest=hashlib.sha256(actual.tobytes()).hexdigest();assert actual.tobytes()==rebuilt.tobytes() and digest==f['rgba_sha256']==s['frames'][i]['source_frame_rgba_sha256'];sx,sy=s['frames'][i]['clothing'];assert actual.getpixel((sx,sy))[3]==255;cells.append({'index':i,'rgba_sha256':digest,'clothing':s['frames'][i]['clothing']})
 sheets[kind]={'sheet_sha256':m['sha256'],'master_sha256':m['master_sha256'],'cells':cells};clips+=len(m['animations_source_columns'])*4
assert clips==60
muzzles=json.loads((folder/'moving_shot.muzzles.json').read_text());assert muzzles['sheet_sha256']==sheets['moving_shot']['sheet_sha256'];im=Image.open(folder/'moving_shot_sheet.png').convert('RGBA')
for row,e in enumerate(muzzles['frames']):x,y=e['muzzle'];assert e['column']==3 and im.getpixel((3*48+x,row*64+y))[3]==255
write('atlas-proofs.json',{'complete_cells_reconstructed':128,'exact_opaque_hashbound_garment_anchors':128,'clips':clips,'sheets':sheets,'muzzle_four':muzzles,'semantic_art_acceptance_separately_visual':True})
print(json.dumps({'runs':[{k:v for k,v in p.items() if k not in ['primary_routes','result_sha256']} for p in proofs],'atlas128':True,'clips60':True}))
