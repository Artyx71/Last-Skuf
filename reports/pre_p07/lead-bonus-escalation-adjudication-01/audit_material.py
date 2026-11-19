"""Independent read-only material audit, no operational imports or engine/Git calls."""
from pathlib import Path
import json,hashlib,re,shutil
O=Path(__file__).resolve().parent;R=O.parents[2];W=R/'.autopilot/worktrees/P07'
E=W/'reports/pre_p07/bonus-legacy-supplement-01';A=W/'reports/pre_p07/bonus-live-adapter-03';C=W/'reports/pre_p07/bonus-live-adapter-02/core'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((E/'source_before.json').read_text());after=json.loads((E/'source_after.json').read_text());assert before==after
for rel,sha in before.items():assert h(W/rel)==sha,rel
prior=json.loads((A/'source_before.json').read_text());game={p:sha for p,sha in before.items() if p.startswith('game/')};priorgame={p:sha for p,sha in prior.items() if p.startswith('game/')}
assert game.keys()==priorgame.keys();changed=[p for p in game if game[p]!=priorgame[p]];assert changed==['game/scripts/qa/story_replay.gd'],changed
for rel,sha in game.items():assert h(E/'isolated_project'/rel)==sha,rel
source=(W/changed[0]).read_text();oldsource=(A/'isolated_project'/changed[0]).read_text()
checks=lambda s:[x.strip() for x in s.splitlines() if 'check(' in x and not x.lstrip().startswith('func check(')]
assert checks(source)==checks(oldsource)
assert 'if DisplayServer.get_name() != "headless": await RenderingServer.frame_post_draw' in source
assert source.count('await key(KEY_F4)')==oldsource.count('await key(KEY_F4)')==1
result=json.loads((E/'result.json').read_text());nested=result['p04_input']
assert len(result['checks'])==41 and all(x is True for x in result['checks'].values())
assert len(nested['checks'])==49 and all(x is True for x in nested['checks'].values())
assert result['passed'] is True and nested['passed'] is True and result['route_warps']==nested['route_warps']==0 and len(nested['deaths'])==10
for death in nested['deaths']:
 assert death['actual_ai_death'] is True and death['damage_events']==1
 assert death['reset_actions']==death['reset_bullets']==death['reset_kills']==0 and death['latency_ms']<1000
assert result['story']['completion_rewards']==1
for event in ['EV_CH01_INTRO','EV_CH01_PHONE','EV_CH01_OUTRO','EV_CH01_SERVICE_ESCAPE']:
 assert len([r for r in result['story']['history'] if r['id']==event])==1
validation=json.loads((E/'validation.json').read_text());assert validation['passed'] is True and validation['exit_code']==0 and validation['timeout_seconds']==180 and validation['timed_out'] is False and validation['wall_seconds']<180
assert h(E/'native.log')==validation['log_sha256']
assert not any(x in (E/'native.log').read_text() for x in ['SCRIPT ERROR:','Parse Error:','FAIL: P05'])
assert result['startup_after_physics_wait']['drawn_frames']==0 and result['startup_before_first_key']['drawn_frames']==4
assert result['startup_after_physics_wait']['window_focus'] is True and result['startup_before_first_key']['window_focus'] is True
adapterruns=json.loads((A/'runs.json').read_text());assert len(adapterruns)==4 and [r['checks'] for r in adapterruns]==[21,4,38,5]
for row in adapterruns:
 assert row['passed'] is True and row['exit_code']==0 and h(A/(row['name']+'.log'))==row['log_sha256']
 data=json.loads((A/(row['name']+'-result.json')).read_text());assert len(data['checks'])==row['checks'] and all(r['passed'] is True for r in data['checks'])
core=json.loads((C/'validation.json').read_text());assert core['passed'] is True
coredata=json.loads((C/'checks-result.json').read_text());assert coredata['passed']==101 and coredata['failed']==0 and len(coredata['checks'])==101 and all(x['passed'] is True for x in coredata['checks'])
for row in core['runs']:assert row['passed'] is True
for mode in ['before_rename','after_rename']:assert next(r for r in core['runs'] if r['name']==mode)['exit_code']==-9
# Current core/IO helpers remain the tested moved implementation; only QA replay differs in Game.
corebefore=json.loads((C/'source_before.json').read_text())
critical=['tools/p07_bonus_pilot.py','tools/fixtures/p07_bonus_contract.gd','tools/fixtures/p07_bonus_host.gd','game/scripts/story/bonus_progress.gd','game/scripts/story/story_service.gd','game/scripts/core/bootstrap.gd','game/scripts/ui/story_journal.gd']
for rel in critical:assert before[rel]==corebefore[rel],rel
canonical={'game/scripts/story/story_state.gd':'ae0a3f566f93fa9d0c35795708f9d3dc0672b9c60d332676b560204993db4922','game/scripts/story/story_registry.gd':'8dabb3a960208b3554dce3ba818f4efbc6bdc2ae390739e1e4abe4bdabc011b6','game/resources/story/registry.json':'7f338f4e889f560ce2b98448a9243f80018984c0b01def8bf9f03b30777effb4','game/resources/story/routes.json':'7137e57c9e17678bcfca6e0ad39bae9f2904f880a31116da4f70bbeb9b689aa8'}
for rel,sha in canonical.items():assert h(R/rel)==h(W/rel)==sha
job=R/'.autopilot/jobs/b72bdfd3dce24e3fb499c3d06bb06c02';receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text())
assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
lock=json.loads((W/'tools/toolchain.lock.json').read_text());engine=W/'.tools/godot'/('Godot_v'+lock['release']+'_linux.x86_64');assert h(engine)==lock['linux_binary_sha256']
for rel in critical+['game/scripts/qa/story_replay.gd','tools/p07_legacy_startup_probe.py','specs/BONUS_PROGRESS_CONTRACT.md']:
 out=O/'source-snapshot'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(W/rel,out)
rows={'schema':1,'scope':'MANUAL_FINITE_SUPPLEMENT_AND_RETAINED_H05_MATERIAL_AUDIT','runtime_source_head':'a0ab23a9838d9308ee9acc38d3ef2cdc91cedfc4','source_keys_rehashed':len(before),'Game_files_rehashed':len(game),'unchanged_Game_from_a684':len(game)-1,'only_changed_Game':changed,'old_check_call_lines_identical':len(checks(source)),'first_F4_calls':1,'native_timeout_unchanged':180,'actual_native_checks':41,'actual_nested_Input_checks':49,'actual_deaths':10,'route_warps':0,'canonical_completion_rewards':1,'core_actual_checks_reused':101,'retained_first4_actual_checks':[21,4,38,5],'critical_core_owner_UI_pins_exact':{p:before[p] for p in critical},'canonical4_ROOT_Work_accepted_hashes':canonical,'startup_after_old_wait':result['startup_after_physics_wait'],'startup_before_key':result['startup_before_first_key'],'operation':'b72bdfd3dce24e3fb499c3d06bb06c02','receipt':receipt,'receipt_sha256':h(job/'receipt.json'),'input_sha256':h(job/'input.json'),'Godot_binary_sha256':h(engine),'ordinary_user_profiles_untouched':True,'broad_fail03_not_rewritten_PASS':True,'reviewer_engine_Controller_Git_network_calls':0}
(O/'own-material-audit.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({k:v for k,v in rows.items() if k not in ['critical_core_owner_UI_pins_exact','canonical4_ROOT_Work_accepted_hashes','startup_after_old_wait','startup_before_key','receipt']},indent=2))
