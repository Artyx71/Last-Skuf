extends "res://scripts/core/combat_lab.gd"
## First authored chapter. Combat, contact clock and enemy AI are inherited unchanged.
const Progress = preload("res://scripts/levels/chapter_progress.gd")
var story: Node
var requested_replay := false
var progress: RefCounted
var director: Node
var audio: Node
var ui: CanvasLayer
var camera: Camera2D
var doors: Dictionary = {}
var has_key := false
var phone_seen := false
var checkpoint := "start"
var resume_state := "playing"
var dialogue_kind := ""
var message := ""
var message_time := 0.0
var visited_phone := false
var save_ok := true
var scene_ready := false
var frame_times: Array[float] = []
var resume_lock_ticks := 0

func _ready() -> void:
 config_path = "res://resources/chapters/missed_fight.json"
 story = get_node("/root/StoryState")
 requested_replay = story.pending_replay
 story.begin_chapter("CH01_THE_MISSED_FIGHT")
 progress = Progress.new()
 save_ok = progress.load_progress()
 if requested_replay and save_ok: save_ok = progress.checkpoint("start")
 checkpoint = progress.data.checkpoint
 if checkpoint == "complete": checkpoint = "start"
 super._ready()
 for bounds in config.fixture_bounds:
  _add_wall(Rect2(bounds[0],bounds[1],bounds[2],bounds[3]))
 for child in get_children():
  if child is Label: child.hide()
 var world := Sprite2D.new()
 world.texture = preload("res://assets/art/missed_fight/world.png")
 world.centered = false; world.z_index = -10
 add_child(world)
 for definition in config.signs:
  var sign := _add_label(definition.text_ru, Vector2(definition.at[0],definition.at[1]), 10, Color("d9d3b2"))
  sign.z_index = -1
 for definition in config.doors:
  var rect := Rect2(definition.bounds[0], definition.bounds[1], definition.bounds[2], definition.bounds[3])
  var body := StaticBody2D.new()
  body.position = rect.position; body.collision_layer = 1; body.collision_mask = 2|4
  var shape := CollisionShape2D.new()
  var rectangle := RectangleShape2D.new()
  rectangle.size = rect.size; shape.shape = rectangle; shape.position = rect.size/2
  body.add_child(shape)
  var art := Sprite2D.new()
  art.centered = false; art.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
  body.add_child(art); add_child(body)
  doors[definition.id] = {"body":body,"shape":shape,"art":art,"open":false,"rect":rect}
 camera = Camera2D.new()
 camera.position = player.position
 camera.limit_left = 0; camera.limit_top = 0
 camera.limit_right = int(config.world_size[0]); camera.limit_bottom = int(config.world_size[1])
 camera.position_smoothing_enabled = false
 add_child(camera)
 var interaction := InputEventKey.new()
 interaction.physical_keycode = KEY_F
 if not InputMap.has_action("interact"):
  InputMap.add_action("interact"); InputMap.action_add_event("interact", interaction)
 director = get_node("/root/DialogueDirector")
 director.restore()
 director.active = false
 save_ok = story.resume_progress(progress,director) and save_ok
 director.finished.connect(_dialogue_finished)
 audio = get_node("/root/AudioDirector")
 audio.select_music("res://resources/chapters/missed_fight_music.json")
 ui = preload("res://scripts/ui/mission_ui.gd").new()
 ui.mission = self
 add_child(ui)
 scene_ready = true
 reset_encounter()
 if not save_ok: _notice("Сохранение повреждено. Исходный файл сохранён; прогресс не записывается.")
 if progress.data.checkpoint == "complete":
  state = "complete"
  score = int(progress.data.best_score)
 elif checkpoint == "start" and (requested_replay or not director.seen.get("CH01_INTRO", false)):
  start_dialogue("intro")
 if "--p04-replay" in OS.get_cmdline_user_args():
  call_deferred("_run_evidence")
 elif "--capture-mission" in OS.get_cmdline_user_args():
  call_deferred("_capture_and_quit")
 elif "--p04-smoke" in OS.get_cmdline_user_args():
  call_deferred("_smoke_and_quit")

func _add_wall(bounds: Rect2) -> void:
 var body := StaticBody2D.new()
 body.position = bounds.get_center(); body.collision_layer = 1; body.collision_mask = 2|4
 var shape := CollisionShape2D.new()
 var rectangle := RectangleShape2D.new()
 rectangle.size = bounds.size; shape.shape = rectangle
 body.add_child(shape); add_child(body)

func reset_encounter() -> void:
 super.reset_encounter()
 has_key = checkpoint == "service"
 phone_seen = false
 visited_phone = false
 if checkpoint == "service": player.position = Vector2(config.checkpoint_position[0], config.checkpoint_position[1])
 for id in doors: _set_door(id, id == "service" and has_key)
 last_reset_snapshot = snapshot()
 if scene_ready:
  resume_lock_ticks = 0
  _freeze_actors(false)
  message = ""; message_time = 0.0
  director.active = false; director.set_process(true)
  audio.dialogue_active(false)
  ui.settings_panel.hide(); ui.history_panel.hide()

func _set_door(id: String, opened: bool) -> void:
 var door: Dictionary = doors[id]
 door.open = opened
 door.shape.set_deferred("disabled", opened)
 var texture := AtlasTexture.new()
 texture.atlas = preload("res://assets/art/missed_fight/doors.png")
 var frame := 2 if opened else (1 if has_key or id == "street" else 0)
 texture.region = Rect2(frame*32, 0, 32, 96)
 door.art.texture = texture

func _physics_process(delta: float) -> void:
 if not scene_ready: return
 if resume_lock_ticks > 0:
  resume_lock_ticks -= 1
  if resume_lock_ticks == 0: _freeze_actors(false)
 if Input.is_action_just_pressed("restart") and state in ["playing","dead","complete"]:
  if state == "complete":
   if save_ok and progress.checkpoint("start"):
    story.pending_replay = true; story.begin_chapter("CH01_THE_MISSED_FIGHT")
    checkpoint = "start"; reset_encounter(); start_dialogue("intro")
   else: _notice("Не удалось сохранить повтор. Проверьте доступ к файлу.")
  else: reset_encounter()
 if state == "dead":
  death_timer = maxf(0, death_timer-delta)
  if auto_retry and death_timer <= 0: reset_encounter()
 elif state == "playing":
  elapsed += delta; encounter_ticks += 1
  noise_remaining = maxf(0, noise_remaining-delta)
  message_time = maxf(0, message_time-delta)
  if Input.is_action_just_pressed("interact"): interact()
  var zone := Rect2(config.phone_zone[0],config.phone_zone[1],config.phone_zone[2],config.phone_zone[3])
  if state == "playing" and not phone_seen and zone.has_point(player.position):
   visited_phone = true
   start_dialogue("phone")
  # Resolve music after immediate AI threat events have had time to settle.
  var threat := &"EXPLORE"
  for enemy in enemies:
   if enemy.state in ["pursue","telegraph","recover"]: threat = &"COMBAT"; break
   if enemy.state in ["alert","investigate"]: threat = &"SUSPICION"
  if audio.state != threat and audio.pending_state != threat: audio.request_state(threat)
 if camera:
  camera.position = player.position
 if state == "dead":
  player.modulate = Color("b1bdcb") if get_node("/root/OptionsStore").values.reduced_gore else Color("a66f80")
 queue_redraw()

func player_died() -> void:
 if state != "playing": return
 super.player_died()
 if save_ok and not progress.record_death(): _notice("Не удалось сохранить счётчик смертей.")

func make_noise(point: Vector2) -> void:
 super.make_noise(point)
 audio_event.emit(&"noise", point)

func interact() -> void:
 if state != "playing": return
 var key_point := Vector2(config.key_position[0], config.key_position[1])
 if not has_key and player.position.distance_to(key_point) < 48:
  has_key = true
  _set_door("service", false)
  audio.play_cue(&"ui_accept")
  _notice("КУРТКА НАЙДЕНА · ключ от служебки в кармане")
  return
 for id in doors:
  var door: Dictionary = doors[id]
  if not door.open and player.position.distance_to(door.rect.get_center()) < 80:
   if id == "service" and not has_key:
    _notice(config.interactions_ru.locked); return
   _set_door(id, true)
   audio.play_cue(&"door_open", player.position)
   _notice("СЛУЖЕБКА ОТКРЫТА" if id == "service" else "ВЫХОД ВО ДВОР ОТКРЫТ")
   return
 if _exit_rect().has_point(player.position):
  if not has_key or not phone_seen:
   _notice("Забери куртку и ответь на звонок в служебном коридоре."); return
  start_dialogue("outro")

func _checkpoint_if_crossed() -> void:
 if checkpoint == "start" and doors.service.open and player.position.x > 416:
  if save_ok and progress.checkpoint("service"):
   checkpoint = "service"
   _notice("КОНТРОЛЬНАЯ ТОЧКА · служебный коридор")
  elif save_ok:
   _notice("Контрольная точка не записана. Проверьте доступ к сохранению.")

func _process(delta: float) -> void:
 if not scene_ready: return
 if frame_times.size() < 12000: frame_times.append(delta*1000)
 if state == "playing": _checkpoint_if_crossed()
 director.hold_speed = Input.is_key_pressed(KEY_SHIFT)

func _notice(value: String) -> void:
 message = value; message_time = 3.5

func start_dialogue(kind: String) -> void:
 state = "dialogue"; dialogue_kind = kind
 _freeze_actors(true)
 if not director.start_scene("res://resources/dialogue/missed_fight_"+kind+".json"):
  state = "playing"; _freeze_actors(false); _notice("Не удалось открыть диалог.")

func _dialogue_finished(_id: StringName) -> void:
 if state != "dialogue": return
 if dialogue_kind == "phone": phone_seen = true
 if dialogue_kind == "outro":
  score = 1000 if kills == 0 else 0
  if save_ok and progress.complete(score) and story.complete_ch01(director):
   state = "complete"
   combat.reset(); audio.request_state(&"CLEAR"); audio.play_cue(&"clear")
  else:
   state = "playing"; _notice("Глава не сохранена. Проверьте файл и повторите F у выхода.")
 else: state = "playing"
 if state == "playing":
  # Space advancing a line must not also initiate a melee contact on that physics tick.
  resume_lock_ticks = 2
  _freeze_actors(true)

func objective_text() -> String:
 if state == "complete": return "ГЛАВА ЗАВЕРШЕНА · история сохранена · следующая глава пока недоступна"
 if state == "dialogue" and dialogue_kind == "intro": return config.subtitle_ru
 if not has_key: return "КУРТКА У РАКОВИНЫ · северо-запад · F рядом с крючком"
 if not doors.service.open: return "КЛЮЧ В КАРМАНЕ · служебная дверь на востоке · F"
 if not phone_seen: return "УХОДИ ЧЕРЕЗ СЛУЖЕБКУ · E: бросить мелочь по направлению взгляда"
 return "ДОМОЙ · открой дверь справа, затем к выходу на севере двора · F"

func status_text() -> String:
 if not save_ok: return "СОХРАНЕНИЕ ПОВРЕЖДЕНО · файл сохранён для восстановления · запись отключена"
 if state == "dead": return "ПОГИБ · возврат к контрольной точке за 250 мс · R"
 if message_time > 0: return message
 if state == "paused": return "ПАУЗА · угрозы и время остановлены"
 var nearby := ""
 if not has_key and player.position.distance_to(Vector2(config.key_position[0],config.key_position[1])) < 48: nearby = config.interactions_ru.key
 for id in doors:
  if not doors[id].open and player.position.distance_to(doors[id].rect.get_center()) < 80: nearby = config.interactions_ru[id]
 if _exit_rect().has_point(player.position): nearby = config.interactions_ru.exit
 return nearby if not nearby.is_empty() else "Уход без убийств · %.1fс · отвлечение %.1fс · %s" % [elapsed, player.distract_cooldown, "служебка" if checkpoint == "service" else "туалет"]

func _unhandled_input(event: InputEvent) -> void:
 if not scene_ready: return
 if event is InputEventKey and event.pressed and not event.echo:
  if (event.keycode == KEY_ESCAPE and state == "complete") or (event.keycode == KEY_Q and state == "paused"):
   get_viewport().set_input_as_handled()
   get_tree().change_scene_to_file("res://scenes/bootstrap/bootstrap.tscn")
  elif event.keycode == KEY_O or event.keycode == KEY_ESCAPE:
   if state == "paused":
    state = resume_state; ui.settings_panel.hide(); director.set_process(true)
    _freeze_actors(false)
    audio.request_state(&"EXPLORE"); audio.dialogue_active(state == "dialogue")
   else:
    resume_state = state; state = "paused"; ui.settings_panel.show(); director.set_process(false)
    _freeze_actors(true)
    audio.request_state(&"PAUSE")
   get_viewport().set_input_as_handled()
  elif event.keycode == KEY_H and state == "dialogue": ui.toggle_history()
  elif event.keycode == KEY_K and state == "dialogue" and not ui.history_panel.visible: director.skip_seen()
  elif event.keycode == KEY_SPACE and state == "dialogue" and not ui.history_panel.visible:
   director.advance(); audio.play_cue(&"ui_accept")

func _freeze_actors(frozen: bool) -> void:
 player.process_mode = Node.PROCESS_MODE_DISABLED if frozen else Node.PROCESS_MODE_INHERIT
 combat.process_mode = Node.PROCESS_MODE_DISABLED if frozen else Node.PROCESS_MODE_INHERIT
 player.set_physics_process(not frozen)
 combat.set_physics_process(not frozen)
 for enemy in enemies:
  enemy.process_mode = Node.PROCESS_MODE_DISABLED if frozen else Node.PROCESS_MODE_INHERIT
  enemy.set_physics_process(not frozen)

func _draw() -> void:
 if noise_remaining > 0:
  draw_arc(noise_position, 14+(2.1-noise_remaining)*9, 0, TAU, 24, Color("80cbb4"), 1)

func _exit_tree() -> void:
 if is_instance_valid(director): director.set_process(true); director.active = false
 if is_instance_valid(audio):
  audio.dialogue_active(false)
  audio.select_music("")

func _run_evidence() -> void:
 await preload("res://scripts/qa/mission_replay.gd").new().run(self)

func _smoke_and_quit() -> void:
 await _frames(8)
 var ok: bool = player.actions_ready and audio.ready_assets and doors.size() == 2 and director.active
 print("P04_SMOKE passed=", ok)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(), 0 if ok else 1)
