extends Control
## Real data-driven conversation viewer, isolated from campaign viewing and story facts.
signal closed
const Characters = preload("res://scripts/systems/character_catalog.gd")
var session: Node
var portrait: TextureRect
var body: RichTextLabel
var speaker: Label
var hint: Label
var selector: OptionButton
var history: Panel
var history_body: RichTextLabel
var ids: Array[String] = []
var vhs: Node2D
var selected_actor := "gabar"

func _ready() -> void:
 set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 _build()
 session = preload("res://scripts/systems/character_dialogue_session.gd").new()
 add_child(session)
 session.director.line_changed.connect(_line_changed)
 session.director.text_changed.connect(_text_changed)
 session.director.finished.connect(func(_id: StringName): hint.text = "Просмотр завершён. Можно выбрать другого персонажа или повторить.")
 for id in Characters.entries():
  if id == "yakuza": continue
  ids.append(id)
  selector.add_item(str(ids.size()) + ". " + Characters.actor(id).display_name)
 selector.item_selected.connect(func(index: int): open_actor(ids[index]))
 vhs = preload("res://scripts/ui/vhs_overlay.gd").new()
 vhs.z_index = 12
 add_child(vhs)
 get_node("/root/OptionsStore").changed.connect(_options_changed)
 _options_changed(&"", null)
 open_actor(selected_actor)
 if "--p06-cast-replay" in OS.get_cmdline_user_args():
  var replay := preload("res://scripts/qa/cast_replay.gd").new()
  get_tree().root.add_child.call_deferred(replay)
  replay.call_deferred("run", self)
 elif "--p06-cast-smoke" in OS.get_cmdline_user_args(): call_deferred("_smoke")

func _smoke() -> void:
 for i in 5: await get_tree().process_frame
 print("P06_CAST_SMOKE ready=", portrait.texture != null)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0 if portrait.texture != null else 1)

func _label(value: String, at: Vector2, bounds: Vector2, font_size := 16) -> Label:
 var node := Label.new();node.text = value;node.position = at;node.size = bounds
 node.add_theme_font_size_override("font_size", font_size)
 add_child(node)
 return node

func _button(text: String, at: Vector2, bounds: Vector2, callback: Callable) -> Button:
 var button := Button.new();button.text = text;button.position = at;button.size = bounds
 button.add_theme_font_size_override("font_size", 12);button.pressed.connect(callback);add_child(button)
 return button

func _build() -> void:
 var backdrop := ColorRect.new();backdrop.color = Color("101522");backdrop.size = Vector2(640,360);add_child(backdrop)
 _label("ПЕРСОНАЖИ · ПОЛИГОН", Vector2(20,12), Vector2(600,24), 20)
 selector = OptionButton.new();selector.position = Vector2(20,48);selector.size = Vector2(250,28);add_child(selector)
 _button("Повторить", Vector2(282,48), Vector2(130,28), _repeat)
 _button("Назад / Esc", Vector2(480,48), Vector2(140,28), _close)
 var disclaimer := _label("Вымышленная сцена. Просмотр не меняет историю и не открывает главы.", Vector2(20,88), Vector2(600,24), 12)
 disclaimer.add_theme_color_override("font_color", Color("a7bac5"))
 portrait = preload("res://scripts/ui/character_portrait.gd").new()
 portrait.position = Vector2(20,128);portrait.size = Vector2(160,160);add_child(portrait)
 speaker = _label("", Vector2(195,123), Vector2(425,24), 18)
 speaker.add_theme_color_override("font_color",Color("ffc773"))
 body = RichTextLabel.new();body.position = Vector2(195,156);body.size = Vector2(425,125)
 body.bbcode_enabled = false;body.scroll_active = false;body.add_theme_font_size_override("normal_font_size", 17);add_child(body)
 _button("Дальше / Space", Vector2(195,286), Vector2(138,28), _advance)
 _button("Журнал / H", Vector2(340,286), Vector2(110,28), _history)
 _button("Пропустить / K", Vector2(457,286), Vector2(163,28), _skip)
 hint = _label("", Vector2(20,326), Vector2(600,24), 11)
 history = Panel.new();history.position = Vector2(180,110);history.size = Vector2(440,208);history.z_index = 20;add_child(history)
 history_body = RichTextLabel.new();history_body.position = Vector2(12,12);history_body.size = Vector2(416,184)
 history_body.add_theme_font_size_override("normal_font_size",14);history.add_child(history_body);history.hide()

func _options_changed(_key: StringName, _value: Variant) -> void:
 if not vhs: return
 var options: Node = get_node("/root/OptionsStore")
 vhs.enabled = options.values.vhs
 vhs.reduced_motion = options.values.reduced_motion
 body.add_theme_font_size_override("normal_font_size", int(17 * float(options.values.text_scale)))

func open_actor(id: String) -> bool:
 selected_actor = id
 if id in ids: selector.select(ids.find(id))
 history.hide()
 if not session.open(id):
  portrait.texture = null;body.text = "Просмотр этого персонажа пока недоступен.";speaker.text = Characters.actor(id).get("display_name", "");hint.text = "Выберите другого персонажа."
  return false
 return true

func _line_changed(line: Dictionary) -> void:
 speaker.text = Characters.speaker(line.speaker).display_name
 portrait.show_line(line)

func _text_changed(text: String, count: int) -> void:
 body.text = text;body.visible_characters = count
 hint.text = "Space: раскрыть / дальше · Shift: быстрее" + (" · K: пропустить просмотренное" if session.director.can_skip() else "")

func _repeat() -> void:
 if not session or selected_actor not in ids or not Characters.presentation_ready(selected_actor): return
 if session.director.start_scene("res://resources/dialogue/p06_" + selected_actor + ".json"):
  session.director.set_process(true)

func _advance() -> void:
 if session and not history.visible: session.director.advance()

func _history() -> void:
 if not session: return
 history.visible = not history.visible
 history_body.text = "ЖУРНАЛ · H закрыть\n\n"
 for line in session.director.history: history_body.text += line.speaker_ru + ": " + line.text_ru + "\n\n"
 session.director.set_process(not history.visible)

func _skip() -> void:
 if session and not history.visible: session.director.skip_seen()

func _process(_delta: float) -> void:
 if session: session.director.hold_speed = Input.is_physical_key_pressed(KEY_SHIFT)

func _unhandled_input(event: InputEvent) -> void:
 if event is InputEventKey and event.pressed and not event.echo:
  # Consume while this Control still owns a viewport; Esc may remove the scene.
  get_viewport().set_input_as_handled()
  if event.keycode >= KEY_1 and event.keycode <= KEY_9:
   var index := int(event.keycode - KEY_1)
   if index < ids.size(): open_actor(ids[index])
   return
  match event.keycode:
   KEY_SPACE: _advance()
   KEY_H: _history()
   KEY_K: _skip()
   KEY_R: _repeat()
   KEY_ESCAPE: _close()

func _close() -> void:
 session.pause_view()
 if closed.get_connections().is_empty(): get_tree().change_scene_to_file("res://scenes/bootstrap/bootstrap.tscn")
 else: closed.emit()
