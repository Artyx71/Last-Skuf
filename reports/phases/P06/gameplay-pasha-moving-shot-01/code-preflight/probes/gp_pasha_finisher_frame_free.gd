extends "res://tests/pasha_moving_shot_replay.gd"
## Reachable enemy frame0->1 is set inside Core; source frame1 alone is not proof.
class TailObserver:
 extends Node
 var review
 func _physics_process(_delta:float)->void:review.observe_after_Core()
var watched_target:Variant
var armed:=false
var pending:=false
var callback_proof:Dictionary={}
var observed:Dictionary={}
func frames(count:int)->void:
 for i in count:
  await physics_frame
  await process_frame
func state_proof()->Dictionary:
 var jobs:Array=[]
 for job in lab.combat.finishers:
  jobs.append({"id":job.id,"epoch":job.epoch,"committed":job.committed,"source_live":is_instance_valid(job.source),"target_live":is_instance_valid(job.target)})
 return {"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,"damage_events":lab.combat.damage_events,"receipts":lab.combat.receipts.duplicate(true),"contact_events":lab.combat.contact_events.duplicate(true),"score":lab.score,"ammo":lab.player.movement_ability.ammo,"rounds_spent":lab.player.movement_ability.rounds_spent,"finishers":jobs,"target_live":is_instance_valid(watched_target)}
func on_audio(_cue:StringName,_at:Vector2)->void:pass
func target_frame_changed()->void:
 if not armed or not is_instance_valid(watched_target):return
 if watched_target.state!="finisher_reaction" or not String(watched_target.sprite.animation).begins_with("finish_firearm_") or watched_target.sprite.frame!=1:return
 var stack:=get_stack()
 var inside_Core:=false
 for entry in stack:
  if entry.get("function","")=="_tick_finishers" and String(entry.get("source","")).ends_with("combat_system.gd"):inside_Core=true
 if not inside_Core:
  # Do not free on an earlier Player/NPC presentation and call it a Core callback.
  return
 armed=false
 callback_proof={"stack":stack,"inside_Core_tick_finishers":inside_Core,"before_free":state_proof(),"target_state":watched_target.state,"target_animation":String(watched_target.sprite.animation),"target_frame":watched_target.sprite.frame,"target_id":watched_target.get_instance_id()}
 # Remove only the actual despawned target from the lab's loose collection.
 # No later reset/iteration of a freed enemy is used by this probe.
 lab.enemies.erase(watched_target)
 watched_target.free()
 callback_proof["free_effective"]=not is_instance_valid(watched_target)
 callback_proof["after_free"]=state_proof()
 pending=true
func observe_after_Core()->void:
 if not pending:return
 pending=false
 observed=state_proof()
func run()->void:
 output=OS.get_environment("AYAY_GP_PASHA_PROBE_OUTPUT")
 if output.is_empty():preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,2);return
 headless=true;DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab
 await frames(2);await tap(KEY_7);lab.auto_retry=false
 check("registered_Pasha_selected",lab.player.actor_id=="pasha" and lab.player.prepared_ability=="moving_shot")
 if lab.player.actor_id!="pasha":await finish_result();return
 watched_target=await setup(2,20,1)
 await tap(KEY_SPACE)
 var budget:=50
 while watched_target.hits_received==0 and budget>0:await frames(1);budget-=1
 check("vulnerability_earned_by_actual_Input_shove",watched_target.hits_received==1 and watched_target.health==1 and watched_target.state=="stunned")
 watched_target.set_physics_process(true)
 while not lab.player.action_kind.is_empty() and budget>0:await frames(1);budget-=1
 check("firearm_tool_selected_from_registered_policy",lab.select_equipment(3) and lab.player.can_use_finisher("firearm"))
 watched_target.sprite.frame_changed.connect(target_frame_changed)
 var observer:=TailObserver.new();observer.review=self;observer.process_physics_priority=1000;root.add_child(observer)
 armed=true
 await tap(KEY_V)
 budget=100
 while observed.is_empty() and budget>0:await frames(1);budget-=1
 check("target_contact1_callback_reached_inside_real_Core",not armed and not observed.is_empty() and callback_proof.get("inside_Core_tick_finishers",false))
 if not observed.is_empty():
  check("target_really_freed_and_observer_same_tick",callback_proof.free_effective and observed.tick==callback_proof.before_free.tick)
  check("target_loss_does_not_consume_firearm_round_or_commit_damage",observed.rounds_spent==0 and observed.ammo==4 and observed.damage_events==callback_proof.before_free.damage_events and observed.score==0 and observed.contact_events==callback_proof.before_free.contact_events)
  await frames(3)
  check("freed_target_reservation_eventually_removed",lab.combat.finishers.is_empty())
 await finish_result()
func finish_result()->void:
 var passed:=checks.all(func(c:Dictionary):return c.passed)
 var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"scope":"GP_PASHA_PREFLIGHT_FINISHER_FRAME_FREE_BASELINE","phase_approval":false,"runtime_approval":false,"actual_input":true,"passed":passed,"requires_clean_engine_log":true,"checks":checks,"callback":callback_proof,"same_tick_after_Core":observed,"inconclusive_if_free_not_effective":true},"  "));file.close()
 print("RESULT GP_PASHA_FINISHER_FREE passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
