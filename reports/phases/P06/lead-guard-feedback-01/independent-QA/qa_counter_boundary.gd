extends SceneTree
## Direct fixed-clock component fixtures; not Input or rendered-playback evidence.
const Lab = preload("res://scripts/core/character_lab.gd")
var checks: Array[Dictionary] = []
func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL QA_COUNTER_BOUNDARY "+label)
func shape_snapshot(player: Node) -> Array:
	var result: Array = []
	for node in player.get_children():
		if node is CollisionShape2D:
			result.append([node.name,node.position,node.rotation,node.scale,node.disabled,node.shape.get_class(),node.shape.get_rect()])
	return result
func state_snapshot(lab: Node) -> Array:
	var p = lab.player
	return [p.health,p.hits_received,p.position,p.velocity,p.action_kind,p.action_elapsed,p.action_timer,p.action_frame,p.ability_cooldown,p.ability_uses,p.counter_spent,p.counter_blocks,p.action_authority_snapshot.duplicate(true),p.collision_layer,p.collision_mask,shape_snapshot(p),lab.score,lab.combat.next_attack_id,lab.combat.damage_events,lab.combat.attacks.duplicate(true),lab.combat.projectiles.duplicate(true),lab.combat.receipts.duplicate(true)]
func run() -> void:
	root.content_scale_size=Vector2i(640,360)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	var lab = Lab.new()
	root.add_child(lab);current_scene=lab
	lab.auto_retry=false
	check("actual_Oleg_fixture",lab.select_fixture("olezhka_training"))
	await process_frame
	await process_frame
	lab.process_mode=Node.PROCESS_MODE_DISABLED
	var p=lab.player
	check("unchanged_guard_and_action_constants",p.COUNTER_GUARD_OPEN==0.06 and p.COUNTER_GUARD_CLOSE==0.26 and p.COUNTER_WINDUP==0.28 and p.COUNTER_ACTIVE==0.10 and p.COUNTER_RECOVERY==0.34 and p.COUNTER_COOLDOWN==2.0)
	check("direct_setup_uses_real_ability",p.use_ability() and p.action_kind=="special" and p.action_ability_id=="training_counter")
	var cases := [[0.0,false],[0.059999,false],[0.06,true],[0.060001,true],[0.259999,true],[0.26,true],[0.260001,false],[0.279999,false]]
	for item in cases:
		p.action_elapsed=float(item[0]);p.action_frame=0
		var expected: bool=item[1]
		check("fixed_clock_window_"+str(item[0]),p.counter_window_open()==expected)
		if expected:check("model_guard_matches_fixed_clock_"+str(item[0]),p.counter_feedback().phase=="guard")
	p.action_elapsed=0.1;p.action_frame=1
	check("contact_pose_never_guard",not p.counter_window_open())
	p.action_frame=0;p.counter_spent=true
	check("already_spent_never_guard",not p.counter_window_open())
	p.counter_spent=false;lab.state="options"
	check("options_window_closed_and_model_paused",not p.counter_window_open() and p.counter_feedback().phase=="paused")
	lab.state="playing";p.health=0
	check("dead_window_closed_and_model_dead",not p.counter_window_open() and p.counter_feedback().phase=="dead")
	p.health=1;p.action_kind="shove"
	check("wrong_action_not_guard",not p.counter_window_open())
	p.action_kind="special";p.action_ability_id="wrong"
	check("wrong_ability_not_guard",not p.counter_window_open())
	p.action_ability_id="training_counter"
	var snapshot := state_snapshot(lab)
	for i in 100:
		var view: Dictionary=p.counter_feedback();view.phase="fake";view.progress=-999.0;view.window_open=false
	check("pure_read_and_snapshot_mutation_preserve_Core_body_and_clock",snapshot==state_snapshot(lab) and p.counter_feedback().phase=="guard")
	var hud: Node=lab.counter_feedback
	var nodes: Array=[hud];nodes.append_array(hud.find_children("*","",true,false))
	var no_physics := true
	var no_mouse := true
	var no_timers := true
	for node in nodes:
		if node is CollisionObject2D:no_physics=false
		if node is Timer:no_timers=false
		if node is Control and node.mouse_filter!=Control.MOUSE_FILTER_IGNORE:no_mouse=false
	check("HUD_adds_no_body_Area_or_CollisionObject",no_physics)
	check("HUD_and_all_controls_ignore_mouse",no_mouse)
	check("HUD_has_no_separate_Timer",no_timers)
	var rect: Rect2=lab.counter_feedback.meter.get_global_rect()
	check("actual_Control_bar_is_exact_5px_above_arena",rect.size==Vector2(274,5) and rect.position.y+rect.size.y<=62 and rect.position.x+rect.size.x<=640)
	check("HUD_updates_after_default_process_without_physics_method",lab.counter_feedback.process_priority==100 and not lab.counter_feedback.get_script().source_code.contains("func _physics_process"))
	p.cancel_action()
	check("cancel_does_not_refund_cooldown_or_keep_guard",not p.counter_window_open() and p.counter_feedback().phase=="cooldown" and p.ability_cooldown==2.0)
	lab.reset_encounter();p=lab.player
	check("reset_returns_ready_and_no_duplicate_panel",p.counter_feedback().phase=="ready" and p.ability_cooldown==0 and p.counter_blocks==0 and lab.get_children().filter(func(n):return n.get_script()==preload("res://scripts/ui/counter_feedback.gd")).size()==1)
	p.use_ability();p.action_elapsed=0.1;p.action_frame=0
	lab.scene_policy.invalidate()
	check("invalidated_authority_denies_window_and_model",not p.counter_window_open() and p.counter_feedback().phase=="unavailable")
	lab.scene_policy.open("olezhka_training")
	check("reopened_generation_does_not_reauthorize_old_action",not p.counter_window_open() and p.counter_feedback().phase=="unavailable")
	var passed := checks.all(func(item: Dictionary):return item.passed)
	root.remove_child(lab);lab.queue_free();await process_frame
	var out:=OS.get_environment("AYAY_QA_COUNTER_OUTPUT")
	var file:=FileAccess.open(out.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"DIRECT_CLOCK_NEGATIVE_PREDICATE_PURITY_AND_UI_GEOMETRY_ONLY","passed":passed,"checks":checks,"phase_approval":false},"  "));file.close()
	print("QA_COUNTER_BOUNDARY ",checks.filter(func(item:Dictionary):return item.passed).size(),"/",checks.size())
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
