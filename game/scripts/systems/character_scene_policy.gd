extends RefCounted
## Scene-owned P06 authority. No save/actor/context dictionary is accepted as input.
## Host must reset CombatSystem before switching fixture; generation also revokes jobs.
const PATH := "res://resources/characters/sandbox_scenes.json"
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const Profile = preload("res://scripts/systems/character_combat_profile.gd")
var _active: Dictionary = {}
var _generation := 0

static func definitions() -> Dictionary:
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not parsed is Dictionary or parsed.get("schema") != 1: return {}
 var scenes: Variant = parsed.get("scenes")
 if not scenes is Dictionary: return {}
 for id in scenes:
  var scene: Variant = scenes[id]
  if not scene is Dictionary or scene.get("scene_id") != id: return {}
  if not scene.get("actor_id") is String or not scene.get("context") is String: return {}
  if not Catalog.valid_context(scene.actor_id,scene.context): return {}
  if not scene.get("equipment_categories") is Array: return {}
  var allowed := Catalog.allowed_equipment(scene.actor_id,scene.context)
  for category in scene.equipment_categories:
   if category not in allowed: return {}
 return scenes.duplicate(true)

func open(scene_id: String) -> bool:
 # Only a resource-registered scene key is accepted. Never load this from a save's
 # actor/context fields. Sandbox selection explicitly starts a fresh host fixture.
 _generation += 1
 _active = definitions().get(scene_id,{}).duplicate(true)
 return not _active.is_empty()

func invalidate() -> void:
 _generation += 1
 _active.clear()

func definition() -> Dictionary:
 return _active.duplicate(true)

func action_authority(actor_id: String) -> Dictionary:
 if _active.is_empty() or actor_id != _active.actor_id: return {}
 return {"actor_id":actor_id,"context":_active.context,"fixture_id":_active.scene_id,
  "generation":_generation,"scene_instance":get_instance_id()}

func finisher_authority(actor_id: String, category: String, equipped_category: String) -> Dictionary:
 if _active.is_empty() or actor_id != _active.actor_id or category != equipped_category: return {}
 if category not in _active.equipment_categories or category not in Catalog.allowed_equipment(actor_id,_active.context): return {}
 return {"actor_id":actor_id,"context":_active.context,"fixture_id":_active.scene_id,
  "generation":_generation,"scene_instance":get_instance_id(),"category":category}

func resolve_finisher(actor_id: String, category: String, equipped_category: String, base: Dictionary) -> Dictionary:
 if finisher_authority(actor_id,category,equipped_category).is_empty(): return {}
 return Profile.resolve_finisher(actor_id,_active.context,category,base)

func movement_speed() -> float:
 if _active.is_empty(): return 0.0
 var actor := Catalog.actor(_active.actor_id)
 return float(actor.get("context_rules",{}).get(_active.context,{}).get("speed",actor.speed))

func ability_id() -> String:
 if _active.is_empty(): return ""
 var actor := Catalog.actor(_active.actor_id)
 return String(actor.get("context_rules",{}).get(_active.context,{}).get("ability",actor.ability_id))
