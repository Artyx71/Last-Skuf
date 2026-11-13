extends SceneTree
const Registry = preload("res://scripts/story/story_registry.gd")
var failures := 0
var checks := 0
func expect(value: bool, id: String) -> void:
 checks += 1
 if not value: failures += 1; push_error("FAIL: "+id)
func _initialize() -> void: call_deferred("run")
func run() -> void:
 var r := Registry.new()
 expect(r.errors.is_empty(), "registry_valid "+str(r.errors))
 expect(r.chapters.size() == 21 and r.events.size() == 43, "explicit_registry_count")
 for fault in ["duplicate", "unknown", "cycle", "chronology", "pov", "planned_scene", "condition", "effect"]:
  var source: Dictionary = r.data.duplicate(true)
  match fault:
   "duplicate": source.events.append(source.events[0].duplicate(true))
   "unknown": source.chapters[1].prerequisites = ["UNKNOWN"]
   "cycle": source.chapters[0].prerequisites = [source.chapters[20].event_id]
   "chronology": source.chapters[0].chronology = 99
   "pov": source.chapters[3].chronology = source.chapters[9].chronology; source.chapters[3].period = source.chapters[9].period
   "planned_scene": source.chapters[1].scene = "res://scenes/levels/missed_fight.tscn"
   "condition": source.events[0].condition = {"eq":["flags.unknown",true]}
   "effect": source.decisions[0].accept = {"relationships.yakuza_olezhka":3}
  var invalid := Registry.new(source)
  expect(not invalid.errors.is_empty(), "reject_"+fault)
 var nonlinear: Dictionary = r.data.duplicate(true)
 nonlinear.chapters[1].presentation = 3; nonlinear.chapters[2].presentation = 2
 expect(Registry.new(nonlinear).errors.is_empty(),"presentation_independent_of_chronology")
 expect(not r.meets({"eq":["choices.D01",false]}, {"choices":{}}), "absent_not_refused")
 expect(r.meets({"all":[{"any":[{"eq":["choices.D01",false]}]},{"not":{"eq":["choices.D02",true]}}]}, {"choices":{"D01":false}}), "composed_conditions")
 print("STORY_REGISTRY_TEST checks=",checks," failures=",failures)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failures else 0)
