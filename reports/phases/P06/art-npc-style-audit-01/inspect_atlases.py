from pathlib import Path
import hashlib,json,subprocess
from PIL import Image
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-npc-style-audit-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
inputs={};metrics={}; directions=['down','left','right','up'];cats=['unarmed','blunt','sharp','firearm','environmental']
for folder in ['game/assets/art/enemies','game/assets/art/combat_polish','assets/source_art/combat_polish']:
 for p in sorted((W/folder).rglob('*')):
  if p.is_file() and p.suffix in ['.png','.json','.py','.md','.txt']:
   inputs[str(p.relative_to(W))]={'sha256':sha(p),'bytes':p.stat().st_size}
for kind in ['patrol','rusher','shooter']:
 files={}
 for suffix in ['reactions','finishers']:
  name=f'{kind}_{suffix}.png';p=W/'game/assets/art/combat_polish'/name;im=Image.open(p).convert('RGBA');cols=im.width//48
  assert im.height==256 and cols==(24 if suffix=='reactions' else 15)
  cells=[im.crop((c*48,r*64,(c+1)*48,(r+1)*64)) for r in range(4) for c in range(cols)]
  hashes=[hashlib.sha256(c.tobytes()).hexdigest() for c in cells]
  src=W/'assets/source_art/combat_polish'/name.replace('.png','_native_source.png');assert src.read_bytes()==p.read_bytes()
  old=subprocess.check_output(['git','-C',str(W),'show',f'9128605a6e4a715b3abd71df0124e12a860bead6:game/assets/art/combat_polish/{name}']);assert hashlib.sha256(old).hexdigest()==sha(p)
  redp=p.with_name(p.stem+'_reduced.png');red=Image.open(redp).convert('RGBA');assert red.size==im.size and red.getchannel('A').tobytes()==im.getchannel('A').tobytes()
  assert hashlib.sha256(subprocess.check_output(['git','-C',str(W),'show',f'9128605a6e4a715b3abd71df0124e12a860bead6:game/assets/art/combat_polish/{redp.name}'])).hexdigest()==sha(redp)
  files[suffix]={'dimensions':list(im.size),'slots':len(cells),'unique_RGBA_cells':len(set(hashes)),'native_source_byte_exact':True,'accepted_P04G_912_byte_exact':True,'FullReduced_alpha_identical':True,'per_direction_unique':[len(set(hashes[r*cols:(r+1)*cols])) for r in range(4)]}
  if suffix=='finishers':
   files[suffix]['reuse_per_direction']={d:{'all5_restrained_equal':len({hashes[r*cols+c*3] for c in range(5)})==1,'all5_corpses_equal':len({hashes[r*cols+c*3+2] for c in range(5)})==1,'contact_unique':len({hashes[r*cols+c*3+1] for c in range(5)})} for r,d in enumerate(directions)}
 metrics[kind]=files
for p in [W/'game/scripts/ai/enemy_actor.gd',W/'game/scripts/actors/polish_frames.gd',W/'game/scripts/systems/combat_system.gd',W/'game/scripts/systems/character_combat_profile.gd',W/'game/resources/characters/combat_profiles.json',W/'game/resources/combat/finishers.json',W/'specs/CHARACTER_EXPANSION_SPEC.md',W/'specs/P06_COMBAT_ACCEPTANCE.md',W/'docs/ART_BIBLE.md',W/'AGENTS.md',W/'agents/LEAD_REVIEWER.md',W/'reports/phases/P04G/decision.json']:
 inputs[str(p.relative_to(W))]={'sha256':sha(p),'bytes':p.stat().st_size}
for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha']:
 for n in ['finisher_sheet.png','finisher.json','finisher.sockets.json']:
  p=W/'game/assets/art/characters'/actor/n;inputs[str(p.relative_to(W))]={'sha256':sha(p),'bytes':p.stat().st_size}
put('source-inventory.json',{'schema':1,'WORK_HEAD_at_inspection':subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip(),'base':'WORK','files':inputs,'only_listed_inputs_bound':True})
put('atlas-metrics.json',{'schema':1,'archetypes':metrics,'actual_visual_files_viewed':['game/assets/art/enemies/'+k+'_sheet.png' for k in ['patrol','rusher','shooter']]+['game/assets/art/combat_polish/'+k+'_'+s+'.png' for k in ['patrol','rusher','shooter'] for s in ['finishers','reactions']]+['game/assets/art/combat_polish/patrol_finishers_reduced.png']+['assets/source_art/combat_polish/attempt2/'+k+'_key1_master.png' for k in ['patrol','rusher','shooter']]+['game/assets/art/characters/'+k+'/finisher_sheet.png' for k in ['gabar','olezhka','timka','ryzhik','tega','pasha']],'runtime_view_or_new_acceptance':False,'new_drawings_generated':0})
print(json.dumps(metrics,indent=2))
