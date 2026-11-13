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

func _run() -> void:
 await frames(2)
 var store := preload("res://scripts/core/options_store.gd").new()
 store.storage_path = "user://p03_test_options.json"
 root.add_child(store)
 # _ready's environment override must never select the player's normal preferences.
 store.storage_path = "user://p03_test_options.json"
 var expected := {"master": 0.35, "music": 0.55, "sfx": 0.45, "voice_ui": 0.65,
  "text_speed": 58.0, "instant_text": true, "vhs": false, "reduced_motion": true,
  "reduced_impact": true, "subtitles": true, "text_scale": 1.2}
 for key in expected:
  check(store.set_value(StringName(key), expected[key], false), "accept option " + key)
 check(store.save_options() == OK, "versioned preferences persist")
 var second := preload("res://scripts/core/options_store.gd").new()
 root.add_child(second)
 second.storage_path = store.storage_path
 check(second.load_options(), "read saved preferences")
 check(second.values == expected, "all eleven options round trip")
 for bus in {"Master": "master", "Music": "music", "SFX": "sfx", "SFX_UI": "voice_ui", "Speech_Cues": "voice_ui"}:
  var key: String = {"Master": "master", "Music": "music", "SFX": "sfx", "SFX_UI": "voice_ui", "Speech_Cues": "voice_ui"}[bus]
  check(absf(db_to_linear(AudioServer.get_bus_volume_db(AudioServer.get_bus_index(bus))) - expected[key]) < 0.0001, "actual bus gain " + bus)
 check(AudioServer.get_bus_send(AudioServer.get_bus_index("Music_Ambience")) == &"Music", "ambient bus follows Music volume")
 check(second.set_value(&"sfx", 0.0, false) and AudioServer.is_bus_mute(AudioServer.get_bus_index("SFX")), "zero volume actually mutes")
 check(not second.set_value(&"vhs", "yes", false), "reject wrong boolean type")
 check(not second.set_value(&"music", NAN, false), "reject nonfinite gain")
 check(not second.set_value(&"unknown", 1.0, false), "reject unknown preference")
 second.set_value(&"music", 10.0, false)
 check(second.values.music == 1.0, "clamp volume range")
 var file := FileAccess.open(store.storage_path, FileAccess.WRITE)
 file.store_string('{"schema":999,"values":{"music":0}}')
 file.close()
 check(not second.load_options(), "reject unsupported settings version")
 DirAccess.remove_absolute(store.storage_path)
 store.queue_free()
 second.queue_free()
 await frames(2)
 await finish()
