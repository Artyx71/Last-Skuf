from pathlib import Path
import json,collections,math
O=Path(__file__).resolve().parent
raw=json.loads((O/'actual-evidence/raw.json').read_text());metrics=json.loads((O/'actual-evidence/metrics.json').read_text())
counts=collections.defaultdict(collections.Counter)
for a in raw['requests']:
 counts[a['context']][a['kind']]+=1
 p=[p for p in raw['physics']if p['usec']==a['accepted_usec']and p['tick']==a['accepted_tick']];d=[p for p in raw['draws']if p['usec']==a['render_usec']and p['draw']==a['render_draw']]
 assert len(p)==len(d)==1
 assert p[0]['state']==a['accepted_state']and d[0]['state']==a['render_state']and p[0]['state']['context']==d[0]['state']['context']==a['context']
 changed=[p for p in raw['draws']if p['usec']>=a['accepted_usec']and p.get('state',{}).get('context')==a['context']and any(p['state'][k]!=a['before_state'][k]for k in ['draw_position','animation','frame'])]
 assert changed[0]['usec']==a['render_usec']
 if a['kind']=='melee':assert len([c for c in raw['contacts']if c['context']==a['context']and c['usec']==a['contact_usec']and c['action']=='shove'and c['action_frame']==1 and c['target']!=c['player_id']and c['usec']>a['accepted_usec']])==1
 if a['kind']=='restart':
  assert len([c for c in raw['contacts']if c['context']==a['context']and c['usec']==a['death_usec']and c['lethal']is True and c['target']==c['player_id']])==1
  assert a['before_state']['health']==0 and a['before_state']['host_state']=='dead'and a['accepted_state']['health']==1 and a['accepted_state']['host_state']=='playing'
assert len(counts)==8 and all(v=={'move':4,'melee':1,'restart':1}for v in counts.values())
def st(v):
 s=sorted(v);return {'samples':len(s),'p50':s[math.ceil(len(s)*.5)-1],'p95':s[math.ceil(len(s)*.95)-1],'p99':s[math.ceil(len(s)*.99)-1],'max':s[-1]}
values={'input_accept_ms':[(a['accepted_usec']-a['input_usec'])/1000 for a in raw['requests']], 'input_render_ms':[(a['render_usec']-a['input_usec'])/1000 for a in raw['requests']], 'death_to_control_ms':[(a['accepted_usec']-a['death_usec'])/1000 for a in raw['requests']if a['kind']=='restart'],'accepted_to_contact_ms':[(a['contact_usec']-a['accepted_usec'])/1000 for a in raw['requests']if a['kind']=='melee']}
assert all(metrics[k]==st(v)for k,v in values.items());assert len(raw['checks'])==74 and all(c['passed']is True for c in raw['checks'])
print('ACTUAL BASELINE: 74 checks,48 state/context/first-draw bindings,8 outgoing+8 lethal Corebindings and independently derived latency stats PASS. Validator counterexamples remain separate.')
