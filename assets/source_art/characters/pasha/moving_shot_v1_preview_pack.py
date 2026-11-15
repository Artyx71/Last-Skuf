from pathlib import Path
import sys,shutil,json,hashlib
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent;sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as p
p.ROOT=d/'preview-project';p.MAPS['moving_shot']={'moving_shot':list(range(8))};s=p.ROOT/'assets/source_art/characters/pasha';s.mkdir(parents=True,exist_ok=False);shutil.copyfile(d/'moving_shot_master_v1.png',s/'moving_shot_master_v1.png');p.pack('pasha','moving_shot','v1','reference',True)
(d/'preview_recipe.json').write_text(json.dumps({'source_only':True,'runtime_approval':False,'phase_approval':False,'canonical_packer_sha256':p.sha(w/'assets/source_art/characters/pack_actor_sheet.py'),'wrapper_sha256':p.sha(Path(__file__)),'extension':'mapping only: moving_shot own8columns for all4directions; same canonical wholecell/palette/alpha/referenceanchor algorithm','native_sha256':p.sha(s/'moving_shot_native_v1.png')},indent=2)+'\n')
