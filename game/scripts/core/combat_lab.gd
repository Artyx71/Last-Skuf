extends Node2D
## P02 technical encounter: native input, active opponents, deterministic cached retry.

signal audio_event(event_id: StringName, at: Vector2)

const Bindings = preload("res://scripts/core/input_bindings.gd")
const Player = preload("res://scripts/actors/combat_player.gd")
const Enemy = preload("res://scripts/ai/enemy_actor.gd")
const Combat = preload("res://scripts/systems/combat_system.gd")
const CONFIG_PATH := "res://resources/combat/prototype.json"
var config_path := CONFIG_PATH
var config: Dictionary
var visual_config: Dictionary
var player: CharacterBody2D
var enemies: Array[CharacterBody2D] = []
var combat: Node2D
var state := "playing"
var kills := 0
var shots_fired := 0
var score := 0
var elapsed := 0.0
var encounter_ticks := 0
var seed_value := 0
var rng := RandomNumberGenerator.new()
var auto_retry := true
var retry_delay := 0.25
var death_timer := 0.0
var death_started_usec := 0
var total_deaths := 0
var restart_latencies_ms: Array[float] = []
var noise_position := Vector2.ZERO
var noise_remaining := 0.0
var status_label: Label
var kit_label: Label
var hint_label: Label
var gallery_mode := false
var replay_running := false
var baseline_snapshot: Dictionary
var last_reset_snapshot: Dictionary
var escape_detection_count := 0
var equipment_index := 0
var training_bench: Node2D
var equipment_label: Label
var options_panel: Control
var damage_portrait: Sprite2D


func _ready() -> void:
	process_physics_priority = -20
	Bindings.install()
	var audio := get_node_or_null("/root/AudioDirector")
	if audio: audio_event.connect(audio.on_gameplay_audio)
	config = JSON.parse_string(FileAccess.get_file_as_string(config_path))
	visual_config = JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/weapon_visuals.json"))
	assert(config.schema == 1, "P02 combat config schema")
	for bounds in config.walls:
		_add_wall(Rect2(bounds[0], bounds[1], bounds[2], bounds[3]))
	combat = Combat.new()
	combat.lab = self
	add_child(combat)
	player = Player.new()
	player.lab = self
	add_child(player)
	for spawn in config.spawns:
		var enemy := Enemy.new()
		enemy.lab = self
		enemy.kind = spawn.kind
		enemy.definition = config.enemies[spawn.kind]
		enemy.spawn_position = Vector2(spawn.position[0], spawn.position[1])
		enemy.patrol_end = Vector2(spawn.patrol_end[0], spawn.patrol_end[1])
		add_child(enemy)
		enemies.append(enemy)
	_add_label("P02 / БОЕВОЙ ПОЛИГОН · ТЕХНИЧЕСКАЯ ГЕОМЕТРИЯ", Vector2(17, 8), 14, Color("66e5cc"))
	kit_label = _add_label("", Vector2(17, 30), 12, Color("ffcc71"))
	status_label = _add_label("", Vector2(17, 321), 12, Color("d8d6e8"))
	hint_label = _add_label("", Vector2(17, 341), 11, Color("a7a6bd"))
	if config_path == CONFIG_PATH:
		training_bench = Sprite2D.new()
		training_bench.texture = load("res://assets/art/combat_polish/training_bench.png")
		training_bench.position = Vector2(302,270)
		training_bench.z_index = 1
		training_bench.set_meta("finisher_enabled",true)
		add_child(training_bench)
		combat.register_environment("training_bench",training_bench)
		equipment_label = _add_label("",Vector2(17,47),10,Color("edcf82"))
		damage_portrait = Sprite2D.new()
		damage_portrait.texture = load("res://assets/art/combat_polish/yakuza_damage.png")
		damage_portrait.region_enabled = true
		damage_portrait.region_rect = Rect2(0,0,160,160)
		damage_portrait.position = Vector2(530,120)
		damage_portrait.scale = Vector2(0.5,0.5)
		damage_portrait.z_index = 8
		damage_portrait.visible = false
		add_child(damage_portrait)
		_build_polish_options()
	reset_encounter()
	baseline_snapshot = snapshot()
	if "--p04g-replay" in OS.get_cmdline_user_args():
		replay_running = true
		var replay := preload("res://scripts/qa/p04g_replay.gd").new()
		replay.lab = self
		add_child(replay)
	elif "--combat-replay" in OS.get_cmdline_user_args():
		replay_running = true
		call_deferred("_replay")
	elif "--capture-combat" in OS.get_cmdline_user_args():
		call_deferred("_capture_and_quit")


func reset_encounter() -> void:
	if death_started_usec > 0:
		restart_latencies_ms.append(float(Time.get_ticks_usec() - death_started_usec) / 1000.0)
	death_started_usec = 0
	seed_value = int(config.seed)
	rng.seed = seed_value
	state = "playing"
	kills = 0
	shots_fired = 0
	score = 0
	elapsed = 0.0
	encounter_ticks = 0
	death_timer = 0.0
	noise_remaining = 0.0
	noise_position = Vector2.ZERO
	gallery_mode = false
	escape_detection_count = 0
	equipment_index = 0
	combat.reset()
	player.reset(Vector2(config.player_spawn[0], config.player_spawn[1]))
	for enemy in enemies:
		enemy.reset()
	_update_hud()
	queue_redraw()
	last_reset_snapshot = snapshot()
	audio_event.emit(&"retry", Vector2.ZERO)


func set_kit(value: String) -> void:
	assert(value in ["escape", "training"], "Unknown combat kit")
	player.cancel_action()
	player.kit = value
	player.melee_cooldown = 0.0
	player.ranged_cooldown = 0.0
	_update_hud()


func make_noise(point: Vector2) -> void:
	noise_position = point
	noise_remaining = 2.1
	for enemy in enemies:
		enemy.hear_noise(point)


func player_died() -> void:
	if state != "playing":
		return
	state = "dead"
	audio_event.emit(&"death", player.global_position)
	total_deaths += 1
	death_timer = retry_delay
	death_started_usec = Time.get_ticks_usec()
	_update_hud()


func _physics_process(delta: float) -> void:
	if Input.is_action_just_pressed("restart"):
		reset_encounter()
	elif config_path == CONFIG_PATH and Input.is_action_just_pressed("equipment_next") and state == "playing":
		select_equipment((equipment_index + 1) % 5)
	elif config_path == CONFIG_PATH and Input.is_action_just_pressed("polish_options"):
		options_panel.visible = not options_panel.visible
	elif Input.is_action_just_pressed("switch_kit") and state == "playing":
		set_kit("training" if player.kit == "escape" else "escape")
	if state == "dead":
		death_timer = maxf(0, death_timer - delta)
		if auto_retry and death_timer <= 0:
			reset_encounter()
	elif state == "playing":
		elapsed += delta
		encounter_ticks += 1
		noise_remaining = maxf(0.0, noise_remaining - delta)
		if not gallery_mode and _exit_rect().has_point(player.position):
			state = "escaped"
			audio_event.emit(&"state_clear", player.global_position)
			score = 1000 if kills == 0 else 0
			escape_detection_count = 0
			for enemy in enemies:
				escape_detection_count += enemy.detection_count
	_update_hud()
	queue_redraw()


func _update_hud() -> void:
	if not kit_label:
		return
	if damage_portrait:
		damage_portrait.visible = player.hits_received > 0
		damage_portrait.region_rect.position.x = (0 if get_node("/root/OptionsStore").values.reduced_gore else mini(2,player.hits_received)) * 160
	if equipment_label:
		var names := ["Кулаки","Труба","Нож","Пистолет","Верстак"]
		equipment_label.text = "Tab: " + names[equipment_index] + " · F: добивание после толчка · C/WASD: отмена · O: эффекты"
	kit_label.text = String(config.kits[player.kit].label) + (" · ОРУЖЕЙНЫЙ СТЕНД" if gallery_mode else " · ЦЕЛЬ: ВЫХОД БЕЗ УБИЙСТВ")
	hint_label.text = "WASD · Space/ЛКМ: нож · ПКМ: пистолет · F2: уход · R: заново · Esc: меню" if player.kit == "training" else "WASD · E: отвлечь · Space/ЛКМ: толчок · F2: учебный · R: заново · Esc: меню"
	if state == "dead":
		status_label.text = "ПОГИБ · возврат за 250 мс / R · попадание смертельно"
	elif state == "escaped":
		status_label.text = "УШЁЛ · убийств %d · эвакуация %d · R: повторить" % [kills, score]
	else:
		status_label.text = "ЖИВ · убийств %d · выстрелов %d · E %.1fс · %.1fс" % [kills, shots_fired, player.distract_cooldown, elapsed]


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().change_scene_to_file("res://scenes/bootstrap/bootstrap.tscn")


func _exit_rect() -> Rect2:
	var bounds: Array = config.exit
	return Rect2(bounds[0], bounds[1], bounds[2], bounds[3])


func _draw() -> void:
	draw_rect(Rect2(20, 62, 600, 248), Color("151a24"))
	for x in range(20, 621, 16):
		draw_line(Vector2(x, 62), Vector2(x, 310), Color("202a35"))
	for y in range(62, 311, 16):
		draw_line(Vector2(20, y), Vector2(620, y), Color("202a35"))
	if config.is_empty():
		return
	draw_rect(_exit_rect(), Color("245c50"))
	draw_line(Vector2(590, 282), Vector2(608, 282), Color("78f3bf"), 3)
	draw_line(Vector2(602, 276), Vector2(608, 282), Color("78f3bf"), 3)
	draw_line(Vector2(602, 288), Vector2(608, 282), Color("78f3bf"), 3)
	if noise_remaining > 0:
		draw_arc(noise_position, 14 + (2.1 - noise_remaining) * 9, 0, TAU, 24, Color("6ed9eb"), 1.5)
		draw_circle(noise_position, 3, Color("6ed9eb"))
	if state == "dead":
		draw_rect(Rect2(20, 62, 600, 248), Color(0.5, 0.03, 0.12, 0.17))


func _add_wall(bounds: Rect2) -> void:
	var body := StaticBody2D.new()
	body.position = bounds.get_center()
	body.collision_layer = 1
	body.collision_mask = 2 | 4
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = bounds.size
	shape.shape = rectangle
	body.add_child(shape)
	var visual := Polygon2D.new()
	var half := bounds.size / 2
	visual.polygon = PackedVector2Array([-half, Vector2(half.x, -half.y), half, Vector2(-half.x, half.y)])
	visual.color = Color("4c4a62")
	body.add_child(visual)
	add_child(body)


func _add_label(value: String, at: Vector2, size: int, color: Color) -> Label:
	var label := Label.new()
	label.z_index = 10
	label.text = value
	label.position = at
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	add_child(label)
	return label


func _vector(value: Vector2) -> Array:
	return [snappedf(value.x, 0.001), snappedf(value.y, 0.001)]


func snapshot() -> Dictionary:
	var enemy_states: Array[Dictionary] = []
	for enemy in enemies:
		enemy_states.append({"kind": enemy.kind, "position": _vector(enemy.position),
			"velocity": _vector(enemy.velocity), "health": enemy.health, "state": enemy.state,
			"timer": enemy.timer, "stun": enemy.stun_remaining,
			"investigate": enemy.investigate_remaining, "investigate_point": _vector(enemy.investigate_point),
			"target": _vector(enemy.patrol_target), "aim": _vector(enemy.locked_aim), "facing": enemy.facing,
			"detections": enemy.detection_count, "attacks": enemy.attacks_started, "hits": enemy.hits_received,
			"transitions": enemy.transitions.duplicate(), "layer": enemy.collision_layer,
			"animation": String(enemy.sprite.animation) if enemy.sprite else "awaiting_art",
			"frame": enemy.sprite.frame if enemy.sprite else 0,
			"defeat_elapsed": enemy.defeat_elapsed, "sprite_visible": enemy.sprite.visible if enemy.sprite else false,
			"sprite_alpha": enemy.sprite.modulate.a if enemy.sprite else 0.0,
			"defeat_cue_visible": enemy.defeat_visual.visible})
	return {"seed": seed_value, "rng_state": str(rng.state), "state": state,
		"kills": kills, "shots_fired": shots_fired, "score": score, "time": elapsed, "ticks": encounter_ticks,
		"player": {"position": _vector(player.position), "velocity": _vector(player.velocity),
			"health": player.health, "kit": player.kit, "facing": String(player.facing),
			"melee_cooldown": player.melee_cooldown, "ranged_cooldown": player.ranged_cooldown,
			"distract_cooldown": player.distract_cooldown, "hits": player.hits_received,
			"aim": _vector(player.explicit_aim), "mouse_aim": player.mouse_aim,
			"action_timer": player.action_timer, "action_animation": String(player.action_animation),
			"action_elapsed": player.action_elapsed, "action_duration": player.action_duration,
			"action_frame": player.action_frame, "action_kind": player.action_kind,
			"action_windup": player.action_windup, "action_active": player.action_active,
			"action_recovery": player.action_recovery,
			"action_direction": player.action_direction, "action_aim": _vector(player.action_aim),
			"melee_attack_id": player.melee_attack_id, "weapon_kind": player.weapon_kind,
			"weapon_z": player.weapon_visual.z_index,
			"animation": String(player.sprite.animation), "frame": player.sprite.frame},
		"enemies": enemy_states, "bullets": combat.projectiles.size(), "hitboxes": combat.attacks.size(),
		"attack_sequence": combat.next_attack_id, "damage_events": combat.damage_events,
		"wall_impacts": combat.wall_impacts, "hit_flash": combat.hit_flash, "hit_position": _vector(combat.last_hit_position),
		"noise_position": _vector(noise_position), "noise_remaining": noise_remaining,
		"death_timer": death_timer, "gallery": gallery_mode}


func training_fixture() -> void:
	# Controlled separate bench, never used for the escape route or campaign kit.
	reset_encounter()
	gallery_mode = true
	set_kit("training")
	enemies[0].position = Vector2(95, 284)
	enemies[1].position = Vector2(224, 284)
	enemies[2].position = Vector2(598, 112)
	player.set_aim(Vector2.RIGHT)


func _frames(count: int) -> void:
	for frame in count:
		await get_tree().physics_frame


func _tap(action: String) -> void:
	Input.action_press(action)
	await _frames(1)
	Input.action_release(action)
	await _frames(1)


func _capture() -> int:
	var output := OS.get_environment("AYAY_CAPTURE_PATH")
	if output.is_empty():
		return ERR_INVALID_PARAMETER
	await RenderingServer.frame_post_draw
	return get_viewport().get_texture().get_image().save_png(output)


func _capture_and_quit() -> void:
	await _frames(6)
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), await _capture())


func _replay() -> void:
	# This is the actual scene and its native input controller, not a second simulation.
	auto_retry = false
	await _frames(30)
	reset_encounter()
	var start_snapshot := snapshot()
	player.set_aim(Vector2.UP)
	Input.action_press("move_right")
	await _frames(30)
	await _tap("distract")
	var route_frames := 32
	while state == "playing" and route_frames < 480:
		await _frames(1)
		route_frames += 1
	Input.action_release("move_right")
	var escape_result := {"cleared": state == "escaped", "kills": kills,
		"frames": route_frames, "active_enemies": enemies.size(), "detections": escape_detection_count,
		"real_input": true, "kit": player.kit, "snapshot": snapshot(), "start_snapshot": start_snapshot}
	await _frames(60)
	# Genuine lethal AI encounter: stand still as rusher spots, warns and lands a hit.
	reset_encounter()
	var safety_frames := 0
	while state == "playing" and safety_frames < 360:
		await _frames(1)
		safety_frames += 1
	var died: bool = state == "dead" and player.hits_received > 0
	await _frames(15)
	var death_snapshot := snapshot()
	await _tap("restart")
	var retry_alive: bool = state == "playing" and player.health == 1
	var max_latency := 0.0
	for latency in restart_latencies_ms:
		max_latency = maxf(max_latency, latency)
	var restart_result := {"deaths": total_deaths, "actual_ai_death": died,
		"retry_alive": retry_alive, "max_latency_ms": max_latency,
		"snapshots_equal": last_reset_snapshot == start_snapshot,
		"death_snapshot": death_snapshot, "reset_snapshot": last_reset_snapshot}
	await _frames(30)
	training_fixture()
	await _frames(1)
	await _tap("attack_melee")
	await _frames(14)
	var melee_hits: int = enemies[0].hits_received
	await _tap("attack_ranged")
	await _frames(35)
	var ranged_hits: int = enemies[1].hits_received
	var training_result := {"melee_hits": melee_hits, "ranged_hits": ranged_hits,
		"kills": kills, "shots_fired": shots_fired, "kit": player.kit, "snapshot": snapshot()}
	await _frames(35)
	var capture_code := OK
	if not OS.get_environment("AYAY_CAPTURE_PATH").is_empty():
		capture_code = await _capture()
	var result := {"schema": 1, "passed": escape_result.cleared and escape_result.kills == 0
		and escape_result.detections > 0 and died and retry_alive and max_latency < 1000
		and restart_result.snapshots_equal and melee_hits == 1 and ranged_hits == 1 and capture_code == OK,
		"escape": escape_result, "restart": restart_result, "training": training_result,
		"capture_code": capture_code}
	var result_path := OS.get_environment("AYAY_COMBAT_RESULT_PATH")
	if not result_path.is_empty():
		var file := FileAccess.open(result_path, FileAccess.WRITE)
		file.store_string(JSON.stringify(result, "  "))
	print("COMBAT_REPLAY ", JSON.stringify(result))
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0 if result.passed else 1)


func select_equipment(index: int) -> bool:
	if config_path != CONFIG_PATH or not index in range(5): return false
	if not combat.finisher_for(player).is_empty(): return false
	equipment_index = index
	var categories := ["unarmed","blunt","sharp","firearm","environmental"]
	player.finisher_category = categories[index]
	player.finisher_weapon = "unarmed" if index == 4 else categories[index]
	# Keep the normal Space attack as the earned nonlethal stun setup. A selected
	# training finisher tool never grants the campaign a ranged/knife attack kit.
	set_kit("escape")
	_update_hud()
	return true


func _build_polish_options() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 30
	add_child(layer)
	var vhs := preload("res://scripts/ui/vhs_overlay.gd").new()
	layer.add_child(vhs)
	var store := get_node("/root/OptionsStore")
	store.changed.connect(func(_key: StringName,_value: Variant):
		vhs.enabled = store.values.vhs
		vhs.reduced_motion = store.values.reduced_motion)
	vhs.enabled = store.values.vhs
	vhs.reduced_motion = store.values.reduced_motion
	options_panel = PanelContainer.new()
	options_panel.position = Vector2(195,70)
	options_panel.custom_minimum_size = Vector2(250,230)
	layer.add_child(options_panel)
	var box := VBoxContainer.new()
	options_panel.add_child(box)
	var title := Label.new()
	title.text = "ЭФФЕКТЫ · O: закрыть"
	box.add_child(title)
	var gore := OptionButton.new()
	gore.add_item("Насилие: Full")
	gore.add_item("Насилие: Reduced")
	gore.selected = 1 if store.values.reduced_gore else 0
	gore.item_selected.connect(func(index: int): store.set_value(&"reduced_gore",index == 1))
	box.add_child(gore)
	for key in ["decals","flashes","vhs","reduced_motion"]:
		var control := CheckButton.new()
		control.text = {"decals":"Следы на поверхностях","flashes":"Вспышки попаданий","vhs":"VHS","reduced_motion":"Меньше движения"}[key]
		control.button_pressed = store.values[key]
		control.toggled.connect(func(value: bool): store.set_value(StringName(key),value))
		box.add_child(control)
	var label := Label.new()
	label.text = "Тряска 0–100%"
	box.add_child(label)
	var slider := HSlider.new()
	slider.min_value = 0; slider.max_value = 100; slider.step = 1
	slider.value = store.values.shake
	slider.value_changed.connect(func(value: float): store.set_value(&"shake",value))
	box.add_child(slider)
	options_panel.hide()
