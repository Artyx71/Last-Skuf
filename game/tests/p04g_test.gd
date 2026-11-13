extends SceneTree
## Actual CombatSystem/actors/world integration. No render callbacks authorize damage.
var passed := 0
var failed := 0
var lab: Node2D
var target: CharacterBody2D
var store: Node
var samples: Array[Dictionary] = []

func _initialize() -> void: call_deferred("_run")
func check(value: bool,title: String) -> void:
	if value:
		passed += 1
		print("PASS ",title)
	else:
		failed += 1
		push_error("FAIL: " + title)
func frames(n: int) -> void:
	for i in n:
		await physics_frame
		await process_frame
func fixture(category := "unarmed", earned := true) -> void:
	for action in ["attack_melee","finisher","move_down","cancel_finisher"]: Input.action_release(action)
	lab.reset_encounter()
	lab.auto_retry = false
	lab.gallery_mode = true
	lab.player.position = Vector2(250,270)
	lab.player.set_aim(Vector2.RIGHT)
	lab.player.health = 3
	for enemy in lab.enemies:
		enemy.set_physics_process(false)
		enemy.position = Vector2(500,90)
	target = lab.enemies[0]
	target.position = Vector2(280,270)
	lab.training_bench.set_meta("finisher_enabled",true)
	lab.select_equipment(["unarmed","blunt","sharp","firearm","environmental"].find(category))
	await frames(2)
	if earned:
		Input.action_press("attack_melee")
		await frames(2)
		Input.action_release("attack_melee")
		await frames(5)
		check(target.health == 1 and target.hits_received == 1 and target.state == "stunned",category+" earned ordinary damage0/stun1.15 contact")

func _run() -> void:
	lab = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(lab)
	store = root.get_node("OptionsStore")
	await frames(2)
	check(Engine.get_write_movie_path().is_empty(),"ordinary headless run never claims MovieMaker")
	var impact: Node2D = lab.combat.impact
	var ground_z: int = impact.ground_layer.z_index+impact.z_index+lab.combat.z_index
	check(ground_z<lab.player.z_index and impact.z_index>lab.player.z_index,"ground stains below actors while clothing/held contact poses remain above")
	var effects: Image = impact.texture.get_image()
	for column in [4,5,8,9]:
		var mask := effects.get_region(Rect2i(column*48,0,48,64)).get_used_rect()
		var pivot: Vector2 = impact.effect_pivots["finisher" if column>=8 else "floor"]
		check(mask.position.y-pivot.y>=-20 and mask.end.y-pivot.y<=0,"actual ground stain pixels align near contact feet instead of south of body "+str(column))
	await fixture("unarmed",false)
	check(not lab.combat.eligible(lab.player,target,"unarmed"),"standing target ineligible")
	target.transition("knockdown",1.2)
	check(lab.combat.eligible(lab.player,target,"unarmed"),"earned knockdown eligible")
	target.transition("stunned",1.15);target.stun_remaining = 1.15
	lab.player.set_aim(Vector2.LEFT)
	check(not lab.combat.eligible(lab.player,target,"unarmed"),"wrong facing rejected")
	lab.player.set_aim(Vector2.RIGHT)
	target.position.x = 300
	check(not lab.combat.eligible(lab.player,target,"unarmed"),"out of range rejected")
	target.position.x = 280
	check(not lab.combat.eligible(lab.player,target,"sharp"),"unequipped sharp rejected")
	lab.player.position = Vector2(200,188);target.position = Vector2(200,153);lab.player.set_aim(Vector2.UP)
	await frames(2)
	check(not lab.combat.eligible(lab.player,target,"unarmed"),"wall blocks otherwise eligible target")
	await fixture("environmental")
	lab.training_bench.set_meta("finisher_enabled",false)
	check(not lab.player.try_finisher(),"disabled registered environment rejected")
	lab.training_bench.set_meta("finisher_enabled",true)
	lab.training_bench.position.x = 400
	check(not lab.player.try_finisher(),"distant registered environment rejected")
	lab.training_bench.position.x = 302
	for category in ["unarmed","blunt","sharp","firearm","environmental"]:
		await fixture(category)
		check(lab.player.try_finisher(),category+" real loadout starts after earned stun")
		var job: Dictionary = lab.combat.finisher_for(lab.player)
		var id: int = job.id
		var definition: Dictionary = job.definition.duplicate(true)
		await frames(35)
		check(target.health == 1 and target.hits_received == 1,category+" long >.58s windup deals no hidden damage")
		await frames(25)
		check(target.health == 0 and target.hits_received == 2 and lab.kills == 1,category+" one actual lethal contact")
		check(lab.player.sprite.animation == StringName("finish_"+category+"_right"),category+" authored action remains during recovery")
		var first: Dictionary = lab.combat.contact_events[-1]
		check(first.finisher and first.cue == "finish_"+category,category+" typed synced contact cue")
		for i in 4: lab.combat._apply_hit(target,definition,id,lab.player)
		check(target.hits_received == 2 and lab.kills == 1 and lab.score == 100 and lab.combat.damage_events == 2,category+" callback/reentry cannot double hit/kill")
		check(not lab.player.try_finisher() and not lab.player.attack_melee(),category+" committed recovery rejects reentry")
		target.set_physics_process(true) # Dead actor advances only its actual collapse presentation.
		await frames(50)
		check(lab.combat.finishers.is_empty() and target.state == "dead",category+" exits and dead priority retained")
		var socket := preload("res://scripts/actors/polish_frames.gd").clothing_offset(target.sprite)
		var attached := false
		for decal in lab.combat.impact.decals:
			if decal.get("actor")==target:
				attached = decal.at.distance_to(target.global_position+socket)<0.01
		check(target.sprite.frame==2 and socket.y>-20 and attached,category+" clothing wound follows actual settled corpse torso instead of standing height")
		target.transition("attack",1)
		target.hear_noise(Vector2.ZERO)
		check(target.state == "dead",category+" dead cannot be overridden by attack/noise")
		lab.reset_encounter()
		var hits: int = target.hits_received
		check(not lab.combat._apply_hit(target,definition,id,lab.player) and target.hits_received == hits,"stale pre-reset stamped contact rejected "+category)
	await fixture("unarmed")
	lab.player.try_finisher()
	await frames(8)
	lab._set_options_visible(true)
	var paused_clock: float = lab.player.action_elapsed
	var paused_hits: int = target.hits_received
	Input.action_press("attack_melee")
	await frames(4)
	Input.action_release("attack_melee")
	store.set_value(&"decals",false,false)
	await frames(3)
	check(lab.player.action_elapsed==paused_clock and target.hits_received==paused_hits,"settings GUI input cannot attack or advance paused finisher contact")
	lab._set_options_visible(false)
	await frames(60)
	check(lab.kills==1 and lab.score==100,"closing settings resumes the same once-only contact clock")
	await fixture("unarmed",false)
	target.receive_knockdown(1.2)
	target.transition("hurt",0.2)
	target.transition("attack",0.1)
	lab.combat.start_melee(target,"enemy",Vector2.LEFT,lab.config.attacks.enemy_melee)
	await frames(3)
	check(target.state=="knockdown" and lab.player.hits_received==0,"fall priority rejects lower hurt/attack and stale attack bind")
	target.receive_hit(0,1.15,990,lab.player)
	check(target.state=="knockdown","weaker stun cannot overwrite active knockdown")
	target.receive_hit(1,0,991,lab.player)
	target.transition("recover",1,true)
	check(target.state=="dead" and lab.kills==1,"death dominates hurt/fall and forced stale recovery")
	await fixture("unarmed")
	target.health=5
	lab.player.try_finisher()
	var retained: Dictionary = lab.combat.finisher_for(lab.player).duplicate(true)
	await frames(60)
	for callback in 5: lab.combat._apply_hit(target,retained.definition,retained.id,lab.player)
	check(target.health==4 and target.hits_received==2 and lab.kills==0 and lab.score==0,"receipt rejects repeated callbacks even while contacted target is still alive")
	# Distinct interruptions must remove reservation and pending contact.
	for reason in ["input","movement","range","weapon","target_hit","target_loss","environment","source_attack"]:
		await fixture("environmental" if reason == "environment" else "unarmed")
		check(lab.player.try_finisher(),reason+" cancellation fixture starts")
		await frames(10)
		match reason:
			"input": Input.action_press("cancel_finisher")
			"movement": Input.action_press("move_down")
			"range": target.position.x += 100
			"weapon": lab.player.finisher_weapon = "sharp"
			"target_loss": lab.remove_child(target)
			"target_hit": target.receive_hit(0,0,700,lab.player)
			"environment": lab.training_bench.set_meta("finisher_enabled",false)
			"source_attack": lab.player.receive_hit(1,0,701,target)
		await frames(65)
		check(target.health == 1 and lab.kills == 0 and lab.combat.finishers.is_empty(),reason+" cancels before contact, no kill")
		if reason == "target_loss": lab.add_child(target)
		Input.action_release("move_down");Input.action_release("cancel_finisher")
	await fixture("unarmed")
	lab.player.try_finisher()
	await frames(20)
	lab.reset_encounter()
	await frames(70)
	check(lab.kills == 0 and lab.score == 0 and lab.combat.damage_events == 0,"reset before contact destroys finisher authority")
	await fixture("unarmed")
	target.set_physics_process(true)
	check(lab.player.try_finisher(),"live AI target can be finished after earned shove")
	await frames(58)
	var committed_score: int = lab.score
	Input.action_press("cancel_finisher");await frames(2);Input.action_release("cancel_finisher")
	check(lab.kills == 1 and committed_score == 100 and lab.score == 100,"cancel after contact preserves exactly one score and kill")
	lab.player.receive_hit(3,0,999,target)
	await frames(2)
	check(lab.player.health == 0 and lab.kills == 1 and lab.score == 100 and lab.combat.finishers.is_empty(),"death interrupts committed recovery without refund or repeated contact")
	for surface in ["concrete","metal"]:
		await fixture("sharp",false)
		lab.set_kit("training")
		lab.player.position=Vector2(200,188) if surface=="concrete" else Vector2(600,284)
		lab.player.set_aim(Vector2.UP if surface=="concrete" else Vector2.RIGHT)
		target.position=Vector2(500,90)
		await frames(2)
		lab.player.attack_melee()
		await frames(12)
		check(lab.combat.wall_impacts==1 and lab.combat.damage_events==0,"native sharp wall contact exactly once on "+surface)
		var found := false
		for event in root.get_node("AudioDirector").event_log:
			if event.get("kind")=="cue" and event.get("id")=="impact_sharp_"+surface: found=true
		check(found,"weapon+registered surface routes distinct actual cue "+surface)
	# Strong hitstop must never stop the original action/contact clock.
	await fixture("unarmed",false)
	lab.set_kit("training");target.health = 3
	lab.player.attack_melee()
	await frames(7)
	check(lab.combat.impact.hold_remaining > 0 and target.hits_received == 1,"strong hit presents bounded held poses")
	var elapsed: float = lab.player.action_elapsed
	await frames(2)
	check(lab.player.action_elapsed > elapsed and target.hits_received == 1,"physics clock advances through presentation hitstop exactly once")
	await frames(4)
	check(lab.combat.impact.held_poses.is_empty(),"hitstop .045s releases held sprites")
	var strong_event := {"at":Vector2(280,270),"direction":Vector2.RIGHT,"strong":true,"damage":0,"finisher":false}
	lab.combat.impact.on_contact(strong_event)
	lab.combat.impact._process(0.06)
	lab.combat.impact.on_contact(strong_event)
	check(lab.combat.impact.hold_remaining==0 and lab.combat.impact.held_poses.is_empty(),"burst cooldown prevents unbounded continuous hitstop")
	var camera := Camera2D.new()
	camera.position=Vector2(333,222);camera.offset=Vector2(7,-3)
	lab.add_child(camera)
	await frames(2)
	store.set_value(&"shake",100,false)
	lab.combat.impact.shake_remaining=0.1
	lab.combat.impact._process(0.01)
	check(camera.offset.distance_to(Vector2(7,-3))<=4.25 and camera.position==Vector2(333,222),"capped camera shake preserves authored chapter camera position and base offset")
	store.set_value(&"shake",0,false)
	lab.combat.impact._process(0.01)
	check(camera.offset.is_equal_approx(Vector2(7,-3)),"shake0 restores original camera offset")
	camera.queue_free()
	await frames(2)
	# Collision-safe impulse into actual training wall.
	lab.player.position = Vector2(30,284)
	lab.player.apply_impulse(Vector2(-100,0))
	await frames(20)
	check(lab.player.position.x >= 27.9,"knockback cannot tunnel through boundary wall")
	# Cosmetic overload/caps/TTL is independent of gameplay RNG and options.
	var rng_before: int = lab.rng.state
	var event := {"at":Vector2(280,270),"direction":Vector2.RIGHT,"strong":false,"damage":1,"finisher":true}
	for i in 200: lab.combat.impact.on_contact(event)
	check(lab.combat.impact.particles.size() == 48 and lab.combat.impact.decals.size() == 40,"bounded 48 particles / 40 decals under overload")
	check(lab.rng.state == rng_before,"cosmetic RNG cannot consume encounter RNG")
	lab.combat.impact._process(19)
	check(lab.combat.impact.particles.is_empty() and lab.combat.impact.decals.is_empty(),"particles and decals TTL expires")
	var outcomes: Array[Dictionary] = []
	for reduced in [false,true]:
		store.set_value(&"reduced_gore",reduced,false)
		store.set_value(&"decals",not reduced,false)
		store.set_value(&"shake",0 if reduced else 100,false)
		store.set_value(&"flashes",not reduced,false)
		store.set_value(&"vhs",not reduced,false)
		await fixture("unarmed")
		lab.player.try_finisher()
		await frames(62)
		outcomes.append({"kills":lab.kills,"score":lab.score,"health":target.health,"hits":target.hits_received,"events":lab.combat.damage_events,"rng":str(lab.rng.state),"player":lab.player.position})
		var current_texture: AtlasTexture = target.sprite.sprite_frames.get_frame_texture(&"finish_unarmed_right",1)
		check(current_texture.atlas.resource_path.ends_with("_reduced.png") == reduced,"gore mode selects actual neutral/full reaction raster without changing action clock")
		if reduced:
			check(lab.combat.impact.shake_offset == Vector2.ZERO and not lab.combat.impact.flashes_enabled(),"shake0 and flashesOff honored")
	check(outcomes[0] == outcomes[1],"Full/Reduced/decals/shake/flashes/VHS preserve actual gameplay outcome and RNG")
	lab.reset_encounter()
	check(lab.combat.impact.particles.is_empty() and lab.combat.impact.decals.is_empty() and lab.combat.finishers.is_empty(),"reset clears all transient reservations and effects")
	# Frame coverage uses actual imported resources and nonempty bounds.
	var loader = preload("res://scripts/actors/polish_frames.gd")
	for actor in lab.enemies:
		for state in loader.STATES:
			for direction in loader.DIRECTIONS:
				var animation := StringName("reaction_"+state+"_"+direction)
				check(actor.sprite.sprite_frames.get_frame_count(animation)==3,actor.kind+" coverage "+animation)
				var hashes := {}
				for f in 3:
					var image: Image = actor.sprite.sprite_frames.get_frame_texture(animation,f).get_image()
					hashes[hash(image.get_data())] = true
					check(image.get_used_rect().has_area(),"nonempty "+actor.kind+" "+animation+str(f))
				check(hashes.size() >= 2,"authored articulation "+actor.kind+" "+animation)
	for actor in [lab.player]+lab.enemies:
		for category in loader.CATEGORIES:
			for direction in loader.DIRECTIONS:
				check(actor.sprite.sprite_frames.get_frame_count(StringName("finish_"+category+"_"+direction))==3,"finisher frame coverage "+category+" "+direction)
	var connections_before: int = store.get_signal_connection_list("changed").size()
	var temporary_lab: Node2D = load("res://scenes/world/combat_lab.tscn").instantiate()
	root.add_child(temporary_lab)
	await frames(2)
	temporary_lab.queue_free()
	await frames(2)
	check(store.get_signal_connection_list("changed").size()==connections_before,"scene teardown disconnects all gore/VHS option listeners")
	var result := {"passed":failed==0,"assertions":passed,"failed":failed,"outcomes":outcomes}
	var path := OS.get_environment("AYAY_P04G_TEST_RESULT")
	if not path.is_empty():
		var file := FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "))
	print("RESULT passed=%d failed=%d" % [passed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failed else 0)
