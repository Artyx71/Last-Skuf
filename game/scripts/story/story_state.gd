extends RefCounted
## Event-sourced story facts. Commit is publish-after-rename; replay never writes campaign data.
const Registry = preload("res://scripts/story/story_registry.gd")
const VERSION := 2
var registry: RefCounted
var state: Dictionary
var path := "user://story_v2.json"
var status := "NEW"
var last_error := ""
var writable := true
var simulation := false
var replay := false

func _init(planned := false) -> void:
 simulation = planned
 registry = Registry.new()
 state = fresh()

func fresh() -> Dictionary:
 var result := {"schema":VERSION,"domain":"scenario" if simulation else "campaign","history":[],"ledger":{},"chapter_complete":{},"choices":{},"flags":{},"evidence":{},"relationships":{},"secrets":{},"unlocks":[Registry.CH01],"endings":{"unlocked":[Registry.PRIMARY[0]],"completed":[]},"completion_rewards":0}
 for group in ["flags","evidence","secrets","relationships"]:
  for id in registry.data[group]: result[group][id] = 0 if group == "relationships" else false
 return result

func _fail(message: String) -> bool:
 last_error = message
 return false

func _effects(candidate: Dictionary, effects: Dictionary) -> void:
 for path_id in effects:
  var parts: PackedStringArray = String(path_id).split(".")
  if parts[0] == "relationships": candidate[parts[0]][parts[1]] = clampi(candidate[parts[0]][parts[1]] + int(effects[path_id]), -2, 2)
  else: candidate[parts[0]][parts[1]] = effects[path_id]

func _apply(candidate: Dictionary, id: String, value: Variant) -> bool:
 if not registry.errors.is_empty(): return _fail("REGISTRY_INVALID")
 if candidate.ledger.has(id):
  return true if candidate.ledger[id] == value and typeof(candidate.ledger[id]) == typeof(value) else _fail("CANONICAL_LOCKED")
 if id.begins_with("EV_ENDING_"):
  var route := id.trim_prefix("EV_")
  if not value is bool or not value or not registry.PRIMARY.has(route): return _fail("ENDING_INVALID")
  var final_id: String = registry.data.chapters[20].id
  if not candidate.chapter_complete.has(final_id) or not route in eligible(candidate): return _fail("ENDING_UNAVAILABLE")
  if not candidate.endings.completed.is_empty(): return _fail("PRIMARY_LOCKED")
  candidate.endings.completed.append(route)
 elif id == "EV_REAL_PRIME_OVERLAY":
  if not value is bool or not value or not overlay_eligible(candidate): return _fail("OVERLAY_UNAVAILABLE")
  candidate.endings.completed.append("ENDING_REAL_PRIME")
 else:
  if not registry.events.has(id): return _fail("UNKNOWN_EVENT")
  var event: Dictionary = registry.events[id]
  if not registry.entry_ready(event.chapter, candidate, simulation): return _fail("CHAPTER_UNAVAILABLE")
  if candidate.chapter_complete.has(event.chapter): return _fail("CHAPTER_CLOSED")
  for dependency in event.prerequisites:
   if not candidate.ledger.has(dependency): return _fail("EVENT_ORDER")
  if not registry.meets(event.condition, candidate): return _fail("CONDITION_UNMET")
  if event.kind == "decision":
   if not value is bool: return _fail("CHOICE_TYPE")
   var decision_id := id.trim_prefix("EV_")
   var definition: Dictionary = registry.decisions[decision_id]
   candidate.choices[decision_id] = value
   _effects(candidate, definition.accept if value else definition.refuse)
  else:
   if not value is bool or not value: return _fail("EVENT_TYPE")
   _effects(candidate, event.effects)
  if event.kind == "complete":
   candidate.chapter_complete[event.chapter] = true
   candidate.completion_rewards += 1
 candidate.ledger[id] = value
 candidate.history.append({"id":id,"value":value})
 candidate.unlocks.clear()
 for c in registry.data.chapters:
  if registry.entry_ready(c.id, candidate, true): candidate.unlocks.append(c.id)
 candidate.endings.unlocked = eligible(candidate)
 return true

func eligible(candidate: Dictionary = {}) -> Array:
 var current: Dictionary = state if candidate.is_empty() else candidate
 var result: Array = [registry.PRIMARY[0]]
 # Eligibility is a plan for the final act, never permission to launch planned content.
 if not current.chapter_complete.has(registry.data.chapters[19].id): return result
 for id in [registry.PRIMARY[1],registry.PRIMARY[2]]:
  if registry.meets(registry.routes.primary[id].condition, current): result.append(id)
 return result

func overlay_eligible(candidate: Dictionary = {}) -> bool:
 var current: Dictionary = state if candidate.is_empty() else candidate
 return not current.endings.completed.is_empty() and registry.meets(registry.routes.overlay.condition, current)

func route_plan(route: String) -> Dictionary:
 if not route in eligible(): return {}
 var result: Dictionary = registry.routes.primary[route].duplicate(true)
 result.erase("condition")
 result["content_available"] = false
 result["ally_entry"] = "olezhka_access" if state.flags.kimono_truth else "independent_entry"
 result["supplier"] = "ryzhik_ally_safe" if state.flags.ryzhik_warned else ("ryzhik_rival_exposed" if state.choices.has("D03") else "ryzhik_unresolved")
 result["cyberx_escape"] = "backup_preserved_exposure_risk" if state.flags.pasha_shared_evidence else ("sale_exposure_trust_lost" if state.choices.has("D02") else "no_archive_support")
 result["group_at_18"] = "gabar_publicly_cleared" if state.flags.gabar_exonerated else "gabar_questioned"
 result["proof_at_20"] = "independent_phone_corroboration" if state.flags.phone_decoded else "financial_witness_route"
 result["evidence_escape"] = "public_exposure" if state.evidence.illegal_operations and state.evidence.founding_records else "protect_surviving_clues"
 result["secret_overlay"] = overlay_eligible()
 return result

func _equivalent(actual: Variant, expected: Variant) -> bool:
 if expected is int: return Registry.integer(actual,expected,expected)
 if typeof(actual) != typeof(expected): return false
 if expected is Dictionary:
  if actual.size() != expected.size(): return false
  for key in expected:
   if not actual.has(key) or not _equivalent(actual[key],expected[key]): return false
  return true
 if expected is Array:
  if actual.size() != expected.size(): return false
  for i in expected.size():
   if not _equivalent(actual[i],expected[i]): return false
  return true
 return actual == expected

func validate(value: Variant) -> bool:
 if not value is Dictionary or value.get("schema") != VERSION or not Registry.integer(value.get("schema"),VERSION,VERSION): return _fail("SCHEMA_VERSION")
 if value.get("domain") != ("scenario" if simulation else "campaign") or not value.get("history") is Array or value.history.size() > 128: return _fail("SAVE_DOMAIN_OR_HISTORY")
 var rebuilt := fresh()
 for row in value.history:
  if not row is Dictionary or row.size() != 2 or not row.get("id") is String or not row.get("value") is bool: return _fail("HISTORY_TYPE")
  if rebuilt.ledger.has(row.id) or not _apply(rebuilt, row.id, row.value): return _fail("HISTORY_INVALID")
 # Exact derived state comparison rejects missing/extra keys, forged relationships/rewards,
 # arbitrary flags and partial saves; JSON numbers are also range/type checked below.
 if not _equivalent(value,rebuilt): return _fail("DERIVED_STATE_MISMATCH")
 if not Registry.integer(value.completion_rewards,0,21): return _fail("REWARD_RANGE")
 for group in ["flags","evidence","secrets","choices","chapter_complete","ledger"]:
  for item in value[group].values():
   if not item is bool: return _fail("BOOL_TYPE")
 for number in value.relationships.values():
  if not Registry.integer(number,-2,2): return _fail("RELATIONSHIP_RANGE")
 return true

func _write(candidate: Dictionary) -> bool:
 if not writable or replay: return _fail("WRITE_DISABLED")
 var temporary := path+".tmp"
 var file := FileAccess.open(temporary,FileAccess.WRITE)
 if file == null: return _fail("OPEN_FAILED")
 file.store_string(JSON.stringify(candidate,"  "))
 file.flush()
 var error := file.get_error()
 file.close()
 if error != OK:
  DirAccess.remove_absolute(temporary)
  return _fail("WRITE_FAILED")
 # Same-directory rename leaves the old save intact on failure.
 if DirAccess.rename_absolute(temporary,path) != OK:
  DirAccess.remove_absolute(temporary)
  return _fail("RENAME_FAILED")
 return true

func record(id: String, value: Variant = true) -> bool:
 if not writable: return _fail("WRITE_DISABLED")
 var candidate := state.duplicate(true)
 if not _apply(candidate,id,value): return false
 if candidate == state: return true
 if not replay and not _write(candidate): return false
 state = candidate
 return true

func choose(id: String, accepted: bool) -> bool:
 return record("EV_"+id, accepted)

func complete_chapter(id: String) -> bool:
 if not registry.chapters.has(id): return _fail("UNKNOWN_CHAPTER")
 return record(registry.chapters[id].event_id)

func finish_story(route: String) -> bool:
 return record("EV_"+route)

func finish_overlay() -> bool:
 return record("EV_REAL_PRIME_OVERLAY")

func fork_replay() -> RefCounted:
 var sandbox: RefCounted = get_script().new(simulation)
 sandbox.state = state.duplicate(true)
 sandbox.replay = true
 sandbox.path = ""
 return sandbox

static func read_json(filename: String) -> Variant:
 var parser := JSON.new()
 return parser.data if parser.parse(FileAccess.get_file_as_string(filename)) == OK else null

func load_save(chapter_path := "", dialogue_path := "") -> bool:
 if FileAccess.file_exists(path):
  var parsed: Variant = read_json(path)
  if not validate(parsed):
   writable = false; status = "INVALID_PRESERVED"
   return false
  state = fresh()
  for row in parsed.history: _apply(state,row.id,row.value)
  status = "LOADED"
  return true
 return migrate_legacy(chapter_path,dialogue_path)

func migrate_legacy(chapter_path: String, dialogue_path: String) -> bool:
 var candidate := fresh()
 var has_legacy := false
 if not chapter_path.is_empty() and FileAccess.file_exists(chapter_path):
  var old := preload("res://scripts/levels/chapter_progress.gd").new()
  old.path = chapter_path
  if not old.load_progress():
   writable = false; status = "LEGACY_INVALID_PRESERVED"; return _fail("LEGACY_CHAPTER_INVALID")
  has_legacy = true
  if old.data.completed:
   if not _apply(candidate,"EV_CH01_SERVICE_ESCAPE",true): return false
 if not dialogue_path.is_empty() and FileAccess.file_exists(dialogue_path):
  var old: Variant = read_json(dialogue_path)
  if not _valid_legacy_dialogue(old):
   writable = false; status = "LEGACY_INVALID_PRESERVED"; return _fail("LEGACY_DIALOGUE_INVALID")
  has_legacy = true
  # Completion may already be migrated; preserve dialogue facts before chapter close.
  var completed: bool = candidate.chapter_complete.has(Registry.CH01)
  candidate = fresh()
  for suffix in ["INTRO","PHONE","OUTRO"]:
   if old.ledger.get("EV_CH01_"+suffix,false):
    if not _apply(candidate,"EV_CH01_"+suffix,true): return false
  if completed and not _apply(candidate,"EV_CH01_SERVICE_ESCAPE",true): return false
 if has_legacy:
  if not _write(candidate): status = "MIGRATION_WRITE_FAILED"; return false
  state = candidate; status = "MIGRATED"
 return true

func _valid_legacy_dialogue(old: Variant) -> bool:
 if not old is Dictionary or not Registry.integer(old.get("schema"),1,1): return false
 for group in ["ledger","seen","flags"]:
  if not old.get(group) is Dictionary: return false
  for value in old[group].values():
   if not value is bool: return false
 if not old.get("active") is bool or not old.get("resource") is String or not old.resource.begins_with("res://resources/dialogue/"): return false
 if not FileAccess.file_exists(old.resource): return false
 var resource: Variant = JSON.parse_string(FileAccess.get_file_as_string(old.resource))
 if not resource is Dictionary or not resource.get("lines") is Array: return false
 if not Registry.integer(old.get("line_index"),0,resource.lines.size()-1): return false
 if not Registry.integer(old.get("visible_count"),0,String(resource.lines[int(old.line_index)].text_ru).length()): return false
 if not old.get("line_elapsed") is float and not old.get("line_elapsed") is int: return false
 if not is_finite(float(old.line_elapsed)) or old.line_elapsed < 0 or not old.get("history") is Array: return false
 for line in old.history:
  if not line is Dictionary or not line.get("line_id") is String or not line.get("text_ru") is String: return false
 return true
