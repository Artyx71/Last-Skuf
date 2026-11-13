extends RefCounted
## Validated identities and presentation data; no story unlocks or inferred abilities.
const PATH := "res://resources/characters/catalog.json"
const EXPRESSIONS := ["neutral", "angry", "surprise", "hurt", "catchphrase"]
const EQUIPMENT := ["unarmed", "blunt", "sharp", "firearm", "environmental"]

static func entries() -> Dictionary:
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not parsed is Dictionary or parsed.get("schema") != 1: return {}
 var actors: Variant = parsed.get("actors")
 if not actors is Dictionary: return {}
 for id in actors:
  var actor: Variant = actors[id]
  if not actor is Dictionary or actor.get("actor_id") != id: return {}
  if actor.get("speaker_id") != String(id).to_upper(): return {}
  if not actor.get("role") in ["playable", "supporting"]: return {}
  if actor.get("expressions") != EXPRESSIONS: return {}
  if not actor.get("contexts") is Array or actor.contexts.is_empty(): return {}
  if not actor.get("equipment_categories") is Array: return {}
  for category in actor.equipment_categories:
   if category not in EQUIPMENT: return {}
  if actor.role == "playable":
   var matrix: Variant = actor.get("equipment_by_context")
   if not matrix is Dictionary or matrix.size() != actor.contexts.size(): return {}
   for context in actor.contexts:
    if not matrix.get(context) is Array: return {}
    for category in matrix[context]:
     if category not in actor.equipment_categories: return {}
  if actor.role == "supporting" and (not actor.equipment_categories.is_empty() or not String(actor.get("ability_id", "")).is_empty()): return {}
 return actors

static func actor(id: String) -> Dictionary:
 return entries().get(id, {}).duplicate(true)

static func speaker(id: String) -> Dictionary:
 var definition := actor(id.to_lower())
 return definition if definition.get("speaker_id") == id else {}

static func valid_line(speaker_id: String, emotion: String) -> bool:
 var definition := speaker(speaker_id)
 return not definition.is_empty() and emotion in definition.expressions

static func valid_context(actor_id: String, context: String) -> bool:
 var definition := actor(actor_id)
 return not definition.is_empty() and definition.role == "playable" and context in definition.contexts

static func presentation_ready(actor_id: String) -> bool:
 var definition := actor(actor_id)
 return not definition.is_empty() and ResourceLoader.exists(definition.portrait_file)

static func allowed_equipment(actor_id: String, context: String) -> Array:
 var definition := actor(actor_id)
 if definition.get("role") != "playable" or context not in definition.get("contexts", []): return []
 return definition.equipment_by_context.get(context, []).duplicate()
