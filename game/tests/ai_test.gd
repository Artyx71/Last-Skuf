extends SceneTree
## Test visible reaction and committed warnings against actual world collision.
var passed := 0
var failed := 0
var lab: Node2D


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


func _fixture(index: int) -> CharacterBody2D:
	lab.reset_encounter()
	lab.auto_retry = false
	lab.player.set_physics_process(true)
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(500, 90)
	var enemy: CharacterBody2D = lab.enemies[index]
	enemy.position = Vector2(190, 284)
	enemy.patrol_target = Vector2(220, 284)
	lab.player.position = Vector2(60, 284)
	await _frames(2)
	return enemy


func _run() -> void:
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	for index in 3:
		var enemy: CharacterBody2D = await _fixture(index)
		_check(enemy.sees_player(), enemy.kind + " sees actual visible player")
		enemy.set_physics_process(true)
		await _frames(2)
		_check(enemy.state == "alert", enemy.kind + " visible reaction precedes pursuit")
		await _frames(6)
		_check(enemy.state == "alert", enemy.kind + " reaction is not instantaneous")
		await _frames(16)
		_check("pursue" in enemy.transitions, enemy.kind + " alert enters pursuit")
		if index != 2:
			_check(enemy.position.x < 190, enemy.kind + " pursuit physically closes distance")
		else:
			_check(enemy.state == "telegraph", "shooter warns at ranged distance")
		_check(lab.player.health == 1, enemy.kind + " cannot damage during reaction")
	var occluded: CharacterBody2D = await _fixture(0)
	occluded.position = Vector2(200, 130)
	occluded.patrol_target = Vector2(260, 130)
	lab.player.position = Vector2(200, 200)
	await _frames(2)
	_check(not occluded.sees_player(), "wall prevents AI detection")
	occluded.set_physics_process(true)
	await _frames(15)
	_check(occluded.state == "patrol" and occluded.detection_count == 0, "occluded player does not aggro patrol")
	_check(occluded.position.x > 200, "patrol moves while player remains occluded")
	var rusher: CharacterBody2D = await _fixture(1)
	rusher.position = Vector2(84, 284)
	await _frames(2)
	rusher.set_physics_process(true)
	await _frames(24)
	_check(rusher.state == "telegraph", "rusher commits visible melee warning")
	var warning_start: float = rusher.timer
	_check(warning_start > 0.4 and lab.player.health == 1, "rusher warning leaves reaction window")
	await _frames(12)
	_check(lab.player.health == 1 and lab.combat.attacks.is_empty(), "warning is not a hidden live hitbox")
	# Native movement avoids a locked attack; no teleport to dodge.
	lab.player.set_physics_process(true)
	Input.action_press("move_left")
	await _frames(12)
	Input.action_release("move_left")
	await _frames(20)
	_check(lab.player.health == 1 and "recover" in rusher.transitions, "leaving committed melee volume avoids lethal hit")
	var lethal: CharacterBody2D = await _fixture(1)
	lethal.position = Vector2(84, 284)
	await _frames(2)
	lethal.set_physics_process(true)
	await _frames(80)
	_check(lab.state == "dead" and lab.player.health == 0, "rusher telegraph resolves to real lethal damage")
	_check(lab.player.hits_received == 1, "lethal damage cannot repeat on dead player")
	var shooter: CharacterBody2D = await _fixture(2)
	shooter.set_physics_process(true)
	await _frames(30)
	_check(shooter.state == "telegraph" and lab.combat.projectiles.is_empty(), "shooter telegraph precedes bullet creation")
	await _frames(90)
	_check(lab.state == "dead" and lab.player.hits_received == 1, "shooter projectile reaches actual player physics body")
	var behind_wall: CharacterBody2D = await _fixture(2)
	behind_wall.position = Vector2(200, 130)
	lab.player.position = Vector2(200, 210)
	behind_wall.locked_aim = Vector2.DOWN
	behind_wall.transition("telegraph", 0.1)
	await _frames(2)
	behind_wall.set_physics_process(true)
	await _frames(40)
	_check(lab.player.health == 1 and lab.combat.wall_impacts == 1, "wall blocks even an already-committed enemy shot")
	var distracted: CharacterBody2D = await _fixture(1)
	distracted.set_physics_process(true)
	await _frames(20)
	lab.make_noise(Vector2(190, 220))
	var before: Vector2 = distracted.position
	await _frames(20)
	_check(distracted.state == "investigate" and distracted.position.y < before.y, "distraction diverts active rusher to real noise")
	await _frames(140)
	_check("alert" in distracted.transitions and distracted.investigate_remaining == 0, "finite distraction returns to detection loop")
	print("RESULT passed=%d failed=%d" % [passed, failed])
	quit(1 if failed else 0)
