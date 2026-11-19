extends "res://tests/p07_bonus_contract.gd"
## Actual autoload/scene/UI adapters. Future chapter eligibility remains an explicit double.
var service: Node
var native := false
var captures: Array[String] = []

func frames(count := 3) -> void:
	for index in count: await process_frame

func tap(code: Key) -> void:
	var event := InputEventKey.new(); event.keycode = code; event.physical_keycode = code; event.pressed = true
	Input.parse_input_event(event); await frames(2)
	event = InputEventKey.new(); event.keycode = code; event.physical_keycode = code; event.pressed = false
	Input.parse_input_event(event); await frames(2)

func click(point: Vector2) -> void:
	var event := InputEventMouseButton.new(); event.button_index = MOUSE_BUTTON_LEFT; event.position = point; event.pressed = true
	Input.parse_input_event(event); await frames(1)
	event = InputEventMouseButton.new(); event.button_index = MOUSE_BUTTON_LEFT; event.position = point; event.pressed = false
	Input.parse_input_event(event); await frames(2)

func capture(name: String) -> void:
	if not native: return
	await RenderingServer.frame_post_draw
	var location := OS.get_environment("AYAY_BP_CAPTURE").path_join(name+".png")
	check("capture_"+name,root.get_texture().get_image().save_png(location) == OK)
	captures.append(location)

func bootstrap() -> Node:
	assert(change_scene_to_file(Progress.BOOTSTRAP) == OK)
	await scene_changed; await frames()
	return current_scene

func enable_eligibility_double() -> RefCounted:
	var progress := EligibilityDouble.new(service)
	service.bonus = progress
	return progress

func start_host() -> Node:
	var menu := await bootstrap()
	assert(service.launch_bonus(Progress.IDS[0],menu))
	await scene_changed; await frames()
	return current_scene

func lifecycle() -> void:
	var progress := enable_eligibility_double()
	var actor := await start_host()
	var main_before := bytes_at(service.store.path)
	service.pending_replay = true; service.pending_replay = false
	check("live_pending_replay_restore_revokes_without_exit_during_transition",not service.complete_bonus(actor))
	check("live_replay_no_main_write",main_before == bytes_at(service.store.path))
	actor = await start_host()
	var canonical: RefCounted = service.store
	service.session = canonical.fork_replay(); service.session = canonical
	check("live_fork_restore_revokes_without_exit_during_transition",not service.complete_bonus(actor))
	actor = await start_host()
	check("same_store_adoption_legal",service.adopt_campaign(canonical))
	check("live_same_profile_epoch_revokes_queued_exit",not service.complete_bonus(actor))
	actor = await start_host()
	var replacement := Story.new(); replacement.path = canonical.path; assert(replacement.load_save())
	service.store = replacement; service.session = replacement
	check("live_direct_store_replacement_revokes",not service.complete_bonus(actor))
	actor = await start_host()
	var other := Story.new(); other.path = profile.path_join("B/story.json")
	DirAccess.make_dir_recursive_absolute(other.path.get_base_dir()); assert(other.record("EV_CH01_INTRO"))
	check("live_profile_adopt",service.adopt_campaign(other))
	check("live_A_to_B_stale_exit_denied",not service.complete_bonus(actor) and not FileAccess.file_exists(other.path.get_base_dir().path_join("bonus_progress_v1.json")))
	check("profile_A_bytes_preserved",main_before == bytes_at(canonical.path))
	assert(service.adopt_campaign(canonical))
	actor = await start_host()
	var pending_actor: Node = actor
	await bootstrap()
	check("live_scene_change_revokes",not service.complete_bonus(pending_actor))
	check("no_bonus_file_from_lifecycle_denials",not FileAccess.file_exists(progress.path))

func journal() -> void:
	origin = await bootstrap()
	await tap(KEY_J)
	check("real_bootstrap_journal_visible",origin.journal.visible)
	check("real_21_main_and_two_bonus_rows",service.store.registry.data.chapters.size() == 21 and origin.journal.list.item_count == 23)
	var main_before := bytes_at(service.store.path)
	for row in [21,22]:
		origin.journal.list.grab_focus()
		origin.journal.list.select(0); origin.journal._select(0)
		await tap(KEY_END)
		if row == 21: await tap(KEY_UP)
		check("keyboard_bonus_selection_"+str(row),origin.journal.selected == row and origin.journal.launch.disabled)
		await tap(KEY_ENTER)
		check("planned_bonus_enter_stays_"+str(row),current_scene == origin and origin.journal.visible)
		var scroll: float = origin.journal.list.get_v_scroll_bar().value
		origin.journal.list.select(0); origin.journal._select(0)
		origin.journal.list.get_v_scroll_bar().value = scroll
		await frames(2)
		var local := Vector2(-1,-1)
		for y in int(origin.journal.list.size.y):
			if origin.journal.list.get_item_at_position(Vector2(16,y),true) == row:
				local = Vector2(16,y); break
		check("mouse_bonus_hit_target_"+str(row),local.x >= 0)
		if local.x >= 0: await click(origin.journal.list.global_position+local)
		check("mouse_bonus_selection_"+str(row),origin.journal.selected == row and origin.journal.launch.disabled)
		if origin.journal.selected == row: await click(origin.journal.launch.get_global_rect().get_center())
		check("planned_bonus_mouse_stays_"+str(row),current_scene == origin and origin.journal.selected == row and origin.journal.launch.disabled)
		check("planned_direct_launch_denied_"+str(row),not service.launch_bonus(Progress.IDS[row-21],origin))
	check("planned_journal_no_sidecar_or_main_change",main_before == bytes_at(service.store.path) and not FileAccess.file_exists(service.store.path.get_base_dir().path_join("bonus_progress_v1.json")))
	await capture("planned_bonus_journal")

func normal_return() -> void:
	enable_eligibility_double()
	var actor := await start_host()
	var before := bytes_at(service.store.path)
	check("actual_packed_test_host_bound",actor.scene_file_path == "res://tests/p07_bonus_host.tscn" and actor.get_script() == Host)
	check("live_host_commit",service.complete_bonus(actor))
	var committed := bytes_at(service.bonus.path)
	check("live_duplicate_once",service.complete_bonus(actor) and committed == bytes_at(service.bonus.path))
	check("live_leave_accepted",service.leave_bonus(actor))
	await scene_changed; await frames()
	check("actual_bootstrap_ready_return_opens_bonus_journal",current_scene.scene_file_path == Progress.BOOTSTRAP and current_scene.journal.visible and current_scene.journal.selected == 21)
	check("actual_return_intent_consumed_once",not service.consume_bonus_return(current_scene))
	check("return_main_unchanged",before == bytes_at(service.store.path))
	await capture("returned_bonus_journal")

func cli_return() -> void:
	# Controlled pending-return precondition; actual Bootstrap._ready/CLI logic is unmodified.
	var progress := enable_eligibility_double()
	progress._return = {"store":service.store,"profile":ProjectSettings.globalize_path(service.store.path).simplify_path(),"generation":progress.generation}
	await bootstrap()
	check("real_CLI_flag_present","--open-mission" in OS.get_cmdline_user_args())
	check("actual_ready_return_precedes_CLI",current_scene.scene_file_path == Progress.BOOTSTRAP and current_scene.journal != null and current_scene.journal.visible)
	check("CLI_return_intent_once",not service.consume_bonus_return(current_scene))
	await capture("CLI_return_precedence")
	assert(change_scene_to_file(Progress.BOOTSTRAP) == OK)
	await scene_changed; await frames(8)
	check("unconsumed_CLI_behavior_restored",current_scene != null and current_scene.scene_file_path == "res://scenes/levels/missed_fight.tscn")

func run() -> void:
	profile = OS.get_environment("AYAY_BP_PROFILE"); assert(profile.is_absolute_path())
	service = root.get_node("StoryState")
	assert(service.store.record("EV_CH01_INTRO"))
	native = DisplayServer.get_name() != "headless"
	var mode := OS.get_environment("AYAY_BP_MODE")
	if mode == "cli": await cli_return()
	else:
		await journal()
		await lifecycle()
		await normal_return()
	var passed := 0
	for row in rows:
		if row.passed: passed += 1
	put(OS.get_environment("AYAY_BP_RESULT"),JSON.stringify({"schema":1,"mode":mode,"checks":rows,"passed":passed,"failed":rows.size()-passed,
		"renderer":DisplayServer.get_name(),"captures":captures,"real_owner_and_UI_adapters":true,
		"positive_future_chapter_scene_eligibility_double":true,"CLI_pending_return_seeded":mode=="cli",
		"actual_new_bonus_levels_or_canonical_CH10_CH14_unlock":false},"  "))
	print("BONUS_LIVE ",mode," checks=",rows.size()," failed=",rows.size()-passed)
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed == rows.size() else 1)
