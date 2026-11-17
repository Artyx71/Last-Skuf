"""Logic-equivalent zero-sample counterexample, not Godot or physical-input execution."""
from pathlib import Path
import json,hashlib
Q=Path(__file__).resolve().parent
src=(Q/'candidate.gd.txt').read_text()
assert 'var actual_held:=true' in src
assert 'for i in range(first_input_trace,ammo_trace.size()):' in src
assert 'actual_held=actual_held and observed.run_pressed and Vector2(observed.input_vector[0],observed.input_vector[1]).is_equal_approx(DIRECTIONS[di])' in src
def exact_vector_cases(samples):
 value=True
 for row in samples:value=value and row['run_pressed'] and row['input_vector']==[0,1]
 return value
samples=[{'run_pressed':True,'input_vector':[0,1]} for _ in range(32)]
wrongrun=samples.copy();wrongrun[7]={'run_pressed':False,'input_vector':[0,1]}
wrongdir=samples.copy();wrongdir[7]={'run_pressed':True,'input_vector':[0,0]}
rows=[]
for name,values,expected in [('valid32',samples,True),('run_drop',wrongrun,False),('direction_drop',wrongdir,False),('missing_all',[],False)]:
 actual=exact_vector_cases(values);rows.append({'case':name,'samples':len(values),'expected':expected,'actual':actual,'passed':actual==expected})
print(json.dumps({'source_sha256':hashlib.sha256(src.encode()).hexdigest(),'scope':'PURE_LOGICAL_PREFLIGHT_NOT_ENGINE','cases':rows}))
