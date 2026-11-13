extends SceneTree
## Structural/protected-region checks. Independent visual motion review is still required.

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


func _run() -> void:
	var texture := load("res://assets/art/yakuza/portrait_motion.png") as Texture2D
	var base_texture := load("res://assets/art/yakuza/portraits.png") as Texture2D
	_check(texture != null and base_texture != null, "real portrait textures imported")
	if texture == null or base_texture == null:
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1)
		return
	var sheet := texture.get_image()
	var original := base_texture.get_image()
	# Texture import fixes RGB in fully transparent border pixels according to the
	# atlas layout. Check source RGBA exactly and imported visible pixels separately.
	var source_sheet := Image.load_from_file(ProjectSettings.globalize_path("res://assets/art/yakuza/portrait_motion.png"))
	var source_base := Image.load_from_file(ProjectSettings.globalize_path("res://assets/art/yakuza/portraits.png"))
	var metadata: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/art/yakuza/portrait_motion_atlas.json"))
	_check(sheet.get_size() == Vector2i(480, 320), "six native 160px feature frames")
	_check(int(metadata.get("schema", 0)) == 1, "versioned motion atlas")
	_check(metadata.get("emotions", []) == ["neutral", "angry"], "two authored emotions")
	_check(metadata.get("states", []) == ["rest", "talk", "blink"], "rest talk blink layout")
	var frames: Array = metadata.get("frames", [])
	_check(frames.size() == 6, "all six frame records present")
	var root_path := ProjectSettings.globalize_path("res://").trim_suffix("/").get_base_dir()
	var palette := {}
	for index in frames.size():
		var record: Dictionary = frames[index]
		var rect: Array = record["rect"]
		var frame := sheet.get_region(Rect2i(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))
		var row := index / 3
		var base := original.get_region(Rect2i(int(row) * 160, 0, 160, 160))
		var raw_frame := source_sheet.get_region(Rect2i(int(rect[0]), int(rect[1]), int(rect[2]), int(rect[3])))
		var raw_base := source_base.get_region(Rect2i(int(row) * 160, 0, 160, 160))
		var label := str(record["id"])
		var mask: Image
		if record.get("mask") != null:
			mask = Image.load_from_file(root_path.path_join(str(record["mask"])))
			_check(mask != null and mask.get_size() == Vector2i(160, 160), label + " saved feature mask")
		var changed := 0
		var outside := 0
		var mask_area := 0
		var alpha_matches := true
		var binary_alpha := true
		var visible_outside := 0
		for y in 160:
			for x in 160:
				var pixel := frame.get_pixel(x, y)
				var approved := base.get_pixel(x, y)
				var inside: bool = mask != null and mask.get_pixel(x, y).r > 0.5
				if inside:
					mask_area += 1
				if raw_frame.get_pixel(x, y) != raw_base.get_pixel(x, y):
					changed += 1
					if not inside:
						outside += 1
				if pixel.a > 0.0 and pixel != approved and not inside:
					visible_outside += 1
				alpha_matches = alpha_matches and pixel.a == approved.a
				binary_alpha = binary_alpha and pixel.a in [0.0, 1.0]
				if pixel.a == 1.0:
					palette[pixel.to_rgba32()] = true
		_check(alpha_matches, label + " preserves approved silhouette alpha")
		_check(binary_alpha, label + " binary pixel alpha")
		_check(frame.get_used_rect().size.y > 100, label + " nonempty portrait")
		_check(visible_outside == 0, label + " imported visible protected pixels unchanged")
		if str(record["state"]) == "rest":
			_check(changed == 0, label + " approved RGBA unchanged")
		else:
			_check(changed > 50, label + " real feature pixel changes")
			_check(mask_area > 50 and mask_area < 1600, label + " bounded feature-only mask")
			_check(outside == 0, label + " no edits outside saved feature mask")
	_check(palette.size() <= 31, "motion stays within approved 31-color palette")
	print("RESULT passed=%d failed=%d" % [passed, failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)
