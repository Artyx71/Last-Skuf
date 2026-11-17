from pathlib import Path
from PIL import Image
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((R/'reports/phases/P06/lead-timka-present-01/source-freeze.json').read_text())['recorded_source_inventory_sha256'];checks=[]
for kind,columns,count in [('world',8,32),('action',7,28),('finisher',6,24)]:
 png=W/f'game/assets/art/characters/timka/{kind}_sheet.png';sockets=W/f'game/assets/art/characters/timka/{kind}.sockets.json';meta=json.loads(sockets.read_text());im=Image.open(png).convert('RGBA');assert sha(png)==old[str(png.relative_to(W))] and meta['sheet_sha256']==sha(png) and len(meta['frames'])==count
 for i,f in enumerate(meta['frames']):
  x,y=f['clothing'];assert f['index']==i and isinstance(x,int) and isinstance(y,int) and im.getpixel((i%columns*48+x,i//columns*64+y))[3]==255
 checks.append({'kind':kind,'count':count,'sheet_sha256':sha(png),'sockets_sha256':sha(sockets),'bitmap_unchanged_since_present_source_adoption':True,'all_points_opaque_integer':True})
refs=json.loads((R/'assets/references/manifest.json').read_text());assert all(sha(R/x['path'])==x['sha256'] for x in refs);assert sha(W/'game/scripts/systems/combat_system.gd')==old['game/scripts/systems/combat_system.gd'];assert sha(W/'game/scripts/ai/enemy_actor.gd')==old['game/scripts/ai/enemy_actor.gd']
(O/'provenance-sockets-check.json').write_text(json.dumps({'schema':1,'scope':'READ_ONLY_HASH_PIXEL_CHECKS_NOT_NEW_ART_OR_LIKENESS_REVIEW','sockets':checks,'bound_points_total':84,'Core_and_enemy_code_unchanged_since_present':True,'root_private_manifest_count':len(refs),'private_manifest_sha256':sha(R/'assets/references/manifest.json'),'raw_private_photos_not_copied_or_uploaded':True,'new_bitmaps_audio_or_generator_calls_by_reviewer':0,'clothing_semantics_not_inferred_only_from_alpha_or_palette':True},indent=2)+'\n');print(json.dumps({'sockets':84,'sheets_unchanged':3,'root_private_manifest_count':len(refs),'Core_NPC_unchanged':True}))
