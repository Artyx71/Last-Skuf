extends RefCounted
## Tega moves a real registered object with his foot, never a ranged shockwave.
const KIND := "special"
const WINDUP := 0.18
const ACTIVE := 0.18
const RECOVERY := 0.32
const COOLDOWN := 2.4
const SPEED := 210.0

func required_frames(actor_id: String) -> SpriteFrames:
	if actor_id != "tega": return null
	# The own FIN sheet already supplies ready / foot contact / tired recovery.
	var extra := SpriteFrames.new()
	extra.remove_animation(&"default")
	return extra

func start(body: CharacterBody2D) -> bool:
	if body.movement_ability != self or body.prepared_ability != "environment_kick": return false
	if not body._can_begin_action() or body.ability_cooldown > 0: return false
	body._face_aim()
	var object: PhysicsBody2D = body.lab.combat.environment_kicks.find_object(body,body.aim_direction())
	if object == null: return false
	body.action_windup = WINDUP
	body.action_active = ACTIVE
	body.action_recovery = RECOVERY
	body._play_action(KIND,WINDUP+ACTIVE+RECOVERY)
	var id: int = body.lab.combat.environment_kicks.begin(body,object)
	if id == 0:
		body.cancel_action()
		return false
	body.melee_attack_id = id
	body.ability_cooldown = COOLDOWN
	body.ability_uses += 1
	body.ability_distance = 0.0
	body.last_ability_path.assign([body.global_position])
	return true

func advance_motion(body: CharacterBody2D, delta: float) -> void:
	if body.movement_ability != self or body.action_kind != KIND or not body._action_authorized(): return
	var step := maxf(0.0,minf(body.action_elapsed,WINDUP+ACTIVE)-maxf(body.action_elapsed-delta,WINDUP))
	body.lab.combat.environment_kicks.request_step(body,step*SPEED)
