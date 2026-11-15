extends "res://tests/gabar_combat_replay.gd"
## Input moves the existing registered bench; NPC damage requires its real sweep.
var object_trace: Array[Dictionary] = []

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
			var actor_start: Vector2 = lab.player.position
			var object_start: Vector2 = lab.training_bench.position
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
			root.remove_child(lab);lab.queue_free();await process_frame;lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact)
		else:
			lab.player.scene_policy=lab.scene_policy;lab.scene_policy.open("tega_training");await tap(KEY_R)
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
	# Existing finisher system, earned vulnerability, own contact drawings.
	for di in 4:
		for category in ["unarmed","blunt","environmental"]:
			var target := await setup(di,false);segment="finisher_"+category+"_"+NAMES[di]
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
	await setup(2,false);await capture("tega_after_restart")
	var failed:=checks.filter(func(e:Dictionary):return not e.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"TEGA_ENVIRONMENT_COMPONENT_ONLY","phase_approval":false,"passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"checks":checks,"trace":trace,"object_trace":object_trace,"contacts":contacts,"captures":captures,"not_tested":["all7 unique audio and NPC matrix","actual host FPS","hardware input latency","native Windows","subjective listening","full P06"]},"  "));file.close()
	print("RESULT P06_TEGA passed=%d failed=%d"%[checks.size()-failed,failed]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)

func make_wall(at: Vector2, size: Vector2) -> StaticBody2D:
	var wall:=StaticBody2D.new();wall.position=at;wall.collision_layer=1
	var shape:=CollisionShape2D.new();var rectangle:=RectangleShape2D.new();rectangle.size=size;shape.shape=rectangle;wall.add_child(shape);lab.add_child(wall)
	return wall
