extends RefCounted
## Optional room-host routing. Combat clocks, FSM and collision masks stay owned
## by the existing actor/Core. Geometry is in logical world pixels.
## AStarGrid2D API: https://docs.godotengine.org/en/stable/classes/class_astargrid2d.html
const CELL := 16.0
const MARGIN := 0.5
var bounds := Rect2()
var blockers: Array[Rect2] = []
var revision := 0
var grids: Dictionary = {}
var paths: Dictionary = {}
var requests := 0
var replans := 0
var last_reason := "unconfigured"

func configure(world: Rect2, rectangles: Array[Rect2]) -> void:
	bounds = world
	blockers.assign(rectangles)
	revision += 1
	grids.clear()
	paths.clear()
	last_reason = "layout_changed"

func reset_paths() -> void:
	paths.clear()

func _foot(body: CharacterBody2D) -> Rect2:
	if not is_zero_approx(body.global_rotation) or not body.global_scale.is_equal_approx(Vector2.ONE): return Rect2()
	var result := Rect2()
	var found := false
	for child in body.get_children():
		if not child is CollisionShape2D or child.disabled: continue
		if not child.shape is RectangleShape2D or not is_zero_approx(child.rotation) or not child.scale.is_equal_approx(Vector2.ONE): return Rect2()
		var shape: RectangleShape2D = child.shape
		var rectangle := Rect2(child.position - shape.size * 0.5, shape.size)
		result = result.merge(rectangle) if found else rectangle
		found = true
	return result

func _grid(foot: Rect2) -> AStarGrid2D:
	var key := str(foot)
	if grids.has(key): return grids[key]
	if grids.size() >= 8: grids.clear()
	var grid := AStarGrid2D.new()
	grid.region = Rect2i(Vector2i.ZERO, Vector2i(ceili(bounds.size.x/CELL)+1,ceili(bounds.size.y/CELL)+1))
	grid.cell_size = Vector2(CELL,CELL)
	grid.offset = bounds.position
	grid.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_NEVER
	grid.default_compute_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	grid.default_estimate_heuristic = AStarGrid2D.HEURISTIC_MANHATTAN
	grid.update()
	for y in grid.region.size.y:
		for x in grid.region.size.x:
			var id := Vector2i(x,y)
			var rectangle := Rect2(grid.get_point_position(id)+foot.position,foot.size).grow(MARGIN)
			var solid := not bounds.encloses(rectangle)
			for wall in blockers:
				if rectangle.intersects(wall):
					solid = true
					break
			grid.set_point_solid(id,solid)
	grids[key] = grid
	return grid

func _cell(point: Vector2) -> Vector2i:
	return Vector2i(roundi((point.x-bounds.position.x)/CELL),roundi((point.y-bounds.position.y)/CELL))

func _toward(body: CharacterBody2D, point: Vector2, speed: float, delta: float) -> Vector2:
	var displacement := point-body.global_position
	return displacement.normalized()*minf(speed,displacement.length()/maxf(delta,0.000001))

func velocity_for(body: CharacterBody2D, goal: Vector2, speed: float, delta: float) -> Vector2:
	requests += 1
	if bounds.size.x <= 0 or bounds.size.y <= 0 or speed <= 0 or delta <= 0:
		last_reason = "invalid_request"
		return Vector2.ZERO
	var foot := _foot(body)
	if foot.size.x <= 0 or foot.size.y <= 0:
		last_reason = "unsupported_collider"
		return Vector2.ZERO
	# The direct sweep only knows physical walls. Respect the host's navigation
	# boundary even when no wall was authored along its edge.
	if not bounds.encloses(Rect2(body.global_position+foot.position,foot.size).grow(MARGIN)) or not bounds.encloses(Rect2(goal+foot.position,foot.size).grow(MARGIN)):
		last_reason = "outside_endpoint"
		return Vector2.ZERO
	if body.global_position.distance_to(goal) <= 3.0:
		last_reason = "arrived"
		return Vector2.ZERO
	body.force_update_transform()
	# Prefer the actual swept body when a direct path is clear. No grid snapping
	# or changes to position/masks/health/animation/attack eligibility happen here.
	if not body.test_move(body.global_transform,goal-body.global_position,null,0.08,true):
		paths.erase(body.get_instance_id())
		last_reason = "direct_sweep_clear"
		return _toward(body,goal,speed,delta)
	var grid := _grid(foot)
	var start := _cell(body.global_position)
	var end := _cell(goal)
	if not grid.is_in_boundsv(start) or not grid.is_in_boundsv(end) or grid.is_point_solid(start) or grid.is_point_solid(end):
		last_reason = "blocked_or_outside_endpoint"
		return Vector2.ZERO
	var id := body.get_instance_id()
	var rebuild := not paths.has(id)
	if not rebuild:
		var old: Dictionary = paths[id]
		rebuild = old.revision != revision or old.goal.distance_to(goal) > 4.0 or old.foot != foot
		if not rebuild and old.index < old.points.size():
			rebuild = body.global_position.distance_to(old.points[old.index]) > CELL*2.5
	if rebuild:
		if paths.size() >= 128: paths.clear()
		var points := grid.get_point_path(start,end)
		paths[id] = {"goal":goal,"foot":foot,"revision":revision,"points":points,"index":0}
		replans += 1
	var route: Dictionary = paths[id]
	while route.index < route.points.size() and body.global_position.distance_to(route.points[route.index]) <= 0.1:
		route.index += 1
	if route.index >= route.points.size():
		last_reason = "no_route"
		return Vector2.ZERO
	var waypoint: Vector2 = route.points[route.index]
	var motion := _toward(body,waypoint,speed,delta)*delta
	if body.test_move(body.global_transform,motion,null,0.08,true):
		paths.erase(id)
		last_reason = "physical_blocker_replan_required"
		return Vector2.ZERO
	last_reason = "grid_route"
	return motion/delta
