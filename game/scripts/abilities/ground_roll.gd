extends RefCounted
## Eight authored poses on one physics clock. No immunity or collision changes.
const Frames = preload("res://scripts/actors/character_frames.gd")
const KIND := "roll"
const WINDUP := 0.08
const ACTIVE := 0.32
const RECOVERY := 0.16
const COOLDOWN := 1.2
const SPEED := 180.0

func required_frames(actor_id: String) -> SpriteFrames:
	return Frames.roll_frames(actor_id)

func start(body: CharacterBody2D) -> bool:
	if body.movement_ability != self or body.prepared_ability != "dance_step": return false
	if not body._can_begin_action() or body.ability_cooldown > 0: return false
	body._face_aim()
	body.action_windup = WINDUP
	body.action_active = ACTIVE
	body.action_recovery = RECOVERY
	body.ability_cooldown = COOLDOWN
	body.ability_uses += 1
	body.ability_distance = 0.0
	body.last_ability_path.assign([body.global_position])
	body._play_action(KIND,WINDUP+ACTIVE+RECOVERY)
	# The landing control is a real Core overlap, not contact from an animation
	# callback. No health damage/score; only the visible planted-foot pose6.
	var contact := {"damage":0,"stun":0.45,"windup":WINDUP+ACTIVE,
		"active":RECOVERY/2.0,"recovery":RECOVERY/2.0,"reach":18.0,
		"radius":13.0,"category":"unarmed","strong":false}
	body.melee_attack_id = body.lab.combat.start_melee(body,"player",body.action_aim,contact)
	return true

func present(body: CharacterBody2D) -> void:
	var phase := 0.0
	if body.action_elapsed < WINDUP:
		body.action_frame = 0
		phase = body.action_elapsed/WINDUP
	elif body.action_elapsed < WINDUP+ACTIVE:
		var progress: float = (body.action_elapsed-WINDUP)*5.0/ACTIVE
		body.action_frame = 1+mini(4,int(floor(progress)))
		phase = fmod(progress,1.0)
	else:
		var progress: float = (body.action_elapsed-WINDUP-ACTIVE)*2.0/RECOVERY
		body.action_frame = 6+mini(1,int(floor(progress)))
		phase = fmod(progress,1.0)
	body.sprite.play(body.action_animation)
	body.sprite.pause()
	body.sprite.set_frame_and_progress(body.action_frame,clampf(phase,0.0,1.0))
	body.weapon_visual_update()

func advance_motion(body: CharacterBody2D, delta: float) -> void:
	if body.movement_ability != self or body.action_kind != KIND or not body._action_authorized(): return
	# Integrate only the active fraction of this tick, including boundary ticks.
	var step := maxf(0.0,minf(body.action_elapsed,WINDUP+ACTIVE)-maxf(body.action_elapsed-delta,WINDUP))
	if step <= 0.0: return
	var before := body.global_position
	body.move_and_collide(body.action_aim*SPEED*step)
	body.ability_distance += body.global_position.distance_to(before)
	body.last_ability_path.append(body.global_position)

func melee_phase(body: CharacterBody2D) -> String:
	if body.action_frame < 6: return "windup"
	return "contact" if body.action_frame == 6 else "finished"
