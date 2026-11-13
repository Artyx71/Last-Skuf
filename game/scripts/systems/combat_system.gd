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
signal contact_committed(event: Dictionary)
var encounter_epoch := 0
var receipts: Dictionary = {}
var contact_events: Array[Dictionary] = []
var impact: Node2D
var polish: Dictionary
var finisher_definitions: Dictionary
var finishers: Array[Dictionary] = []
var finisher_history: Array[Dictionary] = []
var environments: Dictionary = {}

func _stamp(definition: Dictionary) -> Dictionary:
	var result := definition.duplicate(true)
	result["_epoch"] = encounter_epoch
	return result



func _ready() -> void:
	process_physics_priority = 10
	polish = JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/polish.json"))
	finisher_definitions = JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/finishers.json")).definitions
	impact = preload("res://scripts/systems/combat_impact.gd").new()
	impact.combat = self
	add_child(impact)
	contact_committed.connect(impact.on_contact)


func cancel_melee(source: CharacterBody2D) -> void:
	for attack in attacks.duplicate():
		if attack.source == source:
			attacks.erase(attack)
	queue_redraw()


func _melee_phase(attack: Dictionary) -> String:
	if attack.source.has_method("bind_melee"):
		var windup := float(attack.definition.get("windup",0))
		if attack.time < windup: return "windup"
		if attack.time >= windup + float(attack.definition.active): return "finished"
	if attack.source.has_method("melee_phase"):
		return attack.source.melee_phase(attack.id)
	var windup := float(attack.definition.get("windup", 0.0))
	if attack.time < windup:
		return "windup"
	return "contact" if attack.time < windup + float(attack.definition.active) else "finished"


func reset() -> void:
	for job in finishers.duplicate(): cancel_finisher(job.source, "reset", true)
	finishers.clear()
	finisher_history.clear()
	encounter_epoch += 1
	receipts.clear()
	contact_events.clear()
	if impact: impact.reset()
	attacks.clear()
	projectiles.clear()
	next_attack_id = 0
	damage_events = 0
	wall_impacts = 0
	hit_flash = 0.0
	last_hit_position = Vector2.ZERO
	queue_redraw()


func start_melee(source: CharacterBody2D, team: String, direction: Vector2, definition: Dictionary) -> int:
	lab.audio_event.emit(&"weapon_melee", source.global_position)
	next_attack_id += 1
	if source.has_method("bind_melee"): source.bind_melee(next_attack_id,definition)
	attacks.append({"id": next_attack_id, "source": source, "team": team,
		"direction": direction.normalized(), "definition": _stamp(definition), "time": 0.0, "hit": []})
	queue_redraw()
	return next_attack_id


func fire(source: CharacterBody2D, team: String, direction: Vector2, definition: Dictionary) -> int:
	definition = _stamp(definition)
	lab.audio_event.emit(&"weapon_fire", source.global_position)
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
			_wall_contact(obstruction.position, definition)
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
	_tick_finishers(delta)
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
		if source.has_method("present_melee_contact"): source.present_melee_contact(attack.id)
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
				_wall_contact(contact.position, bullet.definition)
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


func _wall_contact(at: Vector2, definition: Dictionary) -> void:
	var weapon := String(definition.get("category", "firearm"))
	var surface := "metal" if at.x > 430 else "concrete"
	lab.audio_event.emit(StringName("impact_" + weapon + "_" + surface), at)


func _apply_hit(target: Node2D, definition: Dictionary, attack_id: int, source: Node2D) -> bool:
	if not is_instance_valid(target) or not is_instance_valid(source) or target.health <= 0:
		return false
	if int(definition.get("_epoch", encounter_epoch)) != encounter_epoch:
		return false
	var token := str(attack_id) + ":" + str(target.get_instance_id())
	if receipts.has(token): return false
	receipts[token] = true
	damage_events += 1
	var category := String(definition.get("category", "unarmed"))
	var strong := bool(definition.get("strong", int(definition.damage) > 0))
	var direction := (target.global_position - source.global_position).normalized()
	last_hit_position = target.global_position + Vector2(0, -28)
	hit_flash = 0.16
	target.receive_hit(int(definition.damage), float(definition.get("stun", 0)), attack_id, source)
	if target.has_method("apply_impulse"):
		target.apply_impulse(direction * (float(polish.knockback_strong) if strong else float(polish.knockback_weak)))
	var cue := String(definition.get("cue", "impact_" + category + "_body"))
	lab.audio_event.emit(StringName(cue), target.global_position)
	var event := {"epoch": encounter_epoch, "id": attack_id, "target": target.get_instance_id(),
		"tick": Engine.get_physics_frames(), "at": target.global_position, "direction": direction,
		"category": category, "strong": strong, "damage": int(definition.damage),
		"lethal": target.health <= 0, "finisher": bool(definition.get("finisher", false)), "cue": cue}
	contact_events.append(event)
	if contact_events.size() > 512: contact_events.pop_front()
	contact_committed.emit(event)
	return true


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
	if hit_flash > 0 and impact.flashes_enabled():
		draw_arc(last_hit_position, 9, 0, TAU, 12, Color("ffffff"), 2)


func register_environment(id: String, object: Node2D) -> void:
	environments[id] = object

func eligible(source: CharacterBody2D, target: CharacterBody2D, category: String, job: Dictionary = {}) -> bool:
	if not finisher_definitions.has(category) or not is_instance_valid(target) or not is_instance_valid(source): return false
	if lab.state != "playing" or source.health <= 0 or target.health <= 0: return false
	var definition: Dictionary = finisher_definitions[category]
	if source.finisher_weapon != definition.weapon: return false
	var reserved: bool = not job.is_empty() and target.state == "finisher_reaction" and job.target == target
	if not target.state in ["stunned", "knockdown"] and not reserved: return false
	if reserved and float(job.vulnerability) + 0.00001 < float(job.elapsed): return false
	var offset: Vector2 = target.global_position - source.global_position
	if offset.length() > float(definition.range) or offset.length() < 8: return false
	if source.aim_direction().dot(offset.normalized()) < float(definition.facing_dot): return false
	if not clear_line(source.global_position + Vector2(0,-7), target.global_position + Vector2(0,-7)): return false
	if definition.has("environment"):
		var object: Node2D = environments.get(definition.environment)
		if not is_instance_valid(object) or not object.is_inside_tree() or not object.get_meta("finisher_enabled",false): return false
		if object.global_position.distance_to(target.global_position) > float(definition.environment_range): return false
		if not clear_line(target.global_position + Vector2(0,-7), object.global_position + Vector2(0,-7)): return false
	return true

func finisher_for(source: CharacterBody2D) -> Dictionary:
	for job in finishers:
		if job.source == source: return job
	return {}

func start_finisher(source: CharacterBody2D, target: CharacterBody2D, category: String) -> bool:
	if not finisher_for(source).is_empty() or not eligible(source,target,category): return false
	for job in finishers:
		if job.target == target: return false
	source.cancel_action()
	var definition := _stamp(finisher_definitions[category])
	next_attack_id += 1
	var duration := float(definition.windup) + float(definition.active) + float(definition.recovery)
	var vulnerability: float = target.stun_remaining if target.state == "stunned" else target.timer
	finishers.append({"id":next_attack_id,"epoch":encounter_epoch,"source":source,"target":target,"category":category,
		"definition":definition,"elapsed":0.0,"stage":"windup","committed":false,"vulnerability":vulnerability})
	source.action_windup = float(definition.windup)
	source.action_active = float(definition.active)
	source.action_recovery = float(definition.recovery)
	source._face_aim()
	source._play_action("finish_" + category,duration)
	target.locked_aim = (source.global_position-target.global_position).normalized()
	target.begin_finisher(category,duration)
	return true

func cancel_finisher(source: CharacterBody2D, reason: String, force := false) -> bool:
	var job := finisher_for(source)
	if job.is_empty(): return false
	if job.committed and not force: return false
	_record_finisher(job,"interrupted_recovery" if job.committed else "cancelled",reason)
	if is_instance_valid(job.target) and job.target.health > 0 and job.target.state == "finisher_reaction":
		job.target.reaction_category = ""
		job.target.stun_remaining = maxf(0,float(job.vulnerability)-float(job.elapsed))
		job.target.transition("stunned",job.target.stun_remaining)
	finishers.erase(job)
	return true

func _record_finisher(job: Dictionary, stage: String, reason := "") -> void:
	finisher_history.append({"id":job.id,"epoch":job.epoch,"category":job.category,"stage":stage,"reason":reason,
		"elapsed":job.elapsed,"committed":job.committed,"tick":Engine.get_physics_frames()})
	if finisher_history.size() > 128: finisher_history.pop_front()

func _tick_finishers(delta: float) -> void:
	for job in finishers.duplicate():
		if not is_instance_valid(job.source) or not is_instance_valid(job.target):
			_record_finisher(job,"cancelled","freed_actor")
			finishers.erase(job)
			continue
		if job.source.health <= 0:
			cancel_finisher(job.source,"attack",true)
			continue
		job.elapsed = job.source.action_elapsed # Existing player action clock is authoritative.
		var definition: Dictionary = job.definition
		if not job.committed:
			var moving := Input.get_vector("move_left","move_right","move_up","move_down").length_squared() > 0
			if moving or not eligible(job.source,job.target,job.category,job):
				var actor: CharacterBody2D = job.source
				cancel_finisher(actor,"movement" if moving else "eligibility_lost")
				actor.cancel_action()
				continue
			if job.elapsed + 0.00001 >= float(definition.windup):
				# Present both registered contact poses on the damage tick. No animation callback damage.
				job.source._present_action()
				job.target.sprite.set_frame_and_progress(1,0)
				job.committed = true # Reentry guard precedes the only existing damage path.
				job.stage = "contact"
				_apply_hit(job.target,definition,job.id,job.source)
				_record_finisher(job,"contact")
		if job.committed and job.elapsed >= float(definition.windup)+float(definition.active): job.stage = "recovery"
		if job.source.action_kind.is_empty() or job.elapsed >= float(definition.windup)+float(definition.active)+float(definition.recovery):
			_record_finisher(job,"finished")
			finishers.erase(job)
