from pathlib import Path
import sys,shutil,json,hashlib
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent
sys.path.insert(0,str(w/'assets/source_art/characters'));import pack_actor_sheet as p
p.ROOT=d/'preview-project';s=p.ROOT/'assets/source_art/characters/ryzhik'
assert not (s/'action_native_v1a.png').exists()
shutil.copyfile(d/'action_master_v1a.png',s/'action_master_v1a.png')
p.pack('ryzhik','action','v1a','reference',True)
m=json.loads((s/'action_manifest_v1a.json').read_text());(d/'preview_recipe_v1a.json').write_text(json.dumps({'canonical_packer_sha256':p.sha(w/'assets/source_art/characters/pack_actor_sheet.py'),'wrapper_sha256':p.sha(Path(__file__)),'master_sha256':m['master_sha256'],'native_sha256':m['sha256'],'source_only':True,'phase_approval':False,'runtime_approval':False,'whole_figure_normalization_recipe_sha256':p.sha(d/'whole_figure_normalization_v1a.json')},indent=2)+'\n')
