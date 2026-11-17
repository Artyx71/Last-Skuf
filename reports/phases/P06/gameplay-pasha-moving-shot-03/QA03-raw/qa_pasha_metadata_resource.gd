extends "res://tests/pasha_moving_shot_replay.gd"
## Future final-candidate QA ONLY. Does not duplicate Gameplay bodyimpact/reset/free probes.
var originals:Dictionary={}
func frames(count:int)->void:
 for i in count:
  await physics_frame
  await process_frame
func read_text(path:String)->String:return FileAccess.get_file_as_string(path)
func write_text(path:String,text:String)->void:
 var f=FileAccess.open(path,FileAccess.WRITE);f.store_string(text);f.close()
func snapshot()->Dictionary:
 return {"actor":lab.player.get_instance_id(),"authority":lab.scene_policy.action_authority(lab.player.actor_id),"epoch":lab.combat.encounter_epoch,"attacks":lab.combat.attacks.duplicate(true),"projectiles":lab.combat.projectiles.duplicate(true),"receipts":lab.combat.receipts.duplicate(true),"action":lab.player.action_kind,"cooldown":lab.player.ability_cooldown,"options":lab.options_panel.visible,"state":lab.state,"score":lab.score}
func refusal(label:String,path:String,bad:String)->void:
 lab.select_fixture("gabar_training")
 var pending_action:bool=lab.player.use_ability()
 lab._set_options_visible(true)
 var before:Dictionary=snapshot()
 write_text(path,bad)
 var denied:bool=not lab.select_fixture("pasha_training")
 check(label+":atomic_refusal_with_actual_pending_Gabar",pending_action and not before.attacks.is_empty() and denied and snapshot()==before)
 write_text(path,originals[path])
func run()->void:
 output=OS.get_environment("AYAY_P06_PASHA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);lab.auto_retry=false
 var layout_path:String="res://assets/art/characters/pasha/moving_shot.json"
 var muzzle_path:String="res://assets/art/characters/pasha/moving_shot.muzzles.json"
 var socket_path:String="res://assets/art/characters/pasha/moving_shot.sockets.json"
 var png_path:String="res://assets/art/characters/pasha/moving_shot_sheet.png"
 for path in [layout_path,muzzle_path,socket_path]:originals[path]=read_text(path)
 refusal("missing_moving_layout",layout_path,"null")
 var data:Dictionary=JSON.parse_string(originals[layout_path]);data.actor_id="gabar";refusal("wrong_moving_identity",layout_path,JSON.stringify(data))
 data=JSON.parse_string(originals[layout_path]);data.animations_source_columns.moving_shot.pop_back();refusal("missing_eighth_source_pose",layout_path,JSON.stringify(data))
 data=JSON.parse_string(originals[layout_path]);data.frames.pop_back();refusal("missing_one_of_32_frame_records",layout_path,JSON.stringify(data))
 refusal("missing_muzzles",muzzle_path,"null")
 data=JSON.parse_string(originals[muzzle_path]);data.sheet_sha256="0".repeat(64);refusal("stale_muzzle_sheet_binding",muzzle_path,JSON.stringify(data))
 data=JSON.parse_string(originals[muzzle_path]);data.frames[0].column=2;refusal("muzzle_wrong_contact_pose",muzzle_path,JSON.stringify(data))
 data=JSON.parse_string(originals[muzzle_path]);data.frames[0].muzzle=[0,0];refusal("transparent_muzzle_pixel",muzzle_path,JSON.stringify(data))
 data=JSON.parse_string(originals[muzzle_path]);data.frames[0].muzzle=[0.5,2];refusal("fractional_muzzle",muzzle_path,JSON.stringify(data))
 data=JSON.parse_string(originals[socket_path]);data.sheet_sha256="0".repeat(64);refusal("stale_clothing_sheet_binding",socket_path,JSON.stringify(data))
 check("all_text_inputs_restored_exact",read_text(layout_path)==originals[layout_path] and read_text(muzzle_path)==originals[muzzle_path] and read_text(socket_path)==originals[socket_path])
 lab._set_options_visible(false);await tap(KEY_7)
 check("real_Input_selects_own_ready_Pasha",lab.player.actor_id=="pasha" and lab.player.prepared_ability=="moving_shot" and lab.player.authored_frames.get_animation_names().size()==60)
 var foreign=preload("res://scripts/abilities/moving_shot.gd").new()
 check("foreign_strategy_cannot_start_or_spend_owner_clip",not foreign.start(lab.player) and not foreign.spend_round(lab.player,lab.combat.encounter_epoch,90001,"QA_foreign") and lab.player.movement_ability.ammo==4 and lab.player.ability_uses==0)
 await setup(2,170,20)
 for index in 4:
  while lab.player.ability_cooldown>0 or not lab.player.action_kind.is_empty():await frames(1)
  await tap(KEY_F)
  var budget:int=30
  while lab.player.movement_ability.rounds_spent<index+1 and budget>0:await frames(1);budget-=1
  check("actual_round_cost_"+str(index),lab.player.movement_ability.rounds_spent==index+1 and lab.player.movement_ability.ammo==3-index)
 var strategy=lab.player.movement_ability
 var entry:Dictionary=strategy.cost_history[0].duplicate(true)
 var old_costs:int=strategy.cost_history.size()
 var old_ammo:int=strategy.ammo
 check("duplicate_same_cost_token_is_idempotent",strategy.spend_round(lab.player,entry.epoch,entry.id,"QA_duplicate_token") and strategy.ammo==old_ammo and strategy.cost_history.size()==old_costs and strategy.rounds_spent==4)
 check("negative_epoch_cannot_charge_resource",not strategy.spend_round(lab.player,lab.combat.encounter_epoch-1,99100,"QA_stale") and strategy.ammo==old_ammo)
 await frames(12)
 check("empty_clip_actual_HUD_and_finite_bounds",strategy.ammo==0 and not lab.player.use_ability() and not lab.player.attack_ranged() and not lab.player.can_use_finisher("firearm") and lab.ranged_feedback.displayed_feedback.ammo==0 and lab.ranged_feedback.title.text.contains("0 / 4"))
 var before_read:Dictionary={"ammo":strategy.ammo,"refill":strategy.refill_elapsed,"costs":strategy.cost_history.duplicate(true),"uses":lab.player.ability_uses,"receipts":lab.combat.receipts.duplicate(true)}
 var feedback:Dictionary=lab.player.ranged_feedback();feedback.ammo=999;feedback.phase="fake"
 check("feedback_snapshot_mutation_cannot_change_combat_resource",lab.player.movement_ability.ammo==before_read.ammo and strategy.refill_elapsed==before_read.refill and strategy.cost_history==before_read.costs and lab.player.ability_uses==before_read.uses and lab.combat.receipts==before_read.receipts)
 check("HUD_readable_above_playfield_and_nonintercepting",lab.ranged_feedback.meter.size.y>=2 and lab.ranged_feedback.meter.size.y<=5 and lab.ranged_feedback.meter.get_global_rect().end.y<=54 and lab.ranged_feedback.title.get_global_rect().end.y<=54 and lab.ranged_feedback.detail.get_global_rect().end.y<=54 and lab.ranged_feedback.mouse_filter==Control.MOUSE_FILTER_IGNORE and lab.ranged_feedback.title.mouse_filter==Control.MOUSE_FILTER_IGNORE and lab.ranged_feedback.detail.mouse_filter==Control.MOUSE_FILTER_IGNORE and lab.ranged_feedback.meter.mouse_filter==Control.MOUSE_FILTER_IGNORE)
 lab._set_options_visible(true)
 var frozen:Array=[strategy.ammo,strategy.refill_elapsed,lab.player.ability_cooldown,lab.player.action_elapsed]
 await frames(70)
 check("options_cannot_mint_passive_rounds",frozen==[strategy.ammo,strategy.refill_elapsed,lab.player.ability_cooldown,lab.player.action_elapsed] and lab.ranged_feedback.displayed_feedback.phase=="paused")
 lab._set_options_visible(false);await tap(KEY_R);await frames(1)
 check("actual_R_resets_clip_tokens_HUD_and_Core_jobs",lab.player.movement_ability.ammo==4 and lab.player.movement_ability.rounds_spent==0 and lab.player.movement_ability.spent_tokens.is_empty() and lab.combat.moving_shots.jobs.is_empty() and lab.combat.projectiles.is_empty() and lab.ranged_feedback.displayed_feedback.ammo==4)
 var passed:bool=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_PASHA_METADATA_ATOMIC_RESOURCE_HUD_BOUNDS_ONLY","phase_approval":false,"passed":passed,"checks":checks},"  "));f.close()
 print("RESULT QA_PASHA_METADATA_RESOURCE passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
