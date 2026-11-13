extends RefCounted
## Authored character atlas playback. This loader does not authorize combat actions.
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const DIRECTIONS := ["down", "left", "right", "up"]
const WORLD_COLUMNS := {"idle":[0,1], "walk":[2,3,4,5], "run":[6,7]}
const SIZE := Vector2(48,64)
const PIVOT := Vector2(24,58)

static func _matches_numbers(actual: Variant, expected: Array) -> bool:
 if not actual is Array or actual.size() != expected.size(): return false
 for index in expected.size():
  if not (actual[index] is float or actual[index] is int) or actual[index] != expected[index]: return false
 return true

static func world_frames(actor_id: String) -> SpriteFrames:
 var definition := Catalog.actor(actor_id)
 if definition.get("role") != "playable" or not definition.has("world_file"): return null
 var path: String = definition.world_file
 var metadata_path := path.get_base_dir().path_join("world.json")
 if not ResourceLoader.exists(path) or not FileAccess.file_exists(metadata_path): return null
 var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(metadata_path))
 if not parsed is Dictionary: return null
 if parsed.get("schema") != 1 or parsed.get("actor_id") != actor_id or parsed.get("kind") != "world": return null
 if not _matches_numbers(parsed.get("frame_size"),[48,64]) or not _matches_numbers(parsed.get("pivot"),[24,58]) or parsed.get("directions") != DIRECTIONS: return null
 var columns: Variant = parsed.get("animations_source_columns")
 if not columns is Dictionary or columns.size() != WORLD_COLUMNS.size(): return null
 for state in WORLD_COLUMNS:
  if not _matches_numbers(columns.get(state),WORLD_COLUMNS[state]): return null
 var texture: Texture2D = load(path)
 if texture == null or texture.get_size() != Vector2(384,256): return null
 var frames := SpriteFrames.new()
 frames.remove_animation(&"default")
 for row in DIRECTIONS.size():
  for state in WORLD_COLUMNS:
   var animation := StringName(state+"_"+DIRECTIONS[row])
   frames.add_animation(animation)
   frames.set_animation_speed(animation,{"idle":3.0,"walk":8.0,"run":12.0}[state])
   frames.set_animation_loop(animation,true)
   for column in WORLD_COLUMNS[state]:
    var atlas := AtlasTexture.new()
    atlas.atlas = texture
    atlas.region = Rect2(Vector2(column,row)*SIZE,SIZE)
    frames.add_frame(animation,atlas)
 return frames
