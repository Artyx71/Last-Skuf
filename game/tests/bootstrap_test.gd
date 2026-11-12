extends SceneTree
## Dependency-free native integration harness, versioned with this repository.

var failed := 0
var passed := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, title: String) -> void:
	if condition:
		passed += 1
		print("PASS ", title)
	else:
		failed += 1
		push_error("FAIL " + title)


func _run() -> void:
	_check(ProjectSettings.get_setting("display/window/size/viewport_width") == 640, "logical width")
	_check(ProjectSettings.get_setting("display/window/size/viewport_height") == 360, "logical height")
	_check(ProjectSettings.get_setting("rendering/textures/canvas_textures/default_texture_filter") == 0, "nearest filter")
	_check(ProjectSettings.get_setting("display/window/stretch/scale_mode") == "integer", "integer scaling")
	var scene: PackedScene = load("res://scenes/bootstrap/bootstrap.tscn")
	var instance := scene.instantiate()
	root.add_child(instance)
	await process_frame
	var labels := instance.find_children("*", "Label", true, false)
	var has_disclaimer := false
	var has_scope := false
	for label in labels:
		has_disclaimer = has_disclaimer or "не являются утверждениями" in label.text
		has_scope = has_scope or "ещё не реализован" in label.text
	_check(has_disclaimer, "fiction disclaimer visible in scene")
	_check(has_scope, "bootstrap scope explicit")
	print("RESULT passed=%d failed=%d" % [passed, failed])
	quit(1 if failed else 0)
