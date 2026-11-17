extends "res://tests/gabar_combat_replay.gd"
## Actual Input and authored roll; fixtures declare setup, never a measured teleport.
const Roll = preload("res://scripts/abilities/ground_roll.gd")
const MOVEMENT_KEYS := [KEY_S,KEY_A,KEY_D,KEY_W]

func check(label: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":label,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_RYZHIK "+label)

func roll_fixture(di: int, landing_target := true) -> CharacterBody2D:
	segment="setup_"+NAMES[di]
	lab.reset_encounter()
	lab.auto_retry=false
	lab.player.position=[Vector2(280,220),Vector2(300,240),Vector2(260,240),Vector2(280,276)][di]
	lab.player.set_aim(DIRECTIONS[di])
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position=Vector2(540,100)
	lab.training_bench.set_meta("finisher_enabled",false)
	lab.training_bench.position=Vector2(450,270)
	var target: CharacterBody2D=lab.enemies[0]
	target.health=1
	if landing_target: target.position=lab.player.position+DIRECTIONS[di]*(57.6+14.0)
	await frames(2)
	return target

func run() -> void:
	output=OS.get_environment("AYAY_P06_RYZHIK_OUTPUT")
	headless=DisplayServer.get_name()=="headless"
	if output.is_empty():
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	lab=Lab.new();root.add_child(lab);current_scene=lab
	await frames(2);await tap(KEY_5)
	check("real_registered_Input_selection",lab.player.actor_id=="ryzhik" and lab.player.prepared_ability=="dance_step")
	if lab.player.actor_id!="ryzhik":
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact)
	var all_own:=true
	var atlas: SpriteFrames=lab.player.sprite.sprite_frames
	for name in atlas.get_animation_names():
		for f in atlas.get_frame_count(name):
			var t:=atlas.get_frame_texture(name,f)
			all_own=all_own and t.get_meta("character_id","")=="ryzhik" and t.has_meta("clothing_socket")
	check("all60clips_own_and_clothing_bound",atlas.get_animation_names().size()==60 and all_own)
	check("speed120_no_ranged_kit",lab.player.move_speed==120 and not lab.player.attack_ranged())
	for category in ["sharp","firearm"]: check("latent_drawings_do_not_grant_"+category,not lab.player.can_use_finisher(category))
	trace_enabled=true
	for di in 4:
		var target:=await roll_fixture(di)
		segment="walk_roll_walk_"+NAMES[di]
		key(MOVEMENT_KEYS[di],true);await frames(2);key(MOVEMENT_KEYS[di],false);await frames(1)
		var start: Vector2=lab.player.position
		target.position=start+DIRECTIONS[di]*(57.6+14.0)
		var offset:=trace.size();var contact_offset:=contacts.size()
		await capture(segment+"_world_before")
		await tap(KEY_F)
		check("Input_starts_own_frame0_"+NAMES[di],lab.player.action_kind=="roll" and lab.player.action_frame==0 and lab.player.sprite.animation==StringName("roll_"+NAMES[di]))
		await capture(segment+"_roll0")
		for f in range(1,8):
			var budget:=45
			while lab.player.action_kind=="roll" and lab.player.action_frame<f and budget>0:
				await frames(1);budget-=1
			check("observed_roll_frame_"+NAMES[di]+str(f),lab.player.action_kind=="roll" and lab.player.action_frame==f)
			await capture(segment+"_roll"+str(f))
		await frames(12)
		var seen:Array=[];var continuous:=true
		for i in range(offset,trace.size()):
			var item:Dictionary=trace[i]
			if item.action_kind=="roll" and item.action_frame not in seen:seen.append(item.action_frame)
			if i>offset:
				var prev:Dictionary=trace[i-1]
				continuous=continuous and Vector2(item.position[0],item.position[1]).distance_to(Vector2(prev.position[0],prev.position[1]))<=180.0*float(item.tick-prev.tick)/60.0+0.01
		check("all8poses_ordered_"+NAMES[di],seen==[0,1,2,3,4,5,6,7],{"seen":seen})
		check("swept_continuous_57px_"+NAMES[di],continuous and lab.player.position.distance_to(start+DIRECTIONS[di]*57.6)<0.04,{"actual_distance":lab.player.ability_distance})
		var new_contacts:=contacts.slice(contact_offset)
		check("one_real_landing_contact_on_pose6_"+NAMES[di],new_contacts.size()==1 and new_contacts[0].player_action_frame==6 and new_contacts[0].player_animation=="roll_"+NAMES[di],{"contacts":new_contacts})
		check("landing_control_not_lethal_or_scored_"+NAMES[di],target.health==1 and target.hits_received==1 and target.stun_remaining>0 and lab.score==0 and lab.combat.damage_events==1)
		check("recovery_cooldown_masks_"+NAMES[di],lab.player.action_kind.is_empty() and lab.player.ability_cooldown>0 and not lab.player.use_ability() and lab.player.collision_layer==2 and lab.player.collision_mask==1)
		# Real WORLD return follows the finite own recovery without a fixture reset.
		key(MOVEMENT_KEYS[di],true);await frames(2);key(MOVEMENT_KEYS[di],false);await frames(1)
		await capture(segment+"_world_after")
		check("world_return_"+NAMES[di],lab.player.sprite.animation==StringName("idle_"+NAMES[di]))
		await frames(55)
		check("cooldown_recovers_"+NAMES[di],lab.player.ability_cooldown==0)
	segment="wall"
	await roll_fixture(2,false)
	var wall:=StaticBody2D.new();wall.collision_layer=1
	var shape:=CollisionShape2D.new();var rectangle:=RectangleShape2D.new();rectangle.size=Vector2(4,64);shape.shape=rectangle;wall.add_child(shape);wall.position=lab.player.position+Vector2(25,-7);lab.add_child(wall);await frames(2)
	var start:Vector2=lab.player.position
	await tap(KEY_F);await frames(38)
	check("wall_blocks_swept_roll_no_tunnel",lab.player.position.x<wall.position.x and lab.player.ability_distance>0 and lab.player.ability_distance<20 and lab.combat.damage_events==0)
	await capture("wall_blocks_roll");wall.queue_free();await frames(2)
	for reason in ["cancel","revoke","reopen","replace","hurt","death"]:
		await roll_fixture(2,false);segment="interrupt_"+reason
		await tap(KEY_F);await frames(8)
		check(reason+":inside_actual_roll",lab.player.action_kind=="roll" and lab.player.ability_distance>0)
		start=lab.player.position
		if reason=="cancel":await tap(KEY_C)
		if reason=="revoke":lab.scene_policy.invalidate()
		if reason=="reopen":lab.scene_policy.open("ryzhik_training")
		if reason=="replace":
			var replacement=preload("res://scripts/systems/character_scene_policy.gd").new();replacement.open("ryzhik_training");lab.player.scene_policy=replacement
		if reason=="hurt":lab.player.health=2;lab.player.receive_hit(1,0.0,900,lab.enemies[0])
		if reason=="death":lab.player.receive_hit(1,0.0,901,lab.enemies[0])
		await frames(12)
		check(reason+":stops_motion_contact_once",lab.player.position.distance_to(start)<0.001 and lab.player.action_kind!="roll" and lab.combat.attacks.is_empty() and lab.combat.damage_events==0 and lab.score==0)
		if reason=="death":check("own_death_no_immunity",lab.state=="dead" and lab.player.health==0 and lab.player.sprite.animation==&"fall_right")
		if reason=="replace":lab.player.scene_policy=lab.scene_policy
		if reason in ["revoke","reopen"]:lab.scene_policy.open("ryzhik_training")
		await tap(KEY_R)
		check(reason+":restart_resets_cost",lab.state=="playing" and lab.player.health==1 and lab.player.ability_cooldown==0 and lab.player.action_kind.is_empty())
	# Production incoming Core overlaps in three actual roll phases; initial
	# opponents are placed before F, not teleported into a measured action.
	for phase_index in 3:
		for fatal in [false,true]:
			var target:=await roll_fixture(2,false)
			segment="Core_incoming_"+str(phase_index)+("_fatal" if fatal else "_hurt")
			target.position=lab.player.position+Vector2([20.0,30.0,43.0][phase_index],0)
			lab.player.health=1 if fatal else 2
			await frames(2);await tap(KEY_F)
			while lab.player.action_elapsed<float([0.03,0.20,0.44][phase_index]):await frames(1)
			var clock_before:float=lab.player.action_elapsed
			target.locked_aim=(lab.player.position-target.position).normalized()
			var incoming:int=lab.combat.start_melee(target,"enemy",target.locked_aim,lab.config.attacks.enemy_melee)
			await frames(1)
			var hits:=contacts.filter(func(item:Dictionary):return item.segment==segment and item.target_is_player)
			check(segment+":real_Core_damage_no_immunity",hits.size()==1 and lab.player.health==(0 if fatal else 1) and lab.player.hits_received==1 and lab.combat.defended_events.is_empty(),{"clock_before":clock_before,"incoming":incoming})
			check(segment+":actual_enemy_attack_pose",String(target.sprite.animation).begins_with("reaction_attack_") and target.attack_id==incoming)
			check(segment+":own_hurt_or_fall_replaces_roll",lab.player.action_kind==("fall" if fatal else "hit") and lab.player.sprite.animation==StringName(("fall_" if fatal else "hit_")+"right"))
			await capture(segment+"_actual_contact")
			var distance:float=lab.player.ability_distance
			await frames(12)
			check(segment+":no_ghost_motion_or_repeated_incoming",lab.player.ability_distance==distance and lab.player.hits_received==1 and lab.player.action_kind!="roll" and lab.score==0)
			await tap(KEY_R)
			check(segment+":restart_clears_real_receipts",lab.player.health==1 and lab.player.hits_received==0 and lab.combat.receipts.is_empty() and lab.player.ability_cooldown==0)
	# All three permitted own finishers use genuinely Input-earned baseline
	# shove control. AI starts disabled for initial placement, then the actual
	# stunned NPC clock/motion/reactions run through death; no injected stun.
	var finisher_outcomes:Dictionary={}
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		root.get_node("OptionsStore").set_value(&"decals",true,false)
		for di in 4:
			for category in ["unarmed","blunt","environmental"]:
				var target:=await roll_fixture(di,false)
				segment="finisher_"+str(reduced)+"_"+category+"_"+NAMES[di]
				target.position=lab.player.position+DIRECTIONS[di]*20.0
				lab.training_bench.position=target.position+DIRECTIONS[di]*24.0
				lab.training_bench.set_meta("finisher_enabled",category=="environmental")
				check(segment+":allowed_tool",lab.select_equipment({"unarmed":0,"blunt":1,"environmental":4}[category]))
				await frames(2);await tap(KEY_SPACE)
				var budget:=35
				while target.hits_received==0 and budget>0:await frames(1);budget-=1
				check(segment+":actual_Input_shove_earned_stun",target.health==1 and target.hits_received==1 and target.state=="stunned")
				target.set_physics_process(true)
				while not lab.player.action_kind.is_empty() and budget>0:await frames(1);budget-=1
				await tap(KEY_V)
				check(segment+":own_windup_and_real_reaction",lab.player.action_kind=="finish_"+category and target.state=="finisher_reaction" and target.sprite.frame==0)
				await capture(segment+"_windup")
				budget=65
				while lab.player.action_kind=="finish_"+category and lab.player.action_frame<1 and budget>0:await frames(1);budget-=1
				var fin_contacts:=contacts.filter(func(item:Dictionary):return item.segment==segment and item.get("finisher",false))
				check(segment+":one_Core_contact_on_own_frame1",fin_contacts.size()==1 and fin_contacts[0].player_frame==1 and fin_contacts[0].player_animation=="finish_"+category+"_"+NAMES[di])
				check(segment+":NPC_dead_contact_then_once_reward",target.health==0 and target.state=="dead" and target.sprite.frame==1 and target.hits_received==2 and lab.score==100)
				await capture(segment+"_contact")
				await frames(9)
				check(segment+":NPC_own_corpse2",target.state=="dead" and target.sprite.frame==2)
				await capture(segment+"_corpse_recovery")
				await frames(45)
				check(segment+":no_repeat_damage_score_or_job",target.hits_received==2 and lab.score==100 and lab.combat.finishers.is_empty() and not lab.player.try_finisher())
				var outcome:=[target.health,target.hits_received,lab.score,lab.combat.damage_events,lab.player.health,lab.combat.finishers.size()]
				var route:String=NAMES[di]+"_"+String(category)
				if not reduced:finisher_outcomes[route]=outcome
				else:check(segment+":Full_Reduced_same_once_health_score",finisher_outcomes[route]==outcome,{"Full":finisher_outcomes[route],"Reduced":outcome})
	await roll_fixture(2,false);segment="options_pause"
	await tap(KEY_F);await frames(8);lab._set_options_visible(true)
	var clock:float=lab.player.action_elapsed;start=lab.player.position;var cost:float=lab.player.ability_cooldown
	await frames(12)
	check("pause_freezes_clock_cost_motion",lab.player.action_elapsed==clock and lab.player.position==start and lab.player.ability_cooldown==cost)
	lab._set_options_visible(false);await frames(36)
	check("resume_finishes_finite_roll",lab.player.action_kind.is_empty() and absf(lab.player.ability_distance-57.6)<0.04)
	var overlay_proofs:Array=[]
	var outcomes:Array=[]
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false);root.get_node("OptionsStore").set_value(&"decals",not reduced,false);root.get_node("OptionsStore").set_value(&"shake",0 if reduced else 100,false);root.get_node("OptionsStore").set_value(&"flashes",not reduced,false)
		await roll_fixture(2);segment="settings_"+str(reduced);await tap(KEY_F);await frames(38)
		outcomes.append([lab.player.health,lab.score,lab.combat.damage_events,lab.enemies[0].health,lab.enemies[0].hits_received,snappedf(lab.player.ability_distance,0.01)])
	check("Full_Reduced_same_combat_logic",outcomes[0]==outcomes[1])
	# Real nonfatal Core damage creates a persistent clothing decal. Wait out
	# hurt, then roll UP without restarting/clearing the real effect pool.
	root.get_node("OptionsStore").set_value(&"reduced_gore",false,false)
	root.get_node("OptionsStore").set_value(&"decals",true,false)
	root.get_node("OptionsStore").set_value(&"shake",0,false)
	root.get_node("OptionsStore").set_value(&"flashes",false,false)
	var source:=await roll_fixture(3,false)
	segment="persistent_blood_UP_roll"
	source.position=lab.player.position+Vector2(20,0)
	source.locked_aim=Vector2.LEFT
	lab.player.health=2 # Declared nonfatal test durability, not a story grant.
	await frames(2)
	var blood_attack:int=lab.combat.start_melee(source,"enemy",Vector2.LEFT,lab.config.attacks.enemy_melee)
	await frames(1)
	check("clothing_case_real_nonfatal_Core_contact",lab.player.health==1 and lab.player.hits_received==1 and lab.combat.damage_events==1 and source.attack_id==blood_attack)
	await frames(15)
	check("hurt_ends_without_restart_or_clearing_decals",lab.player.action_kind.is_empty() and lab.player.ability_cooldown==0 and lab.combat.impact.decals.any(func(entry:Dictionary):return entry.get("actor")==lab.player and entry.column in [6,7]))
	await tap(KEY_F)
	check("injured_player_can_roll_without_immunity",lab.player.action_kind=="roll" and lab.player.health==1 and lab.player.hits_received==1)
	for f in range(8):
		var budget:=45
		while lab.player.action_kind=="roll" and lab.player.action_frame<f and budget>0:await frames(1);budget-=1
		await frames(1) # The live effect process follows this pose, not a stale hurt socket.
		await capture("persistent_blood_UP_roll"+str(f))
		var blood:Array=lab.combat.impact.decals.filter(func(entry:Dictionary):return entry.get("actor")==lab.player and entry.column in [6,7])
		var expected:Vector2=lab.player.global_position+preload("res://scripts/actors/polish_frames.gd").clothing_offset(lab.player.sprite)
		var t:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
		var live_at:Vector2=blood[0].at if not blood.is_empty() else Vector2.INF
		check("actual_blood_tracks_own_UP_pose"+str(f),lab.player.action_kind=="roll" and lab.player.action_frame==f and t.get_meta("source_kind","")=="roll" and not blood.is_empty() and live_at.distance_to(expected)<=3.2)
		var socket:Vector2=t.get_meta("clothing_socket",Vector2.INF)
		overlay_proofs.append({"tick":Engine.get_physics_frames(),"animation":String(lab.player.sprite.animation),"frame":lab.player.sprite.frame,"source_column":t.get_meta("source_column",-1),"clothing_socket":[socket.x,socket.y],"world_anchor":[expected.x,expected.y],"live_decal_at":[live_at.x,live_at.y],"remaining_ttl":blood[0].ttl if not blood.is_empty() else 0,"renderer":DisplayServer.get_name()})
	await frames(10)
	check("blood_case_has_no_ghost_damage_or_score",lab.player.health==1 and lab.player.hits_received==1 and lab.combat.damage_events==1 and lab.score==0)
	await tap(KEY_R)
	check("restart_clears_real_clothing_decal",lab.combat.impact.decals.is_empty() and lab.player.hits_received==0 and lab.player.health==1)
	await capture("ryzhik_ready_after_restart")
	var failed:=checks.filter(func(item:Dictionary):return not item.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);file.store_string(JSON.stringify({"schema":1,"scope":"RYZHIK_ROLL_COMPONENT_ONLY","passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"phase_approval":false,"checks":checks,"trace":trace,"captures":captures,"contacts":contacts,"clothing_overlay":overlay_proofs,"not_tested":["full sevenhero finisher/audio/NPC matrix","actual host FPS","hardware input latency","native Windows","subjective listening","full P06"]},"  "));file.close()
	print("RESULT P06_RYZHIK passed=%d failed=%d"%[checks.size()-failed,failed]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
