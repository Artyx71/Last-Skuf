extends Node
## Sole campaign owner; viewing history remains DialogueDirector's responsibility.
signal changed
const Store = preload("res://scripts/story/story_state.gd")
var store: RefCounted
var session: RefCounted
var pending_replay := false
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

func begin_chapter(id: String) -> bool:
 if not store.registry.entry_ready(id,store.state): return false
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
