extends Node
## Test goal, not a playable mission or a shipped character/scene grant.
var alive := true
var objective := true
var jobs := false
func bonus_goal_ready() -> bool:
	return alive and objective and not jobs
