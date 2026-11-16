extends Node
## Native/headless mode is declared by the harness. Every viewing action uses Input.
var viewer: Control
var checks: Array[Dictionary] = []
var output := ""
var campaign_before := PackedByteArray()
var campaign_state := ""
var campaign: Node
var viewing_trace: Array[Dictionary] = []

func record(label: String, ok: bool, details: Dictionary = {}) -> void:
 checks.append({"name":label,"passed":ok,"details":details})
 if not ok: push_error("FAIL P06_CAST " + label)

func frames(count: int) -> void:
 for i in count: await get_tree().process_frame

func tap(key: Key) -> void:
 var event := InputEventKey.new();event.keycode = key;event.physical_keycode = key;event.pressed = true
 Input.parse_input_event(event);await frames(2)
 event = InputEventKey.new();event.keycode = key;event.physical_keycode = key;event.pressed = false
 Input.parse_input_event(event);await frames(2)

func capture(name: String) -> void:
 if DisplayServer.get_name() == "headless": return
 await RenderingServer.frame_post_draw
 var code := get_viewport().get_texture().get_image().save_png(output.path_join(name + ".png"))
 record("capture:" + name, code == OK)

func observe_viewing(phase: String, expected_emotion: String) -> void:
 var director: Node = viewer.session.director
 var line: Dictionary = director.current_line()
 viewing_trace.append({"phase":phase,"expected_emotion":expected_emotion,"tick":Engine.get_physics_frames(),
  "wall_usec":Time.get_ticks_usec(),"actor":viewer.selected_actor,"active":director.active,
  "line_index":director.line_index,"line_id":line.get("line_id",""),"emotion":line.get("emotion",""),
  "visible_count":director.visible_count,"text_length":String(line.get("text_ru","")).length(),
  "body_visible":viewer.body.visible_characters,"hold_speed":director.hold_speed,
  "shift_pressed":Input.is_physical_key_pressed(KEY_SHIFT),"space_pressed":Input.is_physical_key_pressed(KEY_SPACE)})

func run(node: Control) -> void:
 viewer = node
 output = OS.get_environment("AYAY_P06_CAST_OUTPUT")
 if output.is_empty():
  push_error("AYAY_P06_CAST_OUTPUT required")
  preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(),1)
  return
 DirAccess.make_dir_recursive_absolute(output)
 await frames(3)
 var options: Node = get_node("/root/OptionsStore")
 options.set_value(&"vhs", false, false)
 if "--p06-cast-large-text" in OS.get_cmdline_user_args(): options.set_value(&"text_scale",1.25,false)
 campaign = get_node("/root/DialogueDirector")
 # Establish a genuine unfinished CH01 viewing state in the isolated harness save.
 record("campaign_fixture_started", campaign.start_scene("res://resources/dialogue/missed_fight_intro.json"))
 campaign.reveal();campaign.advance()
 campaign_before = FileAccess.get_file_as_bytes(campaign.save_path)
 campaign_state = JSON.stringify(get_node("/root/StoryState").store.state)
 var expected_resource: String = campaign.resource_path
 var expected_line: int = campaign.line_index
 record("nine_cast_ids", viewer.ids.size() == 9)
 for index in viewer.ids.size():
  var id: String = viewer.ids[index]
  await tap((KEY_1 + index) as Key)
  record("Input_select:" + id, viewer.selected_actor == id and viewer.session.director.active and viewer.portrait.actor_id == id)
  var expression_index := 0
  for expression in ["neutral","angry","surprise","hurt","catchphrase"]:
   await frames(16)
   var director: Node = viewer.session.director
   var expected_definition: Dictionary = director.data.lines[expression_index]
   var expected_id: String = expected_definition.line_id
   observe_viewing("before_reveal",expression)
   record("line_before_reveal:"+id+":"+expression,director.active and director.line_index==expression_index and director.current_line().line_id==expected_id and director.current_line().emotion==expression)
   # Space reveals an unfinished line, but advances an already revealed one.
   # Observe actual state first; never skip a line just to exercise the reveal key.
   if director.visible_count < director.current_line().text_ru.length():
    await tap(KEY_SPACE)
   observe_viewing("after_reveal",expression)
   record("reveal_preserves_line:"+id+":"+expression,director.active and director.line_index==expression_index and director.current_line().line_id==expected_id)
   record("expression:" + id + ":" + expression, viewer.portrait.actor_id == id and viewer.portrait.expression == expression and viewer.session.director.current_line().emotion == expression and viewer.body.visible_characters == viewer.body.text.length(), {"portrait_file":viewer.portrait.texture.atlas.resource_path if viewer.portrait.texture else "","body_content_height":viewer.body.get_content_height(),"body_height":viewer.body.size.y})
   record("text_fits:" + id + ":" + expression, viewer.body.get_content_height() <= viewer.body.size.y)
   await capture(id + "_" + expression)
   observe_viewing("before_advance",expression)
   await tap(KEY_SPACE)
   observe_viewing("after_advance",expression)
   var last_line: bool = expression_index==viewer.session.director.data.lines.size()-1
   record("Input_advances_exactly_once:"+id+":"+expression,(not director.active) if last_line else (director.active and director.line_index==expression_index+1))
   expression_index+=1
  record("finished:" + id, not viewer.session.director.active)
  await tap(KEY_H)
  record("Input_history:" + id, viewer.history.visible and viewer.session.director.history.size() == 5)
  await tap(KEY_H)
  await tap(KEY_R)
  record("Input_repeat_seen:" + id, viewer.session.director.active and viewer.session.director.can_skip())
  await tap(KEY_K)
  record("Input_skip_seen:" + id, not viewer.session.director.active)
  record("campaign_unchanged:" + id, campaign_before == FileAccess.get_file_as_bytes(campaign.save_path) and campaign.resource_path == expected_resource and campaign.line_index == expected_line and JSON.stringify(get_node("/root/StoryState").store.state) == campaign_state)
 await tap(KEY_ESCAPE)
 # Scene ownership changes are deferred; wait for the actual bootstrap plus old viewer removal.
 for i in 20:
  await frames(1)
  if not is_instance_valid(viewer) and get_tree().current_scene and get_tree().current_scene.get_script().resource_path == "res://scripts/core/bootstrap.gd": break
 record("Input_exit_to_bootstrap", not is_instance_valid(viewer) and not campaign.has_meta("p06_viewing_session"))
 campaign.set_process(false)
 record("campaign_file_after_exit", campaign_before == FileAccess.get_file_as_bytes(campaign.save_path))
 var result := {"schema":1,"actual_input":true,"renderer":DisplayServer.get_name(),"new_voice_recordings":false,"agent_listening":false,"checks":checks,"viewing_trace":viewing_trace,"campaign_resource":expected_resource,"campaign_line":expected_line}
 result["passed"] = checks.all(func(item: Dictionary):return item.passed)
 var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
 print("P06_CAST_REPLAY ",JSON.stringify(result))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(),0 if result.passed else 1)
