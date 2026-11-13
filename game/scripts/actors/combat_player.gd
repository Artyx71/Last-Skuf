extends "res://scripts/actors/yakuza_actor.gd"
## P01 movement stays intact. Actions and contact share one fixed-physics pose clock.

const WeaponVisual = preload("res://scripts/actors/combat_weapon_visual.gd")
var impulse := Vector2.ZERO
var lab: Node2D
var health := 1
var kit := "escape"
var melee_cooldown := 0.0
var ranged_cooldown := 0.0
var distract_cooldown := 0.0
var hits_received := 0
var explicit_aim := Vector2.ZERO
var mouse_aim := false
var action_timer := 0.0
var action_elapsed := 0.0
var action_duration := 0.0
var action_animation: StringName = &""
var action_direction := "right"
var action_aim := Vector2.RIGHT
var action_kind := ""
var action_frame := 0
var action_windup := 0.0
var action_active := 0.0
var action_recovery := 0.0
var melee_attack_id := 0
var weapon_kind := ""
var audio_step_distance := 0.0
var finisher_weapon := "unarmed"
var finisher_category := "unarmed"
var actions_ready := false
var weapon_visual: Node2D


func _ready() -> void:
	super._ready()
	process_physics_priority = -10
	# Keep a rear hand layer above the arena floor even when its relative z is -1.
	z_index = int(lab.visual_config.render_planes.actor_body)
	var path := "res://assets/art/yakuza/action_sheet.png"
	assert(ResourceLoader.exists(path), "P02 authored action art required")
	var texture: Texture2D = load(path)
	for row in DIRECTIONS.size():
		for action in [{"name": "shove", "first": 0, "count": 3},
				{"name": "hit", "first": 3, "count": 2}, {"name": "fall", "first": 5, "count": 3},
				{"name": "fire", "first": 1, "count": 1}]:
			var animation := StringName(action.name + "_" + String(DIRECTIONS[row]))
			sprite.sprite_frames.add_animation(animation)
			sprite.sprite_frames.set_animation_speed(animation, float(lab.visual_config.actions.fps))
			sprite.sprite_frames.set_animation_loop(animation, false)
			for column in range(action.first, action.first + action.count):
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.region = Rect2(Vector2(column, row) * FRAME_SIZE, FRAME_SIZE)
				sprite.sprite_frames.add_frame(animation, atlas)
	preload("res://scripts/actors/polish_frames.gd").append(sprite.sprite_frames,
		"res://assets/art/combat_polish/yakuza_finishers.png", ["unarmed","blunt","sharp","firearm","environmental"], "finish_")
	actions_ready = true
	weapon_visual = WeaponVisual.new()
	weapon_visual.player = self
	add_child(weapon_visual)


func _play_action(action: String, duration: float) -> void:
	action_kind = action
	action_direction = String(facing)
	action_aim = aim_direction()
	action_animation = StringName(action + "_" + action_direction)
	action_duration = duration
	action_elapsed = 0.0
	action_timer = duration
	action_frame = 0
	_present_action()


func _present_action() -> void:
	if action_animation.is_empty():
		return
	var fps := float(lab.visual_config.actions.fps)
	var count := sprite.sprite_frames.get_frame_count(action_animation)
	var phase := action_elapsed * fps
	var progress: float = phase - floor(phase + 0.00001)
	action_frame = mini(int(floor(phase + 0.00001)), count - 1)
	if action_kind == "shove" or action_kind.begins_with("finish_"):
		if action_elapsed + 0.00001 < action_windup:
			action_frame = 0
			progress = action_elapsed / action_windup
		elif action_elapsed + 0.00001 < action_windup + action_active:
			action_frame = 1
			progress = (action_elapsed - action_windup) / action_active
		else:
			action_frame = 2
			progress = (action_elapsed - action_windup - action_active) / action_recovery
	sprite.play(action_animation)
	sprite.pause()
	sprite.set_frame_and_progress(action_frame, clampf(progress, 0.0, 1.0))
	weapon_visual_update()


func weapon_visual_update() -> void:
	if weapon_visual:
		var sockets: Dictionary = lab.visual_config.anchors[action_direction]
		var layers: Array = sockets.get(action_kind + "_layers", [sockets.layer])
		weapon_visual.z_index = int(layers[mini(action_frame, layers.size() - 1)])
		weapon_visual.queue_redraw()


func weapon_socket_visible() -> bool:
	var sockets: Dictionary = lab.visual_config.anchors[action_direction]
	var visibility: Array = sockets.get(action_kind + "_visible", [true])
	return bool(visibility[mini(action_frame, visibility.size() - 1)])


func _advance_action(delta: float) -> void:
	if action_animation.is_empty():
		return
	action_elapsed = minf(action_duration, action_elapsed + delta)
	action_timer = maxf(0.0, action_duration - action_elapsed)
	if action_timer <= 0.00001 and action_kind != "fall":
		cancel_action()


func cancel_action() -> void:
	var job: Dictionary = lab.combat.finisher_for(self)
	if not job.is_empty() and job.committed and health > 0 and action_timer > 0.00001: return
	lab.combat.cancel_finisher(self,"action_cancel",health <= 0)
	lab.combat.cancel_melee(self)
	action_timer = 0.0
	action_elapsed = 0.0
	action_duration = 0.0
	action_animation = &""
	action_kind = ""
	action_frame = 0
	action_windup = 0.0
	action_active = 0.0
	action_recovery = 0.0
	melee_attack_id = 0
	weapon_kind = ""
	weapon_visual_update()


func melee_phase(attack_id: int) -> String:
	if health <= 0 or attack_id != melee_attack_id or action_kind != "shove":
		return "finished"
	var contact := int(lab.visual_config.actions.contact_frame)
	if action_frame < contact:
		return "windup"
	return "contact" if action_frame == contact else "finished"


func weapon_socket() -> Vector2:
	if not action_kind in ["shove", "fire"]:
		return Vector2.ZERO
	var points: Array = lab.visual_config.anchors[action_direction][action_kind]
	var point: Array = points[mini(action_frame, points.size() - 1)]
	return Vector2(point[0], point[1]) - FRAME_PIVOT


func visual_muzzle() -> Vector2:
	return global_position + weapon_socket() + action_aim * float(lab.visual_config.pistol.barrel)


func reset(at: Vector2) -> void:
	audio_step_distance = 0.0
	impulse = Vector2.ZERO
	cancel_action()
	position = at
	velocity = Vector2.ZERO
	health = int(lab.config.player.health)
	move_speed = float(lab.config.player.speed)
	facing = &"right"
	kit = "escape"
	finisher_weapon = "unarmed"
	finisher_category = "unarmed"
	melee_cooldown = 0.0
	ranged_cooldown = 0.0
	distract_cooldown = 0.0
	hits_received = 0
	explicit_aim = Vector2.ZERO
	mouse_aim = false
	action_direction = "right"
	action_aim = Vector2.RIGHT
	modulate = Color.WHITE
	sprite.play(&"idle_right")
	sprite.set_frame_and_progress(0, 0.0)
	weapon_visual_update()
	queue_redraw()


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and event.relative.length_squared() > 0.01 and explicit_aim.length_squared() < 0.01:
		mouse_aim = true


func set_aim(direction: Vector2) -> void:
	explicit_aim = direction.normalized()


func clear_aim() -> void:
	explicit_aim = Vector2.ZERO
	mouse_aim = false


func aim_direction() -> Vector2:
	if explicit_aim.length_squared() > 0.01:
		return explicit_aim
	if mouse_aim:
		var aim := get_global_mouse_position() - (global_position + Vector2(0, -7))
		if aim.length_squared() > 1.0:
			return aim.normalized()
	return {&"right": Vector2.RIGHT, &"left": Vector2.LEFT, &"down": Vector2.DOWN, &"up": Vector2.UP}[facing]


func _physics_process(delta: float) -> void:
	if lab.state == "playing": _move_impulse(delta)
	_advance_action(delta)
	if lab.state != "playing" or health <= 0:
		velocity = Vector2.ZERO
		if not action_animation.is_empty():
			_present_action()
		elif sprite.animation.begins_with("walk_"):
			sprite.play(StringName("idle_" + String(facing)))
		queue_redraw()
		return
	var audio_previous := position
	var job: Dictionary = lab.combat.finisher_for(self)
	if not job.is_empty():
		if Input.is_action_just_pressed("cancel_finisher"):
			if lab.combat.cancel_finisher(self,"cancel_input"): cancel_action()
		if Input.is_action_just_pressed("attack_melee") and not job.committed:
			cancel_action()
		elif not Input.get_vector("move_left","move_right","move_up","move_down").is_zero_approx() and not job.committed:
			cancel_action()
		else:
			velocity = Vector2.ZERO
			_present_action()
			return
	super._physics_process(delta)
	audio_step_distance += position.distance_to(audio_previous)
	if audio_step_distance >= 24.0:
		audio_step_distance = fmod(audio_step_distance, 24.0)
		var material := "metal" if position.x > 430 else "concrete"
		lab.audio_event.emit(StringName("footstep_" + material), global_position)
	melee_cooldown = maxf(0.0, melee_cooldown - delta)
	ranged_cooldown = maxf(0.0, ranged_cooldown - delta)
	distract_cooldown = maxf(0.0, distract_cooldown - delta)
	if Input.is_action_just_pressed("attack_melee"):
		attack_melee()
	if Input.is_action_just_pressed("attack_ranged"):
		attack_ranged()
	if Input.is_action_just_pressed("finisher"):
		try_finisher()
	if Input.is_action_just_pressed("distract"):
		distract()
	if not action_animation.is_empty():
		_present_action()
	queue_redraw()


func _face_aim() -> void:
	var direction := aim_direction()
	if absf(direction.x) > absf(direction.y):
		facing = &"right" if direction.x > 0 else &"left"
	else:
		facing = &"down" if direction.y > 0 else &"up"


func try_finisher() -> bool:
	for enemy in lab.enemies:
		if lab.combat.start_finisher(self,enemy,finisher_category): return true
	return false

func attack_melee() -> bool:
	var job: Dictionary = lab.combat.finisher_for(self)
	if not job.is_empty() and job.committed: return false
	if lab.state != "playing" or health <= 0 or melee_cooldown > 0:
		return false
	cancel_action()
	var definition: Dictionary = lab.config.attacks[lab.config.kits[kit].melee]
	melee_cooldown = float(definition.cooldown)
	_face_aim()
	action_windup = float(definition.windup)
	action_active = float(definition.active)
	action_recovery = float(definition.recovery)
	_play_action("shove", action_windup + action_active + action_recovery)
	weapon_kind = "knife" if kit == "training" else ""
	melee_attack_id = lab.combat.start_melee(self, "player", action_aim, definition)
	weapon_visual_update()
	return true


func attack_ranged() -> bool:
	var job: Dictionary = lab.combat.finisher_for(self)
	if not job.is_empty() and job.committed: return false
	var weapon: String = lab.config.kits[kit].ranged
	if weapon.is_empty() or lab.state != "playing" or health <= 0 or ranged_cooldown > 0:
		return false
	cancel_action()
	var definition: Dictionary = lab.config.attacks[weapon]
	ranged_cooldown = float(definition.cooldown)
	_face_aim()
	_play_action("fire", float(lab.visual_config.actions.fire_hold))
	weapon_kind = "pistol"
	weapon_visual_update()
	lab.shots_fired += 1
	lab.combat.fire(self, "player", action_aim, definition)
	return true


func distract() -> bool:
	if lab.state != "playing" or health <= 0 or distract_cooldown > 0:
		return false
	distract_cooldown = float(lab.config.kits[kit].distract_cooldown)
	var point := global_position + aim_direction() * 110.0
	var ray := PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -7), point, 1)
	var obstruction := get_world_2d().direct_space_state.intersect_ray(ray)
	if not obstruction.is_empty():
		point = obstruction.position - aim_direction() * 4.0
	lab.make_noise(point)
	return true


func receive_hit(damage: int, _stun: float, _attack_id: int, _source: Node2D) -> void:
	if health <= 0:
		return
	health = maxi(0, health - damage)
	lab.combat.cancel_finisher(self,"attack",true)
	cancel_action()
	hits_received += 1
	if health == 0:
		modulate = Color("a66f80")
		_play_action("fall", 0.25)
		lab.player_died()
	else:
		_play_action("hit", 2.0 / float(lab.visual_config.actions.fps))
	queue_redraw()


func _draw() -> void:
	if health > 0:
		draw_arc(Vector2(0, -5), 12, -0.3, PI + 0.3, 16, Color("66e5cc"), 1)
		var aim := aim_direction()
		draw_line(Vector2(0, -7) + aim * 16, Vector2(0, -7) + aim * 23, Color("66e5cc"), 2)


func apply_impulse(value: Vector2) -> void:
	impulse = value.limit_length(100)

func _move_impulse(delta: float) -> void:
	if impulse.length_squared() > 0.01:
		move_and_collide(impulse * delta)
		impulse = impulse.move_toward(Vector2.ZERO, 700 * delta)
