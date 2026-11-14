extends SceneTree
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("_run")
func check(condition: bool, title: String) -> void:
 if condition:
  passed += 1
  print("PASS ", title)
 else:
  failed += 1
  push_error("FAIL " + title)
func frames(n: int) -> void:
 for i in n: await process_frame
func finish() -> void:
 print("RESULT passed=%d failed=%d" % [passed, failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)

var exits := 0
var done := 0
func _run() -> void:
 await frames(2)
 root.get_node("OptionsStore").values = root.get_node("OptionsStore").DEFAULTS.duplicate()
 root.get_node("OptionsStore").storage_path = "user://p03_test_ui_options.json"
 root.get_node("DialogueDirector").save_path = "user://p03_test_dialogue_input.json"
 var director := preload("res://scripts/systems/dialogue_director.gd").new()
 root.add_child(director)
 director.save_path = "user://p03_test_dialogue.json"
 director.set_process(false)
 director.exit_action.connect(func(_a: Dictionary): exits += 1)
 director.finished.connect(func(_id: StringName): done += 1)
 check(director.start_scene(), "structured external scene loads")
 check(director.data.event_id == "EV_P03_UNPAID_DELIVERY", "stable event ID")
 check(director.data.lines.size() == 5, "bounded authored five-line scene")
 check(director.visible_count == 0 and director.line_index == 0, "typewriter starts hidden")
 check(not director.skip_seen() and director.active, "unseen scene cannot skip")
 director._process(0.03)
 check(director.visible_count == 1, "one character revealed by clock")
 director.advance()
 check(director.line_index == 0 and director.visible_count == director.current_line().text_ru.length(), "first action reveals entire current line")
 director.advance()
 check(director.line_index == 1 and director.history.size() == 1, "second action advances and records history")
 check(director.current_line().emotion == "angry", "actual expression changes")
 director._process(0.03)
 check(director.autosave(), "partial line autosaves")
 var restored := preload("res://scripts/systems/dialogue_director.gd").new()
 root.add_child(restored)
 restored.set_process(false)
 restored.save_path = director.save_path
 check(restored.restore(), "active dialogue restores")
 check(restored.line_index == 1 and restored.visible_count == director.visible_count and restored.history.size() == 1, "restore exact line/progress/history")
 check(exits == 0, "restore does not fire exit actions")
 director.visible_count = director.current_line().text_ru.find("?")
 director.char_timer = 0
 director._process(0.001)
 check(director.char_timer > 0.15, "punctuation has authored typing pause")
 director.char_timer = 1.0
 director.hold_speed = true
 director._process(0.1)
 check(director.char_timer < 0.51, "held speed consumes fivefold timer")
 director.hold_speed = false
 director.line_index = 0
 director._enter_line()
 director.hold_speed = true
 director._process(0.03)
 check(director.visible_count >= 5, "held text reveals multiple elapsed characters on one render frame")
 director.hold_speed = false
 director.line_index = 3
 director._enter_line()
 director.reveal()
 check(not director.advance() and director.line_index == 3, "authored phone hold prevents immediate advance")
 director.line_elapsed = 0.81
 check(director.advance() and director.line_index == 4, "phone hold releases after authored duration")
 var durable_path: String = director.save_path
 director.save_path = "user://missing_p03_directory/dialogue.json"
 director.reveal()
 director.line_elapsed = 2.0
 director.advance()
 check(director.active and exits == 0 and director.flags.is_empty() and director.ledger.is_empty(), "failed save rolls back scene consequence and stays active")
 director.save_path = durable_path
 while director.active:
  director.line_elapsed = 2.0
  director.reveal()
  director.advance()
 check(exits == 1 and done == 1, "scene executes one exit action once")
 check(director.flags.p03_delivery_interrupted and director.ledger.has(director.data.event_id), "persist real narrative consequence")
 director.advance()
 director._finish()
 check(exits == 1 and done == 1, "duplicate finish/advance cannot repeat exit")
 director.start_scene()
 check(director.can_skip() and director.skip_seen(), "seen scene safely skips")
 check(exits == 1 and done == 2, "seen replay preserves once-only ledger")
 var completed := preload("res://scripts/systems/dialogue_director.gd").new()
 root.add_child(completed)
 completed.save_path = director.save_path
 completed.set_process(false)
 check(completed.restore() and not completed.active and completed.seen.has(director.data.scene_id), "completed scene restore retains seen status")
 completed.start_scene()
 completed.exit_action.connect(func(_a: Dictionary): exits += 1)
 completed.skip_seen()
 check(exits == 1, "disk roundtrip cannot repeat consequence")
 var opts := root.get_node("OptionsStore")
 opts.set_value(&"instant_text", true, false)
 director.start_scene()
 check(director.visible_count == director.current_line().text_ru.length(), "instant text option applied at entry")
 opts.set_value(&"instant_text", false, false)
 director.active = false
 # Native input/UI, actual sheet and background world integration.
 var lab: Node2D = load("res://scenes/world/dialogue_audio_lab.tscn").instantiate()
 root.add_child(lab)
 await frames(3)
 var live: Node = root.get_node("DialogueDirector")
 live.save_path = "user://p03_test_dialogue_input.json"
 live.seen.clear()
 live.ledger.clear()
 live.start_scene()
 live.set_process(false)
 await lab._tap("dialogue_next")
 check(live.line_index == 0 and live.visible_count == live.current_line().text_ru.length(), "native Space action reveals")
 await lab._tap("dialogue_next")
 check(live.line_index == 1, "native Space action advances")
 await lab._tap("dialogue_history")
 check(lab.history_panel.visible and lab.history_text.text.contains("Я принёс"), "native H opens actual history")
 await lab._tap("dialogue_history")
 await lab._tap("dialogue_options")
 check(lab.settings_panel.visible and not live.is_processing(), "native options pause typing")
 await lab._tap("dialogue_options")
 check(not lab.settings_panel.visible and live.is_processing(), "closing options resumes typing")
 check(lab.motion_asset_ready and lab.portrait_texture.get_width() == 480, "real six-frame portrait sheet integrated")
 opts.set_value(&"reduced_motion", true, false)
 lab._update_portrait()
 check(lab.portrait_column == 0 and lab.vhs.reduced_motion, "reduced motion uses still portrait and still scanlines")
 opts.set_value(&"vhs", false, false)
 check(not lab.vhs.enabled and lab.body.visible, "VHS off preserves captions")
 live.line_index = 3
 live._enter_line()
 live.reveal()
 opts.set_value(&"subtitles", false, false)
 check(not lab.caption.visible and lab.body.visible and lab.body.text == live.current_line().text_ru, "sound-caption toggle preserves essential bleep-only dialogue text")
 opts.set_value(&"subtitles", true, false)
 check(lab.caption.visible and lab.caption.text.contains("ЖИНЬКА"), "sound-caption toggle restores phone cue caption")
 opts.set_value(&"text_scale", 1.25, false)
 for index in live.data.lines.size():
  live.line_index = index
  live._enter_line()
  live.reveal()
  await frames(2)
  check(lab.body.get_content_height() <= lab.body.size.y, "maximum text size fits authored line " + str(index))

 var slider: HSlider = lab.settings_panel.get_node("music")
 slider.value = 0.4
 check(absf(opts.values.music - 0.4) < 0.001, "actual slider updates persisted volume")
 check(lab.world.visible and lab.world.player.visible, "technical world remains visible")
 live.active = false
 lab.queue_free()
 director.queue_free()
 restored.queue_free()
 completed.queue_free()
 await frames(3)
 DirAccess.remove_absolute("user://p03_test_dialogue.json")
 DirAccess.remove_absolute("user://p03_test_dialogue_input.json")
 DirAccess.remove_absolute("user://p03_test_ui_options.json")
 await finish()
