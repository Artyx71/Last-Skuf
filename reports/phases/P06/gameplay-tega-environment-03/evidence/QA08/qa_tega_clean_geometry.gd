extends "res://tests/qa_tega_callback_geometry.gd"
## Clean callback: Node transform mutation and READ-ONLY geometry telemetry only.
## No production eligibility helper or transform-flush method is called by this probe.
func raw_shape_proof()->Dictionary:
 var circle:=CircleShape2D.new();circle.radius=8.0
 var xf:=Transform2D(0,lab.player.global_position+Vector2(0,-6)+Vector2.RIGHT*23.0)
 var shape:CollisionShape2D
 for c in lab.training_bench.get_children():
  if c is CollisionShape2D:shape=c;break
 var server_body:Transform2D=PhysicsServer2D.body_get_state(lab.training_bench.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM)
 var server_shape:Transform2D=server_body*PhysicsServer2D.body_get_shape_transform(lab.training_bench.get_rid(),0)
 var q:=PhysicsShapeQueryParameters2D.new();q.shape=circle;q.transform=xf;q.collision_mask=1;q.exclude=[lab.player.get_rid()]
 var overlap:=false
 for e in lab.get_world_2d().direct_space_state.intersect_shape(q,16):
  if e.collider==lab.training_bench:overlap=true
 return {"Node_body":[lab.training_bench.global_position.x,lab.training_bench.global_position.y],"Node_shape":[shape.global_transform.origin.x,shape.global_transform.origin.y],"PhysicsServer_body":[server_body.origin.x,server_body.origin.y],"PhysicsServer_shape":[server_shape.origin.x,server_shape.origin.y],"circle":[xf.origin.x,xf.origin.y],"direct_current_Node_collide":circle.collide(xf,shape.shape,shape.global_transform),"direct_server_collide":circle.collide(xf,shape.shape,server_shape),"DirectSpaceState_overlap":overlap}
func on_audio(cue:StringName,_at:Vector2)->void:
 if cue!=&"impact_unarmed_metal" or qa_mode.is_empty():return
 qa_mode=""
 var before=raw_shape_proof()
 lab.training_bench.position+=Vector2(0,16)
 source_after_callback=lab.player.position;prop_after_callback=lab.training_bench.position
 immediate={"tick":Engine.get_physics_frames(),"before_change":before,"after_change":raw_shape_proof(),"source_mask":lab.player.collision_mask,"object_mask":lab.training_bench.collision_mask,"source_exceptions":ids(lab.player),"object_exceptions":ids(lab.training_bench),"damage_events":lab.combat.damage_events,"receipt_count":lab.combat.receipts.size()}
 pending=true
func observe_after_callback()->void:
 if not pending:return
 super.observe_after_callback()
 observed["raw_geometry_after_Core"]=raw_shape_proof()
func run()->void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false;lab.audio_event.connect(on_audio)
 var observer:=Observer.new();observer.qa=self;observer.process_physics_priority=1000;root.add_child(observer)
 await setup(2,false);qa_mode="clean_unforced_side_shift"
 await tap(KEY_F);await frames(25)
 var proof={"callback":immediate.duplicate(true),"same_tick_after_Core":observed.duplicate(true)}
 check("clean_callback_and_observer_same_tick",qa_mode.is_empty() and not observed.is_empty() and observed.tick==immediate.tick,proof)
 check("direct_current_Node_miss_with_old_PhysicsServer_contact",immediate.before_change.direct_current_Node_collide and not immediate.after_change.direct_current_Node_collide and immediate.after_change.DirectSpaceState_overlap and immediate.after_change.PhysicsServer_body!=immediate.after_change.Node_body,proof)
 check("production_postcallback_path_synced_PhysicsServer_to_current_Node",observed.raw_geometry_after_Core.PhysicsServer_body==observed.raw_geometry_after_Core.Node_body and not observed.raw_geometry_after_Core.DirectSpaceState_overlap and not observed.raw_geometry_after_Core.direct_current_Node_collide,proof)
 check("no_stale_motion_or_job_after_clean_callback",Vector2(observed.actor_delta[0],observed.actor_delta[1]).length()<0.0001 and Vector2(observed.prop_delta[0],observed.prop_delta[1]).length()<0.0001 and observed.jobs==0,proof)
 check("no_contact_or_mask_exception_side_effect",observed.damage_events==immediate.damage_events and observed.receipt_count==immediate.receipt_count and observed.source_mask==immediate.source_mask and observed.object_mask==immediate.object_mask and observed.source_exceptions==immediate.source_exceptions and observed.object_exceptions==immediate.object_exceptions,proof)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_CLEAN_CALLBACK_PRODUCTION_SYNC","phase_approval":false,"passed":passed,"checks":checks,"proof":proof,"probe_calls_runtime_eligibility_or_transform_flush":false},"  "));f.close()
 print("RESULT QA_TEGA_CLEAN_GEOMETRY passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
