extends RefCounted
## Isolated compatibility-pilot candidate; not installed in StoryService or shipped UI.
const Story = preload("res://scripts/story/story_state.gd")
const IDS := ["BONUS_OFFLINE_BUILD", "BONUS_COUNTER_LESSON"]
const CHAPTERS := ["CH14_AGENT_SWARM", "CH10_THE_KIMONO"]
const BOOTSTRAP := "res://scenes/bootstrap/bootstrap.tscn"
var owner: Node
var state := fresh()
var path := ""
var writable := true
var error := ""
var generation := 0
var _store: RefCounted
var _campaign_path := ""
var _active: Dictionary = {}
var _return: Dictionary = {}

static func fresh() -> Dictionary:
	return {"schema":1,"domain":"bonus_profile","history":[],
		"completed":{IDS[0]:false,IDS[1]:false}}

func _init(service: Node) -> void:
	owner = service
	_sync_scope()

func _fail(message: String) -> bool:
	error = message
	return false

func revoke() -> void:
	generation += 1
	_active.clear()
	_return.clear()

func _sync_scope() -> bool:
	if not is_instance_valid(owner) or not owner.store is Story: return _fail("OWNER_INVALID")
	var current: RefCounted = owner.store
	if current.path.is_empty(): return _fail("PROFILE_INVALID")
	var current_path: String = ProjectSettings.globalize_path(current.path).simplify_path()
	if current != _store or current_path != _campaign_path:
		revoke()
		_store = current
		_campaign_path = current_path
		path = current_path.get_base_dir().path_join("bonus_progress_v1.json")
		state = fresh()
		writable = true
		error = ""
		return load_save()
	return true

func _valid_campaign() -> bool:
	if not _sync_scope() or owner.session != _store or owner.pending_replay: return false
	if not _store.writable or _store.simulation or _store.replay or not _store.validate(_store.state): return false
	if not FileAccess.file_exists(_campaign_path): return false
	var disk: Variant = Story.read_json(_campaign_path)
	return _store.validate(disk) and _store._equivalent(disk,_store.state)

func _prerequisite(id: String) -> bool:
	var index := IDS.find(id)
	if index < 0: return false
	var chapter: String = CHAPTERS[index]
	return _store.registry.entry_ready(chapter,_store.state) and _store.state.chapter_complete.get(chapter,false)

func _scene_path(_id: String) -> String:
	# Both actual bonus missions remain planned; a save cannot supply a scene/ability grant.
	return ""

func can_launch(id: String) -> bool:
	return id in IDS and _valid_campaign() and writable \
		and path == _campaign_path.get_base_dir().path_join("bonus_progress_v1.json") \
		and _prerequisite(id) and not _scene_path(id).is_empty()

func begin(id: String, host: Variant, origin: Variant) -> bool:
	if not can_launch(id) or not is_instance_valid(host) or not is_instance_valid(origin): return _fail("UNAVAILABLE")
	if not host is Node or not origin is Node: return _fail("HOST_INVALID")
	if origin.scene_file_path != BOOTSTRAP or origin.get_tree().current_scene != origin: return _fail("ORIGIN_INVALID")
	if host.scene_file_path != _scene_path(id): return _fail("HOST_INVALID")
	revoke()
	_active = {"id":id,"host":weakref(host),"generation":generation,"store":_store,
		"profile":_campaign_path,"origin":weakref(origin),"replay":state.completed[id]}
	return true

func _authorized(host: Variant) -> bool:
	if not is_instance_valid(host) or not host is Node: return false
	if host.is_queued_for_deletion() or not host.is_inside_tree(): return false
	if not _valid_campaign() or _active.is_empty(): return false
	if not writable or path != _campaign_path.get_base_dir().path_join("bonus_progress_v1.json"): return false
	return is_instance_valid(host) and _active.host.get_ref() == host and _active.store == _store \
		and _active.profile == _campaign_path and _active.generation == generation \
		and host.scene_file_path == _scene_path(_active.id) and _prerequisite(_active.id)

func complete(host: Variant) -> bool:
	# Check current owner/prerequisite BEFORE the idempotent and read-only branches.
	if not _authorized(host): return _fail("SESSION_REVOKED")
	var request_generation := generation
	if not host.has_method("bonus_goal_ready"): return _fail("GOAL_UNRESOLVED")
	var ready: Variant = host.bonus_goal_ready()
	# A host callback may synchronously revoke, replace the profile, or free itself.
	if not _authorized(host) or generation != request_generation: return _fail("SESSION_REVOKED")
	if not ready is bool or not ready: return _fail("GOAL_UNRESOLVED")
	if _active.replay or state.completed[_active.id]: return true
	var candidate := state.duplicate(true)
	candidate.history.append(_active.id)
	candidate.completed[_active.id] = true
	if not validate(candidate) or not _write(candidate): return false
	state = candidate
	return true

func request_return(host: Variant) -> bool:
	if not _authorized(host): return _fail("RETURN_REVOKED")
	_return = {"store":_store,"profile":_campaign_path,"generation":generation}
	_active.clear()
	return true

func consume_return(bootstrap: Variant) -> bool:
	if not _sync_scope() or _return.is_empty() or not is_instance_valid(bootstrap): return false
	if not bootstrap is Node: return false
	var allowed: bool = _return.store == _store and _return.profile == _campaign_path \
		and _return.generation == generation and bootstrap.scene_file_path == BOOTSTRAP \
		and bootstrap.get_tree().current_scene == bootstrap
	revoke()
	return allowed

static func validate(value: Variant) -> bool:
	if not value is Dictionary or value.size() != 4: return false
	if not value.get("schema") is float and not value.get("schema") is int: return false
	if value.schema != 1 or value.get("domain") != "bonus_profile": return false
	if not value.get("history") is Array or value.history.size() > 2 or not value.get("completed") is Dictionary: return false
	if value.completed.size() != 2: return false
	var expected := fresh()
	for id in value.history:
		if not id is String or not id in IDS or expected.completed[id]: return false
		expected.history.append(id)
		expected.completed[id] = true
	for id in IDS:
		if not value.completed.get(id) is bool or value.completed[id] != expected.completed[id]: return false
	return true

static func strict_decode(text: String) -> Variant:
	if text.length() > 65536: return null
	var parser := JSON.new()
	if parser.parse(text) != OK: return null
	# Native JSON accepts duplicate keys/trailing commas; this six-key namespace must not.
	var strings := RegEx.create_from_string('"([^"\\\\]|\\\\.)*"')
	var keys := {}
	var outside := ""
	var previous := 0
	for token in strings.search_all(text):
		outside += text.substr(previous,token.get_start()-previous)+"s"
		previous = token.get_end()
		if text.substr(previous).strip_edges().begins_with(":"):
			var key: Variant = JSON.parse_string(token.get_string())
			if keys.has(key): return null
			keys[key] = true
	outside += text.substr(previous)
	for whitespace in [" ","\t","\r","\n"]: outside = outside.replace(whitespace,"")
	if ",}" in outside or ",]" in outside: return null
	return parser.data if validate(parser.data) else null

func load_save() -> bool:
	if not FileAccess.file_exists(path): return true
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null: writable = false; return _fail("READ_FAILED")
	if file.get_length() > 65536: file.close(); writable = false; return _fail("OVERSIZE_PRESERVED")
	var text := file.get_as_text()
	var read_error := file.get_error()
	file.close()
	var parsed: Variant = strict_decode(text)
	if read_error != OK or parsed == null:
		writable = false
		return _fail("INVALID_PRESERVED")
	# JSON numbers are floats; rebuild the typed derived state just like StoryState.load_save.
	state = fresh()
	for id in parsed.history:
		state.history.append(id)
		state.completed[id] = true
	return true

func _boundary(_stage: String) -> bool:
	return true

func _write(candidate: Dictionary) -> bool:
	var temporary := path+".tmp"
	var file := FileAccess.open(temporary,FileAccess.WRITE)
	if file == null: return _fail("OPEN_FAILED")
	file.store_string(JSON.stringify(candidate,"  "))
	file.flush()
	var write_error := file.get_error()
	file.close()
	if write_error != OK or not _boundary("written"):
		DirAccess.remove_absolute(temporary)
		return _fail("WRITE_FAILED")
	if not _boundary("before_rename") or DirAccess.rename_absolute(temporary,path) != OK:
		DirAccess.remove_absolute(temporary)
		return _fail("RENAME_FAILED")
	_boundary("after_rename")
	return true
