from pathlib import Path
import json,hashlib,argparse
O=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);a=p.parse_args();W=a.source_root
contract=json.loads((O/'actual-evidence/final-df/contract.PROPOSED.json').read_text());old=O.parent/'qa-pacing-calibration-01/actual-evidence';base=json.loads((old/'source_before.json').read_text());current=contract['source_inventory_sha256'];assert base==contract['baseline_source_inventory_sha256'];assert len(current)==len(base)==616
changed=sorted(n for n in current if current[n]!=base[n]);assert changed==['tools/p07_pacing.py','tools/tests/test_p07_pacing.py']
assert contract['baseline_raw_sha256']==hashlib.sha256((old/'raw.json').read_bytes()).hexdigest();assert contract['baseline_metrics_sha256']==hashlib.sha256((O/'actual-evidence/final-df/metrics.json').read_bytes()).hexdigest()
assert contract['guard_only_rebase']['current_guard_head']=='df7a6eeae8a8e1a440f8d8e35d84a17a20296290'
for n,h in current.items():assert hashlib.sha256((W/n).read_bytes()).hexdigest()==h,n
for n in changed:assert hashlib.sha256((O/'final-source-df'/n).read_bytes()).hexdigest()==current[n]
print('616/616 current source files match proposed final contract; baseline map exact; only2 Python guard/test paths changed; Game/GDScript/settings unchanged; raw and correctedmetrics SHA exact.')
