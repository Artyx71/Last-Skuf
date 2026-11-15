extends "res://tests/tega_environment_replay.gd"
## QA-only collider fixture. Measure stop AFTER the actual block; fractional first steps may fit.
func frames(count: int) -> void:
 for i in count:
  await physics_frame
  await process_frame
func run() -> void:
 output=OS.get_environment("AYAY_P06_TEGA_OUTPUT");headless=true
 DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_6);lab.auto_retry=false
 await setup(2,false)
 var wall=make_wall(lab.player.position+Vector2(10,-1),Vector2(1,2))
 await frames(2)
 var actor_origin:Vector2=lab.player.position
 var prop_origin:Vector2=lab.training_bench.position
 check("foot_target_valid_actor_sweep_blocked_prop_sweep_clear",lab.combat.environment_kicks.find_object(lab.player,Vector2.RIGHT)==lab.training_bench and lab.player.test_move(lab.player.global_transform,Vector2(3.5,0)) and not lab.training_bench.test_move(lab.training_bench.global_transform,Vector2(3.5,0)))
 await tap(KEY_F)
 var budget:int=40
 var blocked:Array=[]
 while budget>0:
  blocked=lab.combat.environment_kicks.history.filter(func(e:Dictionary):return e.stage=="actor_blocked")
  if not blocked.is_empty():break
  await frames(1);budget-=1
 var at_block:Vector2=lab.player.position
 var prop_at_block:Vector2=lab.training_bench.position
 var distance:float=lab.player.ability_distance
 var history:Array=lab.combat.environment_kicks.history.duplicate(true)
 var proof={"actor_origin":[actor_origin.x,actor_origin.y],"prop_origin":[prop_origin.x,prop_origin.y],"actor_at_block":[at_block.x,at_block.y],"prop_at_block":[prop_at_block.x,prop_at_block.y],"distance_at_block":distance,"clock":lab.player.action_elapsed,"frame":lab.player.action_frame,"history":history}
 check("actual_actor_block_during_active_pose",blocked.size()==1 and lab.player.action_frame==1,proof)
 check("preblock_fractional_travel_coupled_and_bounded",distance>=0 and distance<3.5 and (at_block-actor_origin).distance_to(prop_at_block-prop_origin)<0.02,proof)
 await frames(45)
 check("both_stable_after_block_no_contact_or_late_motion",lab.player.position==at_block and lab.training_bench.position==prop_at_block and lab.player.ability_distance==distance and lab.combat.damage_events==0 and lab.combat.environment_kicks.jobs.is_empty() and lab.player.collision_mask==1 and lab.training_bench.collision_mask==6,proof)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_TEGA_ACTOR_ONLY_WALL_BOUNDARY","passed":passed,"phase_approval":false,"checks":checks,"proof":proof},"  "));f.close()
 print("RESULT QA_TEGA_WALL passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
