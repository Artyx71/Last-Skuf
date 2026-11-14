extends RefCounted
## Authored character atlas playback. This loader does not authorize combat actions.
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const DIRECTIONS := ["down", "left", "right", "up"]
const WORLD_COLUMNS := {"idle":[0,1], "walk":[2,3,4,5], "run":[6,7]}
const ACTION_COLUMNS := {"shove":[0,1,2], "interact":[3], "hit":[4], "fall":[5,6], "fire":[7]}
const FINISHER_COLUMNS := {"finish_unarmed":[0,1,6], "finish_blunt":[0,2,6], "finish_sharp":[0,3,6], "finish_firearm":[0,4,6], "finish_environmental":[0,5,6], "special":[0,7,6]}
const SHEET_COLUMNS := {"world":WORLD_COLUMNS, "action":ACTION_COLUMNS, "finisher":FINISHER_COLUMNS}
const SIZE := Vector2(48,64)
const PIVOT := Vector2(24,58)

static func _matches_numbers(actual: Variant, expected: Array) -> bool:
 if not actual is Array or actual.size() != expected.size(): return false
 for index in expected.size():
  if not (actual[index] is float or actual[index] is int) or actual[index] != expected[index]: return false
 return true

static func world_frames(actor_id: String) -> SpriteFrames:
 return _sheet_frames(actor_id,"world")

static func action_frames(actor_id: String) -> SpriteFrames:
 return _sheet_frames(actor_id,"action")

static func finisher_frames(actor_id: String) -> SpriteFrames:
 return _sheet_frames(actor_id,"finisher")

static func combat_frames(actor_id: String) -> SpriteFrames:
 # A missing authored sheet prevents construction; there is no Yakuza fallback.
 var result := world_frames(actor_id)
 var action := action_frames(actor_id)
 var finisher := finisher_frames(actor_id)
 if result == null or action == null or finisher == null: return null
 for addition in [action,finisher]:
  for name in addition.get_animation_names():
   result.add_animation(name)
   result.set_animation_speed(name,addition.get_animation_speed(name))
   result.set_animation_loop(name,addition.get_animation_loop(name))
   for index in addition.get_frame_count(name):
    result.add_frame(name,addition.get_frame_texture(name,index),addition.get_frame_duration(name,index))
 return result

static func _sheet_frames(actor_id: String, kind: String) -> SpriteFrames:
 if not SHEET_COLUMNS.has(kind): return null
 var definition := Catalog.actor(actor_id)
 if definition.get("role") != "playable" or not definition.has(kind+"_file"): return null
 var path_value: Variant = definition[kind+"_file"]
 if not path_value is String or path_value.is_empty(): return null
 var path: String = path_value
 var metadata_path := path.get_base_dir().path_join(kind+".json")
 if not ResourceLoader.exists(path) or not FileAccess.file_exists(metadata_path): return null
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(metadata_path))
 if not _valid_layout(parsed,actor_id,kind): return null
 var expected: Dictionary = SHEET_COLUMNS[kind]
 var texture := _sheet_texture(path_value)
 if texture == null: return null
 var frames := SpriteFrames.new()
 frames.remove_animation(&"default")
 for row in DIRECTIONS.size():
  for state in expected:
   var animation := StringName(state+"_"+DIRECTIONS[row])
   frames.add_animation(animation)
   frames.set_animation_speed(animation,{"idle":3.0,"walk":8.0,"run":12.0}[state] if kind=="world" else 10.0)
   frames.set_animation_loop(animation,kind=="world")
   for column in expected[state]:
    var atlas := AtlasTexture.new()
    atlas.atlas = texture
    atlas.region = Rect2(Vector2(column,row)*SIZE,SIZE)
    atlas.set_meta("character_id",actor_id)
    atlas.set_meta("source_kind",kind)
    atlas.set_meta("source_direction",DIRECTIONS[row])
    atlas.set_meta("source_column",column)
    frames.add_frame(animation,atlas)
 return frames

static func _sheet_texture(path_value: Variant) -> Texture2D:
 if not path_value is String or path_value.is_empty() or not ResourceLoader.exists(path_value): return null
 var resource: Resource = load(path_value)
 if not resource is Texture2D: return null
 var texture := resource as Texture2D
 return texture if texture.get_size()==Vector2(384,256) else null

static func _valid_layout(parsed: Variant, actor_id: String, kind: String) -> bool:
 if not SHEET_COLUMNS.has(kind) or not parsed is Dictionary: return false
 if parsed.get("schema") != 1 or parsed.get("actor_id") != actor_id or parsed.get("kind") != kind: return false
 if not _matches_numbers(parsed.get("frame_size"),[48,64]) or not _matches_numbers(parsed.get("pivot"),[24,58]) or parsed.get("directions") != DIRECTIONS: return false
 var expected: Dictionary = SHEET_COLUMNS[kind]
 var columns: Variant = parsed.get("animations_source_columns")
 if not columns is Dictionary or columns.size()!=expected.size(): return false
 for state in expected:
  if not _matches_numbers(columns.get(state),expected[state]): return false
 var source_frames: Variant = parsed.get("frames")
 if not source_frames is Array or source_frames.size()!=32 or parsed.get("source_cells")!=32: return false
 for index in 32:
  var entry: Variant = source_frames[index]
  var row := index/8
  var column := index%8
  if not entry is Dictionary or entry.get("direction")!=DIRECTIONS[row]: return false
  if not _matches_numbers([entry.get("column")],[column]): return false
  if not _matches_numbers(entry.get("rect"),[column*48,row*64,48,64]): return false
 return true
