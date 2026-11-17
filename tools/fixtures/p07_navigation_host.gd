extends "res://scripts/core/combat_lab.gd"
## QA/mission-pipeline host: optional adapter, same actual actors/Core/FSM.
const Router = preload("res://scripts/ai/room_navigation.gd")
var navigation := Router.new()
func _ready() -> void:
	super._ready()
	refresh_navigation()
func refresh_navigation() -> void:
	var rectangles: Array[Rect2] = []
	for child in get_children():
		if not child is PhysicsBody2D or child.collision_layer & 1 == 0: continue
		for collider in child.get_children():
			if collider is CollisionShape2D and not collider.disabled:
				assert(collider.shape is RectangleShape2D, "Pilot uses actual rectangle blockers")
				var shape: RectangleShape2D = collider.shape
				rectangles.append(collider.global_transform * Rect2(-shape.size*0.5,shape.size))
	if rectangles != navigation.blockers:
		navigation.configure(Rect2(0,0,640,360),rectangles)
func _physics_process(delta: float) -> void:
	refresh_navigation()
	super._physics_process(delta)
func navigation_velocity(body: CharacterBody2D, target: Vector2, speed: float) -> Vector2:
	return navigation.velocity_for(body,to_global(target),speed,body.get_physics_process_delta_time())
func reset_encounter() -> void:
	super.reset_encounter()
	if navigation != null: navigation.reset_paths()
