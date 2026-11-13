extends RefCounted
## Shared atlas loader; playback is owned by existing action clocks/FSM.
const DIRECTIONS := ["down", "left", "right", "up"]
const STATES := ["telegraph", "attack", "recovery", "hurt", "stun", "knockdown", "death", "finisher_reaction"]
const CATEGORIES := ["unarmed", "blunt", "sharp", "firearm", "environmental"]
static func append(frames: SpriteFrames, path: String, states: Array, prefix := "") -> void:
	assert(ResourceLoader.exists(path), "P04G authored sheet required: " + path)
	var texture: Texture2D = load(path)
	for row in 4:
		for column in states.size():
			var name := StringName(prefix + states[column] + "_" + DIRECTIONS[row])
			frames.add_animation(name)
			frames.set_animation_loop(name, false)
			frames.set_animation_speed(name, 10)
			for frame in 3:
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.region = Rect2((column*3+frame)*48, row*64, 48,64)
				frames.add_frame(name, atlas)
