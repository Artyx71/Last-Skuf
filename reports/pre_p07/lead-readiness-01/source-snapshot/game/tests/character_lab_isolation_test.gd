extends SceneTree
## Actual sandbox lifecycle must preserve an unfinished campaign viewing record.
var checks: Array[Dictionary] = []
var campaign: Node
var before: Dictionary
var output := ""

func _initialize() -> void: call_deferred("run")
func check(name: String, passed: bool) -> void:
	checks.append({"name":name,"passed":passed})
	if not passed: push_error("FAIL P06_LAB_ISOLATION "+name)
func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
func tap(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode=code;event.physical_keycode=code;event.pressed=true
	Input.parse_input_event(event)
	await frames(1)
	event=InputEventKey.new();event.keycode=code;event.physical_keycode=code;event.pressed=false
	Input.parse_input_event(event)
	await frames(1)
func snapshot() -> Dictionary:
	return {"resource":campaign.resource_path,"line":campaign.line_index,"count":campaign.visible_count,"timer":campaign.char_timer,"elapsed":campaign.line_elapsed,"history":campaign.history.duplicate(true),"ledger":campaign.ledger.duplicate(true),"flags":campaign.flags.duplicate(true),"file":FileAccess.get_file_as_bytes(campaign.save_path),"story":JSON.stringify(root.get_node("StoryState").store.state)}
func unchanged() -> bool: return snapshot()==before
func run() -> void:
	output=OS.get_environment("AYAY_P06_COMBAT_ISOLATION_OUTPUT")
	if output.is_empty():
		push_error("AYAY_P06_COMBAT_ISOLATION_OUTPUT required")
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	campaign=root.get_node("DialogueDirector")
	for initially_processing in [true,false]:
		campaign.set_process(initially_processing)
		check("real_unfinished_CH01_starts:"+str(initially_processing),campaign.start_scene("res://resources/dialogue/missed_fight_intro.json"))
		campaign.reveal();campaign.advance()
		before=snapshot()
		var lab:=preload("res://scripts/core/character_lab.gd").new()
		root.add_child(lab);current_scene=lab
		lab.auto_retry=false
		for enemy in lab.enemies: enemy.set_physics_process(false)
		check("campaign_paused_on_entry:"+str(initially_processing),not campaign.is_processing() and campaign.active)
		await tap(KEY_SPACE);await tap(KEY_F);await frames(30)
		check("combat_Input_preserves_CH01_view_and_story:"+str(initially_processing),unchanged())
		await tap(KEY_O);await frames(15)
		check("effects_panel_preserves_CH01_view_and_story:"+str(initially_processing),lab.state=="options" and unchanged())
		await tap(KEY_R)
		check("retry_preserves_CH01_view_and_story:"+str(initially_processing),unchanged())
		check("registered_fixture_reopen_succeeds:"+str(initially_processing),lab.select_fixture("gabar_training"))
		await frames(5)
		check("actor_replacement_preserves_CH01_view_and_story:"+str(initially_processing),unchanged())
		root.remove_child(lab)
		check("exit_restores_only_prior_processing:"+str(initially_processing),campaign.is_processing()==initially_processing and not campaign.has_meta("p06_viewing_session"))
		# Freeze the probe immediately after exit, before ordinary campaign typing resumes.
		campaign.set_process(false)
		check("exit_keeps_same_resource_line_file_and_facts:"+str(initially_processing),unchanged())
		lab.queue_free()
		await frames(1)
	var guard := preload("res://scripts/systems/campaign_view_guard.gd").new()
	var contender := preload("res://scripts/systems/campaign_view_guard.gd").new()
	root.add_child(guard);root.add_child(contender)
	campaign.set_process(true)
	check("first_pause_owner_acquires",guard.acquire(campaign))
	check("second_pause_owner_cannot_steal",not contender.acquire(campaign))
	contender.release()
	check("nonowner_release_keeps_pause_owner",not campaign.is_processing() and campaign.get_meta("p06_viewing_session")==guard.get_instance_id())
	guard.release()
	check("owner_release_restores_prior_processing",campaign.is_processing() and not campaign.has_meta("p06_viewing_session"))
	campaign.set_process(false)
	guard.release()
	check("duplicate_release_does_not_resume_changed_state",not campaign.is_processing())
	check("guard_can_reacquire",guard.acquire(campaign))
	campaign.set_meta("p06_viewing_session",contender.get_instance_id())
	guard.release()
	check("stale_owner_cannot_release_new_owner",not campaign.is_processing() and campaign.get_meta("p06_viewing_session")==contender.get_instance_id())
	campaign.remove_meta("p06_viewing_session")
	guard.queue_free();contender.queue_free()
	var passed:=checks.all(func(item: Dictionary):return item.passed)
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"ACTUAL_COMBAT_SANDBOX_CAMPAIGN_ISOLATION_ONLY","phase_approval":false,"passed":passed,"checks":checks,"resource":campaign.resource_path,"line":campaign.line_index},"  "));file.close()
	print("RESULT P06_LAB_ISOLATION passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
