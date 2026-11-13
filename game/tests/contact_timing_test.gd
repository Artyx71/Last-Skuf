extends SceneTree
## Native input regression for CMB-P02-01. Observe the presented pose after physics damage.
var passed := 0
var failed := 0
var lab: Node2D
var evidence: Array[Dictionary] = []


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, title: String) -> void:
	if condition:
		passed += 1
		print("PASS ", title)
	else:
		failed += 1
		push_error("FAIL " + title)


func _frames(count: int) -> void:
	for tick in count:
		await physics_frame


func _fixture(kit := "training", direction := Vector2.RIGHT) -> void:
	Input.action_release("attack_melee")
	Input.action_release("move_left")
	Input.action_release("move_down")
	lab.reset_encounter()
	lab.auto_retry = false
	lab.set_kit(kit)
	lab.player.position = Vector2(250, 260)
	lab.player.set_aim(direction)
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(500, 90)
	lab.enemies[0].position = lab.player.position + direction * 30
	lab.enemies[0].health = 3
	await _frames(2)


func _run() -> void:
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	for kit in ["escape", "training"]:
		for direction in [Vector2.DOWN, Vector2.LEFT, Vector2.RIGHT, Vector2.UP]:
			await _fixture(kit, direction)
			var rows: Array[Dictionary] = []
			var first_hit_frame := -1
			var early := false
			var saw_windup := false
			var saw_contact := false
			var recovered_hits := -1
			var contact_ticks := 0
			Input.action_press("attack_melee")
			for tick in 20:
				await physics_frame
				await process_frame
				var frame: int = lab.player.sprite.frame
				var animation: String = String(lab.player.sprite.animation)
				var hits: int = lab.enemies[0].hits_received
				if animation.begins_with("shove_"):
					if frame == 0:
						saw_windup = true
						early = early or hits > 0
					if frame == 1:
						saw_contact = true
						contact_ticks += 1
					if hits > 0 and first_hit_frame < 0:
						first_hit_frame = frame
					if frame == 2 and recovered_hits < 0:
						recovered_hits = hits
				rows.append({"tick": tick, "animation": animation, "frame": frame,
					"elapsed": lab.player.action_elapsed, "hits": hits,
					"health": lab.enemies[0].health, "stun": lab.enemies[0].stun_remaining})
				if tick == 1:
					Input.action_release("attack_melee")
			var title: String = kit + " " + str(direction)
			_check(saw_windup and not early, title + " frame0 wind-up has no damage or stun")
			_check(saw_contact and first_hit_frame == 1, title + " first actual hit coincides with authored contact1")
			_check(lab.enemies[0].hits_received == 1 and recovered_hits == 1, title + " recovery adds no second hit")
			var definition: Dictionary = lab.config.attacks["shove" if kit == "escape" else "knife"]
			_check(contact_ticks >= ceili(float(definition.active) * 60), title + " preserves full .14/.16 second contact window")
			_check(lab.enemies[0].health == (3 if kit == "escape" else 2), title + " correct nonlethal/lethal damage amount")
			evidence.append({"kit": kit, "direction": [direction.x, direction.y], "rows": rows})
	await _fixture()
	# Target starts in range but walks out during wind-up. An immediate hidden volume would hit.
	lab.enemies[0].position = lab.player.position + Vector2(45, 0)
	await _frames(2)
	lab.enemies[0].set_physics_process(true)
	lab.enemies[0].hear_noise(Vector2(400, 260))
	Input.action_press("attack_melee")
	await _frames(20)
	Input.action_release("attack_melee")
	_check(lab.enemies[0].hits_received == 0, "target escaping during wind-up is not hit by an early volume")
	await _fixture()
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	lab.reset_encounter()
	await _frames(15)
	_check(lab.combat.attacks.is_empty() and lab.kills == 0 and lab.combat.damage_events == 0,
		"restart during wind-up cancels pending contact")
	await _fixture()
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	lab.enemies[1].position = lab.player.position + Vector2(24, 0)
	await _frames(1)
	lab.combat.start_melee(lab.enemies[1], "enemy", Vector2.LEFT, lab.config.attacks.enemy_melee)
	await _frames(2)
	var player_pending := false
	for attack in lab.combat.attacks:
		player_pending = player_pending or attack.source == lab.player
	_check(lab.state == "dead" and lab.enemies[0].hits_received == 0 and not player_pending,
		"actual player death cancels pending melee before contact")
	await _fixture()
	var pending: Dictionary = lab.config.attacks.enemy_melee.duplicate()
	pending.windup = 0.2
	lab.enemies[0].position = lab.player.position + Vector2(24, 0)
	await _frames(2)
	lab.combat.start_melee(lab.enemies[0], "enemy", Vector2.LEFT, pending)
	lab.enemies[0].health = 1
	lab.player.attack_ranged()
	await _frames(24)
	_check(lab.enemies[0].health == 0 and lab.player.health == 1 and lab.combat.attacks.is_empty(),
		"actual enemy death cancels its pending attack")
	await _fixture()
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	lab.enemies[0].health = 1
	lab.combat.fire(lab.player, "player", Vector2.RIGHT, lab.config.attacks.pistol)
	await _frames(18)
	_check(lab.enemies[0].health == 0 and lab.enemies[0].hits_received == 1 and lab.kills == 1,
		"already defeated target receives no later contact damage")
	await _fixture()
	lab.enemies[0].position = Vector2(350, 260)
	await _frames(2)
	Input.action_press("attack_melee")
	var late_wait := 0
	while (lab.player.action_kind != "shove" or lab.player.action_elapsed < 0.183) and late_wait < 30:
		await _frames(1)
		late_wait += 1
	Input.action_release("attack_melee")
	lab.enemies[0].position = Vector2(280, 260)
	await _frames(2)
	_check(lab.player.action_frame == 1 and lab.enemies[0].hits_received == 1,
		"target entering late in original .16 second active window still receives actual contact")
	await _fixture()
	lab.enemies[0].position = Vector2(350, 260)
	await _frames(2)
	Input.action_press("attack_melee")
	var recovery_wait := 0
	while (lab.player.action_kind != "shove" or lab.player.action_frame != 2) and recovery_wait < 30:
		await _frames(1)
		recovery_wait += 1
	Input.action_release("attack_melee")
	lab.enemies[0].position = Vector2(280, 260)
	await _frames(4)
	_check(lab.enemies[0].hits_received == 0, "new target entering recovery frame2 cannot receive damage")
	# Locked action pose must keep its socket when movement changes current facing.
	await _fixture()
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	Input.action_press("move_down")
	await _frames(4)
	_check(lab.player.facing == &"down" and lab.player.action_direction == "right"
		and lab.player.sprite.animation == &"shove_right", "movement cannot rotate a locked action socket")
	Input.action_release("move_down")
	var result := {"passed": failed == 0, "assertions": passed, "failed": failed, "samples": evidence}
	var output := OS.get_environment("AYAY_TIMING_RESULT")
	if not output.is_empty():
		var file := FileAccess.open(output, FileAccess.WRITE)
		file.store_string(JSON.stringify(result, "  "))
	print("RESULT passed=%d failed=%d" % [passed, failed])
	quit(1 if failed else 0)
