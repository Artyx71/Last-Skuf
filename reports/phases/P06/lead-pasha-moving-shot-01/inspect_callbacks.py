from pathlib import Path
import json,hashlib,shutil
O=Path(__file__).parent;R=O.parents[3];W=R/'.autopilot/worktrees/P06';GP=R/'reports/phases/P06/gameplay-pasha-moving-shot-01/code-preflight/targeted-closure-final17b';Q=R/'reports/phases/P06/qa-pasha-moving-shot-03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=json.loads((GP/'independent-raw-proof.json').read_text());impact=d['impact'];assert impact['passed'] is True and len(impact['checks'])==5 and impact['same_tick_after_Core']==impact['callback']['after_reset']
a=impact['callback']['before_reset'];b=impact['same_tick_after_Core'];assert a['epoch']+1==b['epoch'] and a['tick']==b['tick'] and b['ammo']==4 and b['rounds_spent']==b['damage_events']==b['decals']==b['particles']==b['moving_jobs']==b['projectiles']==0 and not b['contact_events'] and not b['receipts']
f=d['finisher'];assert f['passed'] is True and len(f['checks'])==7 and f['callback']['free_effective'] and f['callback']['inside_Core_tick_finishers'];after=f['same_tick_after_Core'];assert after['target_live'] is False and after['ammo']==4 and after['rounds_spent']==0 and after['score']==0 and after['damage_events']==1
binding=json.loads((GP/'evidence/WORK-source-before.json').read_text());current=json.loads((O/'source-freeze.json').read_text())['source_hashes'];changed=[k for k,v in current.items() if binding.get(k)!=v];assert changed==['game/scripts/ui/ranged_feedback.gd']
assert sha(W/'game/scripts/systems/combat_system.gd')==sha(GP/'binding/source-snapshot-final-17b/game/scripts/systems/combat_system.gd')
wall=json.loads((Q/'wall-closure/result.json').read_text());assert wall['passed'] is True and len(wall['checks'])==16;summ=[]
for p in wall['proofs']:
 a=p['before_callback'];b=p['after_Core_same_tick'];assert a['tick']==b['tick']
 if p['reset']:assert b['epoch']==a['epoch']+1 and b['hit_flash']==0 and b['last_hit_position']==[0,0] and b['ammo']==4 and b['rounds_spent']==0 and b['jobs']==b['projectiles']==b['damage_events']==0
 else:assert b['hit_flash']==.15 and b['ammo']==3 and b['rounds_spent']==1
 summ.append({'branch':p['branch'],'reset':p['reset'],'before':a,'after_Core':b})
pre=Q/'HUD-preflight-verification.json';pd=json.loads(pre.read_text());assert pd['checks']==18 and pd['actualPNG9']==9 and len(pd['samples'])==9 and all(x['meter']==[380,49,144,2] and x['opaque_NPC_pixels_under_meter']==0 for x in pd['samples'])
out=O/'causal-proof-subset';out.mkdir(exist_ok=True)
for p,name in [(GP/'independent-raw-proof.json','GP-originals-final17b-raw.json'),(GP/'decision.json','GP-originals-final17b-decision.json'),(Q/'wall-closure/result.json','b359-wall16-result.json'),(Q/'qa_pasha_wall_reset_v2.gd','qa_pasha_wall_reset_v2.gd'),(pre,'HUD-nine-fixtures.json'),(Q/'author-evidence/HUD-preflight/probe.gd','HUD-actual-pixel-probe.gd')]:shutil.copyfile(p,out/name)
preimg=W/'reports/phases/P06/pasha-moving-shot-01/hud-preflight-01/04_cooldown.png';shutil.copyfile(preimg,O/'native-HUD/preflight_04_cooldown.png')
(O/'causal-closure-proofs.json').write_text(json.dumps({'GP_PAS01_actual5_pass':True,'GP_PAS02_actual7_pass':True,'targeted_runtime_source':'17b162d9d4320650f7e0422d63c1c2c77882a9d3','b359_rollforward_only_changed_source':changed,'Core_exact_to_targeted_source':True,'b359_fresh_wall16':summ,'HUD_preflight_actual9_states18checks':pd['samples'],'preflight_cooldown_PNG_sha256':sha(preimg),'all9_NPC_pixel_overlap_counts_zero_for_saved_fixtures':True,'all_future_NPC_camera_positions_guaranteed':False,'reviewer_engine_runs':0},ensure_ascii=False,indent=2)+'\n')
print({'original5and7':True,'UI_only_keys':changed,'wall_cases':len(summ),'HUDstates':len(pd['samples'])})
