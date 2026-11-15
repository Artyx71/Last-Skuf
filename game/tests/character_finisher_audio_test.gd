extends SceneTree
## Real imported assets and denied/malformed routing; not mixer/listening evidence.
const Routes = preload("res://scripts/systems/character_finisher_audio.gd")
const Profile = preload("res://scripts/systems/character_combat_profile.gd")
const EXPECTED := {
 "gabar":["unarmed","blunt","firearm"], "olezhka":["unarmed","blunt","sharp"],
 "timka":["unarmed","blunt","environmental"], "ryzhik":["unarmed","blunt","environmental"],
 "tega":["unarmed","blunt","environmental"], "pasha":["unarmed","blunt","sharp","firearm","environmental"]
}
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, label: String) -> void:
 if ok: passed+=1; print("PASS ",label)
 else: failed+=1; push_error("FAIL "+label)
func run() -> void:
 var data: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(Routes.PATH))
 var entries: Dictionary=Routes.entries()
 var base: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://resources/combat/finishers.json")).definitions
 var timings: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://resources/characters/combat_profiles.json")).profiles
 var audio: Node=root.get_node("AudioDirector")
 check(entries.size()==20 and audio.ready_assets,"twenty real routes; actual autoload starts")
 var paths: Array=[]
 var hashes: Array=[]
 for actor_id in EXPECTED:
  var context: String="athletic_prime" if actor_id=="timka" else "training"
  for category in base:
   var cue: String=Routes.cue_for(actor_id,context,category)
   if category not in EXPECTED[actor_id]:
    check(cue.is_empty(),actor_id+":"+category+" denied")
    continue
   var wanted: String="finish_"+actor_id+("_prime" if actor_id=="timka" else "")+"_"+category
   check(cue==wanted and entries.has(wanted),wanted+" exact route")
   if not entries.has(wanted): continue
   var entry: Dictionary=entries[wanted]
   var stream: Resource=load(entry.path)
   check(stream is AudioStreamWAV and not stream.stereo and stream.mix_rate==44100 and stream.loop_mode==AudioStreamWAV.LOOP_DISABLED and stream.get_length()>=0.20 and stream.get_length()<=0.35,wanted+" actual imported mono44100 finite nonlooping stream")
   var bytes:=FileAccess.get_file_as_bytes(entry.path)
   var digest:=HashingContext.new();digest.start(HashingContext.HASH_SHA256);digest.update(bytes)
   var hash: String=digest.finish().hex_encode()
   check(hash==entry.source_sha256 and hash not in hashes and entry.path not in paths,wanted+" actual source SHA and unique file")
   hashes.append(hash);paths.append(entry.path)
   check(audio.manifest.sfx.get(wanted)==entry and entry.bus=="SFX",wanted+" engine registry exact binding")
   var copy: Dictionary=Profile.resolve_finisher(actor_id,context,category,base[category])
   var old: Dictionary=base[category].duplicate(true)
   for field in old:
    if field not in ["windup","active","recovery","cue"]:
     check(copy.get(field)==old[field],wanted+" preserves gameplay "+field)
   check(copy.get("cue")==wanted and copy.get("windup")==timings[actor_id].finisher.windup and copy.get("active")==timings[actor_id].finisher.active and copy.get("recovery")==timings[actor_id].finisher.recovery,wanted+" keeps accepted clocks")
 for category in base:
  check(Routes.cue_for("timka","peaceful_present",category).is_empty(),"present grants no cue "+category)
  check(Profile.resolve_finisher("yakuza","training",category,base[category])==base[category],"Yakuza whole definition unchanged "+category)
  check(audio.manifest.sfx[base[category].cue].path=="res://assets/audio/combat_polish/finish_"+category+".wav","Yakuza legacy stream retained "+category)
 for actor_id in ["kaban","ellana","elya","unknown","yakuza"]:
  check(Routes.cue_for(actor_id,"training","unarmed").is_empty(),"no new cue grant "+actor_id)
 check(Routes.cue_for("timka","training","unarmed").is_empty() and Routes.cue_for("gabar","athletic_prime","unarmed").is_empty(),"wrong contexts denied")
 # Mutations of a valid manifest probe real binding failures, not missing labels alone.
 for value in [null,[],"text",1,true]:
  check(not Routes._valid_manifest(value),"non-object rejected "+str(value))
 for value in [null,true,0,2,"1"]:
  var bad: Dictionary=data.duplicate(true);bad.schema=value
  check(not Routes._valid_manifest(bad),"invalid schema rejected "+str(value))
 for value in [null,[],"text"]:
  var bad: Dictionary=data.duplicate(true);bad.sfx=value
  check(not Routes._valid_manifest(bad),"non-object cues rejected "+str(value))
 var name: String="finish_gabar_unarmed"
 for field in ["actor_id","context","category","path","bus","gain_db"]:
  var bad: Dictionary=data.duplicate(true);bad.sfx[name].erase(field)
  check(not Routes._valid_manifest(bad),"missing binding rejected "+field)
 for pair in [["actor_id","pasha"],["context","athletic_prime"],["category","blunt"],["path",data.sfx.finish_pasha_unarmed.path],["path","res://missing.wav"],["bus","Music"],["gain_db",true],["gain_db","-2.5"],["gain_db",1],["gain_db",-25],["gain_db",NAN],["gain_db",INF]]:
  var bad: Dictionary=data.duplicate(true);bad.sfx[name][pair[0]]=pair[1]
  check(not Routes._valid_manifest(bad),"invalid binding rejected "+str(pair))
 var missing: Dictionary=data.duplicate(true);missing.sfx.erase(name)
 check(not Routes._valid_manifest(missing),"missing required route rejected")
 var extra: Dictionary=data.duplicate(true);extra.sfx["finish_timka_prime_firearm"]=data.sfx[name]
 check(not Routes._valid_manifest(extra),"extra forbidden route rejected")
 var detached:=Routes.entries();detached[name].path="res://missing.wav"
 check(Routes.entries()[name].path==data.sfx[name].path,"caller mutation cannot replace subsequent asset binding")
 print("RESULT passed=%d failed=%d" % [passed,failed])
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
