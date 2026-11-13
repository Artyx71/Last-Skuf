extends SceneTree
## Runtime pixels and frame occupancy; independent visual review is still required.

var passed := 0
var failed := 0


func _initialize() -> void:
	call_deferred("_run")


func _check(condition: bool, message: String) -> void:
	if condition:
		passed += 1
		print("PASS ", message)
	else:
		failed += 1
		push_error("FAIL " + message)


func _inspect(path: String, walking: bool) -> void:
	_check(ResourceLoader.exists(path), "native resource exists " + path)
	if not ResourceLoader.exists(path):
		return
	var image := (load(path) as Texture2D).get_image()
	_check(image.get_size() == Vector2i(384, 256), "48x64 x8x4 " + path)
	var colors := {}
	var partial := 0
	var transparent := 0
	for y in image.get_height():
		for x in image.get_width():
			var pixel := image.get_pixel(x, y)
			if pixel.a == 0:
				transparent += 1
			elif pixel.a == 1:
				colors[pixel.to_rgba32()] = true
			else:
				partial += 1
	_check(partial == 0, "binary alpha " + path)
	_check(colors.size() <= 64, "palette <=64 " + path)
	_check(transparent > image.get_width() * image.get_height() / 8, "transparent background " + path)
	for row in 4:
		var hashes := {}
		var bottoms: Array[int] = []
		for column in 8:
			var frame := image.get_region(Rect2i(column * 48, row * 64, 48, 64))
			var bounds := frame.get_used_rect()
			_check(bounds.has_area(), "nonempty frame %s %d/%d" % [path, row, column])
			_check(bounds.position.x > 0 and bounds.end.x < 48 and bounds.position.y > 0 and bounds.end.y < 64,
				"unclipped frame %s %d/%d" % [path, row, column])
			bottoms.append(bounds.end.y)
			if column >= 2:
				hashes[hash(frame.get_data())] = true
		if walking:
			_check(hashes.size() >= 4, "at least4 distinct walk poses " + path + str(row))
			_check(bottoms.max() - bottoms.min() <= 3, "stable walking foot anchor " + path + str(row))
	print("ART ", path, " colors=", colors.size(), " transparent=", transparent)


func _run() -> void:
	for kind in ["patrol", "rusher", "shooter"]:
		_inspect("res://assets/art/enemies/" + kind + "_sheet.png", true)
	_inspect("res://assets/art/yakuza/action_sheet.png", false)
	print("RESULT passed=%d failed=%d" % [passed, failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)
