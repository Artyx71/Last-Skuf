extends "res://tests/qa_tega_callback_geometry.gd"
## Additional independent controls: LOS, foot shape at valid range/facing, replacement action.
var callback_wall:StaticBody2D
func on_audio(cue:StringName,_at:Vector2)->void:
 if cue!=&"impact_unarmed_metal" or qa_mode.is_empty():return
 var mode:=qa_mode;qa_mode=""
 var old_id:int=lab.player.melee_attack_id
 var new_started:=false
 if mode=="foot_shape_miss":lab.training_bench.position+=Vector2(0,16)
 if mode=="LOS_becomes_blocked":callback_wall.collision_layer=1
 if mode=="listener_replaces_with_shove":
  lab.player.cancel_action()
  new_started=lab.player.attack_melee()
 source_after_callback=lab.player.position;prop_after_callback=lab.training_bench.position
 var offset:Vector2=prop_after_callback-source_after_callback
 immediate={"mode":mode,"tick":Engine.get_physics_frames(),"actor":[source_after_callback.x,source_after_callback.y],"prop":[prop_after_callback.x,prop_after_callback.y],"distance":offset.length(),"facing_dot":Vector2.RIGHT.dot(offset.normalized()),"actual_foot_eligible":lab.combat.environment_kicks._near_foot(lab.player,lab.training_bench,Vector2.RIGHT),"source_mask":lab.player.collision_mask,"object_mask":lab.training_bench.collision_mask,"source_exceptions":ids(lab.player),"object_exceptions":ids(lab.training_bench),"jobs":lab.combat.environment_kicks.jobs.size(),"damage_events":lab.combat.damage_events,"receipt_count":lab.combat.receipts.size(),"clock":lab.player.action_elapsed,"frame":lab.player.action_frame,"old_action_id":old_id,"new_action_started":new_started,"new_action_id":lab.player.melee_attack_id,"new_action_kind":lab.player.action_kind}
 pending=true
func observe_after_callback()->void:
 if not pending:return
 super.observe_after_callback()
 observed["action_id"]=lab.player.melee_attack_id
 observed["action_kind"]=lab.player.action_kind
 observed["animation"]=String(lab.player.sprite.animation)
 observed["authorized"]=lab.player._action_authorized()
 observed["attack_ids"]=lab.combat.attacks.map(func(a:Dictionary):return a.id)
func run()->void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.audio_event.connect(on_audio)
 var observer:=Observer.new();observer.qa=self;observer.process_physics_priority=1000;root.add_child(observer)
 for mode in ["foot_shape_miss","LOS_becomes_blocked","listener_replaces_with_shove"]:
  await setup(2,false)
  if mode=="LOS_becomes_blocked":
   callback_wall=make_wall(lab.player.position+Vector2(12,-6),Vector2(1,4));callback_wall.collision_layer=0;await frames(2)
  immediate={};observed={};qa_mode=mode
  await tap(KEY_F);await frames(25)
  var proof={"callback":immediate.duplicate(true),"same_tick_after_Core":observed.duplicate(true)};proofs.append(proof)
  check(mode+":actual_same_tick_callback_observer",qa_mode.is_empty() and not observed.is_empty() and observed.tick==immediate.tick,proof)
  if observed.is_empty():continue
  if mode=="listener_replaces_with_shove":
   check(mode+":real_replacement_action_created",immediate.new_action_started and immediate.new_action_kind=="shove" and immediate.new_action_id!=immediate.old_action_id,proof)
   check(mode+":stop_old_job_preserves_new_action_and_reservation",observed.action_kind=="shove" and observed.action_id==immediate.new_action_id and observed.action_id in observed.attack_ids and observed.authorized and observed.jobs==0,proof)
  else:
   check(mode+":eligibility_invalid_with_range_and_facing_still_valid",immediate.distance>=12 and immediate.distance<=38 and immediate.facing_dot>=0.85 and not immediate.actual_foot_eligible,proof)
   check(mode+":no_stale_step_after_overlap_or_LOS_change",Vector2(observed.actor_delta[0],observed.actor_delta[1]).length()<0.0001 and Vector2(observed.prop_delta[0],observed.prop_delta[1]).length()<0.0001 and observed.jobs==0,proof)
  check(mode+":masks_exceptions_contact_state_preserved",observed.damage_events==immediate.damage_events and observed.receipt_count==immediate.receipt_count and observed.source_mask==immediate.source_mask and observed.object_mask==immediate.object_mask and observed.source_exceptions==immediate.source_exceptions and observed.object_exceptions==immediate.object_exceptions,proof)
  if mode=="LOS_becomes_blocked":callback_wall.queue_free();await frames(2)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_CALLBACK_SPATIAL_AND_REPLACEMENT_ACTION","phase_approval":false,"passed":passed,"checks":checks,"proofs":proofs},"  "));f.close()
 print("RESULT QA_TEGA_CALLBACK_EXTENDED passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
