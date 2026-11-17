extends SceneTree
const Policy = preload("res://scripts/systems/character_scene_policy.gd")
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
 if ok: passed += 1;print("PASS ",label)
 else: failed += 1;push_error("FAIL " + label)
func run() -> void:
 var policy := Policy.new()
 check(policy.definition().is_empty() and policy.finisher_authority("timka","unarmed","unarmed").is_empty(), "no authority before registered scene opens")
 var definitions := Policy.definitions()
 check(definitions.size()==7, "seven explicit six-hero/context fixtures, no support/Yakuza replacement")
 var base: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/finishers.json")).definitions
 for scene_id in definitions:
  var d: Dictionary=definitions[scene_id]
  check(policy.open(scene_id) and policy.definition()==d, "registered immutable resource fixture opens: "+scene_id)
  for category in ["unarmed","blunt","sharp","firearm","environmental"]:
   var authority := policy.finisher_authority(d.actor_id,category,category)
   var resolved := policy.resolve_finisher(d.actor_id,category,category,base[category])
   var allowed: bool=category in d.equipment_categories
   check((not authority.is_empty())==allowed and (not resolved.is_empty())==allowed, "scene/actor/equipment matrix: "+scene_id+":"+category)
   check(policy.finisher_authority("kaban",category,category).is_empty() and policy.finisher_authority("unknown",category,category).is_empty(), "actor substitution denied: "+scene_id+":"+category)
  var copy := policy.definition();copy.context="athletic_prime";copy.actor_id="pasha";copy.equipment_categories.append("sharp")
  check(policy.definition()==d, "mutating returned resource copy cannot grant context/equipment: "+scene_id)
 check(policy.open("timka_present") and policy.ability_id()=="disengage" and is_equal_approx(policy.movement_speed(),84), "present scene grants peaceful disengage, no prime movement")
 check(policy.open("timka_prime") and policy.ability_id()=="clinch" and is_equal_approx(policy.movement_speed(),118), "registered prime scene selects own movement/ability metadata only")
 var old := policy.finisher_authority("timka","unarmed","unarmed")
 var copy := old.duplicate(true);copy.context="peaceful_present";copy.generation=999
 check(policy.finisher_authority("timka","unarmed","unarmed")==old, "external authority copy cannot mutate scene owner")
 check(policy.open("timka_prime") and policy.finisher_authority("timka","unarmed","unarmed")!=old, "reopening same scene revokes prior generation")
 var second := Policy.new();second.open("timka_prime")
 check(second.finisher_authority("timka","unarmed","unarmed")!=policy.finisher_authority("timka","unarmed","unarmed"), "new scene owner has distinct instance authority")
 for unregistered in ["athletic_prime","training","timka","unknown","res://levels/prime.tscn",'{"actor_id":"timka","context":"athletic_prime"}']:
  check(not policy.open(unregistered) and policy.definition().is_empty() and policy.finisher_authority("timka","unarmed","unarmed").is_empty(), "save/context text cannot create registered scene: "+unregistered)
 policy.open("gabar_training")
 check(policy.finisher_authority("gabar","unarmed","blunt").is_empty(), "selected tool category must match requested category")
 policy.invalidate()
 check(policy.definition().is_empty() and policy.movement_speed()==0 and policy.ability_id().is_empty(), "scene teardown revokes all grants")
 print("RESULT passed=%d failed=%d" % [passed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
