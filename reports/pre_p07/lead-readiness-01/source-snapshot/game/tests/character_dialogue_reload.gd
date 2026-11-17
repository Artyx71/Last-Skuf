extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
 await process_frame
 var director: Node = root.get_node("DialogueDirector")
 director.set_process(false)
 var before := FileAccess.get_file_as_bytes(director.save_path)
 var restored: bool = director.restore()
 var ok: bool = restored and director.resource_path == "res://resources/dialogue/missed_fight_intro.json" and director.line_index == 1 and director.active and before == FileAccess.get_file_as_bytes(director.save_path)
 var result := {"passed":ok,"actual_new_process":true,"resource":director.resource_path,"line":director.line_index,"visible_count":director.visible_count,"campaign_file_unchanged":before == FileAccess.get_file_as_bytes(director.save_path)}
 var output := OS.get_environment("AYAY_P06_CAST_OUTPUT")
 var file := FileAccess.open(output.path_join("process-reload.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
 print("P06_CAST_PROCESS_RELOAD ", JSON.stringify(result))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if ok else 1)
