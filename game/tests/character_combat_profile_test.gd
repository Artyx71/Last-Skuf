extends SceneTree
const Profile = preload("res://scripts/systems/character_combat_profile.gd")
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const EXPECTED := {
 "gabar":["unarmed","blunt","firearm"], "olezhka":["unarmed","blunt","sharp"],
 "timka":["unarmed","blunt","environmental"], "ryzhik":["unarmed","blunt","environmental"],
 "tega":["unarmed","blunt","environmental"], "pasha":["unarmed","blunt","sharp","firearm","environmental"]
}
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
 if ok: passed += 1;print("PASS ",label)
 else: failed += 1;push_error("FAIL " + label)
func run() -> void:
 var base: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/finishers.json")).definitions
 var original := JSON.stringify(base)
 for category in base:
  check(Profile.resolve_finisher("yakuza","training",category,base[category]) == base[category], "weak Yakuza training clocks unchanged: " + category)
  check(Profile.resolve_finisher("yakuza","campaign",category,base[category]).is_empty(), "campaign escape kit grants no training finisher: " + category)
  check(Profile.resolve_finisher("timka","peaceful_present",category,base[category]).is_empty(), "peaceful Timka denies finisher: " + category)
  check(Profile.resolve_finisher("timka","unknown",category,base[category]).is_empty(), "unknown Timka context denies: " + category)
  for id in EXPECTED:
   var context := "athletic_prime" if id == "timka" else "training"
   var resolved := Profile.resolve_finisher(id,context,category,base[category])
   if category in EXPECTED[id]:
    check(not resolved.is_empty() and resolved.character_id == id and resolved.damage == base[category].damage and resolved.weapon == base[category].weapon, "allowed copied profile preserves damage/weapon: " + id + ":" + category)
    resolved["damage"] = 999
   else:
    check(resolved.is_empty(), "denied character/equipment pair: " + id + ":" + category)
 for id in EXPECTED:
  check(Catalog.allowed_equipment(id,"athletic_prime" if id=="timka" else "training") == EXPECTED[id], "explicit per-context equipment: " + id)
 check(Catalog.allowed_equipment("timka","peaceful_present").is_empty() and Catalog.allowed_equipment("timka","unknown").is_empty(), "present/unknown equipment grants empty")
 check(JSON.stringify(base) == original, "resolving/mutating hero copy never changes global Yakuza definitions")
 check(Profile.resolve_finisher("kaban","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("ellana","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("elya","training","unarmed",base.unarmed).is_empty(), "supporting portraits grant no combat")
 check(Profile.resolve_finisher("unknown","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("gabar","unknown","unarmed",base.unarmed).is_empty(), "unknown identity/context denied")
 check(Profile.resolve_finisher("gabar","training","firearm",base.unarmed).is_empty(), "mismatched category definition rejected")
 print("RESULT passed=%d failed=%d" % [passed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
