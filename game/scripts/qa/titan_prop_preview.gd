extends Node2D
## Art review surface only; this is not an accessible story chapter.
const BENCH = preload("res://assets/art/the_titan/bench_press.png")

func _ready() -> void:
 texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
 for item in [[Vector2(158, 198), 1.0], [Vector2(448, 198), 2.0]]:
  var sprite := Sprite2D.new()
  sprite.texture = BENCH
  sprite.position = item[0]
  sprite.scale = Vector2.ONE * float(item[1])
  add_child(sprite)
 _label("CH02 · ПРОВЕРКА АССЕТА, НЕ ГОТОВАЯ ГЛАВА", Vector2(20, 16), 16)
 _label("128 × 128 · 1×", Vector2(96, 280), 14)
 _label("128 × 128 · 2×", Vector2(386, 334), 14)
 var capture := OS.get_environment("AYAY_TITAN_PROP_CAPTURE")
 if not capture.is_empty():
  await RenderingServer.frame_post_draw
  await RenderingServer.frame_post_draw
  var error := get_viewport().get_texture().get_image().save_png(capture)
  print(JSON.stringify({"capture_error":error,"texture_size":[BENCH.get_width(),BENCH.get_height()],"nearest":texture_filter == CanvasItem.TEXTURE_FILTER_NEAREST,"chapter_playthrough":false}))
  get_tree().quit(0 if error == OK else 1)

func _label(value: String, at: Vector2, size: int) -> void:
 var label := Label.new()
 label.text = value
 label.position = at
 label.add_theme_font_size_override("font_size", size)
 add_child(label)

func _draw() -> void:
 draw_rect(Rect2(0, 0, 640, 360), Color("346766"))
 for x in range(0, 640, 32):
  draw_line(Vector2(x, 0), Vector2(x, 360), Color("25474b"))
 for y in range(0, 360, 32):
  draw_line(Vector2(0, y), Vector2(640, y), Color("25474b"))

func _unhandled_input(event: InputEvent) -> void:
 if event.is_action_pressed("ui_cancel"): get_tree().quit()
