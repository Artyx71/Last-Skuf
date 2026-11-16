extends RefCounted
## Own eight drawn poses, ordinary swept movement, finite rounds. No immunity.
const Frames = preload("res://scripts/actors/character_frames.gd")
const KIND := "moving_shot"
const WINDUP := 0.10
const ACTIVE := 0.08
const RECOVERY := 0.12
const COOLDOWN := 0.40
const CLIP := 4
const REFILL_SECONDS := 0.90
var ammo := CLIP
var refill_elapsed := 0.0
var rounds_spent := 0
var spent_tokens: Dictionary = {}
var cost_history: Array[Dictionary] = []

func required_frames(actor_id: String) -> SpriteFrames:
	var result: SpriteFrames = Frames.moving_shot_frames(actor_id)
	if result == null: return null
	for direction in Frames.DIRECTIONS:
		if not result.get_frame_texture(StringName(KIND+"_"+direction),3).has_meta("muzzle_socket"): return null
	return result

func reset(_body: CharacterBody2D) -> void:
	ammo = CLIP
	refill_elapsed = 0.0
	rounds_spent = 0
	spent_tokens.clear()
	cost_history.clear()

func start(body: CharacterBody2D) -> bool:
	if body.movement_ability != self or body.prepared_ability != KIND: return false
	if not body._can_begin_action() or body.ability_cooldown > 0 or ammo <= 0: return false
	body._face_aim()
	body.action_windup = WINDUP
	body.action_active = ACTIVE
	body.action_recovery = RECOVERY
	var serial: int = body.action_serial+1
	var epoch: int = body.lab.combat.encounter_epoch
	body._play_action(KIND,WINDUP+ACTIVE+RECOVERY)
	if body.action_serial!=serial or body.lab.combat.encounter_epoch!=epoch or body.movement_ability!=self: return false
	var id: int = body.lab.combat.moving_shots.begin(body,self)
	if id == 0:
		if body.action_serial==serial and body.lab.combat.encounter_epoch==epoch: body.cancel_action()
		return false
	body.ranged_action_id = id
	body.ability_cooldown = COOLDOWN
	body.ability_uses += 1
	body.ability_distance = 0.0
	body.last_ability_path.assign([body.global_position])
	return true

func present(body: CharacterBody2D) -> void:
	var phase := 0.0
	if body.action_elapsed < WINDUP:
		phase = body.action_elapsed*3.0/WINDUP
		body.action_frame = mini(2,int(floor(phase)))
	elif body.action_elapsed < WINDUP+ACTIVE:
		phase = (body.action_elapsed-WINDUP)*2.0/ACTIVE
		body.action_frame = 3+mini(1,int(floor(phase)))
	else:
		phase = (body.action_elapsed-WINDUP-ACTIVE)*3.0/RECOVERY
		body.action_frame = 5+mini(2,int(floor(phase)))
	body.sprite.play(body.action_animation)
	body.sprite.pause()
	body.sprite.set_frame_and_progress(body.action_frame,clampf(fmod(phase,1.0),0.0,1.0))
	body.weapon_visual_update()

func advance_motion(body: CharacterBody2D, _delta: float) -> void:
	# CharacterBody2D already moved through its existing Input/move_and_slide.
	# Record that physical path; this ability never teleports or forces a lunge.
	if body.movement_ability != self or body.action_kind != KIND or not body._action_authorized(): return
	if not body.last_ability_path.is_empty():
		body.ability_distance += body.global_position.distance_to(body.last_ability_path.back())
	body.last_ability_path.append(body.global_position)

func advance_passive(body: CharacterBody2D, delta: float) -> void:
	if body.movement_ability != self or not body._prepared_policy_matches_live(): return
	if ammo >= CLIP:
		refill_elapsed = 0.0
		return
	if body.action_kind == KIND: return
	refill_elapsed += delta
	while refill_elapsed >= REFILL_SECONDS and ammo < CLIP:
		ammo += 1
		refill_elapsed -= REFILL_SECONDS

func can_spend(body: CharacterBody2D) -> bool:
	return body.movement_ability == self and body.prepared_ability == KIND and body._prepared_policy_matches_live() and body.health > 0 and body.lab.state == "playing" and ammo > 0

func spend_round(body: CharacterBody2D, epoch: int, action_id: int, reason: String) -> bool:
	if epoch != body.lab.combat.encounter_epoch or body.movement_ability != self or body.prepared_ability != KIND or not body._prepared_policy_matches_live() or body.health<=0 or body.lab.state!="playing": return false
	var token := str(epoch)+":"+str(action_id)
	if spent_tokens.has(token): return true
	if ammo<=0: return false
	spent_tokens[token] = true
	if spent_tokens.size()>512: spent_tokens.erase(spent_tokens.keys()[0])
	ammo -= 1
	refill_elapsed = 0.0
	rounds_spent += 1
	cost_history.append({"epoch":epoch,"id":action_id,"reason":reason,"tick":Engine.get_physics_frames(),"ammo":ammo,"pose":body.sprite.frame})
	if cost_history.size()>128: cost_history.pop_front()
	return true

func feedback(body: CharacterBody2D) -> Dictionary:
	var phase := "unavailable"
	if body.health<=0: phase="dead"
	elif body.lab.state=="options": phase="paused"
	elif body._prepared_policy_matches_live() and body.lab.state=="playing":
		if body.action_kind==KIND: phase="firing"
		elif ammo<=0: phase="empty"
		elif not body.action_kind.is_empty(): phase="busy"
		elif body.ability_cooldown>0: phase="cooldown"
		else: phase="ready"
	return {"phase":phase,"ammo":ammo,"clip":CLIP,"cooldown":body.ability_cooldown,
		"cooldown_total":COOLDOWN,"refill":refill_elapsed/REFILL_SECONDS,"refill_seconds":REFILL_SECONDS-refill_elapsed}
