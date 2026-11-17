from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-c09-gabar-reuse-feasibility-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
files=[W/p for p in ['AGENTS.md','docs/ART_BIBLE.md','specs/P06_COMBAT_ACCEPTANCE.md','planning/P06_C09_TASKS.md','game/assets/art/combat_polish/atlas.json','game/assets/art/combat_polish/shooter_reactions.png','game/assets/art/combat_polish/shooter_reactions_reduced.png','game/assets/art/combat_polish/shooter_finishers.png','game/assets/art/combat_polish/shooter_finishers_reduced.png','game/assets/art/enemies/shooter_sheet.png','game/assets/art/characters/gabar/finisher_sheet.png','game/assets/art/characters/gabar/finisher.json','assets/source_art/combat_polish/README.md','assets/source_art/combat_polish/pack_generated.py','assets/source_art/combat_polish/render.py','assets/source_art/npc_styles/gabar/source-v3/master.png','assets/source_art/npc_styles/gabar/preview-v3/gabar_npc_native.png','assets/source_art/npc_styles/gabar/preview-v3/manifest.json']]+[R/'reports/phases/P06/art-c09-gabar-source-02'/p for p in ['decision.json','review.md','cell-review.json','FINAL_HASHES.json']]
files=sorted(files);write('source-freeze.json',{'scope':'exact reuse feasibility read inputs; no wholeWORK freeze','files':[{'path':str(p.relative_to(R)),'sha256':h(p),'bytes':p.stat().st_size} for p in files]})
for p in files:
 q=O/'source-snapshot'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
a=json.loads((W/'game/assets/art/combat_polish/atlas.json').read_text());reaction=Image.open(W/'game/assets/art/combat_polish/shooter_reactions.png').convert('RGBA');fin=Image.open(W/'game/assets/art/combat_polish/shooter_finishers.png').convert('RGBA');states=a['states'];records=[]
def crop(im,rect):x,y,w,h=rect;return im.crop((x,y,x+w,y+h))
legacy=[]
for f in a['frames']:
 if f['kind']=='shooter' and f['sheet']=='shooter_finishers.png':
  im=crop(fin,f['rect']);legacy.append({k:f[k] for k in ['state','direction','frame','rect']}|{'rgba_sha256':hashlib.sha256(im.tobytes()).hexdigest()})
for di in ['down','left','right','up']:
 b=Image.new('RGB',(590,8*218+38),(20,24,29));d=ImageDraw.Draw(b);d.text((5,5),'ACTUAL P04 SHOOTER '+di+' / frame0,1,2',fill='white')
 for sr,st in enumerate(states):
  y=38+sr*218;d.text((3,y+80),st,fill='white')
  for k in range(3):
   f=next(f for f in a['frames'] if f['kind']=='shooter' and f['sheet']=='shooter_reactions.png' and f['state']==st and f['direction']==di and f['frame']==k);im=crop(reaction,f['rect']);sha=hashlib.sha256(im.tobytes()).hexdigest();matches=[x for x in legacy if x['rgba_sha256']==sha];records.append({k:f[k] for k in ['state','direction','frame','rect','bounds']}|{'rgba_sha256':sha,'metadata_sha_match':sha==f['sha256'],'legacy_FIN_refs_equal':matches})
   bg=Image.new('RGBA',(48,64),(36,48,44,255));bg.alpha_composite(im);x=140+k*150;b.paste(bg.resize((144,192),Image.Resampling.NEAREST),(x,y));tag=f'{st}{k}';tag+=' LEGACY' if any(x['frame']==1 for x in matches) else '';d.text((x,y+196),tag,fill='white')
 b.save(O/f'shooter-all-states-{di}-3x.png')
write('pool-inventory.json',{'reaction_cells':len(records),'reaction_unique_RGBA':len(set(f['rgba_sha256'] for f in records)),'all_metadata_RGBA_SHA_exact':all(f['metadata_sha_match'] for f in records),'legacy_FIN_refs':legacy,'reaction_pool':records,'note':'A reaction cell already used as a legacy category contact cannot count as a newly distinct Gabar contact by renaming or retiming.'})
print({'frozen_files':len(files),'reaction_cells':len(records),'unique':len(set(f['rgba_sha256'] for f in records))})
