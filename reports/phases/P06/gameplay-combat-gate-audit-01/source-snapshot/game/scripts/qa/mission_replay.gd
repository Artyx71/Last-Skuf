extends RefCounted
## Executes the authored scene through its real input/controller/AI, never warps route actors.
var quit_on_finish := true
var mission: Node
var report := {"schema":1,"actual_input":true,"route_warps":0,"checks":{},"captures":[],"events":[]}
var directory := ""
const MOVEMENT := ["move_right","move_left","move_down","move_up"]

func release_movement() -> void:
 for id in MOVEMENT: Input.action_release(id)

func input_vector() -> Array:
 var value := Input.get_vector("move_left","move_right","move_up","move_down")
 return [value.x,value.y]

func abort_idle(id: String, details: Dictionary) -> void:
 release_movement()
 check(id,false)
 report["abort"] = details
 report["audio"] = mission.audio.diagnostics()
 report["final_snapshot"] = mission.snapshot()
 report["progress"] = mission.progress.data.duplicate(true)
 report["passed"] = false
 report["scope"] = "Aborted: real-input idle precondition failed; no stale death/reset evidence reused"
 report["capture_status"] = "BLOCKED_HEADLESS" if DisplayServer.get_name() == "headless" else "PARTIAL_CAPTURE"
 var audio_path := OS.get_environment("AYAY_P04_AUDIO_PATH")
 if not audio_path.is_empty(): mission.audio.end_capture(audio_path)
 var path := OS.get_environment("AYAY_P04_RESULT_PATH")
 if not path.is_empty(): FileAccess.open(path,FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("P04_REPLAY ",JSON.stringify(report))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(mission.get_tree(),1)

func frames(count: int) -> void:
 for i in count: await mission.get_tree().physics_frame

func action(id: String, count := 1) -> void:
 Input.action_press(id)
 await frames(count)
 Input.action_release(id)
 await frames(2)

func key(code: Key) -> void:
 var event := InputEventKey.new()
 event.keycode = code; event.physical_keycode = code; event.pressed = true
 Input.parse_input_event(event)
 await frames(1)
 event = InputEventKey.new()
 event.keycode = code; event.physical_keycode = code; event.pressed = false
 Input.parse_input_event(event)
 await frames(2)

func check(id: String, value: bool) -> void:
 report.checks[id] = value
 if not value: push_error("P04 replay failed: "+id)

func capture(id: String) -> void:
 if directory.is_empty() or DisplayServer.get_name() == "headless": return
 await RenderingServer.frame_post_draw
 var path := directory.path_join(id+".png")
 var code := mission.get_viewport().get_texture().get_image().save_png(path)
 report.captures.append({"id":id,"path":path,"error":code,"position":[mission.player.position.x,mission.player.position.y],"state":mission.state})
 check("capture_"+id, code == OK)

func finish_dialogue() -> void:
 var attempts := 0
 while mission.state == "dialogue" and attempts < 40:
  await key(KEY_SPACE)
  await frames(12)
  attempts += 1
 check("dialogue_finished_"+mission.dialogue_kind, mission.state != "dialogue")

func walk(target: Vector2) -> bool:
 var count := 0
 while mission.player.position.distance_to(target) > 3.5 and count < 650:
  if mission.state == "dialogue":
   mission.director.reveal()
   await frames(2)
   await capture("phone")
   # Pausing a dialogue must not advance the cutscene or allow actors to move.
   await key(KEY_O)
   var before: Dictionary = mission.snapshot()
   var visible: int = mission.director.visible_count
   await frames(30)
   check("pause_freezes_world_dialogue", before == mission.snapshot() and visible == mission.director.visible_count)
   await capture("options")
   await key(KEY_O)
   await finish_dialogue()
  if mission.state != "playing":
   release_movement()
   return false
  var delta: Vector2 = target-mission.player.position
  for pair in [["move_right",delta.x>2],["move_left",delta.x< -2],["move_down",delta.y>2],["move_up",delta.y< -2]]:
   if pair[1]: Input.action_press(pair[0])
   else: Input.action_release(pair[0])
  await frames(1)
  count += 1
 release_movement()
 await frames(2)
 report.events.append({"walk":[target.x,target.y],"reached":mission.player.position.distance_to(target)<5,"state":mission.state,"ticks":mission.encounter_ticks})
 return mission.player.position.distance_to(target)<5 and mission.state == "playing"

func run(world: Node) -> void:
 mission = world
 directory = OS.get_environment("AYAY_P04_CAPTURE_DIR")
 mission.audio.begin_capture()
 await frames(3)
 mission.director.reveal()
 await capture("intro")
 var intro_snapshot: Dictionary = mission.snapshot()
 await frames(20)
 check("dialogue_freezes_actor_clock", intro_snapshot == mission.snapshot())
 await finish_dialogue()
 check("dialogue_space_does_not_attack", mission.player.melee_cooldown == 0.0 and mission.combat.next_attack_id == 0)
 check("escape_kit_only", mission.player.kit == "escape" and not mission.player.attack_ranged())
 await key(KEY_F2)
 check("training_disabled", mission.player.kit == "escape")
 # Locked gate rejects interaction before the coat/key is found.
 check("start_gate_closed", not mission.doors.service.open)
 for point in [Vector2(80,544),Vector2(80,144),Vector2(96,144)]:
  check("walk_key_"+str(point), await walk(point))
 await action("interact")
 check("coat_key_found", mission.has_key)
 await capture("washroom")
 for point in [Vector2(80,144),Vector2(80,544),Vector2(336,544)]:
  check("walk_service_"+str(point), await walk(point))
 await action("interact")
 check("service_gate_open", mission.doors.service.open)
 check("cross_service", await walk(Vector2(432,544)))
 check("checkpoint_persisted", mission.progress.data.checkpoint == "service")
 await capture("service_checkpoint")
 # The same live AI must kill a stationary player, followed by ten real cached retries.
 var death_rows := []
 report["deaths"] = death_rows
 report["idle_waits"] = []
 var reset_signature := ""
 for cycle in 10:
  release_movement()
  mission.auto_retry = false
  var origin: Vector2 = mission.player.position
  var deaths_before: int = int(mission.progress.data.deaths)
  var idle := {"cycle":cycle,"commanded_input":[0,0],"start_position":[origin.x,origin.y],"start_tick":Engine.get_physics_frames(),"observed_input":input_vector(),"mouse_aim":mission.player.mouse_aim}
  var safety := 0
  while mission.state == "playing" and safety < 600:
   # Observe the completed physics tick, rather than its pre-update signal.
   # Keep the general walk/action cadence intact; only idle observation settles.
   await mission.get_tree().physics_frame
   await mission.get_tree().process_frame
   safety += 1
   idle["observed_input"] = input_vector()
   idle["last_position"] = [mission.player.position.x,mission.player.position.y]
   idle["last_state"] = mission.state
   idle["last_tick"] = Engine.get_physics_frames()
   if not Input.get_vector("move_left","move_right","move_up","move_down").is_zero_approx() or mission.player.position.distance_to(origin) > 1.5:
    report.idle_waits.append(idle)
    abort_idle("idle_input_or_position_"+str(cycle),idle)
    return
   release_movement()
  report.idle_waits.append(idle)
  var died: bool = mission.state == "dead" and mission.player.hits_received > 0 and int(mission.progress.data.deaths) == deaths_before+1
  if not died:
   abort_idle("new_ai_death_required_"+str(cycle),idle)
   return
  if cycle == 0: await capture("death")
  var hit_events: int = mission.combat.damage_events
  release_movement()
  mission.auto_retry = true
  var start := Time.get_ticks_usec()
  while mission.state == "dead" and Time.get_ticks_usec()-start < 2000000: await frames(1)
  release_movement()
  var latency: float = float(Time.get_ticks_usec()-mission.death_started_usec)/1000 if mission.death_started_usec > 0 else mission.restart_latencies_ms.back()
  var reset: Dictionary = mission.last_reset_snapshot
  var signature := JSON.stringify(reset).sha256_text()
  if cycle == 0: reset_signature = signature
  check("deterministic_reset_"+str(cycle), signature == reset_signature)
  death_rows.append({"actual_ai_death":died,"damage_events":hit_events,"latency_ms":latency,"checkpoint":mission.checkpoint,"reset_seed":reset.seed,"reset_kills":reset.kills,"reset_actions":reset.hitboxes,"reset_bullets":reset.bullets})
  check("retry_"+str(cycle), died and mission.state == "playing" and mission.player.health == 1 and latency < 1000 and reset.hitboxes == 0 and reset.bullets == 0 and mission.has_key and mission.doors.service.open and not mission.doors.street.open)
 report["deaths"] = death_rows
 mission.player.set_aim(Vector2.UP)
 await action("distract")
 check("actual_distraction", mission.enemies[1].investigate_remaining > 0)
 await capture("distraction")
 check("middle_route", await walk(Vector2(800,560)))
 if mission.state == "dialogue": await finish_dialogue()
 check("phone_finished", mission.phone_seen)
 check("to_street_gate", await walk(Vector2(944,560)))
 await action("interact")
 check("street_gate_open", mission.doors.street.open)
 for point in [Vector2(1056,560),Vector2(1088,560),Vector2(1088,128)]:
  check("walk_exit_"+str(point), await walk(point))
 await capture("street")
 await action("interact")
 await finish_dialogue()
 check("mission_complete_nonlethal", mission.state == "complete" and mission.kills == 0 and mission.score == 1000 and mission.progress.data.completed and mission.progress.data.completion_events == 1)
 await capture("complete")
 # Fresh object reads the actual on-disk progress, not the authoring object's cache.
 var saved := preload("res://scripts/levels/chapter_progress.gd").new()
 check("disk_completion_roundtrip", saved.load_progress() and saved.data.completed and saved.data.completion_events == 1 and saved.data.best_score == 1000)
 await frames(150)
 report["audio"] = mission.audio.diagnostics()
 report["final_snapshot"] = mission.snapshot()
 report["progress"] = saved.data
 var sorted: Array[float] = mission.frame_times.duplicate()
 sorted.sort()
 report["frame_timings"] = {"samples":sorted.size(),"p50_ms":sorted[int(sorted.size()*.50)],"p95_ms":sorted[int(sorted.size()*.95)],"p99_ms":sorted[int(sorted.size()*.99)],"backend":RenderingServer.get_video_adapter_name(),"display":DisplayServer.get_name(),"movie_maker":not Engine.get_write_movie_path().is_empty()}
 var audio_path := OS.get_environment("AYAY_P04_AUDIO_PATH")
 if not audio_path.is_empty(): check("audio_capture_saved", mission.audio.end_capture(audio_path) == OK)
 var success := true
 for value in report.checks.values(): success = success and value
 report["passed"] = success
 report["scope"] = "Headless real-input simulation; no rendered frames" if DisplayServer.get_name() == "headless" else "Rendered actual engine run"
 report["capture_status"] = "BLOCKED_HEADLESS" if DisplayServer.get_name() == "headless" else "CAPTURED"
 var path := OS.get_environment("AYAY_P04_RESULT_PATH")
 if not path.is_empty():
  var file := FileAccess.open(path,FileAccess.WRITE)
  file.store_string(JSON.stringify(report,"  "))
 print("P04_REPLAY ", JSON.stringify(report))
 if quit_on_finish: preload("res://scripts/core/runtime_shutdown.gd").quit_clean(mission.get_tree(),0 if success else 1)
