extends "res://tests/gabar_combat_replay.gd"
## Input moves the existing registered bench; NPC damage requires its real sweep.
var object_trace: Array[Dictionary] = []
const MOVE_KEYS := [KEY_S,KEY_A,KEY_D,KEY_W]
var foot_callback_mode := ""

func on_audio(cue: StringName, _at: Vector2) -> void:
	if cue != &"impact_unarmed_metal" or foot_callback_mode.is_empty(): return
	var mode := foot_callback_mode
	foot_callback_mode = ""
	if mode=="cancel": lab.player.cancel_action()
	if mode=="revoke": lab.scene_policy.invalidate()
	if mode=="reset": lab.combat.reset()
	if mode=="disabled": lab.training_bench.set_meta("finisher_enabled",false)
	if mode=="free": lab.training_bench.free()
	if mode=="direct_cancel": lab.combat.environment_kicks.cancel(lab.player)
	if mode=="unregistered": lab.combat.environments.erase("training_bench")
	if mode=="replace":
		var replacement:=StaticBody2D.new();lab.add_child(replacement);lab.combat.register_environment("training_bench",replacement);replacement.queue_free()

func check(label: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":label,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_TEGA "+label)

func frames(count: int) -> void:
	for i in count:
		await super.frames(1)
		if trace_enabled and is_instance_valid(lab.training_bench):
			object_trace.append({"segment":segment,"tick":Engine.get_physics_frames(),"object":[lab.training_bench.position.x,lab.training_bench.position.y],"mask":lab.training_bench.collision_mask,"jobs":lab.combat.environment_kicks.jobs.size(),"action_frame":lab.player.action_frame})

func setup(di: int, with_target := true) -> CharacterBody2D:
	segment = "setup_"+NAMES[di]
	lab.reset_encounter()
	lab.auto_retry = false
	lab.player.position = Vector2(280,240)
	lab.player.set_aim(DIRECTIONS[di])
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(540,100)
	lab.training_bench.position = lab.player.position+DIRECTIONS[di]*28.0
	lab.training_bench.set_meta("finisher_enabled",true)
	lab.combat.register_environment("training_bench",lab.training_bench)
	var target: CharacterBody2D = lab.enemies[0]
	if with_target: target.position = lab.training_bench.position+DIRECTIONS[di]*34.0
	await frames(2)
	return target

func run() -> void:
	output = OS.get_environment("AYAY_P06_TEGA_OUTPUT")
	headless = DisplayServer.get_name()=="headless"
	if output.is_empty():
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size = Vector2i(640,360)
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	root.get_node("OptionsStore").set_value(&"shake",0,false)
	lab = Lab.new(); root.add_child(lab); current_scene = lab
	await frames(2); await tap(KEY_6)
	check("Input_selects_registered_Tega",lab.player.actor_id=="tega" and lab.player.prepared_ability=="environment_kick")
	if lab.player.actor_id != "tega":
		preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
		return
	lab.auto_retry = false
	lab.combat.contact_committed.connect(on_contact)
	lab.audio_event.connect(on_audio)
	trace_enabled = true
	var atlas: SpriteFrames = lab.player.sprite.sprite_frames
	var all_own := true
	for name in atlas.get_animation_names():
		for i in atlas.get_frame_count(name):
			var t := atlas.get_frame_texture(name,i)
			all_own = all_own and t.get_meta("character_id","")=="tega" and t.has_meta("clothing_socket")
	check("all56_own_clips_and96_clothing_anchors",atlas.get_animation_names().size()==56 and all_own)
	check("speed92_no_cannon_or_ranged",lab.player.move_speed==92 and not lab.player.attack_ranged())
	for category in ["sharp","firearm"]: check("latent_"+category+"_denied",not lab.player.can_use_finisher(category))
	var outcomes: Dictionary = {}
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		for di in 4:
			var target := await setup(di)
			segment = "object_hit_"+str(reduced)+"_"+NAMES[di]
			key(MOVE_KEYS[di],true); await frames(2); key(MOVE_KEYS[di],false); await frames(1)
			check(segment+":actual_own_walk_to_idle",lab.player.sprite.animation==StringName("idle_"+NAMES[di]))
			var actor_start: Vector2 = lab.player.position
			var object_start: Vector2 = lab.training_bench.position
			var cross: Vector2 = DIRECTIONS[di].orthogonal()*20.0
			check(segment+":original_object_blocks_LOS",not lab.combat.clear_line(object_start-cross,object_start+cross))
			var start_index := trace.size()
			await capture(segment+"_world")
			await tap(KEY_F)
			check(segment+":own_windup_no_early_damage",lab.player.action_kind=="special" and lab.player.action_frame==0 and target.hits_received==0)
			await capture(segment+"_windup")
			var budget := 40
			while target.hits_received==0 and budget>0: await frames(1); budget-=1
			var hit := contacts.filter(func(e: Dictionary): return e.segment==segment and not e.target_is_player)
			var collisions: Array = lab.combat.environment_kicks.history.filter(func(e: Dictionary): return e.stage=="object_collision")
			check(segment+":real_object_collision_and_Core_contact",hit.size()==1 and collisions.size()==1 and collisions[0].collider==target.get_instance_id() and hit[0].id==collisions[0].id)
			check(segment+":contact_pose1_and_NPC_death",target.health==0 and target.hits_received==1 and hit.size()==1 and hit[0].player_action_frame==1 and hit[0].player_animation=="special_"+NAMES[di] and target.state=="dead")
			check(segment+":physical_object_and_actor_travel",lab.training_bench.position.distance_to(object_start)>3 and lab.player.position.distance_to(actor_start)>3 and (lab.training_bench.position-lab.player.position).distance_to(object_start-actor_start)<0.02)
			check(segment+":object_movement_opens_real_LOS",lab.combat.clear_line(object_start-cross,object_start+cross))
			check(segment+":original_masks_restored",lab.training_bench.collision_mask==6 and lab.training_bench.get_collision_exceptions().is_empty() and lab.player.collision_mask==1 and lab.player.get_collision_exceptions().is_empty())
			await capture(segment+"_contact")
			await frames(45)
			var phases: Array = []
			for item in trace.slice(start_index):
				if item.action_kind=="special" and item.action_frame not in phases: phases.append(item.action_frame)
			check(segment+":ordered_recovery_and_once",phases==[0,1,2] and target.hits_received==1 and lab.combat.damage_events==1 and lab.score==0 and lab.player.action_kind.is_empty() and lab.combat.environment_kicks.jobs.is_empty())
			check(segment+":finite_cooldown",lab.player.ability_cooldown>0 and not lab.player.use_ability())
			await capture(segment+"_recovered")
			var result := [lab.player.health,target.health,target.hits_received,lab.combat.damage_events,lab.score,snappedf(lab.player.ability_distance,0.01)]
			if not reduced: outcomes[NAMES[di]] = result
			else: check(segment+":Full_Reduced_identical",outcomes[NAMES[di]]==result,{"Full":outcomes[NAMES[di]],"Reduced":result})
			await tap(KEY_R)
			check(segment+":restart_restores_original_object_transform",lab.training_bench.position==object_start and lab.player.ability_cooldown==0 and lab.combat.environment_kicks.history.is_empty() and lab.combat.receipts.is_empty())
	for reason in ["far","behind","side","disabled","unregistered","wall"]:
		await setup(2,false); segment = "deny_"+reason
		var wall: StaticBody2D
		if reason=="far": lab.training_bench.position += Vector2(40,0)
		if reason=="behind": lab.training_bench.position = lab.player.position-Vector2(28,0)
		if reason=="side": lab.training_bench.position = lab.player.position+Vector2(0,28)
		if reason=="disabled": lab.training_bench.set_meta("finisher_enabled",false)
		if reason=="unregistered": lab.combat.environments.erase("training_bench")
		if reason=="wall":
			wall = make_wall(lab.player.position+Vector2(12,-6),Vector2(2,20))
		await frames(2); await tap(KEY_F)
		check(segment+":no_cost_no_motion_no_damage",lab.player.ability_cooldown==0 and lab.player.ability_uses==0 and lab.combat.environment_kicks.jobs.is_empty() and lab.player.action_kind.is_empty() and lab.combat.damage_events==0)
		if wall!=null: wall.queue_free(); await frames(2)
	for reason in ["cancel","disabled","unregistered","replaced_object","revoke","reopen","replace_policy","hurt","death","freed_object"]:
		await setup(2,false); segment = "interrupt_"+reason
		await tap(KEY_F)
		var before: Vector2 = lab.training_bench.position
		if reason=="cancel": await tap(KEY_C)
		if reason=="disabled": lab.training_bench.set_meta("finisher_enabled",false)
		if reason=="unregistered": lab.combat.environments.erase("training_bench")
		if reason=="replaced_object":
			var replacement := StaticBody2D.new();lab.add_child(replacement);lab.combat.register_environment("training_bench",replacement);replacement.queue_free()
		if reason=="revoke": lab.scene_policy.invalidate()
		if reason=="reopen": lab.scene_policy.open("tega_training")
		if reason=="replace_policy":
			var policy := preload("res://scripts/systems/character_scene_policy.gd").new();policy.open("tega_training");lab.player.scene_policy=policy
		if reason=="hurt": lab.player.health=2; lab.player.receive_hit(1,0.0,999,lab.enemies[0])
		if reason=="death": lab.player.receive_hit(1,0.0,999,lab.enemies[0])
		if reason=="freed_object": lab.training_bench.queue_free()
		await frames(40)
		check(segment+":no_stale_motion_or_damage",lab.combat.environment_kicks.jobs.is_empty() and lab.combat.damage_events==0 and lab.score==0 and (not is_instance_valid(lab.training_bench) or lab.training_bench.position==before))
		if reason=="freed_object":
			# This case intentionally frees the actual registered body; rebuild the
			# scene only after verifying no stale access, never during measured F.
			root.remove_child(lab);lab.queue_free();await process_frame;lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
		else:
			lab.player.scene_policy=lab.scene_policy;lab.scene_policy.open("tega_training");await tap(KEY_R)
	for mode in ["cancel","revoke","reset","disabled","free","direct_cancel","unregistered","replace"]:
		await setup(2,false);segment="foot_callback_"+mode
		var object_start:Vector2=lab.training_bench.position
		var actor_start:Vector2=lab.player.position
		foot_callback_mode=mode
		await tap(KEY_F);await frames(30)
		check(segment+":callback_really_executed",foot_callback_mode.is_empty())
		check(segment+":no_stale_first_active_step",lab.player.position==actor_start and (not is_instance_valid(lab.training_bench) or lab.training_bench.position==object_start) and lab.combat.environment_kicks.jobs.is_empty() and lab.combat.damage_events==0)
		if mode=="free":
			root.remove_child(lab);lab.queue_free();await process_frame;lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
		else:lab.scene_policy.open("tega_training");await tap(KEY_R)
	for reason in ["cancel","disabled","revoke"]:
		await setup(2,false);segment="active_interrupt_"+reason
		await tap(KEY_F)
		while lab.player.action_elapsed<0.24:await frames(1)
		var before:Vector2=lab.training_bench.position
		var distance:float=lab.player.ability_distance
		check(segment+":actual_active_motion",lab.player.action_frame==1 and distance>0)
		if reason=="cancel":await tap(KEY_C)
		if reason=="disabled":lab.training_bench.set_meta("finisher_enabled",false)
		if reason=="revoke":lab.scene_policy.invalidate()
		await frames(25)
		check(segment+":stops_remaining_sweep",lab.training_bench.position==before and lab.player.ability_distance==distance and lab.combat.environment_kicks.jobs.is_empty() and lab.combat.damage_events==0)
		lab.scene_policy.open("tega_training");await tap(KEY_R)
	await setup(2,false);segment="wall_stops_object"
	var wall := make_wall(lab.training_bench.position+Vector2(27,-6),Vector2(4,30))
	await frames(2);await tap(KEY_F);await frames(40)
	check("wall_stops_real_object_no_tunnel",lab.player.ability_distance>0 and lab.player.ability_distance<20 and lab.training_bench.position.x<wall.position.x and lab.combat.damage_events==0)
	await capture(segment);wall.queue_free();await frames(2)
	await setup(2,false);segment="options_pause"
	await tap(KEY_F);await frames(12);lab._set_options_visible(true)
	var object_before: Vector2=lab.training_bench.position;var clock:float=lab.player.action_elapsed;var cost:float=lab.player.ability_cooldown
	await frames(12)
	check("options_freeze_object_clock_cost",lab.training_bench.position==object_before and lab.player.action_elapsed==clock and lab.player.ability_cooldown==cost)
	lab._set_options_visible(false);await frames(40)
	check("resume_finite_bounded_shove",lab.player.action_kind.is_empty() and lab.player.ability_distance>30 and lab.player.ability_distance<=37.81)
	# Hostile Core melee is applied before the pending object's same-tick move.
	for phase_index in 3:
		for fatal in [false,true]:
			var target:=await setup(2,false)
			segment="incoming_"+str(phase_index)+("_fatal" if fatal else "_hurt")
			target.position=lab.player.position+Vector2([0.0,12.6,37.8][phase_index],20)
			target.locked_aim=Vector2.UP
			lab.player.health=1 if fatal else 2
			await frames(2);await tap(KEY_F)
			while lab.player.action_elapsed<float([0.03,0.24,0.43][phase_index]):await frames(1)
			var clock_before:float=lab.player.action_elapsed
			var object_before_hit:Vector2=lab.training_bench.position
			var incoming:int=lab.combat.start_melee(target,"enemy",Vector2.UP,lab.config.attacks.enemy_melee)
			await frames(1)
			var hit:=contacts.filter(func(e:Dictionary):return e.segment==segment and e.target_is_player)
			check(segment+":real_incoming_Core_contact",hit.size()==1 and lab.player.health==(0 if fatal else 1) and lab.player.hits_received==1 and target.attack_id==incoming,{"clock_before":clock_before})
			check(segment+":no_same_tick_posthumous_object_motion",lab.training_bench.position==object_before_hit and lab.combat.environment_kicks.jobs.is_empty() and lab.combat.damage_events==1)
			check(segment+":own_hurt_or_death_replaces_kick",lab.player.action_kind==("fall" if fatal else "hit") and lab.player.sprite.animation==StringName(("fall_" if fatal else "hit_")+"right") and String(target.sprite.animation).begins_with("reaction_attack_"))
			await capture(segment+"_contact");await frames(25)
			check(segment+":no_ghost_damage_or_movement",lab.training_bench.position==object_before_hit and lab.player.hits_received==1 and lab.score==0)
			await tap(KEY_R)
			check(segment+":restart_clears_once_receipts",lab.player.health==1 and lab.player.hits_received==0 and lab.combat.receipts.is_empty() and lab.player.ability_cooldown==0)
	# Persistent real clothing blood survives hurt into the own special keyposes.
	root.get_node("OptionsStore").set_value(&"reduced_gore",false,false)
	root.get_node("OptionsStore").set_value(&"decals",true,false)
	root.get_node("OptionsStore").set_value(&"flashes",false,false)
	var overlay_proofs:Array=[]
	for di in 4:
		var enemy:=await setup(di,false);segment="clothing_"+NAMES[di]
		key(MOVE_KEYS[di],true);await frames(2);key(MOVE_KEYS[di],false);await frames(1)
		enemy.position=lab.player.position+DIRECTIONS[di].orthogonal()*20
		enemy.locked_aim=-DIRECTIONS[di].orthogonal()
		lab.player.health=2
		await frames(2)
		lab.combat.start_melee(enemy,"enemy",enemy.locked_aim,lab.config.attacks.enemy_melee)
		await frames(1);await capture(segment+"_real_hurt")
		check(segment+":real_nonfatal_blood_without_reset",lab.player.health==1 and lab.player.hits_received==1 and lab.combat.damage_events==1)
		await frames(15);await tap(KEY_F)
		for pose in 3:
			var budget:=45
			while lab.player.action_kind=="special" and lab.player.action_frame<pose and budget>0:await frames(1);budget-=1
			await frames(1)
			var blood:Array=lab.combat.impact.decals.filter(func(e:Dictionary):return e.get("actor")==lab.player and e.column in [6,7])
			var expected:Vector2=lab.player.global_position+preload("res://scripts/actors/polish_frames.gd").clothing_offset(lab.player.sprite)
			var live_at:Vector2=blood[0].at if not blood.is_empty() else Vector2.INF
			check(segment+":clothing_tracks_special_pose"+str(pose),lab.player.action_kind=="special" and lab.player.action_frame==pose and not blood.is_empty() and live_at.distance_to(expected)<=3.6)
			var texture:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
			var socket:Vector2=texture.get_meta("clothing_socket",Vector2.INF)
			overlay_proofs.append({"direction":NAMES[di],"pose":pose,"tick":Engine.get_physics_frames(),"socket":[socket.x,socket.y],"expected":[expected.x,expected.y],"actual":[live_at.x,live_at.y],"ttl":blood[0].ttl if not blood.is_empty() else 0})
			await capture(segment+"_special"+str(pose))
		await tap(KEY_R)
		check(segment+":R_clears_real_clothing",lab.combat.impact.decals.is_empty() and lab.player.hits_received==0)
	# Existing finisher system, earned vulnerability, own contact drawings.
	var finisher_outcomes: Dictionary = {}
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		for di in 4:
			for category in ["unarmed","blunt","environmental"]:
				var target := await setup(di,false);segment="finisher_"+str(reduced)+"_"+category+"_"+NAMES[di]
				target.position=lab.player.position+DIRECTIONS[di]*20.0
				lab.training_bench.position=target.position+DIRECTIONS[di]*24.0
				lab.training_bench.set_meta("finisher_enabled",category=="environmental")
				lab.select_equipment({"unarmed":0,"blunt":1,"environmental":4}[category])
				await frames(2);await tap(KEY_SPACE)
				var budget:=40
				while target.hits_received==0 and budget>0:await frames(1);budget-=1
				check(segment+":earned_stun",target.hits_received==1 and target.health==1 and target.state=="stunned")
				target.set_physics_process(true)
				while not lab.player.action_kind.is_empty() and budget>0:await frames(1);budget-=1
				await tap(KEY_V);await capture(segment+"_windup")
				budget=65
				while target.health>0 and budget>0:await frames(1);budget-=1
				var committed:=contacts.filter(func(e:Dictionary):return e.segment==segment and e.finisher)
				check(segment+":once_own_contact1_NPC_reaction1",committed.size()==1 and committed[0].player_frame==1 and committed[0].player_animation=="finish_"+category+"_"+NAMES[di] and target.state=="dead" and target.sprite.frame==1 and lab.score==100)
				await capture(segment+"_contact");await frames(10)
				check(segment+":corpse2",target.sprite.frame==2)
				await capture(segment+"_corpse");await frames(45)
				check(segment+":no_duplicate_reward",target.hits_received==2 and lab.combat.damage_events==2 and lab.score==100 and lab.combat.finishers.is_empty() and not lab.player.try_finisher())
				var route:String=category+"_"+NAMES[di]
				var result:=[target.health,target.hits_received,lab.combat.damage_events,lab.score,lab.player.health]
				if not reduced:finisher_outcomes[route]=result
				else:check(segment+":Full_Reduced_identical",finisher_outcomes[route]==result)
	await setup(2,false);await capture("tega_after_restart")
	var failed:=checks.filter(func(e:Dictionary):return not e.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"TEGA_ENVIRONMENT_COMPONENT_ONLY","phase_approval":false,"passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"checks":checks,"trace":trace,"object_trace":object_trace,"contacts":contacts,"captures":captures,"clothing_overlay":overlay_proofs,"not_tested":["all7 unique audio and NPC matrix","actual host FPS","hardware input latency","native Windows","subjective listening","full P06"]},"  "));file.close()
	print("RESULT P06_TEGA passed=%d failed=%d"%[checks.size()-failed,failed]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)

func make_wall(at: Vector2, size: Vector2) -> StaticBody2D:
	var wall:=StaticBody2D.new();wall.position=at;wall.collision_layer=1
	var shape:=CollisionShape2D.new();var rectangle:=RectangleShape2D.new();rectangle.size=size;shape.shape=rectangle;wall.add_child(shape);lab.add_child(wall)
	return wall
