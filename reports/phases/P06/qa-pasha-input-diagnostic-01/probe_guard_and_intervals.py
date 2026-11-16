"""Pure exact7a guard logic/real-data recomputation. No GDScript parser or engine invocation."""
from pathlib import Path
import json,math,copy,hashlib,collections
Q=Path(__file__).resolve().parent;W=Q.parents[3]/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/pasha-input-diagnostic-01'
def strict(text):
 def pairs(items):
  d={}
  for k,v in items:
   if k in d:raise ValueError('duplicate '+k)
   d[k]=v
  return d
 def finite(s):
  n=float(s)
  if not math.isfinite(n):raise ValueError(s)
  return n
 def bad(s):raise ValueError(s)
 return json.loads(text,object_pairs_hook=pairs,parse_float=finite,parse_constant=bad)
s=(Q/'guard-source7a76.gd.txt').read_text();assert 'var actual_held:=ammo_trace.size()>first_input_trace' in s;assert 'observed.segment==segment and int(observed.tick)>previous_input_tick and observed.run_pressed' in s;assert 'previous_input_tick=int(observed.tick)' in s
D={'down':[0,1],'left':[-1,0],'right':[1,0],'up':[0,-1]}
def actual_guard(rows,segment,vector):
 held=len(rows)>0;previous=-1
 try:
  for row in rows:
   held=held and row['segment']==segment and int(row['tick'])>previous and row['run_pressed'] and all(abs(float(x)-y)<1e-5 for x,y in zip([row['input_vector'][0],row['input_vector'][1]],vector))
   previous=int(row['tick'])
 except (KeyError,TypeError,ValueError):return False
 return bool(held)
real=[];first=None
for mode,folder in [('headless','headless/live'),('native','native/live'),('movie','native/movie')]:
 path=P/folder/'result.json';d=strict(path.read_text());allrows=d['ammo_trace'];expected=set()
 for reduced in ['false','true']:
  for direction,vec in D.items():
   seg='moving_shot_'+reduced+'_'+direction;expected.add(seg);indices=[i for i,x in enumerate(allrows) if x['segment']==seg];start,end=min(indices),max(indices);span=allrows[start:end+1];trace=[x for x in d['trace'] if x['segment']==seg];checks={'nonempty_exact32':len(span)==len(indices)==32,'no_foreign_scope_hidden_in_filtered_interval':indices==list(range(start,end+1)) and all(x['segment']==seg for x in span),'actual_int_unique_increasing_ticks':all(type(x['tick']) is int for x in span) and all(b['tick']>a['tick'] for a,b in zip(span,span[1:])),'exact_tick_binding_to_physics_trace':[x['tick'] for x in span]==[x['tick'] for x in trace],'actual7a_guard_accepts_saved_records':actual_guard(span,seg,vec)};real.append({'mode':mode,'segment':seg,'interval_start_index':start,'interval_end_index':end,'samples':len(span),'checks':checks,'passed':all(checks.values())})
   if first is None:first=(span,seg,vec)
 real.append({'mode':mode,'scope':'no_unknown_moving_shot_intervals','passed':set(x['segment'] for x in allrows if x['segment'].startswith('moving_shot_'))==expected})
base,seg,vec=first;cases=[]
def add(name,rows,expected):
 actual=actual_guard(rows,seg,vec);cases.append({'name':name,'records':len(rows),'expected':expected,'actual':actual,'passed':actual==expected})
add('valid_actual32',base,True);add('missing_all',[],False)
for name,mut in [('wrong_segment',lambda a:a[7].update(segment='foreign')),('run_off',lambda a:a[7].update(run_pressed=False)),('zero_vector',lambda a:a[7].update(input_vector=[0,0])),('duplicate_tick',lambda a:a[7].update(tick=a[6]['tick'])),('reverse_tick',lambda a:a.reverse())]:
 rows=copy.deepcopy(base);mut(rows);add(name,rows,False)
result={'scope':'PURE7A_GUARD_CLOSURE_AND_ACTUAL_CONTIGUOUS_INTERVAL_BINDING','source_commit':'7a76f7bff2e583ae7a49bf3c6d23135740e6bc81','source_sha256':hashlib.sha256(s.encode()).hexdigest(),'actual_route_cases':24,'actual_observations':sum(x.get('samples',0) for x in real),'real_cases':real,'negative_and_control_cases':cases,'all_passed':all(x['passed'] for x in real+cases),'no_GDScript_compile_or_engine_claim':True};(Q/'guard-and-interval-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'actual24':all(x['passed'] for x in real),'samples':result['actual_observations'],'controls':len(cases),'all_passed':result['all_passed']}))
