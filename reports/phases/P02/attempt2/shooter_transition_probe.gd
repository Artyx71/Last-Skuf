extends SceneTree

var elapsed_frames := 0
var all_sprites: Array[AnimatedSprite2D] = []
var state_label: Label
var output_dir: String
var records: Array[Dictionary] = []
var previous_state := ""

func _initialize() -> void:
	call_deferred("setup")

func setup() -> void:
	output_dir = OS.get_environment("AYAY_SHOOTER_PROBE_OUTPUT")
	root.size = Vector2i(640, 360)
	root.content_scale_size = Vector2i(640, 360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	RenderingServer.set_default_clear_color(Color("242835"))
	var heading := Label.new()
	heading.text = "Shooter idle / walk transition | 640 x 360"
	heading.position = Vector2(45, 15)
	heading.add_theme_font_size_override("font_size", 21)
	root.add_child(heading)
	for info in [["BEFORE", 145], ["AFTER", 405]]:
		var label := Label.new()
		label.text = info[0]
		label.position = Vector2(info[1], 50)
		root.add_child(label)
	state_label = Label.new()
	state_label.position = Vector2(25, 82)
	root.add_child(state_label)
	var guide := Line2D.new()
	guide.add_point(Vector2(70, 180))
	guide.add_point(Vector2(575, 180))
	guide.width = 1
	guide.default_color = Color("586276")
	root.add_child(guide)
	var guide2 := Line2D.new()
	guide2.add_point(Vector2(70, 330))
	guide2.add_point(Vector2(575, 330))
	guide2.width = 1
	guide2.default_color = Color("586276")
	root.add_child(guide2)
	var local_root := ProjectSettings.globalize_path("res://").get_base_dir().get_base_dir()
	var paths := [output_dir.path_join("shooter_before.png"), local_root.path_join("game/assets/art/enemies/shooter_sheet.png")]
	for version in range(2):
		var image := Image.load_from_file(paths[version])
		var texture := ImageTexture.create_from_image(image)
		for row in [0, 3]:
			var direction_index := 0 if row == 0 else 1
			var frames := SpriteFrames.new()
			frames.remove_animation("default")
			for animation in ["idle", "walk"]:
				frames.add_animation(animation)
				frames.set_animation_speed(animation, 3.0 if animation == "idle" else 8.0)
				frames.set_animation_loop(animation, true)
				var columns: Array = [0, 1] if animation == "idle" else [2, 3, 4, 5, 6, 7]
				for column in columns:
					var region := AtlasTexture.new()
					region.atlas = texture
					region.region = Rect2(column * 48, row * 64, 48, 64)
					frames.add_frame(animation, region)
			for scale_factor in [1, 2]:
				var sprite := AnimatedSprite2D.new()
				sprite.sprite_frames = frames
				sprite.centered = false
				sprite.offset = Vector2(-24, -58)
				sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
				sprite.position = Vector2(130 + version * 260 + direction_index * 110, 180 if scale_factor == 1 else 330)
				sprite.scale = Vector2.ONE * scale_factor
				root.add_child(sprite)
				sprite.play("idle")
				all_sprites.append(sprite)

func _process(_delta: float) -> bool:
	if all_sprites.is_empty():
		return false
	var local_frame := elapsed_frames % 132
	var state := "walk" if local_frame >= 36 and local_frame < 96 else "idle"
	if state != previous_state:
		for sprite in all_sprites:
			sprite.play(state)
			sprite.frame = 0
		previous_state = state
	state_label.text = "%s | idle 3 FPS, walk 8 FPS | native above, 2x below" % state.to_upper()
	records.append({"movie_frame": elapsed_frames, "state": state, "actual_animation_frame": all_sprites[0].frame, "after_frame": all_sprites[4].frame})
	if elapsed_frames in [30, 40, 75, 100]:
		capture.call_deferred(elapsed_frames)
	elapsed_frames += 1
	if elapsed_frames >= 396:
		var report := {"actual_godot_probe": true, "movie_fps": 60, "logical_canvas": [640, 360], "walk_fps": 8, "idle_fps": 3, "cycles": 3, "frames": records, "review_status": "AUTHOR_VISUAL_INSPECTION_PENDING_NOT_INDEPENDENT_PASS"}
		var file := FileAccess.open(output_dir.path_join("shooter_transition_probe.json"), FileAccess.WRITE)
		file.store_string(JSON.stringify(report, "\t") + "\n")
		quit(0)
	return false

func capture(frame_number: int) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output_dir.path_join("shooter_transition_%03d.png" % frame_number))
