extends "res://tests/qa_tega_callback_geometry.gd"
## Independent direct Shape2D.collide versus scene/PhysicsServer/space-cache authority.
func shape_proof()->Dictionary:
 var circle:=CircleShape2D.new();circle.radius=8.0
 var xf:=Transform2D(0,lab.player.global_position+Vector2(0,-6)+Vector2.RIGHT*23.0)
 var shape:CollisionShape2D
 for c in lab.training_bench.get_children():
  if c is CollisionShape2D:shape=c;break
 var physics_body:Transform2D=PhysicsServer2D.body_get_state(lab.training_bench.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM)
 var physics_shape:Transform2D=physics_body*PhysicsServer2D.body_get_shape_transform(lab.training_bench.get_rid(),0)
 var q:=PhysicsShapeQueryParameters2D.new();q.shape=circle;q.transform=xf;q.collision_mask=1;q.exclude=[lab.player.get_rid()]
 var overlap:=false
 for e in lab.get_world_2d().direct_space_state.intersect_shape(q,16):
  if e.collider==lab.training_bench:overlap=true
 return {"node_body_origin":[lab.training_bench.global_position.x,lab.training_bench.global_position.y],"Node_shape_origin":[shape.global_transform.origin.x,shape.global_transform.origin.y],"PhysicsServer_body_origin":[physics_body.origin.x,physics_body.origin.y],"PhysicsServer_shape_origin":[physics_shape.origin.x,physics_shape.origin.y],"foot_circle_origin":[xf.origin.x,xf.origin.y],"direct_Shape2D_collide_current_Node":circle.collide(xf,shape.shape,shape.global_transform),"direct_Shape2D_collide_PhysicsServer_transform":circle.collide(xf,shape.shape,physics_shape),"DirectSpaceState_contains_object":overlap,"runtime_near_foot":lab.combat.environment_kicks._near_foot(lab.player,lab.training_bench,Vector2.RIGHT)}
func on_audio(cue:StringName,_at:Vector2)->void:
 if cue!=&"impact_unarmed_metal" or qa_mode.is_empty():return
 var mode:=qa_mode;qa_mode=""
 var old_id:int=lab.player.melee_attack_id
 var old_epoch:int=lab.combat.encounter_epoch
 var new_started:=false
 var before=shape_proof()
 if mode in ["Node_shift_without_force","Node_shift_with_force"]:lab.training_bench.position+=Vector2(0,16)
 if mode=="reset_then_new_same_kind_F":
  var at:Vector2=lab.player.position
  lab.combat.reset()
  lab.player.reset(at)
  lab.player.set_aim(Vector2.RIGHT)
  new_started=lab.player.use_ability()
 var before_force=shape_proof()
 if mode=="Node_shift_with_force":lab.training_bench.force_update_transform()
 var after_force=shape_proof()
 source_after_callback=lab.player.position;prop_after_callback=lab.training_bench.position
 immediate={"mode":mode,"tick":Engine.get_physics_frames(),"actor":[source_after_callback.x,source_after_callback.y],"prop":[prop_after_callback.x,prop_after_callback.y],"before_change":before,"after_change_before_force":before_force,"after_optional_force":after_force,"old_action_id":old_id,"old_epoch":old_epoch,"new_action_started":new_started,"new_action_id":lab.player.melee_attack_id,"new_epoch":lab.combat.encounter_epoch,"action_kind":lab.player.action_kind,"jobs":lab.combat.environment_kicks.jobs.size(),"source_mask":lab.player.collision_mask,"object_mask":lab.training_bench.collision_mask,"source_exceptions":ids(lab.player),"object_exceptions":ids(lab.training_bench),"damage_events":lab.combat.damage_events,"receipt_count":lab.combat.receipts.size()}
 pending=true
func observe_after_callback()->void:
 if not pending:return
 super.observe_after_callback()
 observed["action_id"]=lab.player.melee_attack_id
 observed["action_kind"]=lab.player.action_kind
 observed["authorized"]=lab.player._action_authorized()
 observed["epoch"]=lab.combat.encounter_epoch
 observed["job_ids"]=lab.combat.environment_kicks.jobs.map(func(j:Dictionary):return j.id)
 observed["job_epochs"]=lab.combat.environment_kicks.jobs.map(func(j:Dictionary):return j.epoch)
 observed["shape_proof_after_Core"]=shape_proof()
func run()->void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.audio_event.connect(on_audio)
 var observer:=Observer.new();observer.qa=self;observer.process_physics_priority=1000;root.add_child(observer)
 for mode in ["Node_shift_without_force","Node_shift_with_force","reset_then_new_same_kind_F"]:
  await setup(2,false);immediate={};observed={};qa_mode=mode
  await tap(KEY_F);await frames(25)
  var proof={"callback":immediate.duplicate(true),"same_tick_after_Core":observed.duplicate(true)};proofs.append(proof)
  check(mode+":real_same_tick_observer",qa_mode.is_empty() and not observed.is_empty() and observed.tick==immediate.tick,proof)
  if observed.is_empty():continue
  if mode=="reset_then_new_same_kind_F":
   check(mode+":legitimate_reset_and_new_environment_action_created",immediate.new_action_started and immediate.action_kind=="special" and immediate.jobs==1 and immediate.new_epoch!=immediate.old_epoch,proof)
   check(mode+":numeric_id_collision_exercised",immediate.new_action_id==immediate.old_action_id,proof)
   check(mode+":old_job_stop_preserves_new_epoch_action",observed.action_kind=="special" and observed.action_id==immediate.new_action_id and observed.epoch==immediate.new_epoch and observed.jobs==1 and observed.action_id in observed.job_ids and observed.epoch in observed.job_epochs and observed.authorized,proof)
  else:
   check(mode+":direct_Node_shape_collision_miss_proven",not immediate.after_optional_force.direct_Shape2D_collide_current_Node and immediate.before_change.direct_Shape2D_collide_current_Node,proof)
   check(mode+":geometry_telemetry_recorded",immediate.after_change_before_force.has("PhysicsServer_body_origin") and observed.shape_proof_after_Core.has("DirectSpaceState_contains_object"),proof)
   check(mode+":no_step_of_object_at_ineligible_current_Node_geometry",Vector2(observed.actor_delta[0],observed.actor_delta[1]).length()<0.0001 and Vector2(observed.prop_delta[0],observed.prop_delta[1]).length()<0.0001 and observed.jobs==0,proof)
  check(mode+":no_contact_or_mask_exception_side_effect",observed.damage_events==immediate.damage_events and observed.receipt_count==immediate.receipt_count and observed.source_mask==immediate.source_mask and observed.object_mask==immediate.object_mask and observed.source_exceptions==immediate.source_exceptions and observed.object_exceptions==immediate.object_exceptions,proof)
  await frames(30)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_PHYSICS_TRANSFORM_AND_EPOCH_REPLACEMENT","phase_approval":false,"passed":passed,"checks":checks,"proofs":proofs},"  "));f.close()
 print("RESULT QA_TEGA_PHYSICS passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
