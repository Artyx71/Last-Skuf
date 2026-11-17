extends SceneTree
## Requires a fresh isolated copied project per fixture. Never modify actual WORK.
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var audio: Node=root.get_node_or_null("AudioDirector")
 var mode: String=OS.get_environment("AYAY_C01_QA_MODE")
 var exists: bool=is_instance_valid(audio)
 var ready: bool=exists and bool(audio.get("ready_assets"))
 var children: int=audio.get_child_count() if exists else -1
 var passed: bool=ready if mode=="valid" else (exists and not ready and children==0)
 var cue: String="finish_gabar_unarmed"
 var entry: Variant=audio.get("manifest").get("sfx",{}).get(cue) if exists else null
 var result: Dictionary={"scope":"ISOLATED_STARTUP_NOT_MIX_OR_LISTENING","mode":mode,"AudioDirector_exists":exists,"ready_assets":ready,"audio_children":children,"resolved_gabar_entry":entry,"passed":passed}
 print(JSON.stringify(result))
 var output: String=OS.get_environment("AYAY_C01_QA_OUTPUT")
 if not output.is_empty():
  var file: FileAccess=FileAccess.open(output,FileAccess.WRITE)
  if file:file.store_string(JSON.stringify(result,"  "))
 # Harness must additionally reject ANY Script Error/parser error; counts alone do not prove clean failure.
 quit(0 if passed else 1)
