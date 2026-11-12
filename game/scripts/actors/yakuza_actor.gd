extends CharacterBody2D
## Responsive low-speed movement; no random stumbling or unearned combat power.

const SHEET_PATH := "res://assets/art/yakuza/world_sheet.png"
const DIRECTIONS: Array[StringName] = [&"down", &"left", &"right", &"up"]
const FRAME_SIZE := Vector2(48, 64)
const FRAME_PIVOT := Vector2(24, 58)

@export var move_speed := 82.0
var facing: StringName = &"down"
var sprite: AnimatedSprite2D


func _ready() -> void:
	collision_layer = 2
	collision_mask = 1
	var shape := CollisionShape2D.new()
	var rectangle := RectangleShape2D.new()
	rectangle.size = Vector2(16, 12)
	shape.shape = rectangle
	shape.position = Vector2(0, -6)
	add_child(shape)
	assert(ResourceLoader.exists(SHEET_PATH), "Actual P01 character art required")
	var texture: Texture2D = load(SHEET_PATH)
	var frames := SpriteFrames.new()
	frames.remove_animation(&"default")
	for row in DIRECTIONS.size():
		for state in ["idle", "walk"]:
			var animation := StringName(state + "_" + String(DIRECTIONS[row]))
			frames.add_animation(animation)
			frames.set_animation_speed(animation, 3.0 if state == "idle" else 8.0)
			var first := 0 if state == "idle" else 2
			var count := 2 if state == "idle" else 6
			for column in range(first, first + count):
				var atlas := AtlasTexture.new()
				atlas.atlas = texture
				atlas.region = Rect2(Vector2(column, row) * FRAME_SIZE, FRAME_SIZE)
				frames.add_frame(animation, atlas)
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.position = FRAME_SIZE * 0.5 - FRAME_PIVOT
	sprite.texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	add_child(sprite)
	sprite.play(&"idle_down")


func _physics_process(_delta: float) -> void:
	var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	velocity = direction * move_speed
	move_and_slide()
	if direction.length_squared() > 0.0:
		if absf(direction.x) > absf(direction.y):
			facing = &"right" if direction.x > 0.0 else &"left"
		else:
			facing = &"down" if direction.y > 0.0 else &"up"
		var animation := StringName("walk_" + String(facing))
		if sprite.animation != animation:
			sprite.play(animation)
	else:
		var animation := StringName("idle_" + String(facing))
		if sprite.animation != animation:
			sprite.play(animation)
