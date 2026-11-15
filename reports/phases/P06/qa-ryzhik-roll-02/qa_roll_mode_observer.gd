extends "res://tests/ryzhik_roll_replay.gd"
## Observation only. Inherited actualInput/coverage/assertions unchanged.
func on_contact(event:Dictionary)->void:
 super.on_contact(event)
 var item:Dictionary=contacts.back()
 var mode:bool=bool(root.get_node("OptionsStore").values.reduced_gore)
 item.qa_actual_reduced_mode=mode
 item.qa_impact_reduced_mode=lab.combat.impact.reduced()
 item.qa_receipt_reserved=lab.combat.receipts.has(str(event.id)+":"+str(event.target))
 if event.finisher and not item.target_is_player:
  var target:Node=instance_from_id(event.target)
  var texture:Texture2D=target.sprite.sprite_frames.get_frame_texture(target.sprite.animation,target.sprite.frame)
  item.qa_NPC_contact_frame=target.sprite.frame
  item.qa_NPC_state=target.get("state")
  item.qa_NPC_health=target.get("health")
  item.qa_NPC_palette_bound=texture is AtlasTexture and texture.has_meta("full_atlas") and texture.atlas==texture.get_meta("reduced_atlas" if mode else "full_atlas")
 contacts[contacts.size()-1]=item
