from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=Path(__file__).resolve().parent;D=W/'reports/phases/P06/pasha-moving-shot-01';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=json.loads((D/'native-02/source_hashes.json').read_text());new=json.loads((D/'native-03/source_hashes.json').read_text());probe=json.loads((D/'hud-preflight-01/source_hashes.json').read_text());assert new==probe
changes=[p for p in set(old)|set(new) if old.get(p)!=new.get(p)];assert changes==['game/scripts/ui/ranged_feedback.gd'];keys=[p for p in old if p.startswith('game/assets/art/characters/pasha/')];assert len(keys)==20 and all(old[p]==new[p] for p in keys)
a=json.loads((D/'native-02/live/result.json').read_text());b=json.loads((D/'native-03/live/result.json').read_text());A={x['name']:x for x in a['captures']};B={x['name']:x for x in b['captures']};assert set(A)==set(B) and b['passed'] and len(b['checks'])==581 and len(B)==188
r=[];crop=(190,90,470,320)
for name in B:
 pa,pb=Path(A[name]['path']),Path(B[name]['path']);ha,hb=[hashlib.sha256(Image.open(p).convert('RGBA').crop(crop).tobytes()).hexdigest() for p in [pa,pb]];assert ha==hb,name;r.append({'name':name,'current_path_ROOT_relative':str(pb.relative_to(R)),'current_png_sha256':sha(pb),'prior_crop_RGBA_sha256':ha,'fresh_crop_RGBA_sha256':hb,'gameplay_crop_exact':True})
for res in [a,b]:assert len(res['clothing_overlay'])==32 and all(x['actual']==x['expected'] for x in res['clothing_overlay'])
names=['empty_clip_HUD','refill_HUD','shared_clip_firearm_finisher','paused_HUD','shot_wall','incoming_before_launch_false','incoming_before_launch_true','pasha_after_restart'];board=Image.new('RGB',(1280,378*4),(23,28,34));d=ImageDraw.Draw(board)
for i,name in enumerate(names):
 im=Image.open(Path(B[name]['path'])).convert('RGB');x=i%2*640;y=i//2*378;board.paste(im,(x,y+18));d.text((x+2,y+2),name+' actual native03',fill=(240,220,190))
board.save(O/'native03_actual_full_viewports.png');Image.open(Path(B['pasha_after_restart']['path'])).crop((374,8,634,115)).resize((1560,642),Image.Resampling.NEAREST).save(O/'native03_ready_HUD_6x.png')
j={'schema':1,'status':'PRELIMINARY_NATIVE03_DELTA_VISUAL_REVIEW_PENDING','source_head':'b359747361c6ac76ccfc0cc8ff262c8327cf33e4','fresh_native_checks':581,'fresh_native_captures':188,'source_map_byteexact_to_HUD_preflight':True,'only_source_path_changed_from17b':changes,'Pasha_art_metadata20_exact':{p:new[p] for p in keys},'all188_actual_fresh_png_bound':r,'crop':crop,'gameplay_crops_exact_to_ART02':188,'native_clothing_overlay':b['clothing_overlay'],'native_launches':b['launches'],'native_contacts':b['contacts'],'phase_approval':False};(O/'native_delta_metrics.json').write_text(json.dumps(j,indent=2)+'\n');print('All188 fresh gameplay crops exact priorART02;20asset/metadataentries exact;source map exact approved HUD geometry; movie pending.')
