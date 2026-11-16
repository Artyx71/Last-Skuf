extends "res://tests/gabar_combat_replay.gd"
## Real registered Pasha, Input, finite ammunition and Core projectile contacts.
const MOVE_KEYS := [KEY_S,KEY_A,KEY_D,KEY_W]
class EndOfCoreObserver:
	extends Node
	var replay
	func _physics_process(_delta: float) -> void: replay.observe_after_core()
var ammo_trace: Array[Dictionary] = []
var launches: Array[Dictionary] = []
var costs: Array[Dictionary] = []
var callback_mode := ""
var callback_executed := false
var callback_new_action := false
var overlay_proofs: Array[Dictionary] = []
var impact_reset_pending := false
var impact_reset_executed := false
var wall_reset_pending := false
var wall_reset_executed := false
var wall_observe_pending := false
var wall_observation: Dictionary = {}
var input_focus_events: Array[Dictionary] = []
var movie_window_no_focus_requested := false
var despawn_target: Variant
var despawn_armed := false
var despawn_executed := false

func check(label: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":label,"passed":ok,"details":details.duplicate(true)})
	if not ok: push_error("FAIL P06_PASHA "+label)

func note_input_focus(focused: bool) -> void:
	input_focus_events.append({"focused":focused,"tick":Engine.get_physics_frames(),
		"wall_usec":Time.get_ticks_usec(),"segment":segment})

func frames(count: int) -> void:
	for i in count:
		await super.frames(1)
		# SceneTree.process_frame precedes Node._process. Observe the completed
		# presentation/HUD/garment update, rather than last frame's decal position.
		await create_timer(0.0).timeout
		if trace_enabled and is_instance_valid(lab.player) and lab.player.actor_id=="pasha":
			var p: CharacterBody2D=lab.player
			var observed_input:Vector2=Input.get_vector("move_left","move_right","move_up","move_down")
			ammo_trace.append({"segment":segment,"tick":Engine.get_physics_frames(),"ammo":p.movement_ability.ammo,
				"refill":p.movement_ability.refill_elapsed,"cooldown":p.ability_cooldown,"action":p.action_kind,
				"pose":p.sprite.frame,"jobs":lab.combat.moving_shots.jobs.size(),"bullets":lab.combat.projectiles.size(),
				"hud":lab.ranged_feedback.displayed_feedback.duplicate(true),
				"input_vector":[observed_input.x,observed_input.y],
				"run_pressed":Input.is_action_pressed("character_run"),"window_focused":root.has_focus(),
				"window_no_focus":root.get_flag(Window.FLAG_NO_FOCUS) if not headless else false})

func on_audio(cue: StringName, _at: Vector2) -> void:
	if cue==&"impact_firearm_concrete" and wall_reset_pending:
		wall_reset_pending=false;wall_reset_executed=true
		var at:Vector2=lab.player.position
		lab.combat.reset();lab.player.reset(at)
		wall_observe_pending=true
		return
	if cue==&"impact_firearm_body" and impact_reset_pending:
		impact_reset_pending=false;impact_reset_executed=true
		lab.combat.reset();lab.player.reset(Vector2(300,240))
		return
	if cue!=&"weapon_fire" or callback_mode.is_empty(): return
	var mode:=callback_mode
	callback_mode=""
	callback_executed=true
	if mode=="cancel":lab.player.cancel_action()
	if mode=="revoke":lab.scene_policy.invalidate()
	if mode=="reopen":lab.scene_policy.open("pasha_training")
	if mode=="reset":lab.combat.reset()
	if mode=="reset_new_F":
		var at:Vector2=lab.player.position
		lab.combat.reset();lab.player.reset(at)
		callback_new_action=lab.player.use_ability()
	if mode=="replace":lab.select_fixture("pasha_training")
	if mode=="foreign_strategy":lab.player.movement_ability=preload("res://scripts/abilities/moving_shot.gd").new()

func observe_after_core() -> void:
	if not wall_observe_pending:return
	wall_observe_pending=false
	wall_observation={"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,
		"flash":lab.combat.hit_flash,"at":lab.combat.last_hit_position,"ammo":lab.player.movement_ability.ammo,
		"jobs":lab.combat.moving_shots.jobs.size(),"bullets":lab.combat.projectiles.size()}

func despawn_on_finisher_contact() -> void:
	if not despawn_armed or not is_instance_valid(despawn_target):return
	if despawn_target.state!="finisher_reaction" or despawn_target.sprite.frame!=1:return
	var inside_core:=false
	for item in get_stack():
		if item.function=="_tick_finishers" and String(item.source).ends_with("combat_system.gd"):inside_core=true
	if not inside_core:return
	despawn_armed=false
	lab.enemies.erase(despawn_target)
	despawn_target.free()
	despawn_executed=not is_instance_valid(despawn_target)

func setup(di: int, target_distance := 90.0, target_health := 1) -> CharacterBody2D:
	segment="setup_"+NAMES[di]
	lab.player.scene_policy=lab.scene_policy
	if lab.scene_policy.ability_id()!="moving_shot":lab.scene_policy.open("pasha_training")
	lab.reset_encounter();lab.auto_retry=false
	# Vertical lanes use the existing open gap between authored walls. The first
	# baseline deliberately retained in reports exposed out-of-bounds targets.
	lab.player.position=[Vector2(380,200),Vector2(300,240),Vector2(300,240),Vector2(380,270)][di]
	lab.player.set_aim(DIRECTIONS[di])
	for enemy in lab.enemies:
		enemy.set_physics_process(false);enemy.position=Vector2(560,100)
	lab.training_bench.position=Vector2(480,270)
	lab.training_bench.set_meta("finisher_enabled",false)
	var target:CharacterBody2D=lab.enemies[0]
	target.position=lab.player.position+DIRECTIONS[di]*target_distance
	target.health=target_health
	target.locked_aim=-DIRECTIONS[di]
	await frames(2)
	return target

func wait_launch(budget := 30) -> bool:
	while lab.combat.moving_shots.history.is_empty() and budget>0:
		await frames(1);budget-=1
	return not lab.combat.moving_shots.history.is_empty()

func mouse_trigger(pressed: bool) -> void:
	var event:=InputEventMouseButton.new()
	event.button_index=MOUSE_BUTTON_RIGHT;event.pressed=pressed
	event.position=Vector2(450,240)
	Input.parse_input_event(event)

func remember_launches() -> void:
	for entry in lab.combat.moving_shots.history:
		var copy:Dictionary=entry.duplicate(true);copy.segment=segment;launches.append(copy)
	for entry in lab.player.movement_ability.cost_history:
		var copy:Dictionary=entry.duplicate(true);copy.segment=segment;costs.append(copy)

func run() -> void:
	output=OS.get_environment("AYAY_P06_PASHA_OUTPUT")
	headless=DisplayServer.get_name()=="headless"
	if output.is_empty():preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1);return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	# Existing WORLD replay uses this same QA-only MovieMaker window isolation.
	# Scripted Input events remain ordinary Input; never reassert dropped keys.
	if not headless and not Engine.get_write_movie_path().is_empty():
		root.set_flag(Window.FLAG_NO_FOCUS,true)
		movie_window_no_focus_requested=true
	root.focus_entered.connect(func():note_input_focus(true))
	root.focus_exited.connect(func():note_input_focus(false))
	root.get_node("OptionsStore").set_value(&"vhs",false,false)
	root.get_node("OptionsStore").set_value(&"shake",0,false)
	lab=Lab.new();root.add_child(lab);current_scene=lab
	await frames(2);await tap(KEY_7)
	check("Input_selects_registered_Pasha",lab.player.actor_id=="pasha" and lab.player.prepared_ability=="moving_shot")
	if lab.player.actor_id!="pasha":preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1);return
	lab.auto_retry=false
	lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
	var observer:=EndOfCoreObserver.new();observer.replay=self;observer.process_physics_priority=1000;root.add_child(observer)
	trace_enabled=true
	var atlas:SpriteFrames=lab.player.sprite.sprite_frames
	var own:=true
	for name in atlas.get_animation_names():
		for i in atlas.get_frame_count(name):
			var t:Texture2D=atlas.get_frame_texture(name,i)
			own=own and t.get_meta("character_id","")=="pasha" and t.has_meta("clothing_socket")
	check("all60_clips_128_own_source_drawings_clothing",own and atlas.get_animation_names().size()==60)
	check("Pasha_speed125_no_legacy_training_kit",lab.player.move_speed==125 and lab.player.kit=="escape")
	var hud_in_header:=true
	var hud_rects:Array=[]
	for widget in [lab.ranged_feedback.title,lab.ranged_feedback.detail,lab.ranged_feedback.meter]:
		var rect:Rect2=widget.get_global_rect()
		hud_rects.append([rect.position.x,rect.position.y,rect.size.x,rect.size.y])
		hud_in_header=hud_in_header and rect.end.y<=54 and rect.end.x<=640
	check("actual_ammo_HUD_rects_stay_above_arena",hud_in_header,{"rects":hud_rects})
	await setup(2,170,5);segment="actual_RMB_held_trigger"
	mouse_trigger(true);await frames(36)
	check("held_RMB_launches_only_one_round",lab.player.ability_uses==1 and lab.player.movement_ability.rounds_spent==1 and lab.shots_fired==1)
	mouse_trigger(false);await frames(2);mouse_trigger(true);await frames(12);mouse_trigger(false)
	check("released_repressed_RMB_fires_second_round",lab.player.ability_uses==2 and lab.player.movement_ability.rounds_spent==2 and lab.player.movement_ability.ammo==2)
	var outcomes:Dictionary={}
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		for di in 4:
			var target:=await setup(di)
			segment="moving_shot_"+str(reduced)+"_"+NAMES[di]
			var start:Vector2=lab.player.position
			var first_trace:=trace.size()
			var first_input_trace:=ammo_trace.size()
			key(MOVE_KEYS[di],true);key(KEY_SHIFT,true)
			await tap(KEY_F)
			check(segment+":windup_no_early_round_or_damage",lab.player.action_kind=="moving_shot" and lab.player.action_frame==0 and lab.player.movement_ability.ammo==4 and target.hits_received==0)
			check(segment+":cannot_restart_during_action",not lab.player.use_ability() and not lab.player.attack_ranged())
			await capture(segment+"_windup")
			check(segment+":actual_Core_launch",await wait_launch())
			var record:Dictionary=lab.combat.moving_shots.history[0] if not lab.combat.moving_shots.history.is_empty() else {}
			check(segment+":one_round_on_drawn_muzzle3",lab.player.movement_ability.ammo==3 and lab.player.movement_ability.rounds_spent==1 and record.get("source_pose")==3 and lab.player.sprite.frame==3)
			check(segment+":muzzle_tracks_current_drawn_gun",not record.is_empty() and Vector2(record.muzzle[0],record.muzzle[1]).distance_to(lab.player.visual_muzzle())<0.01)
			await capture(segment+"_launch")
			await frames(24)
			var actual_held:=true
			for i in range(first_input_trace,ammo_trace.size()):
				var observed:Dictionary=ammo_trace[i]
				actual_held=actual_held and observed.run_pressed and Vector2(observed.input_vector[0],observed.input_vector[1]).is_equal_approx(DIRECTIONS[di])
			check(segment+":actual_Input_vector_and_run_remain_held",actual_held,{"samples":ammo_trace.size()-first_input_trace,"movie_window_no_focus":movie_window_no_focus_requested})
			key(MOVE_KEYS[di],false);key(KEY_SHIFT,false)
			var phases:Array=[]
			var continuous:=true
			for i in range(first_trace,trace.size()):
				var item:Dictionary=trace[i]
				if item.action_kind=="moving_shot" and item.action_frame not in phases:phases.append(item.action_frame)
				if i>first_trace:
					var previous:Dictionary=trace[i-1]
					var step:=Vector2(item.position[0],item.position[1]).distance_to(Vector2(previous.position[0],previous.position[1]))
					continuous=continuous and step<=180.0*float(item.tick-previous.tick)/60.0+0.01
			check(segment+":all8_ordered_poses_then_held_run",phases==[0,1,2,3,4,5,6,7] and lab.player.action_kind.is_empty() and lab.player.sprite.animation==StringName("run_"+NAMES[di]),{"phases":phases})
			check(segment+":physical_run_no_teleport_or_immunity",continuous and lab.player.position.distance_to(start)>70 and lab.player.collision_layer==2 and lab.player.collision_mask==1)
			check(segment+":one_bullet_one_damage_no_score",target.hits_received==1 and target.health==0 and lab.combat.damage_events==1 and lab.score==0 and lab.shots_fired==1 and lab.combat.moving_shots.jobs.is_empty())
			await capture(segment+"_recovered")
			remember_launches()
			var outcome:=[target.health,target.hits_received,lab.combat.damage_events,lab.score,lab.player.movement_ability.ammo]
			if not reduced:outcomes[NAMES[di]]=outcome
			else:check(segment+":Full_Reduced_same_logic",outcomes[NAMES[di]]==outcome)
	# Four launches outpace passive replenishment: the HUD reflects a real empty clip.
	await setup(2,190,20);segment="finite_clip_and_refill"
	for round_index in 4:
		await tap(KEY_F)
		await frames(23)
		check("finite_round_"+str(round_index),lab.player.movement_ability.ammo==3-round_index and lab.player.movement_ability.rounds_spent==round_index+1)
	check("empty_F_and_normal_ranged_denied",not lab.player.use_ability() and not lab.player.attack_ranged() and not lab.player.can_use_finisher("firearm"))
	await frames(1)
	check("actual_HUD_shows_empty_and_recovery",lab.ranged_feedback.displayed_feedback.phase=="empty" and lab.ranged_feedback.title.text.contains("0 / 4") and lab.ranged_feedback.detail.text.contains("ПУСТО"))
	await capture("empty_clip_HUD")
	# The empty clip was earned by Input; place a nearby live target without a
	# resource reset, earn its stun, and try actual V rather than just an API query.
	var empty_target:CharacterBody2D=lab.enemies[0]
	empty_target.position=lab.player.position+Vector2(20,0)
	lab.select_equipment(3)
	var hits_before:int=empty_target.hits_received
	await frames(2);await tap(KEY_SPACE)
	var empty_budget:=35
	while not lab.player.action_kind.is_empty() and empty_budget>0:await frames(1);empty_budget-=1
	check("empty_clip_target_stun_earned_by_Input",empty_target.state=="stunned" and empty_target.hits_received==hits_before+1 and lab.player.movement_ability.ammo==0)
	await tap(KEY_V)
	check("empty_clip_Input_V_cannot_reserve_firearm_finisher",lab.combat.finishers.is_empty() and lab.player.action_kind.is_empty() and lab.player.movement_ability.rounds_spent==4 and lab.score==0)
	var before:int=lab.player.movement_ability.ammo
	await frames(60)
	check("passive_recovers_one_real_round",lab.player.movement_ability.ammo>before and lab.player.movement_ability.ammo<4)
	await capture("refill_HUD")
	await frames(180)
	check("refill_caps_at_four",lab.player.movement_ability.ammo==4 and lab.player.movement_ability.refill_elapsed==0)
	var mixed_target:=await setup(2,20)
	segment="shared_clip_shot_then_firearm_finisher"
	lab.player.set_aim(Vector2.LEFT);await tap(KEY_F)
	var mixed_budget:=30
	while not lab.player.action_kind.is_empty() and mixed_budget>0:await frames(1);mixed_budget-=1
	check("mixed_clip_actual_shot_spends_first_round",lab.player.movement_ability.ammo==3 and lab.player.movement_ability.rounds_spent==1 and mixed_target.hits_received==0)
	lab.player.set_aim(Vector2.RIGHT);lab.select_equipment(3)
	await tap(KEY_SPACE);mixed_budget=35
	while not lab.player.action_kind.is_empty() and mixed_budget>0:await frames(1);mixed_budget-=1
	check("mixed_clip_earns_target_stun",mixed_target.state=="stunned" and mixed_target.hits_received==1)
	mixed_target.set_physics_process(true);await tap(KEY_V);mixed_budget=35
	while mixed_target.health>0 and mixed_budget>0:await frames(1);mixed_budget-=1
	check("firearm_finisher_spends_same_clip_second_round_once",mixed_target.health==0 and lab.player.movement_ability.ammo==2 and lab.player.movement_ability.rounds_spent==2 and lab.score==100)
	check("shared_clip_records_two_distinct_contact_costs",lab.player.movement_ability.cost_history.size()==2 and lab.player.movement_ability.cost_history[0].reason=="moving_shot" and lab.player.movement_ability.cost_history[1].reason=="firearm_finisher")
	await capture("shared_clip_firearm_finisher")
	# MovieMaker capture() is a no-op. Preserve the actual committed pose through
	# a render boundary before the next fixture resets its actors and resources.
	await frames(2)
	# Cancelling or losing authority before contact never consumes ammunition.
	for mode in ["cancel","revoke","reopen","replace_policy","hurt","death"]:
		await setup(2);segment="before_contact_"+mode
		await tap(KEY_F)
		if mode=="cancel":await tap(KEY_C)
		if mode=="revoke":lab.scene_policy.invalidate()
		if mode=="reopen":lab.scene_policy.open("pasha_training")
		if mode=="replace_policy":
			var policy:=preload("res://scripts/systems/character_scene_policy.gd").new();policy.open("pasha_training");lab.player.scene_policy=policy
		if mode=="hurt":lab.player.health=2;lab.player.receive_hit(1,0.0,991,lab.enemies[0])
		if mode=="death":lab.player.receive_hit(1,0.0,992,lab.enemies[0])
		await frames(25)
		check(segment+":no_stale_bullet_or_round",lab.combat.moving_shots.history.is_empty() and lab.combat.projectiles.is_empty() and lab.player.movement_ability.ammo==4 and lab.player.movement_ability.rounds_spent==0)
	# Sound callbacks are external, including a legitimate reset/new F with reused id.
	for mode in ["cancel","revoke","reopen","reset","reset_new_F","replace","foreign_strategy"]:
		await setup(2);segment="audio_callback_"+mode
		callback_mode=mode;callback_executed=false;callback_new_action=false
		var epoch:int=lab.combat.encounter_epoch
		await tap(KEY_F);await frames(30)
		check(segment+":callback_executed",callback_executed)
		if mode=="reset_new_F":
			check(segment+":new_epoch_action_survives_old_callback",callback_new_action and lab.combat.encounter_epoch==epoch+1 and lab.player.movement_ability.rounds_spent==1 and lab.combat.moving_shots.history.size()==1 and lab.combat.moving_shots.history[0].epoch==epoch+1)
		else:check(segment+":no_old_launch_or_stale_write",lab.combat.moving_shots.history.is_empty() and lab.combat.damage_events==0 and lab.combat.projectiles.is_empty())
		if mode=="foreign_strategy":lab.select_fixture("pasha_training")
	await setup(2);segment="options_freeze"
	await tap(KEY_F);await wait_launch();await frames(16)
	lab._set_options_visible(true)
	var frozen:=[lab.player.movement_ability.ammo,lab.player.movement_ability.refill_elapsed,lab.player.ability_cooldown,lab.player.action_elapsed]
	await frames(15)
	check("pause_freezes_ammo_refill_action_and_cooldown",frozen==[lab.player.movement_ability.ammo,lab.player.movement_ability.refill_elapsed,lab.player.ability_cooldown,lab.player.action_elapsed] and lab.ranged_feedback.displayed_feedback.phase=="paused")
	await capture("paused_HUD");lab._set_options_visible(false);await frames(60)
	check("resume_continues_passive_refill",lab.player.movement_ability.ammo==4)
	await tap(KEY_R)
	check("R_resets_cost_HUD_jobs_and_projectiles",lab.player.movement_ability.ammo==4 and lab.player.movement_ability.rounds_spent==0 and lab.combat.moving_shots.jobs.is_empty() and lab.combat.projectiles.is_empty())
	# Actual Body2D collision constrains continuous movement during the shot.
	await setup(2,180,3);segment="wall_body_and_bullet"
	lab.player.position=Vector2(603,284);key(KEY_D,true);key(KEY_SHIFT,true)
	await tap(KEY_F);await frames(24);key(KEY_D,false);key(KEY_SHIFT,false)
	check("shot_does_not_disable_existing_wall_collision",lab.player.position.x<=612.1 and lab.player.position.x>=603 and lab.player.collision_mask==1 and lab.combat.wall_impacts>0)
	await capture("shot_wall")
	await setup(2,70,3);segment="impact_sound_reset"
	impact_reset_pending=true;impact_reset_executed=false
	await tap(KEY_F);await frames(30)
	check("impact_reset_callback_really_executed",impact_reset_executed)
	check("impact_reset_leaves_no_old_contact_or_effect_in_new_epoch",lab.combat.contact_events.is_empty() and lab.combat.receipts.is_empty() and lab.combat.damage_events==0 and lab.combat.impact.decals.is_empty(),{"contacts":lab.combat.contact_events,"decals":lab.combat.impact.decals.size(),"epoch":lab.combat.encounter_epoch})
	for distance in [10,44]:
		await setup(2,170,8);segment="wall_sound_reset_"+str(distance)
		var wall:=StaticBody2D.new();wall.position=lab.player.position+Vector2(distance,-7);wall.collision_layer=1
		var shape:=CollisionShape2D.new();var rectangle:=RectangleShape2D.new();rectangle.size=Vector2(2,16);shape.shape=rectangle;wall.add_child(shape);lab.add_child(wall)
		wall_reset_pending=true;wall_reset_executed=false;wall_observation={}
		var wall_epoch:int=lab.combat.encounter_epoch
		await frames(2);await tap(KEY_F);await frames(20)
		check(segment+":actual_wall_reset_callback",wall_reset_executed and not wall_observation.is_empty())
		check(segment+":same_tick_no_phantom_flash_or_old_bullet",not wall_observation.is_empty() and wall_observation.epoch==wall_epoch+1 and wall_observation.flash==0 and wall_observation.at==Vector2.ZERO and wall_observation.ammo==4 and wall_observation.jobs==0 and wall_observation.bullets==0,wall_observation)
		wall.queue_free();await frames(2)
	# Already launched rounds may finish after recovery, but never cross authority epochs.
	for revoke in [false,true]:
		var distant:=await setup(2,210,3)
		segment="committed_projectile_"+str(revoke)
		await tap(KEY_F);await wait_launch();await tap(KEY_C)
		if revoke:lab.scene_policy.invalidate()
		await frames(35)
		check(segment+":one_cost_not_refunded_by_cancel",lab.player.movement_ability.rounds_spent==1)
		check(segment+":live_authority_controls_delayed_contact",distant.hits_received==(0 if revoke else 1) and lab.combat.damage_events==(0 if revoke else 1) and lab.combat.projectiles.is_empty())
	# Hostile Core contacts resolve before this frame's deferred muzzle launch.
	for fatal in [false,true]:
		var enemy:=await setup(2,120)
		segment="incoming_before_launch_"+str(fatal)
		enemy.position=lab.player.position+Vector2(0,20);enemy.locked_aim=Vector2.UP
		lab.player.health=1 if fatal else 2
		await frames(2);await tap(KEY_F)
		while lab.player.action_elapsed<0.075:await frames(1)
		lab.combat.start_melee(enemy,"enemy",Vector2.UP,lab.config.attacks.enemy_melee)
		await frames(1)
		var hit:=contacts.filter(func(e:Dictionary):return e.segment==segment and e.target_is_player)
		check(segment+":real_incoming_contact_no_immunity",hit.size()==1 and lab.player.health==(0 if fatal else 1))
		check(segment+":same_tick_shot_cancelled_before_cost",lab.player.movement_ability.rounds_spent==0 and lab.player.movement_ability.ammo==4 and lab.combat.moving_shots.history.is_empty() and lab.combat.moving_shots.jobs.is_empty())
		check(segment+":own_hurt_or_fall_and_NPC_attack",lab.player.action_kind==("fall" if fatal else "hit") and String(enemy.sprite.animation).begins_with("reaction_attack_"))
		await capture(segment)
		await tap(KEY_R)
		check(segment+":restart_clears_death_and_receipts",lab.player.health==1 and lab.player.hits_received==0 and lab.combat.receipts.is_empty())
	# Nonfatal actual blood, then all eight own moving poses with held movement.
	root.get_node("OptionsStore").set_value(&"reduced_gore",false,false)
	root.get_node("OptionsStore").set_value(&"decals",true,false)
	root.get_node("OptionsStore").set_value(&"flashes",false,false)
	for di in 4:
		var enemy:=await setup(di,120)
		segment="clothing_"+NAMES[di]
		enemy.position=lab.player.position+DIRECTIONS[di].orthogonal()*20
		enemy.locked_aim=-DIRECTIONS[di].orthogonal();lab.player.health=2
		await frames(2)
		lab.combat.start_melee(enemy,"enemy",enemy.locked_aim,lab.config.attacks.enemy_melee)
		await frames(1)
		check(segment+":real_nonfatal_hit_creates_blood",lab.player.health==1 and lab.player.hits_received==1 and lab.combat.damage_events==1)
		await capture(segment+"_hurt");await frames(15)
		key(MOVE_KEYS[di],true);key(KEY_SHIFT,true);await tap(KEY_F)
		for pose in 8:
			var budget:=25
			while lab.player.action_kind=="moving_shot" and lab.player.action_frame<pose and budget>0:await frames(1);budget-=1
			var blood:Array=lab.combat.impact.decals.filter(func(e:Dictionary):return e.get("actor")==lab.player and e.column in [6,7])
			var expected:Vector2=lab.player.global_position+preload("res://scripts/actors/polish_frames.gd").clothing_offset(lab.player.sprite)
			var live_at:Vector2=blood[0].at if not blood.is_empty() else Vector2.INF
			var texture:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
			var socket:Vector2=texture.get_meta("clothing_socket",Vector2.INF)
			check(segment+":actual_blood_tracks_pose"+str(pose),lab.player.action_kind=="moving_shot" and lab.player.sprite.frame==pose and not blood.is_empty() and live_at.distance_to(expected)<=3.6)
			overlay_proofs.append({"direction":NAMES[di],"pose":pose,"tick":Engine.get_physics_frames(),"socket":[socket.x,socket.y],"expected":[expected.x,expected.y],"actual":[live_at.x,live_at.y]})
			await capture(segment+"_pose"+str(pose))
		key(MOVE_KEYS[di],false);key(KEY_SHIFT,false)
		await tap(KEY_R)
		check(segment+":R_clears_blood",lab.combat.impact.decals.is_empty() and lab.player.hits_received==0)
	# Existing earned stun/finishers, every direction/category, invariant gore logic.
	var finisher_outcomes:Dictionary={}
	for reduced in [false,true]:
		root.get_node("OptionsStore").set_value(&"reduced_gore",reduced,false)
		for di in 4:
			for category in ["unarmed","blunt","sharp","firearm","environmental"]:
				var target:=await setup(di,20)
				segment="finisher_"+str(reduced)+"_"+category+"_"+NAMES[di]
				lab.training_bench.position=target.position+DIRECTIONS[di]*24
				lab.training_bench.set_meta("finisher_enabled",category=="environmental")
				lab.select_equipment(["unarmed","blunt","sharp","firearm","environmental"].find(category))
				await frames(2);await tap(KEY_SPACE)
				var budget:=40
				while target.hits_received==0 and budget>0:await frames(1);budget-=1
				check(segment+":earned_stun",target.state=="stunned" and target.health==1 and target.hits_received==1)
				target.set_physics_process(true)
				while not lab.player.action_kind.is_empty() and budget>0:await frames(1);budget-=1
				await tap(KEY_V);await capture(segment+"_windup")
				budget=70
				while target.health>0 and budget>0:await frames(1);budget-=1
				var hit:=contacts.filter(func(e:Dictionary):return e.segment==segment and e.finisher)
				check(segment+":own_contact1_and_NPC_reaction",hit.size()==1 and hit[0].player_frame==1 and hit[0].player_animation=="finish_"+category+"_"+NAMES[di] and target.state=="dead" and target.sprite.frame==1 and lab.score==100)
				check(segment+":finite_firearm_cost_once",lab.player.movement_ability.rounds_spent==(1 if category=="firearm" else 0))
				await capture(segment+"_contact");await frames(10)
				check(segment+":corpse2",target.sprite.frame==2)
				await capture(segment+"_corpse");await frames(45)
				check(segment+":damage_reward_once",target.hits_received==2 and lab.combat.damage_events==2 and lab.score==100 and lab.combat.finishers.is_empty() and not lab.player.try_finisher())
				var outcome:=[target.health,target.hits_received,lab.combat.damage_events,lab.score,lab.player.movement_ability.rounds_spent]
				if not reduced:finisher_outcomes[category+NAMES[di]]=outcome
				else:check(segment+":Full_Reduced_identical",finisher_outcomes[category+NAMES[di]]==outcome)
	# Regression for the independently reproduced freed-argument error. The
	# actual enemy frame signal runs inside Core, after an Input-earned stun.
	despawn_target=await setup(2,20)
	segment="despawn_during_actual_finisher_frame_signal"
	await tap(KEY_SPACE)
	var despawn_budget:=35
	while not lab.player.action_kind.is_empty() and despawn_budget>0:await frames(1);despawn_budget-=1
	check("despawn_probe_stun_earned_by_Input",despawn_target.state=="stunned" and despawn_target.hits_received==1)
	despawn_target.set_physics_process(true);lab.select_equipment(3)
	despawn_target.sprite.frame_changed.connect(despawn_on_finisher_contact)
	despawn_armed=true;despawn_executed=false
	await tap(KEY_V);await frames(30)
	check("target_freed_by_actual_Core_contact_frame_signal",despawn_executed and not despawn_armed)
	check("freed_target_cannot_charge_or_commit_finisher",lab.player.movement_ability.rounds_spent==0 and lab.player.movement_ability.ammo==4 and lab.combat.damage_events==1 and lab.score==0 and lab.combat.finishers.is_empty())
	# Remove this deliberate despawn fixture before any encounter reset.
	root.remove_child(lab);lab.queue_free();await process_frame
	lab=Lab.new();root.add_child(lab);current_scene=lab
	await frames(2);await tap(KEY_7);lab.auto_retry=false
	lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
	await setup(2);await capture("pasha_after_restart")
	var failed:=checks.filter(func(e:Dictionary):return not e.passed).size()
	var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"PASHA_MOVING_SHOT_COMPONENT_ONLY","phase_approval":false,"passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"checks":checks,"trace":trace,"ammo_trace":ammo_trace,"input_focus_events":input_focus_events,"movie_window_no_focus_requested":movie_window_no_focus_requested,"launches":launches,"costs":costs,"contacts":contacts,"captures":captures,"clothing_overlay":overlay_proofs,"not_tested":["all7 unique audio and NPC matrix","actual host FPS","hardware input latency","native Windows","subjective listening","full P06"]},"  "));file.close()
	print("RESULT P06_PASHA passed=%d failed=%d"%[checks.size()-failed,failed]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
