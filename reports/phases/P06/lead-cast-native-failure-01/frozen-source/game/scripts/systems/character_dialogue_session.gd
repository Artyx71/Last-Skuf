extends Node
## A private viewing session. It never replaces the campaign singleton's resource/save.
const Director = preload("res://scripts/systems/dialogue_director.gd")
const Characters = preload("res://scripts/systems/character_catalog.gd")
var director: Node
var campaign: Node
var campaign_processing := false
var owns_pause := false
var save_path := "user://p06_character_dialogue_v1.json"

func _ready() -> void:
 campaign = get_node_or_null("/root/DialogueDirector")
 if campaign:
  # Only one sandbox viewing session may own the campaign processing pause.
  assert(not campaign.has_meta("p06_viewing_session"), "P06 dialogue session already open")
  campaign.set_meta("p06_viewing_session", get_instance_id())
  campaign_processing = campaign.is_processing()
  campaign.set_process(false)
  owns_pause = true
 var override := OS.get_environment("AYAY_P06_DIALOGUE_SAVE_PATH")
 if not override.is_empty(): save_path = override
 director = Director.new()
 director.name = "SandboxDialogueDirector"
 director.use_environment_save_path = false
 director.save_path = save_path
 add_child(director)
 director.set_process(false)
 # A mismatched viewing file must never restore campaign dialogue into this instance.
 if FileAccess.file_exists(save_path):
  var saved: Variant = JSON.parse_string(FileAccess.get_file_as_string(save_path))
  if saved is Dictionary and String(saved.get("resource", "")).begins_with("res://resources/dialogue/p06_"):
   director.restore()

func open(actor_id: String) -> bool:
 if not Characters.presentation_ready(actor_id) or actor_id == "yakuza": return false
 var path := "res://resources/dialogue/p06_" + actor_id + ".json"
 if director.resource_path != path or not director.active:
  if not director.start_scene(path): return false
 else:
  director.line_changed.emit(director.current_line())
  director.text_changed.emit(director.current_line().text_ru, director.visible_count)
 director.set_process(true)
 return true

func pause_view() -> void:
 if not is_instance_valid(director): return
 director.autosave()
 director.set_process(false)
 if director.audio: director.audio.dialogue_active(false)

func _exit_tree() -> void:
 if is_instance_valid(director):
  director.autosave()
  director.set_process(false)
 if owns_pause and is_instance_valid(campaign) and campaign.get_meta("p06_viewing_session", 0) == get_instance_id():
  campaign.remove_meta("p06_viewing_session")
  campaign.set_process(campaign_processing)
  if is_instance_valid(director) and director.audio: director.audio.dialogue_active(campaign.active)
 owns_pause = false
