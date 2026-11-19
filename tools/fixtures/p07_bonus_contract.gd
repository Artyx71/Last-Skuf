extends SceneTree
const Progress = preload("res://tests/p07_bonus_progress.gd")
const Story = preload("res://scripts/story/story_state.gd")
const Host = preload("res://tests/p07_bonus_host.gd")
const BeforeStrict = preload("res://tests/p07_bonus_before_strict.gd")
var rows: Array[Dictionary] = []
var profile := ""
var origin: Node
var roundtrip_diagnostic := {}
var strictness_witness := {}

class Owner extends Node:
	var store: RefCounted
	var session: RefCounted
	var pending_replay := false

class EligibilityDouble extends "res://tests/p07_bonus_progress.gd":
	# Only future chapter/scene eligibility is doubled; campaign validation and IO stay real.
	var fixture_ready := true
	var fault := ""
	var crash := ""
	func _prerequisite(id: String) -> bool:
		return fixture_ready and id in IDS
	func _scene_path(id: String) -> String:
		return "res://tests/p07_bonus_host.tscn" if id in IDS else ""
	func _boundary(stage: String) -> bool:
		if stage == crash:
			var marker := FileAccess.open(OS.get_environment("AYAY_BP_BOUNDARY"),FileAccess.WRITE)
			marker.store_string(stage); marker.flush(); marker.close()
			OS.kill(OS.get_process_id())
		return stage != fault

func _initialize() -> void: call_deferred("run")
func check(label: String, ok: bool) -> void:
	rows.append({"check":label,"passed":ok})
	if not ok: push_warning("FAIL BONUS "+label)

func owner_at(directory: String) -> Owner:
	DirAccess.make_dir_recursive_absolute(directory)
	var service := Owner.new(); root.add_child(service)
	service.store = Story.new(); service.store.path = directory.path_join("story_v2.json")
	if FileAccess.file_exists(service.store.path):
		assert(service.store.load_save())
	else: assert(service.store.record("EV_CH01_INTRO"))
	service.session = service.store
	return service

func host() -> Node:
	var actor := Host.new()
	actor.scene_file_path = "res://tests/p07_bonus_host.tscn"
	root.add_child(actor)
	return actor

func bytes_at(path: String) -> PackedByteArray:
	return FileAccess.get_file_as_bytes(path) if FileAccess.file_exists(path) else PackedByteArray()

func put(path: String, text: String) -> void:
	var file := FileAccess.open(path,FileAccess.WRITE)
	assert(file != null); file.store_string(text); file.close()

func mutations() -> void:
	var owner := owner_at(profile.path_join("A"))
	var main_before := bytes_at(owner.store.path)
	var main_state: Dictionary = owner.store.state.duplicate(true)
	var actual := Progress.new(owner)
	check("missing_sidecar_defaultfalse_no_file",actual.state == Progress.fresh() and not FileAccess.file_exists(actual.path))
	for id in Progress.IDS:
		check("production_planned_locked_"+id,not actual.can_launch(id) and not actual.begin(id,host(),origin))
	check("unknown_id_locked",not actual.can_launch("ENDING_REAL_PRIME"))
	var progress := EligibilityDouble.new(owner)
	var actor := host()
	check("fixture_only_positive_session",progress.begin(Progress.IDS[0],actor,origin))
	actor.objective = false
	check("unresolved_goal_no_write",not progress.complete(actor) and not FileAccess.file_exists(progress.path))
	actor.objective = true; actor.alive = false
	check("dead_host_no_write",not progress.complete(actor) and not FileAccess.file_exists(progress.path))
	actor.alive = true; actor.jobs = true
	check("pending_jobs_no_write",not progress.complete(actor) and not FileAccess.file_exists(progress.path))
	actor.jobs = false
	check("first_complete_real_file",progress.complete(actor) and progress.state.history == [Progress.IDS[0]] and FileAccess.file_exists(progress.path))
	var committed := bytes_at(progress.path)
	check("duplicate_callback_same_session_no_write",progress.complete(actor) and committed == bytes_at(progress.path) and progress.state.history.size() == 1)
	progress.fixture_ready = false
	check("prerequisite_before_idempotent",not progress.complete(actor) and committed == bytes_at(progress.path))
	progress.fixture_ready = true
	check("prerequisite_restore_does_not_revive_old_exit",not progress.complete(actor) and committed == bytes_at(progress.path))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	check("forged_host_denied",not progress.complete(host()) and committed == bytes_at(progress.path))
	progress.revoke()
	check("cancel_or_newgame_generation_revoked",not progress.complete(actor) and committed == bytes_at(progress.path))
	check("completed_replay_begin",progress.begin(Progress.IDS[0],actor,origin))
	check("completed_replay_readonly",progress.complete(actor) and committed == bytes_at(progress.path))
	check("return_intent_from_same_host",progress.request_return(actor))
	check("return_retires_completion_authority",not progress.complete(actor))
	check("fixed_bootstrap_return_once",progress.consume_return(origin) and not progress.consume_return(origin))
	check("second_bonus_begin",progress.begin(Progress.IDS[1],actor,origin))
	check("second_unique_complete",progress.complete(actor) and progress.state.history.size() == 2)
	check("main_campaign_bytes_state_and_reward_unchanged",main_before == bytes_at(owner.store.path) and main_state == owner.store.state)
	check("production_still_locked_despite_completed_sidecar",not actual.can_launch(Progress.IDS[0]) and not actual.can_launch(Progress.IDS[1]))
	var restored := EligibilityDouble.new(owner)
	check("actual_file_roundtrip",restored.state == progress.state and restored.writable)
	var file := FileAccess.open(progress.path,FileAccess.READ)
	var raw: Variant = Progress.strict_decode(file.get_as_text())
	roundtrip_diagnostic = {"read_error":file.get_error(),"restored_error":restored.error,"restored_writable":restored.writable,
		"decoded_schema_type":typeof(raw.schema),"memory_schema_type":typeof(progress.state.schema),
		"raw_dictionary_equals_typed":raw == progress.state,"rebuilt_dictionary_equals_typed":restored.state == progress.state}
	file.close()
	check("new_profile_defaultfalse",Progress.new(owner_at(profile.path_join("B"))).state == Progress.fresh())

func isolation() -> void:
	var owner := owner_at(profile.path_join("scopeA"))
	var old_path: String = owner.store.path
	var progress := EligibilityDouble.new(owner)
	var actor := host(); assert(progress.begin(Progress.IDS[0],actor,origin))
	var other := owner_at(profile.path_join("scopeB"))
	owner.store = other.store; owner.session = owner.store
	check("A_to_B_queued_exit_rejected",not progress.complete(actor) and not FileAccess.file_exists(progress.path) and not FileAccess.file_exists(old_path.get_base_dir().path_join("bonus_progress_v1.json")))
	check("B_begin",progress.begin(Progress.IDS[0],actor,origin))
	owner.store = Story.new(); owner.store.path = other.store.path; assert(owner.store.load_save()); owner.session = owner.store
	check("same_profile_store_replacement_rejected",not progress.complete(actor) and not FileAccess.file_exists(progress.path))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	owner.pending_replay = true
	check("pending_replay_denied",not progress.complete(actor))
	owner.pending_replay = false
	check("pending_replay_restore_does_not_revive_exit",not progress.complete(actor))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	owner.session = owner.store.fork_replay()
	check("fork_session_denied",not progress.complete(actor))
	owner.session = owner.store
	check("fork_restore_does_not_revive_exit",not progress.complete(actor))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	owner.store.writable = false
	check("readonly_campaign_denied",not progress.complete(actor))
	owner.store.writable = true
	check("readonly_restore_does_not_revive_exit",not progress.complete(actor))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	var source: Dictionary = owner.store.state.duplicate(true)
	owner.store.state.chapter_complete["CH14_AGENT_SWARM"] = true
	check("forged_campaign_state_denied",not progress.complete(actor))
	owner.store.state = source
	check("valid_state_restore_does_not_revive_exit",not progress.complete(actor))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	put(owner.store.path,"{")
	check("invalid_campaign_disk_denied",not progress.complete(actor))
	put(owner.store.path,JSON.stringify(source))
	check("valid_disk_restore_does_not_revive_exit",not progress.complete(actor))
	assert(progress.begin(Progress.IDS[0],actor,origin))
	owner.store.simulation = true
	check("scenario_never_unlocks",not progress.can_launch(Progress.IDS[0]))
	owner.store.simulation = false
	check("simulation_restore_does_not_revive_exit",not progress.complete(actor))
	check("no_profile_bonus_files_on_denials",not FileAccess.file_exists(progress.path))

func namespace_aliases() -> void:
	for mode in ["main_is_tmp","main_is_final","main_created_after_candidate"]:
		var directory := profile.path_join(mode)
		DirAccess.make_dir_recursive_absolute(directory)
		var service := Owner.new(); root.add_child(service)
		service.store = Story.new(); service.session = service.store
		service.store.path = directory.path_join("bonus_progress_v1.json.tmp" if mode == "main_is_tmp" else "./bonus_progress_v1.json")
		if mode != "main_created_after_candidate": assert(service.store.record("EV_CH01_INTRO"))
		var progress := EligibilityDouble.new(service)
		if mode == "main_created_after_candidate": assert(service.store.record("EV_CH01_INTRO"))
		var before := bytes_at(service.store.path)
		check(mode+"_namespace_rejected_before_launch",not progress.can_launch(Progress.IDS[0]) and not progress.begin(Progress.IDS[0],host(),origin) and progress.error == "UNAVAILABLE")
		check(mode+"_main_bytes_schema_preserved",before == bytes_at(service.store.path) and service.store.validate(Story.read_json(service.store.path)))

func callback_revocation() -> void:
	var owner := owner_at(profile.path_join("callbacksA")); var progress := EligibilityDouble.new(owner)
	var actor := host(); var first_path: String = progress.path
	assert(progress.begin(Progress.IDS[0],actor,origin))
	actor.callback = func(): progress.revoke()
	check("goal_callback_revoke_clean_denial",not progress.complete(actor) and not FileAccess.file_exists(first_path))
	actor.callback = Callable()
	assert(progress.begin(Progress.IDS[0],actor,origin))
	var other := owner_at(profile.path_join("callbacksB"))
	actor.callback = func():
		owner.store = other.store
		owner.session = owner.store
	check("goal_callback_profile_swap_no_commit",not progress.complete(actor) and not FileAccess.file_exists(first_path) and not FileAccess.file_exists(progress.path))
	actor.callback = Callable(); assert(progress.begin(Progress.IDS[0],actor,origin))
	actor.callback = func(): actor.queue_free()
	check("goal_callback_queued_host_clean_denial",not progress.complete(actor) and not FileAccess.file_exists(progress.path))
	var freed := host(); freed.free()
	check("already_freed_host_clean_denial",not progress.complete(freed) and not progress.request_return(freed))
	var nested_host := host(); var nested: Array[bool] = []
	assert(progress.begin(Progress.IDS[0],nested_host,origin))
	nested_host.callback = func(): nested.append(progress.complete(nested_host))
	check("nested_goal_callback_no_recursion_single_commit",progress.complete(nested_host) and nested == [false] and progress.state.history == [Progress.IDS[0]])

func invalid_files() -> void:
	var owner := owner_at(profile.path_join("invalid"))
	var main := bytes_at(owner.store.path)
	var location: String = owner.store.path.get_base_dir().path_join("bonus_progress_v1.json")
	var cases := {"corrupt":"{", "duplicate_root":'{"schema":1,"schema":1,"domain":"bonus_profile","history":[],"completed":{"BONUS_OFFLINE_BUILD":false,"BONUS_COUNTER_LESSON":false}}',
		"duplicate_escaped":'{"schema":1,"\\u0073chema":1,"domain":"bonus_profile","history":[],"completed":{"BONUS_OFFLINE_BUILD":false,"BONUS_COUNTER_LESSON":false}}',
		"trailing_comma":'{"schema":1,"domain":"bonus_profile","history":[],"completed":{"BONUS_OFFLINE_BUILD":false,"BONUS_COUNTER_LESSON":false,}}'}
	for fault in ["newer","partial","extra","nonbool","duplicate_history","unknown_id","contradictory","duplicate_completed"]:
		var data := Progress.fresh()
		match fault:
			"newer": data.schema = 99
			"partial": data.erase("history")
			"extra": data["scene"] = "res://scenes/levels/missed_fight.tscn"
			"nonbool": data.completed[Progress.IDS[0]] = 0
			"duplicate_history": data.history = [Progress.IDS[0],Progress.IDS[0]]; data.completed[Progress.IDS[0]] = true
			"unknown_id": data.history = ["ENDING_REAL_PRIME"]
			"contradictory": data.completed[Progress.IDS[1]] = true
			"duplicate_completed":
				cases[fault] = JSON.stringify(data).replace('"BONUS_OFFLINE_BUILD":false','"BONUS_OFFLINE_BUILD":false,"BONUS_OFFLINE_BUILD":false')
				continue
		cases[fault] = JSON.stringify(data)
	cases["oversize"] = " ".repeat(65537)
	for number in ["01","1.","1.e0","+1","1e"]:
		var malformed := JSON.stringify(Progress.fresh()).replace('"schema":1','"schema":'+number)
		cases["number_"+number] = malformed
		strictness_witness[number] = {"before_50_accepted":BeforeStrict.strict_decode(malformed) != null,
			"current_accepted":Progress.strict_decode(malformed) != null}
	for fault in cases:
		put(location,cases[fault]); var old := bytes_at(location)
		var progress := EligibilityDouble.new(owner)
		check("invalid_preserved_"+fault,not progress.writable and old == bytes_at(location) and not progress.begin(Progress.IDS[0],host(),origin))
		check("invalid_does_not_touch_main_"+fault,main == bytes_at(owner.store.path) and owner.store.validate(owner.store.state))
	check("strict_accepts_escaped_legal_keys",Progress.strict_decode(JSON.stringify(Progress.fresh()).replace('"schema"','"\\u0073chema"')) != null)
	for number in ["1.0","1e0","1E-00"]:
		check("strict_accepts_valid_number_"+number,Progress.strict_decode(JSON.stringify(Progress.fresh()).replace('"schema":1','"schema":'+number)) != null)
	DirAccess.remove_absolute(location)
	put(location+".tmp",JSON.stringify(Progress.fresh()))
	check("orphan_tmp_not_commit",EligibilityDouble.new(owner).state == Progress.fresh() and not FileAccess.file_exists(location))

func failures() -> void:
	var owner := owner_at(profile.path_join("failures")); var progress := EligibilityDouble.new(owner)
	var actor := host(); assert(progress.begin(Progress.IDS[0],actor,origin)); assert(progress.complete(actor))
	assert(progress.begin(Progress.IDS[1],actor,origin)); var old := bytes_at(progress.path); var state_before: Dictionary = progress.state.duplicate(true)
	for boundary in ["written","before_rename"]:
		progress.fault = boundary
		check("injected_"+boundary+"_rollback",not progress.complete(actor) and old == bytes_at(progress.path) and progress.state == state_before and not FileAccess.file_exists(progress.path+".tmp"))
	progress.fault = ""
	var location: String = progress.path
	DirAccess.make_dir_absolute(location+".tmp"); put(location+".tmp/keep","keep")
	check("actual_open_failure_rollback",not progress.complete(actor) and old == bytes_at(location) and progress.state == state_before)
	DirAccess.remove_absolute(location+".tmp/keep"); DirAccess.remove_absolute(location+".tmp")
	check("retry_after_failure_commits_once",progress.complete(actor) and progress.state.history.size() == 2)
	var rename_owner := owner_at(profile.path_join("rename_failure")); var rename_progress := EligibilityDouble.new(rename_owner)
	assert(rename_progress.begin(Progress.IDS[0],actor,origin))
	DirAccess.make_dir_absolute(rename_progress.path); put(rename_progress.path+"/keep","keep")
	check("actual_rename_failure_rollback",not rename_progress.complete(actor) and FileAccess.get_file_as_string(rename_progress.path+"/keep") == "keep" and rename_progress.state == Progress.fresh())

func process_case(mode: String) -> void:
	var owner := owner_at(profile.path_join("crash")); var progress := EligibilityDouble.new(owner); var actor := host()
	if mode == "prepare":
		assert(progress.begin(Progress.IDS[0],actor,origin)); check("prepare_one_committed",progress.complete(actor))
	elif mode in ["before_rename","after_rename"]:
		assert(progress.begin(Progress.IDS[1],actor,origin)); progress.crash = mode; progress.complete(actor)
		check("crash_must_terminate_process",false)
	else:
		var count := 1 if mode == "recover_before" else 2
		check(mode+"_correct_disk_authority",progress.state.history.size() == count)
		var old := bytes_at(progress.path)
		assert(progress.begin(Progress.IDS[0],actor,origin))
		check(mode+"_duplicate_committed_readonly",progress.complete(actor) and old == bytes_at(progress.path))
		check(mode+"_main_save_still_valid",owner.store.validate(Story.read_json(owner.store.path)))

func run() -> void:
	profile = OS.get_environment("AYAY_BP_PROFILE")
	assert(not profile.is_empty() and profile.is_absolute_path())
	origin = load(Progress.BOOTSTRAP).instantiate(); root.add_child(origin); current_scene = origin
	var mode := OS.get_environment("AYAY_BP_MODE")
	if mode == "checks": mutations(); isolation(); namespace_aliases(); callback_revocation(); invalid_files(); failures()
	else: process_case(mode)
	var passed := 0
	for row in rows:
		if row.passed: passed += 1
	var report := {"schema":1,"mode":mode,"checks":rows,"passed":passed,"failed":rows.size()-passed,
		"roundtrip_diagnostic":roundtrip_diagnostic,
		"strictness_witness":strictness_witness,
		"positive_eligibility_is_test_double":true,"real_current_campaign_bonus_launches":0,
		"shipped_bonus_UI_or_levels_tested":false,"new_export_or_audio_tests":false}
	put(OS.get_environment("AYAY_BP_RESULT"),JSON.stringify(report,"  "))
	print("BONUS_CONTRACT ",mode," checks=",rows.size()," failed=",rows.size()-passed)
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed == rows.size() else 1)
