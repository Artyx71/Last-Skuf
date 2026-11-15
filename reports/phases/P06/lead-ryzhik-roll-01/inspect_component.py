"""Independent read-only numeric/artifact inspection; no engine invocation."""
from pathlib import Path
import json, hashlib, math, collections, ast, copy, subprocess
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[4]
WORK=ROOT/'.autopilot/worktrees/P06'
OUT=Path(__file__).parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda n,d:(OUT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
results={}
dirs={'down':(0,1),'left':(-1,0),'right':(1,0),'up':(0,-1)}
for run,mode in [('headless-04','live'),('native-03','live'),('native-03','movie')]:
 p=WORK/'reports/phases/P06/ryzhik-roll-01'/run/mode/'result.json'
 d=json.loads(p.read_text()); trace=d['trace']; cs=d['contacts']; checks=d['checks']
 assert all(c['passed'] is True for c in checks)
 assert d['phase_approval'] is False and d['actual_input'] is True and d['passed'] is True
 routes={}
 for direction,aim in dirs.items():
  ts=[t for t in trace if t['segment']=='walk_roll_walk_'+direction]
  rs=[t for t in ts if t['action_kind']=='roll']; start=rs[0]['position']; errs=[]; poses=[]
  for t in rs:
   distance=180*max(0,min(t['action_elapsed']-.08,.32))
   expected=[start[i]+aim[i]*distance for i in range(2)]
   errs.append(math.dist(expected,t['position']))
   if not poses or poses[-1]!=t['action_frame']:poses.append(t['action_frame'])
  route_cs=[c for c in cs if c['segment']=='walk_roll_walk_'+direction]
  assert max(errs)<.002 and poses==list(range(8)) and len(route_cs)==1
  c=route_cs[0]; assert c['damage']==0 and c['player_action_frame']==6 and not c['lethal'] and not c['finisher']
  assert .4-1e-9<=c['player_action_elapsed']<.48+1e-9
  assert abs(math.dist(start,rs[-1]['position'])-57.6)<.002
  maxstep=max(math.dist(a['position'],b['position']) for a,b in zip(rs,rs[1:]))
  assert maxstep<3.002
  routes[direction]={'samples':len(rs),'ordered_poses':poses,'max_integral_position_error_px':max(errs),'distance_px':math.dist(start,rs[-1]['position']),'max_tick_step_px':maxstep,'contact_clock':c['player_action_elapsed'],'join_animations':list(dict.fromkeys(t['animation'] for t in ts))}
 incoming=[c for c in cs if c['segment'].startswith('Core_incoming_')]
 assert len(incoming)==6 and all(c['damage']==1 and c['target_is_player'] for c in incoming)
 finish_segments=sorted({c['segment'] for c in cs if c['finisher']})
 assert len(finish_segments)==24
 for seg in finish_segments:
  ss=[c for c in cs if c['segment']==seg];assert len(ss)==2
  assert ss[0]['damage']==0 and not ss[0]['finisher']
  assert ss[1]['damage']==1 and ss[1]['finisher'] and ss[1]['lethal'] and ss[1]['player_frame']==1
  tail=[t for t in trace if t['segment']==seg][-1]
  assert tail['score']==100 and tail['damage_events']==2 and tail['action_kind']==''
 pairs=[c for c in checks if 'Full_Reduced_same_once_health_score' in c['name']]
 assert len(pairs)==12 and all(c['details']['Full']==c['details']['Reduced']==[0,2,100,2,1,0] for c in pairs)
 overlays=d['clothing_overlay'];assert len(overlays)==8 and [o['frame'] for o in overlays]==list(range(8))
 offsets=[math.dist(o['world_anchor'],o['live_decal_at']) for o in overlays]
 assert max(offsets)<=3.2 and all(o['remaining_ttl']>0 for o in overlays)
 assert overlays[2]['clothing_socket']==[23,31] and overlays[5]['clothing_socket']==[23,33]
 assert len([c for c in cs if c['segment']=='persistent_blood_UP_roll'])==1
 # Wall harness keeps setup_right as its trace segment; identify it by the
 # dedicated capture tick when native, otherwise by the first roll after UP.
 cutoff=max(t['tick'] for t in trace if t['segment']=='walk_roll_walk_up')
 wallrows=[]
 for t in trace:
  if t['tick']>cutoff and t['action_kind']=='roll':
   if wallrows and t['tick']!=wallrows[-1]['tick']+1:break
   wallrows.append(t)
 assert wallrows and wallrows[0]['position']==[260,240]
 walldistance=math.dist(wallrows[0]['position'],wallrows[-1]['position'])
 assert 0<walldistance<20 and all(t['damage_events']==0 and t['score']==0 for t in wallrows)
 interruptions={}
 for reason in ['cancel','revoke','reopen','replace','hurt','death']:
  name='interrupt_'+reason;ss=[t for t in trace if t['segment']==name]
  assert ss and ss[-1]['action_kind']!='roll' and ss[-1]['score']==0 and ss[-1]['damage_events']==0
  assert not [c for c in cs if c['segment']==name]
  interruptions[reason]={'samples':len(ss),'no_Core_contacts':True,'last_score':ss[-1]['score'],'last_damage_events':ss[-1]['damage_events']}
 results[run+'/'+mode]={'source_path':str(p.relative_to(WORK)),'sha256':sha(p),'checks':len(checks),'trace_samples':len(trace),'Core_contacts':len(cs),'routes':routes,'wall_stopped_actual_distance_px':walldistance,'interruptions':interruptions,'phase_incoming_contacts':len(incoming),'additional_nonfatal_blood_contact':1,'finisher_cases':len(finish_segments),'Full_Reduced_pairs':len(pairs),'once_outcome_vector':[0,2,100,2,1,0],'clothing_max_offset_px':max(offsets),'blood_overlays':overlays}
write('numeric-proofs.json',results)
# Independently reconstruct all32 native cells from complete master cells.
s=WORK/'assets/source_art/characters/ryzhik'; master=Image.open(s/'roll_master_v2a.png').convert('RGBA'); native=Image.open(s/'roll_native_v2a.png').convert('RGBA')
m=json.loads((s/'roll_manifest_v2a.json').read_text());colors=[tuple(bytes.fromhex(c)) for c in m['packing']['palette_hex']]
pal=Image.new('P',(1,1));pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
oldmaster=Image.open(s/'roll_master_v1.png').convert('RGBA');oldnative=Image.open(s/'roll_native_v1.png').convert('RGBA')
changed_master=[];changed_native=[];cells=[]
for i,f in enumerate(m['frames']):
 box=f['source_rect'];cell=master.crop(box).resize((48,64),Image.Resampling.NEAREST)
 alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
 cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(alpha);cell.paste((0,0,0,0),(0,0),ImageOps.invert(alpha))
 x,y,w,h=f['rect'];native_box=(x,y,x+w,y+h)
 rebuilt=Image.new('RGBA',(48,64));rebuilt.paste(cell,tuple(f['translate_native']));actual=native.crop(native_box)
 assert rebuilt.tobytes()==actual.tobytes() and hashlib.sha256(actual.tobytes()).hexdigest()==f['rgba_sha256']
 assert sum(alpha.get_flattened_data())==sum(actual.getchannel('A').get_flattened_data())
 if master.crop(box).tobytes()!=oldmaster.crop(box).tobytes():changed_master.append(i)
 if actual.tobytes()!=oldnative.crop(native_box).tobytes():changed_native.append(i)
 cells.append({'index':i,'rgba_sha256':f['rgba_sha256'],'bounds':list(actual.getbbox()),'translate_native':f['translate_native']})
assert changed_master==changed_native==[26,29]
assert sha(WORK/'game/assets/art/characters/ryzhik/roll_sheet.png')==sha(s/'roll_native_v2a.png')
old_sockets=json.loads((s/'roll_runtime_v1.sockets.json').read_text());new_sockets=json.loads((WORK/'game/assets/art/characters/ryzhik/roll.sockets.json').read_text())
changed_sockets=[i for i,(a,b) in enumerate(zip(old_sockets['frames'],new_sockets['frames'])) if a!=b]
assert changed_sockets==[26,29]
write('art-transfer-proofs.json',{'master_sha256':sha(s/'roll_master_v2a.png'),'native_sha256':sha(s/'roll_native_v2a.png'),'reconstructed_cells':len(cells),'changed_master_cells':changed_master,'changed_native_cells':changed_native,'changed_socket_entries':changed_sockets,'other30_wholecells_byte_exact':True,'source_pixel_semantics_visual_review_separate':True,'cells':cells})
# Parse only the pure validator AST; never import/run the production runner.
tool=WORK/'tools/verify_p06_ryzhik.py';tree=ast.parse(tool.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='valid_replay');ns={'SCOPE':'RYZHIK_ROLL_COMPONENT_ONLY'};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(tool),'exec'),ns)
valid=ns['valid_replay'];probes=[]
for run,mode in [('headless-04','live'),('native-03','live'),('native-03','movie')]:
 d=json.loads((WORK/'reports/phases/P06/ryzhik-roll-01'/run/mode/'result.json').read_text());headless=run.startswith('headless')
 assert valid(d,headless) and not valid(d,not headless);probes.append({'case':run+'/'+mode,'actual_mode_accepted':True,'opposite_mode_rejected':True})
for renderer in ['', ' ',None,True,1,[],{},'unknown','X11 ',' X11']:
 d=copy.deepcopy(d);d['renderer']=renderer;assert not valid(d,False) and not valid(d,True)
 probes.append({'case':'invalid-renderer:'+repr(renderer),'rejected':True})
write('pure-validator-probes.json',{'pure_AST_only':True,'production_execution':False,'probes':probes})
print(json.dumps({'runs':{k:{q:v[q] for q in ['checks','trace_samples','Core_contacts','finisher_cases','clothing_max_offset_px']} for k,v in results.items()},'reconstructed32':True,'two_changed_cells':changed_native,'pure_probes':len(probes)}))
