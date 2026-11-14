extends "res://tests/gabar_combat_replay.gd"
## Actual production Olezhka controller; only the replay helpers are inherited.
var defenses: Array[Dictionary] = []
var revoke_after_parry := false

func check(name: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_OLEZHKA "+name)

func on_defense(event: Dictionary) -> void:
	var item := event.duplicate(true)
	item.segment = segment
	item.player_animation = String(lab.player.sprite.animation)
	item.player_frame = lab.player.sprite.frame
	item.player_action_elapsed = lab.player.action_elapsed
	defenses.append(item)
	if revoke_after_parry:
		revoke_after_parry = false
		lab.scene_policy.invalidate()

func enemy_strike(enemy: CharacterBody2D, category := "unarmed") -> int:
	var definition: Dictionary = lab.config.attacks.enemy_melee.duplicate(true)
	definition.category = category
	return lab.combat.start_melee(enemy,"enemy",(lab.player.position-enemy.position).normalized(),definition)

func run() -> void:
	output = OS.get_environment("AYAY_P06_OLEZHKA_OUTPUT")
	headless = DisplayServer.get_name()=="headless"
	if output.is_empty():
		push_error("AYAY_P06_OLEZHKA_OUTPUT required")
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
	await frames(2)
	check("complete_real_Olezhka_fixture_constructs",lab.select_fixture("olezhka_training"))
	if lab.player.actor_id != "olezhka":
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	lab.combat.contact_committed.connect(on_contact)
	lab.combat.contact_defended.connect(on_defense)
	if not headless: check("actual_engine_audio_recorder_starts",root.get_node("AudioDirector").begin_capture())
	check("own_56_clips_and_registered_speed",lab.player.sprite.sprite_frames.get_animation_names().size()==56 and lab.player.move_speed==106)
	check("firearm_environment_and_normal_ranged_denied",not lab.select_equipment(3) and not lab.select_equipment(4) and not lab.player.attack_ranged())
	await tap(KEY_TAB)
	check("equipment_blunt",lab.player.finisher_category=="blunt")
	await tap(KEY_TAB)
	check("equipment_sharp",lab.player.finisher_category=="sharp")
	await tap(KEY_TAB)
	check("equipment_skips_denied_to_unarmed",lab.player.finisher_category=="unarmed")
	trace_enabled = true
	for di in 4:
		segment = "continuous_run_guard_"+NAMES[di]
		await fixture(DIRECTIONS[di],3,false)
		for enemy in lab.enemies: enemy.position=Vector2(520,100)
		var code: Key = [KEY_S,KEY_A,KEY_D,KEY_W][di]
		key(code,true)
		await frames(7)
		await capture(segment+"_walk")
		key(KEY_SHIFT,true)
		await frames(7)
		check("held_run_Input_"+NAMES[di],lab.player.sprite.animation==StringName("run_"+NAMES[di]))
		await capture(segment+"_run")
		var before := trace.size()
		await tap(KEY_F)
		check("run_enters_guard_"+NAMES[di],lab.player.action_kind=="special" and lab.player.action_frame==0)
		await capture(segment+"_guard")
		await frames(46)
		check("miss_returns_to_same_held_run_"+NAMES[di],lab.player.action_kind.is_empty() and lab.player.sprite.animation==StringName("run_"+NAMES[di]) and lab.combat.damage_events==0)
		var bounded := true
		for index in range(before+1,trace.size()):
			var a: Dictionary=trace[index-1]
			var b: Dictionary=trace[index]
			if Vector2(a.position[0],a.position[1]).distance_to(Vector2(b.position[0],b.position[1]))>lab.player.move_speed*1.44*float(b.tick-a.tick)/60.0+0.001: bounded=false
		check("continuous_guard_path_has_no_teleport_"+NAMES[di],bounded)
		await capture(segment+"_back_to_run")
		key(code,false);key(KEY_SHIFT,false)
		await frames(2)
	for di in 4:
		segment = "counter_"+NAMES[di]
		var target: CharacterBody2D = await fixture(DIRECTIONS[di],3,false)
		await tap(KEY_F)
		check("guard_Input_"+NAMES[di],lab.player.action_kind=="special" and lab.player.action_frame==0 and lab.combat.attacks.is_empty())
		await capture(segment+"_guard")
		await frames(5)
		var incoming := enemy_strike(target)
		await frames(1)
		check("actual_melee_parried_"+NAMES[di],lab.player.health==1 and lab.player.hits_received==0 and lab.player.counter_blocks==1 and lab.combat.defended_events.size()==1 and lab.player.action_frame==1)
		check("parry_has_no_damage_blood_score_"+NAMES[di],lab.combat.damage_events==0 and lab.combat.contact_events.is_empty() and lab.score==0)
		await capture(segment+"_parry")
		check("same_receipt_cannot_parry_twice_"+NAMES[di],not lab.combat._apply_hit(lab.player,{"damage":1,"category":"unarmed"},incoming,target,"melee") and lab.player.counter_blocks==1)
		await frames(2)
		check("counter_contacts_through_Core_once_"+NAMES[di],target.health==2 and target.hits_received==1 and lab.combat.damage_events==1 and lab.player.health==1 and lab.score==0)
		await capture(segment+"_contact")
		await frames(8)
		check("finite_visible_recovery_"+NAMES[di],lab.player.action_kind=="special" and lab.player.action_frame==2)
		await capture(segment+"_recovery")
		await frames(25)
		check("counter_finite_and_cooldown_"+NAMES[di],lab.player.action_kind.is_empty() and lab.player.ability_cooldown>0 and not lab.player.use_ability() and target.hits_received==1 and lab.combat.attacks.is_empty())
	segment = "counter_miss"
	var target: CharacterBody2D = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await frames(48)
	check("miss_never_schedules_damage",target.hits_received==0 and lab.player.counter_blocks==0 and lab.combat.damage_events==0 and lab.player.action_kind.is_empty() and lab.combat.attacks.is_empty())
	await frames(80)
	check("cooldown_expires_and_allows_next_guard",lab.player.ability_cooldown==0 and lab.player.use_ability())
	for delay in [1,2,13,14]:
		segment = "counter_boundary_delay_"+str(delay)
		target = await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F)
		await frames(delay)
		var before_clock: float=lab.player.action_elapsed
		enemy_strike(target)
		await frames(1)
		var expected: bool = delay in [2,13]
		check("window_edge_"+str(delay),(lab.player.counter_blocks==1)==expected and (lab.player.health==1)==expected,{"before_contact_clock":before_clock,"expected_parry":expected})
		await frames(3)
	for reason in ["range","friendly","wall"]:
		segment="counter_geometry_"+reason
		target=await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F);await frames(5)
		var wall: StaticBody2D
		if reason=="range":target.position=lab.player.position+Vector2.RIGHT*46
		if reason=="friendly":target.collision_layer=2
		if reason=="wall":
			wall=StaticBody2D.new();wall.collision_layer=1;wall.collision_mask=0
			var shape:=CollisionShape2D.new();var rectangle:=RectangleShape2D.new();rectangle.size=Vector2(4,30);shape.shape=rectangle;wall.add_child(shape);wall.position=lab.player.position+Vector2(15,-7);lab.add_child(wall)
			await frames(1)
			check("own_defense_LOS_guard_rejects_wall",not lab.player.defend_melee_contact({"category":"unarmed"},912,target))
		var definition: Dictionary=lab.config.attacks.enemy_melee.duplicate(true)
		if reason=="range":definition.reach=34
		lab.combat.start_melee(target,"enemy",Vector2.LEFT,definition)
		await frames(3)
		check("geometry_guard_"+reason,lab.player.counter_blocks==0 and lab.combat.defended_events.is_empty() and (lab.player.health==1 if reason=="wall" else lab.player.health==0))
		if is_instance_valid(wall):wall.queue_free();await frames(1)
	for reason in ["early","late","rear","side","cancel","revoked","reopened","projectile","finisher","nonmelee","wrong_category"]:
		segment = "counter_reject_"+reason
		target = await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F)
		if reason=="late": await frames(18)
		elif reason!="early": await frames(5)
		if reason=="rear": target.position=lab.player.position+Vector2.LEFT*30
		if reason=="side": target.position=lab.player.position+Vector2.DOWN*30
		if reason=="cancel": await tap(KEY_C)
		if reason=="revoked": lab.scene_policy.invalidate()
		if reason=="reopened": lab.scene_policy.open("olezhka_training")
		if reason=="projectile":
			lab.combat.fire(target,"enemy",(lab.player.position-target.position).normalized(),lab.config.attacks.enemy_bullet)
		elif reason in ["finisher","nonmelee"]:
			lab.combat._apply_hit(lab.player,{"damage":1,"category":"unarmed","finisher":reason=="finisher"},911,target,"melee" if reason=="finisher" else "")
		else: enemy_strike(target,"firearm" if reason=="wrong_category" else "unarmed")
		await frames(6)
		check("no_invulnerability_"+reason,lab.player.health==0 and lab.player.counter_blocks==0 and lab.combat.defended_events.is_empty() and target.hits_received==0 and lab.combat.damage_events==1)
		if reason in ["revoked","reopened"]: check("restore_registered_authority_"+reason,lab.select_fixture("olezhka_training"))
	segment = "counter_one_contact_only"
	target = await fixture(Vector2.RIGHT,3,false)
	var second: CharacterBody2D = lab.enemies[1]
	second.position = target.position+Vector2(0,2)
	second.health = 3
	await tap(KEY_F)
	await frames(5)
	enemy_strike(target)
	enemy_strike(second)
	await frames(4)
	check("only_one_simultaneous_contact_parried",lab.player.counter_blocks==1 and lab.player.health==0 and lab.combat.defended_events.size()==1 and lab.combat.damage_events==1 and target.hits_received+second.hits_received==0)
	segment = "counter_revoke_after_parry"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await frames(5)
	revoke_after_parry = true
	enemy_strike(target)
	await frames(10)
	check("parry_reentry_revoke_prevents_counter_damage",lab.player.health==1 and lab.player.counter_blocks==1 and target.hits_received==0 and lab.combat.damage_events==0 and lab.combat.attacks.is_empty())
	check("restore_after_reentry",lab.select_fixture("olezhka_training"))
	segment = "counter_reset"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await frames(5)
	enemy_strike(target)
	await frames(1)
	lab.reset_encounter()
	for enemy in lab.enemies: enemy.set_physics_process(false)
	await frames(12)
	check("reset_clears_pending_counter_receipts_effects",lab.player.counter_blocks==0 and lab.player.ability_uses==0 and lab.player.ability_cooldown==0 and lab.combat.defended_events.is_empty() and lab.combat.receipts.is_empty() and lab.combat.damage_events==0 and lab.combat.attacks.is_empty())
	segment = "counter_options"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await frames(5)
	lab._set_options_visible(true)
	var clock: float = lab.player.action_elapsed
	var cooldown: float = lab.player.ability_cooldown
	await frames(12)
	check("options_pause_guard_and_cooldown",lab.player.action_elapsed==clock and lab.player.ability_cooldown==cooldown)
	lab._set_options_visible(false)
	enemy_strike(target)
	await frames(3)
	check("options_resume_same_guard_window",lab.player.counter_blocks==1 and target.hits_received==1)
	for di in 4:
		segment="reactions_"+NAMES[di]
		target=await fixture(DIRECTIONS[di],1,false)
		await tap(KEY_F);await tap(KEY_C)
		var nonlethal: Dictionary=lab.config.attacks.enemy_melee.duplicate(true)
		nonlethal.damage=0
		lab.combat.start_melee(target,"enemy",-DIRECTIONS[di],nonlethal)
		await frames(2)
		check("authored_hurt_"+NAMES[di],lab.player.health==1 and lab.player.hits_received==1 and lab.player.sprite.animation==StringName("hit_"+NAMES[di]))
		await capture(segment+"_hurt")
		enemy_strike(target)
		await frames(2)
		check("incoming_damage_cancels_to_authored_fall_"+NAMES[di],lab.player.health==0 and lab.player.sprite.animation==StringName("fall_"+NAMES[di]) and lab.player.sprite.frame==0 and lab.combat.attacks.all(func(item: Dictionary):return item.source!=lab.player))
		await capture(segment+"_fall")
		await frames(18)
		check("authored_death_hold_"+NAMES[di],lab.player.sprite.animation==StringName("fall_"+NAMES[di]) and lab.player.sprite.frame==1 and lab.player.counter_blocks==0)
		await capture(segment+"_death_hold")
	for category in ["unarmed","blunt","sharp"]:
		for di in 4:
			segment = "finisher_"+category+"_"+NAMES[di]
			target = await fixture(DIRECTIONS[di],1,true)
			check("equip_"+segment,lab.select_equipment(["unarmed","blunt","sharp"].find(category)))
			await tap(KEY_SPACE)
			var wait := 0
			while target.hits_received==0 and wait<30:
				await frames(1)
				wait += 1
			check("earned_shove_stun_"+segment,target.health==1 and target.hits_received==1 and target.state=="stunned")
			await tap(KEY_V)
			check("finisher_registered_windup_"+segment,not lab.combat.finisher_for(lab.player).is_empty() and lab.player.action_frame==0)
			await capture(segment+"_windup")
			wait = 0
			while target.health>0 and wait<40:
				await frames(1)
				wait += 1
			check("finisher_once_contact_"+segment,target.health==0 and target.hits_received==2 and lab.score==100 and lab.combat.damage_events==2 and lab.player.action_frame==1)
			await capture(segment+"_contact")
			await frames(8)
			await capture(segment+"_recovery")
			await tap(KEY_V)
			await frames(25)
			check("dead_no_repeat_damage_score_"+segment,target.state=="dead" and target.hits_received==2 and lab.score==100 and lab.combat.finisher_for(lab.player).is_empty())
	var settings_results: Array = []
	for reduced in [false,true]:
		segment = "counter_reduced_"+str(reduced)
		target = await fixture(Vector2.RIGHT,3,false)
		var options := root.get_node("OptionsStore")
		var intended := {"reduced_gore":reduced,"decals":not reduced,"flashes":not reduced,"shake":0.0 if reduced else 100.0,"vhs":not reduced}
		for key_name in intended:
			check("setting_applied:"+str(reduced)+":"+key_name,options.set_value(StringName(key_name),intended[key_name],false) and options.values[key_name]==intended[key_name])
		await tap(KEY_F)
		await frames(5)
		enemy_strike(target)
		await frames(12)
		settings_results.append([lab.player.health,target.health,target.hits_received,lab.combat.damage_events,lab.combat.defended_events.size(),lab.player.counter_blocks,lab.score,lab.player.collision_layer,lab.player.collision_mask])
		await capture(segment)
	check("Full_Reduced_preserve_counter_physics",settings_results[0]==settings_results[1],{"results":settings_results})
	var aligned := true
	for item in contacts:
		if item.segment.begins_with("counter_") and not item.target_is_player:
			aligned = aligned and item.player_action_frame==1 and String(item.player_animation).begins_with("special_")
		if item.finisher and not item.target_is_player: aligned = aligned and item.player_frame==1 and String(item.player_animation).begins_with("finish_")
	check("damage_uses_authored_contact_frame",aligned)
	var grid_error := 0.0
	var fractional := false
	for item in trace:
		var origin:=Vector2(item.visual_origin[0],item.visual_origin[1])
		grid_error=maxf(grid_error,origin.distance_to(origin.round()))
		var position:=Vector2(item.position[0],item.position[1])
		fractional=fractional or position.distance_to(position.round())>0.1
	check("pixel_alignment_preserves_fractional_body",grid_error<0.0001 and fractional,{"maximum_grid_error":grid_error})
	if not headless:
		await frames(12)
		check("actual_engine_audio_recording_saved",root.get_node("AudioDirector").end_capture(output.path_join("engine_mix.wav"))==OK)
	var failed := checks.filter(func(item: Dictionary):return not item.passed).size()
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"OLEZHKA_PRODUCTION_CONTROLLER_INTEGRATION_ONLY","phase_approval":false,"actual_input":true,"actor_id":"olezhka","renderer":DisplayServer.get_name(),"passed":failed==0,"checks":checks,"contacts":contacts,"defenses":defenses,"trace":trace,"captures":captures,"fixture":"declared placements and durability; paused AI only where specified; genuine core melee collision dispatch; finisher stun earned with Space against active enemy","not_tested":["other hero abilities","subjective hearing/real-time feel","native Windows","exports","full P06"]},"  "))
	file.close()
	print("RESULT P06_OLEZHKA passed=%d failed=%d" % [checks.size()-failed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
