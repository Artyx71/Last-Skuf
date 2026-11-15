extends RefCounted
## Authored character atlas playback. This loader does not authorize combat actions.
const Catalog = preload("res://scripts/systems/character_catalog.gd")
const DIRECTIONS := ["down", "left", "right", "up"]
const WORLD_COLUMNS := {"idle":[0,1], "walk":[2,3,4,5], "run":[6,7]}
const ACTION_COLUMNS := {"shove":[0,1,2], "interact":[3], "hit":[4], "fall":[5,6], "fire":[7]}
const FINISHER_COLUMNS := {"finish_unarmed":[0,1,6], "finish_blunt":[0,2,6], "finish_sharp":[0,3,6], "finish_firearm":[0,4,6], "finish_environmental":[0,5,6], "special":[0,7,6]}
const SHEET_COLUMNS := {"world":WORLD_COLUMNS, "action":ACTION_COLUMNS, "finisher":FINISHER_COLUMNS}
const TIMKA_PROFILE := "timka_supported_v1"
const TIMKA_SOURCE_COLUMNS := {"world":[0,1,2,3,4,5,6,7], "action":[0,1,2,3,4,5,6], "finisher":[0,1,2,5,6,7]}
const TIMKA_ACTION_COLUMNS := {"shove":[0,1,2], "interact":[3], "hit":[4], "fall":[5,6]}
const TIMKA_FINISHER_COLUMNS := {"finish_unarmed":[0,1,4], "finish_blunt":[0,2,4], "finish_environmental":[0,3,4], "special":[0,5,4]}
const SIZE := Vector2(48,64)
const PIVOT := Vector2(24,58)

static func _layout_spec(actor_id: String, kind: String) -> Dictionary:
 if not SHEET_COLUMNS.has(kind) or actor_id not in ["gabar","olezhka","timka","ryzhik","tega","pasha"]: return {}
 if actor_id == "timka":
  var columns: Array = TIMKA_SOURCE_COLUMNS[kind]
  var maps: Dictionary = {"world":WORLD_COLUMNS,"action":TIMKA_ACTION_COLUMNS,"finisher":TIMKA_FINISHER_COLUMNS}[kind]
  return {"schema":2,"profile":TIMKA_PROFILE,"columns":columns.size(),"source_columns":columns,"mapping":maps,"count":columns.size()*4}
 return {"schema":1,"columns":8,"mapping":SHEET_COLUMNS[kind],"count":32}

static func _valid_sha(value: Variant) -> bool:
 if not value is String or value.length()!=64: return false
 for letter in value:
  if not "0123456789abcdef".contains(letter): return false
 return true

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

static func timka_present_frames() -> SpriteFrames:
 # This context has no finisher/ranged clips. Its backward step explicitly
 # reuses this actor's four walk drawings; it is not a new source-art claim.
 var result := world_frames("timka")
 var action := action_frames("timka")
 if result == null or action == null: return null
 _append_clips(result,action)
 for direction in DIRECTIONS:
  var name := StringName("disengage_"+direction)
  result.add_animation(name)
  result.set_animation_loop(name,false)
  for item in [["shove_",0],["walk_",3],["walk_",2],["walk_",1],["walk_",0],["shove_",2]]:
   result.add_frame(name,result.get_frame_texture(StringName(item[0]+direction),item[1]))
 return result

static func _append_clips(result: SpriteFrames, addition: SpriteFrames) -> void:
 for name in addition.get_animation_names():
  result.add_animation(name)
  result.set_animation_speed(name,addition.get_animation_speed(name))
  result.set_animation_loop(name,addition.get_animation_loop(name))
  for index in addition.get_frame_count(name):
   result.add_frame(name,addition.get_frame_texture(name,index),addition.get_frame_duration(name,index))

static func combat_frames(actor_id: String) -> SpriteFrames:
 # A missing authored sheet prevents construction; there is no Yakuza fallback.
 var result := world_frames(actor_id)
 var action := action_frames(actor_id)
 var finisher := finisher_frames(actor_id)
 if result == null or action == null or finisher == null: return null
 for addition in [action,finisher]: _append_clips(result,addition)
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
 var spec := _layout_spec(actor_id,kind)
 var expected: Dictionary = spec.mapping
 var texture := _sheet_texture(path_value,Vector2(int(spec.columns)*48,256))
 if texture == null: return null
 if spec.schema==2 and not _valid_sheet_pixels(texture.get_image(),parsed): return null
 var socket_path := path.get_base_dir().path_join(kind+".sockets.json")
 var sockets: Dictionary = {}
 if FileAccess.file_exists(socket_path):
  var socket_data: Variant = JSON.parse_string(FileAccess.get_file_as_string(socket_path))
  if not _valid_sockets(socket_data,parsed): return null
  sockets = socket_data
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
    if spec.schema==2:
     atlas.set_meta("layout_profile",TIMKA_PROFILE)
     atlas.set_meta("original_source_column",spec.source_columns[column])
    if not sockets.is_empty():
     var point: Array = sockets.frames[row*int(spec.columns)+column].clothing
     atlas.set_meta("clothing_socket",Vector2(point[0],point[1]))
    frames.add_frame(animation,atlas)
 return frames

static func _valid_sockets(sockets: Variant, layout: Dictionary) -> bool:
 if not sockets is Dictionary: return false
 var actor: Variant = layout.get("actor_id")
 var kind: Variant = layout.get("kind")
 if not actor is String or not kind is String or not _valid_layout(layout,actor,kind): return false
 var spec := _layout_spec(actor,kind)
 if sockets.get("schema")!=spec.schema: return false
 if sockets.get("actor_id")!=layout.get("actor_id") or sockets.get("kind")!=layout.get("kind"): return false
 if sockets.get("sheet_sha256")!=layout.get("sha256"): return false
 if spec.schema==2:
  if sockets.get("layout_profile")!=TIMKA_PROFILE: return false
  if not _matches_numbers([sockets.get("source_cells")],[spec.count]): return false
  if not _matches_numbers(sockets.get("source_column_mapping"),spec.source_columns): return false
 var entries: Variant = sockets.get("frames")
 if not entries is Array or entries.size()!=spec.count: return false
 for index in int(spec.count):
  var entry: Variant = entries[index]
  if not entry is Dictionary or not _matches_numbers([entry.get("index")],[index]): return false
  if spec.schema==2:
   var source: Dictionary = layout.frames[index]
   if entry.get("direction")!=source.direction: return false
   if not _matches_numbers([entry.get("column"),entry.get("source_column")],[source.column,source.source_column]): return false
  var point: Variant = entry.get("clothing")
  if not point is Array or point.size()!=2: return false
  for axis in 2:
   if not (point[axis] is int or point[axis] is float) or point[axis]!=floor(point[axis]): return false
   if point[axis]<0 or point[axis]>=[48,64][axis]: return false
 return true

static func _sheet_texture(path_value: Variant, expected_size := Vector2(384,256)) -> Texture2D:
 if not path_value is String or path_value.is_empty() or not ResourceLoader.exists(path_value): return null
 var resource: Resource = load(path_value)
 if not resource is Texture2D: return null
 var texture := resource as Texture2D
 return texture if texture.get_size()==expected_size else null

static func _valid_sheet_pixels(image: Image, layout: Dictionary) -> bool:
 # Imports can bleed RGB into fully transparent pixels (fix_alpha_border).
 # Compare alpha + visible RGB exactly, canonicalizing only hidden RGB to zero
 # as the source packer does. The adopter still verifies exact raw PNG/RGBA.
 if image==null or not _valid_layout(layout,"timka",String(layout.get("kind",""))): return false
 var spec := _layout_spec("timka",layout.kind)
 if image.get_size()!=Vector2i(int(spec.columns)*48,256): return false
 image.convert(Image.FORMAT_RGBA8)
 for frame in layout.frames:
  var rect: Array = frame.rect
  var data := image.get_region(Rect2i(int(rect[0]),int(rect[1]),48,64)).get_data()
  for offset in range(0,data.size(),4):
   if data[offset+3]==0:
    data[offset]=0
    data[offset+1]=0
    data[offset+2]=0
  var digest := HashingContext.new()
  if digest.start(HashingContext.HASH_SHA256)!=OK or digest.update(data)!=OK: return false
  if digest.finish().hex_encode()!=frame.rgba_sha256: return false
 return true

static func _valid_layout(parsed: Variant, actor_id: String, kind: String) -> bool:
 if not SHEET_COLUMNS.has(kind) or not parsed is Dictionary: return false
 var spec := _layout_spec(actor_id,kind)
 if spec.is_empty(): return false
 if not _matches_numbers([parsed.get("schema")],[spec.schema]) or parsed.get("actor_id") != actor_id or parsed.get("kind") != kind: return false
 if not _matches_numbers(parsed.get("frame_size"),[48,64]) or not _matches_numbers(parsed.get("pivot"),[24,58]) or parsed.get("directions") != DIRECTIONS: return false
 if spec.schema==2:
  if parsed.get("layout_profile")!=TIMKA_PROFILE: return false
  if not _matches_numbers(parsed.get("dimensions"),[int(spec.columns)*48,256]): return false
  if not _matches_numbers([parsed.get("columns_per_direction")],[spec.columns]): return false
  if not _matches_numbers(parsed.get("source_column_mapping"),spec.source_columns): return false
  if not _valid_sha(parsed.get("sha256")) or not _valid_sha(parsed.get("master_sha256")): return false
 elif parsed.has("layout_profile"): return false
 var expected: Dictionary = spec.mapping
 var columns: Variant = parsed.get("animations_source_columns")
 if not columns is Dictionary or columns.size()!=expected.size(): return false
 for state in expected:
  if not _matches_numbers(columns.get(state),expected[state]): return false
 var source_frames: Variant = parsed.get("frames")
 if not source_frames is Array or source_frames.size()!=spec.count or not _matches_numbers([parsed.get("source_cells")],[spec.count]): return false
 for index in int(spec.count):
  var entry: Variant = source_frames[index]
  var row := index/int(spec.columns)
  var column := index%int(spec.columns)
  if not entry is Dictionary or entry.get("direction")!=DIRECTIONS[row]: return false
  if not _matches_numbers([entry.get("column")],[column]): return false
  if not _matches_numbers(entry.get("rect"),[column*48,row*64,48,64]): return false
  if spec.schema==2:
   if not _matches_numbers([entry.get("index"),entry.get("source_column")],[index,spec.source_columns[column]]): return false
   if not _matches_numbers(entry.get("pivot"),[24,58]): return false
   if not _valid_sha(entry.get("rgba_sha256")): return false
 return true
