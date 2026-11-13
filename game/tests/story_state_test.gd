extends SceneTree
const Store = preload("res://scripts/story/story_state.gd")
var failures := 0
var checks := 0
func expect(ok: bool, title: String) -> void:
 checks += 1
 if not ok: failures += 1; push_error("FAIL: "+title)
func _initialize() -> void: call_deferred("run")
func run() -> void:
 var store := Store.new()
 store.path = OS.get_environment("AYAY_STORY_SAVE_PATH")
 expect(not store.path.is_empty(),"isolated_path")
 expect(store.registry.errors.is_empty(),"registry")
 expect(store.validate(store.state),"fresh_valid")
 var original: Dictionary = store.state.duplicate(true)
 for id in ["UNKNOWN", "EV_D01", "EV_CH02_COMPLETE", "EV_PHONE_DECODED"]:
  expect(not store.record(id) and store.state == original,"unavailable_no_mutation_"+id)
 expect(not store.record("EV_CH01_INTRO",1) and store.state == original,"strict_event_bool")
 expect(store.record("EV_CH01_INTRO"),"durable_intro")
 var bytes := FileAccess.get_file_as_string(store.path)
 expect(store.record("EV_CH01_INTRO") and FileAccess.get_file_as_string(store.path) == bytes,"idempotent_bytes")
 expect(store.complete_chapter(store.registry.CH01),"complete_ch01")
 var fresh := Store.new(); fresh.path = store.path
 expect(fresh.load_save() and fresh.state == store.state,"actual_disk_roundtrip")
 var sandbox: RefCounted = fresh.fork_replay()
 var before: Dictionary = fresh.state.duplicate(true)
 expect(not sandbox.record("EV_CH01_INTRO",false) and sandbox.state == before,"locked_replay_fact")
 expect(sandbox.complete_chapter(store.registry.CH01) and fresh.state == before,"replay_reward_once")
 expect(fresh.state.completion_rewards == 1,"one_reward")
 var blank := Store.new(); blank.path = store.path+".blank"
 var isolated: RefCounted = blank.fork_replay()
 expect(isolated.record("EV_CH01_PHONE") and blank.state.history.is_empty() and not FileAccess.file_exists(blank.path),"replay_new_fact_never_persists")
 for fault in ["newer","partial","range","bool","extra","duplicate","order"]:
  var invalid: Dictionary = fresh.state.duplicate(true)
  match fault:
   "newer": invalid.schema = 99
   "partial": invalid.erase("choices")
   "range": invalid.relationships.yakuza_olezhka = 3
   "bool": invalid.flags.kimono_truth = 0
   "extra": invalid.flags.unknown = true
   "duplicate": invalid.history.append(invalid.history[0])
   "order": invalid.history.push_front({"id":"EV_D01","value":true})
  expect(not fresh.validate(invalid),"reject_save_"+fault)
  var invalid_bytes := JSON.stringify(invalid)
  FileAccess.open(store.path,FileAccess.WRITE).store_string(invalid_bytes)
  var disk_invalid := Store.new(); disk_invalid.path = store.path
  expect(not disk_invalid.load_save() and not disk_invalid.writable and FileAccess.get_file_as_string(store.path) == invalid_bytes,"reject_disk_preserve_"+fault)
 var file := FileAccess.open(store.path,FileAccess.WRITE); file.store_string("{"); file.close()
 var broken := Store.new(); broken.path = store.path
 expect(not broken.load_save() and not broken.record("EV_CH01_INTRO") and FileAccess.get_file_as_string(store.path) == "{", "corrupt_preserved_write_disabled")
 var failure := Store.new(); failure.path = store.path+"/missing/save.json"
 before = failure.state.duplicate(true)
 expect(not failure.record("EV_CH01_INTRO") and failure.state == before,"open_failure_rollback")
 # Rename failure after a successful temporary write, not just open failure.
 failure.path = store.path+"-directory"; DirAccess.make_dir_absolute(failure.path)
 FileAccess.open(failure.path+"/keep",FileAccess.WRITE).close()
 expect(not failure.record("EV_CH01_INTRO") and failure.state == before and FileAccess.file_exists(failure.path+"/keep"),"rename_failure_rollback")
 var chapter_path := store.path+".legacy_chapter"
 var dialogue_path := store.path+".legacy_dialogue"
 var legacy := preload("res://scripts/levels/chapter_progress.gd").new(); legacy.path = chapter_path
 expect(legacy.complete(1000) and legacy.record_death(),"legacy_fixture")
 var dialogue := {"schema":1,"resource":"res://resources/dialogue/missed_fight_phone.json","active":false,"line_index":0,"visible_count":0,"line_elapsed":0.0,"history":[],"seen":{"CH01_PHONE":true},"ledger":{"EV_CH01_PHONE":true},"flags":{"ch01_phone_seen":true}}
 file = FileAccess.open(dialogue_path,FileAccess.WRITE); file.store_string(JSON.stringify(dialogue)); file.close()
 var chapter_bytes := FileAccess.get_file_as_string(chapter_path)
 var dialogue_bytes := FileAccess.get_file_as_string(dialogue_path)
 DirAccess.remove_absolute(store.path)
 var migrated := Store.new(); migrated.path = store.path
 expect(migrated.load_save(chapter_path,dialogue_path) and migrated.status == "MIGRATED", "migrate_legacy")
 expect(migrated.state.ledger.has("EV_CH01_PHONE") and migrated.state.chapter_complete.has(store.registry.CH01) and migrated.state.completion_rewards == 1,"migrated_facts")
 var failed_migration := Store.new(); failed_migration.path = store.path+"/missing/story.json"
 expect(not failed_migration.load_save(chapter_path,dialogue_path) and failed_migration.state.history.is_empty() and not failed_migration.writable,"migration_write_rollback")
 expect(chapter_bytes == FileAccess.get_file_as_string(chapter_path) and dialogue_bytes == FileAccess.get_file_as_string(dialogue_path),"legacy_bytes_untouched")
 var again := Store.new(); again.path = store.path
 expect(again.load_save(chapter_path,dialogue_path) and again.state == migrated.state,"migration_once")
 # A bad legacy file cannot silently create a fresh campaign.
 DirAccess.remove_absolute(store.path)
 file = FileAccess.open(dialogue_path,FileAccess.WRITE); file.store_string('{"schema":1}'); file.close()
 var bad_legacy := Store.new(); bad_legacy.path = store.path
 expect(not bad_legacy.load_save(chapter_path,dialogue_path) and not FileAccess.file_exists(store.path),"partial_legacy_preserved")
 print("STORY_STATE_TEST checks=",checks," failures=",failures)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failures else 0)
