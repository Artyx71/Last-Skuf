extends "res://tests/timka_present_replay.gd"
## QA-only observation. Calls inherited production replay unchanged.
func on_contact(event:Dictionary)->void:
 super.on_contact(event)
 var item:Dictionary=contacts.back()
 var token=str(event.id)+":"+str(event.target)
 item.qa_actual_receipt_token=token
 item.qa_actual_receipt_reserved=lab.combat.receipts.has(token)
 item.qa_actual_receipt_count=lab.combat.receipts.size()
 item.qa_damage_events=lab.combat.damage_events
 item.qa_health_after=lab.player.health
 item.qa_hits_received=lab.player.hits_received
 item.qa_action_after=lab.player.action_kind
 item.qa_counter_blocks=lab.player.counter_blocks
 item.qa_score=lab.score
 item.qa_collision_mask=lab.player.collision_mask
 item.qa_collision_layer=lab.player.collision_layer
 item.qa_active_fixture=lab.scene_policy.definition().get("scene_id","")
 item.qa_previous_trace=trace.back().duplicate(true) if not trace.is_empty() else {}
 contacts[contacts.size()-1]=item
