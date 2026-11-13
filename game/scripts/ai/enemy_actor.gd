extends CharacterBody2D
## Observable deterministic FSM: patrol→alert→pursue→telegraph→recover.

var lab: Node2D
var kind := "patrol"
var definition: Dictionary
var spawn_position := Vector2.ZERO
var patrol_end := Vector2.ZERO
var patrol_target := Vector2.ZERO
var health := 1
var state := "patrol"
var timer := 0.0
var stun_remaining := 0.0
var investigate_remaining := 0.0
var investigate_point := Vector2.ZERO
var locked_aim := Vector2.RIGHT
var facing := "down"
var sprite: AnimatedSprite2D
var transitions: Array[String] = []
var detection_count := 0
var attacks_started := 0
var hits_received := 0
var animation_ready := false
var defeat_elapsed := 0.0
var defeat_visual: Node2D


func _ready() -> void:
	z_index = int(lab.visual_config.render_planes.actor_body)
	collision_layer = 4
	collision_mask = 1
	var shape := CollisionShape2D.new()
	var bounds := RectangleShape2D.new()
	bounds.size = Vector2(16, 12)
	shape.shape = bounds
	shape.position = Vector2(0, -6)
	add_child(shape)
	_load_art()
	defeat_visual = preload("res://scripts/ai/enemy_defeat_visual.gd").new()
	defeat_visual.actor = self
	defeat_visual.z_index = 1
	defeat_visual.visible = false
	add_child(defeat_visual)


func _load_art() -> void:
	var path := "res://assets/art/enemies/" + kind + "_sheet.png"
	if not ResourceLoader.exists(path):
		return # Art production runs independently. No substitute character is drawn.
	var texture: Texture2D = load(path)
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	var directions := ["down", "left", "right", "up"]
	for row in 4:
		for motion in ["idle", "walk"]:
			var animation := StringName(motion + "_" + directions[row])
			frames.add_animation(animation)
			frames.set_animation_speed(animation, 3.0 if motion == "idle" else 8.0)
			for column in range(0 if motion == "idle" else 2, 2 if motion == "idle" else 8):
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.region = Rect2(column * 48, row * 64, 48, 64)
				frames.add_frame(animation, atlas)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.position = Vector2(0, -26)
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(sprite)
	sprite.play(&"idle_down")
	animation_ready = true


func reset() -> void:
	position = spawn_position
	patrol_target = patrol_end
	velocity = Vector2.ZERO
	health = 1
	defeat_elapsed = 0.0
	defeat_visual.visible = false
	defeat_visual.queue_redraw()
	collision_layer = 4
	state = "patrol"
	timer = 0.0
	stun_remaining = 0.0
	investigate_remaining = 0.0
	investigate_point = Vector2.ZERO
	locked_aim = Vector2.RIGHT
	facing = "down"
	transitions = ["patrol"]
	detection_count = 0
	attacks_started = 0
	hits_received = 0
	modulate = Color.WHITE
	if sprite:
		sprite.visible = true
		sprite.modulate = Color.WHITE
		sprite.play(&"idle_down")
		sprite.set_frame_and_progress(0, 0.0)
	queue_redraw()


func transition(next: String, duration := 0.0) -> void:
	state = next
	timer = duration
	transitions.append(next)
	if next == "alert": lab.audio_event.emit(&"state_suspicion", global_position)
	elif next == "telegraph": lab.audio_event.emit(&"state_combat", global_position)


func sees_player() -> bool:
	return lab.player.health > 0 and position.distance_to(lab.player.position) <= float(definition.sight) and lab.combat.clear_line(position + Vector2(0, -7), lab.player.position + Vector2(0, -7))


func hear_noise(point: Vector2) -> void:
	if health <= 0 or position.distance_to(point) > 260:
		return
	investigate_point = point
	investigate_remaining = 2.1
	transition("investigate")


func receive_hit(damage: int, stun: float, _attack_id: int, _source: Node2D) -> void:
	if health <= 0:
		return
	hits_received += 1
	health = maxi(0, health - damage)
	if health <= 0:
		collision_layer = 0
		velocity = Vector2.ZERO
		lab.combat.cancel_melee(self)
		defeat_elapsed = 0.0
		defeat_visual.visible = true
		defeat_visual.queue_redraw()
		if sprite:
			sprite.pause()
		transition("dead")
		lab.kills += 1
	elif stun > 0:
		stun_remaining = stun
		transition("stunned", stun)
	queue_redraw()


func _physics_process(delta: float) -> void:
	if health <= 0:
		velocity = Vector2.ZERO
		var fade := float(lab.visual_config.enemy_defeat.fade_seconds)
		var cue := float(lab.visual_config.enemy_defeat.cue_seconds)
		defeat_elapsed = minf(cue, defeat_elapsed + delta)
		defeat_visual.visible = defeat_elapsed < cue
		defeat_visual.queue_redraw()
		if sprite:
			sprite.modulate.a = maxf(0.0, 1.0 - defeat_elapsed / fade)
			sprite.visible = defeat_elapsed < fade
		queue_redraw()
		return
	if lab.state != "playing" or health <= 0:
		velocity = Vector2.ZERO
		if health > 0 and sprite and sprite.animation.begins_with("walk_"):
			sprite.play(StringName("idle_" + facing))
		return
	velocity = Vector2.ZERO
	timer = maxf(0, timer - delta)
	match state:
		"stunned":
			stun_remaining = maxf(0, stun_remaining - delta)
			if stun_remaining <= 0:
				transition("patrol")
		"investigate":
			investigate_remaining = maxf(0, investigate_remaining - delta)
			_walk_to(investigate_point, float(definition.chase_speed) * 0.8)
			if investigate_remaining <= 0:
				transition("patrol")
		"patrol":
			if sees_player():
				detection_count += 1
				transition("alert", float(definition.reaction))
			else:
				_walk_to(patrol_target, float(definition.speed))
				if position.distance_to(patrol_target) < 4:
					patrol_target = spawn_position if patrol_target == patrol_end else patrol_end
		"alert":
			if not sees_player():
				transition("patrol")
			elif timer <= 0:
				transition("pursue")
		"pursue":
			if not sees_player():
				transition("patrol")
			elif position.distance_to(lab.player.position) <= float(definition.range):
				locked_aim = (lab.player.position - position).normalized()
				attacks_started += 1
				transition("telegraph", float(definition.telegraph))
			else:
				_walk_to(lab.player.position, float(definition.chase_speed))
		"telegraph":
			if timer <= 0:
				# Direction is locked during warning; running out of the aim line is valid.
				var attack: Dictionary = lab.config.attacks[definition.attack]
				if kind == "shooter":
					lab.combat.fire(self, "enemy", locked_aim, attack)
				else:
					lab.combat.start_melee(self, "enemy", locked_aim, attack)
				transition("recover", float(definition.recovery))
		"recover":
			if timer <= 0:
				transition("pursue")
	move_and_slide()
	_update_animation()
	queue_redraw()


func _walk_to(point: Vector2, speed: float) -> void:
	if position.distance_to(point) > 3:
		velocity = (point - position).normalized() * speed


func _update_animation() -> void:
	var direction := velocity if velocity.length_squared() > 1 else locked_aim
	if absf(direction.x) > absf(direction.y):
		facing = "right" if direction.x > 0 else "left"
	elif direction.length_squared() > 0:
		facing = "down" if direction.y > 0 else "up"
	if sprite:
		var animation := StringName(("walk_" if velocity.length_squared() > 1 else "idle_") + facing)
		if sprite.animation != animation:
			sprite.play(animation)


func _draw() -> void:
	if health <= 0:
		return
	var color := Color("a8a9bb")
	if state in ["alert", "pursue"]:
		color = Color("ffcc71")
	elif state == "telegraph":
		color = Color("ff546f")
	elif state in ["stunned", "investigate"]:
		color = Color("6ed9eb")
	draw_arc(Vector2(0, -5), 12, 0, TAU, 20, color, 1.5)
	if state == "telegraph":
		var length := float(definition.range) if kind == "shooter" else 33.0
		draw_line(Vector2(0, -7), Vector2(0, -7) + locked_aim * length, color, 1.5)
		var progress := 1.0 - timer / float(definition.telegraph)
		draw_arc(Vector2(0, -37), 7, -PI / 2, -PI / 2 + TAU * progress, 20, color, 2)
	elif state == "alert":
		draw_line(Vector2(0, -43), Vector2(0, -35), color, 3)
