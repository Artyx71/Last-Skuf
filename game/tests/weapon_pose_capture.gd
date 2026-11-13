extends SceneTree
## Actual-draw evidence fixture; no alternate combat or altered P01 artwork.
var lab: Node2D


func _initialize() -> void:
	call_deferred("_run")


func _frames(count: int) -> void:
	for tick in count:
		await physics_frame


func _run() -> void:
	var output := OS.get_environment("AYAY_WEAPON_CAPTURE_DIR")
	if output.is_empty():
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	var rows: Array[Dictionary] = []
	var directions := {"down": Vector2.DOWN, "left": Vector2.LEFT, "right": Vector2.RIGHT, "up": Vector2.UP}
	for weapon in ["melee", "ranged"]:
		for direction in directions:
			lab.reset_encounter()
			lab.gallery_mode = true
			lab.set_kit("training")
			lab.player.position = Vector2(310, 260)
			lab.player.set_aim(directions[direction])
			for enemy in lab.enemies:
				enemy.set_physics_process(false)
				enemy.position = Vector2(540, 100)
			await _frames(2)
			var action := "attack_melee" if weapon == "melee" else "attack_ranged"
			Input.action_press(action)
			await _frames(2)
			Input.action_release(action)
			var ticks := 0
			while weapon == "melee" and lab.player.action_frame != 1 and ticks < 20:
				await _frames(1)
				ticks += 1
			await RenderingServer.frame_post_draw
			var filename: String = weapon + "_" + direction + ".png"
			var code := root.get_texture().get_image().save_png(output.path_join(filename))
			var hand: Vector2 = lab.player.weapon_socket()
			var muzzle: Vector2 = lab.player.visual_muzzle()
			rows.append({"weapon": weapon, "direction": direction, "animation": String(lab.player.sprite.animation),
				"frame": lab.player.sprite.frame, "hand_local": [hand.x, hand.y], "muzzle_global": [muzzle.x, muzzle.y],
				"layer": lab.player.weapon_visual.z_index, "player_body_z": lab.player.z_index,
				"enemy_body_z": lab.enemies[0].z_index, "saved": code == OK, "file": filename,
				"projectile_visual_offsets": lab.combat.projectiles.map(func(bullet): return [bullet.visual_offset.x, bullet.visual_offset.y])})
			await _frames(22)
	# Separate actual defeat presentation samples from native melee, with AI/timers enabled.
	for enemy in lab.enemies:
		enemy.set_physics_process(true)
	lab.training_fixture()
	await _frames(2)
	Input.action_press("attack_melee")
	await _frames(2)
	Input.action_release("attack_melee")
	await _frames(7)
	var defeat_rows: Array[Dictionary] = []
	for sample in [{"name": "defeat_fade", "wait": 0}, {"name": "defeat_cue", "wait": 12}, {"name": "defeat_cleared", "wait": 40}]:
		await _frames(sample.wait)
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(output.path_join(sample.name + ".png"))
		defeat_rows.append({"file": sample.name + ".png", "snapshot": lab.snapshot()})
	lab.reset_encounter()
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
	lab.player.position = Vector2(80, 75)
	await _frames(2)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output.path_join("hud_upper_edge.png"))
	var file := FileAccess.open(output.path_join("weapon_captures.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema": 1, "real_draw": true, "real_input": true, "captures": rows, "defeat": defeat_rows}, "  "))
	quit(0)
