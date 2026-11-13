extends SceneTree
## Structural checks only. Passing this never certifies likeness or artistic quality.

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


func _pixel_structure(image: Image, label: String) -> void:
	var colors := {}
	var partial_alpha := 0
	var transparent := 0
	for y in image.get_height():
		for x in image.get_width():
			var pixel := image.get_pixel(x, y)
			if pixel.a == 0.0:
				transparent += 1
			elif pixel.a == 1.0:
				colors[pixel.to_rgba32()] = true
			else:
				partial_alpha += 1
	_check(partial_alpha == 0, label + " binary alpha without baked smooth fringe")
	_check(transparent > image.get_width() * image.get_height() * 0.05, label + " meaningful transparency")
	_check(colors.size() <= 64, label + " controlled palette <=64 colors")
	print(label, " colors=", colors.size(), " transparent=", transparent)


func _run() -> void:
	var sheet := (load("res://assets/art/yakuza/world_sheet.png") as Texture2D).get_image()
	var portraits := (load("res://assets/art/yakuza/portraits.png") as Texture2D).get_image()
	var past := (load("res://assets/art/yakuza/portraits_past.png") as Texture2D).get_image()
	_check(not sheet.is_empty() and sheet.get_size() == Vector2i(384, 256), "world sheet native 48x64 x 8 x 4")
	_check(not portraits.is_empty() and portraits.get_size() == Vector2i(800, 160), "five native 160px portraits")
	_check(not past.is_empty() and past.get_size() == Vector2i(800, 160), "five native flashback portraits")
	if sheet.is_empty() or portraits.is_empty():
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1)
		return
	_pixel_structure(sheet, "world")
	_pixel_structure(portraits, "portraits")
	_pixel_structure(past, "flashback")
	_check(hash(past.get_data()) != hash(portraits.get_data()), "separate authored eras")
	for row in 4:
		var walk_hashes := {}
		var bottoms: Array[int] = []
		for column in 8:
			var frame := sheet.get_region(Rect2i(column * 48, row * 64, 48, 64))
			var bounds := frame.get_used_rect()
			_check(bounds.has_area(), "nonempty frame %d/%d" % [row, column])
			_check(bounds.position.x > 0 and bounds.end.x < 48 and bounds.position.y > 0 and bounds.end.y <= 62,
				"unclipped frame %d/%d" % [row, column])
			bottoms.append(bounds.end.y)
			if column >= 2:
				walk_hashes[hash(frame.get_data())] = true
		_check(walk_hashes.size() >= 4, "distinct walk poses row " + str(row))
		_check(bottoms.max() - bottoms.min() <= 3, "stable foot anchor row " + str(row))
	for index in 5:
		var frame := portraits.get_region(Rect2i(index * 160, 0, 160, 160))
		_check(frame.get_used_rect().size.y > 100, "portrait filled " + str(index))
	print("RESULT passed=%d failed=%d" % [passed, failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)
