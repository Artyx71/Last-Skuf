from pathlib import Path
import sys,json,hashlib,shutil
r=Path(__file__).resolve().parents[4];w=r/'.autopilot/worktrees/P06';d=Path(__file__).parent
sys.path.insert(0,str(w/'assets/source_art/characters'))
import pack_actor_sheet as canonical
preview=d/'preview-project';source=preview/'assets/source_art/characters/ryzhik';source.mkdir(parents=True,exist_ok=False)
shutil.copyfile(d/'roll_master_v1.png',source/'roll_master_v1.png')
canonical.ROOT=preview
canonical.MAPS['roll']={'roll':list(range(8))}
canonical.pack('ryzhik','roll','v1','reference',True)
manifest=json.loads((source/'roll_manifest_v1.json').read_text())
recipe={'schema':1,'source_only':True,'runtime_approval':False,'phase_approval':False,'canonical_packer':str(w/'assets/source_art/characters/pack_actor_sheet.py'),'canonical_packer_sha256':hashlib.sha256((w/'assets/source_art/characters/pack_actor_sheet.py').read_bytes()).hexdigest(),'wrapper_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'in_memory_extension_only':{'kind':'roll','map':list(range(8)),'ROOT':'this ignored preview-project'},'operation':'Exact existing whole192x256cell NN48x64/alpha128/sharedpalette/fixedrowcol0baseline58, no anatomy edits, no runtimewrites','master_sha256':manifest['master_sha256'],'native_sha256':manifest['sha256'],'source_cells':32,'unique_native_drawings':manifest['unique_native_drawings']}
(d/'preview_recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
print('SOURCE CANDIDATE ONLY',source)
