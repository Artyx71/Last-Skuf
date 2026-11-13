extends RefCounted
## Initial keyboard bindings. Full persistent remapping belongs to a later gate.


static func install() -> void:
	var bindings := {
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"move_up": [KEY_W, KEY_UP],
		"move_down": [KEY_S, KEY_DOWN],
		"attack_melee": [KEY_SPACE],
		"distract": [KEY_E],
		"restart": [KEY_R],
		"switch_kit": [KEY_F2],
		"finisher": [KEY_F],
		"cancel_finisher": [KEY_C],
		"equipment_next": [KEY_TAB],
		"polish_options": [KEY_O],
	}
	for action: String in bindings:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action, 0.2)
		for key: int in bindings[action]:
			var event := InputEventKey.new()
			event.physical_keycode = key
			InputMap.action_add_event(action, event)
	for action: String in {"attack_melee": MOUSE_BUTTON_LEFT, "attack_ranged": MOUSE_BUTTON_RIGHT}:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		var mouse_event := InputEventMouseButton.new()
		mouse_event.button_index = MOUSE_BUTTON_LEFT if action == "attack_melee" else MOUSE_BUTTON_RIGHT
		if not InputMap.action_has_event(action, mouse_event):
			InputMap.action_add_event(action, mouse_event)
