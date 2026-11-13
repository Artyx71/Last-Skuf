extends PanelContainer
## Player-facing recap and honest chapter availability. No future scenes are launchable.
var story: Node
var list: ItemList
var recap: Label
var launch: Button
var close: Button
var selected := 0

func _ready() -> void:
 set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 add_theme_stylebox_override("panel",_background())
 var margin := MarginContainer.new()
 for side in ["left","right","top","bottom"]: margin.add_theme_constant_override("margin_"+side,16)
 add_child(margin)
 var column := VBoxContainer.new(); margin.add_child(column)
 var title := Label.new(); title.text = "ИСТОРИЯ · ГЛАВЫ"; title.add_theme_font_size_override("font_size",22); column.add_child(title)
 var row := HBoxContainer.new(); row.size_flags_vertical = Control.SIZE_EXPAND_FILL; column.add_child(row)
 list = ItemList.new(); list.custom_minimum_size = Vector2(270,220); list.size_flags_vertical = Control.SIZE_EXPAND_FILL; list.add_theme_font_size_override("font_size",14); row.add_child(list)
 var right := VBoxContainer.new(); right.size_flags_horizontal = Control.SIZE_EXPAND_FILL; row.add_child(right)
 var scroll := ScrollContainer.new(); scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL; scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED; right.add_child(scroll)
 recap = Label.new(); recap.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; recap.size_flags_horizontal = Control.SIZE_EXPAND_FILL; recap.add_theme_font_size_override("font_size",15); scroll.add_child(recap)
 launch = Button.new(); launch.text = "Продолжить · Enter"; launch.pressed.connect(_launch); right.add_child(launch)
 close = Button.new(); close.text = "Назад · Esc / J"; close.pressed.connect(hide); right.add_child(close)
 list.item_selected.connect(_select)
 story.changed.connect(refresh)
 refresh()

func _background() -> StyleBoxFlat:
 var style := StyleBoxFlat.new(); style.bg_color = Color("10131f"); return style

func refresh() -> void:
 list.clear()
 for chapter in story.store.registry.data.chapters:
  var status := "скоро"
  if chapter.availability == "playable": status = "пройдена" if story.store.state.chapter_complete.has(chapter.id) else "доступна"
  list.add_item("%02d · %s · %s" % [chapter.presentation,chapter.title_ru,status])
 list.select(selected); _select(selected)

func _select(index: int) -> void:
 selected = index
 var chapter: Dictionary = story.store.registry.data.chapters[index]
 var completed: bool = story.store.state.chapter_complete.has(chapter.id)
 launch.disabled = not story.store.registry.entry_ready(chapter.id,story.store.state)
 launch.text = "Повторить · Enter" if completed else "Продолжить · Enter"
 if chapter.availability != "playable":
  recap.text = "%s\n\nЭта глава ещё в работе. Вернитесь к первой главе — она уже доступна.\n\nНовые главы появятся после их выпуска." % chapter.title_ru
 else:
  recap.text = "14 октября 2023 · Раньше\nЯкудза · служебный выход\n\nКуртка у раковины. Драка за дверью. Жинька звонит. Якудза выбирается домой без геройства.\n\n" + ("Вы уже ушли через двор. Повтор не изменит историю и не даст повторную награду." if completed else "Найдите куртку, откройте служебку и выйдите во двор. Пройденная глава останется в журнале.")
 if not story.error_message.is_empty(): recap.text += "\n\n"+story.error_message

func _launch() -> void:
 var chapter: Dictionary = story.store.registry.data.chapters[selected]
 if not story.store.registry.entry_ready(chapter.id,story.store.state): return
 story.pending_replay = story.store.state.chapter_complete.has(chapter.id)
 get_tree().change_scene_to_file(chapter.scene)

func _input(event: InputEvent) -> void:
 if not visible: return
 if event is InputEventKey and event.pressed and not event.echo:
  if event.keycode in [KEY_ESCAPE,KEY_J,KEY_F4]: hide(); get_viewport().set_input_as_handled()
  elif event.keycode == KEY_ENTER:
   get_viewport().set_input_as_handled(); _launch()
