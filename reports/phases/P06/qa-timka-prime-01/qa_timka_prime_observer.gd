extends "res://tests/timka_prime_replay.gd"
## Observation only; inherited original Input/tests/time/coverage unchanged.
func on_contact(event:Dictionary)->void:
 super.on_contact(event)
 var item:Dictionary=contacts.back()
 var job:Dictionary=lab.combat.finisher_for(lab.player)
 var pose:Texture2D=lab.player.sprite.sprite_frames.get_frame_texture(lab.player.sprite.animation,lab.player.sprite.frame)
 var target:Node=instance_from_id(event.target)
 item.qa_receipt_reserved=lab.combat.receipts.has(str(event.id)+":"+str(event.target))
 item.qa_receipt_count=lab.combat.receipts.size()
 item.qa_job_committed=job.get("committed",false)
 item.qa_job_elapsed=job.get("elapsed",0)
 item.qa_job_category=job.get("category","")
 item.qa_definition=job.get("definition",{}).duplicate(true)
 item.qa_prepared_fixture=lab.player.prepared_definition.get("scene_id","")
 item.qa_prepared_matches=lab.player._prepared_policy_matches_live()
 item.qa_pose_kind=pose.get_meta("source_kind","")
 item.qa_pose_original_column=pose.get_meta("original_source_column",-1)
 item.qa_target_state="player" if target==lab.player else target.get("state")
 item.qa_target_health=target.get("health")
 item.qa_target_hits=target.get("hits_received")
 item.qa_target_stun=0.0 if target==lab.player else target.get("stun_remaining")
 item.qa_target_impulse=[target.impulse.x,target.impulse.y]
 item.qa_target_frame=target.sprite.frame
 item.qa_target_animation=String(target.sprite.animation)
 item.qa_actual_score=lab.score
 item.qa_actual_kills=lab.kills
 item.qa_actual_ability_uses=lab.player.ability_uses
 item.qa_actual_cooldown=lab.player.ability_cooldown
 item.qa_previous_trace=trace.back().duplicate(true) if not trace.is_empty() else {}
 contacts[contacts.size()-1]=item
