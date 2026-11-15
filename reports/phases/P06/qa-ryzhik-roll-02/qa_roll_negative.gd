extends "res://tests/ryzhik_roll_replay.gd"
## QA-only metadata/authority adversaries; normal Input owns the measured roll.
var observations:Array[Dictionary]=[]
func on_contact(event:Dictionary)->void:
 super.on_contact(event)
 var pose:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
 observations.append({"segment":segment,"id":event.id,"target":event.target,"tick":event.tick,"receipt_reserved":lab.combat.receipts.has(str(event.id)+":"+str(event.target)),"frame":lab.player.action_frame,"clock":lab.player.action_elapsed,"kind":pose.get_meta("source_kind",""),"column":pose.get_meta("source_column",-1),"score":lab.score,"damage":event.damage})
func snap()->Dictionary:
 return {"id":lab.player.get_instance_id(),"authority":lab.scene_policy.action_authority(lab.player.actor_id),"epoch":lab.combat.encounter_epoch,"attacks":lab.combat.attacks.duplicate(true),"receipts":lab.combat.receipts.duplicate(true),"cooldown":lab.player.ability_cooldown,"action":lab.player.action_kind,"options":lab.options_panel.visible,"state":lab.state}
func write_file(path:String,text:String)->void:
 var f=FileAccess.open(path,FileAccess.WRITE);f.store_string(text);f.close()
func run()->void:
 output=OS.get_environment("AYAY_P06_RYZHIK_OUTPUT");headless=DisplayServer.get_name()=="headless";DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact)
 check("real_pending_Gabar_action",lab.player.use_ability() and not lab.combat.attacks.is_empty());lab._set_options_visible(true);var before=snap()
 var path="res://assets/art/characters/ryzhik/roll.json";var original=FileAccess.get_file_as_string(path)
 write_file(path,"null");check("missing_roll_refuses_atomically",not lab.select_fixture("ryzhik_training") and snap()==before)
 var wrong:Dictionary=JSON.parse_string(original);wrong.actor_id="gabar";write_file(path,JSON.stringify(wrong));check("wrong_roll_identity_refuses_atomically",not lab.select_fixture("ryzhik_training") and snap()==before);write_file(path,original)
 var socket="res://assets/art/characters/ryzhik/roll.sockets.json";var saved=FileAccess.get_file_as_string(socket);wrong=JSON.parse_string(saved);wrong.sheet_sha256="0".repeat(64);write_file(socket,JSON.stringify(wrong));check("stale_roll_socket_refuses_atomically",not lab.select_fixture("ryzhik_training") and snap()==before);write_file(socket,saved)
 check("metadata_restored_exact",FileAccess.get_file_as_string(path)==original and FileAccess.get_file_as_string(socket)==saved)
 lab._set_options_visible(false);await tap(KEY_5);check("own_strategy_loaded",lab.player.actor_id=="ryzhik" and lab.player.movement_ability!=null)
 for index in [2,3]:check("latent_tool_no_grant_"+str(index),not lab.select_equipment(index))
 var foreign=Roll.new();var cost:float=lab.player.ability_cooldown;check("foreign_strategy_instance_cannot_start",not foreign.start(lab.player) and lab.player.ability_cooldown==cost and lab.player.ability_uses==0)
 var target=await roll_fixture(2);segment="QA_landing_revoke_reentry";var second=lab.enemies[1];second.position=target.position+Vector2(0,4);await frames(2);revoke_on_contact=true
 await tap(KEY_F);await frames(38)
 check("one_actual_overlap_before_revocation",target.hits_received+second.hits_received==1 and lab.combat.damage_events==1)
 check("per_recipient_authority_stops_second_contact",lab.combat.receipts.size()==1 and lab.combat.attacks.is_empty() and lab.player.action_kind!="roll" and lab.score==0)
 check("revocation_does_not_refund_cost",lab.player.ability_uses==1 and lab.player.ability_cooldown>0)
 lab.scene_policy.open("ryzhik_training");target=await roll_fixture(2);segment="QA_alive_duplicate_receipt";await tap(KEY_F);await frames(27)
 var id:int=lab.player.melee_attack_id;var token=str(id)+":"+str(target.get_instance_id());check("alive_target_has_actual_landing_receipt",target.health==1 and target.hits_received==1 and lab.combat.receipts.has(token) and lab.player.action_frame==6)
 var damage:int=lab.combat.damage_events;check("duplicate_callback_rejected_while_target_alive",not lab.combat._apply_hit(target,{"damage":1,"stun":0.0,"category":"unarmed"},id,lab.player) and target.health==1 and target.hits_received==1 and lab.combat.damage_events==damage and lab.score==0)
 lab.player.cancel_action();var stopped:Vector2=lab.player.position;await frames(4);check("cancel_no_later_motion_or_contact",lab.player.position.distance_to(stopped)<0.001 and target.hits_received==1 and lab.combat.attacks.is_empty())
 lab.scene_policy.open("timka_present");check("other_actor_policy_cannot_grant_actions",not lab.player.use_ability() and not lab.player.attack_melee() and not lab.player.can_use_finisher("unarmed"));key(KEY_D,true);await frames(4);key(KEY_D,false);check("other_actor_policy_no_locomotion",lab.player.position.distance_to(stopped)<0.001)
 await tap(KEY_5);check("atomic_host_reselection_recovers",lab.player.actor_id=="ryzhik" and lab.player._prepared_policy_matches_live() and lab.player.move_speed==120)
 var passed=checks.all(func(c:Dictionary):return c.passed);var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"QA_ROLL_ADVERSARIES_ONLY","passed":passed,"phase_approval":false,"checks":checks,"observations":observations},"  "));f.close();print("RESULT QA_ROLL_NEGATIVE passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
