extends SceneTree
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("_run")
func check(condition: bool, title: String) -> void:
 if condition:
  passed += 1
  print("PASS ", title)
 else:
  failed += 1
  push_error("FAIL " + title)
func frames(n: int) -> void:
 for i in n: await process_frame
func finish() -> void:
 print("RESULT passed=%d failed=%d" % [passed, failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self, 1 if failed else 0)

func _run() -> void:
 await frames(2)
 var audio: Node = root.get_node("AudioDirector")
 audio.mixer_clock_enabled = false
 check(audio.ready_assets, "actual manifest and audio files load")
 check(audio.synchronized.stream_count == 4, "four stems share one synchronized mixer")
 check(audio.stem_starts == 1 and audio.diagnostics().music_players == 1, "music begins once")
 for i in 4:
  var stream: AudioStreamOggVorbis = audio.synchronized.get_sync_stream(i)
  check(stream.loop and absf(stream.get_length() - 13.3333333333) < 0.001, "actual stem loops at 8 bars " + str(i))
 audio.request_state(&"SUSPICION")
 check(audio.pending_beat % 4 == 0, "suspicion scheduled at bar boundary")
 var boundary: int = audio.pending_beat
 audio.clock = boundary * audio.beat_seconds - 0.01
 audio._process(0.005)
 check(audio.state == &"EXPLORE", "state not applied before target beat")
 audio._process(0.006)
 check(audio.state == &"SUSPICION", "state commits at target bar")
 audio.request_state(&"COMBAT")
 boundary = audio.pending_beat
 check(boundary > int(audio.clock / audio.beat_seconds), "combat scheduled on next beat")
 audio.clock = boundary * audio.beat_seconds
 audio._process(0.001)
 check(audio.state == &"COMBAT", "combat commits without restarting stems")
 audio._process(1.0)
 check(audio.current_gains.drums > 0.99, "combat actual layer gain rises")
 audio.dialogue_active(true)
 audio._process(1.0)
 check(absf(audio.current_gains.drums - 0.32) < 0.01, "dialogue ducks actual layer gain")
 audio.dialogue_active(false)
 audio.request_state(&"PAUSE")
 audio._process(1.0)
 check(absf(audio.current_gains.drums - 0.18) < 0.01, "pause lowers actual music gain")
 audio.request_state(&"COMBAT")
 audio._process(1.0)
 check(audio.pause_duck == 1.0, "resume returns pause gain")
 check(not audio.request_state(&"INVALID"), "invalid state rejected")
 check(audio.play_cue(&"weapon_fire", Vector2(100, 100)), "real spatial weapon event plays")
 check(not audio.play_cue(&"weapon_fire", Vector2(100, 100)), "rapid repeated weapon cue throttled")
 check(audio.diagnostics().active_voices <= audio.MAX_VOICES, "bounded polyphony")
 var options: Node = root.get_node("OptionsStore")
 options.set_value(&"reduced_impact", true, false)
 check(audio.play_cue(&"impact_body", Vector2(110, 110)), "reduced-impact SFX still audible")
 var reduction_seen := false
 for voice in audio.spatial_voices:
  if voice.playing and voice.stream.resource_path == audio.manifest.sfx.impact_body.path:
   reduction_seen = is_equal_approx(voice.volume_db, float(audio.manifest.sfx.impact_body.gain_db) - 5.0)
 check(reduction_seen, "reduced impact lowers actual voice gain by 5 dB")
 # Mechanic/RNG noninterference measured on actual gameplay objects and signal emissions.
 var lab: Node2D = load("res://scenes/world/combat_lab.tscn").instantiate()
 root.add_child(lab)
 await physics_frame
 lab.set_physics_process(false)
 lab.player.set_physics_process(false)
 for enemy in lab.enemies: enemy.set_physics_process(false)
 lab.reset_encounter()
 var before: Dictionary = lab.snapshot()
 for id in [&"footstep_concrete_1", &"footstep_concrete_2", &"footstep_metal_1", &"footstep_metal_2", &"weapon_melee", &"impact_wall"]:
  lab.audio_event.emit(id, Vector2(120, 120))
  audio.variant(&"speech_yakuza", Vector2.ZERO)
 check(lab.snapshot() == before, "typed audio events preserve complete combat snapshot and RNG")
 var starts: int = audio.stem_starts
 for cycle in 10:
  lab.player.receive_hit(1, 0, cycle, lab.enemies[0])
  check(lab.state == "dead", "real lethal damage audio lifecycle " + str(cycle))
  lab.reset_encounter()
  check(audio.stem_starts == starts and audio.diagnostics().music_players == 1, "retry never stacks/restarts music " + str(cycle))
 check(lab.total_deaths == 10, "all ten real deaths exercised")
 check(audio.diagnostics().active_voices <= audio.MAX_VOICES, "death/retry storm stays within polyphony")
 lab.queue_free()
 await frames(2)
 await finish()
