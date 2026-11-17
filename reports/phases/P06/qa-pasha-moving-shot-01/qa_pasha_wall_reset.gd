extends "res://tests/pasha_moving_shot_replay.gd"
## Independent wall-audio callback branch probe; not Gameplay body-impact/free probes.
class Observer:
 extends Node
 var qa
 func _physics_process(_delta:float)->void:qa.observe_after_wall()
var branch:=""
var reset_requested:=false
var pending:=false
var before_callback:Dictionary={}
var immediate:Dictionary={}
var after:Dictionary={}
var proofs:Array[Dictionary]=[]
func frames(count:int)->void:
 for i in count:
  await physics_frame
  await process_frame
func on_audio(cue:StringName,at:Vector2)->void:
 if cue!=&"impact_firearm_concrete" or not before_callback.is_empty():return
 before_callback={"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,"projectiles":lab.combat.projectiles.size(),"at":[at.x,at.y],"action_frame":lab.player.action_frame,"ammo":lab.player.movement_ability.ammo}
 if reset_requested:
  var location:Vector2=lab.player.position
  lab.combat.reset();lab.player.reset(location)
 immediate={"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,"hit_flash":lab.combat.hit_flash,"last_hit_position":[lab.combat.last_hit_position.x,lab.combat.last_hit_position.y]}
 pending=true
func observe_after_wall()->void:
 if not pending:return
 pending=false
 after={"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,"hit_flash":lab.combat.hit_flash,"last_hit_position":[lab.combat.last_hit_position.x,lab.combat.last_hit_position.y],"wall_impacts":lab.combat.wall_impacts,"projectiles":lab.combat.projectiles.size(),"jobs":lab.combat.moving_shots.jobs.size(),"ammo":lab.player.movement_ability.ammo,"rounds_spent":lab.player.movement_ability.rounds_spent,"damage_events":lab.combat.damage_events,"score":lab.score,"source_layer":lab.player.collision_layer,"source_mask":lab.player.collision_mask,"source_exceptions":lab.player.get_collision_exceptions().size()}
func run()->void:
 output=OS.get_environment("AYAY_P06_PASHA_OUTPUT");headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);await tap(KEY_7);lab.auto_retry=false;lab.audio_event.connect(on_audio)
 var observer:=Observer.new();observer.qa=self;observer.process_physics_priority=1000;root.add_child(observer)
 for which in ["muzzle","travel"]:
  for reset in [false,true]:
   await setup(2,170,8)
   branch=which;reset_requested=reset;before_callback={};immediate={};after={}
   var wall:StaticBody2D=StaticBody2D.new();wall.position=lab.player.position+Vector2(10 if which=="muzzle" else 44,-7);wall.collision_layer=1
   var cs:=CollisionShape2D.new();var rect:=RectangleShape2D.new();rect.size=Vector2(2,16);cs.shape=rect;wall.add_child(cs);lab.add_child(wall)
   await frames(2);await tap(KEY_F);await frames(20)
   var label:=which+("_reset" if reset else "_control")
   var proof={"branch":which,"reset":reset,"before_callback":before_callback.duplicate(true),"immediate_after_callback":immediate.duplicate(true),"after_Core_same_tick":after.duplicate(true)};proofs.append(proof)
   check(label+":actual_wall_branch_same_tick_observed",not before_callback.is_empty() and not after.is_empty() and before_callback.projectiles==(0 if which=="muzzle" else 1) and after.tick==immediate.tick,proof)
   if after.is_empty():wall.queue_free();await frames(2);continue
   if reset:
    check(label+":reset_really_cleared_state_inside_listener",immediate.epoch==before_callback.epoch+1 and immediate.hit_flash==0 and immediate.last_hit_position==[0.0,0.0],proof)
    check(label+":old_wall_callback_cannot_restore_flash_in_new_epoch",after.epoch==immediate.epoch and after.hit_flash==0 and after.last_hit_position==[0.0,0.0],proof)
    check(label+":reset_ammo_jobs_masks_and_damage_remain_clean",after.ammo==4 and after.rounds_spent==0 and after.jobs==0 and after.projectiles==0 and after.damage_events==0 and after.score==0 and after.source_layer==2 and after.source_mask==1 and after.source_exceptions==0,proof)
   else:
    check(label+":positive_control_real_wall_flash",after.epoch==before_callback.epoch and after.wall_impacts==1 and after.hit_flash>0 and after.last_hit_position!=[0.0,0.0],proof)
    check(label+":one_actual_round_spent",after.ammo==3 and after.rounds_spent==1,proof)
    check(label+":no_NPC_damage_or_collision_mask_changes",after.damage_events==0 and after.score==0 and after.source_layer==2 and after.source_mask==1 and after.source_exceptions==0,proof)
   wall.queue_free();await frames(2)
 var passed=checks.all(func(c:Dictionary):return c.passed)
 var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_PASHA_WALL_AUDIO_EPOCH_BASELINE","phase_approval":false,"passed":passed,"checks":checks,"proofs":proofs,"not_Gameplay_body_impact_or_target_free_probe":true},"  "));f.close()
 print("RESULT QA_PASHA_WALL passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
