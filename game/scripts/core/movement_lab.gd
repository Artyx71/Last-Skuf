extends Node2D
## Deliberately labelled technical lab. Environment geometry is not mission art.

const InputBindings = preload("res://scripts/core/input_bindings.gd")
const Actor = preload("res://scripts/actors/yakuza_actor.gd")
const EXPRESSIONS := ["СПОКОЕН", "ЗЛИТСЯ", "УДИВЛЁН", "РАНЕН", "АЫАЫ"]
var actor: CharacterBody2D
var portrait: TextureRect
var emotion_label: Label
var expression := 0
var past_version := false


func _ready() -> void:
	InputBindings.install()
	for wall in [Rect2(12, 46, 428, 8), Rect2(12, 314, 428, 8), Rect2(12, 46, 8, 276),
			Rect2(432, 46, 8, 276), Rect2(186, 148, 32, 98), Rect2(292, 96, 68, 32)]:
		_add_wall(wall)
	actor = Actor.new()
	actor.position = Vector2(106, 188)
	add_child(actor)
	_add_label("P01 / ЛАБОРАТОРИЯ ДВИЖЕНИЯ", Vector2(18, 12), 18, Color("66e5cc"))
	_add_label("WASD/стрелки · 1–5: эмоции · Tab: эпоха · Esc", Vector2(18, 334), 12, Color("b9b9cc"))
	_add_label("ЯКУДЗА", Vector2(458, 14), 22, Color("ff477e"))
	portrait = TextureRect.new()
	portrait.position = Vector2(458, 54)
	portrait.size = Vector2(160, 160)
	portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(portrait)
	emotion_label = _add_label("", Vector2(458, 224), 12, Color("66e5cc"))
	_add_label("АРТ-КАНДИДАТ\nСходство не утверждено.\n\nТехнический стенд.\nЭто ещё не миссия.", Vector2(458, 250), 12, Color("b9b9cc"))
	set_expression(0)
	if OS.get_environment("AYAY_LAB_PAST") == "1":
		set_past_version(true)
	if "--lab-replay" in OS.get_cmdline_user_args():
		call_deferred("_replay")
	if "--capture-lab" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		var output := OS.get_environment("AYAY_CAPTURE_PATH")
		if output.is_empty():
			get_tree().quit(1)
			return
		get_tree().quit(get_viewport().get_texture().get_image().save_png(output))


func _draw() -> void:
	draw_rect(Rect2(20, 54, 412, 260), Color("141622"))
	for x in range(20, 433, 16):
		draw_line(Vector2(x, 54), Vector2(x, 314), Color("202333"))
	for y in range(54, 315, 16):
		draw_line(Vector2(20, y), Vector2(432, y), Color("202333"))
	draw_line(Vector2(448, 12), Vector2(448, 324), Color("49465b"), 1.0)


func _add_wall(rectangle: Rect2) -> void:
	var body := StaticBody2D.new()
	body.position = rectangle.get_center()
	body.collision_layer = 1
	body.collision_mask = 2
	var shape := CollisionShape2D.new()
	var bounds := RectangleShape2D.new()
	bounds.size = rectangle.size
	shape.shape = bounds
	body.add_child(shape)
	var visual := Polygon2D.new()
	var half := rectangle.size * 0.5
	visual.polygon = PackedVector2Array([-half, Vector2(half.x, -half.y), half, Vector2(-half.x, half.y)])
	visual.color = Color("4e475c")
	body.add_child(visual)
	add_child(body)


func _add_label(text: String, at: Vector2, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.position = at
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	add_child(label)
	return label


func set_expression(index: int) -> void:
	expression = clampi(index, 0, 4)
	var atlas := AtlasTexture.new()
	var filename := "portraits_past.png" if past_version else "portraits.png"
	atlas.atlas = load("res://assets/art/yakuza/" + filename)
	atlas.region = Rect2(expression * 160, 0, 160, 160)
	portrait.texture = atlas
	emotion_label.text = ("ТОГДА · " if past_version else "СЕЙЧАС · ") + EXPRESSIONS[expression]


func set_past_version(value: bool) -> void:
	past_version = value
	set_expression(expression)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().quit()
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode >= KEY_1 and event.keycode <= KEY_5:
			set_expression(event.keycode - KEY_1)
		elif event.keycode == KEY_TAB:
			set_past_version(not past_version)


func _replay() -> void:
	# Genuine engine input and animation playback for repeatable visual evidence.
	for action in ["move_down", "move_right", "move_up", "move_left"]:
		Input.action_press(action)
		for frame in 48:
			await get_tree().physics_frame
		Input.action_release(action)
		for frame in 30:
			await get_tree().physics_frame
	for index in 5:
		set_expression(index)
		for frame in 36:
			await get_tree().physics_frame
	get_tree().quit()
