extends SceneTree
## Exercise native physics, input and the actual generated SpriteFrames.

const Bindings = preload("res://scripts/core/input_bindings.gd")
var passed := 0
var failed := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, title: String) -> void:
	if condition:
		passed += 1
		print("PASS ", title)
	else:
		failed += 1
		push_error("FAIL " + title)


func _frames(count: int) -> void:
	for index in count:
		await physics_frame


func _run() -> void:
	Bindings.install()
	var lab: Node2D = load("res://scenes/world/movement_lab.tscn").instantiate()
	root.add_child(lab)
	await _frames(2)
	var actor: CharacterBody2D = lab.actor
	for action in ["move_left", "move_right", "move_up", "move_down"]:
		_check(InputMap.action_get_events(action).size() == 2, action + " WASD + arrow binding")
	actor.position = Vector2(80, 110)
	var start := actor.position
	Input.action_press("move_right")
	await _frames(30)
	Input.action_release("move_right")
	await _frames(2)
	var horizontal := actor.position.distance_to(start)
	_check(horizontal > 36.0 and horizontal < 45.0, "fixed-step movement speed")
	_check(actor.facing == &"right", "right facing follows input")
	_check(actor.sprite.animation == &"idle_right", "release restores idle facing")
	actor.position = start
	Input.action_press("move_right")
	Input.action_press("move_down")
	await _frames(30)
	Input.action_release("move_right")
	Input.action_release("move_down")
	await _frames(2)
	_check(absf(actor.position.distance_to(start) - horizontal) < 3.0, "diagonal speed normalized")
	for direction in ["down", "left", "right", "up"]:
		actor.position = Vector2(90, 180)
		Input.action_press("move_" + direction)
		await _frames(3)
		_check(actor.sprite.animation == StringName("walk_" + direction), "directional walk " + direction)
		var old_frame: int = actor.sprite.frame
		await _frames(10)
		_check(actor.sprite.frame != old_frame, "actual animation advances " + direction)
		Input.action_release("move_" + direction)
		await _frames(2)
		_check(actor.sprite.animation == StringName("idle_" + direction), "directional idle " + direction)
	actor.position = Vector2(412, 210)
	Input.action_press("move_right")
	await _frames(30)
	Input.action_release("move_right")
	await _frames(2)
	_check(actor.position.x <= 424.1, "solid wall prevents crossing")
	actor.position = Vector2(160, 194)
	Input.action_press("move_right")
	await _frames(30)
	Input.action_release("move_right")
	await _frames(2)
	_check(actor.position.x <= 178.1, "interior prop blocks actor")
	for index in 5:
		lab.set_expression(index)
		_check(lab.portrait.texture.region.position.x == index * 160, "portrait expression " + str(index))
	var present_texture: Texture2D = lab.portrait.texture.atlas
	lab.set_past_version(true)
	_check(lab.portrait.texture.atlas != present_texture, "flashback switches actual portrait source")
	for index in 5:
		lab.set_expression(index)
		_check(lab.portrait.texture.region.position.x == index * 160, "flashback expression " + str(index))
	lab.set_past_version(false)
	_check(lab.portrait.texture.atlas == present_texture, "return to present source")
	print("RESULT passed=%d failed=%d" % [passed, failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)
