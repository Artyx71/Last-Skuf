extends CanvasLayer
## World stays behind the existing DialogueDirector. All controls remain text-first.
var mission: Node2D
var director: Node
var options: Node
var header: Label
var objective: Label
var status: Label
var hint: Label
var dialogue_panel: Panel
var portrait: TextureRect
var body: RichTextLabel
var speaker: Label
var caption: Label
var next_hint: Label
var history_panel: Panel
var history_text: RichTextLabel
var settings_panel: Panel
var result_panel: Panel
var result_text: Label
var time := 0.0
var row := 0
var vhs: Node2D
var option_controls: Dictionary = {}

func _ready() -> void:
 layer = 20
 director = get_node("/root/DialogueDirector")
 options = get_node("/root/OptionsStore")
 header = label("", Vector2(14, 7), Vector2(612, 20), 14)
 objective = label("", Vector2(14, 29), Vector2(612, 20), 12)
 status = label("", Vector2(14, 315), Vector2(612, 20), 12)
 hint = label("WASD · F: действие · E: отвлечь · Space: толчок · O: пауза · R: заново", Vector2(14, 340), Vector2(612, 15), 10)
 var top := panel(Vector2.ZERO, Vector2(640, 54)); top.z_index = -1
 var bottom := panel(Vector2(0, 311), Vector2(640, 49)); bottom.z_index = -1
 dialogue_panel = panel(Vector2(12, 186), Vector2(616, 162))
 portrait = TextureRect.new()
 portrait.position = Vector2(2, 1)
 portrait.size = Vector2(160, 160)
 portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
 dialogue_panel.add_child(portrait)
 speaker = label("Якудза", Vector2(180, 195), Vector2(420, 20), 14, dialogue_panel, true)
 caption = label("", Vector2(180, 220), Vector2(420, 20), 11, dialogue_panel, true)
 caption.add_theme_color_override("font_color", Color("80cbb4"))
 body = RichTextLabel.new()
 body.position = Vector2(168, 60)
 body.size = Vector2(426, 70)
 body.scroll_active = false
 dialogue_panel.add_child(body)
 next_hint = label("", Vector2(180, 322), Vector2(420, 20), 10, dialogue_panel, true)
 history_panel = panel(Vector2(80, 60), Vector2(540, 245))
 history_text = RichTextLabel.new()
 history_text.position = Vector2(14, 12); history_text.size = Vector2(512, 220)
 history_text.add_theme_font_size_override("normal_font_size", 14)
 history_panel.add_child(history_text)
 history_panel.hide()
 _settings()
 result_panel = panel(Vector2(80, 76), Vector2(480, 213))
 result_text = label("", Vector2(100, 91), Vector2(438, 175), 17, result_panel, true)
 result_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
 result_panel.hide()
 vhs = preload("res://scripts/ui/vhs_overlay.gd").new()
 vhs.z_index = -2
 add_child(vhs)
 director.line_changed.connect(_line)
 director.text_changed.connect(_text)
 options.changed.connect(func(_key: StringName, _value: Variant): apply_options())
 apply_options()

func label(value: String, at: Vector2, bounds: Vector2, font_size: int, parent: Node = null, relative := false) -> Label:
 if parent == null: parent = self
 var node := Label.new()
 node.position = at - parent.position if relative else at
 node.size = bounds
 node.text = value
 node.add_theme_font_size_override("font_size", font_size)
 node.add_theme_color_override("font_color", Color("f4ebd5"))
 parent.add_child(node)
 return node

func panel(at: Vector2, bounds: Vector2) -> Panel:
 var node := Panel.new()
 node.position = at; node.size = bounds
 var style := StyleBoxFlat.new()
 style.bg_color = Color("10141ff5"); style.border_color = Color("4f5b68")
 style.set_border_width_all(1)
 node.add_theme_stylebox_override("panel", style)
 add_child(node)
 return node

func _settings() -> void:
 settings_panel = panel(Vector2(88, 56), Vector2(464, 251))
 label("ПАУЗА · O / Esc: вернуться · Q: меню", Vector2(102, 66), Vector2(430, 22), 15, settings_panel, true)
 var y := 35
 for key in ["master", "music", "sfx", "voice_ui", "text_scale"]:
  var title: String = {"master":"Общая", "music":"Музыка", "sfx":"Эффекты", "voice_ui":"Реплики / UI", "text_scale":"Размер текста"}[key]
  label(title, Vector2(102, 56+y), Vector2(145, 22), 12, settings_panel, true)
  var slider := HSlider.new()
  slider.position = Vector2(168, y+3); slider.size = Vector2(275, 15)
  slider.min_value = 1.0 if key == "text_scale" else 0.0
  slider.max_value = 1.25 if key == "text_scale" else 1.0
  slider.step = .05; slider.value = options.values[key]
  slider.value_changed.connect(func(value: float): options.set_value(StringName(key), value))
  settings_panel.add_child(slider); option_controls[key] = slider
  y += 23
 var i := 0
 for key in ["vhs", "reduced_motion", "reduced_gore", "reduced_impact", "instant_text", "subtitles"]:
  var control := CheckButton.new()
  control.position = Vector2(10+(i%2)*224, 157+(i/2)*27)
  control.text = {"vhs":"VHS", "reduced_motion":"Меньше движения", "reduced_gore":"Меньше насилия", "reduced_impact":"Мягче звук", "instant_text":"Текст сразу", "subtitles":"Подписи звуков"}[key]
  control.add_theme_font_size_override("font_size", 12)
  control.button_pressed = options.values[key]
  control.toggled.connect(func(value: bool): options.set_value(StringName(key), value))
  settings_panel.add_child(control); option_controls[key] = control
  i += 1
 settings_panel.hide()

func apply_options() -> void:
 body.add_theme_font_size_override("normal_font_size", int(16 * options.values.text_scale))
 vhs.enabled = options.values.vhs
 vhs.reduced_motion = options.values.reduced_motion
 caption.visible = options.values.subtitles

func _line(line: Dictionary) -> void:
 row = 1 if line.emotion == "angry" else 0
 time = 0
 caption.text = line.get("caption_ru", "")

func _text(value: String, count: int) -> void:
 body.text = value
 body.visible_characters = count

func toggle_history() -> void:
 history_panel.visible = not history_panel.visible
 history_text.text = "ЖУРНАЛ · H: закрыть\n\n"
 for line in director.history: history_text.text += line.speaker_ru + ": " + line.text_ru + "\n\n"

func _process(delta: float) -> void:
 time += delta
 header.text = "01 / " + String(mission.config.title_ru) + " · ЯКУДЗА"
 objective.text = mission.objective_text()
 status.text = mission.status_text()
 dialogue_panel.visible = director.active and mission.state == "dialogue"
 next_hint.text = "Space: раскрыть / дальше · Shift: быстрее · H: журнал" + (" · K: пропустить" if director.can_skip() else "")
 if dialogue_panel.visible:
  var column := 0
  if not options.values.reduced_motion:
   var speaking: bool = director.visible_count < director.current_line().text_ru.length()
   column = 2 if fmod(time, 3.2) > 3.05 else (1 if speaking and int(time * 7) % 2 else 0)
  var texture := AtlasTexture.new()
  texture.atlas = preload("res://assets/art/yakuza/portrait_motion.png")
  texture.region = Rect2(column*160, row*160, 160, 160)
  portrait.texture = texture
 result_panel.visible = mission.state == "complete"
 if result_panel.visible:
  result_text.text = "ДРАКА ЗАКОНЧИЛАСЬ БЕЗ ТЕБЯ\n\nГлава 01 пройдена · %d очков\nЛучший уход: %d · смертей: %d\n\nR: повторить · Esc: меню" % [mission.score, mission.progress.data.best_score, mission.progress.data.deaths]
 hint.visible = not dialogue_panel.visible and not settings_panel.visible
