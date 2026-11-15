extends SceneTree
## Independent fresh copied-project startup, not mixer or listening acceptance.
func _initialize() -> void:
 call_deferred("run")
func run() -> void:
 var audio: Node=root.get_node_or_null("AudioDirector")
 var mode: String=OS.get_environment("AYAY_C01_QA_MODE")
 var exists: bool=is_instance_valid(audio)
 var ready: bool=exists and bool(audio.get("ready_assets"))
 var children: int=audio.get_child_count() if exists else -1
 var cue: String="finish_gabar_unarmed"
 var entry: Variant=audio.get("manifest").get("sfx",{}).get(cue) if exists else null
 var repeat_return: bool=audio.load_assets() if exists else false
 var after_children: int=audio.get_child_count() if exists else -1
 var starts: int=audio.get("stem_starts") if exists else -1
 var pool_count: int=audio.get("voices").size() if exists else -1
 var spatial_pool_count: int=audio.get("spatial_voices").size() if exists else -1
 var checks: Array[Dictionary]=[]
 checks.append({"label":"autoload exists","passed":exists})
 if mode=="valid":
  checks.append({"label":"actual startup ready","passed":ready})
  checks.append({"label":"one music and two12voicepools","passed":children==25 and pool_count==12 and spatial_pool_count==12})
  checks.append({"label":"repeat load idempotent","passed":repeat_return and children==after_children and starts==1})
  checks.append({"label":"final actual gabar binding","passed":entry is Dictionary and entry.get("path")=="res://assets/audio/character_finishers/finish_gabar_unarmed.wav" and entry.get("bus")=="SFX" and entry.get("gain_db")==-2.5})
 else:
  checks.append({"label":"collision startup denied","passed":not ready and not repeat_return})
  checks.append({"label":"no partial music or voice nodes","passed":children==0 and after_children==0 and starts==0 and pool_count==0 and spatial_pool_count==0})
 var passed: bool=true
 for item in checks:
  passed=passed and bool(item.passed)
  print(("PASS " if item.passed else "FAIL ")+item.label)
 var result: Dictionary={"scope":"ISOLATED_STARTUP_NOT_MIX_OR_LISTENING","mode":mode,"ready_assets":ready,"audio_children":children,"resolved_gabar_entry":entry,"checks":checks,"passed":passed}
 var output: String=OS.get_environment("AYAY_C01_QA_OUTPUT")
 if not output.is_empty():
  var file: FileAccess=FileAccess.open(output,FileAccess.WRITE)
  if file:file.store_string(JSON.stringify(result,"  "))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
