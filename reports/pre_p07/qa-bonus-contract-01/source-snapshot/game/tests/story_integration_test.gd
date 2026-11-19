extends SceneTree
## Fault-injection fixtures; real walking/Input evidence lives in story_replay.gd.
var failures := 0
var checks := 0
func _initialize() -> void: call_deferred("run")
func expect(ok: bool, id: String) -> void:
 checks += 1
 if not ok: failures += 1; push_error("FAIL: "+id)
func frames(count: int) -> void:
 for i in count: await physics_frame
func run() -> void:
 var story := root.get_node("StoryState")
 var mission: Node = load("res://scenes/levels/missed_fight.tscn").instantiate()
 root.add_child(mission); await frames(3)
 mission.director._finish()
 expect(story.store.state.ledger.has("EV_CH01_INTRO"),"real_director_signal_commits_intro")
 mission.start_dialogue("phone"); mission.director._finish()
 expect(story.store.state.ledger.has("EV_CH01_PHONE") and mission.phone_seen,"real_phone_fact")
 var healthy_path: String = story.store.path
 var before: Dictionary = story.store.state.duplicate(true)
 story.store.path = healthy_path+"/missing/story.json"
 mission.start_dialogue("outro"); mission.director._finish()
 expect(mission.state == "playing" and mission.progress.data.completed and not story.store.state.chapter_complete.has(story.store.registry.CH01),"story_failure_retains_retry_after_legacy_complete")
 expect(story.store.state == before,"story_failure_no_partial_publish")
 story.store.path = healthy_path
 # A fresh service store must recover from durable P04 completion, no second reward.
 var restored := preload("res://scripts/story/story_state.gd").new()
 restored.path = healthy_path
 expect(restored.load_save(),"reopen_existing_incomplete_story")
 story.store = restored; story.session = restored
 expect(story.resume_progress(mission.progress,mission.director),"reconcile_pending_ch01_completion")
 expect(restored.state.completion_rewards == 1 and restored.state.ledger.has("EV_CH01_OUTRO"),"recovery_imports_finished_outro_before_completion")
 mission.start_dialogue("outro"); mission.director._finish()
 expect(mission.state == "complete" and story.store.state.completion_rewards == 1,"repeat_exit_idempotent")
 var frozen := FileAccess.get_file_as_string(healthy_path)
 mission.queue_free(); await frames(3)
 mission = load("res://scenes/levels/missed_fight.tscn").instantiate(); root.add_child(mission); await frames(3)
 expect(mission.state == "complete" and story.session.replay,"completed_reload_uses_sandbox")
 Input.action_press("restart"); await frames(1); Input.action_release("restart"); await frames(2)
 expect(mission.state == "dialogue" and story.session.replay,"R_keeps_replay_sandbox")
 mission.director.skip_seen()
 expect(mission.state == "playing" and FileAccess.get_file_as_string(healthy_path) == frozen,"seen_skip_cannot_rewrite_canonical")
 mission.queue_free(); await frames(3)
 print("STORY_INTEGRATION_TEST checks=",checks," failures=",failures)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failures else 0)
