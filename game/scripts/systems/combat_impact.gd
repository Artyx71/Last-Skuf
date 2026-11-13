extends Node2D
## Presentation clock only: hitstop holds drawn poses; physics/action clocks never stop.
## Cosmetic sequence uses its own RNG, never lab.rng. Bounded sprites, no Timer nodes.
var combat: Node2D
var particles: Array[Dictionary] = []
var decals: Array[Dictionary] = []
var cosmetic_rng := RandomNumberGenerator.new()
var hold_remaining := 0.0
var hold_cooldown := 0.0
var applied_shake := Vector2.ZERO
var shake_camera: Camera2D
var shake_remaining := 0.0
var flash_remaining := 0.0
var shake_offset := Vector2.ZERO
var held_poses: Array[Dictionary] = []
var held_ids: Dictionary = {}
var texture: Texture2D
var options: Node

func _ready() -> void:
	z_index = 2
	options = get_node_or_null("/root/OptionsStore")
	cosmetic_rng.seed = 407
	if ResourceLoader.exists("res://assets/art/combat_polish/effects.png"):
		texture = load("res://assets/art/combat_polish/effects.png")

func flashes_enabled() -> bool:
	return options == null or bool(options.values.get("flashes", true))

func reduced() -> bool:
	return options != null and bool(options.values.reduced_gore)

func reset() -> void:
	_release_poses()
	particles.clear()
	decals.clear()
	hold_remaining = 0
	hold_cooldown = 0
	_clear_shake()
	shake_remaining = 0
	flash_remaining = 0
	shake_offset = Vector2.ZERO
	cosmetic_rng.seed = 407
	queue_redraw()

func _release_poses() -> void:
	for row in held_poses:
		if is_instance_valid(row.sprite): row.sprite.self_modulate.a = 1
	held_poses.clear()
	held_ids.clear()

func on_contact(event: Dictionary) -> void:
	var cfg: Dictionary = combat.polish
	if event.strong and hold_cooldown <= 0:
		hold_cooldown = 0.12
		hold_remaining = float(cfg.hitstop_seconds)
		shake_remaining = float(cfg.shake_seconds)
		# Snapshot the exact committed pose; no hit query or damage in render callbacks.
		for actor in [combat.lab.player] + combat.lab.enemies:
			if not is_instance_valid(actor) or actor.get_instance_id() in held_ids or not actor.sprite.visible: continue
			held_ids[actor.get_instance_id()] = true
			held_poses.append({"sprite": actor.sprite, "texture": actor.sprite.sprite_frames.get_frame_texture(actor.sprite.animation, actor.sprite.frame),
				"position": actor.global_position + actor.sprite.position - Vector2(24,32), "color": actor.sprite.modulate,
				"actor_id": actor.get_instance_id(), "clothing_at": actor.global_position+preload("res://scripts/actors/polish_frames.gd").clothing_offset(actor.sprite)})
			actor.sprite.self_modulate.a = 0
	if flashes_enabled(): flash_remaining = float(cfg.flash_seconds)
	var direction: Vector2 = event.direction
	var row := 2 if absf(direction.x) > absf(direction.y) and direction.x > 0 else (1 if absf(direction.x) > absf(direction.y) else (0 if direction.y > 0 else 3))
	particles.append({"at": event.at + Vector2(0,-24), "ttl": float(cfg.particle_ttl), "row": row, "column": 0})
	while particles.size() > int(cfg.particle_cap): particles.pop_front()
	if event.damage > 0:
		for column in ([4, 6, 8] if event.finisher else [4, 6]):
			decals.append({"at": event.at + (Vector2(0,-24) if column == 6 else Vector2.ZERO), "ttl": float(cfg.decal_ttl), "row": row, "column": column + cosmetic_rng.randi_range(0,1), "actor": instance_from_id(event.target) if column == 6 and event.has("target") else null})
		var ray := PhysicsRayQueryParameters2D.create(event.at + Vector2(0,-7), event.at + Vector2(0,-7) + direction * 45, 1)
		var wall := combat.get_world_2d().direct_space_state.intersect_ray(ray)
		if not wall.is_empty(): decals.append({"at": wall.position, "ttl": float(cfg.decal_ttl), "row": row, "column": 10})
	while decals.size() > int(cfg.decal_cap): decals.pop_front()
	queue_redraw()

func _process(delta: float) -> void:
	hold_cooldown = maxf(0,hold_cooldown-delta)
	hold_remaining = maxf(0, hold_remaining - delta)
	if hold_remaining <= 0 and not held_poses.is_empty(): _release_poses()
	shake_remaining = maxf(0, shake_remaining - delta)
	flash_remaining = maxf(0, flash_remaining - delta)
	var intensity := float(options.values.get("shake",100)) / 100.0 if options else 1.0
	if options and options.values.reduced_motion: intensity = 0
	shake_offset = Vector2(cosmetic_rng.randf_range(-1,1), cosmetic_rng.randf_range(-1,1)) * float(combat.polish.max_shake_px) * intensity if shake_remaining > 0 else Vector2.ZERO
	# Preserve the chapter Camera2D transform; shake changes only camera.offset.
	var current_camera := get_viewport().get_camera_2d()
	if current_camera != shake_camera:
		_clear_shake()
		shake_camera = current_camera
	if shake_camera:
		shake_camera.offset += shake_offset-applied_shake
	else:
		get_viewport().canvas_transform.origin += shake_offset-applied_shake
	applied_shake = shake_offset
	for pool in [particles, decals]:
		for entry in pool.duplicate():
			if entry.has("actor") and is_instance_valid(entry.actor):
				entry.at = entry.actor.global_position+preload("res://scripts/actors/polish_frames.gd").clothing_offset(entry.actor.sprite)
				for held in held_poses:
					if held.actor_id==entry.actor.get_instance_id(): entry.at=held.clothing_at
			entry.ttl -= delta
			if entry.ttl <= 0: pool.erase(entry)
	queue_redraw()

func _draw() -> void:
	if texture:
		if options == null or options.values.get("decals", true):
			for decal in decals:
				if not reduced():
					# Clothing's authored mask is centred at source(24,32), unlike floor stains.
					_draw_cell(decal.at, decal.column, decal.row)
		for particle in particles:
			var frame := mini(3, int((float(combat.polish.particle_ttl) - particle.ttl) * 4 / float(combat.polish.particle_ttl)))
			_draw_cell(particle.at, 11 if reduced() else frame, particle.row)
	for row in held_poses:
		draw_texture(row.texture, row.position, row.color)

func _draw_cell(at: Vector2, column: int, row: int) -> void:
	draw_texture_rect_region(texture, Rect2(at - Vector2(24,32), Vector2(48,64)), Rect2(column*48,row*64,48,64))

func _clear_shake() -> void:
	if is_instance_valid(shake_camera): shake_camera.offset -= applied_shake
	elif is_inside_tree(): get_viewport().canvas_transform.origin -= applied_shake
	applied_shake = Vector2.ZERO

func _exit_tree() -> void:
	_release_poses()
	_clear_shake()
