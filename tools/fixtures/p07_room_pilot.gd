extends SceneTree
## Production CH01 scene/host/geometry; route actors are positioned only for
## targeted navigation diagnostics, never presented as a chapter playthrough.
const Mission = preload("res://scenes/levels/missed_fight.tscn")
const Progress = preload("res://scripts/levels/chapter_progress.gd")
var checks: Array[Dictionary] = []
var rows: Array[Dictionary] = []
var mission: Node2D
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(label: String, value: bool) -> void:
	checks.append({"check":label,"passed":value})
	if not value: push_warning("FAIL "+label)
func freeze_except(actor: CharacterBody2D) -> void:
	mission.player.set_physics_process(false)
	mission.player.position = Vector2(-1024,-1024)
	mission.combat.set_physics_process(false)
	for other in mission.enemies:
		other.set_physics_process(other == actor)
func follow(actor: CharacterBody2D, goal: Vector2, ticks: int) -> Dictionary:
	var result := {"reached":false,"overlap":false,"jump":false,"ticks":0,"trail":[]}
	var prior := actor.position
	for tick in ticks:
		await frames(1)
		result.ticks = tick+1
		var collider: CollisionShape2D
		for child in actor.get_children():
			if child is CollisionShape2D and not child.disabled: collider = child; break
		assert(collider != null and collider.shape is RectangleShape2D)
		var rectangle: Rect2 = collider.global_transform * Rect2(-collider.shape.size*0.5,collider.shape.size)
		for blocker in mission.room_navigation.router.blockers:
			result.overlap = result.overlap or rectangle.intersects(blocker)
		result.jump = result.jump or prior.distance_to(actor.position) > float(actor.definition.speed)/60.0+0.15
		prior = actor.position
		if tick%12 == 0: result.trail.append({"tick":tick,"position":[prior.x,prior.y],"reason":mission.room_navigation.router.last_reason,"state":actor.state})
		if prior.distance_to(goal) < 4.1:
			result.reached = true
			break
	return result
func run() -> void:
	mission = Mission.instantiate()
	root.add_child(mission)
	await frames(3)
	mission.director._finish() # Targeted fixture setup, not real-input proof.
	await frames(3)
	mission.auto_retry = false
	check("production_host_loaded",mission.room_navigation.supported and mission.room_navigation.router.bounds == Rect2(0,0,1152,640))
	for actor in mission.enemies:
		freeze_except(actor)
		for route in ["service_door","hall_cover"]:
			actor.transition("patrol")
			var start := Vector2(336,544) if route == "service_door" else Vector2(480,400)
			var goal := Vector2(432,544) if route == "service_door" else Vector2(736,400)
			actor.position = start
			actor.patrol_target = goal
			actor.velocity = Vector2.ZERO
			var closed: Dictionary = {}
			if route == "service_door":
				mission._set_door("service",false)
				await frames(3)
				closed = await follow(actor,goal,90)
				check(actor.kind+"/closed_service",not closed.reached and actor.position.x < 368 and not closed.overlap and not closed.jump)
				var old_revision: int = mission.room_navigation.router.revision
				mission._set_door("service",true)
				await frames(3)
				check(actor.kind+"/deferred_open_synchronized",mission.doors.service.shape.disabled and mission.room_navigation.router.revision > old_revision)
			var opened := await follow(actor,goal,1500)
			check(actor.kind+"/"+route+"/reachable",opened.reached and not opened.overlap and not opened.jump and actor.animation_ready and actor.state == "patrol")
			rows.append({"kind":actor.kind,"route":route,"closed":closed,"opened":opened})
	# The existing checkpoint and real physical door must survive fresh scene load.
	for actor in mission.enemies: actor.set_physics_process(false)
	mission.has_key = true
	mission.player.position = Vector2(432,544)
	mission._checkpoint_if_crossed()
	check("checkpoint_persisted",mission.checkpoint == "service" and mission.progress.data.checkpoint == "service")
	var restored := Progress.new()
	check("fresh_save_object",restored.load_progress() and restored.data.checkpoint == "service")
	mission.player_died()
	mission.reset_encounter()
	await frames(3)
	check("retry_real_state",mission.player.health == 1 and mission.has_key and mission.doors.service.open and not mission.doors.street.open and mission.combat.attacks.is_empty() and mission.combat.projectiles.is_empty())
	check("retry_physical_doors",mission.doors.service.shape.disabled and not mission.doors.street.shape.disabled and mission.room_navigation.supported)
	mission.queue_free()
	await frames(3)
	mission = Mission.instantiate()
	root.add_child(mission)
	await frames(3)
	check("fresh_scene_checkpoint",mission.checkpoint == "service" and mission.has_key and mission.doors.service.shape.disabled and not mission.doors.street.shape.disabled and mission.room_navigation.supported)
	var passed := checks.filter(func(c: Dictionary):return c.passed).size()
	var file := FileAccess.open(OS.get_environment("AYAY_P07_ROOM_PILOT_RESULT"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"CH01_PRODUCTION_HOST_GEOMETRY_DOORS_DETOUR_RETRY_COMPONENT","checks":checks,"passed":passed,"failed":checks.size()-passed,"rows":rows,"route_actor_setup_warps":true,"chapter_playthrough_claim":false,"full_H02_Readiness_or_P07_approval":false},"  "))
	file.close()
	mission.queue_free()
	await frames(2)
	print("RESULT ROOM_PILOT %d/%d" % [passed,checks.size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed == checks.size() else 1)
