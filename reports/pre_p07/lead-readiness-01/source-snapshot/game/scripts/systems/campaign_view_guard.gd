extends Node
## Pause ownership only. Never loads, advances or saves the campaign dialogue.
var campaign: Node
var was_processing := false
var owns_pause := false

func acquire(director: Node) -> bool:
	if owns_pause or not is_instance_valid(director) or director.has_meta("p06_viewing_session"): return false
	campaign = director
	was_processing = campaign.is_processing()
	campaign.set_meta("p06_viewing_session",get_instance_id())
	campaign.set_process(false)
	owns_pause = true
	if is_instance_valid(campaign.audio): campaign.audio.dialogue_active(false)
	return true

func release() -> void:
	if owns_pause and is_instance_valid(campaign) and campaign.get_meta("p06_viewing_session",0)==get_instance_id():
		campaign.remove_meta("p06_viewing_session")
		campaign.set_process(was_processing)
		if is_instance_valid(campaign.audio): campaign.audio.dialogue_active(campaign.active)
	owns_pause = false

func _exit_tree() -> void:
	release()
