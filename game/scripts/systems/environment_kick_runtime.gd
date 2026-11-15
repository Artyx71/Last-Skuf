extends RefCounted
## Core extension: only real swept object collisions can request Core damage.
## Tick runs AFTER hostile melee/projectiles, before committing any object hit.
var combat: Node2D
var jobs: Array[Dictionary] = []
var history: Array[Dictionary] = []
var reset_transforms: Dictionary = {}

func _valid_object(object: PhysicsBody2D) -> bool:
	return is_instance_valid(object) and not object.is_queued_for_deletion() and object.is_inside_tree() and object.get_meta("finisher_enabled",false) and object.collision_layer & 1 != 0

func _near_foot(source: CharacterBody2D, object: PhysicsBody2D, aim: Vector2) -> bool:
	if not _valid_object(object): return false
	var offset := object.global_position-source.global_position
	if offset.length() < 12.0 or offset.length() > 38.0 or aim.dot(offset.normalized()) < 0.85: return false
	# Test the existing collider with a short foot reach, excluding only self.
	var sphere := CircleShape2D.new()
	sphere.radius = 8.0
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = sphere
	query.transform = Transform2D(0,source.global_position+Vector2(0,-6)+aim*23.0)
	query.collision_mask = 1
	query.exclude = [source.get_rid()]
	var overlapping := false
	for entry in combat.get_world_2d().direct_space_state.intersect_shape(query,16):
		if entry.collider == object: overlapping = true
	if not overlapping: return false
	var ray := PhysicsRayQueryParameters2D.create(source.global_position+Vector2(0,-6),object.global_position+Vector2(0,-6),1)
	ray.exclude = [source.get_rid(),object.get_rid()]
	return combat.get_world_2d().direct_space_state.intersect_ray(ray).is_empty()

func find_object(source: CharacterBody2D, aim: Vector2) -> PhysicsBody2D:
	var nearest: PhysicsBody2D
	var distance := INF
	for key in combat.environments:
		var candidate: Variant = combat.environments[key]
		if not is_instance_valid(candidate) or not candidate is PhysicsBody2D: continue
		if _near_foot(source,candidate,aim) and source.global_position.distance_squared_to(candidate.global_position)<distance:
			nearest = candidate
			distance = source.global_position.distance_squared_to(candidate.global_position)
	return nearest

func begin(source: CharacterBody2D, object: PhysicsBody2D) -> int:
	if jobs.size() >= 8 or not _authorized_source(source) or not _near_foot(source,object,source.action_aim): return 0
	for job in jobs:
		if job.source == source or job.object == object: return 0
	var key := ""
	for id in combat.environments:
		if combat.environments[id] == object: key = id; break
	if key.is_empty(): return 0
	combat.next_attack_id += 1
	jobs.append({"id":combat.next_attack_id,"epoch":combat.encounter_epoch,"source":source,"object":object,
		"key":key,"authority":source.action_authority_snapshot.duplicate(true),"aim":source.action_aim,
		"step":0.0,"stopped":false,"foot_contact":false,"distance":0.0,
		"definition":combat._stamp({"damage":1,"stun":0.55,"category":"environmental","strong":true})})
	return combat.next_attack_id

func _authorized_source(source: CharacterBody2D) -> bool:
	if not is_instance_valid(source) or source.is_queued_for_deletion() or not source.is_inside_tree(): return false
	if source != combat.lab.player or combat.lab.state != "playing" or source.health <= 0: return false
	return source.has_method("_action_authorized") and source.actor_id == "tega" and source.prepared_ability == "environment_kick" and source.action_kind == "special" and source.action_ability_id == "environment_kick" and source._action_authorized()

func _valid_job(job: Dictionary) -> bool:
	return job.epoch == combat.encounter_epoch and _authorized_source(job.source) and job.source.melee_attack_id == job.id and job.authority == job.source.action_authority_snapshot and _valid_object(job.object) and combat.environments.get(job.key) == job.object

func request_step(source: CharacterBody2D, distance: float) -> void:
	for job in jobs:
		if job.source == source:
			job.step = clampf(distance,0.0,210.0/60.0)
			return

func _record(job: Dictionary, stage: String, extra: Dictionary = {}) -> void:
	var item := {"id":job.id,"epoch":job.epoch,"stage":stage,"tick":Engine.get_physics_frames(),
		"distance":job.distance,"object_id":job.object.get_instance_id() if is_instance_valid(job.object) else 0}
	item.merge(extra)
	history.append(item)
	if history.size() > 128: history.pop_front()

func cancel(source: CharacterBody2D) -> void:
	for job in jobs.duplicate():
		if job.source == source:
			_record(job,"cancelled")
			jobs.erase(job)

func reset() -> void:
	jobs.clear()
	history.clear()
	for object in reset_transforms:
		if is_instance_valid(object): object.global_transform = reset_transforms[object]
	reset_transforms.clear()

func tick() -> void:
	for job in jobs.duplicate():
		if not _valid_job(job):
			_record(job,"revoked")
			jobs.erase(job)
			continue
		var source: CharacterBody2D = job.source
		var object: PhysicsBody2D = job.object
		if not _near_foot(source,object,job.aim):
			_record(job,"lost_foot_contact")
			jobs.erase(job)
			source.cancel_action()
			continue
		if source.action_frame != 1 or job.stopped: job.step = 0.0; continue
		if not job.foot_contact:
			job.foot_contact = true
			_record(job,"foot_contact",{"source_frame":source.sprite.frame,"animation":String(source.sprite.animation)})
			combat._wall_contact(object.global_position,{"category":"unarmed"},object)
			combat.lab.make_noise(object.global_position)
		var motion: Vector2 = job.aim*float(job.step)
		job.step = 0.0
		if motion.is_zero_approx(): continue
		# Exceptions and mask changes are synchronous and restored before events.
		var source_ignored: bool = object in source.get_collision_exceptions()
		if not source_ignored: source.add_collision_exception_with(object)
		var actor_blocked := source.test_move(source.global_transform,motion)
		if not source_ignored: source.remove_collision_exception_with(object)
		if actor_blocked:
			job.stopped = true
			_record(job,"actor_blocked")
			continue
		if not reset_transforms.has(object): reset_transforms[object] = object.global_transform
		var mask := object.collision_mask
		var object_ignored: bool = source in object.get_collision_exceptions()
		object.collision_mask = mask | 1 | 4
		if not object_ignored: object.add_collision_exception_with(source)
		var before := object.global_position
		var collision := object.move_and_collide(motion)
		object.collision_mask = mask
		if not object_ignored: object.remove_collision_exception_with(source)
		var travelled := object.global_position-before
		source.move_and_collide(travelled)
		job.distance += travelled.length()
		source.ability_distance += travelled.length()
		source.last_ability_path.append(source.global_position)
		source.sync_ability_presentation()
		if collision == null: continue
		job.stopped = true
		var target: Object = collision.get_collider()
		_record(job,"object_collision",{"travel":[travelled.x,travelled.y],"normal":[collision.get_normal().x,collision.get_normal().y],"collider":target.get_instance_id() if is_instance_valid(target) else 0,"source_frame":source.sprite.frame})
		# Real collider, same pinned job and contact pose; Core reserves once-token.
		if not _valid_job(job) or source.action_frame != 1: continue
		if target is CharacterBody2D and target in combat.lab.enemies and target.health > 0:
			combat._apply_hit(target,job.definition,job.id,source,"environment_object")
		elif target is CollisionObject2D and target.collision_layer & 1:
			combat.wall_impacts += 1
			combat._wall_contact(collision.get_position(),job.definition,target)
