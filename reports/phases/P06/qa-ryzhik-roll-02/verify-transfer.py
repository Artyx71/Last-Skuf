from pathlib import Path
import json,hashlib
from PIL import Image
Q=Path(__file__).resolve().parent;O=Q.parent/'qa-ryzhik-roll-01/isolated-project';I=Q/'isolated-project';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rel='game/assets/art/characters/ryzhik/';old=Image.open(O/rel/'roll_sheet.png').convert('RGBA');new=Image.open(I/rel/'roll_sheet.png').convert('RGBA');assert old.size==new.size==(384,256);cells=[];changed=[]
for i in range(32):
 x=(i%8)*48;y=(i//8)*64;a=old.crop((x,y,x+48,y+64)).tobytes();b=new.crop((x,y,x+48,y+64)).tobytes();same=a==b
 if not same:changed.append(i)
 cells.append({'index':i,'old_RGBA_sha256':hashlib.sha256(a).hexdigest(),'new_RGBA_sha256':hashlib.sha256(b).hexdigest(),'exact_equal':same})
assert changed==[26,29];a=json.loads((O/rel/'roll.sockets.json').read_text());b=json.loads((I/rel/'roll.sockets.json').read_text());socketdiff=[i for i in range(32) if a['frames'][i]!=b['frames'][i]];assert socketdiff==[26,29]
root=Q.parents[3];W=root/'.autopilot/worktrees/P06';review=W/'reports/phases/P06/art-preflight/ryzhik_roll_v2a_source.json';adopt=json.loads((I/'assets/source_art/characters/ryzhik/roll_v2a_adoption.json').read_text());assert h(review)==adopt['source_review_sha256'] and h(I/rel/'roll_sheet.png')==adopt['runtime_png_sha256'] and h(I/rel/'roll.json')==adopt['runtime_layout_sha256'] and h(I/rel/'roll.sockets.json')==adopt['runtime_sockets_sha256']
(Q/'exact-cell-transfer.json').write_text(json.dumps({'scope':'EXACT_PIXEL_AND_SOCKET_TRANSFER_NOT_ART_ACCEPTANCE','changed_native_cells':changed,'changed_socket_entries':socketdiff,'cells':cells,'actual_accepted_source_review_sha256':h(review),'adoption_json_sha256':h(I/'assets/source_art/characters/ryzhik/roll_v2a_adoption.json'),'native_png_sha256':h(I/rel/'roll_sheet.png'),'all_other30_native_RGBA_and_socket_entries_exact':True,'no_likeness_or_native_visual_acceptance':True},indent=2)+'\n');print('Exact nativeRGBA+socket delta26/29, other30same; actualsource/adoption hashes match')
