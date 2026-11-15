extends RefCounted
## Read-only asset routing, never an equipment grant or a sound-quality verdict.
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const PATH := "res://assets/audio/character_finishers.json"
const FOLDER := "res://assets/audio/character_finishers/"
const ACTORS := ["gabar","olezhka","timka","ryzhik","tega","pasha"]

static func cue_id(actor_id: String, category: String) -> String:
 return "finish_"+actor_id+("_prime" if actor_id=="timka" else "")+"_"+category

static func _valid_manifest(data: Variant, require_resources := true) -> bool:
 if not data is Dictionary: return false
 var schema: Variant=data.get("schema")
 if not (schema is int or schema is float) or schema!=1: return false
 var sounds: Variant=data.get("sfx")
 if not sounds is Dictionary: return false
 var expected_count:=0
 for actor_id in ACTORS:
  var context: String="athletic_prime" if actor_id=="timka" else "training"
  var categories: Array=Catalog.allowed_equipment(actor_id,context)
  if categories.is_empty(): return false
  for category in categories:
   expected_count+=1
   var cue:=cue_id(actor_id,category)
   var entry: Variant=sounds.get(cue)
   if not entry is Dictionary: return false
   if entry.get("actor_id")!=actor_id or entry.get("context")!=context or entry.get("category")!=category: return false
   if entry.get("path")!=FOLDER+cue+".wav" or entry.get("bus")!="SFX": return false
   var gain: Variant=entry.get("gain_db")
   if not (gain is float or gain is int): return false
   if not (float(gain)>=-24.0 and float(gain)<=0.0): return false
   if require_resources and not ResourceLoader.exists(entry.path): return false
 return sounds.size()==expected_count

static func entries() -> Dictionary:
 if not FileAccess.file_exists(PATH): return {}
 var data: Variant=JSON.parse_string(FileAccess.get_file_as_string(PATH))
 if not _valid_manifest(data): return {}
 return data.sfx.duplicate(true)

static func cue_for(actor_id: String, context: String, category: String) -> String:
 if actor_id not in ACTORS: return ""
 var required: String="athletic_prime" if actor_id=="timka" else "training"
 if context!=required or category not in Catalog.allowed_equipment(actor_id,context): return ""
 var cue:=cue_id(actor_id,category)
 return cue if entries().has(cue) else ""
