extends Node
## Sole campaign owner; viewing history remains DialogueDirector's responsibility.
signal changed
const Store = preload("res://scripts/story/story_state.gd")
const Bonus = preload("res://scripts/story/bonus_progress.gd")
var bonus: RefCounted
var store: RefCounted:
 set(value):
  if bonus != null: bonus.revoke()
  store = value
var session: RefCounted:
 set(value):
  if value != store and bonus != null: bonus.revoke()
  session = value
var pending_replay := false:
 set(value):
  if value and bonus != null: bonus.revoke()
  pending_replay = value
var error_message := ""
const DIALOGUE_EVENTS := {"CH01_INTRO":"EV_CH01_INTRO","CH01_PHONE":"EV_CH01_PHONE","CH01_OUTRO":"EV_CH01_OUTRO"}

func _ready() -> void:
 store = Store.new()
 var override := OS.get_environment("AYAY_STORY_SAVE_PATH")
 if not override.is_empty(): store.path = override
 var chapter := preload("res://scripts/levels/chapter_progress.gd").new()
 var director := get_node("/root/DialogueDirector")
 if not store.load_save(chapter.path,director.save_path):
  store.writable = false
  error_message = "История не записывается. Сохранение оставлено для восстановления."
 session = store
 director.finished.connect(_on_dialogue_finished)
 get_tree().scene_changed.connect(_on_scene_changed)

func _bonuses() -> RefCounted:
 if bonus == null: bonus = Bonus.new(self)
 return bonus

func adopt_campaign(candidate: RefCounted) -> bool:
 if not candidate is Store or candidate.simulation or candidate.replay or not candidate.writable: return false
 if candidate.path.is_empty() or not candidate.validate(candidate.state): return false
 var disk: Variant = Store.read_json(candidate.path)
 if not candidate.validate(disk) or not candidate._equivalent(disk,candidate.state): return false
 # Rebinding even the same Store is the owner boundary for a new campaign/profile.
 store = candidate
 session = store
 pending_replay = false
 changed.emit()
 return true

func bonus_entries() -> Array[Dictionary]:
 var controller := _bonuses()
 var entries: Array[Dictionary] = []
 for index in Bonus.IDS.size():
  var id: String = Bonus.IDS[index]
  var available: bool = controller.can_launch(id)
  entries.append({"id":id,"title":Bonus.TITLES[index],"available":available,"completed":controller.state.completed[id]})
 return entries

func launch_bonus(id: String, origin: Variant) -> bool:
 var controller := _bonuses()
 if not controller.can_launch(id): return false
 var packed: Variant = load(controller._scene_path(id))
 if not packed is PackedScene: return false
 var host: Node = packed.instantiate()
 if not controller.begin(id,host,origin): host.free(); return false
 if get_tree().change_scene_to_node(host) != OK:
  controller.revoke(); host.free(); return false
 return true

func complete_bonus(host: Variant) -> bool:
 return _bonuses().complete(host)

func leave_bonus(host: Variant) -> bool:
 var controller := _bonuses()
 if not controller.request_return(host): return false
 if get_tree().change_scene_to_file(Bonus.BOOTSTRAP) != OK:
  controller.revoke(); return false
 return true

func consume_bonus_return(bootstrap: Node) -> bool:
 return bonus != null and bonus.consume_return(bootstrap)

func _on_scene_changed() -> void:
 if bonus != null: bonus.scene_changed(get_tree().current_scene)

func begin_chapter(id: String) -> bool:
 if not store.registry.entry_ready(id,store.state): return false
 if bonus != null: bonus.revoke()
 session = store.fork_replay() if pending_replay or store.state.chapter_complete.has(id) else store
 pending_replay = false
 return true

func sync_dialogue(director: Node) -> bool:
 for scene_id in DIALOGUE_EVENTS:
  var event_id: String = DIALOGUE_EVENTS[scene_id]
  if director.ledger.get(event_id,false) and not session.state.ledger.has(event_id):
   # Completed saves imported before P05 may lack dialogue facts. They stay locked;
   # viewing old scenes cannot retroactively add campaign facts.
   if session.state.chapter_complete.has(store.registry.CH01): continue
   if not session.record(event_id): return _error()
 return true

func _on_dialogue_finished(scene_id: StringName) -> void:
 if not DIALOGUE_EVENTS.has(String(scene_id)): return
 var id: String = DIALOGUE_EVENTS[String(scene_id)]
 if session.state.chapter_complete.has(store.registry.CH01): return
 if not session.record(id): _error()
 else:
  error_message = ""; changed.emit()

func resume_progress(progress: RefCounted, director: Node) -> bool:
 if not store.writable: return _error()
 if not sync_dialogue(director): return false
 if progress.data.completed and not store.state.chapter_complete.has(store.registry.CH01):
  if not store.complete_chapter(store.registry.CH01): return _error()
 return true

func complete_ch01(director: Node) -> bool:
 if not sync_dialogue(director): return false
 if not session.complete_chapter(store.registry.CH01): return _error()
 error_message = ""
 changed.emit()
 return true

func _error() -> bool:
 error_message = "Не удалось сохранить историю. Проверьте доступ к файлу и повторите выход."
 return false
