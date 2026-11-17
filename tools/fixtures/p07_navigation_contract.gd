extends SceneTree
## Actual P06 actors, physics, attacks and art. Synthetic navigation fixtures only.
const Host = preload("res://tests/p07_navigation_host.gd")
var checks: Array[Dictionary] = []
var rows: Array[Dictionary] = []
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func check(label: String, value: bool) -> void:
	checks.append({"check":label,"passed":value})
	if not value: push_warning("FAIL " + label)
func create_lab(scenario: String, kind: String) -> Node2D:
	var lab := Host.new()
	lab.config_path = "res://tests/fixtures/nav_contract_" + scenario + "_" + kind + ".json"
	lab.auto_retry = false
	root.add_child(lab)
	current_scene = lab
	lab.player.set_physics_process(false)
	return lab
func overlaps(lab: Node2D, enemy: CharacterBody2D) -> bool:
	# Independent physical shape extraction, not the router's occupied cells.
	var shape: CollisionShape2D = enemy.get_node("@CollisionShape2D@1") if enemy.has_node("@CollisionShape2D@1") else null
	for child in enemy.get_children():
		if child is CollisionShape2D and not child.disabled: shape = child; break
	assert(shape != null and shape.shape is RectangleShape2D)
	var rect: Rect2 = shape.global_transform * Rect2(-shape.shape.size*0.5,shape.shape.size)
	for wall in lab.navigation.blockers:
		if rect.intersects(wall): return true
	return false
func track(lab: Node2D, ticks: int, stop_at_goal := false) -> Dictionary:
	var enemy: CharacterBody2D = lab.enemies[0]
	var result := {"reached":false,"overlap":false,"jump":false,"trail":[],"ticks":0}
	var prior := enemy.global_position
	for tick in ticks:
		await frames(1)
		result.ticks = tick+1
		result.overlap = result.overlap or overlaps(lab,enemy)
		result.jump = result.jump or prior.distance_to(enemy.global_position) > float(enemy.definition.speed)/60.0+0.15
		prior = enemy.global_position
		if tick%12 == 0: result.trail.append({"tick":tick,"position":[prior.x,prior.y],"state":enemy.state,"reason":lab.navigation.last_reason})
		if enemy.global_position.distance_to(enemy.patrol_end) < 4.1:
			result.reached = true
			if stop_at_goal: break
	return result
func remove_door(lab: Node2D) -> void:
	for body in lab.get_children():
		if not body is StaticBody2D: continue
		for collider in body.get_children():
			if collider is CollisionShape2D and collider.shape is RectangleShape2D and collider.shape.size == Vector2(16,328):
				body.queue_free()
func run() -> void:
	for kind in ["patrol","rusher","shooter"]:
		for scenario in ["door","narrow","wide","alternate","dynamic"]:
			var lab := create_lab(scenario,kind)
			await frames(3)
			var enemy: CharacterBody2D = lab.enemies[0]
			if scenario == "dynamic":
				await frames(20)
				lab._add_wall(Rect2(312,16,16,328))
				await frames(3)
			var closed: Dictionary = {}
			if scenario in ["door","dynamic","narrow"]:
				closed = await track(lab,180)
				check(kind+"/"+scenario+"/blocked",not closed.reached and enemy.position.x < 304 and not closed.overlap and not closed.jump)
			if scenario in ["door","dynamic"]:
				var revision: int = lab.navigation.revision
				remove_door(lab)
				await frames(3)
				check(kind+"/"+scenario+"/layout_invalidated",lab.navigation.revision > revision)
			var opened: Dictionary = {}
			if scenario != "narrow":
				opened = await track(lab,1400,true)
				check(kind+"/"+scenario+"/reached",opened.reached and not opened.overlap and not opened.jump)
			check(kind+"/"+scenario+"/combat_untouched",enemy.health > 0 and lab.kills == 0 and lab.score == 0 and enemy.attacks_started == 0 and enemy.animation_ready)
			lab.reset_encounter()
			check(kind+"/"+scenario+"/reset",lab.navigation.paths.is_empty() and enemy.position == enemy.spawn_position and enemy.state == "patrol")
			rows.append({"kind":kind,"scenario":scenario,"closed":closed,"opened":opened,"requests":lab.navigation.requests,"replans":lab.navigation.replans})
			lab.queue_free()
			await frames(3)
	# A clear physics sweep is not permission to leave navigation bounds.
	var boundary := create_lab("wide","patrol")
	await frames(3)
	var actor: CharacterBody2D = boundary.enemies[0]
	actor.set_physics_process(false)
	var before := actor.position
	for goal in [Vector2(-32,192),Vector2(672,192),Vector2(160,-32),Vector2(160,392)]:
		check("boundary/"+str(goal),boundary.navigation.velocity_for(actor,goal,36,1.0/60.0) == Vector2.ZERO and boundary.navigation.last_reason == "outside_endpoint")
	check("boundary/no_mutation",actor.position == before and actor.collision_layer == 4 and actor.collision_mask == 1)
	check("invalid/speed",boundary.navigation.velocity_for(actor,Vector2(480,192),0,1.0/60.0) == Vector2.ZERO)
	check("invalid/delta",boundary.navigation.velocity_for(actor,Vector2(480,192),36,0) == Vector2.ZERO)
	boundary.queue_free()
	await frames(3)
	# Actual LOS/FSM/contact checks: routing cannot grant wall vision or attacks.
	for kind in ["patrol","rusher","shooter"]:
		for scenario in ["los_closed","los_open"]:
			var lab := create_lab(scenario,kind)
			await frames(3)
			var enemy: CharacterBody2D = lab.enemies[0]
			var states: Array[String] = []
			for tick in 240:
				await frames(1)
				if not enemy.state in states: states.append(enemy.state)
				if lab.player.health <= 0: break
			if scenario == "los_closed":
				check(kind+"/LOS/wall_blocks",not enemy.sees_player() and enemy.attacks_started == 0 and lab.player.health > 0)
			else:
				check(kind+"/LOS/telegraphed_contact",enemy.attacks_started > 0 and "telegraph" in states and "attack" in states and lab.player.health == 0 and lab.total_deaths == 1)
			rows.append({"kind":kind,"scenario":scenario,"states":states,"attacks":enemy.attacks_started,"player_health":lab.player.health,"total_deaths":lab.total_deaths})
			lab.queue_free()
			await frames(3)
	var passed := checks.filter(func(c: Dictionary):return c.passed).size()
	var file := FileAccess.open(OS.get_environment("AYAY_P07_NAV_CONTRACT_OUTPUT"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"OPTIONAL_ROUTER_DOOR_CHOKE_DYNAMIC_LOS_COMPONENT_NOT_FULL_READINESS","checks":checks,"passed":passed,"failed":checks.size()-passed,"rows":rows,"fixed_fps_ticks_not_performance":true,"full_H02_or_P07_approval":false},"  "))
	file.close()
	print("RESULT NAV_CONTRACT %d/%d" % [passed,checks.size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed == checks.size() else 1)
