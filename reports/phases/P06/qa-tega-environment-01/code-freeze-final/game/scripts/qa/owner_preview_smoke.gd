extends Node
## Explicit packaged-preview startup probe. Not full combat, phase or release QA.
var checks: Array[Dictionary] = []
var captures: Array[String] = []
var output := ""

func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL P06_OWNER_PREVIEW "+label)
func frames(count: int) -> void:
	for i in count:
		await get_tree().physics_frame
		await get_tree().process_frame
func tap(key: Key) -> void:
	var event := InputEventKey.new()
	event.keycode=key;event.physical_keycode=key;event.pressed=true
	Input.parse_input_event(event)
	await frames(1)
	event=InputEventKey.new();event.keycode=key;event.physical_keycode=key;event.pressed=false
	Input.parse_input_event(event)
	await frames(1)
func capture(label: String) -> void:
	if output.is_empty() or DisplayServer.get_name()=="headless": return
	await RenderingServer.frame_post_draw
	var path := output.path_join(label+".png")
	check("capture:"+label,get_viewport().get_texture().get_image().save_png(path)==OK)
	captures.append(path)
func run() -> void:
	output=OS.get_environment("AYAY_OWNER_PREVIEW_SMOKE_OUTPUT")
	if not output.is_empty(): DirAccess.make_dir_recursive_absolute(output)
	await frames(3)
	await capture("menu")
	await tap(KEY_F5)
	await frames(4)
	var lab: Node=get_tree().current_scene
	check("F5_opens_real_character_sandbox",lab.get_script().resource_path=="res://scripts/core/character_lab.gd")
	if lab.get_script().resource_path!="res://scripts/core/character_lab.gd":
		finish(); return
	check("Gabar_actual_complete_body_loaded",lab.player.actor_id=="gabar" and lab.player.authored_frames!=null)
	lab.player.set_aim(Vector2.RIGHT)
	await tap(KEY_F)
	check("Gabar_ability_Input_starts",lab.player.ability_uses==1 and lab.player.action_kind=="special")
	await capture("gabar")
	await tap(KEY_2)
	await frames(2)
	check("Oleg_selection_actual_complete_body",lab.player.actor_id=="olezhka" and lab.player.authored_frames!=null)
	await tap(KEY_F)
	check("Oleg_ability_Input_starts",lab.player.ability_uses==1 and lab.player.action_kind=="special")
	await capture("olezhka")
	await tap(KEY_3)
	check("present_Timka_selects_own_context_and_body",lab.player.actor_id=="timka" and lab.scene_policy.definition().context=="peaceful_present" and lab.player.authored_frames!=null)
	lab.player.set_aim(Vector2.RIGHT)
	await tap(KEY_F)
	check("present_disengage_starts_from_Input",lab.player.action_kind=="disengage" and lab.player.ability_uses==1)
	await frames(24)
	check("present_disengage_moves_without_prime_damage",lab.player.ability_distance>0 and lab.player.ability_distance<=33.63 and lab.combat.damage_events==0 and lab.score==0 and not lab.player.can_use_finisher("unarmed"))
	await capture("timka_present")
	await tap(KEY_4)
	check("prime_Timka_selects_separate_body_contract",lab.player.actor_id=="timka" and lab.player.prepared_ability=="clinch" and lab.player.move_speed==118 and lab.player.authored_frames.get_animation_names().size()==48)
	check("prime_cannot_grab_without_vulnerable_target",not lab.player.use_ability() and lab.player.ability_uses==0)
	await capture("timka_prime")
	await tap(KEY_5)
	check("Ryzhik_selects_complete_own_roll_body",lab.player.actor_id=="ryzhik" and lab.player.prepared_ability=="dance_step" and lab.player.authored_frames.get_animation_names().size()==60)
	lab.player.set_aim(Vector2.RIGHT)
	await tap(KEY_F)
	check("Ryzhik_roll_starts_from_Input",lab.player.action_kind=="roll" and lab.player.ability_uses==1)
	await frames(24)
	check("Ryzhik_roll_moves_with_live_collision",lab.player.ability_distance>0 and lab.player.ability_distance<=57.64 and lab.player.collision_layer==2 and lab.player.collision_mask==1)
	await capture("ryzhik_roll")
	await tap(KEY_6)
	check("Tega_selects_complete_environment_body",lab.player.actor_id=="tega" and lab.player.prepared_ability=="environment_kick" and lab.player.authored_frames.get_animation_names().size()==56)
	# Explicit sandbox setup; actual Input and physical displacement are measured.
	lab.player.position=Vector2(274,270)
	lab.player.set_aim(Vector2.RIGHT)
	var bench_start:Vector2=lab.training_bench.position
	await frames(2);await tap(KEY_F)
	check("Tega_kick_starts_with_registered_object_Input",lab.player.action_kind=="special" and lab.player.ability_uses==1)
	await frames(24)
	check("Tega_moves_real_bench_with_restored_masks",lab.player.ability_distance>0 and lab.player.ability_distance<=37.81 and lab.training_bench.position.distance_to(bench_start)>0 and lab.training_bench.collision_mask==6 and lab.player.collision_mask==1)
	await capture("tega_environment_kick")
	var player_id: int=lab.player.get_instance_id()
	var authority: Dictionary=lab.scene_policy.action_authority("tega")
	await tap(KEY_7)
	check("unready_Pasha_preserves_Tega_context",lab.player.get_instance_id()==player_id and lab.scene_policy.action_authority("tega")==authority and not lab.selection_message.is_empty())
	await tap(KEY_ESCAPE)
	await frames(3)
	check("sandbox_returns_to_menu",get_tree().current_scene.get_script().resource_path=="res://scripts/core/bootstrap.gd")
	await tap(KEY_F6)
	await frames(4)
	var viewer: Node=get_tree().current_scene
	check("F6_opens_actual_cast_viewer",viewer.get_script().resource_path=="res://scripts/ui/cast_viewer.gd")
	if viewer.get_script().resource_path=="res://scripts/ui/cast_viewer.gd":
		check("all_nine_cast_entries_available",viewer.ids.size()==9)
		for actor in viewer.ids:
			check("portrait_dialogue_available:"+actor,viewer.open_actor(actor))
			await frames(1)
		viewer.open_actor("timka")
		await frames(2)
		await capture("timka_portrait")
	finish()
func finish() -> void:
	var passed:=checks.all(func(item: Dictionary):return item.passed)
	if not output.is_empty():
		var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema":1,"scope":"PACKAGED_OWNER_PREVIEW_MENU_AND_AVAILABLE_FIXTURES_ONLY","passed":passed,"phase_approval":false,"full_combat_approval":false,"renderer":DisplayServer.get_name(),"checks":checks,"captures":captures},"  "))
		file.close()
	print("RESULT P06_OWNER_PREVIEW passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(),0 if passed else 1)
