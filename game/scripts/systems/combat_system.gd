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
var defended_events: Array[Dictionary] = []
signal contact_defended(event: Dictionary)
var impact: Node2D
var polish: Dictionary
var finisher_definitions: Dictionary
var finishers: Array[Dictionary] = []
var finisher_history: Array[Dictionary] = []
var environments: Dictionary = {}
var environment_kicks := preload("res://scripts/systems/environment_kick_runtime.gd").new()
var moving_shots := preload("res://scripts/systems/moving_shot_runtime.gd").new()

func _stamp(definition: Dictionary) -> Dictionary:
	var result := definition.duplicate(true)
	result["_epoch"] = encounter_epoch
	return result



func _ready() -> void:
	process_physics_priority = 10
	environment_kicks.combat = self
	moving_shots.combat = self
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
	environment_kicks.reset()
	moving_shots.reset()
	for job in finishers.duplicate(): cancel_finisher(job.source, "reset", true)
	finishers.clear()
	finisher_history.clear()
	encounter_epoch += 1
	receipts.clear()
	contact_events.clear()
	defended_events.clear()
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
		"direction": direction.normalized(), "definition": _stamp(definition), "time": 0.0, "hit": [], "wall_hit": false})
	queue_redraw()
	return next_attack_id


func fire(source: CharacterBody2D, team: String, direction: Vector2, definition: Dictionary) -> int:
	definition = _stamp(definition)
	if definition.has("_ranged_authority") and (not source.has_method("authorize_ranged_launch") or not source.authorize_ranged_launch(definition)): return 0
	lab.audio_event.emit(&"weapon_fire", source.global_position)
	# A sound listener may revoke, reset, replace or free the source immediately.
	if not is_instance_valid(source) or source.is_queued_for_deletion() or not source.is_inside_tree() or source.health<=0 or lab.state!="playing" or int(definition._epoch)!=encounter_epoch: return 0
	if definition.has("_ranged_authority") and not source.authorize_ranged_launch(definition): return 0
	next_attack_id += 1
	var attack_id := next_attack_id
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
			_wall_contact(obstruction.position, definition, obstruction.collider)
			if int(definition._epoch)!=encounter_epoch: return attack_id
			last_hit_position = obstruction.position + visual_offset
			hit_flash = 0.15
		else:
			_apply_hit(obstruction.collider, definition, attack_id, source)
		return attack_id
	projectiles.append({"id": attack_id, "source": source, "team": team,
		"position": muzzle,
		"velocity": aim * float(definition.speed), "time": 0.0, "definition": definition,
		"visual_offset": visual_offset})
	return attack_id


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
		if not attack.wall_hit:
			var wall_query := PhysicsRayQueryParameters2D.create(source.global_position+Vector2(0,-7),center+attack.direction*float(definition.radius),1)
			var wall := get_world_2d().direct_space_state.intersect_ray(wall_query)
			if not wall.is_empty():
				attack.wall_hit = true
				wall_impacts += 1
				_wall_contact(wall.position,definition,wall.collider)
		var sphere := CircleShape2D.new()
		sphere.radius = float(definition.radius)
		var query := PhysicsShapeQueryParameters2D.new()
		query.shape = sphere
		query.transform = Transform2D(0.0, center)
		query.collision_mask = 4 if attack.team == "player" else 2
		query.exclude = [source.get_rid()]
		for contact in get_world_2d().direct_space_state.intersect_shape(query, 16):
			if source.has_method("authorize_melee_contact") and not source.authorize_melee_contact(attack.id):
				attacks.erase(attack)
				break
			var target = contact.collider
			if target.get_instance_id() in attack.hit:
				continue
			if not clear_line(source.global_position + Vector2(0, -7), target.global_position + Vector2(0, -7)):
				continue
			attack.hit.append(target.get_instance_id())
			_apply_hit(target, definition, attack.id, source, "melee")
		attack.time += delta
		if not source.has_method("melee_phase") and attack.time >= float(definition.get("windup", 0.0)) + float(definition.active):
			attacks.erase(attack)
	for bullet in projectiles.duplicate():
		if bullet.definition.has("_ranged_authority"):
			if not is_instance_valid(bullet.source) or not bullet.source.authorize_committed_projectile(bullet.definition):
				projectiles.erase(bullet)
				continue
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
				_wall_contact(contact.position, bullet.definition, contact.collider)
				if int(bullet.definition._epoch)!=encounter_epoch: continue
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
	environment_kicks.tick()
	moving_shots.tick()
	queue_redraw()


func _wall_contact(at: Vector2, definition: Dictionary, object: Node = null) -> void:
	var weapon := String(definition.get("category", "firearm"))
	var surface := String(object.get_meta("combat_surface","concrete")) if is_instance_valid(object) else "concrete"
	lab.audio_event.emit(StringName("impact_" + weapon + "_" + surface), at)


func _contact_current(target: Variant, source: Variant, epoch: int, token: String, definition: Dictionary) -> bool:
	# Variant guards run before any typed call or access to a callback-freed node.
	if epoch!=encounter_epoch or not receipts.has(token): return false
	if not is_instance_valid(target) or not is_instance_valid(source): return false
	if not target is Node2D or not source is Node2D: return false
	if target.is_queued_for_deletion() or source.is_queued_for_deletion() or not target.is_inside_tree() or not source.is_inside_tree(): return false
	if definition.has("_ranged_authority"):
		return source.has_method("authorize_committed_projectile") and source.authorize_committed_projectile(definition)
	return true

func _apply_hit(target: Node2D, definition: Dictionary, attack_id: int, source: Node2D, contact_kind := "") -> bool:
	if not is_instance_valid(target) or not is_instance_valid(source) or target.health <= 0:
		return false
	if int(definition.get("_epoch", encounter_epoch)) != encounter_epoch:
		return false
	var token := str(attack_id) + ":" + str(target.get_instance_id())
	if receipts.has(token): return false
	var epoch := encounter_epoch
	var target_id := target.get_instance_id()
	receipts[token] = true
	# Only actual melee collision dispatch opts in. Projectiles, finishers and
	# legacy direct contacts keep their existing damage/effect path. Reserve the
	# same once-token before a parry can queue its separate counterattack.
	if contact_kind == "melee" and not definition.get("finisher",false) and target.has_method("defend_melee_contact"):
		if target.defend_melee_contact(definition.duplicate(true),attack_id,source):
			if not _contact_current(target,source,epoch,token,definition): return false
			var defended := {"epoch":epoch,"id":attack_id,"target":target_id,
				"source":source.get_instance_id(),"tick":Engine.get_physics_frames(),"kind":"training_counter_parry","damage":0}
			defended_events.append(defended)
			if defended_events.size() > 512: defended_events.pop_front()
			contact_defended.emit(defended)
			return false
	if not _contact_current(target,source,epoch,token,definition): return false
	damage_events += 1
	var category := String(definition.get("category", "unarmed"))
	var strong := bool(definition.get("strong", int(definition.damage) > 0))
	var direction := (target.global_position - source.global_position).normalized()
	if definition.get("_impact_direction") is Vector2: direction = definition._impact_direction.normalized()
	last_hit_position = target.global_position + Vector2(0, -28)
	hit_flash = 0.16
	target.receive_hit(int(definition.damage), float(definition.get("stun", 0)), attack_id, source)
	if not _contact_current(target,source,epoch,token,definition): return false
	if target.health > 0 and float(definition.get("knockdown",0)) > 0 and target.has_method("receive_knockdown"):
		target.receive_knockdown(float(definition.knockdown))
		if not _contact_current(target,source,epoch,token,definition): return false
	if target.has_method("apply_impulse"):
		target.apply_impulse(direction * (float(polish.knockback_strong) if strong else float(polish.knockback_weak)))
		if not _contact_current(target,source,epoch,token,definition): return false
	if target.health <= 0 and definition.get("finisher",false) and lab.config_path == lab.CONFIG_PATH:
		lab.score += 100
	var cue := String(definition.get("cue", "impact_" + category + "_body"))
	var event := {"epoch": epoch, "id": attack_id, "target": target_id,
		"tick": Engine.get_physics_frames(), "at": target.global_position, "direction": direction,
		"category": category, "strong": strong, "damage": int(definition.damage),
		"lethal": target.health <= 0, "finisher": bool(definition.get("finisher", false)), "cue": cue}
	lab.audio_event.emit(StringName(cue), event.at)
	if not _contact_current(target,source,epoch,token,definition): return false
	contact_events.append(event)
	if contact_events.size() > 512: contact_events.pop_front()
	contact_committed.emit(event)
	return true


func _draw() -> void:
	if lab.qa_hide_indicators: return
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

func _finisher_definition(source: CharacterBody2D, category: String, job: Dictionary = {}) -> Dictionary:
	# A running contact uses its original stamped definition. Context authorization
	# is independently rechecked by eligible(), so a fixture reset cannot grant power.
	if not job.is_empty(): return job.definition
	var base: Dictionary = finisher_definitions.get(category,{})
	if source.has_method("resolve_finisher"):
		return source.resolve_finisher(category,base.duplicate(true))
	return base

func _finisher_authority(source: CharacterBody2D, category: String) -> Dictionary:
	# Legacy Yakuza keeps its existing policy. Opt-in character resolvers must
	# supply a live scene policy AND a stable identity/context/fixture generation.
	if not source.has_method("resolve_finisher"): return {}
	if not source.has_method("can_use_finisher") or not source.has_method("finisher_authority"): return {}
	if not source.can_use_finisher(category): return {}
	var authority: Variant = source.finisher_authority(category)
	if not authority is Dictionary: return {}
	for field in ["actor_id", "context", "fixture_id"]:
		if not authority.get(field) is String or String(authority[field]).is_empty(): return {}
	if not authority.get("generation") is int or int(authority.generation) < 0: return {}
	if authority.get("category") != category: return {}
	return authority.duplicate(true)

func eligible(source: CharacterBody2D, target: CharacterBody2D, category: String, job: Dictionary = {}) -> bool:
	if not finisher_definitions.has(category) or not is_instance_valid(target) or not is_instance_valid(source): return false
	if lab.state != "playing" or source.health <= 0 or target.health <= 0 or not source.is_inside_tree() or not target.is_inside_tree(): return false
	if source.has_method("resolve_finisher"):
		var authority := _finisher_authority(source,category)
		if authority.is_empty(): return false
		if not job.is_empty() and job.get("authority",{}) != authority: return false
	else:
		# A legacy actor has no per-character resolver. Its host must explicitly
		# grant the training fixture; an earned chapter stun is not a grant.
		if not lab.has_method("legacy_finishers_allowed") or not lab.legacy_finishers_allowed(source): return false
	if source.has_method("can_use_finisher") and not source.can_use_finisher(category): return false
	var definition: Dictionary = _finisher_definition(source,category,job)
	if definition.is_empty(): return false
	if source.finisher_weapon != definition.weapon: return false
	var reserved: bool = job.has("id") and target.state == "finisher_reaction" and job.target == target
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
		if offset.normalized().dot((object.global_position-target.global_position).normalized()) < 0.3: return false
		var environment_query := PhysicsRayQueryParameters2D.create(target.global_position+Vector2(0,-7),object.global_position+Vector2(0,-7),1)
		if object is CollisionObject2D: environment_query.exclude = [object.get_rid()]
		if not get_world_2d().direct_space_state.intersect_ray(environment_query).is_empty(): return false
	return true

func finisher_for(source: CharacterBody2D) -> Dictionary:
	for job in finishers:
		if job.source == source: return job
	return {}

func start_finisher(source: CharacterBody2D, target: CharacterBody2D, category: String) -> bool:
	if not is_instance_valid(source) or not is_instance_valid(target) or not finisher_definitions.has(category): return false
	if not finisher_for(source).is_empty(): return false
	# Resolve once, then reauthorize the SAME definition after cancel_action.
	# No resolver is allowed to spend ammo or change scene state.
	var definition := _finisher_definition(source,category).duplicate(true)
	var authority := _finisher_authority(source,category)
	var candidate := {"definition":definition,"authority":authority}
	if not eligible(source,target,category,candidate): return false
	for job in finishers:
		if job.target == target: return false
	source.cancel_action()
	if not eligible(source,target,category,candidate): return false
	definition = _stamp(definition)
	next_attack_id += 1
	var duration := float(definition.windup) + float(definition.active) + float(definition.recovery)
	var vulnerability: float = target.stun_remaining if target.state == "stunned" else target.timer
	finishers.append({"id":next_attack_id,"epoch":encounter_epoch,"source":source,"target":target,"category":category,
		"definition":definition,"authority":authority,"elapsed":0.0,"stage":"windup","committed":false,"vulnerability":vulnerability})
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
		job.target.transition("stunned",job.target.stun_remaining,true)
	finishers.erase(job)
	return true

func _record_finisher(job: Dictionary, stage: String, reason := "") -> void:
	finisher_history.append({"id":job.id,"epoch":job.epoch,"category":job.category,"stage":stage,"reason":reason,
		"elapsed":job.elapsed,"committed":job.committed,"tick":Engine.get_physics_frames()})
	if finisher_history.size() > 128: finisher_history.pop_front()

func _finisher_nodes_current(job: Dictionary) -> bool:
	if not finishers.has(job) or job.epoch!=encounter_epoch: return false
	if not is_instance_valid(job.source) or not is_instance_valid(job.target): return false
	if job.source.is_queued_for_deletion() or job.target.is_queued_for_deletion(): return false
	return job.source.is_inside_tree() and job.target.is_inside_tree() and is_instance_valid(job.source.sprite) and is_instance_valid(job.target.sprite)

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
				if not _finisher_nodes_current(job): continue
				job.target.sprite.set_frame_and_progress(1,0)
				# Presentation callbacks cannot charge a newly reset/replaced actor.
				if not _finisher_nodes_current(job) or not eligible(job.source,job.target,job.category,job): continue
				if job.source.has_method("commit_finisher_cost") and not job.source.commit_finisher_cost(job.epoch,job.id,job.category):
					var actor: CharacterBody2D=job.source
					cancel_finisher(actor,"resource_lost")
					actor.cancel_action()
					continue
				job.committed = true # Reentry guard precedes the only existing damage path.
				job.stage = "contact"
				_apply_hit(job.target,definition,job.id,job.source)
				# Hit audio/contact listeners may reset/free/replace the reservation.
				if not _finisher_nodes_current(job): continue
				_record_finisher(job,"contact")
		if job.committed and job.elapsed >= float(definition.windup)+float(definition.active): job.stage = "recovery"
		if job.source.action_kind.is_empty() or job.elapsed >= float(definition.windup)+float(definition.active)+float(definition.recovery):
			_record_finisher(job,"finished")
			finishers.erase(job)
