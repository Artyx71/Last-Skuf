extends RefCounted
## Shared room adapter for actual world-layer rectangles and deferred doors.
## It reads physical geometry; mission objectives and AI states remain in hosts.
const Router = preload("res://scripts/ai/room_navigation.gd")
var router := Router.new()
var room: Node2D
var local_bounds := Rect2()
var supported := false

func setup(owner_room: Node2D, rectangle: Rect2) -> void:
	room = owner_room
	local_bounds = rectangle
	refresh()

func _collect(parent: Node, rectangles: Array[Rect2]) -> bool:
	for child in parent.get_children():
		if child is PhysicsBody2D and child.collision_layer & 1 != 0:
			for collider in child.get_children():
				if not collider is CollisionShape2D or collider.disabled: continue
				if not collider.shape is RectangleShape2D: return false
				var shape: RectangleShape2D = collider.shape
				# A rotated wall's AABB would invent impassable space. Restrict the
				# supported contract rather than claiming arbitrary geometry works.
				if not is_zero_approx(collider.global_rotation): return false
				rectangles.append(collider.global_transform * Rect2(-shape.size*0.5,shape.size))
		if not _collect(child,rectangles): return false
	return true

func refresh() -> void:
	supported = is_instance_valid(room) and is_zero_approx(room.global_rotation) and room.global_scale.is_equal_approx(Vector2.ONE)
	if not supported: return
	var rectangles: Array[Rect2] = []
	supported = _collect(room,rectangles)
	if not supported: return
	var world := Rect2(room.to_global(local_bounds.position),local_bounds.size)
	if world != router.bounds or rectangles != router.blockers:
		router.configure(world,rectangles)

func velocity_for(body: CharacterBody2D, local_goal: Vector2, speed: float) -> Vector2:
	if not supported: return Vector2.ZERO
	return router.velocity_for(body,room.to_global(local_goal),speed,body.get_physics_process_delta_time())

func reset_paths() -> void:
	router.reset_paths()
