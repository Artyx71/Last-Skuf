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
	var player_id: int=lab.player.get_instance_id()
	var authority: Dictionary=lab.scene_policy.action_authority("timka")
	await tap(KEY_4)
	check("unready_prime_preserves_present_context",lab.player.get_instance_id()==player_id and lab.scene_policy.action_authority("timka")==authority and not lab.selection_message.is_empty())
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
