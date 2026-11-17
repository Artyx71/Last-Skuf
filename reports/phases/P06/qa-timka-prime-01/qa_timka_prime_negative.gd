extends "res://tests/timka_prime_replay.gd"
## Independent QA-only APIs/metadata adversaries. Real Input earns vulnerability.
var receipt_observations:Array[Dictionary]=[]
func on_contact(event:Dictionary)->void:
 super.on_contact(event)
 var job:Dictionary=lab.combat.finisher_for(lab.player)
 var pose:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
 receipt_observations.append({"segment":segment,"id":event.id,"epoch":event.epoch,"target":event.target,"damage":event.damage,"finisher":event.finisher,"receipt_reserved":lab.combat.receipts.has(str(event.id)+":"+str(event.target)),"job_committed":job.get("committed",false),"job_elapsed":job.get("elapsed",0),"action_kind":lab.player.action_kind,"animation":String(lab.player.sprite.animation),"frame":lab.player.sprite.frame,"source_kind":pose.get_meta("source_kind",""),"original_source_column":pose.get_meta("original_source_column",-1)})
func snap()->Dictionary:
 return {"id":lab.player.get_instance_id(),"authority":lab.scene_policy.action_authority(lab.player.actor_id),"epoch":lab.combat.encounter_epoch,"attacks":lab.combat.attacks.duplicate(true),"receipts":lab.combat.receipts.duplicate(true),"action":lab.player.action_kind,"cost":lab.player.ability_cooldown,"options":lab.options_panel.visible,"state":lab.state}
func write_file(path:String,text:String)->void:
 var f=FileAccess.open(path,FileAccess.WRITE);f.store_string(text);f.close()
func run()->void:
 output=OS.get_environment("AYAY_QA_TIMKA_OUTPUT");headless=DisplayServer.get_name()=="headless";DirAccess.make_dir_recursive_absolute(output)
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2);lab.auto_retry=false;lab.combat.contact_committed.connect(on_contact);trace_enabled=true
 await tap(KEY_3);check("actual_present_fixture",lab.player.prepared_ability=="disengage")
 lab.player.use_ability();lab._set_options_visible(true);var before=snap()
 var base="res://assets/art/characters/timka/";var finpath=base+"finisher.json";var fin=FileAccess.get_file_as_string(finpath)
 write_file(finpath,"null")
 check("missing_FIN_denies_prime_atomically",not lab.select_fixture("timka_prime") and snap()==before)
 var present=preload("res://scripts/actors/character_player.gd").new()
 check("missing_FIN_still_allows_present_body",present.prepare_fixture("timka_present"));present.free();write_file(finpath,fin)
 var sockpath=base+"finisher.sockets.json";var sock=FileAccess.get_file_as_string(sockpath);var bad:Dictionary=JSON.parse_string(sock);bad.sheet_sha256="0".repeat(64);write_file(sockpath,JSON.stringify(bad))
 check("stale_FIN_garment_denies_prime_atomically",not lab.select_fixture("timka_prime") and snap()==before);write_file(sockpath,sock)
 check("FIN_metadata_restored_exact",FileAccess.get_file_as_string(finpath)==fin and FileAccess.get_file_as_string(sockpath)==sock)
 lab._set_options_visible(false)
 for reason in ["context","policy_instance","equipment"]:
  await tap(KEY_4);segment="QA_contact_authority_"+reason
  var target=await prime_target(Vector2.RIGHT);await tap(KEY_F);await frames(23)
  var job:Dictionary=lab.combat.finisher_for(lab.player)
  check(segment+":reservation_live_before_contact",not job.is_empty() and not job.committed and lab.player.action_elapsed<0.48 and lab.player.action_elapsed>0.35)
  check(segment+":equipment_UI_cannot_change_reserved_job",not lab.select_equipment(1))
  if reason=="context":lab.scene_policy.open("timka_present")
  if reason=="policy_instance":
   var newowner=preload("res://scripts/systems/character_scene_policy.gd").new();newowner.open("timka_prime");lab.player.scene_policy=newowner
  if reason=="equipment":lab.player.finisher_category="blunt";lab.player.finisher_weapon="blunt"
  await frames(12)
  check(segment+":contact_reauthorization_blocks_damage",target.health==1 and target.hits_received==1 and lab.combat.damage_events==1 and lab.score==0 and lab.combat.finisher_for(lab.player).is_empty())
  check(segment+":spent_cost_not_refunded",lab.player.ability_uses==1 and lab.player.ability_cooldown>0)
  await tap(KEY_4)
  check(segment+":atomic_switch_recovers_correct_body",lab.player._prepared_policy_matches_live() and lab.player.prepared_ability=="clinch" and lab.player.move_speed==118)
 segment="QA_receipt_once";var target=await prime_target(Vector2.RIGHT);await tap(KEY_F)
 var job:Dictionary=lab.combat.finisher_for(lab.player).duplicate(true);await frames(32)
 check("actual_clinch_receipt_and_once_reward",target.health==0 and target.hits_received==2 and lab.score==100 and lab.kills==1 and lab.player.ability_uses==1 and lab.combat.receipts.has(str(job.id)+":"+str(target.get_instance_id())))
 # Isolated adversarial resurrection makes duplicate rejection depend on receipt,
 # rather than merely the dead-target early return. This is not gameplay setup.
 target.health=1;var hits:int=target.hits_received;var damage:int=lab.combat.damage_events
 check("receipt_rejects_same_callback_even_if_health_positive",not lab.combat._apply_hit(target,job.definition,job.id,lab.player) and target.hits_received==hits and lab.combat.damage_events==damage and lab.score==100)
 target.health=0
 var passed=checks.all(func(c:Dictionary):return c.passed);var f=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"passed":passed,"scope":"QA_PRIME_DIRECT_ADVERSARIES_AND_REAL_INPUT_CONTACT_ONLY","phase_approval":false,"checks":checks,"contacts":contacts,"receipt_observations":receipt_observations,"trace":trace},"  "));f.close()
 print("RESULT QA_TIMKA_PRIME_NEGATIVE passed=%d failed=%d"%[checks.filter(func(c:Dictionary):return c.passed).size(),checks.filter(func(c:Dictionary):return not c.passed).size()])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
