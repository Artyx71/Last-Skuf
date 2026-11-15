extends "res://scripts/actors/combat_player.gd"
## Authored P06 body on the existing controller and CombatSystem. No story grants.
const CharacterFrames = preload("res://scripts/actors/character_frames.gd")
const PixelPresentation = preload("res://scripts/actors/pixel_presentation.gd")
const ScenePolicy = preload("res://scripts/systems/character_scene_policy.gd")
const MOVEMENT_ABILITIES := {"dance_step":preload("res://scripts/abilities/ground_roll.gd"),
	"environment_kick":preload("res://scripts/abilities/environment_kick.gd"),
	"moving_shot":preload("res://scripts/abilities/moving_shot.gd")}
# Add a fixture only with its actual controller handler and gameplay evidence.
const IMPLEMENTED_FIXTURE_ABILITIES := {
	"gabar_training":"gabar_lunge", "olezhka_training":"training_counter",
	"timka_present":"disengage", "timka_prime":"clinch", "ryzhik_training":"dance_step",
	"tega_training":"environment_kick", "pasha_training":"moving_shot"
}
var actor_id := ""
var scene_policy: RefCounted
var authored_frames: SpriteFrames
var prepared_definition: Dictionary = {}
var prepared_ability := ""
var movement_ability: RefCounted
var ability_cooldown := 0.0
var ability_uses := 0
var ability_distance := 0.0
var last_ability_path: Array[Vector2] = []
var action_authority_snapshot: Dictionary = {}
var action_ability_id := ""
var ranged_action_id := 0
var action_serial := 0 # Monotonic across reset, separate from reusable Core IDs.
var counter_spent := false
var counter_blocks := 0
var _clinch_requested := false
const COUNTER_GUARD_OPEN := 0.06
const COUNTER_GUARD_CLOSE := 0.26
const COUNTER_WINDUP := 0.28
const COUNTER_ACTIVE := 0.10
const COUNTER_RECOVERY := 0.34
const COUNTER_COOLDOWN := 2.0
const DISENGAGE_WINDUP := 0.12
const DISENGAGE_ACTIVE := 0.24
const DISENGAGE_RECOVERY := 0.18
const DISENGAGE_COOLDOWN := 1.8
const DISENGAGE_SPEED := 140.0

func configure(id: String, policy: RefCounted) -> bool:
	if is_inside_tree() or not policy is ScenePolicy or policy.definition().get("actor_id") != id: return false
	return prepare_fixture(String(policy.definition().get("scene_id",""))) and bind_policy(policy)

func prepare_fixture(scene_id: String) -> bool:
	# Resolve trusted context and real ability BEFORE loading art or replacing a body.
	if is_inside_tree(): return false
	actor_id = ""
	authored_frames = null
	scene_policy = null
	prepared_definition.clear()
	prepared_ability = ""
	movement_ability = null
	if not IMPLEMENTED_FIXTURE_ABILITIES.has(scene_id): return false
	var proposed := ScenePolicy.new()
	if not proposed.open(scene_id) or proposed.ability_id() != IMPLEMENTED_FIXTURE_ABILITIES[scene_id]: return false
	var definition: Dictionary = proposed.definition()
	var id := String(definition.actor_id)
	var frames: SpriteFrames
	if scene_id == "timka_present": frames = CharacterFrames.timka_present_frames()
	elif scene_id == "timka_prime": frames = CharacterFrames.timka_prime_frames()
	else: frames = _load_combat_frames(id)
	if frames == null: return false
	var strategy: RefCounted
	if MOVEMENT_ABILITIES.has(proposed.ability_id()):
		strategy = MOVEMENT_ABILITIES[proposed.ability_id()].new()
		var extra: SpriteFrames = strategy.required_frames(id)
		if extra == null: return false
		CharacterFrames._append_clips(frames,extra)
	for animation in frames.get_animation_names():
		for frame in frames.get_frame_count(animation):
			var texture := frames.get_frame_texture(animation,frame)
			if not texture.has_meta("clothing_socket") or texture.get_meta("character_id","")!=id: return false
	actor_id = id
	authored_frames = frames
	prepared_definition = definition
	prepared_ability = proposed.ability_id()
	movement_ability = strategy
	return true

func _load_combat_frames(id: String) -> SpriteFrames:
	return CharacterFrames.combat_frames(id)

func bind_policy(policy: RefCounted) -> bool:
	if is_inside_tree(): return false
	scene_policy = null
	if authored_frames == null or prepared_definition.is_empty() or not policy is ScenePolicy: return false
	var definition: Dictionary = policy.definition()
	if definition != prepared_definition or definition.get("actor_id") != actor_id: return false
	var scene_id := String(definition.get("scene_id",""))
	if not IMPLEMENTED_FIXTURE_ABILITIES.has(scene_id): return false
	if policy.ability_id() != prepared_ability or prepared_ability != IMPLEMENTED_FIXTURE_ABILITIES[scene_id]: return false
	if ScenePolicy.definitions().get(scene_id,{}) != prepared_definition: return false
	scene_policy = policy
	return true

func _build_world_frames() -> SpriteFrames:
	return authored_frames

func _configure_action_frames() -> void:
	# The exact prepared context already contains all its required own clips.
	pass

func _ready() -> void:
	super._ready()
	weapon_visual.hide() # New firearms are embedded in the authored contact pose.
	if not InputMap.has_action("character_ability"):
		InputMap.add_action("character_ability")
		var key := InputEventKey.new()
		key.physical_keycode = KEY_F
		InputMap.action_add_event("character_ability",key)
	if not InputMap.has_action("character_run"):
		InputMap.add_action("character_run")
		var key := InputEventKey.new()
		key.physical_keycode = KEY_SHIFT
		InputMap.action_add_event("character_run",key)

func _process(_delta: float) -> void:
	PixelPresentation.align(sprite,self,FRAME_SIZE*0.5-FRAME_PIVOT)

func _movement_multiplier() -> float:
	if not _prepared_policy_matches_live(): return 0.0
	if action_kind in ["special","disengage","roll"]: return 0.0
	return 1.44 if Input.is_action_pressed("character_run") else 1.0

func _movement_state() -> String:
	return "run" if Input.is_action_pressed("character_run") else "walk"

func _physics_process(delta: float) -> void:
	if (action_kind=="shove" or _signature_action(action_kind)) and not _action_authorized(): cancel_action()
	if lab.state == "playing" and health > 0:
		ability_cooldown = maxf(0.0,ability_cooldown-delta)
		if movement_ability!=null and movement_ability.has_method("advance_passive"): movement_ability.advance_passive(self,delta)
	if Input.is_action_just_pressed("cancel_finisher") and _signature_action(action_kind): cancel_action()
	super._physics_process(delta)
	if lab.state == "playing" and health > 0:
		if Input.is_action_just_pressed("character_ability"): use_ability()
		if movement_ability != null and action_kind == movement_ability.KIND and _action_authorized():
			movement_ability.advance_motion(self,delta)
		if action_kind == "disengage" and _action_authorized():
			# Only the active part of this physics tick moves. No teleport, damage,
			# changed collision mask or invulnerability; interruption stops the path.
			var active_end := action_windup+action_active
			var step := maxf(0.0,minf(action_elapsed,active_end)-maxf(action_elapsed-delta,action_windup))
			var before := global_position
			move_and_collide(-action_aim*DISENGAGE_SPEED*step)
			ability_distance += global_position.distance_to(before)
			last_ability_path.append(global_position)
		if action_kind == "special" and action_frame == 1 and scene_policy.ability_id() == "gabar_lunge":
			var before := global_position
			# A short swept body move: walls stop it; collision masks never change.
			move_and_collide(action_aim*210.0*delta)
			ability_distance += global_position.distance_to(before)
			last_ability_path.append(global_position)
	PixelPresentation.align(sprite,self,FRAME_SIZE*0.5-FRAME_PIVOT)

func reset(at: Vector2) -> void:
	super.reset(at)
	if movement_ability!=null and movement_ability.has_method("reset"): movement_ability.reset(self)
	move_speed = scene_policy.movement_speed() if _prepared_policy_matches_live() else 0.0
	ability_cooldown = 0.0
	ability_uses = 0
	ability_distance = 0.0
	last_ability_path.clear()
	counter_spent = false
	counter_blocks = 0
	_clinch_requested = false
	PixelPresentation.align(sprite,self,FRAME_SIZE*0.5-FRAME_PIVOT)

func finisher_authority(category: String) -> Dictionary:
	if not _prepared_policy_matches_live(): return {}
	return scene_policy.finisher_authority(actor_id,category,finisher_category)

func can_use_finisher(category: String) -> bool:
	if finisher_authority(category).is_empty(): return false
	if actor_id=="pasha" and category=="firearm":
		return movement_ability!=null and movement_ability.can_spend(self)
	return true

func resolve_finisher(category: String, base: Dictionary) -> Dictionary:
	if not _prepared_policy_matches_live(): return {}
	return scene_policy.resolve_finisher(actor_id,category,finisher_category,base)

func _prepared_policy_matches_live() -> bool:
	# A real policy for the same actor but another context cannot grant powers
	# to an already prepared body. Only the host's atomic fixture switch can.
	return scene_policy is ScenePolicy and not prepared_definition.is_empty() and scene_policy.definition()==prepared_definition and scene_policy.ability_id()==prepared_ability

func _can_begin_action() -> bool:
	return lab != null and _prepared_policy_matches_live() and lab.state == "playing" and health > 0 and action_timer <= 0.00001 and lab.combat.finisher_for(self).is_empty()

func _play_action(action: String, duration: float) -> void:
	action_serial += 1
	action_authority_snapshot = scene_policy.action_authority(actor_id) if action=="shove" or _signature_action(action) else {}
	action_ability_id = scene_policy.ability_id() if _signature_action(action) else ""
	super._play_action(action,duration)
	if actor_id == "timka" and prepared_ability == "clinch":
		if action == "shove": action_animation = StringName("prime_strike_"+action_direction)
		elif action == "finish_unarmed" and _clinch_requested:
			action_animation = StringName("special_"+action_direction)
			action_ability_id = "clinch"
		_present_action()

func _present_action() -> void:
	if movement_ability != null and action_kind == movement_ability.KIND and movement_ability.has_method("present"):
		movement_ability.present(self)
		return
	if action_kind != "disengage":
		super._present_action()
		return
	var progress := 0.0
	if action_elapsed < action_windup:
		action_frame = 0
		progress = action_elapsed/action_windup
	elif action_elapsed < action_windup+action_active:
		var walk_phase := (action_elapsed-action_windup)*4.0/action_active
		action_frame = 1+mini(3,int(floor(walk_phase)))
		progress = fmod(walk_phase,1.0)
	else:
		action_frame = 5
		progress = (action_elapsed-action_windup-action_active)/action_recovery
	sprite.play(action_animation)
	sprite.pause()
	sprite.set_frame_and_progress(action_frame,clampf(progress,0.0,1.0))
	weapon_visual_update()

func _action_authorized() -> bool:
	if action_authority_snapshot.is_empty() or not _prepared_policy_matches_live(): return false
	if action_authority_snapshot != scene_policy.action_authority(actor_id): return false
	return not _signature_action(action_kind) or action_ability_id == scene_policy.ability_id()

func _signature_action(action: String) -> bool:
	return action in ["special","disengage","roll","moving_shot"]

func attack_melee() -> bool:
	if not _can_begin_action() or melee_cooldown > 0: return false
	# A drawn finisher tool does not grant a normal lethal knife attack.
	var definition: Dictionary = lab.config.attacks.shove.duplicate(true)
	if actor_id == "timka" and prepared_ability == "clinch":
		# Keep the one-hit baseline enemy alive for an earned grapple. Strength
		# comes from the heavy contact/impulse and control, not inflated NPC HP.
		definition.merge({"damage":0,"stun":1.25,"cooldown":0.9,"windup":0.20,
			"active":0.12,"recovery":0.28,"strong":true},true)
	melee_cooldown = float(definition.cooldown)
	_face_aim()
	action_windup = float(definition.windup)
	action_active = float(definition.active)
	action_recovery = float(definition.recovery)
	_play_action("shove",action_windup+action_active+action_recovery)
	melee_attack_id = lab.combat.start_melee(self,"player",action_aim,definition)
	return true

func attack_ranged() -> bool:
	if actor_id=="pasha" and prepared_ability=="moving_shot" and movement_ability!=null:
		return movement_ability.start(self)
	# Selecting a drawn finisher tool does not grant anyone a ranged kit.
	return false

func use_ability() -> bool:
	if not _can_begin_action() or ability_cooldown > 0: return false
	if movement_ability != null: return movement_ability.start(self)
	if actor_id == "timka" and scene_policy.ability_id() == "disengage":
		return _start_disengage()
	if actor_id == "timka" and scene_policy.ability_id() == "clinch":
		return _start_clinch()
	if actor_id == "olezhka" and scene_policy.ability_id() == "training_counter":
		return _start_training_counter()
	# Other abilities remain unavailable until their actual actor integration exists.
	if actor_id != "gabar" or scene_policy.ability_id() != "gabar_lunge": return false
	_face_aim()
	action_windup = 0.18
	action_active = 0.12
	action_recovery = 0.30
	ability_cooldown = 1.6
	ability_uses += 1
	ability_distance = 0.0
	last_ability_path.assign([global_position])
	_play_action("special",action_windup+action_active+action_recovery)
	var definition := {"damage":1,"stun":0.45,"cooldown":1.6,"windup":action_windup,"active":action_active,"recovery":action_recovery,"reach":19.0,"radius":14.0,"category":"unarmed","strong":true}
	melee_attack_id = lab.combat.start_melee(self,"player",action_aim,definition)
	return true

func _start_disengage() -> bool:
	_face_aim()
	action_windup = DISENGAGE_WINDUP
	action_active = DISENGAGE_ACTIVE
	action_recovery = DISENGAGE_RECOVERY
	ability_cooldown = DISENGAGE_COOLDOWN
	ability_uses += 1
	ability_distance = 0.0
	last_ability_path.assign([global_position])
	_play_action("disengage",action_windup+action_active+action_recovery)
	return true

func _start_clinch() -> bool:
	# Grapple only a genuinely vulnerable, reachable target with empty hands.
	# The existing Core owns reservation, contact, damage and once-only reward.
	if finisher_category != "unarmed" or finisher_weapon != "unarmed": return false
	for target in lab.enemies:
		_clinch_requested = true
		var started: bool = lab.combat.start_finisher(self,target,"unarmed")
		_clinch_requested = false
		if started:
			ability_cooldown = 2.4
			ability_uses += 1
			ability_distance = 0.0
			last_ability_path.assign([global_position])
			return true
	return false

func _start_training_counter() -> bool:
	_face_aim()
	action_windup = COUNTER_WINDUP
	action_active = COUNTER_ACTIVE
	action_recovery = COUNTER_RECOVERY
	ability_cooldown = COUNTER_COOLDOWN
	ability_uses += 1
	counter_spent = false
	# Guard pose first; no melee damage is scheduled unless a real incoming
	# contact is parried in the limited window below. A miss is a visible whiff.
	_play_action("special",action_windup+action_active+action_recovery)
	return true

func counter_window_open() -> bool:
	# The HUD and defense use the same live predicate, never a second UI timer.
	if actor_id != "olezhka" or lab == null or lab.state != "playing" or health <= 0: return false
	if action_kind != "special" or action_ability_id != "training_counter" or not _action_authorized(): return false
	return not counter_spent and action_frame == 0 and action_elapsed >= COUNTER_GUARD_OPEN and action_elapsed <= COUNTER_GUARD_CLOSE

func _counter_view(phase: String, progress := 0.0) -> Dictionary:
	return {"phase":phase,"progress":clampf(progress,0.0,1.0),"cooldown":ability_cooldown,
		"window_open":counter_window_open()}

func counter_feedback() -> Dictionary:
	# Read-only presentation snapshot. Calling this never consumes a block/action.
	if actor_id != "olezhka": return _counter_view("hidden")
	if health <= 0: return _counter_view("dead")
	if lab == null: return _counter_view("unavailable")
	if lab.state == "options": return _counter_view("paused")
	if lab.state != "playing" or scene_policy == null: return _counter_view("unavailable")
	if scene_policy.definition().get("actor_id") != actor_id or scene_policy.ability_id() != "training_counter":
		return _counter_view("unavailable")
	if action_kind == "special" and action_ability_id == "training_counter":
		if not _action_authorized(): return _counter_view("unavailable")
		if counter_window_open():
			return _counter_view("guard",(COUNTER_GUARD_CLOSE-action_elapsed)/(COUNTER_GUARD_CLOSE-COUNTER_GUARD_OPEN))
		if action_elapsed < COUNTER_GUARD_OPEN:
			return _counter_view("preparing",action_elapsed/COUNTER_GUARD_OPEN)
		if action_frame == 1 and counter_spent:
			return _counter_view("counter",(action_windup+action_active-action_elapsed)/action_active)
		if action_frame == 2:
			return _counter_view("recovery",action_timer/action_recovery)
		return _counter_view("closed")
	if not action_kind.is_empty() or not lab.combat.finisher_for(self).is_empty(): return _counter_view("busy")
	if ability_cooldown > 0: return _counter_view("cooldown",1.0-ability_cooldown/COUNTER_COOLDOWN)
	return _counter_view("ready",1.0) if _can_begin_action() else _counter_view("unavailable")

func defend_melee_contact(definition: Dictionary, _attack_id: int, source: Node2D) -> bool:
	if not counter_window_open(): return false
	if String(definition.get("category","")) not in ["unarmed","blunt","sharp"]: return false
	if not source is CharacterBody2D or not (source.collision_layer & 4) or source.health <= 0: return false
	var offset := source.global_position-global_position
	if offset.length() < 1.0 or offset.length() > 40.0 or action_aim.dot(offset.normalized()) < 0.65: return false
	if not lab.combat.clear_line(global_position+Vector2(0,-7),source.global_position+Vector2(0,-7)): return false
	counter_spent = true
	counter_blocks += 1
	# The same physics action clock enters its authored contact pose. Damage is
	# still queued through CombatSystem and reauthorised per target on its turn.
	action_elapsed = action_windup
	action_timer = action_duration-action_elapsed
	_present_action()
	var counter := {"damage":1,"stun":0.45,"windup":action_windup,"active":action_active,
		"recovery":action_recovery,"reach":21.0,"radius":14.0,"category":"unarmed","strong":true}
	melee_attack_id = lab.combat.start_melee(self,"player",action_aim,counter)
	return true

func melee_phase(attack_id: int) -> String:
	if movement_ability != null and action_kind == movement_ability.KIND and movement_ability.has_method("melee_phase"):
		if health <= 0 or attack_id != melee_attack_id or not _action_authorized(): return "finished"
		return movement_ability.melee_phase(self)
	if health <= 0 or attack_id != melee_attack_id or action_kind not in ["shove","special"] or not _action_authorized(): return "finished"
	return "windup" if action_frame == 0 else ("contact" if action_frame == 1 else "finished")

func authorize_melee_contact(attack_id: int) -> bool:
	# Rechecked for EACH recipient, including reentry after a previous contact.
	return melee_phase(attack_id) == "contact"

func present_melee_contact(attack_id: int) -> void:
	if attack_id == melee_attack_id: _present_action()

func weapon_visual_update() -> void:
	# Character art includes the weapon: never draw a second procedural pistol.
	if weapon_visual: weapon_visual.hide()

func cancel_action() -> void:
	super.cancel_action()
	if lab != null and lab.combat != null:
		lab.combat.environment_kicks.cancel(self)
		lab.combat.moving_shots.cancel(self)
	ranged_action_id = 0

func sync_ability_presentation() -> void:
	_present_action()
	PixelPresentation.align(sprite,self,FRAME_SIZE*0.5-FRAME_PIVOT)

func visual_muzzle() -> Vector2:
	if actor_id=="pasha" and action_kind=="moving_shot":
		var texture := sprite.sprite_frames.get_frame_texture(sprite.animation,sprite.frame)
		if texture.has_meta("muzzle_socket"):
			return sprite.global_position-FRAME_SIZE*0.5+texture.get_meta("muzzle_socket")
	return super.visual_muzzle()

func authorize_ranged_launch(definition: Dictionary) -> bool:
	if not authorize_committed_projectile(definition) or not _action_authorized(): return false
	return action_kind=="moving_shot" and action_frame==3 and sprite.frame==3 and ranged_action_id==int(definition.get("_ranged_job_id",-1)) and action_serial==int(definition.get("_ranged_action_serial",-1))

func authorize_committed_projectile(definition: Dictionary) -> bool:
	if actor_id!="pasha" or prepared_ability!="moving_shot" or not _prepared_policy_matches_live(): return false
	if lab==null or lab.player!=self or movement_ability==null or is_queued_for_deletion(): return false
	return definition.get("_ranged_authority",{})==scene_policy.action_authority(actor_id) and int(definition.get("_ranged_strategy_id",0))==movement_ability.get_instance_id() and int(definition.get("_ranged_epoch",-1))==lab.combat.encounter_epoch

func commit_finisher_cost(epoch: int, id: int, category: String) -> bool:
	if actor_id!="pasha" or category!="firearm": return true
	return movement_ability!=null and movement_ability.spend_round(self,epoch,id,"firearm_finisher")

func ranged_feedback() -> Dictionary:
	if actor_id!="pasha" or movement_ability==null: return {"phase":"hidden"}
	return movement_ability.feedback(self)
