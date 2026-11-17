extends "res://tests/gabar_combat_replay.gd"
## Real registered present controller and Input; no prime power or test-body fallback.

func check(name: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_TIMKA_PRESENT "+name)

func run() -> void:
	output = OS.get_environment("AYAY_P06_TIMKA_PRESENT_OUTPUT")
	headless = DisplayServer.get_name()=="headless"
	if output.is_empty():
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	lab = Lab.new()
	root.add_child(lab)
	current_scene = lab
	await frames(2)
	await tap(KEY_3)
	check("registered_present_Input_selection",lab.player.actor_id=="timka" and lab.scene_policy.definition().context=="peaceful_present")
	if lab.player.actor_id != "timka":
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	lab.auto_retry = false
	lab.combat.contact_committed.connect(on_contact)
	var clips: SpriteFrames = lab.player.sprite.sprite_frames
	check("own_required_32_clips_speed84",clips.get_animation_names().size()==32 and lab.player.move_speed==84)
	var forbidden_absent := true
	for name in clips.get_animation_names():
		if String(name).begins_with("finish_") or String(name).begins_with("special_") or String(name).begins_with("fire_"): forbidden_absent=false
	check("no_prime_finisher_or_fire_clips_loaded",forbidden_absent)
	for category in ["unarmed","blunt","sharp","firearm","environmental"]:
		check("present_finisher_denied_"+category,not lab.player.can_use_finisher(category))
	for index in 5: check("present_equipment_denied_"+str(index),not lab.select_equipment(index))
	check("present_no_ranged_attack",not lab.player.attack_ranged())
	var all_sockets := true
	for name in clips.get_animation_names():
		for f in clips.get_frame_count(name):
			var texture := clips.get_frame_texture(name,f)
			all_sockets = all_sockets and texture.get_meta("character_id","")=="timka" and texture.has_meta("clothing_socket")
	check("every_required_frame_has_bound_own_clothing_socket",all_sockets)
	trace_enabled = true
	for di in 4:
		segment = "disengage_"+NAMES[di]
		var target := await fixture(DIRECTIONS[di],3,false)
		if di==0:
			# Explicit initial placement below the arena divider, before the
			# measured Input path. The separate wall case keeps its collider.
			lab.player.position.y+=12
			target.position.y+=12
			await frames(2)
		var start: Vector2 = lab.player.position
		var offset := trace.size()
		await tap(KEY_F)
		check("Input_begins_guard_"+NAMES[di],lab.player.action_kind=="disengage" and lab.player.action_frame==0 and lab.combat.attacks.is_empty())
		await capture(segment+"_guard")
		for f in range(1,6):
			var budget := 40
			while lab.player.action_kind=="disengage" and lab.player.action_frame<f and budget>0:
				await frames(1)
				budget-=1
			await capture(segment+"_phase"+str(f))
		await frames(15)
		var expected: Vector2 = start-DIRECTIONS[di]*33.6
		check("bounded_real_backward_motion_"+NAMES[di],lab.player.position.distance_to(expected)<0.03 and absf(lab.player.ability_distance-33.6)<0.03,{"start":[start.x,start.y],"end":[lab.player.position.x,lab.player.position.y],"distance":lab.player.ability_distance})
		var seen: Array = []
		var continuous := true
		for i in range(offset,trace.size()):
			var item: Dictionary = trace[i]
			if item.action_kind=="disengage" and item.action_frame not in seen: seen.append(item.action_frame)
			if i>offset:
				var prev: Dictionary=trace[i-1]
				continuous = continuous and Vector2(item.position[0],item.position[1]).distance_to(Vector2(prev.position[0],prev.position[1]))<=140.0*float(item.tick-prev.tick)/60.0+0.01
		check("all_six_authored_references_displayed_"+NAMES[di],seen==[0,1,2,3,4,5],{"seen":seen})
		check("continuous_collision_path_no_teleport_"+NAMES[di],continuous)
		check("finite_recovery_and_cooldown_"+NAMES[di],lab.player.action_kind.is_empty() and lab.player.ability_cooldown>0 and not lab.player.use_ability())
		check("ability_does_not_damage_or_score_"+NAMES[di],target.health==3 and target.hits_received==0 and lab.combat.damage_events==0 and lab.combat.attacks.is_empty() and lab.score==0 and lab.player.health==1)
		check("collision_masks_unchanged_"+NAMES[di],lab.player.collision_layer==2 and lab.player.collision_mask==1)
		await frames(95)
		check("cooldown_recovers_"+NAMES[di],lab.player.ability_cooldown==0 and lab.player.use_ability())
		lab.player.cancel_action()
	segment = "wall"
	await fixture(Vector2.RIGHT,3,false)
	var wall := StaticBody2D.new()
	wall.collision_layer=1
	var shape:=CollisionShape2D.new()
	var rectangle:=RectangleShape2D.new()
	rectangle.size=Vector2(4,64)
	shape.shape=rectangle
	wall.add_child(shape)
	wall.position=lab.player.position+Vector2(-22,-7)
	lab.add_child(wall)
	await frames(2)
	var start: Vector2=lab.player.position
	await tap(KEY_F)
	await frames(36)
	check("wall_stops_swept_body_without_tunnelling",lab.player.ability_distance>0 and lab.player.ability_distance<13 and lab.player.position.x>wall.position.x)
	await capture("wall_stops_backward_step")
	wall.queue_free()
	await frames(2)
	for reason in ["cancel","revoke","reopen","replace","hurt","death"]:
		segment="interrupt_"+reason
		await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F)
		await frames(9)
		check(reason+":inside_actual_motion",lab.player.action_kind=="disengage" and lab.player.ability_distance>0)
		var before: Vector2=lab.player.position
		if reason=="cancel": await tap(KEY_C)
		if reason=="revoke": lab.scene_policy.invalidate()
		if reason=="reopen": lab.scene_policy.open("timka_present")
		if reason=="replace":
			var owner=preload("res://scripts/systems/character_scene_policy.gd").new()
			owner.open("timka_present")
			lab.player.scene_policy=owner
		if reason=="hurt":
			lab.player.health=2
			lab.player.receive_hit(1,0.0,900,lab.enemies[0])
		if reason=="death": lab.player.receive_hit(1,0.0,901,lab.enemies[0])
		await frames(12)
		check(reason+":motion_cancelled_without_ghost_hit",lab.player.position.distance_to(before)<0.001 and lab.player.action_kind!="disengage" and lab.combat.damage_events==0 and lab.score==0)
		if reason=="death": check("death_has_own_fall_no_invulnerability",lab.state=="dead" and lab.player.health==0 and lab.player.sprite.animation==&"fall_right")
		if reason=="replace": lab.player.scene_policy=lab.scene_policy
		if reason in ["revoke","reopen"]: lab.scene_policy.open("timka_present")
		await tap(KEY_R)
		check(reason+":restart_clears_action_and_cost",lab.state=="playing" and lab.player.health==1 and lab.player.action_kind.is_empty() and lab.player.ability_cooldown==0 and lab.player.ability_distance==0)
	segment="pause"
	await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await frames(9)
	lab._set_options_visible(true)
	var clock: float=lab.player.action_elapsed
	start=lab.player.position
	var cooldown: float=lab.player.ability_cooldown
	await frames(14)
	check("options_freeze_action_cost_and_motion",lab.player.position==start and lab.player.action_elapsed==clock and lab.player.ability_cooldown==cooldown)
	lab._set_options_visible(false)
	await frames(30)
	check("resume_finishes_remaining_bounded_motion",absf(lab.player.ability_distance-33.6)<0.03 and lab.player.action_kind.is_empty())
	var options_results: Array=[]
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		root.get_node("OptionsStore").set_value(&"decals",not reduced,false)
		root.get_node("OptionsStore").set_value(&"shake",0 if reduced else 100,false)
		root.get_node("OptionsStore").set_value(&"flashes",not reduced,false)
		await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F)
		await frames(36)
		options_results.append([lab.player.health,lab.player.hits_received,lab.combat.damage_events,lab.score,snappedf(lab.player.ability_distance,0.01)])
	check("Full_Reduced_preserve_logic",options_results[0]==options_results[1])
	var original: int=lab.player.get_instance_id()
	var generation: int=lab.scene_policy.action_authority("timka").generation
	check("unfinished_prime_rejected_without_replacing_present",not lab.select_fixture("timka_prime") and lab.player.get_instance_id()==original and lab.scene_policy.action_authority("timka").generation==generation)
	check("failed_selection_leaves_present_usable",lab.player.actor_id=="timka" and lab.player.prepared_ability=="disengage")
	await tap(KEY_R)
	await capture("present_ready_after_restart")
	var failed:=checks.filter(func(item:Dictionary):return not item.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"TIMKA_PRESENT_DISENGAGE_COMPONENT_ONLY","passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"phase_approval":false,"checks":checks,"trace":trace,"captures":captures,"contacts":contacts,"not_tested":["prime context mechanics and distinctness","full P06","subjective gameplay feel","physical input latency","performance acceptance","native Windows","new audio/listening"]},"  "))
	file.close()
	print("RESULT P06_TIMKA_PRESENT passed=%d failed=%d"%[checks.size()-failed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
