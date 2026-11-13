extends SceneTree
## Instrumented movement/art preview only: no combat, abilities, score or unlocks.
const Frames = preload("res://scripts/actors/character_frames.gd")
const Bindings = preload("res://scripts/core/input_bindings.gd")
const Catalog = preload("res://scripts/systems/character_catalog.gd")
var output := ""
var actor_id := "gabar"
var actor: CharacterBody2D
var world: Node2D
var label: Label
var checks: Array[Dictionary] = []
var trace: Array[Dictionary] = []
var captures: Dictionary = {}
var headless := true
var capture_images := true
var sequence := "grid"
var maximum_visual_grid_error := 0.0

class PreviewActor:
 extends CharacterBody2D
 var sprite: AnimatedSprite2D
 var facing := "down"
 var speed := 110.0
 var running := false
 func _process(_delta: float) -> void:
  preload("res://scripts/actors/pixel_presentation.gd").align(sprite,self,Vector2(0,-26))
 func _physics_process(_delta: float) -> void:
  var direction := Input.get_vector("move_left","move_right","move_up","move_down")
  running = Input.is_action_pressed("p06_preview_run")
  velocity = direction*speed*(1.44 if running else 1.0)
  move_and_slide()
  preload("res://scripts/actors/pixel_presentation.gd").align(sprite,self,Vector2(0,-26))
  if direction.length_squared()>0:
   facing = ("right" if direction.x>0 else "left") if absf(direction.x)>absf(direction.y) else ("down" if direction.y>0 else "up")
  var state := "idle" if direction.length_squared()==0 else ("run" if running else "walk")
  var animation := StringName(state+"_"+facing)
  if sprite.animation != animation or not sprite.is_playing(): sprite.play(animation)

class MeasurementFloor:
 extends Node2D
 func _draw() -> void:
  draw_rect(Rect2(0,0,640,360),Color("24302c"))
  for x in range(16,640,16): draw_line(Vector2(x,72),Vector2(x,312),Color("2b3733"))
  for y in range(72,313,16): draw_line(Vector2(16,y),Vector2(624,y),Color("2b3733"))
  draw_line(Vector2(312,180),Vector2(328,180),Color("9b875d"))
  draw_line(Vector2(320,176),Vector2(320,184),Color("9b875d"))

func _initialize() -> void: call_deferred("run")
func record(name: String, ok: bool, details: Dictionary = {}) -> void:
 checks.append({"name":name,"passed":ok,"details":details})
 if not ok: push_error("FAIL P06_WORLD " + name)
func key(code: Key, pressed: bool) -> void:
 var event := InputEventKey.new()
 event.keycode = code;event.physical_keycode = code;event.pressed = pressed
 Input.parse_input_event(event)
func frames(count: int) -> void:
 for i in count:
  await process_frame
  if not headless: await RenderingServer.frame_post_draw
func sample() -> void:
 await frames(1)
 var sprite: AnimatedSprite2D = actor.sprite
 var state := String(sprite.animation)
 var phase := sprite.frame
 var visual_origin: Vector2=sprite.get_global_transform_with_canvas().origin
 maximum_visual_grid_error=maxf(maximum_visual_grid_error,visual_origin.distance_to(visual_origin.round()))
 var at := {"sequence":sequence,"visual_origin":[visual_origin.x,visual_origin.y],"animation":state,"frame":phase,"physics_tick":Engine.get_physics_frames(),"wall_usec":Time.get_ticks_usec(),"position":[actor.position.x,actor.position.y],"velocity":[actor.velocity.x,actor.velocity.y]}
 trace.append(at)
 var id := state+"_"+str(phase)
 if not captures.has(id):
  captures[id] = at
  if not headless and capture_images:
   record("actual_viewport_capture:"+id,get_root().get_texture().get_image().save_png(output.path_join(id+".png"))==OK)
func run() -> void:
 output = OS.get_environment("AYAY_P06_WORLD_OUTPUT")
 actor_id = OS.get_environment("AYAY_P06_WORLD_ACTOR")
 if actor_id.is_empty(): actor_id = "gabar"
 headless = DisplayServer.get_name()=="headless"
 capture_images = Engine.get_write_movie_path().is_empty()
 if output.is_empty():
  push_error("AYAY_P06_WORLD_OUTPUT required")
  preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
  return
 DirAccess.make_dir_recursive_absolute(output)
 Bindings.install()
 if not InputMap.has_action("p06_preview_run"):
  InputMap.add_action("p06_preview_run")
  var shift := InputEventKey.new();shift.physical_keycode=KEY_SHIFT
  InputMap.action_add_event("p06_preview_run",shift)
 root.content_scale_size=Vector2i(640,360)
 root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.get_node("OptionsStore").set_value(&"vhs",false,false)
 AudioServer.set_bus_mute(0,true) # Art-only fixture, not a new audio review.
 world=Node2D.new();root.add_child(world);current_scene=world
 world.add_child(MeasurementFloor.new())
 var title := Label.new();title.text="P06 / ТЕХНИЧЕСКИЙ ПРОСМОТР ДВИЖЕНИЯ · БОЙ ЕЩЁ НЕ ПОДКЛЮЧЁН";title.position=Vector2(16,12);title.add_theme_font_size_override("font_size",12);world.add_child(title)
 label=Label.new();label.position=Vector2(16,34);label.add_theme_font_size_override("font_size",12);world.add_child(label)
 var note := Label.new();note.text="Клетка16 px · idle3 / walk8 / run12 кадров/с · pivot24,58 · только арт/движение";note.position=Vector2(16,328);note.add_theme_font_size_override("font_size",11);world.add_child(note)
 var loaded := Frames.world_frames(actor_id)
 record("real_reviewed_world_atlas_loads",loaded!=null)
 record("unknown_identity_never_substitutes_Yakuza",Frames.world_frames("unknown")==null)
 record("supporting_identity_never_substitutes_playable",Frames.world_frames("ellana")==null)
 if loaded == null:
  preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1)
  return
 actor=PreviewActor.new();actor.speed=float(Catalog.actor(actor_id).speed);actor.position=Vector2(320,180)
 var shape := CollisionShape2D.new();var bounds := RectangleShape2D.new();bounds.size=Vector2(16,12);shape.shape=bounds;shape.position=Vector2(0,-6);actor.add_child(shape)
 actor.sprite=AnimatedSprite2D.new();actor.sprite.sprite_frames=loaded;actor.sprite.position=Frames.SIZE*0.5-Frames.PIVOT;actor.sprite.texture_filter=CanvasItem.TEXTURE_FILTER_NEAREST;actor.add_child(actor.sprite);world.add_child(actor)
 await frames(3)
 for direction in Frames.DIRECTIONS:
  var code: Key = {"down":KEY_S,"left":KEY_A,"right":KEY_D,"up":KEY_W}[direction]
  actor.facing=direction
  for state in ["idle","walk","run"]:
   actor.position=Vector2(320,180)
   label.text=Catalog.actor(actor_id).display_name+" / "+direction+" / "+state+" · Input→physics→SpriteFrames"
   key(KEY_SHIFT,state=="run")
   key(code,state!="idle")
   await frames(2)
   var expected := StringName(state+"_"+direction)
   record("actual_Input_state:"+String(expected),actor.sprite.animation==expected)
   var before: Vector2=actor.position
   for i in (48 if state=="idle" else 36): await sample()
   var moved: float=actor.position.distance_to(before)
   record("movement:"+String(expected),moved<0.01 if state=="idle" else moved>50.0,{"distance":moved})
   key(code,false);key(KEY_SHIFT,false)
   await frames(2)
   var columns: Array=Frames.WORLD_COLUMNS[state]
   for index in columns.size():
    record("actual_animation_phase:"+String(expected)+":"+str(index),captures.has(String(expected)+"_"+str(index)))
 # A separate uninterrupted Input path checks real transitions; unlike the grid
 # fixture above, it never resets position/facing between these segments.
 sequence="continuous"
 actor.position=Vector2(320,180)
 var continuous_start:=trace.size()
 var previous_key: Key=KEY_NONE
 for step in [{"key":KEY_NONE,"run":false,"direction":"up"},{"key":KEY_D,"run":false,"direction":"right"},{"key":KEY_D,"run":true,"direction":"right"},{"key":KEY_NONE,"run":false,"direction":"right"},{"key":KEY_S,"run":false,"direction":"down"},{"key":KEY_A,"run":true,"direction":"left"},{"key":KEY_W,"run":false,"direction":"up"},{"key":KEY_NONE,"run":false,"direction":"up"}]:
  if previous_key!=KEY_NONE: key(previous_key,false)
  key(KEY_SHIFT,step.run)
  if step.key!=KEY_NONE: key(step.key,true)
  previous_key=step.key
  label.text=Catalog.actor(actor_id).display_name+" / НЕПРЕРЫВНЫЙ Input / "+step.direction
  await frames(2)
  var state: String="idle" if step.key==KEY_NONE else ("run" if step.run else "walk")
  record("continuous_Input_transition:"+state+"_"+step.direction,actor.sprite.animation==StringName(state+"_"+step.direction))
  for i in 24: await sample()
  if not headless and capture_images: record("transition_capture:"+str(step.direction)+":"+state,get_root().get_texture().get_image().save_png(output.path_join("transition_"+str(trace.size())+"_"+state+"_"+step.direction+".png"))==OK)
 key(KEY_SHIFT,false)
 if previous_key!=KEY_NONE:key(previous_key,false)
 var bounded:=true
 for i in range(continuous_start+1,trace.size()):
  var a: Dictionary=trace[i-1];var b: Dictionary=trace[i]
  var delta_ticks:=int(b.physics_tick)-int(a.physics_tick)
  var distance:=Vector2(b.position[0],b.position[1]).distance_to(Vector2(a.position[0],a.position[1]))
  if distance>actor.speed*1.44*delta_ticks/60.0+0.001:bounded=false
 record("continuous_path_no_fixture_teleports",bounded)
 record("render_only_transform_stays_on_pixel_grid",maximum_visual_grid_error<0.0001,{"maximum_grid_error":maximum_visual_grid_error})
 var fractional_physics:=false
 for sample_point in trace:
  var p:=Vector2(sample_point.position[0],sample_point.position[1])
  if p.distance_to(p.round())>0.1:fractional_physics=true
 record("visual_snap_preserves_fractional_physics_positions",fractional_physics)
 var failed:=0
 for check in checks:
  if not check.passed: failed+=1
 var result:={"phase":"P06","scope":"WORLD_ART_MOVEMENT_PREVIEW_ONLY","phase_approval":false,"actual_input":true,"actor_id":actor_id,"renderer":DisplayServer.get_name(),"headless":headless,"movie":Engine.get_write_movie_path(),"checks":checks,"passed":failed==0,"captures":captures,"trace":trace,"continuous_trace_start":continuous_start,"continuous_input_transitions":true,"maximum_visual_grid_error":maximum_visual_grid_error,"audio":"muted art fixture; no audio acceptance","combat_abilities":"NOT_IMPLEMENTED_IN_THIS_PREVIEW"}
 var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
 print("RESULT P06_WORLD passed=%d failed=%d" % [checks.size()-failed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
