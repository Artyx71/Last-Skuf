extends Control
## Infrastructure screen; never presented as a playable mission.

const DISCLAIMER := "Вымышленная криминальная сатира. События PRIME и действия персонажей не являются утверждениями о реальных людях."


func _ready() -> void:
	if "--open-lab" in OS.get_cmdline_user_args():
		get_tree().call_deferred("change_scene_to_file", "res://scenes/world/movement_lab.tscn")
		return
	var panel := VBoxContainer.new()
	panel.position = Vector2(36, 32)
	panel.size = Vector2(568, 296)
	panel.add_theme_constant_override("separation", 18)
	add_child(panel)
	_add_label(panel, "АЫАЫ: ПОСЛЕДНИЙ СКУФ", 28, Color("ff477e"))
	_add_label(panel, "P01 / АРТ И ДВИЖЕНИЕ", 16, Color("66e5cc"))
	_add_label(panel, "Godot 4 · Windows / Linux\nПолная игра ещё не реализована.", 17, Color("e5e6ef"))
	_add_label(panel, DISCLAIMER, 15, Color("b9b9cc"))
	_add_label(panel, "Enter — лаборатория движения · Esc — выход", 14, Color("b9b9cc"))
	if "--capture-bootstrap" in OS.get_cmdline_user_args():
		await RenderingServer.frame_post_draw
		var output := OS.get_environment("AYAY_CAPTURE_PATH")
		if output.is_empty():
			push_error("AYAY_CAPTURE_PATH required")
			get_tree().quit(1)
			return
		var result := get_viewport().get_texture().get_image().save_png(output)
		print("BOOTSTRAP_CAPTURE error=", result)
		get_tree().quit(0 if result == OK else 1)


func _add_label(parent: Control, text: String, font_size: int, color: Color) -> void:
	var label := Label.new()
	label.text = text
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	parent.add_child(label)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_tree().quit()
	elif event.is_action_pressed("ui_accept"):
		get_tree().change_scene_to_file("res://scenes/world/movement_lab.tscn")
