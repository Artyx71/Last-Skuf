extends SceneTree
## Actual production scene/controller/Input. Bounded Gabar integration, not P06 PASS.
const Lab = preload("res://scripts/core/character_lab.gd")
const NAMES := ["down","left","right","up"]
const DIRECTIONS := [Vector2.DOWN,Vector2.LEFT,Vector2.RIGHT,Vector2.UP]
var lab: Node2D
var checks: Array[Dictionary] = []
var contacts: Array[Dictionary] = []
var trace: Array[Dictionary] = []
var captures: Array[Dictionary] = []
var output := ""
var headless := true
var segment := "initial"
var trace_enabled := false
var revoke_on_contact := false

func _initialize() -> void: call_deferred("run")

func check(name: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_GABAR "+name)

func frames(count: int) -> void:
	for i in count:
		await physics_frame
		await process_frame
		if trace_enabled and is_instance_valid(lab.player):
			var p = lab.player
			trace.append({"segment":segment,"tick":Engine.get_physics_frames(),"wall_usec":Time.get_ticks_usec(),"position":[p.position.x,p.position.y],"velocity":[p.velocity.x,p.velocity.y],"animation":String(p.sprite.animation),"frame":p.sprite.frame,"action_kind":p.action_kind,"action_elapsed":p.action_elapsed,"action_frame":p.action_frame,"damage_events":lab.combat.damage_events,"score":lab.score,"visual_origin":[p.sprite.get_global_transform_with_canvas().origin.x,p.sprite.get_global_transform_with_canvas().origin.y]})

func key(code: Key, pressed: bool) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.physical_keycode = code
	event.pressed = pressed
	Input.parse_input_event(event)

func tap(code: Key) -> void:
	key(code,true)
	await frames(1)
	key(code,false)
	await frames(1)

func capture(name: String) -> void:
	if headless or not Engine.get_write_movie_path().is_empty(): return
	await RenderingServer.frame_post_draw
	var path := output.path_join(name+".png")
	var code := root.get_texture().get_image().save_png(path)
	captures.append({"name":name,"path":path,"code":code,"tick":Engine.get_physics_frames(),"animation":String(lab.player.sprite.animation),"frame":lab.player.sprite.frame})
	check("actual_viewport:"+name,code==OK)

func on_contact(event: Dictionary) -> void:
	var item := event.duplicate(true)
	item.segment = segment
	item.target_is_player = event.target==lab.player.get_instance_id()
	item.player_animation = String(lab.player.sprite.animation)
	item.player_frame = lab.player.sprite.frame
	item.player_action_elapsed = lab.player.action_elapsed
	item.player_action_frame = lab.player.action_frame
	contacts.append(item)
	if revoke_on_contact and not item.target_is_player:
		revoke_on_contact = false
		lab.scene_policy.invalidate()

func fixture(direction: Vector2, target_health := 1, active_target := true) -> CharacterBody2D:
	# Declared initial placements/durability only. Finisher stun is earned by Input.
	lab.reset_encounter()
	lab.auto_retry = false
	lab.player.position = Vector2(280,240)-direction*30
	lab.player.set_aim(direction)
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(520,100)
	lab.training_bench.position = Vector2(450,270)
	lab.training_bench.set_meta("finisher_enabled",false)
	var target: CharacterBody2D = lab.enemies[0]
	target.position = Vector2(280,240)
	target.health = target_health
	target.locked_aim = -direction
	target.set_physics_process(active_target)
	await frames(2)
	return target

func run() -> void:
	output = OS.get_environment("AYAY_P06_GABAR_OUTPUT")
	headless = DisplayServer.get_name()=="headless"
	if output.is_empty():
		push_error("AYAY_P06_GABAR_OUTPUT required")
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	lab = Lab.new()
	root.add_child(lab)
	current_scene = lab
	lab.auto_retry = false
	lab.combat.contact_committed.connect(on_contact)
	if not headless: check("actual_engine_audio_recorder_starts",root.get_node("AudioDirector").begin_capture())
	await frames(3)
	check("real_Gabar_body_owns_56_clips",lab.player.actor_id=="gabar" and lab.player.sprite.sprite_frames.get_animation_names().size()==56)
	check("registered_scene_speed_and_no_legacy_kit",lab.player.move_speed==110 and lab.player.kit=="escape")
	var epoch: int = lab.combat.encounter_epoch
	var authority: Dictionary = lab.player.finisher_authority("unarmed")
	check("unregistered_fixture_keeps_current_actor",not lab.select_fixture("unregistered_fixture") and lab.player.actor_id=="gabar" and lab.combat.encounter_epoch==epoch)
	check("unknown_fixture_rejected",not lab.select_fixture("saved_prime") and lab.scene_policy.definition().actor_id=="gabar")
	var rejected := preload("res://scripts/actors/character_player.gd").new()
	check("supporting_factory_rejected",not rejected.configure("ellana",lab.scene_policy))
	rejected.free()
	check("reopen_registered_fixture_succeeds",lab.select_fixture("gabar_training"))
	check("same_scene_reopen_revokes_old_authority",authority!=lab.player.finisher_authority("unarmed") and lab.combat.encounter_epoch>epoch)
	check("Gabar_sharp_and_environmental_denied",not lab.select_equipment(2) and not lab.select_equipment(4))
	await tap(KEY_TAB)
	check("Tab_cycles_to_blunt_once",lab.player.finisher_category=="blunt")
	await tap(KEY_TAB)
	check("Tab_skips_sharp_to_firearm_once",lab.player.finisher_category=="firearm")
	await tap(KEY_TAB)
	check("Tab_skips_environmental_to_unarmed_once",lab.player.finisher_category=="unarmed")
	await tap(KEY_F2)
	check("F2_does_not_grant_Yakuza_training_kit",lab.player.kit=="escape")
	check("drawn_firearm_does_not_grant_normal_ranged",not lab.player.attack_ranged())
	trace_enabled = true
	for di in 4:
		segment = "movement_"+NAMES[di]
		await fixture(DIRECTIONS[di],1,false)
		var code: Key = [KEY_S,KEY_A,KEY_D,KEY_W][di]
		var start: Vector2 = lab.player.position
		key(code,true)
		await frames(8)
		check("walk_Input_"+NAMES[di],lab.player.sprite.animation==StringName("walk_"+NAMES[di]) and lab.player.position.distance_to(start)>10)
		await capture(segment)
		key(KEY_SHIFT,true)
		await frames(8)
		check("run_Input_"+NAMES[di],lab.player.sprite.animation==StringName("run_"+NAMES[di]))
		await capture("run_"+NAMES[di])
		# Continue the same body/Input path through a special and back to movement.
		for enemy in lab.enemies: enemy.position = Vector2(520,100)
		segment = "continuous_run_special_"+NAMES[di]
		var join_start := trace.size()
		await tap(KEY_F)
		check("run_to_special_join_"+NAMES[di],lab.player.action_kind=="special")
		await capture(segment+"_windup")
		await frames(39)
		check("special_returns_to_held_run_Input_"+NAMES[di],lab.player.action_kind.is_empty() and lab.player.sprite.animation==StringName("run_"+NAMES[di]))
		var bounded := true
		for index in range(join_start+1,trace.size()):
			var a: Dictionary = trace[index-1]
			var b: Dictionary = trace[index]
			var distance := Vector2(a.position[0],a.position[1]).distance_to(Vector2(b.position[0],b.position[1]))
			if distance > maxf(210.0,lab.player.move_speed*1.44)*float(b.tick-a.tick)/60.0+0.001: bounded = false
		check("continuous_run_special_path_has_no_teleports_"+NAMES[di],bounded)
		await capture(segment+"_back_to_run")
		key(code,false)
		key(KEY_SHIFT,false)
		await frames(2)
	for di in 4:
		segment = "special_"+NAMES[di]
		var target: CharacterBody2D = await fixture(DIRECTIONS[di],4,false)
		await tap(KEY_F)
		check("special_Input_enters_windup_"+NAMES[di],lab.player.action_kind=="special" and lab.player.action_frame==0 and target.hits_received==0)
		check("special_cannot_restart_during_windup_"+NAMES[di],not lab.player.use_ability())
		await capture(segment+"_windup")
		var guard := 0
		while target.hits_received==0 and guard<30:
			await frames(1)
			guard += 1
		check("special_contact_once_"+NAMES[di],target.hits_received==1 and target.health==3 and lab.player.action_frame==1)
		await capture(segment+"_contact")
		await frames(12)
		check("special_visible_recovery_"+NAMES[di],lab.player.action_kind=="special" and lab.player.action_frame==2)
		await capture(segment+"_recovery")
		await frames(28)
		check("special_finite_collision_move_and_single_damage_"+NAMES[di],lab.player.ability_distance>15 and lab.player.ability_distance<=28 and lab.combat.damage_events==1 and target.hits_received==1 and lab.player.action_kind.is_empty(),{"distance":lab.player.ability_distance})
		check("special_cooldown_after_recovery_"+NAMES[di],lab.player.ability_cooldown>0 and not lab.player.use_ability())
	segment = "special_wall"
	await fixture(Vector2.RIGHT,4,false)
	lab.player.position = Vector2(603,284)
	await tap(KEY_F)
	await frames(38)
	check("special_sweeps_body_into_wall_without_teleport",lab.player.position.x<=612.1 and lab.player.position.x>=603 and lab.player.ability_distance<12,{"x":lab.player.position.x,"distance":lab.player.ability_distance})
	await capture(segment)
	segment = "special_cancel"
	var cancelled: CharacterBody2D = await fixture(Vector2.RIGHT,4,false)
	await tap(KEY_F)
	await tap(KEY_C)
	await frames(35)
	check("C_cancels_special_before_damage",cancelled.hits_received==0 and lab.combat.attacks.is_empty() and lab.player.ability_uses==1 and lab.player.ability_cooldown>0)
	segment = "special_interrupt"
	cancelled = await fixture(Vector2.RIGHT,4,false)
	await tap(KEY_F)
	lab.combat._apply_hit(lab.player,{"damage":0,"stun":0.2,"category":"unarmed"},991,cancelled)
	await frames(35)
	check("incoming_hit_interrupts_special_without_late_damage",cancelled.hits_received==0 and lab.player.hits_received==1 and lab.combat.attacks.is_empty())
	for action_key in [KEY_SPACE,KEY_F]:
		for revoke_mode in ["invalidate","reopen"]:
			segment = "revoked_pending_"+str(action_key)+"_"+revoke_mode
			var waiting: CharacterBody2D = await fixture(Vector2.RIGHT,4,false)
			await tap(action_key)
			if revoke_mode=="invalidate": lab.scene_policy.invalidate()
			else: lab.scene_policy.open("gabar_training")
			await frames(35)
			check("pending_melee_authority_revoked_"+segment,waiting.hits_received==0 and lab.combat.damage_events==0 and lab.combat.attacks.is_empty() and lab.player.ability_distance==0)
			lab.select_fixture("gabar_training")
	segment = "revoked_between_same_tick_targets"
	var first_target: CharacterBody2D = await fixture(Vector2.RIGHT,4,false)
	var second_target: CharacterBody2D = lab.enemies[1]
	second_target.position = first_target.position+Vector2(0,2)
	second_target.health = 4
	revoke_on_contact = true
	await tap(KEY_F)
	await frames(35)
	check("same_tick_reentry_revokes_remaining_target_contacts",first_target.hits_received+second_target.hits_received==1 and lab.combat.damage_events==1 and lab.combat.attacks.is_empty())
	lab.select_fixture("gabar_training")
	segment = "revoked_during_active_window"
	first_target = await fixture(Vector2.RIGHT,4,false)
	second_target = lab.enemies[1]
	second_target.health = 4
	await tap(KEY_F)
	var active_guard := 0
	while first_target.hits_received==0 and active_guard<30:
		await frames(1)
		active_guard += 1
	check("active_window_first_contact_is_real",first_target.hits_received==1 and lab.player.action_frame==1)
	lab.scene_policy.open("gabar_training")
	second_target.position = lab.player.position+Vector2(20,0)
	await frames(30)
	check("active_window_generation_revoke_blocks_later_targets",second_target.hits_received==0 and lab.combat.damage_events==1 and lab.combat.attacks.is_empty())
	lab.select_fixture("gabar_training")
	for category in ["unarmed","blunt","firearm"]:
		for di in 4:
			segment = "finisher_"+category+"_"+NAMES[di]
			var target: CharacterBody2D = await fixture(DIRECTIONS[di])
			lab.select_equipment(["unarmed","blunt","sharp","firearm","environmental"].find(category))
			await tap(KEY_SPACE)
			var guard := 0
			while target.hits_received==0 and guard<30:
				await frames(1)
				guard += 1
			check("earned_shove_stun_"+segment,target.state=="stunned" and target.health==1 and target.hits_received==1)
			await tap(KEY_V)
			check("finisher_Input_windup_"+segment,not lab.combat.finisher_for(lab.player).is_empty() and lab.player.action_frame==0)
			await capture(segment+"_windup")
			guard = 0
			while target.health>0 and guard<40:
				await frames(1)
				guard += 1
			check("finisher_single_contact_"+segment,target.health==0 and target.hits_received==2 and lab.player.action_frame==1 and lab.score==100 and lab.kills==1)
			await capture(segment+"_contact")
			await frames(8)
			await capture(segment+"_recovery")
			await tap(KEY_V)
			await frames(25)
			check("finisher_once_score_and_cleanup_"+segment,lab.score==100 and lab.kills==1 and lab.combat.damage_events==2 and lab.combat.finishers.is_empty() and lab.player.action_kind.is_empty())
	segment = "finisher_cancel"
	var target: CharacterBody2D = await fixture(Vector2.RIGHT)
	await tap(KEY_SPACE)
	await frames(7)
	await tap(KEY_V)
	await tap(KEY_C)
	await frames(30)
	check("finisher_C_cancels_without_score",target.health==1 and lab.score==0 and lab.combat.finishers.is_empty() and target.hits_received==1)
	segment = "authority_revoked"
	target = await fixture(Vector2.RIGHT)
	await tap(KEY_SPACE)
	await frames(7)
	await tap(KEY_V)
	lab.scene_policy.invalidate()
	await frames(25)
	check("revoked_authority_prevents_finisher_contact",target.health==1 and lab.score==0 and lab.combat.finishers.is_empty())
	check("revoked_authority_denies_new_action",not lab.player.use_ability() and not lab.player.attack_melee())
	lab.select_fixture("gabar_training")
	segment = "reset_active"
	target = await fixture(Vector2.RIGHT)
	await tap(KEY_SPACE)
	await frames(7)
	await tap(KEY_V)
	var previous_epoch: int = lab.combat.encounter_epoch
	await tap(KEY_R)
	check("Input_reset_revokes_jobs_and_all_effects",lab.combat.encounter_epoch>previous_epoch and lab.combat.finishers.is_empty() and lab.combat.receipts.is_empty() and lab.combat.impact.particles.is_empty() and lab.combat.impact.decals.is_empty() and lab.combat.impact.held_poses.is_empty() and lab.score==0 and lab.player.ability_cooldown==0)
	segment = "death_during_special"
	target = await fixture(Vector2.RIGHT,4,false)
	await tap(KEY_F)
	lab.combat._apply_hit(lab.player,{"damage":1,"stun":0,"category":"unarmed"},992,target)
	await frames(30)
	check("death_cancels_special_and_holds_authored_death",lab.player.health==0 and lab.state=="dead" and target.hits_received==0 and lab.combat.attacks.is_empty() and lab.player.sprite.animation==&"fall_right" and lab.player.sprite.frame==1)
	await capture("Gabar_death_hold_right")
	await tap(KEY_R)
	check("retry_restores_character_policy_speed_without_new_unlock",lab.player.health==1 and lab.player.actor_id=="gabar" and lab.player.move_speed==110 and lab.player.ability_cooldown==0 and lab.player.ability_uses==0)
	var settings_results: Array = []
	for reduced in [false,true]:
		segment = "settings_reduced_"+str(reduced)
		var store := root.get_node("OptionsStore")
		store.set_value(&"reduced_gore",reduced,false)
		store.set_value(&"decals",not reduced,false)
		store.set_value(&"flashes",not reduced,false)
		store.set_value(&"shake",0 if reduced else 100,false)
		store.set_value(&"vhs",not reduced,false)
		target = await fixture(Vector2.RIGHT,4,false)
		await tap(KEY_F)
		await frames(37)
		settings_results.append([target.health,target.hits_received,lab.combat.damage_events,lab.score,snappedf(lab.player.ability_distance,0.01),lab.player.ability_uses,lab.player.collision_layer,lab.player.collision_mask])
		await capture("Gabar_gore_reduced_"+str(reduced))
	check("Full_Reduced_other_visual_options_preserve_combat",settings_results[0]==settings_results[1],{"results":settings_results})
	lab.reset_encounter()
	# New body must preserve fractional physics while rendering only on whole pixels.
	var grid_error := 0.0
	var fractional := false
	for item in trace:
		var origin := Vector2(item.visual_origin[0],item.visual_origin[1])
		grid_error = maxf(grid_error,origin.distance_to(origin.round()))
		var position := Vector2(item.position[0],item.position[1])
		fractional = fractional or position.distance_to(position.round())>0.1
	check("render_grid_alignment_preserves_fractional_physics",grid_error<0.0001 and fractional,{"maximum_visual_grid_error":grid_error})
	var aligned := true
	for item in contacts:
		if item.segment.begins_with("special_") and not item.target_is_player:
			aligned = aligned and item.player_action_frame==1 and String(item.player_animation).begins_with("special_")
		if item.finisher: aligned = aligned and item.player_frame==1 and String(item.player_animation).begins_with("finish_")
	check("damage_tick_displays_actual_authored_contact_pose",aligned)
	if not headless:
		await frames(12)
		check("actual_engine_audio_recording_saved",root.get_node("AudioDirector").end_capture(output.path_join("engine_mix.wav"))==OK)
	var failed := 0
	for item in checks:
		if not item.passed: failed += 1
	var report := {"schema":1,"scope":"GABAR_PRODUCTION_CONTROLLER_INTEGRATION_ONLY","phase_approval":false,"actor_id":"gabar","actual_input":true,"renderer":DisplayServer.get_name(),"headless":headless,"movie":Engine.get_write_movie_path(),"passed":failed==0,"checks":checks,"contacts":contacts,"trace":trace,"captures":captures,"fixture":"declared initial positions; special target health4 and paused AI; finisher vulnerability earned by real Space Input against active production enemy","not_tested":["other five hero bodies and abilities","full P06","subjective real-time feel","native Windows","exports"]}
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "))
	file.close()
	print("RESULT P06_GABAR passed=%d failed=%d" % [checks.size()-failed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
