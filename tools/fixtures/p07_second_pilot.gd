extends SceneTree
## Real Input/actors/physics; targeted AI setup is separate from walking routes.
const Host = preload("res://tests/p07_second_pilot_host.gd")
var lab: Node2D
var checks: Array[Dictionary] = []
var rows: Array[Dictionary] = []
var native := false
var moving := false
var wall_frames: Array[float] = []
var previous_usec := 0
var route_overlap := false
var route_jumps := false
var maximum_step := 0.0

func _initialize() -> void: call_deferred("run")

func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
		var now := Time.get_ticks_usec()
		if native and moving and previous_usec > 0: wall_frames.append(float(now-previous_usec)/1000.0)
		previous_usec = now

func check(label: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"check":label,"passed":ok,"details":details})
	if not ok: push_warning("FAIL SECOND_PILOT "+label)

func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)

func release_keys() -> void:
	for code in [KEY_W,KEY_A,KEY_S,KEY_D,KEY_ENTER,KEY_F]: key(code,false)

func tap(code: Key) -> void:
	key(code,true)
	await frames(2)
	key(code,false)
	await frames(2)

func foot(body: CharacterBody2D) -> Rect2:
	for child in body.get_children():
		if child is CollisionShape2D and not child.disabled:
			return child.global_transform*Rect2(-child.shape.size/2,child.shape.size)
	assert(false,"Actual rectangle foot required")
	return Rect2()

func overlaps(body: CharacterBody2D) -> bool:
	var rect := foot(body)
	for blocker in lab.room_navigation.router.blockers:
		if rect.intersects(blocker): return true
	return false

func create(context := "yakuza") -> void:
	lab = Host.new()
	lab.context_key = context
	lab.config_path = "res://tests/p07_second_pilot.json"
	root.add_child(lab)
	current_scene = lab
	await frames(3)
	for enemy in lab.enemies: enemy.set_physics_process(false)

func dispose() -> void:
	release_keys()
	moving = false
	lab.queue_free()
	await frames(3)

func drive(goal: Vector2) -> bool:
	var prior: Vector2 = lab.player.position
	var prior_tick := Engine.get_physics_frames()
	moving = true
	for tick in 600:
		var offset: Vector2 = goal-lab.player.position
		if offset.length() <= 2.1:
			release_keys()
			await frames(1)
			moving = false
			return true
		var code: Key = KEY_D if offset.x > 0 else KEY_A
		if absf(offset.y) > absf(offset.x): code = KEY_S if offset.y > 0 else KEY_W
		for other in [KEY_W,KEY_A,KEY_S,KEY_D]: key(other,other==code)
		await frames(1)
		var step := prior.distance_to(lab.player.position)
		maximum_step = maxf(maximum_step,step)
		var physics_ticks := Engine.get_physics_frames()-prior_tick
		route_jumps = route_jumps or step > lab.player.move_speed*physics_ticks/60.0+0.2
		route_overlap = route_overlap or overlaps(lab.player)
		prior = lab.player.position
		prior_tick = Engine.get_physics_frames()
	release_keys()
	moving = false
	return false

func capture(name: String) -> void:
	if not native: return
	await RenderingServer.frame_post_draw
	var result := root.get_texture().get_image().save_png(OS.get_environment("AYAY_P07_SECOND_CAPTURE")+"/"+name+".png")
	check(name+"/capture",result==OK)

func walking_routes() -> void:
	for context in ["yakuza","gabar_training","olezhka_training","timka_present","timka_prime","ryzhik_training","tega_training","pasha_training"]:
		await create(context)
		route_overlap = false
		route_jumps = false
		maximum_step = 0
		var start := Time.get_ticks_usec()
		var identity_ok: bool = lab.player.get_script()==preload("res://scripts/actors/combat_player.gd") if context=="yakuza" else lab.player.actor_id==lab.scene_policy.definition().actor_id
		check(context+"/actual_body_and_art",identity_ok and lab.player.sprite.sprite_frames.get_animation_names().size()>0)
		check(context+"/initial_physical_gates",not lab.doors.north.shape.disabled and not lab.doors.south.shape.disabled and lab.stage=="lever")
		await tap(KEY_ENTER)
		check(context+"/Input_lever",lab.stage=="collect" and lab.doors.south.shape.disabled and not lab.doors.north.shape.disabled)
		var outbound := true
		for point in [Vector2(80,304),Vector2(256,304),Vector2(256,280),Vector2(352,280),Vector2(544,280),Vector2(544,144)]:
			outbound = await drive(point) and outbound
		check(context+"/outbound_real_Input",outbound and lab.player.position.x>500 and lab.completions==0)
		await tap(KEY_ENTER)
		check(context+"/Input_pickup_changes_real_route",lab.stage=="return" and lab.doors.north.shape.disabled and not lab.doors.south.shape.disabled)
		if context in ["yakuza","tega_training"]: await capture(context+"-return")
		var returning := true
		for point in [Vector2(352,144),Vector2(256,144),Vector2(80,144),Vector2(80,80)]: returning = await drive(point) and returning
		await tap(KEY_ENTER)
		await tap(KEY_ENTER)
		check(context+"/exit_once",returning and lab.stage=="complete" and lab.completions==1 and lab.player.health==1)
		check(context+"/continuous_collision_clearance",not route_overlap and not route_jumps,{"maximum_step":maximum_step,"foot":[foot(lab.player).size.x,foot(lab.player).size.y]})
		rows.append({"context":context,"scope":"actual_Input_walk_no_setup_warps_after_spawn","wall_ms":float(Time.get_ticks_usec()-start)/1000.0,"native":native,"stage":lab.stage,"completions":lab.completions})
		await tap(KEY_R)
		for enemy in lab.enemies: enemy.set_physics_process(false)
		check(context+"/Input_retry_resets_objectives_and_gates",lab.stage=="lever" and lab.completions==0 and lab.player.health==1 and not lab.doors.north.shape.disabled and not lab.doors.south.shape.disabled)
		if context in ["gabar_training","ryzhik_training","timka_present"]:
			# Targeted wall probe, deliberately separate from the no-warp route.
			lab.player.position = Vector2(280,224)
			lab.player.set_aim(Vector2.LEFT if context=="timka_present" else Vector2.RIGHT)
			var mask: int = lab.player.collision_mask
			await tap(KEY_F)
			var bad := false
			var used: int = lab.player.ability_uses
			for tick in 50:
				await frames(1)
				bad = bad or overlaps(lab.player)
			check(context+"/own_movement_ability_stopped_by_wall",used==1 and not bad and lab.player.position.x<=296.1 and lab.player.collision_mask==mask,{"x":lab.player.position.x,"ability":lab.player.prepared_ability})
		await dispose()

func follow(enemy: CharacterBody2D, goal: Vector2, ticks: int) -> Dictionary:
	var bad := false
	var jump := false
	var prior := enemy.position
	var prior_tick := Engine.get_physics_frames()
	for tick in ticks:
		await frames(1)
		bad = bad or overlaps(enemy)
		var physics_ticks := Engine.get_physics_frames()-prior_tick
		jump = jump or prior.distance_to(enemy.position)>float(enemy.definition.chase_speed)*physics_ticks/60.0+0.2
		prior = enemy.position
		prior_tick = Engine.get_physics_frames()
		if prior.distance_to(goal)<=4.1: return {"reached":true,"overlap":bad,"jump":jump,"ticks":tick+1}
	return {"reached":false,"overlap":bad,"jump":jump,"ticks":ticks,"position":[enemy.position.x,enemy.position.y]}

func AI_routes() -> void:
	await create()
	lab.player.set_physics_process(false)
	lab.player.position = Vector2(-1024,-1024)
	var kinds := ["rusher"] if native else ["patrol","rusher","shooter"]
	for kind in kinds:
		var enemy: CharacterBody2D = lab.enemies.filter(func(e: CharacterBody2D):return e.kind==kind)[0]
		for other in lab.enemies: other.set_physics_process(false)
		lab.request_doors(false,true)
		await frames(3)
		enemy.position = Vector2(128,280) # Targeted diagnostic setup, not walking proof.
		enemy.transition("patrol")
		enemy.patrol_target = Vector2(544,280)
		enemy.set_physics_process(true)
		await frames(10)
		check(kind+"/cached_detour_created",lab.room_navigation.router.paths.has(enemy.get_instance_id()))
		var replans: int = lab.room_navigation.router.replans
		lab.request_doors(true,false)
		await frames(3)
		for i in 4:
			enemy.patrol_target = Vector2(512+i*8,144)
			await frames(3)
		var goal: Vector2 = enemy.patrol_target
		var result := await follow(enemy,goal,2400)
		check(kind+"/cached_gate_and_moving_goal",result.reached and not result.overlap and not result.jump and lab.room_navigation.router.replans>replans,result)
		rows.append({"kind":kind,"scope":"targeted_cached_gate_moving_goal","result":result,"replans":lab.room_navigation.router.replans-replans})
		enemy.set_physics_process(false)
		# A closing physical door must wait for an actual occupied foot.
		enemy.position = Vector2(312,144)
		lab.request_doors(false,false)
		await frames(3)
		check(kind+"/occupied_gate_waits",lab.doors.north.shape.disabled and enemy.position==Vector2(312,144))
		enemy.position = Vector2(256,144)
		await frames(3)
		check(kind+"/empty_gate_closes",not lab.doors.north.shape.disabled)
	# Same live host with all three archetypes simultaneously; peers retain P06 masks.
	lab.request_doors(true,true)
	await frames(3)
	var reached := {}
	for i in lab.enemies.size():
		var enemy: CharacterBody2D = lab.enemies[i]
		enemy.reset()
		enemy.position = Vector2(96,96+i*32)
		enemy.patrol_target = Vector2(544,280)
		enemy.set_physics_process(true)
		reached[enemy.kind] = false
	var bad := false
	moving = true
	for tick in 2400:
		await frames(1)
		for enemy in lab.enemies:
			bad = bad or overlaps(enemy)
			if enemy.position.distance_to(Vector2(544,280))<=4.1: reached[enemy.kind] = true
		if reached.values().all(func(v: bool):return v): break
	moving = false
	check("three_live_NPC_routes",reached.values().all(func(v: bool):return v) and not bad,{"reached":reached,"wall_overlap":bad})
	for enemy in lab.enemies: enemy.set_physics_process(false)
	# The adapter contract supports translation and fails closed on rotation.
	lab.position = Vector2(32,16)
	lab.room_navigation.refresh()
	check("translated_room_bounds",lab.room_navigation.supported and lab.room_navigation.router.bounds.position==Vector2(32,16))
	lab.rotation = 0.1
	lab.room_navigation.refresh()
	check("rotated_room_rejected",not lab.room_navigation.supported and lab.navigation_velocity(lab.enemies[0],Vector2(512,144),40)==Vector2.ZERO)
	lab.rotation = 0
	lab.position = Vector2.ZERO
	lab.room_navigation.refresh()
	for kind in kinds:
		var enemy: CharacterBody2D = lab.enemies.filter(func(e: CharacterBody2D):return e.kind==kind)[0]
		enemy.reset()
		enemy.position = Vector2(272,280)
		enemy.spawn_position = enemy.position
		enemy.patrol_target = enemy.position
		lab.player.position = enemy.position+Vector2(float(enemy.definition.range)+36,0)
		lab.request_doors(false,false)
		await frames(3)
		enemy.set_physics_process(true)
		await frames(15)
		check(kind+"/LOS_physical_closed",not enemy.sees_player() and enemy.attacks_started==0)
		lab.request_doors(false,true)
		for tick in 90:
			await frames(1)
			if enemy.state=="pursue": break
		check(kind+"/LOS_alert_to_pursue",enemy.state=="pursue" and "alert" in enemy.transitions)
		lab.request_doors(false,false)
		await frames(5)
		check(kind+"/LOS_loss_existing_patrol_policy",enemy.state=="patrol" and not enemy.sees_player() and enemy.attacks_started==0)
		lab.request_doors(false,true)
		for tick in 90:
			await frames(1)
			if enemy.state=="pursue": break
		check(kind+"/LOS_reacquired",enemy.state=="pursue" and enemy.detection_count>=2)
		lab.request_doors(false,false)
		enemy.receive_hit(0,1.0,0,lab.player)
		enemy.hear_noise(enemy.position+Vector2(0,40))
		await frames(3)
		check(kind+"/stun_priority_over_noise",enemy.state=="stunned" and enemy.attacks_started==0)
		for tick in 90:
			await frames(1)
			if enemy.state=="investigate": break
		check(kind+"/deferred_noise_investigation",enemy.state=="investigate" and lab.player.health==1)
		enemy.receive_hit(1,0,0,lab.player)
		enemy.hear_noise(Vector2(128,144))
		await frames(3)
		check(kind+"/death_priority",enemy.state=="dead" and enemy.velocity==Vector2.ZERO and enemy.attacks_started==0)
		enemy.set_physics_process(false)
	await capture("AI-three-routes")
	await dispose()

func run() -> void:
	native = DisplayServer.get_name()!="headless"
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	root.get_node("OptionsStore").set_value(&"shake",0,false)
	await walking_routes()
	await AI_routes()
	wall_frames.sort()
	var timing := {"native":native,"measurement":"monotonic process-frame samples during movement; headless fixed-fps not performance","samples":wall_frames.size(),"hardware_input_latency_or_campaign_FPS_claim":false}
	if not wall_frames.is_empty():
		for quantile in [0.50,0.95,0.99]: timing[str(quantile)] = wall_frames[mini(wall_frames.size()-1,int(ceil(quantile*wall_frames.size()))-1)]
	var passed := checks.filter(func(c: Dictionary):return c.passed).size()
	var completed_routes := rows.filter(func(row: Dictionary):return row.has("context") and row.stage=="complete" and row.completions==1).size()
	var output := {"schema":1,"passed":passed,"failed":checks.size()-passed,"checks":checks,"rows":rows,"wall_frame_ms":timing,"renderer":RenderingServer.get_video_adapter_name() if native else "headless","CPU":OS.get_processor_name(),"completed_Input_routes":completed_routes,"seven_heroes_eight_registered_contexts":completed_routes==8,"AI_targeted_setups_not_playthrough":true,"peer_collision_separation_claim":false,"new_campaign_or_full_Readiness_approval":false}
	var file := FileAccess.open(OS.get_environment("AYAY_P07_SECOND_RESULT"),FileAccess.WRITE)
	assert(file!=null)
	file.store_string(JSON.stringify(output,"  "))
	file.close()
	print("RESULT SECOND_PILOT %d/%d" % [passed,checks.size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed==checks.size() else 1)
