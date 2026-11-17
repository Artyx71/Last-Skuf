extends RefCounted
## Pure copy-on-resolve character tuning. A trusted scene supplies the context.
const Characters = preload("res://scripts/systems/character_catalog.gd")
const PATH := "res://resources/characters/combat_profiles.json"

static func resolve_finisher(actor_id: String, context: String, category: String, base: Dictionary) -> Dictionary:
 if not Characters.valid_context(actor_id, context) or base.is_empty(): return {}
 if category not in Characters.allowed_equipment(actor_id, context): return {}
 if base.get("category") != category: return {}
 # Existing Yakuza clocks/risks are never changed by selecting another character.
 if actor_id == "yakuza": return base.duplicate(true)
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not parsed is Dictionary or parsed.get("schema") != 1: return {}
 var profile: Dictionary = parsed.get("profiles", {}).get(actor_id, {})
 if profile.is_empty() or context not in profile.get("contexts", []): return {}
 var result := base.duplicate(true)
 for phase in ["windup", "active", "recovery"]:
  var time_value: Variant = profile.get("finisher", {}).get(phase)
  if not (time_value is float or time_value is int) or float(time_value) <= 0: return {}
  result[phase] = float(time_value)
 result["character_id"] = actor_id
 result["character_style"] = profile.style
 result["scene_context"] = context
 return result
