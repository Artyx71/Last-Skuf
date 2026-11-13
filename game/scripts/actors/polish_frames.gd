extends RefCounted
## Shared atlas loader; playback is owned by existing action clocks/FSM.
const DIRECTIONS := ["down", "left", "right", "up"]
const STATES := ["telegraph", "attack", "recovery", "hurt", "stun", "knockdown", "death", "finisher_reaction"]
const CATEGORIES := ["unarmed", "blunt", "sharp", "firearm", "environmental"]
static var socket_atlas: Dictionary = {}

static func clothing_offset(sprite: AnimatedSprite2D) -> Vector2:
	if socket_atlas.is_empty():
		socket_atlas = JSON.parse_string(FileAccess.get_file_as_string("res://assets/art/combat_polish/atlas.json")).get("clothing_sockets",{})
	var texture := sprite.sprite_frames.get_frame_texture(sprite.animation,sprite.frame)
	if texture is AtlasTexture and texture.has_meta("full_atlas"):
		var name: String = texture.get_meta("full_atlas").resource_path.get_file()
		var row := str(int(texture.region.position.y/64))
		var column := str(int(texture.region.position.x/48))
		var point: Array = socket_atlas.get(name,{}).get(row,{}).get(column,[])
		if point.size()==2:
			return sprite.position-Vector2(24,32)+Vector2(point[0],point[1])
	return Vector2(0,-24)

static func append(frames: SpriteFrames, path: String, states: Array, prefix := "") -> void:
	assert(ResourceLoader.exists(path), "P04G authored sheet required: " + path)
	var texture: Texture2D = load(path)
	var reduced: Texture2D = load(path.replace(".png","_reduced.png"))
	for row in 4:
		for column in states.size():
			var name := StringName(prefix + states[column] + "_" + DIRECTIONS[row])
			frames.add_animation(name)
			frames.set_animation_loop(name, false)
			frames.set_animation_speed(name, 10)
			for frame in 3:
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.set_meta("full_atlas",texture)
				atlas.set_meta("reduced_atlas",reduced)
				atlas.region = Rect2((column*3+frame)*48, row*64, 48,64)
				frames.add_frame(name, atlas)


static func apply_gore(sprite: AnimatedSprite2D, reduced: bool) -> void:
	for animation in sprite.sprite_frames.get_animation_names():
		for frame in sprite.sprite_frames.get_frame_count(animation):
			var texture: Texture2D = sprite.sprite_frames.get_frame_texture(animation,frame)
			if texture is AtlasTexture and texture.has_meta("full_atlas"):
				texture.atlas = texture.get_meta("reduced_atlas" if reduced else "full_atlas")

static func connect_options(sprite: AnimatedSprite2D, store: Node) -> void:
	apply_gore(sprite,store.values.reduced_gore)
	var handler := func(key: StringName,value: Variant):
		if key == &"reduced_gore" and is_instance_valid(sprite): apply_gore(sprite,bool(value))
	store.changed.connect(handler)
	sprite.tree_entered.connect(func():
		if is_instance_valid(store):
			if not store.changed.is_connected(handler): store.changed.connect(handler)
			apply_gore(sprite,store.values.reduced_gore))
	sprite.tree_exiting.connect(func():
		if is_instance_valid(store) and store.changed.is_connected(handler): store.changed.disconnect(handler))
