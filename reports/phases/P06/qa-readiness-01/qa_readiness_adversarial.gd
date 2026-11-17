extends SceneTree
## Independent QA probes. This script exists only in ROOT reports isolated copy.
const Player = preload("res://scripts/actors/character_player.gd")
const Policy = preload("res://scripts/systems/character_scene_policy.gd")
var checks: Array[Dictionary] = []

class SwitchableArtProbe:
	extends "res://scripts/actors/character_player.gd"
	var fail_load := false
	func _load_combat_frames(_id: String) -> SpriteFrames:
		return null if fail_load else CharacterFrames.combat_frames("gabar")

class MissingSocketProbe:
	extends "res://scripts/actors/character_player.gd"
	func _load_combat_frames(_id: String) -> SpriteFrames:
		var frames := CharacterFrames.combat_frames("gabar")
		frames.get_frame_texture(&"idle_down",0).remove_meta("clothing_socket")
		return frames

class ForgedAbilityPolicy:
	extends "res://scripts/systems/character_scene_policy.gd"
	func ability_id() -> String:
		return "unimplemented_fake_ability"

func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL QA_READINESS "+label)
func snapshot(lab: Node) -> Dictionary:
	return {"player":lab.player.get_instance_id(),"definition":lab.scene_policy.definition(),
		"authority":lab.scene_policy.action_authority(lab.player.actor_id),"epoch":lab.combat.encounter_epoch,
		"attacks":lab.combat.attacks.duplicate(true),"projectiles":lab.combat.projectiles.duplicate(true),
		"receipts":lab.combat.receipts.duplicate(true),"options":lab.options_panel.visible,
		"action":lab.player.action_kind,"cooldown":lab.player.ability_cooldown,"state":lab.state,"score":lab.score}
func run() -> void:
	var policy := Policy.new()
	check("registered_gabar_policy",policy.open("gabar_training"))
	var player := Player.new()
	check("actual_gabar_prepared_and_bound",player.prepare_fixture("gabar_training") and player.bind_policy(policy))
	var forged_ability := ForgedAbilityPolicy.new()
	check("subclass_policy_has_exact_registered_definition",forged_ability.open("gabar_training") and forged_ability.definition()==policy.definition())
	check("subclass_forged_ability_refused",not player.bind_policy(forged_ability) and player.scene_policy==null)
	check("good_policy_can_rebind_after_forged_ability",player.bind_policy(policy))
	# Both mutable public caches match each other. Trusted registry comparison
	# must still reject this forged scene/context rather than trusting equality.
	policy._active["context"] = "forged_saved_context"
	player.prepared_definition["context"] = "forged_saved_context"
	check("matching_forged_context_cache_refused",not player.bind_policy(policy) and player.scene_policy==null)
	policy.open("gabar_training")
	check("new_registered_preparation_restores_after_forged_cache",player.prepare_fixture("gabar_training") and player.bind_policy(policy))
	var oleg_policy := Policy.new()
	oleg_policy.open("olezhka_training")
	check("actual_other_actor_policy_refused",not player.bind_policy(oleg_policy) and player.scene_policy==null)
	player.free()
	var art_probe := SwitchableArtProbe.new()
	check("supported_complete_art_probe_prepares",art_probe.prepare_fixture("gabar_training"))
	art_probe.fail_load = true
	check("supported_null_art_reprepare_refused",not art_probe.prepare_fixture("gabar_training"))
	check("null_art_clears_all_preparation_and_binding",art_probe.actor_id.is_empty() and art_probe.authored_frames==null and art_probe.scene_policy==null and art_probe.prepared_definition.is_empty() and art_probe.prepared_ability.is_empty() and not art_probe.bind_policy(policy))
	art_probe.free()
	var sockets := MissingSocketProbe.new()
	check("supported_art_one_missing_socket_refused",not sockets.prepare_fixture("gabar_training") and sockets.authored_frames==null and sockets.actor_id.is_empty())
	sockets.free()
	var lab := preload("res://scripts/core/character_lab.gd").new()
	root.add_child(lab)
	current_scene = lab
	lab.auto_retry = false
	lab.process_mode = Node.PROCESS_MODE_DISABLED
	check("actual_lab_gabar_pending_action",lab.player.actor_id=="gabar" and lab.player.use_ability() and not lab.combat.attacks.is_empty())
	lab.combat.fire(lab.player,"player",Vector2.RIGHT,lab.config.attacks.pistol)
	lab.combat._apply_hit(lab.enemies[0],{"damage":0,"stun":0.0,"category":"unarmed"},99123,lab.player)
	lab._set_options_visible(true)
	var before := snapshot(lab)
	check("lab_pending_projectile_receipt_options",not lab.combat.projectiles.is_empty() and not lab.combat.receipts.is_empty() and lab.options_panel.visible)
	var metadata := ProjectSettings.globalize_path("res://assets/art/characters/olezhka/action.json")
	var hidden := metadata+".qa-withheld"
	var original_sha := FileAccess.get_sha256(metadata)
	check("supported_real_metadata_withheld_only_in_ROOT_copy",not FileAccess.file_exists(hidden) and DirAccess.rename_absolute(metadata,hidden)==OK)
	check("actual_supported_missing_art_selection_refused",not lab.select_fixture("olezhka_training"))
	check("missing_art_refusal_is_atomic",snapshot(lab)==before)
	check("actual_missing_metadata_restored",DirAccess.rename_absolute(hidden,metadata)==OK and FileAccess.get_sha256(metadata)==original_sha)
	check("supported_fixture_works_after_exact_metadata_restore",lab.select_fixture("olezhka_training") and lab.player.actor_id=="olezhka")
	var bound: RefCounted = lab.player.scene_policy
	check("live_rebind_denied_without_authority_change",not lab.player.bind_policy(policy) and lab.player.scene_policy==bound)
	check("live_configure_wrong_actor_denied_without_authority_change",not lab.player.configure("gabar",policy) and lab.player.actor_id=="olezhka" and lab.player.scene_policy==bound)
	root.remove_child(lab)
	lab.queue_free()
	await process_frame
	var passed := checks.all(func(item: Dictionary):return item.passed)
	var output := OS.get_environment("AYAY_QA_READINESS_OUTPUT")
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"INDEPENDENT_READINESS_ADVERSARIAL_ONLY","phase_approval":false,"passed":passed,"checks":checks},"  "))
	file.close()
	print("RESULT QA_READINESS passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
