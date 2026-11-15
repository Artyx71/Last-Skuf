extends SceneTree
## Readiness/atomic refusal only; simulated complete art is a negative test double.
## Actual Gabar/Oleg/present Timka bodies below use production art. No new hero/ability approval.
const Player = preload("res://scripts/actors/character_player.gd")
const Policy = preload("res://scripts/systems/character_scene_policy.gd")
var checks: Array[Dictionary] = []

class CompleteArtProbe:
	extends "res://scripts/actors/character_player.gd"
	var load_calls: Array[String] = []
	func _load_combat_frames(id: String) -> SpriteFrames:
		load_calls.append(id)
		# TEST ONLY: make any attempted art load succeed with the real complete
		# Gabar set. This cannot qualify another identity for production/review.
		return CharacterFrames.combat_frames("gabar")

class ForgedPolicy:
	extends RefCounted
	func definition() -> Dictionary:
		return Policy.definitions().gabar_training
	func ability_id() -> String:
		return "gabar_lunge"

func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL P06_READINESS "+label)

func lab_snapshot(lab: Node) -> Dictionary:
	return {"player":lab.player.get_instance_id(),"authority":lab.scene_policy.action_authority(lab.player.actor_id),
		"definition":lab.scene_policy.definition(),"epoch":lab.combat.encounter_epoch,
		"attacks":lab.combat.attacks.duplicate(true),"projectiles":lab.combat.projectiles.duplicate(true),
		"receipts":lab.combat.receipts.duplicate(true),"action":lab.player.action_kind,
		"cooldown":lab.player.ability_cooldown,"score":lab.score,"state":lab.state,
		"options":lab.options_panel.visible}

func run() -> void:
	for key in ["timka_prime","ryzhik_training","tega_training","pasha_training","unknown"]:
		var probe := CompleteArtProbe.new()
		check("unsupported_even_if_complete_art:"+key,not probe.prepare_fixture(key))
		check("unsupported_rejected_before_art_load:"+key,probe.load_calls.is_empty())
		check("unsupported_cannot_bind_stale_body:"+key,probe.authored_frames==null and probe.prepared_definition.is_empty())
		probe.free()
	for key in ["gabar_training","olezhka_training","timka_present"]:
		var policy := Policy.new()
		check("registered_policy:"+key,policy.open(key))
		var player := Player.new()
		check("real_complete_fixture:"+key,player.prepare_fixture(key) and player.bind_policy(policy))
		var forged := ForgedPolicy.new()
		check("duck_typed_policy_denied:"+key,not player.bind_policy(forged) and player.scene_policy==null)
		check("registered_rebind:"+key,player.bind_policy(policy))
		var original: Dictionary = policy.definition()
		policy._active["context"] = "forged_saved_context"
		check("same_actor_wrong_context_denied:"+key,not player.bind_policy(policy) and player.scene_policy==null)
		policy._active = original.duplicate(true)
		policy._active["scene_id"] = "forged_scene"
		check("same_actor_wrong_fixture_denied:"+key,not player.bind_policy(policy))
		policy.open(key)
		check("good_binding_after_rejection:"+key,player.bind_policy(policy))
		check("failed_reprepare_revokes_cache:"+key,not player.prepare_fixture("unknown") and player.authored_frames==null and player.actor_id.is_empty() and not player.bind_policy(policy))
		check("configure_wrong_identity_denied:"+key,not player.configure("pasha",policy))
		player.free()
	var lab := preload("res://scripts/core/character_lab.gd").new()
	root.add_child(lab)
	current_scene = lab
	lab.auto_retry = false
	lab.process_mode = Node.PROCESS_MODE_DISABLED
	# Preserve actual pending work/receipt, not just a blank arena. Direct Core
	# setup here is not Input, normal-ranged-kit or contact-animation acceptance.
	check("real_pending_action_created",lab.player.use_ability() and not lab.combat.attacks.is_empty())
	lab.combat.fire(lab.player,"player",Vector2.RIGHT,lab.config.attacks.pistol)
	lab.combat._apply_hit(lab.enemies[0],{"damage":0,"stun":0.0,"category":"unarmed"},90001,lab.player)
	check("nonempty_real_projectile_and_once_receipt",not lab.combat.projectiles.is_empty() and not lab.combat.receipts.is_empty())
	lab._set_options_visible(true)
	var before := lab_snapshot(lab)
	for key in ["timka_prime","ryzhik_training","tega_training","pasha_training","unknown"]:
		check("live_unsupported_selection_refused:"+key,not lab.select_fixture(key))
		check("refusal_preserves_actor_authority_jobs_receipts_options:"+key,lab_snapshot(lab)==before)
	var old_player: Node = lab.player
	check("supported_Oleg_replaces_actual_Gabar",lab.select_fixture("olezhka_training"))
	check("new_actor_bound_to_exact_registered_context",lab.player!=old_player and lab.player.actor_id=="olezhka" and lab.player.scene_policy==lab.scene_policy and lab.scene_policy.ability_id()=="training_counter")
	check("successful_transition_revokes_old_jobs_and_receipts",lab.combat.encounter_epoch>before.epoch and lab.combat.attacks.is_empty() and lab.combat.projectiles.is_empty() and lab.combat.receipts.is_empty())
	check("successful_transition_closes_options",not lab.options_panel.visible)
	check("live_reprepare_refused_without_mutation",not lab.player.prepare_fixture("gabar_training") and lab.player.actor_id=="olezhka" and lab.player.scene_policy==lab.scene_policy)
	lab.player.use_ability()
	check("supported_present_replaces_Oleg_without_prime_grant",lab.select_fixture("timka_present") and lab.player.actor_id=="timka" and lab.scene_policy.ability_id()=="disengage" and not lab.player.can_use_finisher("unarmed"))
	check("present_transition_revokes_old_jobs",lab.combat.attacks.is_empty() and lab.combat.finishers.is_empty())
	check("supported_return_to_Gabar",lab.select_fixture("gabar_training") and lab.player.actor_id=="gabar" and lab.scene_policy.ability_id()=="gabar_lunge")
	root.remove_child(lab)
	lab.queue_free()
	await process_frame
	var passed := checks.all(func(item: Dictionary):return item.passed)
	var output := OS.get_environment("AYAY_P06_READINESS_OUTPUT")
	if not output.is_empty():
		DirAccess.make_dir_recursive_absolute(output)
		var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema":1,"scope":"READINESS_AND_ATOMIC_REFUSAL_ONLY","phase_approval":false,"passed":passed,"checks":checks},"  "))
		file.close()
	print("RESULT P06_READINESS passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
