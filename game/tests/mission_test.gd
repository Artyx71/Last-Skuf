extends SceneTree
## Negative cases use explicit fixtures; route completion is a separate native-input replay.
const Progress = preload("res://scripts/levels/chapter_progress.gd")
var failures := 0
var checks := 0
var mission: Node

func _initialize() -> void: call_deferred("run")
func expect(value: bool, text: String) -> void:
 checks += 1
 if not value:
  failures += 1
  push_error("FAIL: "+text)
 else: print("PASS: "+text)
func frames(count: int) -> void:
 for i in count: await physics_frame
func press(code: Key) -> void:
 var event := InputEventKey.new()
 event.pressed = true; event.keycode = code; event.physical_keycode = code
 Input.parse_input_event(event)
 await frames(1)
 event = InputEventKey.new(); event.keycode = code; event.physical_keycode = code
 Input.parse_input_event(event)
 await frames(1)
func run() -> void:
 var progress := Progress.new()
 var test_path := progress.path
 expect(progress.load_progress() and progress.data.checkpoint == "start", "new chapter starts before service gate")
 expect(progress.checkpoint("service"), "checkpoint writes atomically")
 var restored := Progress.new()
 expect(restored.load_progress() and restored.data.checkpoint == "service", "checkpoint survives a fresh save object")
 expect(progress.complete(1000) and progress.complete(500), "repeated completion is idempotent")
 restored = Progress.new(); restored.load_progress()
 expect(restored.data.completion_events == 1 and restored.data.best_score == 1000, "completion ledger once, best score never regresses")
 expect(progress.checkpoint("start") and progress.data.completed, "replay preserves canonical completion")
 expect(not progress.checkpoint("unknown"), "unknown checkpoint rejected")
 var original := FileAccess.get_file_as_string(test_path)
 for invalid in ["{", '{"schema":99}', '{"schema":1,"chapter":"CH01_THE_MISSED_FIGHT","checkpoint":"complete","completed":false,"best_score":0,"completion_events":0,"deaths":0}', '{"schema":1,"chapter":"CH01_THE_MISSED_FIGHT","checkpoint":"service","completed":false,"best_score":-1,"completion_events":0,"deaths":0}']:
  var file := FileAccess.open(test_path,FileAccess.WRITE); file.store_string(invalid); file.close()
  var broken := Progress.new()
  expect(not broken.load_progress() and broken.load_status == "INVALID_SAVE" and FileAccess.get_file_as_string(test_path) == invalid, "corrupt save preserved without silent rewrite")
 var file := FileAccess.open(test_path,FileAccess.WRITE); file.store_string(original); file.close()
 progress.path = test_path+"/missing/chapter.json"
 var previous := progress.data.duplicate(true)
 expect(not progress.complete(2000) and progress.data == previous, "write failure does not commit in-memory completion")
 DirAccess.remove_absolute(test_path)
 mission = load("res://scenes/levels/missed_fight.tscn").instantiate()
 root.add_child(mission)
 await frames(3)
 mission.director._finish() # Fixture setup; never counted as playthrough evidence.
 expect(mission.state == "playing" and mission.enemies.size() == 3, "authored chapter uses existing three enemy archetypes")
 mission.auto_retry = false
 mission.player.position = Vector2(336,544)
 await frames(2)
 expect(not mission.combat.clear_line(Vector2(336,537),Vector2(432,537)), "closed service door blocks actual physics ray")
 mission.interact()
 expect(not mission.doors.service.open and not mission.has_key, "locked service door rejects missing key")
 mission.player.position = Vector2(96,144); await frames(1)
 mission.interact()
 expect(mission.has_key and not mission.doors.service.open, "coat gives key without opening distant door")
 mission.player.position = Vector2(336,544); await frames(1)
 mission.interact(); await frames(2)
 expect(mission.doors.service.open and mission.combat.clear_line(Vector2(336,537),Vector2(432,537)), "open door removes actual collision")
 mission.player.position = Vector2(432,544); await frames(3)
 expect(mission.progress.data.checkpoint == "service", "crossed gate persists checkpoint")
 mission.player.set_aim(Vector2.UP)
 Input.action_press("attack_melee"); await frames(1); Input.action_release("attack_melee")
 await press(KEY_O)
 var snap: Dictionary = mission.snapshot()
 await frames(20)
 expect(mission.state == "paused" and mission.snapshot() == snap, "pause freezes action clock, threats and projectiles")
 await press(KEY_O)
 expect(mission.state == "playing" and mission.player.is_physics_processing(), "resume restores actor clock")
 await press(KEY_F2)
 expect(mission.player.kit == "escape" and not mission.player.attack_ranged(), "no training weapons in chapter")
 mission.player.receive_hit(1,0,999,mission.enemies[1]); await frames(2)
 expect(mission.state == "dead", "existing lethal hit lifecycle")
 mission.reset_encounter(); await frames(1)
 expect(mission.player.health == 1 and mission.player.position.distance_to(Vector2(432,544))<3 and mission.has_key and mission.doors.service.open and not mission.doors.street.open and mission.combat.attacks.is_empty() and mission.combat.projectiles.is_empty(), "cached retry restores checkpoint, doors, key and clears combat")
 var before: Dictionary = mission.snapshot()
 root.get_node("OptionsStore").set_value(&"reduced_gore",true,false)
 root.get_node("OptionsStore").set_value(&"vhs",false,false)
 root.get_node("OptionsStore").set_value(&"reduced_motion",true,false)
 expect(before == mission.snapshot(), "visual toggles do not alter combat or mission state")
 mission.state = "dialogue"; mission.dialogue_kind = "outro"
 var valid_path: String = mission.progress.path
 mission.progress.path = valid_path+"/unwritable/chapter.json"
 mission._dialogue_finished(&"CH01_OUTRO")
 expect(mission.state == "playing" and not mission.progress.data.completed, "failed completion save retains playable exit retry")
 mission.progress.path = valid_path
 mission.state = "dialogue"; mission._dialogue_finished(&"CH01_OUTRO")
 expect(mission.state == "complete" and mission.progress.data.completed, "completion commits after durable save")
 mission.queue_free(); await frames(2)
 mission = load("res://scenes/levels/missed_fight.tscn").instantiate()
 root.add_child(mission); await frames(3)
 expect(mission.state == "complete" and mission.progress.data.completion_events == 1, "scene reload reads canonical completion")
 Input.action_press("restart"); await frames(1); Input.action_release("restart"); await frames(2)
 expect(mission.state == "dialogue" and mission.progress.data.completed and mission.progress.data.checkpoint == "start", "chapter replay starts intro without resetting ledger")
 mission.queue_free(); await frames(2)
 print("MISSION_TEST checks=",checks," failures=",failures)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failures == 0 else 1)
