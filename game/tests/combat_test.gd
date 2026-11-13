extends SceneTree
## Collision integration: actual physics shapes, wall rays and continuous bullet sweeps.
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


func _fixture() -> void:
	lab.reset_encounter()
	lab.auto_retry = false
	lab.set_kit("training")
	lab.player.set_physics_process(true)
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(500, 90)
	lab.player.position = Vector2(60, 284)
	lab.enemies[0].position = Vector2(92, 284)
	lab.player.set_aim(Vector2.RIGHT)
	await _frames(2)


func _run() -> void:
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	_check(lab.player.actions_ready, "actual P02 shove/hit/fall sheet loaded")
	for enemy in lab.enemies:
		_check(enemy.z_index == lab.player.z_index and enemy.z_index > 0,
			"shared actor body plane preserves actor order and rear weapon visibility " + enemy.kind)
	for direction in ["down", "left", "right", "up"]:
		_check(lab.player.sprite.sprite_frames.get_frame_count(StringName("fall_" + direction)) == 3,
			"three real fall frames " + direction)
	await _fixture()
	lab.enemies[0].health = 3
	_check(lab.player.attack_melee(), "native melee begins")
	_check(not lab.player.attack_melee(), "cooldown rejects repeated attack")
	await _frames(12)
	_check(lab.enemies[0].hits_received == 1, "persistent volume hits target once per attack")
	_check(lab.enemies[0].health == 2 and lab.combat.damage_events == 1, "one damage event rather than every physics tick")
	await _frames(10)
	_check(lab.combat.attacks.is_empty(), "melee hitbox expires after authored contact window")
	await _fixture()
	lab.player.set_aim(Vector2.LEFT)
	lab.player.attack_melee()
	await _frames(12)
	_check(lab.enemies[0].hits_received == 0, "melee wrong-facing miss")
	await _fixture()
	lab.enemies[0].position = Vector2(130, 284)
	await _frames(2)
	lab.player.attack_melee()
	await _frames(12)
	_check(lab.enemies[0].hits_received == 0, "melee out-of-range miss")
	await _fixture()
	lab.player.position = Vector2(200, 188)
	lab.enemies[0].position = Vector2(200, 153)
	lab.player.set_aim(Vector2.UP)
	await _frames(2)
	lab.player.attack_melee()
	await _frames(12)
	_check(lab.enemies[0].hits_received == 0, "wall occludes overlapping melee volume")
	_check(not lab.combat.clear_line(Vector2(200, 180), Vector2(200, 150)), "native physics LOS blocked by wall")
	await _fixture()
	lab.enemies[0].position = Vector2(224, 284)
	await _frames(2)
	_check(lab.player.attack_ranged(), "training firearm enabled")
	await _frames(30)
	_check(lab.enemies[0].hits_received == 1 and lab.enemies[0].health == 0, "swept projectile hits and kills")
	_check(lab.kills == 1 and lab.shots_fired == 1, "actual damage updates kill and shot counters")
	_check(lab.combat.projectiles.is_empty(), "projectile consumed at first target")
	await _fixture()
	lab.enemies[0].position = Vector2(70, 284)
	await _frames(2)
	lab.player.attack_ranged()
	await _frames(2)
	_check(lab.enemies[0].hits_received == 1, "point-blank target before muzzle still receives swept hit")
	await _fixture()
	lab.player.position = Vector2(200, 218)
	lab.enemies[0].position = Vector2(200, 118)
	lab.player.set_aim(Vector2.UP)
	await _frames(2)
	lab.player.attack_ranged()
	await _frames(30)
	_check(lab.enemies[0].hits_received == 0 and lab.combat.wall_impacts == 1, "wall stops ranged damage")
	await _fixture()
	lab.player.position = Vector2(200, 188)
	lab.enemies[0].position = Vector2(200, 130)
	lab.player.set_aim(Vector2.UP)
	await _frames(2)
	lab.player.attack_ranged()
	await _frames(30)
	_check(lab.enemies[0].hits_received == 0 and lab.combat.wall_impacts == 1,
		"muzzle against a wall cannot spawn a bullet through it")
	await _fixture()
	lab.enemies[0].position = Vector2(224, 284)
	await _frames(2)
	var fast: Dictionary = lab.config.attacks.pistol.duplicate()
	fast.speed = 20000.0
	lab.combat.fire(lab.player, "player", Vector2.RIGHT, fast)
	await _frames(2)
	_check(lab.enemies[0].hits_received == 1, "continuous sweep catches target crossed in a single tick")
	await _fixture()
	lab.enemies[0].position = Vector2(224, 284)
	lab.player.set_aim(Vector2.UP)
	lab.player.attack_ranged()
	await _frames(90)
	_check(lab.enemies[0].hits_received == 0, "ranged aim miss")
	_check(lab.combat.projectiles.is_empty(), "missed bullets expire or hit world")
	await _fixture()
	lab.set_kit("escape")
	_check(lab.player.move_speed == 82, "weak Yakuza retains approved 82px/s speed")
	_check(not lab.player.attack_ranged() and lab.shots_fired == 0, "escape kit cannot fire a gun")
	lab.player.attack_melee()
	await _frames(12)
	_check(lab.enemies[0].health == 1 and lab.kills == 0, "improvised shove is nonlethal")
	_check(lab.enemies[0].stun_remaining > 0 and lab.enemies[0].state == "stunned", "shove buys escape time through stun")
	_check(lab.player.distract(), "noise ability available")
	_check(not lab.player.distract(), "noise ability has finite cooldown")
	_check(lab.noise_remaining > 0 and lab.enemies[0].state == "investigate", "noise changes real enemy intent")
	await _fixture()
	lab.player.set_physics_process(true)
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	await _frames(10)
	_check(lab.enemies[0].hits_received == 1, "actual Input action invokes melee controller")
	_check(lab.player.sprite.animation == &"shove_right" and lab.player.sprite.frame >= 1,
		"native shove animation advances over responsive movement controller")
	lab.player.clear_aim()
	lab.player.facing = &"up"
	_check(lab.player.aim_direction() == Vector2.UP, "keyboard-only aim falls back to facing")
	lab.player.set_aim(Vector2(1, 1))
	_check(is_equal_approx(lab.player.aim_direction().length(), 1), "explicit replay aim is normalized")
	await _fixture()
	lab.enemies[0].set_physics_process(true)
	lab.player.attack_melee()
	await _frames(8)
	_check(lab.enemies[0].health == 0 and lab.enemies[0].defeat_visual.visible,
		"actual defeat produces explicit front-layer cross cue")
	_check(lab.enemies[0].sprite.modulate.a < 1 and lab.enemies[0].defeat_elapsed > 0,
		"defeated standing art fades immediately rather than posing as a corpse")
	await _frames(12)
	_check(not lab.enemies[0].sprite.visible and lab.enemies[0].defeat_visual.visible,
		"standing guard disappears within .18 seconds while defeat cue remains")
	await _frames(35)
	_check(not lab.enemies[0].defeat_visual.visible, "defeat cue expires deterministically")
	lab.enemies[0].set_physics_process(false)
	lab.reset_encounter()
	_check(lab.enemies[0].sprite.visible and lab.enemies[0].sprite.modulate.a == 1
		and lab.enemies[0].defeat_elapsed == 0 and not lab.enemies[0].defeat_visual.visible,
		"restart restores visible live art and clears all defeat presentation state")
	print("RESULT passed=%d failed=%d" % [passed, failed])
	quit(1 if failed else 0)
