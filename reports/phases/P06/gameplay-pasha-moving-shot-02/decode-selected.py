from pathlib import Path
import json,subprocess,itertools
O=Path(__file__).parent;b=json.loads((O/'source-bindings.json').read_text());P=Path(b['canonical_native']);d=json.loads((P/'movie/result.json').read_text());groups={}
for dr in ['down','left','right','up']:
 a=[x for x in d['trace'] if x['segment']=='moving_shot_false_'+dr and x['action_kind']=='moving_shot'];start=a[0]['tick'];groups['moving_'+dr]=list(range(start-1,start+29))
fin=[]
for c in d['contacts']:
 if c['segment'].startswith('finisher_') and c['finisher']:fin.extend([(c['segment']+'_contact',c['tick']-1),(c['segment']+'_corpse',c['tick']+10)])
cloth=[('blood_'+c['direction']+'_pose'+str(c['pose']),c['tick']-1) for c in d['clothing_overlay']]
extra=[(('mixed_actual_FIN_contact' if c['segment']=='shared_clip_shot_then_firearm_finisher' else c['segment']),c['tick']-1) for c in d['contacts'] if c['segment'].startswith('incoming_') or (c['segment']=='shared_clip_shot_then_firearm_finisher' and c['finisher'])]
for name,entries in [('FIN',fin),('clothing',cloth),('extra',extra)]:
 for i in range(0,len(entries),20):groups[name+'-%02d'%(i//20)]=entries[i:i+20]
sel=set()
for ns in groups.values():
 for x in ns:sel.add(x[1] if isinstance(x,tuple) else x)
intervals=[]
for _,g in itertools.groupby(enumerate(sorted(sel)),lambda x:x[1]-x[0]):
 ns=[v for _,v in g];intervals.append((ns[0],ns[-1]))
f=O/'decoded-crops';f.mkdir(exist_ok=True)
def balanced(terms):
 if len(terms)==1:return terms[0]
 mid=len(terms)//2;return '('+balanced(terms[:mid])+'+'+balanced(terms[mid:])+')'
expr=balanced(['between(n\\,%d\\,%d)'%x for x in intervals])
subprocess.run(['ffmpeg','-y','-v','error','-i',b['canonical_movie'],'-vf','select='+expr+',crop=700:440:300:200','-fps_mode','vfr',str(f/'frame-%04d.png')],check=True)
fs=sorted(f.glob('frame-*.png'));assert len(fs)==len(sel);m={n:str(p.relative_to(O)) for n,p in zip(sorted(sel),fs)}
(O/'movie-frame-map.json').write_text(json.dumps({'source_SHA256':b['movie_SHA256'],'canonical_movie':b['canonical_movie'],'crop_original_pixels':[300,200,700,440],'zero_based_indices':m,'groups':groups,'event_frame_mapping':'n = physics_tick - 1, verified around actual incoming/blood frames; final mixed contact is held for rendering by replay, requires independent pixel inspection','note':'Lossless extracted crop pixels; no generated evidence. Joins/timing read together with canonical raw traces; setup boundary jumps excluded from physical-action metrics.'},indent=2)+'\n')
boards=O/'boards';boards.mkdir(exist_ok=True)
for g,ns in groups.items():
 args=['montage','-font','/usr/share/fonts/liberation/LiberationSans-Regular.ttf','-pointsize','10','-background','#ddd','-fill','black']
 for x in ns:
  label,n=x if isinstance(x,tuple) else ('',x);args+=['-label',label.replace('finisher_','FIN_')+' n'+str(n),str(O/m[n])]
 subprocess.run(args+['-geometry','350x220+2+2','-tile','4x',str(boards/(g+'.png'))],check=True,capture_output=True)
print('movie crops',len(fs),'boards',len(groups))
