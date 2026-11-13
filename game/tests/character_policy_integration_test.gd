extends SceneTree
## Actual production CombatSystem contacts with an explicitly test-only policy actor.
## These headless tests do not establish production scene authorization or art quality.
const TestLab = preload("res://tests/fixtures/character_policy_lab.gd")
var lab: Node2D
var target: CharacterBody2D
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
 if ok: passed += 1; print("PASS ",label)
 else: failed += 1; push_error("FAIL " + label)
func frames(count: int) -> void:
 for i in count:
  await physics_frame
  await process_frame
func fixture() -> void:
 lab.mutate_on_cancel = false
 lab.tuning_scale = 1.0
 lab.test_fixture = {"actor_id":"timka","context":"athletic_prime","fixture_id":"unit_prime","generation":1}
 lab.reset_encounter()
 lab.auto_retry = false
 lab.gallery_mode = true
 lab.player.position = Vector2(250,270)
 lab.player.set_aim(Vector2.RIGHT)
 lab.player.health = 3
 for enemy in lab.enemies:
  enemy.set_physics_process(false)
  enemy.position = Vector2(500,90)
 target = lab.enemies[0]
 target.position = Vector2(280,270)
 target.health = 1
 target.stun_remaining = 2.0
 target.transition("stunned",2.0,true)
 lab.select_equipment(0)
 await frames(2)
func new_lab(mode := "policy") -> void:
 if is_instance_valid(lab):
  lab.queue_free()
  await frames(3)
 lab = TestLab.new()
 lab.actor_mode = mode
 root.add_child(lab)
 await frames(2)
 await fixture()
func run() -> void:
 await new_lab()
 var definitions: String = JSON.stringify(lab.combat.finisher_definitions)
 for loss in ["peaceful_present","unknown","missing_fixture","actor_switch","new_generation","fixture_switch"]:
  await fixture()
  check(lab.player.try_finisher(), "prime policy starts actual job before " + loss)
  await frames(6)
  check(target.health == 1 and lab.combat.damage_events == 0, "no hidden windup damage before " + loss)
  if loss == "missing_fixture": lab.test_fixture = {}
  elif loss == "actor_switch": lab.test_fixture.actor_id = "gabar";lab.test_fixture.context = "training"
  elif loss == "new_generation": lab.test_fixture.generation += 1
  elif loss == "fixture_switch": lab.test_fixture.fixture_id = "different_prime"
  else: lab.test_fixture.context = loss
  await frames(50)
  check(lab.combat.finishers.is_empty() and target.health == 1 and target.hits_received == 0 and lab.kills == 0 and lab.score == 0 and lab.combat.damage_events == 0, "live authority loss cancels old job without hit/kill/score: " + loss)
  if loss in ["peaceful_present","unknown","missing_fixture"]:
   check(not lab.player.try_finisher(), "repeated input cannot restore missing prime authority: " + loss)
  else:
   check(lab.combat.finisher_history[-1].reason == "eligibility_lost", "same permitted category cannot preserve stale fixture: " + loss)
 await fixture()
 lab.resolve_calls = 0
 check(lab.player.try_finisher() and lab.resolve_calls == 1, "one pure resolve per start; authorization separately rechecks")
 var job: Dictionary = lab.combat.finisher_for(lab.player)
 var id: int = job.id
 var stamped: Dictionary = job.definition.duplicate(true)
 check(is_equal_approx(float(stamped.windup),0.48), "prime profile clock stamped into real job")
 lab.tuning_scale = 5.0
 await frames(20)
 check(target.health == 1 and lab.combat.damage_events == 0, "late profile tuning never advances original contact")
 await frames(12)
 check(target.health == 0 and target.hits_received == 1 and lab.kills == 1 and lab.score == 100 and lab.combat.damage_events == 1, "original stamped clock commits exactly once despite late tuning")
 check(lab.player.sprite.animation == &"finish_unarmed_right" and target.sprite.frame == 1, "existing source and target contact poses present on actual physics path")
 for i in 4: lab.combat._apply_hit(target,stamped,id,lab.player)
 check(lab.kills == 1 and lab.score == 100 and lab.combat.damage_events == 1, "duplicate contact callbacks cannot duplicate policy-branch score")
 lab.combat.cancel_finisher(lab.player,"test",true)
 check(lab.score == 100 and lab.kills == 1, "cancel after commit cannot refund or duplicate reward")
 await fixture()
 lab.test_fixture = {"actor_id":"gabar","context":"training","fixture_id":"unit_gabar","generation":2}
 lab.select_equipment(2)
 check(not lab.player.try_finisher(), "actual equipped sharp denied for Gabar")
 lab.select_equipment(1)
 check(lab.player.try_finisher(), "allowed equipped blunt starts Gabar job")
 lab.reset_encounter()
 await frames(60)
 check(lab.combat.finishers.is_empty() and lab.combat.damage_events == 0 and lab.score == 0 and lab.kills == 0, "reset destroys pending policy-branch authority")
 await fixture()
 lab.test_fixture = {"actor_id":"tega","context":"training","fixture_id":"unit_tega","generation":3}
 lab.select_equipment(4)
 lab.training_bench.set_meta("finisher_enabled",false)
 check(not lab.player.try_finisher(), "Tega cannot use environmental art without actual enabled registered prop")
 lab.training_bench.set_meta("finisher_enabled",true)
 check(lab.player.try_finisher(), "Tega allowed environmental policy still requires real prop geometry")
 lab.player.receive_hit(3,0.0,10000,target)
 await frames(35)
 check(lab.combat.finishers.is_empty() and target.health == 1 and lab.score == 0, "death cancels new policy branch before contact")
 var outcomes: Array[Dictionary] = []
 var options: Node = root.get_node("OptionsStore")
 for reduced in [false,true]:
  options.set_value(&"reduced_gore",reduced,false)
  options.set_value(&"decals",not reduced,false)
  options.set_value(&"shake",0 if reduced else 100,false)
  options.set_value(&"flashes",not reduced,false)
  options.set_value(&"vhs",not reduced,false)
  await fixture()
  check(lab.player.try_finisher(), "policy branch starts with reduced="+str(reduced))
  await frames(65)
  outcomes.append({"health":target.health,"hits":target.hits_received,"kills":lab.kills,"score":lab.score,"events":lab.combat.damage_events,"rng":str(lab.rng.state)})
 check(outcomes[0] == outcomes[1] and outcomes[0].score == 100, "policy Full/Reduced/settings preserve actual health/hits/score/RNG")
 check(JSON.stringify(lab.combat.finisher_definitions) == definitions, "all policy integration leaves global Yakuza definitions unchanged")
 await new_lab("legacy")
 check(not lab.player.has_method("resolve_finisher") and lab.player.try_finisher(), "switch back to unchanged Yakuza default factory keeps baseline finisher path")
 await frames(65)
 check(lab.kills == 1 and lab.score == 100, "baseline Yakuza still commits after character policy branch")
 await new_lab("resolver_only")
 check(not lab.player.try_finisher() and lab.combat.finishers.is_empty(), "resolver without mandatory live authorization fails closed")
 await new_lab("cancel_mutates")
 lab.mutate_on_cancel = true
 check(not lab.player.try_finisher() and lab.combat.finishers.is_empty() and target.state == "stunned" and lab.combat.damage_events == 0, "authority changed during cancel refuses without partial reservation")
 print("RESULT passed=%d failed=%d" % [passed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
