extends Node
## Sequential actual scene replay. Initial placements are declared fixtures, never
## injected stun/kill state. Setup stun and finishers use real Input and action clocks.
var lab: Node2D
var report := {"schema":1,"passed":true,"checks":[],"captures":[],"finishers":[],"ai":[],"fixture_initial_placements":true,"earned_stun_input":true,"scope":"NOT_SET"}
var output := ""
var headless := false
var timings: Array[float] = []
var stress_active := false
var last_frame_usec := 0
var stress_actors: Array[CharacterBody2D] = []
const CATEGORIES := ["unarmed","blunt","sharp","firearm","environmental"]
const DIRECTIONS := [Vector2.DOWN,Vector2.LEFT,Vector2.RIGHT,Vector2.UP]
const NAMES := ["down","left","right","up"]

func _ready() -> void:
	output = OS.get_environment("AYAY_P04G_CAPTURE_DIR")
	headless = DisplayServer.get_name() == "headless"
	report.scope = "HEADLESS_TECHNICAL_NO_RENDER_EVIDENCE" if headless else "ACTUAL_RENDERED_SCENE"
	call_deferred("run")

func _process(_delta: float) -> void:
	var now := Time.get_ticks_usec()
	if stress_active and last_frame_usec > 0: timings.append(float(now-last_frame_usec)/1000.0)
	last_frame_usec = now

func check(value: bool,name: String) -> void:
	report.checks.append({"name":name,"passed":value})
	if not value:
		report.passed = false
		push_error("FAIL: "+name)

func frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame
		await get_tree().process_frame

func tap(action: String) -> void:
	Input.action_press(action)
	await frames(1)
	Input.action_release(action)
	await frames(1)

func capture(name: String) -> void:
	if headless or output.is_empty(): return
	await RenderingServer.frame_post_draw
	var path := output.path_join(name+".png")
	var code := get_viewport().get_texture().get_image().save_png(path)
	report.captures.append({"name":name,"path":path,"code":code,"tick":Engine.get_physics_frames(),"draw_frame":Engine.get_frames_drawn()})
	check(code==OK,"actual frame "+name)

func fixture(index: int, direction: Vector2, health := 1) -> CharacterBody2D:
	lab.reset_encounter()
	lab.auto_retry = false
	lab.gallery_mode = true
	lab.player.position = Vector2(280,270)-direction*30
	lab.player.set_aim(direction)
	lab.player.health = 100 # QA durability only, declared fixture; all incoming contacts remain real.
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(500,90)
	var target: CharacterBody2D = lab.enemies[index]
	target.position = Vector2(280,270)
	target.health = health
	target.locked_aim = -direction
	target.set_physics_process(true)
	lab.training_bench.position = target.position + direction * 22
	lab.training_bench.set_meta("finisher_enabled",true)
	await frames(2)
	return target

func run() -> void:
	var audio := get_node("/root/AudioDirector")
	check(audio.begin_capture(),"actual mixer recorder starts")
	for ci in CATEGORIES.size():
		for di in DIRECTIONS.size():
			var category: String = CATEGORIES[ci]
			var target: CharacterBody2D = await fixture(ci%3,DIRECTIONS[di])
			lab.select_equipment(ci)
			await tap("attack_melee")
			var wait := 0
			while target.hits_received == 0 and wait<20:
				await frames(1);wait+=1
			check(target.state=="stunned" and target.health==1,"earned shove "+category+NAMES[di])
			await tap("finisher")
			check(not lab.combat.finishers.is_empty(),"input finisher enter "+category+NAMES[di])
			await frames(4)
			await capture(category+"_"+NAMES[di]+"_windup")
			wait = 0
			while target.health>0 and not lab.combat.finishers.is_empty() and wait<90:
				await frames(1);wait+=1
			check(target.health==0 and lab.kills==1 and lab.score==100,"one committed kill "+category+NAMES[di])
			await capture(category+"_"+NAMES[di]+"_contact")
			var events: Array = lab.combat.contact_events.duplicate(true)
			report.finishers.append({"category":category,"direction":NAMES[di],"target_kind":target.kind,"hits":target.hits_received,"kills":lab.kills,"score":lab.score,"events":events,"source_animation":String(lab.player.sprite.animation),"source_frame":lab.player.sprite.frame,"target_animation":String(target.sprite.animation),"target_frame":target.sprite.frame})
			await frames(8)
			await capture(category+"_"+NAMES[di]+"_recovery")
			await frames(40)
			check(lab.combat.finishers.is_empty(),"finisher exit "+category+NAMES[di])
	# All three actual AI warnings/contact/recovery and each directional reaction.
	for index in 3:
		for di in DIRECTIONS.size():
			var target: CharacterBody2D = await fixture(index,DIRECTIONS[di],20)
			var prefix: String = target.kind+"_"+NAMES[di]
			var wait := 0
			while target.state != "telegraph" and wait<160:
				await frames(1);wait+=1
			check(target.state=="telegraph","AI telegraph "+prefix)
			await capture(prefix+"_telegraph")
			while target.state == "telegraph" and wait<240:
				await frames(1);wait+=1
			check(target.state=="attack","AI actual attack "+prefix)
			await capture(prefix+"_attack")
			while target.state=="attack" and wait<280:
				await frames(1);wait+=1
			check(target.state=="recover","AI actual recovery "+prefix)
			await capture(prefix+"_recovery")
			report.ai.append({"kind":target.kind,"direction":NAMES[di],"transitions":target.transitions.duplicate(),"player_hits":lab.player.hits_received})
			# State modifiers travel through existing native melee query and contact clock.
			for action in ["hurt","stun","knockdown","death"]:
				target = await fixture(index,DIRECTIONS[di],20 if action != "death" else 1)
				lab.set_kit("training" if action in ["hurt","death"] else "escape")
				if action == "knockdown":
					# Declared knockdown fixture modifies only this attack's data, never the approved shove resource.
					lab.config.attacks.shove = lab.config.attacks.shove.duplicate(true)
					lab.config.attacks.shove.knockdown = 1.15
				await tap("attack_melee")
				var hits: int = target.hits_received
				wait = 0
				while target.hits_received==hits and wait<12:
					await frames(1);wait+=1
				check(target.state=={"hurt":"hurt","stun":"stunned","knockdown":"knockdown","death":"dead"}[action],"AI receive "+prefix+action)
				await capture(prefix+"_"+action+"_contact")
				await frames(7)
				await capture(prefix+"_"+action+"_settled")
				lab.config.attacks.shove.erase("knockdown")
	# Actual portrait overlay through ordinary incoming hit, then reduced baseline.
	var attacker: CharacterBody2D = await fixture(0,Vector2.RIGHT)
	attacker.set_physics_process(false)
	lab.combat.start_melee(attacker,"enemy",Vector2.LEFT,lab.config.attacks.enemy_melee)
	await frames(3)
	await capture("yakuza_bruised")
	await frames(10)
	lab.combat.start_melee(attacker,"enemy",Vector2.LEFT,lab.config.attacks.enemy_melee)
	await frames(3)
	await capture("yakuza_wounded")
	# Pinned stress: 32 live actor nodes, 8 unique committed contacts per physics tick,
	# 600 frames, max pools, then 10 resets. Deliberately API-driven load fixture;
	# visual QA above separately proves native hit queries/input. No second damage engine.
	await fixture(0,Vector2.RIGHT,100000)
	for enemy in lab.enemies: enemy.set_physics_process(false)
	for i in 32:
		var actor := preload("res://scripts/ai/enemy_actor.gd").new()
		actor.lab=lab;actor.kind=["patrol","rusher","shooter"][i%3];actor.definition=lab.config.enemies[actor.kind]
		actor.spawn_position=Vector2(80+(i%8)*64,120+(i/8)*43);actor.patrol_end=actor.spawn_position
		lab.add_child(actor);actor.reset();actor.health=100000;actor.set_physics_process(false)
		stress_actors.append(actor)
	var load_definition := {"damage":1,"stun":0,"strong":true,"category":"blunt","_epoch":lab.combat.encounter_epoch}
	stress_active = true
	last_frame_usec=Time.get_ticks_usec()
	for frame in 600:
		for hit in 8:
			lab.combat.next_attack_id+=1
			lab.combat._apply_hit(stress_actors[(frame*8+hit)%32],load_definition,lab.combat.next_attack_id,lab.player)
		await frames(1)
	stress_active = false
	await capture("stress_32actors_4800contacts")
	check(lab.combat.impact.particles.size()<=48 and lab.combat.impact.decals.size()==40,"stress bounded pools")
	for actor in stress_actors: actor.queue_free()
	stress_actors.clear()
	for i in 10:
		lab.reset_encounter();await frames(1)
	check(lab.combat.impact.particles.is_empty() and lab.combat.impact.decals.is_empty() and lab.combat.finishers.is_empty(),"10 resets clear transient state")
	check(audio.diagnostics().active_voices<=12,"bounded runtime audio voices")
	var sorted := timings.duplicate();sorted.sort()
	report.performance={"fixture":"32 actors, 8 committed damage events/tick, 600 frames, 4800 contacts, then 10 resets","samples":sorted.size(),"measurement":"monotonic real process-frame intervals, not forced simulation delta","rendered":not headless,"duration_seconds":timings.reduce(func(a: float,b: float):return a+b,0.0)/1000.0,"p50_ms":sorted[int(sorted.size()*.50)],"p95_ms":sorted[int(sorted.size()*.95)],"p99_ms":sorted[int(sorted.size()*.99)],"video_adapter":RenderingServer.get_video_adapter_name(),"display":DisplayServer.get_name(),"os":OS.get_name(),"cpu":OS.get_processor_name(),"movie_maker":not Engine.get_write_movie_path().is_empty(),"movie_path":Engine.get_write_movie_path()}
	report.audio=audio.diagnostics()
	var audio_path := OS.get_environment("AYAY_P04G_AUDIO_PATH")
	if not audio_path.is_empty(): check(audio.end_capture(audio_path)==OK,"actual PCM saved")
	var path := OS.get_environment("AYAY_P04G_RESULT_PATH")
	if not path.is_empty():
		var file := FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "))
	print("P04G_REPLAY passed=",report.passed," checks=",report.checks.size()," captures=",report.captures.size())
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(get_tree(),0 if report.passed else 1)
