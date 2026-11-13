extends "res://scripts/actors/yakuza_actor.gd"
## Escape inventory is canonical for this lab; weapons belong only to the explicit test kit.

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
var action_animation: StringName = &""
var actions_ready := false


func _ready() -> void:
	super._ready()
	var path := "res://assets/art/yakuza/action_sheet.png"
	if not ResourceLoader.exists(path):
		return
	var texture: Texture2D = load(path)
	for row in DIRECTIONS.size():
		for action in [{"name": "shove", "first": 0, "count": 3},
				{"name": "hit", "first": 3, "count": 2}, {"name": "fall", "first": 5, "count": 3}]:
			var animation := StringName(action.name + "_" + String(DIRECTIONS[row]))
			sprite.sprite_frames.add_animation(animation)
			sprite.sprite_frames.set_animation_speed(animation, 12.0)
			sprite.sprite_frames.set_animation_loop(animation, false)
			for column in range(action.first, action.first + action.count):
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.region = Rect2(Vector2(column, row) * FRAME_SIZE, FRAME_SIZE)
				sprite.sprite_frames.add_frame(animation, atlas)
	actions_ready = true


func _play_action(action: String, duration: float) -> void:
	if not actions_ready:
		return
	action_animation = StringName(action + "_" + String(facing))
	action_timer = duration
	sprite.play(action_animation)
	sprite.set_frame_and_progress(0, 0.0)


func reset(at: Vector2) -> void:
	position = at
	velocity = Vector2.ZERO
	health = int(lab.config.player.health)
	move_speed = float(lab.config.player.speed)
	facing = &"right"
	kit = "escape"
	melee_cooldown = 0.0
	ranged_cooldown = 0.0
	distract_cooldown = 0.0
	hits_received = 0
	explicit_aim = Vector2.ZERO
	mouse_aim = false
	action_timer = 0.0
	action_animation = &""
	modulate = Color.WHITE
	sprite.play(&"idle_right")
	sprite.set_frame_and_progress(0, 0.0)


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
	if lab.state != "playing" or health <= 0:
		velocity = Vector2.ZERO
		action_timer = maxf(0.0, action_timer - delta)
		if health > 0 and sprite.animation.begins_with("walk_"):
			sprite.play(StringName("idle_" + String(facing)))
		return
	# Preserve action playback while the P01 controller keeps movement responsive.
	var previous_action: StringName = action_animation if action_timer > 0 else &""
	var previous_frame := sprite.frame
	var previous_progress := sprite.frame_progress
	super._physics_process(delta)
	melee_cooldown = maxf(0.0, melee_cooldown - delta)
	ranged_cooldown = maxf(0.0, ranged_cooldown - delta)
	distract_cooldown = maxf(0.0, distract_cooldown - delta)
	if Input.is_action_just_pressed("attack_melee"):
		attack_melee()
	if Input.is_action_just_pressed("attack_ranged"):
		attack_ranged()
	if Input.is_action_just_pressed("distract"):
		distract()
	if action_timer > 0:
		sprite.play(action_animation)
		if action_animation == previous_action:
			sprite.set_frame_and_progress(previous_frame, previous_progress)
		action_timer = maxf(0.0, action_timer - delta)
	else:
		action_animation = &""
	queue_redraw()


func _face_aim() -> void:
	var direction := aim_direction()
	if absf(direction.x) > absf(direction.y):
		facing = &"right" if direction.x > 0 else &"left"
	else:
		facing = &"down" if direction.y > 0 else &"up"


func attack_melee() -> bool:
	if lab.state != "playing" or health <= 0 or melee_cooldown > 0:
		return false
	var definition: Dictionary = lab.config.attacks[lab.config.kits[kit].melee]
	melee_cooldown = float(definition.cooldown)
	_face_aim()
	lab.combat.start_melee(self, "player", aim_direction(), definition)
	_play_action("shove", 0.25)
	return true


func attack_ranged() -> bool:
	var weapon: String = lab.config.kits[kit].ranged
	if weapon.is_empty() or lab.state != "playing" or health <= 0 or ranged_cooldown > 0:
		return false
	var definition: Dictionary = lab.config.attacks[weapon]
	ranged_cooldown = float(definition.cooldown)
	_face_aim()
	lab.shots_fired += 1
	lab.combat.fire(self, "player", aim_direction(), definition)
	return true


func distract() -> bool:
	if lab.state != "playing" or health <= 0 or distract_cooldown > 0:
		return false
	distract_cooldown = float(lab.config.kits[kit].distract_cooldown)
	var point := global_position + aim_direction() * 110.0
	# A thrown improvised noise stops at actual walls, rather than crossing them.
	var ray := PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -7), point, 1)
	var obstruction := get_world_2d().direct_space_state.intersect_ray(ray)
	if not obstruction.is_empty():
		point = obstruction.position - aim_direction() * 4.0
	lab.make_noise(point)
	return true


func receive_hit(damage: int, _stun: float, _attack_id: int, _source: Node2D) -> void:
	if health <= 0:
		return
	hits_received += 1
	health = maxi(0, health - damage)
	if health == 0:
		modulate = Color("a66f80")
		_play_action("fall", 0.25)
		lab.player_died()
	else:
		_play_action("hit", 0.167)
	queue_redraw()


func _draw() -> void:
	if health > 0:
		draw_arc(Vector2(0, -5), 12, -0.3, PI + 0.3, 16, Color("66e5cc"), 1)
		var aim := aim_direction()
		draw_line(Vector2(0, -7) + aim * 16, Vector2(0, -7) + aim * 23, Color("66e5cc"), 2)
		if kit == "training" and ranged_cooldown > 0.25:
			var muzzle := Vector2(0, -9) + aim * 14
			draw_line(muzzle, muzzle + aim * 12, Color("8b9fb5"), 4)
			draw_line(muzzle + aim * 7, muzzle + aim * 12, Color("e9edf2"), 2)
		elif kit == "training" and action_timer > 0:
			var blade := Vector2(0, -9) + aim * 21
			draw_line(blade - aim * 5, blade, Color("896b4d"), 3)
			draw_line(blade, blade + aim * 10, Color("e9edf2"), 2)
