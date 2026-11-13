extends Node2D
## Native hit volumes and swept projectiles. Layers: walls=1, player=2, enemies=4.

var lab: Node2D
var attacks: Array[Dictionary] = []
var projectiles: Array[Dictionary] = []
var next_attack_id := 0
var damage_events := 0
var wall_impacts := 0
var last_hit_position := Vector2.ZERO
var hit_flash := 0.0


func _ready() -> void:
	process_physics_priority = 10


func cancel_melee(source: CharacterBody2D) -> void:
	for attack in attacks.duplicate():
		if attack.source == source:
			attacks.erase(attack)
	queue_redraw()


func _melee_phase(attack: Dictionary) -> String:
	if attack.source.has_method("melee_phase"):
		return attack.source.melee_phase(attack.id)
	var windup := float(attack.definition.get("windup", 0.0))
	if attack.time < windup:
		return "windup"
	return "contact" if attack.time < windup + float(attack.definition.active) else "finished"


func reset() -> void:
	attacks.clear()
	projectiles.clear()
	next_attack_id = 0
	damage_events = 0
	wall_impacts = 0
	hit_flash = 0.0
	last_hit_position = Vector2.ZERO
	queue_redraw()


func start_melee(source: CharacterBody2D, team: String, direction: Vector2, definition: Dictionary) -> int:
	next_attack_id += 1
	attacks.append({"id": next_attack_id, "source": source, "team": team,
		"direction": direction.normalized(), "definition": definition, "time": 0.0, "hit": []})
	queue_redraw()
	return next_attack_id


func fire(source: CharacterBody2D, team: String, direction: Vector2, definition: Dictionary) -> int:
	next_attack_id += 1
	var aim := direction.normalized()
	var origin := source.global_position + Vector2(0, -7)
	var muzzle := origin + aim * 12.0
	var visual_origin: Vector2 = source.visual_muzzle() if source.has_method("visual_muzzle") else source.global_position + Vector2(0, -28) + aim * 18
	var visual_offset := visual_origin - muzzle
	var muzzle_query := PhysicsRayQueryParameters2D.create(origin, muzzle, 1 | (4 if team == "player" else 2))
	muzzle_query.exclude = [source.get_rid()]
	muzzle_query.hit_from_inside = true
	var obstruction := get_world_2d().direct_space_state.intersect_ray(muzzle_query)
	if not obstruction.is_empty():
		if obstruction.collider.collision_layer & 1:
			wall_impacts += 1
			last_hit_position = obstruction.position + visual_offset
			hit_flash = 0.15
		else:
			_apply_hit(obstruction.collider, definition, next_attack_id, source)
		return next_attack_id
	projectiles.append({"id": next_attack_id, "source": source, "team": team,
		"position": muzzle,
		"velocity": aim * float(definition.speed), "time": 0.0, "definition": definition,
		"visual_offset": visual_offset})
	return next_attack_id


func clear_line(from: Vector2, to: Vector2) -> bool:
	var query := PhysicsRayQueryParameters2D.create(from, to, 1)
	return get_world_2d().direct_space_state.intersect_ray(query).is_empty()


func _physics_process(delta: float) -> void:
	if lab.state != "playing":
		return
	hit_flash = maxf(0.0, hit_flash - delta)
	for attack in attacks.duplicate():
		var source: CharacterBody2D = attack.source
		if not is_instance_valid(source) or source.health <= 0:
			attacks.erase(attack)
			continue
		var phase := _melee_phase(attack)
		if phase == "finished":
			attacks.erase(attack)
			continue
		if phase == "windup":
			attack.time += delta
			continue
		var definition: Dictionary = attack.definition
		var center: Vector2 = source.global_position + Vector2(0, -7) + attack.direction * float(definition.reach)
		var sphere := CircleShape2D.new()
		sphere.radius = float(definition.radius)
		var query := PhysicsShapeQueryParameters2D.new()
		query.shape = sphere
		query.transform = Transform2D(0.0, center)
		query.collision_mask = 4 if attack.team == "player" else 2
		query.exclude = [source.get_rid()]
		for contact in get_world_2d().direct_space_state.intersect_shape(query, 16):
			var target = contact.collider
			if target.get_instance_id() in attack.hit:
				continue
			if not clear_line(source.global_position + Vector2(0, -7), target.global_position + Vector2(0, -7)):
				continue
			attack.hit.append(target.get_instance_id())
			_apply_hit(target, definition, attack.id, source)
		attack.time += delta
		if not source.has_method("melee_phase") and attack.time >= float(definition.get("windup", 0.0)) + float(definition.active):
			attacks.erase(attack)
	for bullet in projectiles.duplicate():
		var start: Vector2 = bullet.position
		var finish: Vector2 = start + bullet.velocity * delta
		var mask := 1 | (4 if bullet.team == "player" else 2)
		var query := PhysicsRayQueryParameters2D.create(start, finish, mask)
		query.hit_from_inside = true
		if is_instance_valid(bullet.source):
			query.exclude = [bullet.source.get_rid()]
		var contact := get_world_2d().direct_space_state.intersect_ray(query)
		if not contact.is_empty():
			if contact.collider.collision_layer & 1:
				wall_impacts += 1
				last_hit_position = contact.position + bullet.visual_offset
				hit_flash = 0.15
			else:
				_apply_hit(contact.collider, bullet.definition, bullet.id, bullet.source)
			projectiles.erase(bullet)
		else:
			bullet.position = finish
			bullet.time += delta
			if bullet.time >= float(bullet.definition.lifetime):
				projectiles.erase(bullet)
	queue_redraw()


func _apply_hit(target: Node2D, definition: Dictionary, attack_id: int, source: Node2D) -> void:
	if target.health <= 0:
		return
	damage_events += 1
	last_hit_position = target.global_position + Vector2(0, -28)
	hit_flash = 0.16
	target.receive_hit(int(definition.damage), float(definition.get("stun", 0)), attack_id, source)


func _draw() -> void:
	for attack in attacks:
		if is_instance_valid(attack.source) and _melee_phase(attack) == "contact":
			var center: Vector2 = attack.source.global_position + Vector2(0, -7)
			var tip: Vector2 = center + attack.direction * float(attack.definition.reach)
			draw_arc(tip, float(attack.definition.radius), 0, TAU, 20, Color("ffe4a3"), 2)
			draw_line(center, tip, Color("ffe4a3"), 2)
	for bullet in projectiles:
		var position: Vector2 = bullet.position + bullet.visual_offset
		var tail: Vector2 = position - bullet.velocity.normalized() * 8
		draw_line(tail, position, Color("ffe587") if bullet.team == "player" else Color("ff687e"), 2)
	if hit_flash > 0:
		draw_arc(last_hit_position, 9, 0, TAU, 12, Color("ffffff"), 2)
