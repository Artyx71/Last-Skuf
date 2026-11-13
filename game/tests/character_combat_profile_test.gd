extends SceneTree
const Profile = preload("res://scripts/systems/character_combat_profile.gd")
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
  check(Profile.resolve_finisher("yakuza","training",category,base[category]) == base[category], "weak Yakuza profile unchanged: " + category)
  check(Profile.resolve_finisher("timka","peaceful_present",category,base[category]).is_empty(), "peaceful Timka cannot gain prime finisher: " + category)
  check(Profile.resolve_finisher("timka","unknown",category,base[category]).is_empty(), "unknown Timka context denies: " + category)
  var prime := Profile.resolve_finisher("timka","athletic_prime",category,base[category])
  check(not prime.is_empty() and prime.character_style == "prime_grapple" and prime.damage == base[category].damage and prime.weapon == base[category].weapon, "trusted prime preserves existing weapon/damage eligibility: " + category)
  for id in ["gabar","olezhka","ryzhik","tega","pasha"]:
   var resolved := Profile.resolve_finisher(id,"training",category,base[category])
   check(not resolved.is_empty() and resolved.character_id == id and resolved.windup < base[category].windup, "independent copied character profile: " + id + ":" + category)
   resolved["damage"] = 999
 check(JSON.stringify(base) == original, "resolving/mutating hero result never changes global Yakuza definitions")
 check(Profile.resolve_finisher("kaban","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("ellana","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("elya","training","unarmed",base.unarmed).is_empty(), "supporting portraits do not grant combat abilities")
 check(Profile.resolve_finisher("unknown","training","unarmed",base.unarmed).is_empty() and Profile.resolve_finisher("gabar","unknown","unarmed",base.unarmed).is_empty(), "unknown identity or scene context denied")
 check(Profile.resolve_finisher("gabar","training","firearm",base.unarmed).is_empty(), "mismatched weapon category definition rejected")
 print("RESULT passed=%d failed=%d" % [passed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
