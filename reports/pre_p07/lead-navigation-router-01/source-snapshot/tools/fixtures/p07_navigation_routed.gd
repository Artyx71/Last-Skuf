extends SceneTree
## Real existing AI/Physics baseline. Diagnostic geometry, not a campaign level.
const Lab = preload("res://tests/p07_navigation_host.gd")
var rows: Array[Dictionary] = []
func _initialize() -> void: call_deferred("run")
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func run() -> void:
	for layout in ["open", "u_obstacle"]:
		for kind in ["patrol", "rusher", "shooter"]:
			var lab := Lab.new()
			lab.config_path = "res://tests/fixtures/p07_nav_" + layout + "_" + kind + ".json"
			lab.auto_retry = false
			root.add_child(lab)
			current_scene = lab
			# Patrol routing is isolated from combat by an actual distant player,
			# never a fake sees_player()/collision implementation.
			lab.player.set_physics_process(false)
			lab.player.position = Vector2(-1024, -1024)
			await frames(3)
			var enemy: CharacterBody2D = lab.enemies[0]
			var goal: Vector2 = enemy.patrol_end
			var trail: Array[Dictionary] = []
			var history: Array[Vector2] = []
			var reached := false
			var stuck := false
			var used_ticks := 0
			for tick in 1800:
				await frames(1)
				used_ticks = tick + 1
				history.append(enemy.position)
				if tick % 6 == 0:
					trail.append({"tick":tick,"position":[enemy.position.x,enemy.position.y],"state":enemy.state,"velocity":[enemy.velocity.x,enemy.velocity.y]})
				if enemy.position.distance_to(goal) < 4.1:
					reached = true
					break
				if history.size() > 120 and enemy.position.distance_to(history[history.size()-121]) < 0.25:
					stuck = true
					break
			rows.append({"layout":layout,"archetype":kind,"goal":[goal.x,goal.y],"final":[enemy.position.x,enemy.position.y],"goal_reached":reached,"stuck_120_ticks":stuck,"physics_ticks":used_ticks,"art_loaded":enemy.animation_ready,"state":enemy.state,"transitions":enemy.transitions.duplicate(),"trail":trail,"navigation_requests":lab.navigation.requests,"navigation_replans":lab.navigation.replans,"navigation_reason":lab.navigation.last_reason})
			lab.queue_free()
			await frames(3)
	var controls := rows.filter(func(row: Dictionary):return row.layout == "open")
	var obstacles := rows.filter(func(row: Dictionary):return row.layout == "u_obstacle")
	var valid: bool = rows.size() == 6 and controls.all(func(row: Dictionary):return row.goal_reached and row.art_loaded) and rows.all(func(row: Dictionary):return row.state == "patrol")
	var gaps: int = obstacles.filter(func(row: Dictionary):return not row.goal_reached and row.stuck_120_ticks).size()
	var output := OS.get_environment("AYAY_P07_NAV_BASELINE_OUTPUT")
	var file := FileAccess.open(output, FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"OPTIONAL_ROUTER_ACTUAL_AI_PATROL_PROBE_NOT_CAMPAIGN_OR_FPS","diagnostic_valid":valid,"u_obstacle_unreached":gaps,"rows":rows,"player_isolation":"Real player kept off-map with physics disabled, no sight/collision stubs","timing":"fixed-fps physics ticks only; no live FPS/latency/duration claim","P06_phase_status_changed":false,"readiness_H02_pass":false},"  "))
	file.close()
	print("RESULT P07_NAV_BASELINE valid=%s U_route_gaps=%d controls=%d" % [str(valid),gaps,controls.size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if valid else 1)
