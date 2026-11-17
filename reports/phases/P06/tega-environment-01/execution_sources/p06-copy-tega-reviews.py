from pathlib import Path
import json,hashlib,shutil,sys
r=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');w=r/'.autopilot/worktrees/P06'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in sys.argv[1:]:
 src=r/'reports/phases/P06'/name;dst=w/'reports/phases/P06'/name
 if (src/'shipping-proofset/shipping-manifest.json').is_file():src=src/'shipping-proofset'
 manifest=next(src/n for n in ['shipping-manifest.json','portable-manifest.json','artifacts.json','transfer_manifest.json'] if (src/n).is_file())
 m=json.loads(manifest.read_text());records=m.get('files_to_copy',m.get('files_sha256',m.get('owned_files_sha256',m.get('entries',m.get('files')))))
 assert records is not None,manifest
 items=records.items() if isinstance(records,dict) else [(e['path'],e) for e in records]
 count=0;size=0
 def cp(p,q,h=None):
  assert p.resolve().is_relative_to(src.resolve()) and p.is_file()
  if h is not None:assert sha(p)==h,p
  q.parent.mkdir(parents=True,exist_ok=True)
  if q.exists():assert sha(q)==sha(p),q
  else:shutil.copyfile(p,q)
  assert sha(q)==sha(p)
 for rel,record in items:
  h=record['sha256'] if isinstance(record,dict) else record;p=src/rel;cp(p,dst/rel,h);count+=1;size+=p.stat().st_size
 for rel in [manifest.name,'decision.json','FINAL_HASHES.json']:
  p=src/rel
  if p.is_file():cp(p,dst/rel)
 print(name,count,'declared files verified/copied;',size,'bytes; decision',sha(src/'decision.json'))
