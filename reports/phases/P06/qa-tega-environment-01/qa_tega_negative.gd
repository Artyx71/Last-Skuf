extends "res://tests/tega_environment_replay.gd"
## Independent isolated QA: production Input for kicks; explicit callbacks are test adversaries.
var qa_mode := ""
var callback_count := 0
var retry_started := false
func frames(count: int) -> void:
 for i in count:
  await physics_frame
  await process_frame
func on_audio(cue: StringName, _at: Vector2) -> void:
 if cue != &"impact_unarmed_metal" or qa_mode.is_empty(): return
 var mode := qa_mode
 qa_mode = ""
 callback_count += 1
 if mode=="free_player":
  lab.process_mode=Node.PROCESS_MODE_DISABLED
  lab.player.free()
 if mode=="queue_free_player":
  lab.process_mode=Node.PROCESS_MODE_DISABLED
  lab.player.queue_free()
 if mode=="replace_body": lab.select_fixture("olezhka_training")
 if mode=="reopen_authority": lab.scene_policy.open("tega_training")
 if mode=="cancel_and_retry":
  lab.player.cancel_action()
  retry_started=lab.player.use_ability()
func snap() -> Dictionary:
 return {"player":lab.player.get_instance_id(),"authority":lab.scene_policy.action_authority(lab.player.actor_id),"epoch":lab.combat.encounter_epoch,"attacks":lab.combat.attacks.duplicate(true),"receipts":lab.combat.receipts.duplicate(true),"cooldown":lab.player.ability_cooldown,"action":lab.player.action_kind,"options":lab.options_panel.visible,"state":lab.state}
func write_text(path: String, value: String) -> void:
 var f=FileAccess.open(path,FileAccess.WRITE);f.store_string(value);f.close()
func rebuild() -> void:
 root.remove_child(lab);lab.queue_free();await process_frame
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6)
 lab.auto_retry=false;lab.audio_event.connect(on_audio)
func run() -> void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true
 DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);lab.auto_retry=false
 check("actual_pending_Gabar_action",lab.player.use_ability() and not lab.combat.attacks.is_empty())
 lab._set_options_visible(true)
 var before=snap()
 var action_path="res://assets/art/characters/tega/action.json"
 var fin_path="res://assets/art/characters/tega/finisher.json"
 var socket_path="res://assets/art/characters/tega/finisher.sockets.json"
 var original_action=FileAccess.get_file_as_string(action_path)
 var original_fin=FileAccess.get_file_as_string(fin_path)
 var original_socket=FileAccess.get_file_as_string(socket_path)
 write_text(action_path,"null")
 check("missing_ACTION_refuses_preserving_real_pending_state",not lab.select_fixture("tega_training") and snap()==before)
 write_text(action_path,original_action)
 write_text(fin_path,"null")
 check("missing_FIN_refuses_preserving_real_pending_state",not lab.select_fixture("tega_training") and snap()==before)
 write_text(fin_path,original_fin)
 var wrong=JSON.parse_string(original_fin);wrong.actor_id="gabar";write_text(fin_path,JSON.stringify(wrong))
 check("wrong_FIN_identity_refuses_atomically",not lab.select_fixture("tega_training") and snap()==before)
 write_text(fin_path,original_fin)
 wrong=JSON.parse_string(original_socket);wrong.sheet_sha256="0".repeat(64);write_text(socket_path,JSON.stringify(wrong))
 check("stale_FIN_garment_binding_refuses_atomically",not lab.select_fixture("tega_training") and snap()==before)
 write_text(socket_path,original_socket)
 check("all_metadata_exactly_restored",FileAccess.get_file_as_string(action_path)==original_action and FileAccess.get_file_as_string(fin_path)==original_fin and FileAccess.get_file_as_string(socket_path)==original_socket)
 lab._set_options_visible(false);await tap(KEY_6)
 check("actual_registered_Tega_selected",lab.player.actor_id=="tega" and lab.player.prepared_ability=="environment_kick")
 var foreign=preload("res://scripts/abilities/environment_kick.gd").new()
 check("foreign_strategy_instance_cannot_create_job_or_cost",not foreign.start(lab.player) and lab.player.ability_uses==0 and lab.combat.environment_kicks.jobs.is_empty())
 for mode in ["free_player","queue_free_player","replace_body","reopen_authority","cancel_and_retry"]:
  await setup(2,false)
  var actor_start:Vector2=lab.player.position
  var object_start:Vector2=lab.training_bench.position
  var epoch:int=lab.combat.encounter_epoch
  qa_mode=mode;callback_count=0;retry_started=false
  await tap(KEY_F);await frames(30)
  check(mode+":actual_audio_callback_executed_once",callback_count==1 and qa_mode.is_empty())
  check(mode+":no_stale_step_or_receipt",lab.training_bench.position==object_start and lab.combat.environment_kicks.jobs.is_empty() and lab.combat.receipts.is_empty() and lab.combat.damage_events==0)
  if mode=="free_player" or mode=="queue_free_player":
   check(mode+":freed_source_not_used",not is_instance_valid(lab.player))
   await rebuild()
  elif mode=="replace_body":
   check(mode+":atomic_real_replacement",lab.player.actor_id=="olezhka" and lab.combat.encounter_epoch>epoch)
   await tap(KEY_6)
  else:
   check(mode+":no_motion_or_refunded_cooldown",lab.player.position==actor_start and lab.player.ability_uses==1 and lab.player.ability_cooldown>0 and not retry_started)
   lab.scene_policy.open("tega_training");await tap(KEY_R)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_ADVERSARIES_ONLY","passed":passed,"phase_approval":false,"checks":checks},"  "));f.close()
 print("RESULT QA_TEGA_NEGATIVE passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
