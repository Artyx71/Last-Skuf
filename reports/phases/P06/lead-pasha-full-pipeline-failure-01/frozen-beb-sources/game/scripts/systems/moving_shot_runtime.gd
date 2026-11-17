extends RefCounted
## Deferred Pasha launch after hostile contacts, on his actual muzzle pose3.
var combat: Node2D
var jobs: Array[Dictionary] = []
var history: Array[Dictionary] = []

func _source_valid(source: Variant, strategy: RefCounted) -> bool:
	if not is_instance_valid(source) or not source is CharacterBody2D or source.is_queued_for_deletion() or not source.is_inside_tree(): return false
	return source==combat.lab.player and source.health>0 and combat.lab.state=="playing" and source.has_method("_action_authorized") and source.actor_id=="pasha" and source.prepared_ability=="moving_shot" and source.movement_ability==strategy and source.action_kind=="moving_shot" and source._action_authorized()

func begin(source: CharacterBody2D, strategy: RefCounted) -> int:
	if jobs.size()>=8 or not _source_valid(source,strategy) or not strategy.can_spend(source): return 0
	for job in jobs:
		if job.source==source: return 0
	combat.next_attack_id += 1
	jobs.append({"id":combat.next_attack_id,"epoch":combat.encounter_epoch,"source":source,"strategy":strategy,
		"authority":source.action_authority_snapshot.duplicate(true),"serial":source.action_serial,"aim":source.action_aim,"fired":false})
	return combat.next_attack_id

func _valid(job: Dictionary) -> bool:
	return jobs.has(job) and job.epoch==combat.encounter_epoch and _source_valid(job.source,job.strategy) and job.source.ranged_action_id==job.id and job.source.action_serial==job.serial and job.authority==job.source.action_authority_snapshot

func cancel(source: CharacterBody2D) -> void:
	for job in jobs.duplicate():
		if job.source==source: jobs.erase(job)

func reset() -> void:
	jobs.clear()
	history.clear()

func tick() -> void:
	for job in jobs.duplicate():
		if not _valid(job):
			jobs.erase(job)
			continue
		var source: CharacterBody2D = job.source
		if job.fired or source.action_frame!=3: continue
		var texture: Texture2D = source.sprite.sprite_frames.get_frame_texture(source.sprite.animation,source.sprite.frame)
		if source.sprite.frame!=3 or not texture.has_meta("muzzle_socket"): continue
		# Reserve before any sound/collision callback; a reset cannot replay it.
		job.fired = true
		if not job.strategy.spend_round(source,job.epoch,job.id,"moving_shot"): continue
		var definition: Dictionary = combat.lab.config.attacks.pistol.duplicate(true)
		definition["_ranged_authority"] = job.authority.duplicate(true)
		definition["_ranged_job_id"] = job.id
		definition["_ranged_strategy_id"] = job.strategy.get_instance_id()
		definition["_ranged_epoch"] = job.epoch
		definition["_ranged_action_serial"] = job.serial
		definition["_impact_direction"] = job.aim
		var at: Vector2 = source.global_position
		var muzzle: Vector2 = source.visual_muzzle()
		var bullet_id: int = combat.fire(source,"player",job.aim,definition)
		# No writes to a replacement actor/strategy after fire's external events.
		if not _valid(job): continue
		if bullet_id>0: combat.lab.shots_fired += 1
		history.append({"epoch":job.epoch,"job_id":job.id,"bullet_id":bullet_id,"tick":Engine.get_physics_frames(),
			"source_pose":3,"at":[at.x,at.y],"muzzle":[muzzle.x,muzzle.y],"authority":job.authority.duplicate(true)})
		if history.size()>128: history.pop_front()
