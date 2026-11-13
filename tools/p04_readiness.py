#!/usr/bin/env python3
"""Read-only readiness audit/queue preparation; never enters P04 or changes its gate."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def main():
    state=json.loads((ROOT/'automation/phase_state.json').read_text())
    required=['game/scripts/systems/combat_system.gd','game/scripts/actors/combat_player.gd',
        'game/scripts/ai/enemy_actor.gd','game/scripts/systems/dialogue_director.gd',
        'game/scripts/systems/audio_director.gd','game/scripts/core/options_store.gd',
        'specs/COMBAT_GORE_POLISH_SPEC.md','autopilot/queue.json']
    inputs=[{'path':p,'exists':(ROOT/p).is_file(),
             'sha256':hashlib.sha256((ROOT/p).read_bytes()).hexdigest() if (ROOT/p).is_file() else None} for p in required]
    decision=json.loads((ROOT/'reports/phases/P03/decision.json').read_text())
    merged=state.get('autopilot',{}).get('phases',{}).get('P03',{}).get('merge',{}).get('status')=='MERGED'
    result={'status':'PREPARED' if all(i['exists'] for i in inputs) else 'FAIL',
        'implementation_allowed':decision['status']=='PASS' and merged,
        'blockers':([] if decision['status']=='PASS' else ['P03 independent PASS required'])+([] if merged else ['P03 exact-SHA protected squash merge required']),
        'active_phase_unchanged':state['active_phase'],'inputs':inputs,
        'scope':'Preparation only. No mission, final art or new finisher is claimed.',
        'campaign_gate':'P04G PASS required before P07'}
    output=ROOT/'reports/autopilot/P04'; output.mkdir(parents=True,exist_ok=True)
    (output/'readiness.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','implementation_allowed','blockers']},ensure_ascii=False))
    return 0 if result['status']=='PREPARED' else 1

if __name__=='__main__': raise SystemExit(main())
