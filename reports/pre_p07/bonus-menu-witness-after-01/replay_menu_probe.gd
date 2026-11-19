extends "res://tests/p07_bonus_live.gd"
## TEST_ONLY future chapter/scene eligibility; real StoryService and Bootstrap only.
func run() -> void:
	profile = OS.get_environment("AYAY_BP_PROFILE")
	assert(profile.is_absolute_path())
	service = root.get_node("StoryState")
	assert(service.store.record("EV_CH01_INTRO"))
	var menu := await bootstrap()
	var canonical: RefCounted = service.store
	var progress := enable_eligibility_double()
	var main_before := bytes_at(canonical.path)
	check("initial_menu_canonical_context",service.session == canonical)
	check("TEST_ONLY_initial_menu_admission",progress.can_launch(Progress.IDS[0]))
	# Explicit read-only replay precondition on the already-admitted CH01 owner API.
	# No CH10/14 completion, production-positive unlock, or chapter playthrough is claimed.
	service.pending_replay = true
	check("existing_CH01_replay_owner_entry",service.begin_chapter("CH01_THE_MISSED_FIGHT"))
	check("actual_session_is_readonly_fork",service.session != canonical and service.session.replay)
	menu = await bootstrap()
	check("real_Bootstrap_return_restores_canonical_menu_session",service.session == canonical and not service.pending_replay)
	check("TEST_ONLY_menu_admission_after_replay",progress.can_launch(Progress.IDS[0]))
	check("main_bytes_preserved",main_before == bytes_at(canonical.path))
	var passed := 0
	for row in rows:
		if row.passed: passed += 1
	put(OS.get_environment("AYAY_BP_RESULT"),JSON.stringify({"schema":1,"scope":"TEST_ONLY_CH01_REPLAY_OWNER_TO_REAL_BOOTSTRAP_CONTEXT","checks":rows,"passed":passed,"failed":rows.size()-passed,"actual_session_is_canonical":service.session == canonical,"actual_session_replay":service.session.replay,"current_scene":menu.scene_file_path,"no_real_CH10_CH14_or_bonus_level_approval":true},"  "))
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed == rows.size() else 1)
