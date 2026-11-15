extends "res://tests/gabar_combat_replay.gd"
## Actual Input -> earned stun -> Core contact -> live stream, on one physics clock.
const Routes = preload("res://scripts/systems/character_finisher_audio.gd")
const LegacyLab = preload("res://scripts/core/combat_lab.gd")
const CATEGORIES := ["unarmed","blunt","sharp","firearm","environmental"]
const FIXTURES := {
 "gabar_training":["unarmed","blunt","firearm"],"olezhka_training":["unarmed","blunt","sharp"],
 "timka_prime":["unarmed","blunt","environmental"],"ryzhik_training":["unarmed","blunt","environmental"],
 "tega_training":["unarmed","blunt","environmental"],"pasha_training":CATEGORIES}
var audio: Node
var audio_events: Array[Dictionary]=[]
var route_results: Array[Dictionary]=[]
var capture_data: Dictionary={}
var active_capture := ""
var capture_started_usec := 0
var solo_events: Array[Dictionary]=[]
var stress_events: Array[Dictionary]=[]
var headroom_only := false

func frames(count: int) -> void:
 for i in count:
  await super.frames(1)
  await create_timer(0.0).timeout

func check(label: String, ok: bool, details: Dictionary={}) -> void:
 checks.append({"name":label,"passed":ok,"details":details.duplicate(true)})
 if not ok: push_error("FAIL C01_RUNTIME "+label)

func playing_streams(cue: String) -> Array:
 var result: Array=[]
 var entry: Dictionary=audio.manifest.sfx.get(cue,{})
 for pool in [audio.voices,audio.spatial_voices]:
  for voice in pool:
   if not voice.playing or voice.stream==null or voice.stream.resource_path!=entry.get("path"): continue
   result.append({"path":voice.stream.resource_path,"instance_id":voice.get_instance_id(),
    "bus":String(voice.bus),"gain_db":voice.volume_db,"pitch":voice.pitch_scale,
    "duration":voice.stream.get_length(),"rate":voice.stream.mix_rate,"stereo":voice.stream.stereo,
    "format":voice.stream.format,"loop":voice.stream.loop_mode})
 return result

func on_audio(cue: StringName, _at: Vector2) -> void:
 if not String(cue).begins_with("finish_"): return
 audio_events.append({"segment":segment,"cue":String(cue),"tick":Engine.get_physics_frames(),
  "epoch":lab.combat.encounter_epoch,"source_pose":lab.player.action_frame,
  "source_animation":String(lab.player.sprite.animation),"streams":playing_streams(String(cue)),
  "capture":active_capture,"capture_elapsed":float(Time.get_ticks_usec()-capture_started_usec)/1000000.0})

func on_contact(event: Dictionary) -> void:
 super.on_contact(event)
 if event.finisher:
  var rows: Array=audio_events.filter(func(e: Dictionary) -> bool: return e.segment==segment and e.cue==event.cue)
  var same: bool=rows.size()==1 and rows[0].tick==event.tick and rows[0].epoch==event.epoch and rows[0].source_pose==1
  var streams: Array=rows[0].streams if rows.size()==1 else []
  var entry: Dictionary=audio.manifest.sfx.get(event.cue,{})
  var gain: float=float(entry.get("gain_db",-100.0))
  if root.get_node("OptionsStore").values.reduced_impact: gain-=5.0
  check(segment+":same_contact_tick_pose_and_one_actual_voice",same and streams.size()==1 and streams[0].bus=="SFX" and is_equal_approx(streams[0].gain_db,gain) and streams[0].pitch==1.0 and streams[0].loop==AudioStreamWAV.LOOP_DISABLED,{"contact":event,"audio":rows})

func prepare(category: String, equipment_allowed := true) -> CharacterBody2D:
 lab.reset_encounter();lab.auto_retry=false
 # Same close initial spacing as the accepted prime fixture: the heavy shove
 # moves the NPC ~6px. Starting at30 lets that real impulse leave unarmed35
 # range before contact; initial26 retains legal geometry without changing it.
 lab.player.position=Vector2(254,270);lab.player.set_aim(Vector2.RIGHT)
 for enemy in lab.enemies:
  enemy.set_physics_process(false);enemy.position=Vector2(560,100)
 var target: CharacterBody2D=lab.enemies[0]
 target.position=Vector2(280,270)
 lab.training_bench.position=Vector2(304,270)
 lab.training_bench.set_meta("finisher_enabled",category=="environmental")
 if category!="environmental":lab.training_bench.position=Vector2(450,270)
 check(segment+":equipment_policy",lab.select_equipment(CATEGORIES.find(category))==equipment_allowed)
 await frames(2)
 await tap(KEY_SPACE)
 var budget:=70
 while not lab.player.action_kind.is_empty() and budget>0:
  await frames(1);budget-=1
 check(segment+":Input_earned_stun",target.health==1 and target.hits_received==1 and target.state=="stunned")
 return target

func complete_route(category: String, expected: String) -> void:
 var target:=await prepare(category)
 target.set_physics_process(true)
 await tap(KEY_V)
 check(segment+":Input_V_reserves_finisher",not lab.combat.finisher_for(lab.player).is_empty() and lab.player.action_frame==0)
 var budget:=110
 while target.health>0 and budget>0:
  await frames(1);budget-=1
 var rows: Array=audio_events.filter(func(e: Dictionary) -> bool:return e.segment==segment)
 check(segment+":correct_stream_kill_once",target.health==0 and target.hits_received==2 and lab.combat.damage_events==2 and lab.kills==1 and lab.score==100 and rows.size()==1 and rows[0].cue==expected)
 await capture(segment+"_contact")
 await frames(2)
 budget=110
 while not lab.player.action_kind.is_empty() and budget>0:
  await frames(1);budget-=1
 await tap(KEY_V);await frames(3)
 rows=audio_events.filter(func(e: Dictionary) -> bool:return e.segment==segment)
 check(segment+":no_second_sound_damage_score",rows.size()==1 and lab.combat.damage_events==2 and lab.kills==1 and lab.score==100 and lab.combat.finishers.is_empty())
 route_results.append({"segment":segment,"cue":expected,"health":target.health,"hits":target.hits_received,
  "damage_events":lab.combat.damage_events,"score":lab.score,"kills":lab.kills,"audio_events":rows,
  "ammo":lab.player.movement_ability.ammo if lab is Lab and lab.player.actor_id=="pasha" else -1})

func capture_begin(name: String) -> void:
 if headless:return
 active_capture=name;capture_started_usec=Time.get_ticks_usec()
 check(name+":actual_mixer_record_begins",audio.begin_capture())
 capture_data[name]={"start_usec":capture_started_usec,"clock":audio.clock,"driver":AudioServer.get_driver_name(),"output_latency":AudioServer.get_output_latency(),"mix_rate":AudioServer.get_mix_rate()}

func capture_end() -> void:
 if headless:return
 var name:=active_capture
 capture_data[name]["end_usec"]=Time.get_ticks_usec()
 var path:=output.path_join(name+".wav")
 var code: int=audio.end_capture(path)
 capture_data[name]["path"]=path;capture_data[name]["code"]=code
 check(name+":actual_mixer_record_saved",code==OK and FileAccess.file_exists(path))
 active_capture=""

func run() -> void:
 output=OS.get_environment("AYAY_C01_OUTPUT");headless=DisplayServer.get_name()=="headless"
 headroom_only="--c01-headroom-only" in OS.get_cmdline_user_args()
 if output.is_empty():preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1);return
 DirAccess.make_dir_recursive_absolute(output)
 root.content_scale_size=Vector2i(640,360);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
 var options: Node=root.get_node("OptionsStore")
 options.set_value(&"vhs",false,false);options.set_value(&"shake",0,false)
 audio=root.get_node("AudioDirector")
 check("actual_assets_ready",audio.ready_assets)
 if not audio.ready_assets:preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1);return
 var starts: int=audio.stem_starts
 lab=Lab.new();root.add_child(lab);current_scene=lab;lab.auto_retry=false
 lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
 await frames(30)
 if not headless:check("real_mixer_driver",AudioServer.get_driver_name()!="Dummy" and audio.mixer_clock_enabled)
 if headroom_only:
  # Target the changed Master effect. Previously verified45 routes/logic are
  # unchanged; these three actual input contacts cover power/prime/firearm.
  audio.request_state(&"COMBAT");await frames(60)
  capture_begin("runtime_mix")
  for row in [["gabar_training","unarmed"],["timka_prime","blunt"],["pasha_training","firearm"]]:
   check(String(row[0])+":headroom_fixture",lab.select_fixture(row[0]))
   segment=String(row[0])+"_headroom_"+String(row[1])
   var context: String="athletic_prime" if row[0]=="timka_prime" else "training"
   await complete_route(row[1],Routes.cue_for(lab.player.actor_id,context,row[1]))
  await frames(25);capture_end()
  await mixer_pass(starts)
  return
 capture_begin("runtime_mix")
 for reduced in [false,true]:
  options.set_value(&"reduced_gore",reduced,false)
  options.set_value(&"reduced_impact",reduced,false)
  for fixture_id in FIXTURES:
   check(fixture_id+":registered_scene",lab.select_fixture(fixture_id))
   for category in FIXTURES[fixture_id]:
    segment=fixture_id+"_"+category+"_"+("reduced" if reduced else "full")
    var context: String="athletic_prime" if fixture_id=="timka_prime" else "training"
    await complete_route(category,Routes.cue_for(lab.player.actor_id,context,category))
 # Every live hero is cancelled/revoked/reset/killed before its contact. No late cue.
 options.set_value(&"reduced_impact",false,false);options.set_value(&"reduced_gore",false,false)
 for fixture_id in FIXTURES:
  for mode in ["cancel","revoke","reset","death","replace"]:
   check(fixture_id+":"+mode+":registered_scene",lab.select_fixture(fixture_id))
   segment=fixture_id+"_before_contact_"+mode
   var target:=await prepare("unarmed");target.set_physics_process(true)
   await tap(KEY_V)
   check(segment+":entered_windup",not lab.combat.finisher_for(lab.player).is_empty())
   if mode=="cancel":await tap(KEY_C)
   elif mode=="revoke":lab.scene_policy.invalidate()
   elif mode=="reset":await tap(KEY_R)
   elif mode=="death":lab.player.receive_hit(1,0.0,991,target)
   elif mode=="replace":lab.select_fixture("gabar_training")
   await frames(65)
   check(segment+":no_late_finisher_voice",audio_events.filter(func(e: Dictionary)->bool:return e.segment==segment).is_empty() and lab.combat.finishers.is_empty())
 check("present_registered",lab.select_fixture("timka_present"));segment="present_denied"
 await prepare("unarmed",false);await tap(KEY_V);await frames(70)
 check("present_no_prime_voice_or_finisher",audio_events.filter(func(e: Dictionary)->bool:return e.segment==segment).is_empty() and lab.combat.finishers.is_empty() and lab.score==0)
 # Real legacy host, not a profile alias. Its five accepted WAVs stay unchanged.
 current_scene=null;lab.free();await frames(2)
 lab=LegacyLab.new();root.add_child(lab);current_scene=lab;lab.auto_retry=false
 lab.combat.contact_committed.connect(on_contact);lab.audio_event.connect(on_audio)
 for category in CATEGORIES:
  segment="yakuza_legacy_"+category
  await complete_route(category,"finish_"+category)
 await frames(25);capture_end()
 if headless:
  finish_replay(starts)
  return
 await mixer_pass(starts)

func mixer_pass(starts: int) -> void:
 # Solo actual playback gives a compact listening artifact, with music muted only
 # inside this test. Full gameplay above uses normal buses and production settings.
 var music_bus:=AudioServer.get_bus_index(&"Music")
 var was_muted:=AudioServer.is_bus_mute(music_bus)
 AudioServer.set_bus_mute(music_bus,true)
 audio.reset_for_retry();await frames(30)
 capture_begin("solo_cues")
 for cue in Routes.entries():
  await frames(6)
  var ok: bool=audio.play_cue(StringName(cue))
  solo_events.append({"cue":cue,"elapsed":float(Time.get_ticks_usec()-capture_started_usec)/1000000.0,"played":ok,"streams":playing_streams(cue)})
  check(cue+":solo_voice",ok and playing_streams(cue).size()==1)
  await frames(30)
 capture_end();AudioServer.set_bus_mute(music_bus,was_muted)
 audio.reset_for_retry();await frames(30);audio.request_state(&"COMBAT");await frames(60)
 capture_begin("stress_mix")
 for burst in 8:
  var before: int=audio.dropped_cues
  var played:=0
  for cue in Routes.entries():
   if audio.play_cue(StringName(cue)):played+=1
  var diagnostic: Dictionary=audio.diagnostics()
  stress_events.append({"burst":burst,"elapsed":float(Time.get_ticks_usec()-capture_started_usec)/1000000.0,"played":played,"active":diagnostic.active_voices,"dropped":audio.dropped_cues-before,"clock":audio.clock})
  check("burst"+str(burst)+":bounded_real_voices",played>0 and diagnostic.active_voices<=audio.MAX_VOICES and audio.dropped_cues>before)
  await frames(42)
 await frames(30);capture_end()
 finish_replay(starts)

func finish_replay(starts: int) -> void:
 check("retry_and_cues_preserve_music_player_clock",audio.stem_starts==starts and audio.diagnostics().music_players==1)
 var ok:=not checks.is_empty() and checks.all(func(c: Dictionary)->bool:return c.passed)
 var data: Dictionary={"schema":1,"scope":"C01_HEADROOM_TARGETED_ONLY" if headroom_only else "C01_RUNTIME_SIGNAL_ONLY","passed":ok,"phase_approval":false,
  "actual_input":true,"renderer":DisplayServer.get_name(),"listening_performed":false,"checks":checks,
  "route_results":route_results,"contacts":contacts,"audio_events":audio_events,"captures":captures,
  "mixer_captures":capture_data,"solo_events":solo_events,"stress_events":stress_events,"audio":audio.diagnostics(),
  "native_windows":"NOT_TESTED","hardware_latency":"NOT_MEASURED"}
 var file:=FileAccess.open(output.path_join("result.json"),FileAccess.WRITE);file.store_string(JSON.stringify(data,"  "));file.close()
 print("C01_RUNTIME_RESULT ",checks.filter(func(c: Dictionary)->bool:return c.passed).size(),"/",checks.size())
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if ok else 1)
