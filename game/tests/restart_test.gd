extends SceneTree
## Ten actual lethal hits, cached auto-retries, complete deterministic snapshots and native escape.
var passed := 0
var failed := 0
var lab: Node2D
var snapshots_equal := true


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
	for index in count:
		await physics_frame


func _run() -> void:
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	lab.player.set_physics_process(true)
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
	lab.reset_encounter()
	var baseline: Dictionary = lab.snapshot()
	for cycle in 10:
		lab.set_kit("training")
		lab.enemies[0].position = Vector2(92, 284)
		lab.player.set_aim(Vector2.RIGHT)
		await _frames(2)
		lab.player.attack_melee()
		await _frames(12)
		_check(lab.kills == 1, "cycle %d real training kill contaminates encounter" % cycle)
		lab.enemies[0].set_physics_process(true)
		await _frames(13)
		lab.enemies[0].set_physics_process(false)
		_check(not lab.enemies[0].sprite.visible and lab.enemies[0].defeat_visual.visible,
			"cycle %d taints defeat timer, sprite visibility and cue before reset" % cycle)
		lab.player.set_aim(Vector2.UP)
		lab.player.attack_ranged()
		lab.player.distract()
		lab.rng.randi()
		lab.score = 73
		lab.enemies[1].position = Vector2(84, 284)
		await _frames(2)
		lab.combat.start_melee(lab.enemies[1], "enemy", Vector2.LEFT, lab.config.attacks.enemy_melee)
		await _frames(2)
		_check(lab.state == "dead" and lab.player.health == 0 and lab.player.hits_received == 1,
			"cycle %d actual physics damage causes death" % cycle)
		_check(lab.player.sprite.animation.begins_with("fall_"), "cycle %d death plays authored fall animation" % cycle)
		var wait_frames := 0
		while lab.state == "dead" and wait_frames < 60:
			await _frames(1)
			wait_frames += 1
		var restored: Dictionary = lab.snapshot()
		var equal := restored == baseline
		snapshots_equal = snapshots_equal and equal
		if not equal:
			for key in baseline:
				if restored[key] != baseline[key]:
					print("SNAPSHOT DIFF ", key, " baseline=", baseline[key], " restored=", restored[key])
		_check(equal, "cycle %d restores complete snapshot including seed/timers/bullets/stuns/score" % cycle)
		_check(wait_frames <= 17 and lab.state == "playing", "cycle %d returns control after 250ms physics timer" % cycle)
	var max_latency := 0.0
	for latency in lab.restart_latencies_ms:
		max_latency = maxf(max_latency, latency)
	_check(lab.total_deaths == 10 and lab.restart_latencies_ms.size() == 10, "all ten actual deaths and retries measured")
	_check(max_latency < 1000.0, "cached death-to-control latency below one second")
	lab.auto_retry = false
	lab.player.set_physics_process(true)
	for enemy in lab.enemies:
		enemy.set_physics_process(true)
	lab.reset_encounter()
	var initial: Vector2 = lab.player.position
	lab.player.set_aim(Vector2.UP)
	Input.action_press("move_right")
	await _frames(30)
	Input.action_press("distract")
	await _frames(2)
	Input.action_release("distract")
	var route_frames := 32
	while lab.state == "playing" and route_frames < 480:
		await _frames(1)
		route_frames += 1
	Input.action_release("move_right")
	_check(lab.state == "escaped", "native input route enters real exit area")
	_check(lab.kills == 0 and lab.shots_fired == 0 and lab.player.kit == "escape", "weak kit escapes with no kills or firearm")
	_check(lab.player.position.distance_to(initial) > 520 and route_frames > 360, "route uses actual 82px/s movement over arena")
	var detections := 0
	var pursuing := 0
	var investigating := 0
	for enemy in lab.enemies:
		detections += enemy.detection_count
		pursuing += 1 if "pursue" in enemy.transitions else 0
		investigating += 1 if "investigate" in enemy.transitions else 0
	_check(detections > 0 and pursuing > 0, "escape opponents detect and pursue rather than sleep")
	_check(investigating > 0, "native E input causes active investigation")
	_check(lab.score == 1000, "escape score rewards nonlethal objective")
	var result := {"passed": failed == 0, "assertions": passed, "failed": failed,
		"restart": {"deaths": lab.total_deaths, "max_latency_ms": max_latency, "snapshots_equal": snapshots_equal},
		"escape": {"cleared": lab.state == "escaped", "kills": lab.kills, "frames": route_frames,
			"detections": detections, "pursuing": pursuing, "real_input": true}}
	var output := OS.get_environment("AYAY_RESTART_RESULT_PATH")
	if not output.is_empty():
		var file := FileAccess.open(output, FileAccess.WRITE)
		file.store_string(JSON.stringify(result, "  "))
	print("RESTART_RESULT ", JSON.stringify(result))
	print("RESULT passed=%d failed=%d" % [passed, failed])
	quit(1 if failed else 0)
