extends Node
## Actual Input events through bootstrap, journal and authored CH01. Future data uses tests only.
const Store = preload("res://scripts/story/story_state.gd")
var report := {"schema":1,"actual_input":true,"route_warps":0,"checks":{},"captures":[]}
var tree: SceneTree
var story: Node
var directory := ""
var route: RefCounted
func frames(count: int) -> void:
 for i in count: await tree.physics_frame
func check(id: String, ok: bool) -> void:
 report.checks[id] = ok
 if not ok: push_error("FAIL: P05 input "+id)
func key(code: Key) -> void:
 var event := InputEventKey.new(); event.keycode = code; event.physical_keycode = code; event.pressed = true
 Input.parse_input_event(event); await frames(1)
 event = InputEventKey.new(); event.keycode = code; event.physical_keycode = code
 Input.parse_input_event(event); await frames(2)
func capture(id: String) -> void:
 if directory.is_empty() or DisplayServer.get_name() == "headless": return
 await RenderingServer.frame_post_draw
 var path := directory.path_join(id+".png")
 var error := tree.root.get_texture().get_image().save_png(path)
 report.captures.append({"id":id,"path":path,"error":error})
 check("capture_"+id,error == OK)
func current_mission() -> Node:
 for i in 30:
  await frames(1)
  if tree.current_scene and tree.current_scene.get("scene_ready") == true: return tree.current_scene
 check("mission_scene_ready",false)
 return null
func run(bootstrap: Control) -> void:
 tree = get_tree(); story = tree.root.get_node("StoryState")
 directory = OS.get_environment("AYAY_P05_CAPTURE_DIR")
 await frames(3)
 var resume_only := "--p05-resume" in OS.get_cmdline_user_args()
 await key(KEY_F4)
 check("journal_visible",bootstrap.journal.visible)
 check("journal_21_slots",bootstrap.journal.list.item_count == 21)
 await capture("journal_initial")
 # Keyboard navigation selects a real unavailable slot; Enter must leave the journal open.
 bootstrap.journal.list.grab_focus()
 await key(KEY_DOWN)
 check("planned_slot_disabled",bootstrap.journal.selected == 1 and bootstrap.journal.launch.disabled)
 await key(KEY_ENTER)
 check("unavailable_enter_stays",tree.current_scene == bootstrap and bootstrap.journal.visible)
 await capture("journal_unavailable")
 await key(KEY_ESCAPE)
 check("journal_close_keeps_bootstrap",not bootstrap.journal.visible)
 await key(KEY_ENTER)
 var mission: Node = await current_mission()
 if mission == null: return
 if resume_only:
  check("fresh_process_story_loaded",story.store.status == "LOADED" and story.store.state.completion_rewards == 1)
  check("fresh_process_chapter_complete",mission.state == "complete" and mission.progress.data.completion_events == 1)
 else:
  route = preload("res://scripts/qa/mission_replay.gd").new()
  route.quit_on_finish = false
  await route.run(mission)
  report["p04_input"] = route.report
  check("real_ch01_with_retry",route.report.get("passed",false))
 var canonical := FileAccess.get_file_as_string(story.store.path)
 var readback := Store.new(); readback.path = story.store.path
 check("durable_story_reload",readback.load_save() and readback.state == story.store.state)
 check("one_ch01_reward",readback.state.completion_rewards == 1)
 for id in ["EV_CH01_INTRO","EV_CH01_PHONE","EV_CH01_OUTRO","EV_CH01_SERVICE_ESCAPE"]:
  check("canonical_once_"+id,readback.state.ledger.get(id,false) and readback.state.history.filter(func(row: Dictionary) -> bool: return row.id == id).size() == 1)
 await key(KEY_ESCAPE)
 await frames(3)
 bootstrap = tree.current_scene
 await key(KEY_J)
 check("completed_chapter_label", "пройдена" in bootstrap.journal.list.get_item_text(0))
 check("future_chapter_still_disabled",not story.store.registry.entry_ready(story.store.registry.data.chapters[1].id,story.store.state))
 await capture("journal_complete")
 await key(KEY_ENTER)
 mission = await current_mission()
 check("replay_starts_intro",mission.state == "dialogue" and story.session.replay)
 await key(KEY_K)
 check("seen_intro_skip_safe",mission.state == "playing")
 route = preload("res://scripts/qa/mission_replay.gd").new()
 route.mission = mission
 # Walk the accepted P04 path, retain real collisions and AI.
 for point in [Vector2(80,544),Vector2(80,144),Vector2(96,144)]: check("replay_key_"+str(point),await route.walk(point))
 await route.action("interact")
 for point in [Vector2(80,144),Vector2(80,544),Vector2(336,544)]: check("replay_service_"+str(point),await route.walk(point))
 await route.action("interact")
 check("replay_cross_checkpoint",await route.walk(Vector2(432,544)))
 await key(KEY_O); await key(KEY_Q); await frames(3)
 # Exit/re-enter without resetting progress: real checkpoint resume during a sandbox replay.
 await key(KEY_ENTER)
 mission = await current_mission()
 check("replay_resume_service",mission.checkpoint == "service" and mission.has_key and mission.state == "playing")
 route.mission = mission
 mission.player.set_aim(Vector2.UP)
 await route.action("distract")
 check("replay_middle",await route.walk(Vector2(800,560)))
 if mission.state == "dialogue": await key(KEY_K)
 check("seen_phone_skip_safe",mission.phone_seen and mission.state == "playing")
 check("replay_street",await route.walk(Vector2(944,560)))
 await route.action("interact")
 for point in [Vector2(1056,560),Vector2(1088,560),Vector2(1088,128)]: check("replay_exit_"+str(point),await route.walk(point))
 await route.action("interact")
 await key(KEY_K)
 check("seen_outro_skip_safe",mission.state == "complete")
 check("replay_canonical_bytes_unchanged",FileAccess.get_file_as_string(story.store.path) == canonical)
 check("replay_no_double_rewards",story.store.state.completion_rewards == 1 and mission.progress.data.completion_events == 1)
 await capture("replay_complete")
 report["story"] = readback.state
 report["audio"] = mission.audio.diagnostics()
 report["display"] = DisplayServer.get_name()
 report["rendered"] = DisplayServer.get_name() != "headless"
 report["scope"] = "Headless Input/save technical execution; no rendered/audio-device/native-Windows claim" if not report.rendered else "Actual renderer/Input run; listening and native Windows require separate review"
 report["passed"] = not false in report.checks.values()
 var output := OS.get_environment("AYAY_P05_RESULT_PATH")
 if not output.is_empty(): FileAccess.open(output,FileAccess.WRITE).store_string(JSON.stringify(report,"  "))
 print("P05_INPUT checks=",report.checks.size()," passed=",report.passed," rendered=",report.rendered)
 route = null
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(tree,0 if report.passed else 1)
