extends "res://tests/p07_second_pilot.gd"
## Software timing observations. frame_post_draw is not display/keyboard latency.
var segment := "setup"
var requests: Array[Dictionary] = []
var draws: Array[Dictionary] = []
var physics: Array[Dictionary] = []
var activity: Array[Dictionary] = []
var contacts: Array[Dictionary] = []
var pending: Dictionary = {}
var death_record: Dictionary = {}
var probe: Node
var current_context := ""
var clip_enabled := false
var clip_frames: Array[Dictionary] = []
var started_usec := 0

class PhysicsProbe extends Node:
	var sample: Callable
	func _ready() -> void: process_physics_priority = 100
	func _physics_process(_delta: float) -> void: sample.call()

func actor_state() -> Dictionary:
	return {"position":[lab.player.global_position.x,lab.player.global_position.y],"draw_position":[lab.player.sprite.global_position.x,lab.player.sprite.global_position.y],"animation":String(lab.player.sprite.animation),"frame":lab.player.sprite.frame,"action":lab.player.action_kind,"action_frame":lab.player.action_frame,"health":lab.player.health,"host_state":lab.state,"context":current_context}

func mark(kind: String, details: Dictionary = {}) -> void:
	activity.append({"usec":Time.get_ticks_usec(),"tick":Engine.get_physics_frames(),"kind":kind,"segment":segment,"context":current_context,"details":details})

func observe_physics() -> void:
	if not is_instance_valid(lab) or not is_instance_valid(lab.player): return
	var now := Time.get_ticks_usec()
	var state := actor_state()
	physics.append({"usec":now,"tick":Engine.get_physics_frames(),"segment":segment,"state":state})
	if pending.is_empty() or pending.has("accepted_usec"): return
	var accepted := false
	if pending.kind=="move": accepted = lab.player.global_position.distance_to(pending.before_position)>0.01
	elif pending.kind=="melee": accepted = lab.player.action_kind=="shove"
	elif pending.kind=="restart": accepted = lab.state=="playing" and lab.player.health>0 and lab.player.velocity.length()>0 and lab.player.position.distance_to(Vector2(lab.config.player_spawn[0],lab.config.player_spawn[1]))>0.01
	if accepted:
		pending["accepted_usec"] = now
		pending["accepted_tick"] = Engine.get_physics_frames()
		pending["accepted_state"] = state
		mark("accepted",{"request":pending.id,"kind":pending.kind})

func post_draw() -> void:
	var now := Time.get_ticks_usec()
	var row := {"usec":now,"draw":Engine.get_frames_drawn(),"tick":Engine.get_physics_frames(),"segment":segment}
	if is_instance_valid(lab) and is_instance_valid(lab.player): row["state"] = actor_state()
	draws.append(row)
	if not pending.is_empty() and pending.has("accepted_usec") and not pending.has("render_usec") and row.has("state"):
		var old: Dictionary = pending.before_state
		var changed: bool = row.state.draw_position!=old.draw_position or row.state.animation!=old.animation or row.state.frame!=old.frame
		if changed:
			pending["render_usec"] = now
			pending["render_draw"] = row.draw
			pending["render_state"] = row.state
			mark("rendered_actor_change",{"request":pending.id})
	if clip_enabled and draws.size()%3==0:
		var path := OS.get_environment("AYAY_P07_SECOND_CAPTURE")+"/clip-%04d.png"%clip_frames.size()
		var error := root.get_texture().get_image().save_png(path)
		clip_frames.append({"usec":now,"path":path,"error":error,"draw":row.draw,"tick":row.tick})

func contact(event: Dictionary) -> void:
	var row := event.duplicate(true)
	row["usec"] = Time.get_ticks_usec()
	row["context"] = current_context
	row["action"] = lab.player.action_kind
	row["action_frame"] = lab.player.action_frame
	row["player_id"] = lab.player.get_instance_id()
	contacts.append(row)
	mark("contact",{"id":event.id,"target":event.target,"lethal":event.lethal})
	if event.target==lab.player.get_instance_id() and event.lethal:
		death_record = row
		mark("death",{"attack_id":event.id,"cue":event.cue,"cause":"actual_AI_melee_contact"})

func attach_probe() -> void:
	probe = PhysicsProbe.new()
	probe.sample = observe_physics
	lab.add_child(probe)
	lab.combat.contact_committed.connect(contact)

func measured_input(kind: String, code: Key) -> Dictionary:
	var record := {"id":requests.size()+1,"kind":kind,"context":current_context,"segment":segment,"input_usec":Time.get_ticks_usec(),"input_tick":Engine.get_physics_frames(),"before_position":lab.player.global_position,"before_state":actor_state()}
	requests.append(record)
	pending = record
	key(code,true)
	if kind=="restart": key(KEY_D,true)
	for tick in 30:
		await frames(1)
		if record.has("render_usec"): break
	if kind=="move": await frames(8)
	key(code,false)
	key(KEY_D,false)
	await frames(2)
	check(current_context+"/"+kind+"/"+str(record.id),record.has("accepted_usec") and record.has("render_usec"))
	if kind=="restart" and not death_record.is_empty(): record["death_usec"] = death_record.usec
	pending = {}
	return record

func settle() -> void:
	release_keys()
	for tick in 120:
		await frames(1)
		if lab.player.action_timer<=0 and lab.player.melee_cooldown<=0: break

func timed_context(context: String) -> void:
	segment = "setup"
	current_context = context
	await create(context)
	attach_probe()
	await frames(45)
	if context=="yakuza":
		segment = "idle_calibration"
		await frames(240)
	segment = "controlled_movement"
	for code in [KEY_D,KEY_S,KEY_A,KEY_W]: await measured_input("move",code)
	segment = "intentional_idle"
	mark("intentional_idle_begin")
	await frames(30)
	mark("intentional_idle_end")
	# Target placement is a contact/latency probe, not an uninterrupted playthrough.
	segment = "attack_probe_setup"
	lab.player.position = Vector2(128,144)
	lab.player.set_aim(Vector2.RIGHT)
	var enemy: CharacterBody2D = lab.enemies[0]
	enemy.position = Vector2(156,144)
	enemy.set_physics_process(true)
	await frames(2)
	segment = "controlled_melee"
	var hits_before := contacts.size()
	var strike := await measured_input("melee",KEY_SPACE)
	await settle()
	check(context+"/actual_outgoing_contact",contacts.size()>hits_before and contacts.back().target==enemy.get_instance_id())
	if contacts.size()>hits_before: strike["contact_usec"] = contacts[hits_before].usec
	for actor in lab.enemies: actor.set_physics_process(false)
	segment = "death_probe_setup"
	lab.reset_encounter()
	lab.player.position = Vector2(128,144)
	enemy.position = Vector2(156,144)
	enemy.spawn_position = enemy.position
	enemy.patrol_end = enemy.position
	enemy.patrol_target = enemy.position
	enemy.set_physics_process(true)
	death_record = {}
	await frames(2)
	segment = "staged_AI_death_wait"
	for tick in 180:
		await frames(1)
		if not death_record.is_empty(): break
	check(context+"/actual_lethal_AI_contact",not death_record.is_empty() and lab.player.health==0 and lab.state=="dead")
	for actor in lab.enemies: actor.set_physics_process(false)
	segment = "controlled_restart"
	await measured_input("restart",KEY_R)
	check(context+"/restart_control_alive",lab.player.health==1 and lab.state=="playing")
	segment = "setup"
	await dispose()

func authored_clip() -> void:
	current_context = "CH01_YAKUZA_CAMERA"
	segment = "authored_setup"
	lab = preload("res://scenes/levels/missed_fight.tscn").instantiate()
	root.add_child(lab)
	current_scene = lab
	await frames(3)
	for enemy in lab.enemies: enemy.set_physics_process(false)
	var replay := preload("res://scripts/qa/mission_replay.gd").new()
	replay.mission = lab
	await replay.finish_dialogue()
	check("authored/real_CH01_loaded",lab.state=="playing" and lab.room_navigation.supported)
	attach_probe()
	segment = "visual_clip_readback"
	clip_enabled = true
	var walked := true
	for point in [Vector2(80,544),Vector2(80,144),Vector2(96,144)]: walked = await drive(point) and walked
	clip_enabled = false
	check("authored/continuous_Input_camera_route",walked and lab.player.health==1 and clip_frames.size()>60)
	await dispose()

func run() -> void:
	native = DisplayServer.get_name()!="headless"
	if not native:
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,2)
		return
	root.set_flag(Window.FLAG_NO_FOCUS,true)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	root.get_node("OptionsStore").set_value(&"shake",0,false)
	RenderingServer.frame_post_draw.connect(post_draw)
	started_usec = Time.get_ticks_usec()
	for context in ["yakuza","gabar_training","olezhka_training","timka_present","timka_prime","ryzhik_training","tega_training","pasha_training"]: await timed_context(context)
	await authored_clip()
	RenderingServer.frame_post_draw.disconnect(post_draw)
	var passed := checks.filter(func(c: Dictionary):return c.passed).size()
	var result := {"schema":1,"scope":"H04_NATIVE_SOFTWARE_OBSERVATIONS_NOT_HARDWARE_OR_CAMPAIGN","started_usec":started_usec,"ended_usec":Time.get_ticks_usec(),"requests":requests,"draws":draws,"physics":physics,"activity":activity,"contacts":contacts,"clip_frames":clip_frames,"checks":checks,"passed":passed,"failed":checks.size()-passed,"hardware":{"CPU":OS.get_processor_name(),"GPU":RenderingServer.get_video_adapter_name(),"backend":DisplayServer.get_name(),"engine":Engine.get_version_info().string,"physics_hz":Engine.physics_ticks_per_second,"max_fps":Engine.max_fps,"viewport":[root.size.x,root.size.y]},"measurement":"accepted is post-actor physics observation; render is first post_draw with changed actor pose/position; not photons or OS key latency","readback_segments_excluded_from_performance":["visual_clip_readback"],"full_Readiness_or_campaign_approval":false}
	var file := FileAccess.open(OS.get_environment("AYAY_P07_SECOND_RESULT"),FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify(result,"  "))
	file.close()
	print("RESULT PACING %d/%d"%[passed,checks.size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed==checks.size() else 1)
