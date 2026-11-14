extends SceneTree
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const Director = preload("res://scripts/systems/dialogue_director.gd")
const Session = preload("res://scripts/systems/character_dialogue_session.gd")
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
 if ok: passed += 1; print("PASS ", label)
 else: failed += 1; push_error("FAIL " + label)
func run() -> void:
 await process_frame
 var entries := Catalog.entries()
 check(entries.size() == 10, "exact seven playables and three supporting identities")
 check(Catalog.speaker("ELLANA").actor_id == "ellana" and Catalog.speaker("ELYA").actor_id == "elya", "partners have distinct validated identities")
 check(not Catalog.valid_line("UNKNOWN", "neutral") and not Catalog.valid_line("gabar", "neutral") and not Catalog.valid_line("GABAR", "unknown"), "unknown/case-confused speaker and emotion rejected")
 check(Catalog.valid_context("timka", "peaceful_present") and Catalog.valid_context("timka", "athletic_prime") and not Catalog.valid_context("timka", "campaign") and not Catalog.valid_context("kaban", "training"), "context matrix does not grant supporting or unknown prime context")
 var verifier := Director.new()
 verifier.use_environment_save_path = false
 verifier.save_path = "user://p06_test_schema.json"
 root.add_child(verifier); verifier.set_process(false)
 for id in entries:
  if id == "yakuza": continue
  check(verifier.load_scene("res://resources/dialogue/p06_" + id + ".json") and verifier.data.lines.size() == 5 and verifier.data.exit_actions.is_empty(), "actual authored five-expression scene validates: " + id)
 verifier.queue_free(); await process_frame
 var campaign: Node = root.get_node("DialogueDirector")
 campaign.save_path = "user://p06_test_campaign_viewing.json"
 check(campaign.start_scene("res://resources/dialogue/missed_fight_intro.json"), "campaign entry starts for interrupted viewing isolation")
 campaign.reveal(); campaign.advance()
 var active_path: String = campaign.resource_path
 var active_line: int = campaign.line_index
 var active_count: int = campaign.visible_count
 var persisted := FileAccess.get_file_as_bytes(campaign.save_path)
 var story: Node = root.get_node("StoryState")
 var campaign_facts := JSON.stringify(story.store.state)
 var session := Session.new()
 session.save_path = "user://p06_test_sandbox_viewing.json"
 root.add_child(session)
 check(session.director.save_path != campaign.save_path and not session.director.use_environment_save_path, "sandbox owns separate file and ignores campaign environment override")
 check(not campaign.is_processing() and campaign.active, "campaign typewriter paused with active resource retained")
 check(session.open("gabar"), "sandbox opens available real Gabar presentation")
 session.director.reveal(); session.director.advance(); session.director.reveal()
 for i in 5: await process_frame
 check(FileAccess.get_file_as_bytes(campaign.save_path) == persisted and campaign.resource_path == active_path and campaign.line_index == active_line and campaign.visible_count == active_count, "sandbox typing/autosave leaves interrupted campaign bytes and viewing position unchanged")
 session.pause_view(); session.queue_free(); await process_frame
 check(not campaign.has_meta("p06_viewing_session") and campaign.is_processing(), "exiting sandbox releases only its own campaign pause")
 campaign.set_process(false)
 check(campaign.resource_path == active_path and campaign.line_index == active_line, "campaign resource and position survive sandbox exit")
 var restored := Director.new();restored.use_environment_save_path = false;restored.save_path = campaign.save_path
 root.add_child(restored);restored.set_process(false)
 check(restored.restore() and restored.resource_path == active_path and restored.line_index == active_line, "fresh director restores original interrupted campaign file")
 check((JSON.stringify(story.store.state)) == campaign_facts, "sandbox scene never changes campaign state")
 restored.queue_free()
 print("RESULT passed=%d failed=%d" % [passed, failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 0 if failed == 0 else 1)
