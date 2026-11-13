extends RefCounted
## Immutable IDs and authored availability. Future timestamps remain explicitly unassigned.
const CH01 := "CH01_THE_MISSED_FIGHT"
const PRIMARY := ["ENDING_WIFE_CALLING", "ENDING_BROTHERHOOD", "ENDING_FAMILY_BUSINESS"]
var data: Dictionary
var routes: Dictionary
var chapters := {}
var events := {}
var decisions := {}
var errors: Array[String] = []

func _init(source: Dictionary = {}, route_source: Dictionary = {}) -> void:
 data = source.duplicate(true) if not source.is_empty() else JSON.parse_string(FileAccess.get_file_as_string("res://resources/story/registry.json"))
 routes = route_source.duplicate(true) if not route_source.is_empty() else JSON.parse_string(FileAccess.get_file_as_string("res://resources/story/routes.json"))
 validate()

static func integer(value: Variant, low: int, high: int) -> bool:
 return (value is int or value is float) and is_finite(float(value)) and value == floor(float(value)) and value >= low and value <= high

func declared(path: String) -> bool:
 var parts := path.split(".")
 if parts.size() != 2: return false
 if parts[0] == "choices": return decisions.has(parts[1])
 if not parts[0] in ["flags", "evidence", "relationships", "secrets"]: return false
 return parts[1] in data.get(parts[0], [])

func valid_condition(value: Variant) -> bool:
 if not value is Dictionary or value.size() != 1: return false
 if value.has("all") or value.has("any"):
  var list: Variant = value.get("all", value.get("any"))
  if not list is Array: return false
  for child in list:
   if not valid_condition(child): return false
  return true
 if value.has("not"): return valid_condition(value["not"])
 if not value.has("eq") or not value.eq is Array or value.eq.size() != 2 or not value.eq[0] is String: return false
 if not declared(value.eq[0]): return false
 return integer(value.eq[1], -2, 2) if value.eq[0].begins_with("relationships.") else value.eq[1] is bool

func meets(condition: Dictionary, state: Dictionary) -> bool:
 if not valid_condition(condition): return false
 if condition.has("all"):
  for child in condition.all:
   if not meets(child, state): return false
  return true
 if condition.has("any"):
  for child in condition.any:
   if meets(child, state): return true
  return false
 if condition.has("not"): return not meets(condition["not"], state)
 var parts: PackedStringArray = String(condition.eq[0]).split(".")
 # Missing is not deliberate false; defaults cannot count as concealment.
 return state.get(parts[0], {}).has(parts[1]) and state[parts[0]][parts[1]] == condition.eq[1]

func valid_effects(value: Variant) -> bool:
 if not value is Dictionary: return false
 for path in value:
  if not path is String or not declared(path) or path.begins_with("choices."): return false
  if path.begins_with("relationships."):
   if not integer(value[path], -2, 2): return false
  elif not value[path] is bool: return false
 return true

func validate() -> bool:
 errors.clear(); chapters.clear(); events.clear(); decisions.clear()
 if data.get("schema") != 1 or not data.get("chapters") is Array or data.chapters.size() != 21:
  errors.append("registry_schema"); return false
 for group in ["flags", "evidence", "secrets", "relationships"]:
  if not data.get(group) is Array: errors.append("declarations"); return false
  var names := {}
  for name in data[group]:
   if not name is String or names.has(name): errors.append("duplicate_declaration"); return false
   names[name] = true
 var positions := {}
 for c in data.chapters:
  if not c is Dictionary: errors.append("chapter_type"); continue
  for key in ["id", "event_id", "title_ru", "period", "timestamp", "timestamp_status", "location", "availability", "scene"]:
   if not c.get(key) is String: errors.append("chapter_field_"+key)
  if not errors.is_empty(): return false
  if chapters.has(c.id) or events.has(c.event_id): errors.append("duplicate_id")
  if not integer(c.get("presentation"), 1, 21) or positions.has(c.get("presentation")): errors.append("presentation")
  if not integer(c.get("chronology"), 1, 10000): errors.append("chronology")
  if not c.get("prerequisites") is Array or not c.get("povs") is Array or c.povs.is_empty(): errors.append("chapter_arrays"); return false
  var actors := {}
  for actor in c.povs:
   if not actor in ["YAKUZA","GABAR","OLEZHKA","TIMKA","RYZHIK","TEGA","PASHA"] or actors.has(actor): errors.append("pov")
   actors[actor] = true
  if not c.availability in ["playable", "planned"]: errors.append("availability")
  if c.availability == "planned" and (c.scene != "" or c.timestamp_status != "production_pending" or c.timestamp != ""): errors.append("planned_content")
  if c.availability == "playable" and (c.id != CH01 or c.scene != "res://scenes/levels/missed_fight.tscn" or not ResourceLoader.exists(c.scene)): errors.append("playable_content")
  positions[c.get("presentation")] = true
  chapters[c.id] = c
  events[c.event_id] = {"id":c.event_id,"chapter":c.id,"kind":"complete","effects":{},"condition":{"all":[]},"prerequisites":c.prerequisites}
 if not chapters.has(CH01): errors.append("missing_ch01"); return false
 var first: Dictionary = chapters[CH01]
 if first.event_id != "EV_CH01_SERVICE_ESCAPE" or first.timestamp != "2023-10-14T22:18:00+03:00" or first.povs != ["YAKUZA"] or first.availability != "playable": errors.append("canonical_ch01")
 for d in data.get("decisions", []):
  if not d is Dictionary or not d.get("id") is String or decisions.has(d.id): errors.append("duplicate_decision"); continue
  decisions[d.id] = d
 if decisions.keys().size() != 6: errors.append("six_decisions")
 for i in range(1, 7):
  if not decisions.has("D%02d" % i): errors.append("decision_id")
 for d in decisions.values():
  if not chapters.has(d.get("chapter")) or not valid_effects(d.get("accept")) or not valid_effects(d.get("refuse")): errors.append("decision_effects")
 for e in data.get("events", []):
  if not e is Dictionary or not e.get("id") is String: errors.append("event_type"); continue
  if events.has(e.id): errors.append("duplicate_event")
  if not chapters.has(e.get("chapter")) or not e.get("kind") in ["dialogue","record","decision"] or not e.get("prerequisites") is Array: errors.append("event_fields"); continue
  if not valid_condition(e.get("condition")) or not valid_effects(e.get("effects")): errors.append("event_conditions")
  if e.kind == "decision" and (not decisions.has(e.id.trim_prefix("EV_")) or decisions[e.id.trim_prefix("EV_")].chapter != e.chapter): errors.append("decision_event")
  events[e.id] = e
 for e in events.values():
  for dependency in e.prerequisites:
   if not events.has(dependency): errors.append("unknown_prerequisite"); continue
   if chapters[events[dependency].chapter].chronology > chapters[e.chapter].chronology: errors.append("backward_causality")
 for a in chapters.values():
  for b in chapters.values():
   if a.id == b.id or a.period != b.period or a.chronology != b.chronology or a.location == b.location: continue
   for actor in a.povs:
    if actor in b.povs: errors.append("simultaneous_pov_conflict")
 var reached := {}
 for iteration in events.size()+1:
  for e in events.values():
   var ready := true
   for dep in e.prerequisites:
    if not reached.has(dep): ready = false
   # Optional events also depend on chapter entry, independent of presentation order.
   for dep in chapters[e.chapter].prerequisites:
    if not reached.has(dep): ready = false
   if ready: reached[e.id] = true
 if reached.size() != events.size(): errors.append("cycle_or_unreachable")
 if routes.get("schema") != 1 or not routes.get("primary") is Dictionary: errors.append("route_schema"); return false
 if routes.primary.size() != 3: errors.append("primary_count")
 for id in PRIMARY:
  if not routes.primary.has(id) or not valid_condition(routes.primary[id].get("condition")): errors.append("route_condition")
 if not valid_condition(routes.get("overlay", {}).get("condition")): errors.append("overlay_condition")
 return errors.is_empty()

func entry_ready(chapter: String, state: Dictionary, planned := false) -> bool:
 if not errors.is_empty() or not chapters.has(chapter): return false
 if not planned and chapters[chapter].availability != "playable": return false
 for id in chapters[chapter].prerequisites:
  if not state.ledger.has(id): return false
 return true
