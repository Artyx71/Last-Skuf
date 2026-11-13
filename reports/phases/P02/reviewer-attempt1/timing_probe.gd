extends SceneTree
func _initialize() -> void:
 call_deferred("_run")
func _run() -> void:
 var lab = load("res://scenes/world/combat_lab.tscn").instantiate()
 root.add_child(lab)
 await physics_frame
 await physics_frame
 lab.reset_encounter()
 lab.auto_retry = false
 lab.set_kit("training")
 lab.player.position = Vector2(58, 284)
 lab.player.set_aim(Vector2.RIGHT)
 for e in lab.enemies:
  e.set_physics_process(false)
  e.position = Vector2(500, 90)
 lab.enemies[0].position = Vector2(88, 284)
 lab.enemies[0].health = 3
 await physics_frame
 await physics_frame
 var rows = []
 var started = Time.get_ticks_usec()
 Input.action_press("attack_melee")
 for tick in 12:
  await physics_frame
  await process_frame
  rows.append({"tick":tick,"ms":float(Time.get_ticks_usec()-started)/1000.0,"animation":String(lab.player.sprite.animation),"frame":lab.player.sprite.frame,"progress":lab.player.sprite.frame_progress,"hits":lab.enemies[0].hits_received,"health":lab.enemies[0].health})
  if tick == 1:
   Input.action_release("attack_melee")
 var early = false
 for row in rows:
  if row.animation == "shove_right" and row.frame == 0 and row.hits > 0:
   early = true
 var result = {"expected_contact_frame":1,"authored_fps":12,"damage_during_windup_observed":early,"rows":rows,"passed":not early}
 var f = FileAccess.open(OS.get_environment("AYAY_TIMING_RESULT"), FileAccess.WRITE)
 f.store_string(JSON.stringify(result,"  "))
 print("TIMING_PROBE ",JSON.stringify(result))
 quit(1 if early else 0)
