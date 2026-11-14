extends Node
## Versioned accessibility/audio settings; tests use an explicitly isolated path.
signal changed(key: StringName, value: Variant)
const DEFAULTS := {"master": 0.8, "music": 0.7, "sfx": 0.8, "voice_ui": 0.8,
 "text_speed": 36.0, "instant_text": false, "vhs": true, "reduced_motion": false,
 "reduced_impact": false, "subtitles": true, "text_scale": 1.0, "reduced_gore": false, "decals": true, "shake": 100.0, "flashes": true}
var values: Dictionary = DEFAULTS.duplicate()
var storage_path := "user://options_v1.json"
var last_error := OK

func _ready() -> void:
 var override := OS.get_environment("AYAY_OPTIONS_PATH")
 if not override.is_empty(): storage_path = override
 load_options()
 apply_buses()

func set_value(key: StringName, value: Variant, persist := true) -> bool:
 if not DEFAULTS.has(String(key)): return false
 var original: Variant = DEFAULTS[String(key)]
 if original is bool:
  if not value is bool: return false
 elif original is float:
  if not (value is float or value is int) or not is_finite(float(value)): return false
  var limits := Vector2(0, 1)
  if key == &"shake": limits = Vector2(0, 100)
  if key == &"text_speed": limits = Vector2(8, 90)
  if key == &"text_scale": limits = Vector2(1, 1.25)
  value = clampf(float(value), limits.x, limits.y)
 values[String(key)] = value
 apply_buses()
 changed.emit(key, value)
 if persist: save_options()
 return true

func apply_buses() -> void:
 var routing := {"Master": "master", "Music": "music", "SFX": "sfx", "SFX_UI": "voice_ui", "Speech_Cues": "voice_ui"}
 for bus in routing:
  var index := AudioServer.get_bus_index(bus)
  if index >= 0:
   var gain := float(values[routing[bus]])
   AudioServer.set_bus_volume_db(index, linear_to_db(maxf(gain, 0.00001)))
   AudioServer.set_bus_mute(index, gain == 0)

func save_options() -> Error:
 var temporary := storage_path + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  last_error = FileAccess.get_open_error()
  return last_error
 file.store_string(JSON.stringify({"schema": 2, "values": values}, "  "))
 file.close()
 last_error = DirAccess.rename_absolute(temporary, storage_path)
 return last_error

func load_options() -> bool:
 if not FileAccess.file_exists(storage_path): return false
 var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(storage_path))
 if not data is Dictionary or (data.get("schema") != 1 and data.get("schema") != 2) or not data.get("values") is Dictionary: return false
 for key in data.values:
  set_value(StringName(key), data.values[key], false)
 return true
