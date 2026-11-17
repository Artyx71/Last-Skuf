"""Read-only Lead numeric and pixel reconstruction checks, no engine invocation."""
from pathlib import Path
from PIL import Image,ImageOps
import json,hashlib,math,collections,ast,copy
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
write=lambda n,d:(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
results={}
for run,mode in [('headless-04','live'),('native-01','live'),('native-01','movie')]:
 p=W/'reports/phases/P06/tega-environment-01'/run/mode/'result.json';d=json.loads(p.read_text());ts=d['trace'];cs=d['contacts'];ot={x['tick']:x for x in d['object_trace']}
 assert all(c['passed'] is True for c in d['checks']) and d['phase_approval'] is False and d['actual_input'] is True
 routes={}
 for reduced in ['false','true']:
  for direction in ['down','left','right','up']:
   seg='object_hit_'+reduced+'_'+direction;rs=[t for t in ts if t['segment']==seg and t['action_kind']=='special'];ss=[c for c in cs if c['segment']==seg]
   assert len(ss)==1 and ss[0]['damage']==1 and ss[0]['lethal'] and ss[0]['player_action_frame']==1 and not ss[0]['finisher']
   poses=list(dict.fromkeys(t['action_frame'] for t in rs));assert poses==[0,1,2]
   start=rs[0]['position'];object_start=ot[rs[0]['tick']]['object'];relative=[object_start[i]-start[i] for i in range(2)]
   errs=[math.dist([ot[t['tick']]['object'][i]-t['position'][i] for i in range(2)],relative) for t in rs if t['tick'] in ot]
   steps=[math.dist(a['position'],b['position']) for a,b in zip(rs,rs[1:])];distance=math.dist(start,rs[-1]['position']);object_distance=math.dist(object_start,ot[rs[-1]['tick']]['object'])
   assert max(errs)<.02 and 3<distance<=37.81 and abs(distance-object_distance)<.02 and max(steps)<=3.501
   assert .18-1e-9<=ss[0]['player_action_elapsed']<.36+1e-9
   assert all(ot[t['tick']]['mask']==6 for t in rs if t['tick'] in ot)
   segment_rows=[t for t in ts if t['segment']==seg]
   # Harness keeps the same segment through its explicit R/reset at the end.
   assert max(t['damage_events'] for t in segment_rows)==1 and all(t['score']==0 for t in segment_rows)
   routes[seg]={'ordered_phases':poses,'actor_distance':distance,'object_distance':object_distance,'max_relative_offset_error':max(errs),'max_tick_displacement':max(steps),'contact_clock':ss[0]['player_action_elapsed'],'contact_pose':ss[0]['player_action_frame']}
 for direction in ['down','left','right','up']:
  a,b=[routes['object_hit_'+mode+'_'+direction] for mode in ['false','true']]
  assert abs(a['actor_distance']-b['actor_distance'])<.001
 fs=sorted({c['segment'] for c in cs if c['finisher']});assert len(fs)==24
 for seg in fs:
  ss=[c for c in cs if c['segment']==seg];assert len(ss)==2 and ss[0]['damage']==0 and not ss[0]['finisher'] and ss[1]['damage']==1 and ss[1]['finisher'] and ss[1]['lethal'] and ss[1]['player_frame']==1
  end=[t for t in ts if t['segment']==seg][-1];assert end['score']==100 and end['damage_events']==2
 pairchecks=[c for c in d['checks'] if c['name'].startswith('finisher_true_') and c['name'].endswith(':Full_Reduced_identical')];assert len(pairchecks)==12
 incoming=[c for c in cs if c['segment'].startswith('incoming_')];assert len(incoming)==6 and all(c['damage']==1 and c['target_is_player'] for c in incoming)
 blood=d['clothing_overlay'];assert len(blood)==12 and {(x['direction'],x['pose']) for x in blood}=={(dr,pose) for dr in ['down','left','right','up'] for pose in range(3)}
 offsets=[math.dist(b['actual'],b['expected']) for b in blood];assert max(offsets)<=3.1 and all(b['ttl']>0 for b in blood)
 denial_segs=sorted({t['segment'] for t in ts if t['segment'].startswith(('deny_','interrupt_','foot_callback_','active_interrupt_'))})
 for seg in denial_segs:assert not [c for c in cs if c['segment']==seg]
 assert len([c for c in cs if c['segment'].startswith('clothing_')])==4
 results[run+'/'+mode]={'result_sha256':sha(p),'checks':len(d['checks']),'trace_samples':len(ts),'object_samples':len(d['object_trace']),'Core_contacts':len(cs),'routes':routes,'FIN_cases':len(fs),'Full_Reduced_FIN_pairs':len(pairchecks),'incoming_six':len(incoming),'additional_real_blood_hits':4,'blood_poses':12,'blood_max_follow_offset':max(offsets),'denial_segments_without_Core_contacts':denial_segs}
write('numeric-proofs.json',results)
atlas=W/'game/assets/art/characters/tega';rows={};clips=0
for kind in ['world','action','finisher']:
 m=json.loads((atlas/(kind+'.json')).read_text());s=json.loads((atlas/(kind+'.sockets.json')).read_text());master=Image.open(W/m['master']).convert('RGBA');native=Image.open(atlas/(kind+'_sheet.png')).convert('RGBA')
 assert sha(W/m['master'])==m['master_sha256'] and sha(atlas/(kind+'_sheet.png'))==m['sha256']==s['sheet_sha256']
 colors=[tuple(bytes.fromhex(c)) for c in m['packing']['palette_hex']];pal=Image.new('P',(1,1));pal.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
 cells=[]
 for i,f in enumerate(m['frames']):
  cell=master.crop(f['source_rect']).resize((48,64),Image.Resampling.NEAREST);a=cell.getchannel('A').point(lambda value:255 if value>=m['packing']['alpha_threshold'] else 0)
  cell=cell.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');cell.putalpha(a);cell.paste((0,0,0,0),(0,0),ImageOps.invert(a));rebuilt=Image.new('RGBA',(48,64));rebuilt.paste(cell,tuple(f['translate_native']));x,y,w,h=f['rect'];actual=native.crop((x,y,x+w,y+h));digest=hashlib.sha256(actual.tobytes()).hexdigest()
  assert actual.tobytes()==rebuilt.tobytes() and digest==f['rgba_sha256']==s['frames'][i]['source_frame_rgba_sha256']
  sx,sy=s['frames'][i]['clothing'];assert actual.getpixel((sx,sy))[3]==255
  cells.append({'index':i,'rgba_sha256':digest,'socket':s['frames'][i]['clothing'],'bounds':list(actual.getbbox())})
 rows[kind]={'master_sha256':m['master_sha256'],'native_sha256':m['sha256'],'cells':cells};clips+=len(m['animations_source_columns'])*4
assert clips==56 and sum(len(row['cells']) for row in rows.values())==96
write('atlas-proofs.json',{'source_pose_count':96,'opaque_hashbound_sockets':96,'clips':clips,'sheets':rows,'semantic_art_acceptance_separate':True})
tool=W/'tools/verify_p06_tega.py';tree=ast.parse(tool.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='valid_replay');ns={'SCOPE':'TEGA_ENVIRONMENT_COMPONENT_ONLY'};exec(compile(ast.Module(body=[fn],type_ignores=[]),str(tool),'exec'),ns)
valid=ns['valid_replay'];probes=[]
for run,mode in [('headless-04','live'),('native-01','live'),('native-01','movie')]:
 d=json.loads((W/'reports/phases/P06/tega-environment-01'/run/mode/'result.json').read_text());headless=run.startswith('headless');assert valid(d,headless) and not valid(d,not headless);probes.append({'case':run+'/'+mode,'correct_mode':True,'opposite_mode_rejected':True})
for renderer in ['', ' ',None,True,1,[],{},'unknown','X11 ',' X11']:
 invalid=copy.deepcopy(d);invalid['renderer']=renderer;assert not valid(invalid,False) and not valid(invalid,True);probes.append({'case':repr(renderer),'rejected':True})
write('pure-report-probes.json',{'pure_AST_only':True,'cases':probes,'engine_runs':0})
print(json.dumps({'runs':{k:{q:v[q] for q in ['checks','trace_samples','object_samples','Core_contacts','FIN_cases','blood_max_follow_offset']} for k,v in results.items()},'atlas_cells':96,'pure_controls':len(probes)}))
