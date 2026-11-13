extends Node
## All stems share one AudioStreamSynchronized mixer clock. No gameplay RNG access.
signal state_committed(state: StringName, beat: int)
const MANIFEST_PATH := "res://assets/audio/manifest.json"
const MAX_VOICES := 12
var manifest: Dictionary = {}
var music: AudioStreamPlayer
var synchronized: AudioStreamSynchronized
var voices: Array[AudioStreamPlayer] = []
var spatial_voices: Array[AudioStreamPlayer2D] = []
var state: StringName = &"EXPLORE"
var pending_state: StringName = &""
var pending_beat := -1
var clock := 0.0
var mixer_clock_enabled := true
var previous_music_position := 0.0
var completed_loops := 0
var dialogue_duck := 1.0
var pause_duck := 1.0
var current_gains: Dictionary = {}
var round_robin: Dictionary = {}
var last_cue: Dictionary = {}
var event_log: Array[Dictionary] = []
var stem_starts := 0
var dropped_cues := 0
var ready_assets := false
var shutting_down := false
var capture_effect: AudioEffectRecord
var capture_slot := -1
var beat_seconds := 60.0 / 144.0
var options: Node
var chapter_music_path := ""

func select_music(path: String) -> bool:
 # Only chapter orchestration changes the score. The existing one-player mixer and SFX pool survive.
 if shutting_down or not ready_assets or music == null or synchronized == null: return false
 if path == chapter_music_path: return true
 var source := MANIFEST_PATH if path.is_empty() else path
 if not FileAccess.file_exists(source): return false
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(source))
 if not parsed is Dictionary or parsed.get("schema") != 1: return false
 var definition: Dictionary = parsed.get("music", {})
 var streams: Array[AudioStream] = []
 if definition.get("stems", []).size() != synchronized.stream_count: return false
 for stem in definition.stems:
  if not ResourceLoader.exists(stem.path): return false
  var stream: AudioStream = load(stem.path)
  if stream is AudioStreamOggVorbis: stream.loop = true
  streams.append(stream)
 music.stop()
 manifest.music = definition
 for i in streams.size():
  synchronized.set_sync_stream(i, streams[i])
  synchronized.set_sync_stream_volume(i, -80.0)
 current_gains.clear()
 for stem in definition.stems: current_gains[stem.id] = 0.0
 beat_seconds = 60.0 / float(definition.bpm)
 clock = 0.0; previous_music_position = 0.0; completed_loops = 0
 state = &"EXPLORE"; pending_state = &""; pending_beat = -1
 pause_duck = 1.0; dialogue_duck = 1.0
 chapter_music_path = path
 music.play(); stem_starts += 1
 _log("score_selected", {"id": definition.id, "music_players": 1})
 return true

func _ready() -> void:
 process_mode = Node.PROCESS_MODE_ALWAYS
 options = get_node_or_null("/root/OptionsStore")
 load_assets()

func load_assets() -> bool:
 if shutting_down: return false
 if ready_assets: return true
 if not FileAccess.file_exists(MANIFEST_PATH): return false
 manifest = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST_PATH))
 if manifest.get("schema") != 1: return false
 synchronized = AudioStreamSynchronized.new()
 synchronized.stream_count = manifest.music.stems.size()
 beat_seconds = 60.0 / float(manifest.music.bpm)
 for i in manifest.music.stems.size():
  var stem: Dictionary = manifest.music.stems[i]
  if not ResourceLoader.exists(stem.path): return false
  var stream: AudioStream = load(stem.path)
  if stream is AudioStreamOggVorbis: stream.loop = true
  synchronized.set_sync_stream(i, stream)
  synchronized.set_sync_stream_volume(i, -80.0)
  current_gains[stem.id] = 0.0
 music = AudioStreamPlayer.new()
 music.name = "SynchronizedMusic"
 music.bus = &"Music"
 music.stream = synchronized
 add_child(music)
 for i in MAX_VOICES:
  var voice := AudioStreamPlayer.new()
  voice.max_polyphony = 1
  add_child(voice)
  voices.append(voice)
  var spatial := AudioStreamPlayer2D.new()
  spatial.max_distance = 850
  spatial.attenuation = 0.8
  add_child(spatial)
  spatial_voices.append(spatial)
 ready_assets = true
 music.play()
 stem_starts += 1
 return true

func request_state(next: StringName) -> bool:
 if shutting_down: return false
 if next == &"PAUSE":
  pause_duck = 0.18
  _log("pause", {})
  return true
 if next == &"CUTSCENE":
  dialogue_active(true)
  return true
 if not manifest.get("music", {}).get("profiles", {}).has(String(next)): return false
 pause_duck = 1.0
 if next == state and pending_state.is_empty(): return true
 pending_state = next
 # Danger enters next beat; lower-energy changes wait for a complete bar.
 var quantum := 1 if next == &"COMBAT" else int(manifest.music.beats_per_bar)
 var beat := int(floor(clock / beat_seconds + 0.00001))
 pending_beat = (int(beat / quantum) + 1) * quantum
 _log("request", {"state": String(next), "scheduled_beat": pending_beat})
 return true

func dialogue_active(active: bool) -> void:
 dialogue_duck = 0.32 if active else 1.0
 if not active: stop_speech()
 _log("dialogue", {"active": active})

func _process(delta: float) -> void:
 if not ready_assets: return
 if mixer_clock_enabled:
  var position := music.get_playback_position()
  if position + beat_seconds < previous_music_position: completed_loops += 1
  previous_music_position = position
  clock = completed_loops * float(manifest.music.loop_seconds) + position + AudioServer.get_time_since_last_mix()
 else:
  # Explicit deterministic scheduler unit test hook; actual scenes always use mixer time.
  clock += delta
 var beat := int(floor(clock / beat_seconds + 0.00001))
 if not pending_state.is_empty() and beat >= pending_beat:
  state = pending_state
  pending_state = &""
  _log("commit", {"state": String(state), "beat": pending_beat})
  state_committed.emit(state, pending_beat)
 var profile: Dictionary = manifest.music.profiles[String(state)]
 for i in manifest.music.stems.size():
  var id: String = manifest.music.stems[i].id
  var target := float(profile.get(id, 0.0)) * dialogue_duck * pause_duck
  current_gains[id] = move_toward(float(current_gains[id]), target, delta * 1.9)
  synchronized.set_sync_stream_volume(i, linear_to_db(maxf(float(current_gains[id]), 0.0001)))

func on_gameplay_audio(event_id: StringName, at: Vector2) -> void:
 if shutting_down: return
 match event_id:
  &"footstep_concrete", &"footstep_metal": variant(event_id, at)
  &"state_suspicion": request_state(&"SUSPICION")
  &"state_combat": request_state(&"COMBAT")
  &"state_clear": request_state(&"CLEAR")
  &"retry": reset_for_retry()
  &"death":
   pause_duck = 0.12
   play_cue(&"death", at)
  _: play_cue(event_id, at)

func play_cue(id: StringName, at := Vector2.ZERO) -> bool:
 if not ready_assets or not manifest.sfx.has(String(id)): return false
 var speech := String(id).begins_with("speech_")
 var interval := 0.065 if speech else (0.10 if String(id).begins_with("footstep") else 0.035)
 # Engine monotonic timer keeps throttling independent of render/physics rate and gameplay RNG.
 var now := Time.get_ticks_usec() / 1000000.0
 if now - float(last_cue.get(String(id), -100.0)) < interval:
  dropped_cues += 1
  return false
 var entry: Dictionary = manifest.sfx[String(id)]
 if not ResourceLoader.exists(entry.path): return false
 var bus: StringName = StringName(entry.bus)
 var spatial := bus == &"SFX" and at != Vector2.ZERO
 var pool: Array = spatial_voices if spatial else voices
 var selected: Node = null
 var active := 0
 for voice in voices:
  if voice.playing: active += 1
 for voice in spatial_voices:
  if voice.playing: active += 1
 # Leave playing tails intact; bounded overload drops new sounds instead of cutting waveforms.
 if active >= MAX_VOICES:
  dropped_cues += 1
  return false
 for voice in pool:
  if not voice.playing:
   selected = voice
   break
 if selected == null: return false
 last_cue[String(id)] = now
 selected.stream = load(entry.path)
 selected.bus = bus
 var impact_reduction := 5.0 if options and options.values.reduced_impact and bus == &"SFX" else 0.0
 selected.volume_db = float(entry.get("gain_db", 0.0)) - impact_reduction
 selected.pitch_scale = 1.0
 if spatial: selected.global_position = at
 selected.play()
 _log("cue", {"id": String(id), "spatial": spatial})
 return true

func variant(prefix: StringName, at: Vector2) -> bool:
 var n := int(round_robin.get(String(prefix), 0))
 round_robin[String(prefix)] = n + 1
 return play_cue(StringName(String(prefix) + "_" + str(n % 2 + 1)), at)

func bleep(speaker: StringName) -> void:
 if speaker != &"YAKUZA": return
 variant(&"speech_yakuza", Vector2.ZERO)

func stop_speech() -> void:
 # Let the already playing short two-tone cue finish its authored release (~225ms), never truncate its waveform.
 # No new cues are scheduled once reveal/skip completes. The bounded pool retains these tails.
 pass

func reset_for_retry() -> void:
 pending_state = &""
 pause_duck = 1.0
 dialogue_active(false)
 request_state(&"EXPLORE")
 play_cue(&"retry")
 _log("retry", {"music_players": 1, "stem_starts": stem_starts})

func _log(kind: String, data: Dictionary) -> void:
 var event := data.duplicate()
 event["kind"] = kind
 event["clock"] = snappedf(clock, 0.00001)
 event_log.append(event)
 if event_log.size() > 2048: event_log.pop_front()

func diagnostics() -> Dictionary:
 var active := 0
 for voice in voices:
  if voice.playing: active += 1
 for voice in spatial_voices:
  if voice.playing: active += 1
 return {"assets_ready": ready_assets, "state": String(state), "pending": String(pending_state),
  "pending_beat": pending_beat, "clock": clock, "mixer_clock": mixer_clock_enabled,
  "playback_position": music.get_playback_position() if music else 0.0, "audio_driver": AudioServer.get_driver_name(), "stem_starts": stem_starts, "music_players": 1 if music else 0,
  "active_voices": active, "voice_limit": MAX_VOICES, "dropped_cues": dropped_cues, "music_id": manifest.music.id,
  "gains": current_gains.duplicate(), "events": event_log.duplicate(true)}

func begin_capture() -> bool:
 if capture_effect: return false
 capture_effect = AudioEffectRecord.new()
 capture_effect.format = AudioStreamWAV.FORMAT_16_BITS
 capture_slot = AudioServer.get_bus_effect_count(0)
 AudioServer.add_bus_effect(0, capture_effect)
 capture_effect.set_recording_active(true)
 return true

func end_capture(path: String) -> Error:
 if not capture_effect: return ERR_UNCONFIGURED
 capture_effect.set_recording_active(false)
 var recording := capture_effect.get_recording()
 var result := recording.save_to_wav(path)
 AudioServer.remove_bus_effect(0, capture_slot)
 capture_effect = null
 return result

func shutdown() -> void:
 if shutting_down: return
 shutting_down = true
 ready_assets = false
 set_process(false)
 if music:
  music.stop()
  music.stream = null
 for voice in voices:
  voice.stop()
  voice.stream = null
 for voice in spatial_voices:
  voice.stop()
  voice.stream = null
 if synchronized:
  for i in synchronized.stream_count: synchronized.set_sync_stream(i, null)

func _exit_tree() -> void:
 shutdown()
