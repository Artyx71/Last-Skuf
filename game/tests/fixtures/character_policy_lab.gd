extends "res://scripts/core/combat_lab.gd"
## TEST ONLY: exercises production CombatSystem hooks with legacy art.
## Not a production character, likeness sample, scene authority or ability proof.
const Profile = preload("res://scripts/systems/character_combat_profile.gd")
const Catalog = preload("res://scripts/systems/character_catalog.gd")
var registered_policy = preload("res://scripts/systems/character_scene_policy.gd").new()
var test_fixture := {"actor_id":"timka", "context":"athletic_prime", "fixture_id":"unit_prime", "generation":1}
var actor_mode := "policy"
var tuning_scale := 1.0
var resolve_calls := 0
var mutate_on_cancel := false

func current_authority(category: String) -> Dictionary:
 if test_fixture.is_empty(): return {}
 if category not in Catalog.allowed_equipment(test_fixture.get("actor_id",""),test_fixture.get("context","")): return {}
 var result := test_fixture.duplicate(true)
 result["category"] = category
 return result

func _create_player() -> CharacterBody2D:
 if actor_mode == "legacy": return super._create_player()
 if actor_mode == "registered":
  var actor := RegisteredPolicyActor.new()
  actor.policy_actor_id = registered_policy.definition().actor_id
  return actor
 if actor_mode == "resolver_only": return ResolverOnlyActor.new()
 if actor_mode == "cancel_mutates": return CancelMutatesActor.new()
 return PolicyActor.new()

class ResolverOnlyActor:
 extends "res://scripts/actors/combat_player.gd"
 func resolve_finisher(category: String, base: Dictionary) -> Dictionary:
  lab.resolve_calls += 1
  var context: String = lab.test_fixture.get("context", "")
  var id: String = lab.test_fixture.get("actor_id", "")
  var result: Dictionary = preload("res://scripts/systems/character_combat_profile.gd").resolve_finisher(id,context,category,base)
  if not result.is_empty(): result.windup *= lab.tuning_scale
  return result

class PolicyActor:
 extends ResolverOnlyActor
 func can_use_finisher(category: String) -> bool:
  return not lab.current_authority(category).is_empty()
 func finisher_authority(category: String) -> Dictionary:
  return lab.current_authority(category)

class CancelMutatesActor:
 extends PolicyActor
 func cancel_action() -> void:
  super.cancel_action()
  if lab.mutate_on_cancel: lab.test_fixture.context = "peaceful_present"

class RegisteredPolicyActor:
 extends "res://scripts/actors/combat_player.gd"
 # TEST-ONLY body/art; production scene-policy component is exercised unchanged.
 var policy_actor_id := ""
 func can_use_finisher(category: String) -> bool:
  return not lab.registered_policy.finisher_authority(policy_actor_id,category,finisher_category).is_empty()
 func finisher_authority(category: String) -> Dictionary:
  return lab.registered_policy.finisher_authority(policy_actor_id,category,finisher_category)
 func resolve_finisher(category: String, base: Dictionary) -> Dictionary:
  return lab.registered_policy.resolve_finisher(policy_actor_id,category,finisher_category,base)
