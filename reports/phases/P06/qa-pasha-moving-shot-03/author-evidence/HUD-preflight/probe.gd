extends "res://tests/pasha_moving_shot_replay.gd"
## Actual viewport geometry preflight, not an independent ART verdict.
var hud_samples:Array[Dictionary]=[]
func opaque_npc_overlap(rect:Rect2)->int:
 var count:=0
 for enemy in lab.enemies:
  if not is_instance_valid(enemy) or not enemy.sprite.visible:continue
  var s:AnimatedSprite2D=enemy.sprite
  var texture:Texture2D=s.sprite_frames.get_frame_texture(s.animation,s.frame)
  var pixels:Image
  if texture is AtlasTexture:pixels=texture.atlas.get_image().get_region(Rect2i(texture.region))
  else:pixels=texture.get_image()
  var size:Vector2=Vector2(pixels.get_size())
  var transform:Transform2D=s.get_global_transform_with_canvas()
  for y in pixels.get_height():
   for x in pixels.get_width():
    if pixels.get_pixel(x,y).a<0.5:continue
    var at:Vector2=transform*(Vector2(x,y)-size*0.5)
    if rect.intersects(Rect2(at,Vector2.ONE)):count+=1
 return count
func hud_capture(label:String)->void:
 await frames(1)
 await RenderingServer.frame_post_draw
 var ui:Control=lab.ranged_feedback
 var rect:Rect2=ui.meter.get_global_rect()
 var overlaps:=opaque_npc_overlap(rect)
 var data:Dictionary={"name":label,"phase":ui.displayed_feedback.phase,"title":ui.title.text,"detail":ui.detail.text,"meter":[rect.position.x,rect.position.y,rect.size.x,rect.size.y],"opaque_NPC_pixels_under_meter":overlaps,"tick":Engine.get_physics_frames()}
 hud_samples.append(data)
 check(label+":actual_visible_HUD_and_no_meter_NPC_overlap",ui.visible and not ui.title.text.is_empty() and not ui.detail.text.is_empty() and overlaps==0 and rect.end.y<=54,data)
 var path:=output.path_join(label+".png")
 check(label+":actual_viewport_saved",root.get_texture().get_image().save_png(path)==OK)
func run()->void:
 output=OS.get_environment("AYAY_P06_PASHA_OUTPUT");headless=DisplayServer.get_name()=="headless"
 if output.is_empty() or headless:preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,2);return
 DirAccess.make_dir_recursive_absolute(output)
 root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 root.get_node("OptionsStore").set_value(&"vhs",false,false);root.get_node("OptionsStore").set_value(&"shake",0,false)
 lab=Lab.new();root.add_child(lab);current_scene=lab
 await frames(2);await tap(KEY_7);lab.auto_retry=false
 await setup(2,170,20);await hud_capture("01_ready")
 await tap(KEY_F);await hud_capture("02_firing_windup")
 await wait_launch();await hud_capture("03_firing_contact")
 while not lab.player.action_kind.is_empty():await frames(1)
 await hud_capture("04_cooldown")
 await setup(2,190,20)
 for i in 4:await tap(KEY_F);await frames(23)
 await hud_capture("05_empty")
 await frames(60);await hud_capture("06_refill")
 lab._set_options_visible(true);await hud_capture("07_paused");lab._set_options_visible(false)
 await setup(2,20);await tap(KEY_SPACE);await hud_capture("08_busy")
 await setup(2,90);lab.player.receive_hit(1,0.0,999,lab.enemies[0]);await hud_capture("09_dead")
 var passed:=checks.all(func(e:Dictionary):return e.passed)
 var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);file.store_string(JSON.stringify({"scope":"AUTHOR_ACTUAL_HUD_NATIVE_PREFLIGHT_ONLY","phase_approval":false,"independent_ART_approval":false,"passed":passed,"renderer":DisplayServer.get_name(),"checks":checks,"samples":hud_samples},"  "));file.close()
 print("RESULT PASHA_HUD_PREFLIGHT passed=%d failed=%d"%[checks.filter(func(e:Dictionary):return e.passed).size(),checks.filter(func(e:Dictionary):return not e.passed).size()]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
