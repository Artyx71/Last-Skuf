extends Node2D
## P03 bounded presentation/audio laboratory; no mission or branch simulation.
const MOTION_PATH := "res://assets/art/yakuza/portrait_motion.png"
var world: Node2D
var director: Node
var audio: Node
var options: Node
var portrait: TextureRect
var portrait_texture: Texture2D
var portrait_metadata: Dictionary = {}
var caption: Label
var speaker: Label
var body: RichTextLabel
var hint: Label
var header: Label
var panel: Panel
var history_panel: Panel
var history_text: RichTextLabel
var settings_panel: Panel
var vhs: Node2D
var portrait_clock := 0.0
var portrait_column := 0
var portrait_row := 0
var motion_asset_ready := false
var pause_open := false
var exit_actions := 0
var replay_running := false

func _ready() -> void:
 director = get_node("/root/DialogueDirector")
 audio = get_node("/root/AudioDirector")
 options = get_node("/root/OptionsStore")
 _bindings()
 world = load("res://scenes/world/combat_lab.tscn").instantiate()
 add_child(world)
 # Preserve the actual technical world and actors behind a noncombat dialogue staging.
 world.set_physics_process(false)
 world.player.set_physics_process(false)
 world.player.position = Vector2(300, 172)
 world.player.sprite.play(&"idle_down")
 for enemy in world.enemies: enemy.set_physics_process(false)
 world.status_label.hide()
 world.kit_label.hide()
 world.hint_label.hide()
 for child in world.get_children():
  if child is Label and child.position.y == 8: child.hide()
 vhs = preload("res://scripts/ui/vhs_overlay.gd").new()
 vhs.z_index = 12
 add_child(vhs)
 _build_ui()
 director.line_changed.connect(_line_changed)
 director.text_changed.connect(_text_changed)
 director.finished.connect(_finished)
 director.exit_action.connect(_exit_action)
 options.changed.connect(_option_changed)
 _apply_options()
 audio.request_state(&"EXPLORE")
 if not director.restore() or not director.active: director.start_scene()
 if "--capture-dialogue" in OS.get_cmdline_user_args(): call_deferred("_capture_and_quit")
 if "--p03-replay" in OS.get_cmdline_user_args():
  replay_running = true
  call_deferred("_replay")

func _bindings() -> void:
 for id in {"dialogue_next": KEY_SPACE, "dialogue_fast": KEY_SHIFT, "dialogue_history": KEY_H,
  "dialogue_skip": KEY_K, "dialogue_options": KEY_O, "dialogue_replay": KEY_R}:
  if not InputMap.has_action(id):
   InputMap.add_action(id)
   var event := InputEventKey.new()
   event.physical_keycode = {"dialogue_next": KEY_SPACE, "dialogue_fast": KEY_SHIFT, "dialogue_history": KEY_H,
    "dialogue_skip": KEY_K, "dialogue_options": KEY_O, "dialogue_replay": KEY_R}[id]
   InputMap.action_add_event(id, event)

func _style(color: Color, border := Color("5c6a78")) -> StyleBoxFlat:
 var style := StyleBoxFlat.new()
 style.bg_color = color
 style.border_color = border
 style.set_border_width_all(1)
 return style

func _label(value: String, at: Vector2, size: Vector2, font_size := 14) -> Label:
 var label := Label.new()
 label.position = at
 label.size = size
 label.text = value
 label.add_theme_font_size_override("font_size", font_size)
 label.add_theme_color_override("font_color", Color("e9e8ed"))
 label.z_index = 30
 add_child(label)
 return label

func _build_ui() -> void:
 header = _label("P03 / ВХОДЯЩИЙ · ДИАЛОГ И ЗВУК", Vector2(20, 9), Vector2(600, 24), 16)
 header.add_theme_color_override("font_color", Color("83dfcb"))
 _label("Вымышленная сцена · технический полигон", Vector2(20, 34), Vector2(600, 20), 11)
 panel = Panel.new()
 panel.position = Vector2(14, 198)
 panel.size = Vector2(612, 148)
 panel.z_index = 20
 panel.add_theme_stylebox_override("panel", _style(Color("101522")))
 add_child(panel)
 portrait = TextureRect.new()
 portrait.position = Vector2(20, 182)
 portrait.size = Vector2(160, 160)
 portrait.z_index = 25
 portrait.mouse_filter = Control.MOUSE_FILTER_IGNORE
 portrait.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
 add_child(portrait)
 motion_asset_ready = ResourceLoader.exists(MOTION_PATH)
 if motion_asset_ready:
  portrait_texture = load(MOTION_PATH)
  portrait_metadata = JSON.parse_string(FileAccess.get_file_as_string("res://assets/art/yakuza/portrait_motion_atlas.json"))
 else:
  # Asset absence is visible in diagnostics and blocks motion acceptance.
  portrait_texture = load("res://assets/art/yakuza/portraits.png")
 speaker = _label("", Vector2(190, 207), Vector2(420, 24), 15)
 speaker.add_theme_color_override("font_color", Color("ffc773"))
 caption = _label("", Vector2(300, 210), Vector2(305, 20), 11)
 caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
 caption.add_theme_color_override("font_color", Color("83dfcb"))
 body = RichTextLabel.new()
 body.position = Vector2(190, 240)
 body.size = Vector2(420, 82)
 body.bbcode_enabled = false
 body.scroll_active = false
 body.add_theme_font_size_override("normal_font_size", 17)
 body.add_theme_color_override("default_color", Color("f1eff4"))
 body.z_index = 30
 add_child(body)
 hint = _label("", Vector2(190, 321), Vector2(420, 20), 10)
 _label("H: журнал · O: настройки · Shift: быстрее · Esc: меню", Vector2(18, 347), Vector2(600, 13), 10)
 history_panel = Panel.new()
 history_panel.position = Vector2(95, 55)
 history_panel.size = Vector2(530, 284)
 history_panel.z_index = 50
 history_panel.add_theme_stylebox_override("panel", _style(Color("111828")))
 add_child(history_panel)
 history_text = RichTextLabel.new()
 history_text.position = Vector2(16, 14)
 history_text.size = Vector2(496, 250)
 history_text.add_theme_font_size_override("normal_font_size", 14)
 history_panel.add_child(history_text)
 history_panel.hide()
 _build_options()

func _build_options() -> void:
 settings_panel = Panel.new()
 settings_panel.position = Vector2(202, 48)
 settings_panel.size = Vector2(424, 293)
 settings_panel.z_index = 60
 settings_panel.add_theme_stylebox_override("panel", _style(Color("111828")))
 add_child(settings_panel)
 var title := Label.new()
 title.text = "НАСТРОЙКИ · O закрыть"
 title.position = Vector2(14, 8)
 title.add_theme_font_size_override("font_size", 14)
 settings_panel.add_child(title)
 var y := 34
 for id in ["master", "music", "sfx", "voice_ui", "text_speed", "text_scale"]:
  var label := Label.new()
  label.position = Vector2(14, y)
  label.text = {"master": "Общая", "music": "Музыка", "sfx": "Эффекты", "voice_ui": "Голос / интерфейс", "text_speed": "Скорость текста", "text_scale": "Размер текста"}[id]
  label.add_theme_font_size_override("font_size", 12)
  settings_panel.add_child(label)
  var slider := HSlider.new()
  slider.name = id
  slider.position = Vector2(165, y + 3)
  slider.size = Vector2(235, 16)
  slider.min_value = 8 if id == "text_speed" else 1.0 if id == "text_scale" else 0
  slider.max_value = 90 if id == "text_speed" else 1.25 if id == "text_scale" else 1
  slider.step = 1 if id == "text_speed" else 0.05
  slider.value = options.values[id]
  slider.value_changed.connect(func(value: float): options.set_value(StringName(id), value))
  settings_panel.add_child(slider)
  y += 24
 var column := 0
 for id in ["instant_text", "vhs", "reduced_motion", "reduced_impact", "subtitles"]:
  var check := CheckButton.new()
  check.position = Vector2(12 + (column % 2) * 206, 183 + (column / 2) * 30)
  check.text = {"instant_text": "Текст сразу", "vhs": "VHS", "reduced_motion": "Меньше движения", "reduced_impact": "Мягче звук", "subtitles": "Подписи звуков"}[id]
  check.add_theme_font_size_override("font_size", 12)
  check.button_pressed = options.values[id]
  check.toggled.connect(func(value: bool): options.set_value(StringName(id), value))
  settings_panel.add_child(check)
  column += 1
 settings_panel.hide()

func _option_changed(_key: StringName, _value: Variant) -> void: _apply_options()
func _apply_options() -> void:
 vhs.enabled = options.values.vhs
 vhs.reduced_motion = options.values.reduced_motion
 body.add_theme_font_size_override("normal_font_size", int(17 * float(options.values.text_scale)))
 body.visible = true
 caption.visible = options.values.subtitles
 # Text-first dialogue stays readable with bleep-only speech; this toggle affects sound captions.

func _line_changed(line: Dictionary) -> void:
 speaker.text = line.get("speaker_ru", line.speaker)
 caption.text = line.get("caption_ru", "")
 portrait_row = 1 if line.emotion == "angry" else 0
 portrait_clock = 0.0
 _update_portrait()

func _text_changed(text: String, count: int) -> void:
 body.text = text
 body.visible_characters = count
 hint.text = "Space: раскрыть / дальше" + (" · K: пропустить" if director.can_skip() else " · первый просмотр")

func _exit_action(_action: Dictionary) -> void: exit_actions += 1
func _finished(_id: StringName) -> void:
 caption.text = "ВЫЗОВ ПРИНЯТ"
 hint.text = "Сцена завершена · R: повторить · K: пропустить просмотренное"
 audio.request_state(&"CLEAR")

func _process(delta: float) -> void:
 if not director: return
 director.hold_speed = Input.is_action_pressed("dialogue_fast")
 portrait_clock += delta
 _update_portrait()

func _update_portrait() -> void:
 if not portrait_texture: return
 portrait_column = 0
 if motion_asset_ready and not options.values.reduced_motion:
  var blink_interval := float(portrait_metadata.blink_interval_seconds)
  var blink_duration := float(portrait_metadata.blink_duration_seconds)
  var blinking := fmod(portrait_clock, blink_interval) >= blink_interval - blink_duration
  var talking: bool = director.active and director.visible_count < director.current_line().text_ru.length()
  portrait_column = 2 if blinking else (1 if talking and int(portrait_clock * float(portrait_metadata.fps.talk)) % 2 == 1 else 0)
 var atlas := AtlasTexture.new()
 atlas.atlas = portrait_texture
 atlas.region = Rect2(portrait_column * 160 if motion_asset_ready else portrait_row * 160, portrait_row * 160 if motion_asset_ready else 0, 160, 160)
 portrait.texture = atlas

func _input(event: InputEvent) -> void:
 if event.is_action_pressed("dialogue_options"):
  pause_open = not pause_open
  settings_panel.visible = pause_open
  director.set_process(not pause_open)
  audio.request_state(&"PAUSE" if pause_open else &"EXPLORE")
  get_viewport().set_input_as_handled()
 elif event.is_action_pressed("dialogue_history"):
  history_panel.visible = not history_panel.visible
  history_text.text = "ЖУРНАЛ · H закрыть\n\n"
  for line in director.history: history_text.text += line.speaker_ru + ": " + line.text_ru + "\n\n"
  get_viewport().set_input_as_handled()
 elif not pause_open and not history_panel.visible:
  if event.is_action_pressed("dialogue_next"):
   director.advance()
   audio.play_cue(&"ui_accept")
   get_viewport().set_input_as_handled()
  elif event.is_action_pressed("dialogue_skip"):
   director.skip_seen()
   get_viewport().set_input_as_handled()
  elif event.is_action_pressed("dialogue_replay") and not director.active:
   director.start_scene()
   get_viewport().set_input_as_handled()
 if event.is_action_pressed("ui_cancel"):
  director.autosave()
  audio.dialogue_active(false)
  get_tree().change_scene_to_file("res://scenes/bootstrap/bootstrap.tscn")
  get_viewport().set_input_as_handled()

func _frames(count: int) -> void:
 for i in count: await get_tree().physics_frame
func _tap(action: String) -> void:
 var event := InputEventAction.new()
 event.action = action
 event.pressed = true
 Input.parse_input_event(event)
 await _frames(1)
 event = InputEventAction.new()
 event.action = action
 event.pressed = false
 Input.parse_input_event(event)
 await _frames(1)
func _capture() -> Error:
 await RenderingServer.frame_post_draw
 var path := OS.get_environment("AYAY_CAPTURE_PATH")
 return get_viewport().get_texture().get_image().save_png(path) if not path.is_empty() else ERR_INVALID_PARAMETER
func _capture_and_quit() -> void:
 await _frames(70)
 if "--capture-large-text" in OS.get_cmdline_user_args():
  options.set_value(&"text_scale", 1.25, false)
  var longest := 0
  for i in director.data.lines.size():
   if director.data.lines[i].text_ru.length() > director.data.lines[longest].text_ru.length(): longest = i
  director.line_index = longest
  director._enter_line()
 director.reveal()
 if "--capture-options" in OS.get_cmdline_user_args():
  settings_panel.show()
  await _frames(3)
 var code := await _capture()
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), code)

func _replay() -> void:
 audio.begin_capture()
 director.start_scene()
 await _frames(75)
 await _tap("dialogue_next")
 await _tap("dialogue_next")
 await _frames(100)
 await _tap("dialogue_history")
 await _frames(30)
 await _tap("dialogue_history")
 # Exercise actual authored phone cue and expression changes.
 while director.active:
  await _frames(65)
  await _tap("dialogue_next")
 await _frames(60)
 audio.request_state(&"SUSPICION")
 await _frames(120)
 audio.request_state(&"COMBAT")
 await _frames(130)
 for cycle in 10:
  # Use real damage/retry lifecycle in the embedded existing combat lab.
  world.auto_retry = false
  world.state = "playing"
  world.player.receive_hit(1, 0, 1000 + cycle, world.enemies[0])
  await _frames(9)
  world.reset_encounter()
  world.set_physics_process(false)
  world.player.set_physics_process(false)
  for enemy in world.enemies: enemy.set_physics_process(false)
  await _frames(9)
 audio.request_state(&"CLEAR")
 await _frames(120)
 var audio_path := OS.get_environment("AYAY_P03_AUDIO_PATH")
 var audio_code: int = audio.end_capture(audio_path) if not audio_path.is_empty() else ERR_INVALID_PARAMETER
 var capture_code := OK
 if not OS.get_environment("AYAY_CAPTURE_PATH").is_empty(): capture_code = await _capture()
 var result := {"schema": 1, "actual_input": true, "finished": not director.active,
  "exit_actions": exit_actions, "motion_asset_ready": motion_asset_ready, "world_visible": world.visible,
  "actual_deaths": world.total_deaths, "audio": audio.diagnostics(), "audio_capture_code": audio_code,
  "capture_code": capture_code, "headless_dummy_is_not_listening": true}
 result["passed"] = not director.active and world.total_deaths == 10 and motion_asset_ready and audio.ready_assets and audio.stem_starts == 1 and audio_code == OK and capture_code == OK
 var path := OS.get_environment("AYAY_P03_RESULT_PATH")
 if not path.is_empty():
  var file := FileAccess.open(path, FileAccess.WRITE)
  file.store_string(JSON.stringify(result, "  "))
 print("P03_REPLAY ", JSON.stringify(result))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0 if result.passed else 1)

func _exit_tree() -> void:
 if is_instance_valid(director):
  director.set_process(true)
  director.autosave()
  director.active = false
 if is_instance_valid(audio): audio.dialogue_active(false)
