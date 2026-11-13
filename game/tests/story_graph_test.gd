extends SceneTree
## Two exhaustive partitions, NOT a claim of every cross-product of future campaign content.
const Store = preload("res://scripts/story/story_state.gd")
const Registry = preload("res://scripts/story/story_registry.gd")
var registry := Registry.new()
var failures := 0
var checks := 0
var paths := 0
var transitions := 0
var unique := {}
var witnesses := {}
var route_counts := {"ENDING_WIFE_CALLING":0,"ENDING_BROTHERHOOD":0,"ENDING_FAMILY_BUSINESS":0,"ENDING_REAL_PRIME":0}
var secret_events := ["EV_MEMORABILIA_1","EV_MEMORABILIA_2","EV_MEMORABILIA_3","EV_SECRET_SUPPOSITORY_CANNON","EV_SECRET_BROKEN_TOOTH","EV_SECRET_BATHROOM_INCIDENT","EV_SECRET_JACK_REVENGE","EV_SECRET_PRIME_PHOTOS","EV_KIMONO_RECORD"]
func _initialize() -> void: call_deferred("run")
func expect(ok: bool, title: String) -> void:
 checks += 1
 if not ok:
  failures += 1
  if failures < 20: push_error("FAIL: "+title)
func observe(store: RefCounted, initial := false) -> void:
 unique[JSON.stringify(store.state).sha256_text()] = true
 if not initial: transitions += 1
func apply_event(store: RefCounted, id: String) -> void:
 expect(store.record(id),"record_"+id+" "+store.last_error)
 observe(store)
func scenario(choices: Array, evidence_mask: int, secret_mask: int = 0) -> RefCounted:
 var store := Store.new(true,registry)
 store.replay = true # Scenario domain, in-memory only; no campaign file access.
 observe(store,true)
 for chapter in registry.data.chapters:
  expect(registry.entry_ready(chapter.id,store.state,true),"no_softlock_entry")
  for d in registry.decisions.values():
   var index := int(String(d.id).trim_prefix("D"))-1
   if d.chapter == chapter.id and choices[index] != -1:
    var accepted: bool = choices[index] == 1
    expect(store.choose(d.id,accepted),"choice_"+d.id)
    var before: Dictionary = store.state.duplicate(true)
    expect(store.choose(d.id,accepted) and not store.choose(d.id,not accepted) and before == store.state,"once_and_first_choice_"+d.id)
    match d.id:
     "D01": expect(store.state.flags.kimono_truth == accepted and store.state.relationships.yakuza_olezhka == (1 if accepted else -1),"d01_bond")
     "D02": expect(store.state.evidence.pashas_backup == accepted and store.state.flags.pasha_shared_evidence == accepted and store.state.relationships.gabar_pasha == (1 if accepted else -1),"d02_backup_trust")
     "D03": expect(store.state.flags.ryzhik_warned == accepted and store.state.relationships.yakuza_ryzhik == (1 if accepted else -1),"d03_supplier_bond")
     "D04": expect(store.state.evidence.open_source_origin == accepted and store.state.flags.gabar_exonerated == accepted,"d04_history")
     "D05": expect(store.state.evidence.tegas_phone == accepted and not store.state.flags.phone_decoded,"d05_secure_not_decode")
     "D06": expect(store.state.flags.yakuza_accepted_responsibility == accepted,"d06_responsibility")
    observe(store)
  for event in registry.data.events:
   if event.chapter != chapter.id: continue
   var index := secret_events.find(event.id)
   if index >= 0 and (secret_mask & (1 << index)) != 0:
    if event.id == "EV_SECRET_SUPPOSITORY_CANNON" and (secret_mask & 7) != 7:
     var before: Dictionary = store.state.duplicate(true)
     expect(not store.record(event.id) and store.state == before,"dream_requires_three_memorabilia")
    else: apply_event(store,event.id)
  if chapter.presentation == 11 and evidence_mask & 1: apply_event(store,"EV_WITNESS_TRANSFER")
  if chapter.presentation == 14:
   var before: Dictionary = store.state.duplicate(true)
   if evidence_mask & 4 and choices[3] == 1 and choices[4] == 1: apply_event(store,"EV_PHONE_DECODED")
   else:
    if choices[3] != 1 or choices[4] != 1:
     expect(not store.record("EV_PHONE_DECODED") and before == store.state,"decode_evidence_dependency")
  if chapter.presentation == 19 and evidence_mask & 2: apply_event(store,"EV_FOUNDING_RECORDS")
  if chapter.presentation == 20 and evidence_mask & 3 == 3: apply_event(store,"EV_VERIFIED_OPERATIONS")
  expect(store.complete_chapter(chapter.id),"chapter_complete_"+chapter.id)
  var before: Dictionary = store.state.duplicate(true)
  expect(store.complete_chapter(chapter.id) and store.state == before,"once_chapter_reward")
  expect(store.state.endings.unlocked.has("ENDING_WIFE_CALLING"),"canonical_default_always")
  observe(store)
 paths += 1
 return store
func run() -> void:
 # Six choices: absent/refuse/accept; three independent acquisition toggles.
 for code in 729:
  var choices: Array = []
  var number := code
  for i in 6:
   choices.append(number%3-1); number /= 3
  for evidence_mask in 8:
   var store := scenario(choices,evidence_mask)
   var illegal: bool = (evidence_mask & 3 == 3) or ((evidence_mask & 4 != 0) and choices[3] == 1 and choices[4] == 1)
   var expected := ["ENDING_WIFE_CALLING"]
   if choices[0] == 1 and choices[5] == 1 and illegal: expected.append("ENDING_BROTHERHOOD")
   var concealments := int(choices[0] == 0)+int(choices[2] == 0)+int(choices[5] == 0)
   if concealments >= 2 and not illegal and not evidence_mask & 2: expected.append("ENDING_FAMILY_BUSINESS")
   expect(store.eligible() == expected,"exact_primary_gates code=%d evidence=%d" % [code,evidence_mask])
   expect(not store.overlay_eligible(),"partial_no_secret_overlay")
   for route in expected:
    route_counts[route] += 1
    var plan: Dictionary = store.route_plan(route)
    expect(plan.epilogues.size() >= 2 and not plan.content_available and plan.has("evidence_escape") and plan.has("supplier"),"distinct_route_plan")
    var sandbox: RefCounted = store.fork_replay()
    expect(sandbox.finish_story(route) and sandbox.finish_story(route),"primary_commit_once")
    if not witnesses.has(route): witnesses[route] = {"decision_code":code,"evidence_mask":evidence_mask,"history":sandbox.state.history,"plan":plan}
   expect(store.validate(store.state),"transition_state_valid")
 # Secret prerequisites: all 512 subsets, with full positive decisions/evidence.
 for mask in 512:
  var store := scenario([1,1,1,1,1,1],7,mask)
  expect(not store.overlay_eligible(),"overlay_only_post_story")
  if mask == 511:
   var brother: RefCounted = store.fork_replay()
   expect(brother.finish_story("ENDING_BROTHERHOOD") and brother.finish_overlay(),"overlay_follows_brotherhood_too")
   expect(brother.state.endings.completed == ["ENDING_BROTHERHOOD","ENDING_REAL_PRIME"],"brotherhood_classification_preserved")
  expect(store.finish_story("ENDING_WIFE_CALLING"),"secret_primary_first")
  var qualifies: bool = mask == 511
  expect(store.overlay_eligible() == qualifies,"exact_secret_subset_%d" % mask)
  expect(store.finish_overlay() == qualifies,"overlay_commit_gate")
  if qualifies:
   route_counts.ENDING_REAL_PRIME += 1
   witnesses.ENDING_REAL_PRIME = {"secret_mask":mask,"history":store.state.history}
   var before: Dictionary = store.state.duplicate(true)
   expect(store.finish_overlay() and before == store.state,"overlay_once")
   expect(store.state.endings.completed == ["ENDING_WIFE_CALLING","ENDING_REAL_PRIME"],"overlay_does_not_replace_primary")
  expect(store.validate(store.state),"secret_save_validation")
 expect(paths == 6344,"explicit_path_count")
 expect(route_counts.ENDING_BROTHERHOOD > 0 and route_counts.ENDING_FAMILY_BUSINESS > 0 and route_counts.ENDING_REAL_PRIME == 1,"all_routes_reached")
 var output := OS.get_environment("AYAY_STORY_GRAPH_PATH")
 var report := {"schema":1,"scope":"Exhaustive 729 ternary decision combinations x 8 evidence acquisition toggles; separately 512 secret subsets with all positive choices/evidence. Not exhaustive interleavings or all campaign content.","paths":paths,"observed_transitions":transitions,"observed_state_visits":transitions+paths,"unique_observed_states":unique.size(),"checks":checks,"failures":failures,"routes":route_counts,"reproducible_witnesses":witnesses}
 if not output.is_empty(): FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("STORY_GRAPH_TEST paths=",paths," transitions=",transitions," states=",unique.size()," checks=",checks," failures=",failures," routes=",route_counts)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failures else 0)
