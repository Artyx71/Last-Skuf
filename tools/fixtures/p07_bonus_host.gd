extends Node
## Test goal, not a playable mission or a shipped character/scene grant.
var alive := true
var objective := true
var jobs := false
var callback := Callable()
func bonus_goal_ready() -> bool:
	var ready := alive and objective and not jobs
	if callback.is_valid(): callback.call()
	return ready
