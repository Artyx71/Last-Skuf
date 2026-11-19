extends RefCounted
## P04 single-chapter save, deliberately bounded before P05 story graph work.
const CHAPTER := "CH01_THE_MISSED_FIGHT"
const DEFAULTS := {"schema": 1, "chapter": CHAPTER, "checkpoint": "start", "completed": false,
 "best_score": 0, "completion_events": 0, "deaths": 0}
var data: Dictionary = DEFAULTS.duplicate(true)
var path := "user://chapter01_v1.json"
var last_error := OK
var load_status := "NEW"

func _init() -> void:
 var override := OS.get_environment("AYAY_CHAPTER_SAVE_PATH")
 if not override.is_empty(): path = override

func load_progress() -> bool:
 if not FileAccess.file_exists(path): return true
 var parser := JSON.new()
 if parser.parse(FileAccess.get_file_as_string(path)) != OK:
  load_status = "INVALID_SAVE"
  return false
 var value: Variant = parser.data
 if not value is Dictionary or value.get("schema") != 1 or value.get("chapter") != CHAPTER:
  load_status = "INVALID_SAVE"
  return false
 if not value.get("checkpoint") in ["start", "service", "complete"] or not value.get("completed") is bool:
  load_status = "INVALID_SAVE"
  return false
 for key in ["best_score", "completion_events", "deaths"]:
  var number: Variant = value.get(key)
  if not (number is int or number is float) or not is_finite(float(number)) or number < 0 or number != floor(float(number)):
   load_status = "INVALID_SAVE"
   return false
 if value.completion_events > 1 or value.completed != (value.completion_events == 1) or (value.checkpoint == "complete" and not value.completed):
  load_status = "INVALID_SAVE"
  return false
 data = value.duplicate(true)
 load_status = "LOADED"
 return true

func save(candidate: Dictionary) -> bool:
 var temporary := path + ".tmp"
 var file := FileAccess.open(temporary, FileAccess.WRITE)
 if file == null:
  last_error = FileAccess.get_open_error()
  return false
 file.store_string(JSON.stringify(candidate, "  "))
 file.flush()
 var write_error := file.get_error()
 file.close()
 if write_error != OK:
  last_error = write_error
  return false
 last_error = DirAccess.rename_absolute(temporary, path)
 if last_error != OK: return false
 data = candidate.duplicate(true)
 return true

func checkpoint(id: String) -> bool:
 if not id in ["start", "service"]: return false
 var next := data.duplicate(true)
 next.checkpoint = id
 return save(next)

func record_death() -> bool:
 var next := data.duplicate(true)
 next.deaths += 1
 return save(next)

func complete(score: int) -> bool:
 var next := data.duplicate(true)
 next.completed = true
 next.checkpoint = "complete"
 next.completion_events = 1
 next.best_score = maxi(int(next.best_score), score)
 return save(next)
