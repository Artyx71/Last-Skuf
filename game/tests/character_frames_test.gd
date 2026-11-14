extends SceneTree
## Authored atlas layout/availability only; not Input/combat/phase acceptance.
const Frames = preload("res://scripts/actors/character_frames.gd")
var checks := 0
var failures := 0

func record(label: String, passed: bool) -> void:
 checks += 1
 if not passed:
  failures += 1
  push_error("FAIL P06_CHARACTER_FRAMES "+label)

func _initialize() -> void: call_deferred("run")

func check_sheet(frames: SpriteFrames, kind: String, mapping: Dictionary) -> void:
 record(kind+"_available",frames!=null)
 if frames==null: return
 record(kind+"_all_direction_clips",frames.get_animation_names().size()==mapping.size()*4)
 for row in 4:
  for state in mapping:
   var name := StringName(state+"_"+["down","left","right","up"][row])
   record(String(name)+"_count",frames.get_frame_count(name)==mapping[state].size())
   record(String(name)+"_loop",frames.get_animation_loop(name)==(kind=="world"))
   var expected_fps: float={"idle":3.0,"walk":8.0,"run":12.0}[state] if kind=="world" else 10.0
   record(String(name)+"_fps",frames.get_animation_speed(name)==expected_fps)
   for index in mapping[state].size():
    var atlas := frames.get_frame_texture(name,index) as AtlasTexture
    record(String(name)+"_authored_texture_"+str(index),atlas!=null and atlas.atlas.resource_path=="res://assets/art/characters/gabar/"+kind+"_sheet.png")
    if atlas==null: continue
    var column: int=mapping[state][index]
    record(String(name)+"_exact_source_cell_"+str(index),atlas.region==Rect2(column*48,row*64,48,64))
    record(String(name)+"_identity_metadata_"+str(index),atlas.get_meta("character_id")=="gabar" and atlas.get_meta("source_kind")==kind and atlas.get_meta("source_direction")==["down","left","right","up"][row] and atlas.get_meta("source_column")==column)

func run() -> void:
 check_sheet(Frames.world_frames("gabar"),"world",{"idle":[0,1],"walk":[2,3,4,5],"run":[6,7]})
 # New hurt4/interact3/fall5,6 differ from the existing Yakuza sheet layout.
 check_sheet(Frames.action_frames("gabar"),"action",{"shove":[0,1,2],"interact":[3],"hit":[4],"fall":[5,6],"fire":[7]})
 record("Olezhka_world_available",Frames.world_frames("olezhka")!=null)
 record("unknown_world_denied",Frames.world_frames("unknown")==null)
 record("unknown_action_denied",Frames.action_frames("unknown")==null)
 record("unknown_finisher_denied",Frames.finisher_frames("unknown")==null)
 record("supporting_cannot_construct_combat",Frames.combat_frames("ellana")==null)
 record("existing_Yakuza_keeps_original_path",Frames.combat_frames("yakuza")==null)
 record("missing_Olezhka_combat_art_never_falls_back",Frames.combat_frames("olezhka")==null)
 # Finisher art is deliberately not substituted while the source task is pending.
 record("Gabar_combat_construction_requires_all_three_sheets",Frames.combat_frames("gabar")==null)
 for value in [null,42,true,[],{},&"res://assets/art/characters/gabar/world_sheet.png",""]:
  record("malformed_texture_path_rejected:"+str(value),Frames._sheet_texture(value)==null)
 record("script_resource_is_not_a_texture",Frames._sheet_texture("res://scripts/systems/character_catalog.gd")==null)
 record("missing_texture_is_not_substituted",Frames._sheet_texture("res://assets/art/characters/unknown/world_sheet.png")==null)
 record("wrong_texture_dimensions_rejected",Frames._sheet_texture("res://assets/art/characters/gabar/portraits.png")==null)
 var valid: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/art/characters/gabar/action.json"))
 record("real_action_metadata_validates",Frames._valid_layout(valid,"gabar","action"))
 record("metadata_identity_mismatch_rejected",not Frames._valid_layout(valid,"olezhka","action"))
 record("unknown_sheet_kind_rejected",not Frames._valid_layout(valid,"gabar","unknown"))
 for value in [null,[],true,"not JSON metadata"]:
  record("malformed_metadata_root_rejected:"+str(value),not Frames._valid_layout(value,"gabar","action"))
 var malformed: Dictionary=valid.duplicate(true)
 malformed.animations_source_columns.hit=[3,4]
 record("legacy_Yakuza_hurt_mapping_rejected",not Frames._valid_layout(malformed,"gabar","action"))
 malformed=valid.duplicate(true);malformed.frames.pop_back()
 record("missing_source_cell_rejected",not Frames._valid_layout(malformed,"gabar","action"))
 malformed=valid.duplicate(true);malformed.frames[1].column=0
 record("duplicate_cell_index_rejected",not Frames._valid_layout(malformed,"gabar","action"))
 malformed=valid.duplicate(true);malformed.frames[0].column=false
 record("boolean_column_is_not_numeric_zero",not Frames._valid_layout(malformed,"gabar","action"))
 malformed=valid.duplicate(true);malformed.frames[0].rect=[0,0,48,64.5]
 record("fractional_cell_bounds_rejected",not Frames._valid_layout(malformed,"gabar","action"))
 malformed=valid.duplicate(true);malformed.frames[0].rect=[0,0,"48",64]
 record("text_dimension_is_not_a_number",not Frames._valid_layout(malformed,"gabar","action"))
 print("RESULT P06_CHARACTER_FRAMES passed=",checks-failures," failed=",failures)
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failures else 0)
