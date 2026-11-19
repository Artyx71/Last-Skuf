extends "res://tests/p07_bonus_contract.gd"
## TEST_ONLY disposable profiles. Old-code bug witness, not mission/readiness acceptance.
func run() -> void:
	profile = OS.get_environment("AYAY_BP_PROFILE")
	assert(profile.is_absolute_path() and not profile.is_empty())
	origin = load(Progress.BOOTSTRAP).instantiate()
	root.add_child(origin)
	current_scene = origin
	var evidence: Array[Dictionary] = []
	for mode in ["main_is_sidecar_tmp", "main_created_after_candidate_at_sidecar"]:
		var directory := profile.path_join(mode)
		DirAccess.make_dir_recursive_absolute(directory)
		var service := Owner.new()
		root.add_child(service)
		service.store = Story.new()
		var filename := "bonus_progress_v1.json.tmp" if mode=="main_is_sidecar_tmp" else "bonus_progress_v1.json"
		service.store.path = directory.path_join(filename)
		service.session = service.store
		if mode=="main_is_sidecar_tmp": assert(service.store.record("EV_CH01_INTRO"))
		var progress := EligibilityDouble.new(service)
		if mode=="main_created_after_candidate_at_sidecar": assert(service.store.record("EV_CH01_INTRO"))
		var before := bytes_at(service.store.path)
		assert(before.size()>0 and service.store.validate(Story.read_json(service.store.path)))
		var actor := host()
		var began := progress.begin(Progress.IDS[0],actor,origin)
		var committed: bool = progress.complete(actor) if began else false
		var after := bytes_at(service.store.path)
		evidence.append({"case":mode,"main_path":service.store.path,"sidecar_path":progress.path,"began":began,"committed":committed,"main_exists_after":FileAccess.file_exists(service.store.path),"main_bytes_preserved":before==after,"main_valid_after":FileAccess.file_exists(service.store.path) and service.store.validate(Story.read_json(service.store.path)),"main_before_utf8":before.get_string_from_utf8(),"main_after_utf8":after.get_string_from_utf8(),"sidecar_after_utf8":bytes_at(progress.path).get_string_from_utf8()})
	var output := {"scope":"TEST_ONLY_OLD_NAMESPACE_ALIAS_WITNESS_NOT_BP_PASS","rows":evidence,"new_production_unlock_or_runtime_approval":false}
	put(OS.get_environment("AYAY_BP_RESULT"),JSON.stringify(output,"  "))
	print("NAMESPACE_ALIAS_WITNESS ",JSON.stringify(output))
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0)
