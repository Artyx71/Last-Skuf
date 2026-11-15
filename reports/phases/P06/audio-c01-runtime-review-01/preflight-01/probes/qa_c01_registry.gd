extends SceneTree
## Independent QA probe. NOT EXECUTED during preflight. Copy into isolated project only.
const Routing = preload("res://scripts/systems/character_finisher_audio.gd")
var checks: Array[Dictionary] = []
func _initialize() -> void:
 call_deferred("run")
func check(label: String, passed: bool) -> void:
 checks.append({"label":label,"passed":passed})
 print(("PASS " if passed else "FAIL ")+label)
func run() -> void:
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(Routing.PATH))
 check("actual registry valid",Routing._valid_manifest(parsed))
 if not parsed is Dictionary:
  quit(1)
  return
 var cue: String="finish_gabar_unarmed"
 for replacement in [null,[],false,"bad"]:
  check("top-level invalid "+str(replacement),not Routing._valid_manifest(replacement,false))
 for field in ["actor_id","context","category","path","bus"]:
  var wrong: Dictionary=parsed.duplicate(true)
  wrong.sfx[cue][field]="wrong"
  check("reject wrong "+field,not Routing._valid_manifest(wrong,false))
 for gain in [true,"-2.5",null,1.0,-25.0,INF,NAN]:
  var wrong: Dictionary=parsed.duplicate(true)
  wrong.sfx[cue].gain_db=gain
  check("reject invalid gain "+str(gain),not Routing._valid_manifest(wrong,false))
 var missing: Dictionary=parsed.duplicate(true)
 missing.sfx.erase(cue)
 check("reject missing required cue",not Routing._valid_manifest(missing,false))
 var extra: Dictionary=parsed.duplicate(true)
 extra.sfx["finish_timka_prime_firearm"]=extra.sfx[cue].duplicate(true)
 check("reject extra excluded cue",not Routing._valid_manifest(extra,false))
 check("Timka present has no cue",Routing.cue_for("timka","present","unarmed").is_empty())
 check("Timka prime no firearm",Routing.cue_for("timka","athletic_prime","firearm").is_empty())
 check("unknown actor no cue",Routing.cue_for("unknown","training","unarmed").is_empty())
 check("wrong context no cue",Routing.cue_for("gabar","athletic_prime","unarmed").is_empty())
 # Observations only: raw SHA verification may instead be enforced by independent build verifier.
 var sha_missing: Dictionary=parsed.duplicate(true)
 sha_missing.erase("source_signal_decision_sha256")
 sha_missing.erase("source_recipe_sha256")
 for id in sha_missing.sfx:sha_missing.sfx[id].erase("source_sha256")
 var observations: Dictionary={"missing_signal_binding_metadata_runtime_validator_accepts":Routing._valid_manifest(sha_missing,false)}
 var output: String=OS.get_environment("AYAY_C01_QA_OUTPUT")
 var result: Dictionary={"scope":"INDEPENDENT_REGISTRY_COMPONENT_ONLY","checks":checks,"observations":observations,"not_listening":true,"not_actual_mixer":true}
 if not output.is_empty():
  var file: FileAccess=FileAccess.open(output,FileAccess.WRITE)
  if file:file.store_string(JSON.stringify(result,"  "))
 var failures: int=0
 for item in checks:
  if not item.passed:failures+=1
 quit(0 if failures==0 else 1)
