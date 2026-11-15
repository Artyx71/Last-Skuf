extends "res://tests/gabar_combat_replay.gd"
## Candidate two-context production integration, not ART/feel or full P06 acceptance.

func check(name: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_TIMKA_PRIME "+name)

func prime_target(direction: Vector2) -> CharacterBody2D:
	var target := await fixture(direction,1,true)
	# Declared close initial placement before Input; keep the real one-hit NPC
	# alive with the nonlethal heavy contact, then earn the clinch vulnerability.
	lab.player.position+=direction*4
	await frames(2)
	await tap(KEY_SPACE)
	await frames(37)
	check(segment+":vulnerability_earned_by_Input",target.health==1 and target.hits_received==1 and target.state=="stunned" and target.stun_remaining>0.5 and lab.player.action_kind.is_empty() and lab.combat.damage_events==1 and lab.score==0)
	return target

func run() -> void:
	output=OS.get_environment("AYAY_P06_TIMKA_PRIME_OUTPUT")
	headless=DisplayServer.get_name()=="headless"
	if output.is_empty():
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	lab=Lab.new()
	root.add_child(lab)
	current_scene=lab
	await frames(2)
	lab.auto_retry=false
	lab.combat.contact_committed.connect(on_contact)
	trace_enabled=true
	for present in [true,false]:
		await tap(KEY_3 if present else KEY_4)
		check("own_context_selected:"+str(present),lab.player.actor_id=="timka" and lab.player.prepared_ability==("disengage" if present else "clinch") and lab.player.move_speed==(84 if present else 118))
		var frameset: SpriteFrames=lab.player.authored_frames
		check("own_required_clip_count:"+str(present),frameset.get_animation_names().size()==(32 if present else 48))
		for di in 4:
			var route: String=("present" if present else "prime")+"_locomotion_"+NAMES[di]
			segment="setup_"+route
			await fixture(DIRECTIONS[di],1,false)
			for enemy in lab.enemies:enemy.position=Vector2(520,100)
			lab.player.position=Vector2(280,300 if di==3 else 190) if di in [0,3] else Vector2(300,280)
			await frames(2)
			segment=route
			var idle: Texture2D=frameset.get_frame_texture(StringName("idle_"+NAMES[di]),0)
			check(segment+":different_authored_stance",idle.get_meta("source_kind")==("world" if present else "finisher"))
			var movement: Texture2D=frameset.get_frame_texture(StringName("walk_"+NAMES[di]),0)
			check(segment+":different_authored_stride",movement.get_meta("original_source_column")== (2 if present else 6) and frameset.get_frame_count(StringName("walk_"+NAMES[di]))==(4 if present else 2))
			var code: Key=[KEY_S,KEY_A,KEY_D,KEY_W][di]
			# Real directional Input establishes facing before either idle pose.
			key(code,true);await frames(2);key(code,false);await frames(2)
			for expected_frame in [0,1]:
				var wait_budget:=60
				while (lab.player.sprite.animation!=StringName("idle_"+NAMES[di]) or lab.player.sprite.frame!=expected_frame) and wait_budget>0:
					await frames(1);wait_budget-=1
				check(segment+":actual_directional_idle_"+str(expected_frame),lab.player.sprite.animation==StringName("idle_"+NAMES[di]) and lab.player.sprite.frame==expected_frame)
				await capture(segment+"_stance"+str(expected_frame))
			var start: Vector2=lab.player.position
			var observed_frames: Array=[]
			var previous_frame: int=-1
			var wraps:=0
			key(code,true)
			for tick in (70 if present else 50):
				await frames(1)
				var actual_frame: int=lab.player.sprite.frame
				if previous_frame>=0 and actual_frame<previous_frame:wraps+=1
				previous_frame=actual_frame
				if actual_frame not in observed_frames:
					observed_frames.append(actual_frame)
					await capture(segment+"_walk_frame"+str(actual_frame))
			check(segment+":real_Input_stride",lab.player.sprite.animation==StringName("walk_"+NAMES[di]) and lab.player.position.distance_to(start)>5)
			check(segment+":all_drawn_walk_frames_displayed",observed_frames==([0,1,2,3] if present else [0,1]),{"observed":observed_frames})
			check(segment+":two_real_animation_cycles",wraps>=2,{"observed_wraps":wraps})
			key(code,false)
			await frames(2)
	for di in 4:
		segment="clinch_"+NAMES[di]
		var target:=await prime_target(DIRECTIONS[di])
		await tap(KEY_F)
		var job: Dictionary=lab.combat.finisher_for(lab.player).duplicate(true)
		check(segment+":Core_reserved_real_target",not job.is_empty() and target.state=="finisher_reaction" and lab.player.ability_uses==1 and lab.player.action_animation==StringName("special_"+NAMES[di]))
		check(segment+":no_early_damage",target.health==1 and target.hits_received==1 and lab.combat.damage_events==1 and lab.score==0 and not lab.player.use_ability())
		await capture(segment+"_guard")
		var limit:=60
		while target.health>0 and limit>0:
			await frames(1)
			limit-=1
		check(segment+":once_contact_kills_and_rewards",target.health==0 and target.hits_received==2 and lab.combat.damage_events==2 and lab.kills==1 and lab.score==100)
		check(segment+":NPC_contact_reaction_is_visible_before_death_hold",target.sprite.frame==1,{"NPC_frame_on_contact":target.sprite.frame})
		var pose: Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
		check(segment+":signature_drawn_contact_on_damage_tick",lab.player.action_frame==1 and lab.player.sprite.animation==StringName("special_"+NAMES[di]) and pose.get_meta("source_kind")=="finisher" and pose.get_meta("original_source_column")==7)
		await capture(segment+"_contact")
		if not job.is_empty(): check(segment+":duplicate_callback_denied",not lab.combat._apply_hit(target,job.definition,job.id,lab.player))
		await frames(8)
		await capture(segment+"_recovery")
		await frames(30)
		check(segment+":finite_recovery_no_repeat",lab.player.action_kind.is_empty() and lab.combat.finisher_for(lab.player).is_empty() and target.health==0 and target.hits_received==2 and lab.score==100 and lab.player.ability_cooldown>0)
		await frames(80)
		check(segment+":cooldown_recovers",lab.player.ability_cooldown==0)
	for reason in ["healthy","range","facing","wall","tool"]:
		segment="deny_"+reason
		var target: CharacterBody2D
		if reason=="healthy": target=await fixture(Vector2.RIGHT,1,false)
		else: target=await prime_target(Vector2.RIGHT)
		var wall: StaticBody2D
		if reason=="range":target.position.x+=70
		if reason=="facing":lab.player.set_aim(Vector2.LEFT)
		if reason=="tool":check("real_blunt_equipped",lab.select_equipment(1))
		if reason=="wall":
			wall=StaticBody2D.new();wall.collision_layer=1
			var shape:=CollisionShape2D.new();var rect:=RectangleShape2D.new();rect.size=Vector2(4,45);shape.shape=rect;wall.add_child(shape)
			wall.position=(lab.player.position+target.position)*0.5+Vector2(0,-7);lab.add_child(wall)
			await frames(2)
		check(segment+":no_grant_cost_or_reservation",not lab.player.use_ability() and lab.player.ability_uses==0 and lab.player.ability_cooldown==0 and lab.combat.finisher_for(lab.player).is_empty() and target.health==1 and lab.score==0)
		if is_instance_valid(wall):wall.queue_free();await frames(1)
	for reason in ["cancel","movement","revoke","reopen","hurt","death","restart"]:
		segment="interrupt_clinch_"+reason
		lab.scene_policy.open("timka_prime")
		var target:=await prime_target(Vector2.RIGHT)
		var attacker: CharacterBody2D=lab.enemies[1]
		attacker.position=lab.player.position+Vector2(-20,0)
		attacker.locked_aim=Vector2.RIGHT
		if reason=="hurt":lab.player.health=2
		await tap(KEY_F)
		await frames(7)
		if reason=="cancel":await tap(KEY_C)
		if reason=="movement":key(KEY_A,true)
		if reason=="revoke":lab.scene_policy.invalidate()
		if reason=="reopen":lab.scene_policy.open("timka_prime")
		if reason in ["hurt","death"]:lab.combat.start_melee(attacker,"enemy",attacker.locked_aim,lab.config.attacks.enemy_melee)
		if reason=="restart":await tap(KEY_R)
		await frames(2)
		key(KEY_A,false)
		check(segment+":no_clinch_damage_or_reward",target.health>0 and lab.score==0 and lab.combat.finisher_for(lab.player).is_empty() and lab.player.action_kind!="finish_unarmed")
		if reason in ["hurt","death"]:
			check(segment+":real_incoming_Core_contact_interrupts",lab.player.health==(1 if reason=="hurt" else 0) and lab.player.hits_received==1 and lab.player.counter_blocks==0 and contacts.any(func(item:Dictionary):return item.segment==segment and item.target_is_player))
			await capture(segment+"_actual_contact")
		if reason!="restart":check(segment+":cost_not_refunded",lab.player.ability_uses==1 and lab.player.ability_cooldown>0)
		lab.scene_policy.open("timka_prime")
		await tap(KEY_R)
		check(segment+":restart_clears_cost_and_receipts",lab.player.health==1 and lab.player.ability_uses==0 and lab.player.ability_cooldown==0 and lab.combat.receipts.is_empty())
	for di in 4:
		for category in ["unarmed","blunt","environmental"]:
			segment="V_finisher_"+category+"_"+NAMES[di]
			var target: CharacterBody2D
			if category=="environmental":
				# Declared whole fixture placement before the first measured Input.
				lab.reset_encounter()
				lab.player.position=Vector2(470,250)-DIRECTIONS[di]*26;lab.player.set_aim(DIRECTIONS[di])
				for enemy in lab.enemies:enemy.set_physics_process(false);enemy.position=Vector2(520,100)
				target=lab.enemies[0];target.position=Vector2(470,250);target.set_physics_process(true)
				lab.training_bench.position=target.position+DIRECTIONS[di]*30;lab.training_bench.set_meta("finisher_enabled",true)
				await frames(2);await tap(KEY_SPACE);await frames(37)
			else:target=await prime_target(DIRECTIONS[di])
			var index: int={"unarmed":0,"blunt":1,"environmental":4}[category]
			check(segment+":registered_equipment",lab.select_equipment(index))
			await tap(KEY_V)
			check(segment+":own_category_pose_started",lab.player.action_animation==StringName("finish_"+category+"_"+NAMES[di]) and not lab.combat.finisher_for(lab.player).is_empty())
			await capture(segment+"_guard")
			var limit:=60
			while target.health>0 and limit>0:await frames(1);limit-=1
			check(segment+":NPC_contact_reaction_is_visible",target.health==0 and target.sprite.frame==1,{"NPC_frame_on_contact":target.sprite.frame})
			await capture(segment+"_contact")
			await frames(10)
			check(segment+":NPC_finishes_in_death_hold",target.state=="dead" and target.sprite.frame==2)
			await capture(segment+"_recovery")
			await frames(25)
			check(segment+":once_reward",target.health==0 and lab.score==100 and lab.kills==1 and target.hits_received==2)
	for index in [2,3]:check("excluded_tool_denied:"+str(index),not lab.select_equipment(index))
	for source_present in [true,false]:
		segment="context_leak_"+str(source_present)
		await tap(KEY_3 if source_present else KEY_4)
		await fixture(Vector2.RIGHT,1,false)
		var before: Vector2=lab.player.position
		lab.scene_policy.open("timka_prime" if source_present else "timka_present")
		check(segment+":same_actor_policy_cannot_replace_prepared_body",not lab.player.use_ability() and not lab.player.attack_melee() and not lab.player.can_use_finisher("unarmed"))
		key(KEY_D,true);await frames(6);key(KEY_D,false)
		check(segment+":no_unauthorized_movement",lab.player.position.distance_to(before)<0.001)
		await tap(KEY_4)
		check(segment+":atomic_host_switch_restores_correct_prime",lab.player.prepared_ability=="clinch" and lab.player.move_speed==118 and lab.player._prepared_policy_matches_live())
	var outcomes: Array=[]
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		root.get_node("OptionsStore").set_value(&"decals",not reduced,false)
		root.get_node("OptionsStore").set_value(&"flashes",not reduced,false)
		root.get_node("OptionsStore").set_value(&"shake",0 if reduced else 100,false)
		segment="settings_"+str(reduced)
		var target:=await prime_target(Vector2.RIGHT)
		await tap(KEY_F);await frames(65)
		outcomes.append([target.health,target.hits_received,lab.combat.damage_events,lab.score,lab.kills,lab.player.ability_uses])
	check("Full_Reduced_preserve_actual_clinch_logic",outcomes[0]==outcomes[1],{"outcomes":outcomes})
	var failed:=checks.filter(func(item:Dictionary):return not item.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"TIMKA_PRIME_CONTEXT_CANDIDATE_ONLY","passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"phase_approval":false,"checks":checks,"trace":trace,"contacts":contacts,"captures":captures,"not_tested":["independent ART/Gameplay acceptance","new character audio/listening","full P06","FPS/hardware latency","native Windows","exports"]},"  "))
	file.close()
	print("RESULT P06_TIMKA_PRIME passed=%d failed=%d"%[checks.size()-failed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
