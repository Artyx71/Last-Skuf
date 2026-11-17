extends "res://tests/olezhka_combat_replay.gd"
## Read the real HUD after its process pass; never call its update from QA.
var observations: Array[Dictionary] = []
var observer: Node

class HUDObserver:
	extends Node
	var replay
	signal sampled
	func _ready() -> void: process_priority = 1000
	func _process(_delta: float) -> void:
		replay.observe_hud()
		sampled.emit()

func check(name: String, ok: bool, details: Dictionary = {}) -> void:
	checks.append({"name":name,"passed":ok,"details":details})
	if not ok: push_error("FAIL P06_COUNTER_FEEDBACK "+name)

func observe_hud() -> void:
	if not is_instance_valid(lab) or not is_instance_valid(lab.player): return
	var hud: Control = lab.counter_feedback
	var player: CharacterBody2D = lab.player
	var shown: Dictionary = hud.displayed_feedback.duplicate(true)
	var rect: Rect2 = hud.meter.get_global_rect()
	observations.append({"segment":segment,"physics_tick":Engine.get_physics_frames(),
		"clock":player.action_elapsed,"action":player.action_kind,"frame":player.action_frame,
		"health":player.health,"cooldown":player.ability_cooldown,"blocks":player.counter_blocks,
		"damage":lab.combat.damage_events,"phase":shown.get("phase",""),
		"window_open":player.counter_window_open(),"model":player.counter_feedback(),
		"displayed":shown,"text":hud.title.text,"bar":hud.meter.value,"visible":hud.visible,
		"bar_rect":[rect.position.x,rect.position.y,rect.size.x,rect.size.y]})

func sample_frames(count: int) -> void:
	for i in count: await observer.sampled

func wait_phase(phase: String, limit := 150) -> bool:
	for i in limit:
		await sample_frames(1)
		if lab.counter_feedback.displayed_feedback.get("phase") == phase: return true
	return false

func run() -> void:
	output = OS.get_environment("AYAY_P06_COUNTER_OUTPUT")
	headless = DisplayServer.get_name()=="headless"
	if output.is_empty():
		push_error("AYAY_P06_COUNTER_OUTPUT required")
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
	observer = HUDObserver.new()
	observer.replay = self
	root.add_child(observer)
	await sample_frames(2)
	check("Gabar_has_no_parry_indicator",not lab.counter_feedback.visible)
	await tap(KEY_2)
	await sample_frames(1)
	check("actual_Input_selects_Oleg_and_ready_HUD",lab.player.actor_id=="olezhka" and lab.counter_feedback.visible and lab.counter_feedback.displayed_feedback.phase=="ready")
	await capture("01_ready")
	lab.combat.contact_committed.connect(on_contact)
	lab.combat.contact_defended.connect(on_defense)

	segment = "miss_window"
	var target: CharacterBody2D = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	check("Input_F_opens_preparation_not_immunity",await wait_phase("preparing",3) and not lab.player.counter_window_open())
	await capture("02_preparing")
	check("real_guard_window_is_visible",await wait_phase("guard",10) and lab.player.counter_window_open())
	await capture("03_guard_open")
	check("miss_window_closes_before_recovery",await wait_phase("closed",25) and not lab.player.counter_window_open())
	await capture("04_window_closed")
	check("miss_has_readable_recovery",await wait_phase("recovery",15))
	await capture("05_recovery")
	check("miss_has_readable_cooldown",await wait_phase("cooldown",35) and not lab.player.use_ability())
	await capture("06_cooldown")
	check("miss_never_damages_or_blocks",target.hits_received==0 and lab.combat.damage_events==0 and lab.player.counter_blocks==0)
	check("ready_returns_when_actual_cooldown_expires",await wait_phase("ready",130) and lab.player.ability_cooldown==0)

	for di in 4:
		segment = "real_parry_"+NAMES[di]
		target = await fixture(DIRECTIONS[di],3,false)
		await tap(KEY_F)
		check("guard_available_"+NAMES[di],await wait_phase("guard",12))
		enemy_strike(target)
		check("actual_front_contact_confirms_HUD_"+NAMES[di],await wait_phase("counter",8) and lab.player.health==1 and lab.player.hits_received==0 and lab.player.counter_blocks==1 and lab.combat.damage_events==0)
		await capture("07_block_"+NAMES[di])
		await sample_frames(3)
		check("counter_once_via_existing_Core_"+NAMES[di],target.hits_received==1 and target.health==2 and lab.combat.damage_events==1 and lab.player.health==1 and lab.score==0)
		check("counter_recovery_visible_"+NAMES[di],await wait_phase("recovery",20))
		await capture("08_counter_recovery_"+NAMES[di])

	segment = "cancel"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await wait_phase("guard",12)
	await tap(KEY_C)
	await sample_frames(1)
	check("Input_C_removes_guard_without_refunding_cooldown",lab.counter_feedback.displayed_feedback.phase=="cooldown" and not lab.player.counter_window_open() and lab.player.ability_cooldown>0 and lab.combat.damage_events==0)
	await capture("09_cancel")

	segment = "death_early"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	enemy_strike(target)
	check("early_fatal_hit_does_not_create_counter",await wait_phase("dead",12) and lab.player.health==0 and lab.player.counter_blocks==0 and target.hits_received==0)
	await capture("10_dead")
	await tap(KEY_R)
	await sample_frames(1)
	check("Input_R_clears_dead_feedback",lab.counter_feedback.displayed_feedback.phase=="ready" and lab.player.health==1 and lab.player.counter_blocks==0)

	segment = "pause"
	target = await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await wait_phase("guard",12)
	await tap(KEY_O)
	await sample_frames(1)
	var clock: float = lab.player.action_elapsed
	var cooldown: float = lab.player.ability_cooldown
	await sample_frames(8)
	check("paused_UI_never_claims_an_active_window",lab.counter_feedback.displayed_feedback.phase=="paused" and not lab.player.counter_window_open() and lab.player.action_elapsed==clock and lab.player.ability_cooldown==cooldown)
	await capture("11_paused")
	await tap(KEY_O)
	await sample_frames(1)
	check("resume_shows_same_live_window",lab.counter_feedback.displayed_feedback.phase=="guard" and lab.player.counter_window_open())
	enemy_strike(target)
	check("resumed_guard_still_parries",await wait_phase("counter",8) and lab.player.counter_blocks==1)

	segment = "authority"
	await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await wait_phase("guard",12)
	lab.scene_policy.invalidate()
	await sample_frames(2)
	check("revocation_cannot_leave_green_ready_or_guard",lab.counter_feedback.displayed_feedback.phase=="unavailable" and not lab.player.counter_window_open() and not lab.player.use_ability())
	await capture("12_revoked")
	await tap(KEY_2)
	await sample_frames(1)
	check("registered_reselection_restores_ready",lab.counter_feedback.displayed_feedback.phase=="ready")
	check("unknown_fixture_refused",not lab.select_fixture("unregistered_fixture"))
	await sample_frames(1)
	check("unknown_selection_keeps_Oleg_feedback",lab.player.actor_id=="olezhka" and lab.counter_feedback.displayed_feedback.phase=="ready")
	await capture("13_unknown_keeps_Oleg")
	await tap(KEY_R)
	await sample_frames(1)
	check("retry_restores_Oleg_feedback_and_status",lab.selection_message.is_empty() and not lab.status_label.text.contains("ещё не готов") and lab.player.actor_id=="olezhka" and lab.counter_feedback.displayed_feedback.phase=="ready")

	var modes: Array = []
	for reduced in [false,true]:
		segment = "settings_"+str(reduced)
		var store := root.get_node("OptionsStore")
		store.set_value(&"reduced_gore",reduced,false)
		store.set_value(&"flashes",not reduced,false)
		store.set_value(&"shake",0 if reduced else 100,false)
		store.set_value(&"vhs",not reduced,false)
		target = await fixture(Vector2.RIGHT,3,false)
		await tap(KEY_F)
		await wait_phase("guard",12)
		check("settings_keep_guard_information_"+str(reduced),lab.counter_feedback.title.text.contains("ОКНО ОТКРЫТО") and lab.counter_feedback.visible)
		await capture("14_settings_guard_"+str(reduced))
		enemy_strike(target)
		await wait_phase("counter",8)
		await sample_frames(3)
		modes.append([lab.player.health,target.health,target.hits_received,lab.player.counter_blocks,lab.combat.damage_events,lab.score,lab.player.collision_layer,lab.player.collision_mask])
	check("Full_Reduced_flash_shake_VHS_leave_mechanics_equal",modes[0]==modes[1],{"results":modes})

	segment = "pure_read"
	await fixture(Vector2.RIGHT,3,false)
	await tap(KEY_F)
	await wait_phase("guard",12)
	var before: Array = [lab.player.action_elapsed,lab.player.ability_cooldown,lab.player.counter_blocks,lab.combat.next_attack_id,lab.combat.damage_events,lab.score]
	for i in 100:
		var view: Dictionary = lab.player.counter_feedback()
		view.phase = "forged"
		view.cooldown = 999
	check("reading_or_mutating_snapshots_never_changes_gameplay",before==[lab.player.action_elapsed,lab.player.ability_cooldown,lab.player.counter_blocks,lab.combat.next_attack_id,lab.combat.damage_events,lab.score] and lab.player.counter_feedback().phase=="guard")
	await tap(KEY_R)
	await sample_frames(1)
	check("reset_clears_clock_and_keeps_one_panel",lab.counter_feedback.displayed_feedback.phase=="ready" and lab.player.action_elapsed==0 and lab.player.ability_cooldown==0 and lab.get_children().filter(func(n):return n.get_script()==preload("res://scripts/ui/counter_feedback.gd")).size()==1)
	await tap(KEY_1)
	await sample_frames(1)
	check("actual_Gabar_selection_hides_Oleg_only_UI",lab.player.actor_id=="gabar" and not lab.counter_feedback.visible)

	var parity := true
	var bounds := true
	var layout := true
	var bar_clear := true
	var phases: Dictionary = {}
	for item in observations:
		if item.displayed != item.model: parity = false
		if item.phase=="guard" and not item.window_open: parity = false
		if item.bar < 0 or item.bar > 1: bounds = false
		if item.visible and (item.bar_rect[1]+item.bar_rect[3]>62 or item.bar_rect[3]!=5): bar_clear=false
		phases[item.phase] = true
	check("every_observed_frame_HUD_matches_current_simulation",parity,{"samples":observations.size()})
	check("bar_is_always_bounded",bounds)
	check("actual_bar_rect_is_5px_and_never_overlaps_arena",bar_clear)
	for phase in ["ready","preparing","guard","closed","counter","recovery","cooldown","paused","dead","unavailable","hidden"]:
		check("observed_real_phase_"+phase,phases.has(phase))
	var hud: Control = lab.counter_feedback
	for text in hud.TEXT.values():
		if hud.title.get_theme_font("font").get_string_size(text,HORIZONTAL_ALIGNMENT_LEFT,-1,11).x>hud.size.x: layout=false
	check("all_labels_fit_reserved_274px_and_no_arena_overlap",layout and hud.position.y+hud.size.y<62 and hud.position.x+hud.size.x<=640)
	var old_panel: Control = hud
	await tap(KEY_ESCAPE)
	await frames(3)
	check("scene_exit_removes_temporary_panel",not is_instance_valid(old_panel))
	observer.queue_free()
	await process_frame
	var failed := checks.filter(func(c: Dictionary): return not c.passed).size()
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"OLEZHKA_GUARD_READABILITY_ONLY","phase_approval":false,"passed":failed==0,"actual_input":true,"renderer":DisplayServer.get_name(),"checks":checks,"observations":observations,"contacts":contacts,"defenses":defenses,"captures":captures,"not_tested":["other hero completion","subjective audio","hardware input latency","FPS acceptance","native Windows","full P06"]},"  "))
	file.close()
	print("P06_COUNTER_FEEDBACK ",checks.size()-failed,"/",checks.size()," passed")
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failed else 0)
