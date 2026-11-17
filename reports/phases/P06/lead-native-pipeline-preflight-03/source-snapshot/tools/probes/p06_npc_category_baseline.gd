extends "res://tests/gabar_combat_replay.gd"
## Independent supplemental BASELINE categories only. No deferred hero-style NPC drawings.
const PAIRS := [[1,"rusher","unarmed"],[1,"rusher","sharp"],[1,"rusher","firearm"],
 [2,"shooter","unarmed"],[2,"shooter","blunt"],[2,"shooter","firearm"],[2,"shooter","environmental"]]
const CATEGORIES := ["unarmed","blunt","sharp","firearm","environmental"]
var npc: CharacterBody2D
var npc_trace: Array[Dictionary]=[]
var npc_contacts: Array[Dictionary]=[]
var outcomes: Dictionary={}
var cases: Array[Dictionary]=[]
var current_category := ""
var current_reduced := false
func frames(count: int) -> void:
 for i in count:
  await super.frames(1)
  if is_instance_valid(npc):
   npc_trace.append({"segment":segment,"tick":Engine.get_physics_frames(),"wall_usec":Time.get_ticks_usec(),
    "kind":npc.kind,"state":npc.state,"health":npc.health,"hits":npc.hits_received,"animation":String(npc.sprite.animation),"frame":npc.sprite.frame,
    "timer":npc.timer,"attack_id":npc.attack_id,"jobs":lab.combat.finishers.size(),"damage_events":lab.combat.damage_events,"score":lab.score})
func on_contact(event: Dictionary) -> void:
 super.on_contact(event)
 if is_instance_valid(npc) and event.target==npc.get_instance_id():
  var item: Dictionary=event.duplicate(true)
  item.segment=segment;item.npc_kind=npc.kind;item.npc_state=npc.state;item.npc_animation=String(npc.sprite.animation);item.npc_frame=npc.sprite.frame
  item.player_animation=String(lab.player.sprite.animation);item.player_frame=lab.player.sprite.frame
  npc_contacts.append(item)
func pair_capture(label: String, expected_frame: int) -> void:
 if headless:return
 await RenderingServer.frame_post_draw
 var path: String=output.path_join(segment+"_"+label+".png")
 var code: int=root.get_texture().get_image().save_png(path)
 captures.append({"name":segment+"_"+label,"path":path,"code":code,"tick":Engine.get_physics_frames(),
  "npc_kind":npc.kind,"npc_state":npc.state,"npc_animation":String(npc.sprite.animation),"npc_frame":npc.sprite.frame,"player_animation":String(lab.player.sprite.animation),"player_frame":lab.player.sprite.frame})
 check(segment+":native_"+label,code==OK and npc.sprite.frame==expected_frame)
func setup_pair(index: int, category: String) -> void:
 npc=null
 lab.reset_encounter();lab.auto_retry=false
 lab.player.position=Vector2(300,240);lab.player.set_aim(Vector2.RIGHT)
 for enemy in lab.enemies:
  enemy.set_physics_process(false);enemy.position=Vector2(560,100)
 npc=lab.enemies[index];npc.position=Vector2(320,240);npc.health=1;npc.locked_aim=Vector2.LEFT
 lab.training_bench.position=npc.position+Vector2(24,0)
 lab.training_bench.set_meta("finisher_enabled",category=="environmental")
 check(segment+":legal_equipment",lab.select_equipment(CATEGORIES.find(category)))
 await frames(2)
 await tap(KEY_SPACE)
 var budget: int=40
 while npc.hits_received==0 and budget>0:await frames(1);budget-=1
 check(segment+":actual_Input_earned_stun",npc.health==1 and npc.hits_received==1 and npc.state=="stunned")
 npc.set_physics_process(true)
 while not lab.player.action_kind.is_empty() and budget>0:await frames(1);budget-=1
func run() -> void:
 output=OS.get_environment("AYAY_NPC_BASELINE_OUTPUT");headless=DisplayServer.get_name()=="headless"
 if output.is_empty():preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1);return
 DirAccess.make_dir_recursive_absolute(output)
 root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 var store: Node=root.get_node("OptionsStore")
 lab=Lab.new();root.add_child(lab);current_scene=lab;await frames(2)
 check("registered_Pasha_all_five_categories",lab.select_fixture("pasha_training"))
 lab.combat.contact_committed.connect(on_contact)
 trace_enabled=true
 for reduced in [false,true]:
  current_reduced=reduced
  store.set_value(&"reduced_gore",reduced,false);store.set_value(&"decals",not reduced,false)
  store.set_value(&"shake",0 if reduced else 100,false);store.set_value(&"flashes",not reduced,false);store.set_value(&"vhs",not reduced,false)
  for row in PAIRS:
   current_category=String(row[2]);segment=String(row[1])+"_"+current_category+"_"+("reduced" if reduced else "full")
   await setup_pair(int(row[0]),current_category)
   check(segment+":actual_kind",npc.kind==row[1])
   var before_player_hits: int=lab.player.hits_received
   await tap(KEY_V)
   var job: Dictionary=lab.combat.finisher_for(lab.player)
   check(segment+":reserved_real_finisher",not job.is_empty() and npc.state=="finisher_reaction" and npc.sprite.frame==0)
   if job.is_empty():continue
   var definition: Dictionary=job.definition.duplicate(true)
   var attack_id: int=int(job.id)
   # Actual protected-state branch, then let this live archetype's real FSM tick.
   npc.transition("attack",0.1);npc.hear_noise(lab.player.position)
   await frames(2)
   check(segment+":protected_FIN_rejects_attack_noise",npc.state=="finisher_reaction" and npc.health==1 and npc.attack_id==0 and lab.player.hits_received==before_player_hits)
   await pair_capture("windup",0)
   var budget: int=90
   while npc.health>0 and budget>0:await frames(1);budget-=1
   var hits: Array=npc_contacts.filter(func(e: Dictionary)->bool:return e.segment==segment and e.finisher)
   check(segment+":actual_same_contact_pose",hits.size()==1 and hits[0].npc_kind==row[1] and hits[0].npc_state=="dead" and hits[0].npc_frame==1 and hits[0].npc_animation=="finish_"+current_category+"_left" and hits[0].player_frame==1 and hits[0].player_animation=="finish_"+current_category+"_right" and hits[0].cue=="finish_pasha_"+current_category)
   check(segment+":real_once_reward_cost",npc.health==0 and npc.hits_received==2 and lab.kills==1 and lab.score==100 and lab.combat.damage_events==2 and lab.player.movement_ability.rounds_spent==(1 if current_category=="firearm" else 0))
   await pair_capture("contact",1)
   await frames(10)
   var texture: Texture2D=npc.sprite.sprite_frames.get_frame_texture(npc.sprite.animation,npc.sprite.frame)
   check(segment+":corpse2_and_actual_gore_variant",npc.state=="dead" and npc.sprite.frame==2 and texture is AtlasTexture and texture.atlas.resource_path.ends_with(String(row[1])+"_finishers"+("_reduced" if reduced else "")+".png"))
   await pair_capture("corpse",2)
   check(segment+":duplicate_receipt_rejected",not lab.combat._apply_hit(npc,definition,attack_id,lab.player))
   npc.transition("attack",0.1,true);npc.hear_noise(lab.player.position);npc.receive_knockdown(0.3)
   await frames(45)
   check(segment+":dead_absorbing_no_late_damage",npc.state=="dead" and npc.health==0 and npc.hits_received==2 and lab.player.hits_received==before_player_hits and lab.kills==1 and lab.score==100 and lab.combat.damage_events==2 and lab.combat.finishers.is_empty())
   var signature: Array=[npc.health,npc.hits_received,lab.kills,lab.score,lab.combat.damage_events,lab.player.movement_ability.rounds_spent,lab.player.hits_received,npc.state]
   var key: String=String(row[1])+":"+current_category
   if not reduced:outcomes[key]=signature
   else:check(segment+":Full_Reduced_same_gameplay",outcomes.get(key)==signature)
   cases.append({"segment":segment,"archetype":row[1],"category":current_category,"mode":"reduced" if reduced else "full","direction":"player_right_NPC_left","signature":signature,"attack_id":attack_id})
   # Freeze only the settled corpse to observe the exact reset snapshot without fresh AI advancement.
   npc.set_physics_process(false)
   await tap(KEY_R)
   check(segment+":Input_reset_clears_baseline",lab.score==0 and lab.kills==0 and lab.combat.damage_events==0 and lab.combat.finishers.is_empty() and lab.combat.projectiles.is_empty() and lab.combat.attacks.is_empty() and lab.combat.impact.particles.is_empty() and lab.combat.impact.decals.is_empty() and npc.health==1 and npc.state=="patrol" and npc.reaction_category.is_empty() and lab.player.movement_ability.ammo==4 and lab.player.movement_ability.rounds_spent==0)
 var passed: bool=not checks.is_empty() and checks.all(func(c: Dictionary)->bool:return c.passed)
 var file: FileAccess=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"schema":1,"scope":"P06_BASELINE_SHARED_NPC_CATEGORY_SUPPLEMENT_ONLY","passed":passed,"actual_input":true,"renderer":DisplayServer.get_name(),"phase_approval":false,"deferred_C09_style_implemented":false,"fixture":"registered Pasha training; seven missing NPC/category pairs, right direction, Input-earned stun, live protected FIN+death+reset; finiteammo reset everycase","checks":checks,"cases":cases,"contacts":npc_contacts,"trace":npc_trace,"captures":captures,"Full_Reduced_signatures":outcomes,"not_tested":["new hero-style NPC art","all directions in this supplemental fixture","performance/FPS/hardwarelatency","native Windows","agent listening","full P06"]},"  "));file.close()
 print("NPC_BASELINE_RESULT ",checks.filter(func(c:Dictionary)->bool:return c.passed).size(),"/",checks.size())
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
