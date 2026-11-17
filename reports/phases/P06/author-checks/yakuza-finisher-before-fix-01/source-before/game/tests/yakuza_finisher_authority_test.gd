extends SceneTree
## Actual Input earned shove stun in CH01/training. No direct stun/health grant.
## Fixture placement and disabled OTHER threats are not a campaign playthrough.
var checks: Array[Dictionary] = []
var observations: Array[Dictionary] = []

func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL YAKUZA_FINISHER_AUTHORITY "+label)
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func tap(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode=code;event.physical_keycode=code;event.pressed=true
	Input.parse_input_event(event)
	await frames(1)
	event=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=false
	Input.parse_input_event(event)
	await frames(1)
func earned_stun(lab: Node, at: Vector2) -> Node:
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
	lab.player.position=at
	lab.player.set_aim(Vector2.RIGHT)
	var target: Node=lab.enemies[0]
	target.position=at+Vector2.RIGHT*24
	target.set_physics_process(true)
	await frames(2)
	await tap(KEY_SPACE)
	for i in 18:
		if target.state=="stunned": break
		await frames(1)
	check("Input_shove_earns_real_Core_stun:"+str(at),target.state=="stunned" and target.hits_received==1 and target.health>0 and lab.combat.damage_events==1 and lab.combat.contact_events[0].damage==0)
	return target
func reservation_snapshot(lab: Node) -> Dictionary:
	return {"jobs":lab.combat.finishers.duplicate(true),"history":lab.combat.finisher_history.duplicate(true),
		"next_attack_id":lab.combat.next_attack_id,"receipts":lab.combat.receipts.duplicate(true),
		"action":lab.player.action_kind,"action_clock":lab.player.action_elapsed,
		"kills":lab.kills,"score":lab.score}
func run() -> void:
	var mission: Node=load("res://scenes/levels/missed_fight.tscn").instantiate()
	root.add_child(mission);current_scene=mission
	await frames(3)
	mission.director._finish() # Explicit intro fixture, not Input playthrough proof.
	mission.auto_retry=false
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		mission.reset_encounter()
		var target: Node=await earned_stun(mission,Vector2(192,224))
		check("CH01_uses_weak_escape_kit:"+str(reduced),mission.player.kit=="escape" and mission.config_path!="res://resources/combat/prototype.json")
		await tap(KEY_V)
		var granted: bool=not mission.combat.finisher_for(mission.player).is_empty()
		observations.append({"reduced_gore":reduced,"actual_Input_V_started_job":granted,"target_state":target.state,"target_health":target.health,"stun_remaining":target.stun_remaining})
		check("CH01_Input_V_cannot_grant_training_finisher:"+str(reduced),not granted)
		if granted:
			# Cleanup only for pre-fix reproduction, never mask the failed check.
			mission.combat.cancel_finisher(mission.player,"negative_test_cleanup",true)
			mission.player.cancel_action()
		for category in ["unarmed","blunt","sharp","firearm","environmental"]:
			mission.player.kit="training" # Forged legacy fields cannot grant scene authority.
			mission.player.finisher_category=category
			mission.player.finisher_weapon="unarmed" if category=="environmental" else category
			var before:=reservation_snapshot(mission)
			var started: bool=mission.combat.start_finisher(mission.player,target,category)
			check("CH01_direct_Core_denies_forged_equipment:"+category+":"+str(reduced),not started and reservation_snapshot(mission)==before)
			if started:
				mission.combat.cancel_finisher(mission.player,"negative_test_cleanup",true)
				mission.player.cancel_action()
		mission.player.kit="escape"
		await frames(30)
		check("refused_finishers_do_not_damage_or_reward:"+str(reduced),mission.kills==0 and mission.score==0 and target.health>0 and target.hits_received==1 and mission.combat.finishers.is_empty())
	root.remove_child(mission);mission.queue_free();await frames(2)
	var training:=preload("res://scripts/core/combat_lab.gd").new()
	root.add_child(training);current_scene=training
	training.auto_retry=false
	training.set_kit("escape")
	var target: Node=await earned_stun(training,Vector2(250,260))
	await tap(KEY_V)
	check("explicit_training_keeps_legacy_finisher",not training.combat.finisher_for(training.player).is_empty() and target.state=="finisher_reaction")
	await tap(KEY_C)
	check("training_finisher_remains_interruptible",training.combat.finishers.is_empty() and target.health>0 and training.kills==0 and training.combat.damage_events==1)
	root.remove_child(training);training.queue_free();await frames(2)
	var passed:=checks.all(func(item: Dictionary):return item.passed)
	var output:=OS.get_environment("AYAY_YAKUZA_FINISHER_TEST_OUTPUT")
	if not output.is_empty():
		DirAccess.make_dir_recursive_absolute(output)
		var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema":1,"scope":"ACTUAL_INPUT_EARNED_STUN_FINISHER_SCENE_AUTHORITY_ONLY","phase_approval":false,"passed":passed,"checks":checks,"observations":observations},"  "))
		file.close()
	print("RESULT YAKUZA_FINISHER_AUTHORITY passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
