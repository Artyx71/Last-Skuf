extends "res://tests/tega_environment_replay.gd"
## Explicit adversarial synchronous transforms, measured AFTER Core in the SAME physics tick.
class Observer:
 extends Node
 var qa
 func _physics_process(_delta:float) -> void: qa.observe_after_callback()
var qa_mode := ""
var pending := false
var immediate:Dictionary={}
var observed:Dictionary={}
var proofs:Array[Dictionary]=[]
var source_after_callback:Vector2
var prop_after_callback:Vector2
func frames(count:int) -> void:
 for i in count:
  await physics_frame
  await process_frame
func ids(b:PhysicsBody2D)->Array:
 var result:Array=[]
 for o in b.get_collision_exceptions():result.append(o.get_instance_id())
 return result
func on_audio(cue:StringName,_at:Vector2)->void:
 if cue!=&"impact_unarmed_metal" or qa_mode.is_empty():return
 var mode:=qa_mode;qa_mode=""
 if mode=="same_object_transform_far":lab.training_bench.position+=Vector2(100,0)
 if mode=="source_transform_far":lab.player.position-=Vector2(100,0)
 source_after_callback=lab.player.position;prop_after_callback=lab.training_bench.position
 immediate={"mode":mode,"tick":Engine.get_physics_frames(),"actor":[source_after_callback.x,source_after_callback.y],"prop":[prop_after_callback.x,prop_after_callback.y],"distance":source_after_callback.distance_to(prop_after_callback),"registered_same_enabled_object":lab.combat.environments.get("training_bench")==lab.training_bench and lab.training_bench.get_meta("finisher_enabled"),"source_mask":lab.player.collision_mask,"object_mask":lab.training_bench.collision_mask,"source_exceptions":ids(lab.player),"object_exceptions":ids(lab.training_bench),"jobs":lab.combat.environment_kicks.jobs.size(),"damage_events":lab.combat.damage_events,"receipt_count":lab.combat.receipts.size(),"clock":lab.player.action_elapsed,"frame":lab.player.action_frame}
 pending=true
func observe_after_callback()->void:
 if not pending:return
 pending=false
 var a:Vector2=lab.player.position;var p:Vector2=lab.training_bench.position
 observed={"tick":Engine.get_physics_frames(),"actor":[a.x,a.y],"prop":[p.x,p.y],"actor_delta":[a.x-source_after_callback.x,a.y-source_after_callback.y],"prop_delta":[p.x-prop_after_callback.x,p.y-prop_after_callback.y],"source_mask":lab.player.collision_mask,"object_mask":lab.training_bench.collision_mask,"source_exceptions":ids(lab.player),"object_exceptions":ids(lab.training_bench),"jobs":lab.combat.environment_kicks.jobs.size(),"damage_events":lab.combat.damage_events,"receipt_count":lab.combat.receipts.size()}
func run()->void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.audio_event.connect(on_audio)
 var observer:=Observer.new();observer.qa=self;observer.process_physics_priority=1000;root.add_child(observer)
 for mode in ["same_object_transform_far","source_transform_far"]:
  await setup(2,false);immediate={};observed={};qa_mode=mode
  await tap(KEY_F);await frames(25)
  var proof={"callback":immediate.duplicate(true),"same_tick_after_Core":observed.duplicate(true)};proofs.append(proof)
  check(mode+":callback_really_moved_same_authorized_instance_far",qa_mode.is_empty() and not immediate.is_empty() and immediate.distance>38 and immediate.registered_same_enabled_object,proof)
  check(mode+":observer_really_after_Core_same_physics_tick",not observed.is_empty() and observed.tick==immediate.tick and immediate.frame==1,proof)
  if observed.is_empty():continue
  check(mode+":no_stale_same_tick_step_after_geometry_invalidated",Vector2(observed.actor_delta[0],observed.actor_delta[1]).length()<0.0001 and Vector2(observed.prop_delta[0],observed.prop_delta[1]).length()<0.0001 and observed.jobs==0,proof)
  check(mode+":no_contact_or_mask_exception_side_effect",observed.damage_events==immediate.damage_events and observed.receipt_count==immediate.receipt_count and observed.source_mask==immediate.source_mask and observed.object_mask==immediate.object_mask and observed.source_exceptions==immediate.source_exceptions and observed.object_exceptions==immediate.object_exceptions,proof)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_SAME_TICK_CALLBACK_SPATIAL_AUTHORITY","phase_approval":false,"passed":passed,"checks":checks,"proofs":proofs},"  "));f.close()
 print("RESULT QA_TEGA_CALLBACK_GEOMETRY passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
