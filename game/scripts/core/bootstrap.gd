extends Control
## Infrastructure screen; never presented as a playable mission.

var journal: Control

const DISCLAIMER := "Вымышленная криминальная сатира. События PRIME и действия персонажей не являются утверждениями о реальных людях."


func _ready() -> void:
	var bonus_return: bool = get_node("/root/StoryState").consume_bonus_return(self)
	if not bonus_return and "--open-character-combat" in OS.get_cmdline_user_args() and not get_tree().has_meta("p06_combat_startup_route"):
		get_tree().set_meta("p06_combat_startup_route", true)
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/character_lab.tscn")
		return
	if not bonus_return and "--open-cast" in OS.get_cmdline_user_args() and not get_tree().has_meta("p06_cast_startup_route"):
		get_tree().set_meta("p06_cast_startup_route", true)
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/cast_viewer.tscn")
		return
	if not bonus_return and "--open-mission" in OS.get_cmdline_user_args():
		get_tree().call_deferred("change_scene_to_file", "res://scenes/levels/missed_fight.tscn")
		return
	if not bonus_return and "--open-dialogue" in OS.get_cmdline_user_args():
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/dialogue_audio_lab.tscn")
		return
	if not bonus_return and "--open-combat" in OS.get_cmdline_user_args():
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/combat_lab.tscn")
		return
	if not bonus_return and "--open-lab" in OS.get_cmdline_user_args():
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/movement_lab.tscn")
		return
	var panel := VBoxContainer.new()
	panel.position = Vector2(36, 32)
	panel.size = Vector2(568, 296)
	panel.add_theme_constant_override("separation", 18)
	add_child(panel)
	_add_label(panel, "АЫАЫ: ПОСЛЕДНИЙ СКУФ", 28, Color("ff477e"))
	_add_label(panel, "ГЛАВА 01 / ПРОПУЩЕННАЯ ДРАКА", 16, Color("66e5cc"))
	_add_label(panel, "ПРОТОТИП В РАЗРАБОТКЕ · Windows / Linux\nПолная игра ещё не реализована.", 17, Color("e5e6ef"))
	_add_label(panel, DISCLAIMER, 15, Color("b9b9cc"))
	_add_label(panel, "Enter — глава 01 · J/F4 — главы · F1 — арт · F2 — учебный бой · F3 — диалог\nF5 — бой персонажей · F6 — портреты и реплики · Esc — выход", 14, Color("b9b9cc"))
	journal = preload("res://scripts/ui/story_journal.gd").new()
	journal.story = get_node("/root/StoryState")
	add_child(journal)
	journal.hide()
	if bonus_return:
		journal.open_bonuses()
	if "--p06-owner-preview-smoke" in OS.get_cmdline_user_args() and not get_tree().root.has_node("P06OwnerPreviewSmoke"):
		var probe := preload("res://scripts/qa/owner_preview_smoke.gd").new()
		probe.name = "P06OwnerPreviewSmoke"
		get_tree().root.add_child.call_deferred(probe)
		probe.call_deferred("run")
	if "--p05-replay" in OS.get_cmdline_user_args() and not get_tree().root.has_node("P05ReplayDriver"):
		var driver := preload("res://scripts/qa/story_replay.gd").new()
		driver.name = "P05ReplayDriver"
		get_tree().root.add_child.call_deferred(driver)
		driver.call_deferred("run", self)
	if "--smoke-bootstrap" in OS.get_cmdline_user_args():
		print("BOOTSTRAP_SMOKE ready=true")
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0)
		return
	if "--capture-bootstrap" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		var output := OS.get_environment("AYAY_CAPTURE_PATH")
		if output.is_empty():
			push_error("AYAY_CAPTURE_PATH required")
			preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 1)
			return
		var result := get_viewport().get_texture().get_image().save_png(output)
		print("BOOTSTRAP_CAPTURE error=", result)
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0 if result == OK else 1)


func _add_label(parent: Control, text: String, font_size: int, color: Color) -> void:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.keycode in [KEY_J, KEY_F4]:
		journal.refresh(); journal.show()
	elif event.is_action_pressed("ui_cancel"):
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0)
	elif event.is_action_pressed("ui_accept"):
		get_tree().change_scene_to_file("res://scenes/levels/missed_fight.tscn")
	elif event is InputEventKey and event.pressed and event.keycode == KEY_F2:
		get_tree().change_scene_to_file("res://scenes/world/combat_lab.tscn")
	elif event is InputEventKey and event.pressed and event.keycode == KEY_F1:
		get_tree().change_scene_to_file("res://scenes/world/movement_lab.tscn")
	elif event is InputEventKey and event.pressed and event.keycode == KEY_F3:
		get_tree().change_scene_to_file("res://scenes/world/dialogue_audio_lab.tscn")
	elif event is InputEventKey and event.pressed and event.keycode == KEY_F5:
		get_tree().change_scene_to_file("res://scenes/world/character_lab.tscn")
	elif event is InputEventKey and event.pressed and event.keycode == KEY_F6:
		get_tree().change_scene_to_file("res://scenes/world/cast_viewer.tscn")
