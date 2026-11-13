extends Node
## External narrative data and a durable once-only event ledger; no string evaluation.
signal line_changed(line: Dictionary)
signal text_changed(text: String, visible_count: int)
signal finished(scene_id: StringName)
signal exit_action(action: Dictionary)
const DEFAULT_SCENE := "res://resources/dialogue/yakuza_phone.json"
var save_path := "user://dialogue_v1.json"
var data: Dictionary = {}
var resource_path := ""
var line_index := 0
var visible_count := 0
var active := false
var char_timer := 0.0
var line_elapsed := 0.0
var history: Array[Dictionary] = []
var seen: Dictionary = {}
var ledger: Dictionary = {}
var flags: Dictionary = {}
var options: Node
var audio: Node
var hold_speed := false
var last_error := OK

func _ready() -> void:
 options = get_node_or_null("/root/OptionsStore")
 audio = get_node_or_null("/root/AudioDirector")
 var override := OS.get_environment("AYAY_DIALOGUE_SAVE_PATH")
 if not override.is_empty(): save_path = override

func load_scene(path := DEFAULT_SCENE) -> bool:
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
 if not parsed is Dictionary or parsed.get("schema") != 1 or not parsed.get("lines") is Array or parsed.lines.is_empty(): return false
 var ids := {}
 for line in parsed.lines:
  for key in ["line_id", "loc_key", "speaker", "emotion", "text_ru"]:
   if not line.get(key) is String or String(line[key]).is_empty(): return false
  if ids.has(line.line_id): return false
  ids[line.line_id] = true
  if line.speaker != "YAKUZA" or not line.emotion in ["neutral", "angry"]: return false
 for condition in parsed.get("entry_conditions", []):
  if not flags.get(condition, false): return false
 for action in parsed.get("exit_actions", []):
  if action.get("type") != "set_flag" or not action.get("name") is String: return false
 data = parsed
 resource_path = path
 return true

func start_scene(path := DEFAULT_SCENE) -> bool:
 if not load_scene(path): return false
 line_index = 0
 history.clear()
 active = true
 if audio: audio.dialogue_active(true)
 _enter_line()
 return true

func current_line() -> Dictionary:
 return data.lines[line_index] if not data.is_empty() else {}

func _enter_line(play_cue := true) -> void:
 visible_count = current_line().text_ru.length() if options and options.values.instant_text else 0
 char_timer = 1.0 / (float(options.values.text_speed) if options else 36.0)
 line_elapsed = 0.0
 line_changed.emit(current_line())
 text_changed.emit(current_line().text_ru, visible_count)
 if audio and play_cue and current_line().has("cue"):
  audio.play_cue(StringName(current_line().cue))
 autosave()

func _process(delta: float) -> void:
 if not active: return
 line_elapsed += delta
 var text: String = current_line().text_ru
 if visible_count >= text.length(): return
 if options and options.values.instant_text:
  reveal()
  return
 char_timer -= delta * (5.0 if hold_speed else 1.0)
 var speed := float(options.values.text_speed) if options else 36.0
 var updated := false
 # Reveal every elapsed character interval, including 90cps/held text on a 60Hz display.
 while char_timer <= 0 and visible_count < text.length():
  visible_count += 1
  updated = true
  var letter := text.substr(visible_count - 1, 1)
  char_timer += 1.0 / speed
  if letter in [".", "!", "?", "…"]: char_timer += 0.16
  elif letter in [",", ":", ";"]: char_timer += 0.07
  if audio and not letter.strip_edges().is_empty() and visible_count % 3 == 1: audio.bleep(StringName(current_line().speaker))
  if letter in [".", "!", "?", ","]: autosave()
 if updated: text_changed.emit(text, visible_count)

func reveal() -> void:
 if not active: return
 visible_count = current_line().text_ru.length()
 if audio: audio.stop_speech()
 text_changed.emit(current_line().text_ru, visible_count)
 autosave()

func advance() -> bool:
 if not active: return false
 if visible_count < current_line().text_ru.length():
  reveal()
  return true
 if line_elapsed < float(current_line().get("hold_seconds", 0.0)): return false
 if history.is_empty() or history.back().line_id != current_line().line_id:
  history.append(current_line().duplicate(true))
 if line_index + 1 == data.lines.size():
  _finish()
 else:
  line_index += 1
  _enter_line()
 return true

func can_skip() -> bool:
 return active and seen.get(data.get("scene_id", ""), false)

func skip_seen() -> bool:
 if not can_skip(): return false
 _finish()
 return true

func _finish() -> void:
 if not active: return
 active = false
 var id: String = data.scene_id
 var old_seen := seen.duplicate()
 var old_ledger := ledger.duplicate()
 var old_flags := flags.duplicate()
 seen[id] = true
 var new_actions: Array[Dictionary] = []
 if not ledger.has(data.event_id):
  for action in data.get("exit_actions", []):
   flags[action.name] = action.value
   new_actions.append(action)
  ledger[data.event_id] = true
 # Persist completion before notifying observers: re-entry/reload cannot duplicate exit actions.
 if not autosave():
  active = true
  seen = old_seen
  ledger = old_ledger
  flags = old_flags
  return
 if audio: audio.dialogue_active(false)
 for action in new_actions: exit_action.emit(action)
 finished.emit(StringName(id))

func autosave() -> bool:
 var temporary := save_path + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  last_error = FileAccess.get_open_error()
  return false
 file.store_string(JSON.stringify({"schema": 1, "resource": resource_path, "active": active,
  "line_index": line_index, "visible_count": visible_count, "line_elapsed": line_elapsed,
  "history": history, "seen": seen, "ledger": ledger, "flags": flags}, "  "))
 file.close()
 last_error = DirAccess.rename_absolute(temporary, save_path)
 return last_error == OK

func restore() -> bool:
 if not FileAccess.file_exists(save_path): return false
 var saved: Variant = JSON.parse_string(FileAccess.get_file_as_string(save_path))
 if not saved is Dictionary or saved.get("schema") != 1: return false
 if not saved.get("resource") is String or not String(saved.resource).begins_with("res://resources/dialogue/"): return false
 for key in ["seen", "ledger", "flags"]:
  if not saved.get(key) is Dictionary: return false
 flags = saved.flags.duplicate()
 if not load_scene(saved.resource): return false
 line_index = clampi(int(saved.get("line_index", 0)), 0, data.lines.size() - 1)
 visible_count = clampi(int(saved.get("visible_count", 0)), 0, current_line().text_ru.length())
 line_elapsed = maxf(0.0, float(saved.get("line_elapsed", 0.0)))
 history.assign(saved.get("history", []))
 seen = saved.seen.duplicate()
 ledger = saved.ledger.duplicate()
 active = bool(saved.get("active", false))
 if audio: audio.dialogue_active(active)
 if active:
  line_changed.emit(current_line())
  text_changed.emit(current_line().text_ru, visible_count)
 return true
