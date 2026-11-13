extends SceneTree
## Signal evidence only. Uses the real AudioDirector/mixer, never a synthetic test clock.
var actions: Array[Dictionary] = []

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var audio := root.get_node("AudioDirector")
	await create_timer(0.7).timeout
	audio.dialogue_active(false)
	audio.request_state(&"EXPLORE")
	await create_timer(1.8).timeout
	var start_clock: float = audio.clock
	var start_usec := Time.get_ticks_usec()
	var began: bool = audio.begin_capture()
	var schedule := [
		[2.0, "state", "SUSPICION"], [5.0, "state", "COMBAT"],
		[8.0, "state", "CLEAR"], [11.0, "state", "EXPLORE"],
		[14.0, "state", "COMBAT"], [17.0, "state", "PAUSE"],
		[18.0, "state", "COMBAT"], [20.0, "dialogue", true],
		[22.0, "dialogue", false], [23.0, "state", "SUSPICION"],
		[26.0, "state", "CLEAR"]]
	for item in schedule:
		while (Time.get_ticks_usec() - start_usec) / 1000000.0 < float(item[0]):
			await process_frame
		actions.append({"kind": item[1], "value": item[2], "clock": audio.clock,
			"capture_elapsed": (Time.get_ticks_usec() - start_usec) / 1000000.0})
		if item[1] == "state": audio.request_state(StringName(item[2]))
		else: audio.dialogue_active(item[2])
	while (Time.get_ticks_usec() - start_usec) / 1000000.0 < 29.0:
		await process_frame
	var code: int = audio.end_capture(OS.get_environment("AYAY_AUDIO_QA_WAV"))
	var diagnostics: Dictionary = audio.diagnostics()
	var data := {"schema": 1, "capture_began": began, "capture_code": code,
		"capture_start_clock": start_clock, "capture_end_clock": audio.clock,
		"actions": actions, "audio": diagnostics, "perceptual_listening": false}
	var file := FileAccess.open(OS.get_environment("AYAY_AUDIO_QA_JSON"), FileAccess.WRITE)
	file.store_string(JSON.stringify(data, "  "))
	file.close()
	var ok: bool = began and code == OK and diagnostics.mixer_clock and diagnostics.stem_starts == 1 and diagnostics.music_players == 1
	print("AUDIO_QA_CAPTURE ", "PASS" if ok else "FAIL", " driver=", diagnostics.audio_driver)
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 0 if ok else 1)
