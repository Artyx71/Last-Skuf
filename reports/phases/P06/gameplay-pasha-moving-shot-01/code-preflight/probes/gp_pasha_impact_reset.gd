extends "res://tests/pasha_moving_shot_replay.gd"
## External reviewer probe. Initial F is actual Input; no production source mutation.
class TailObserver:
 extends Node
 var review
 func _physics_process(_delta:float)->void:review.observe_after_Core()
var armed:=false
var pending:=false
var callback_proof:Dictionary={}
var observed:Dictionary={}
var committed_after_reset:Array=[]
func frames(count:int)->void:
 for i in count:
  await physics_frame
  await process_frame
func state_proof()->Dictionary:
 return {"tick":Engine.get_physics_frames(),"epoch":lab.combat.encounter_epoch,"damage_events":lab.combat.damage_events,"receipts":lab.combat.receipts.duplicate(true),"contact_events":lab.combat.contact_events.duplicate(true),"decals":lab.combat.impact.decals.size(),"particles":lab.combat.impact.particles.size(),"projectiles":lab.combat.projectiles.size(),"moving_jobs":lab.combat.moving_shots.jobs.size(),"ammo":lab.player.movement_ability.ammo,"rounds_spent":lab.player.movement_ability.rounds_spent}
func on_audio(cue:StringName,_at:Vector2)->void:
 if not armed or cue!=&"impact_firearm_body":return
 armed=false
 var before:=state_proof()
 var stack:=get_stack()
 var at:Vector2=lab.player.position
 lab.combat.reset()
 lab.player.reset(at)
 callback_proof={"cue":String(cue),"stack":stack,"before_reset":before,"after_reset":state_proof()}
 pending=true
func record_committed(event:Dictionary)->void:
 if not callback_proof.is_empty():committed_after_reset.append(event.duplicate(true))
func observe_after_Core()->void:
 if not pending:return
 pending=false
 observed=state_proof()
func run()->void:
 output=OS.get_environment("AYAY_GP_PASHA_PROBE_OUTPUT")
 if output.is_empty():preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,2);return
 headless=true;DirAccess.make_dir_recursive_absolute(output)
 root.get_node("OptionsStore").set_value(&"reduced_gore",false,false)
 root.get_node("OptionsStore").set_value(&"decals",true,false)
 lab=Lab.new();root.add_child(lab);current_scene=lab
 await frames(2);await tap(KEY_7);lab.auto_retry=false
 check("registered_Pasha_selected",lab.player.actor_id=="pasha" and lab.player.prepared_ability=="moving_shot")
 if lab.player.actor_id!="pasha":await finish_result();return
 await setup(2,90,1)
 lab.audio_event.connect(on_audio)
 lab.combat.contact_committed.connect(record_committed)
 var observer:=TailObserver.new();observer.review=self;observer.process_physics_priority=1000;root.add_child(observer)
 armed=true
 await tap(KEY_F)
 var budget:=100
 while observed.is_empty() and budget>0:await frames(1);budget-=1
 check("actual_impact_callback_and_same_tick_after_Core_observer",not armed and not callback_proof.is_empty() and not observed.is_empty() and observed.get("tick")==callback_proof.after_reset.tick)
 if not observed.is_empty():
  check("normal_reset_changed_epoch_and_cleared_collections_inside_callback",callback_proof.after_reset.epoch==callback_proof.before_reset.epoch+1 and callback_proof.after_reset.damage_events==0 and callback_proof.after_reset.contact_events.is_empty() and callback_proof.after_reset.receipts.is_empty() and callback_proof.after_reset.decals==0)
  check("old_hit_cannot_publish_contact_into_new_epoch",observed.contact_events.is_empty() and committed_after_reset.is_empty(),{"published_after_reset":committed_after_reset})
  check("old_hit_cannot_recreate_effects_or_damage_after_reset",observed.receipts.is_empty() and observed.damage_events==0 and observed.decals==0 and observed.particles==0)
 await finish_result()
func finish_result()->void:
 var passed:=checks.all(func(c:Dictionary):return c.passed)
 var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"scope":"GP_PASHA_PREFLIGHT_IMPACT_RESET_BASELINE","phase_approval":false,"runtime_approval":false,"actual_input":true,"passed":passed,"requires_clean_engine_log":true,"checks":checks,"callback":callback_proof,"same_tick_after_Core":observed,"committed_after_reset":committed_after_reset},"  "));file.close()
 print("RESULT GP_PASHA_IMPACT_RESET passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
