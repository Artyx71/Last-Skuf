extends "res://scripts/core/combat_lab.gd"
## Technical mission-pipeline pilot, not a campaign chapter or finished artwork.
const NavigationHost = preload("res://scripts/ai/room_navigation_host.gd")
const CharacterPlayer = preload("res://scripts/actors/character_player.gd")
const ScenePolicy = preload("res://scripts/systems/character_scene_policy.gd")
var context_key := "yakuza"
var scene_policy := ScenePolicy.new()
var room_navigation: RefCounted
var doors: Dictionary = {}
var stage := "lever"
var completions := 0

func _create_player() -> CharacterBody2D:
	if context_key == "yakuza": return Player.new()
	assert(scene_policy.open(context_key))
	var body := CharacterPlayer.new()
	assert(body.configure(scene_policy.definition().actor_id,scene_policy))
	return body

func _ready() -> void:
	super._ready()
	auto_retry = false
	for child in get_children():
		if child is Label: child.hide()
	_add_label("PRE-P07 / ТЕХНИЧЕСКИЙ ПИЛОТ · НЕ ГЛАВА",Vector2(24,24),12,Color.WHITE)
	_add_label("Enter: рычаг → цель → выход",Vector2(24,42),11,Color.WHITE)
	for entry in [{"id":"north","rect":Rect2(304,112,16,64)},{"id":"south","rect":Rect2(304,248,16,64)}]:
		var body := StaticBody2D.new()
		body.position = entry.rect.position
		body.collision_layer = 1
		var collider := CollisionShape2D.new()
		var shape := RectangleShape2D.new()
		shape.size = entry.rect.size
		collider.shape = shape
		collider.position = shape.size/2
		body.add_child(collider)
		add_child(body)
		doors[entry.id] = {"body":body,"shape":collider,"desired_open":false}
	room_navigation = NavigationHost.new()
	room_navigation.setup(self,Rect2(0,0,640,360))
	queue_redraw()

func reset_encounter() -> void:
	super.reset_encounter()
	stage = "lever"
	completions = 0
	if not doors.is_empty(): request_doors(false,false)

func request_doors(north: bool, south: bool) -> void:
	doors.north.desired_open = north
	doors.south.desired_open = south

func _occupied(door: Dictionary) -> bool:
	var shape: CollisionShape2D = door.shape
	var rect: Rect2 = shape.global_transform*Rect2(-shape.shape.size/2,shape.shape.size)
	for body in [player]+enemies:
		for child in body.get_children():
			if child is CollisionShape2D and not child.disabled:
				var foot: Rect2 = child.global_transform*Rect2(-child.shape.size/2,child.shape.size)
				if rect.grow(0.5).intersects(foot): return true
	return false

func _physics_process(delta: float) -> void:
	for door in doors.values():
		if door.desired_open or not _occupied(door): door.shape.set_deferred("disabled",door.desired_open)
	if room_navigation != null: room_navigation.refresh()
	super._physics_process(delta)
	if state != "playing": return
	if Input.is_action_just_pressed("ui_accept"):
		if stage == "lever" and player.position.distance_to(Vector2(80,280)) <= 28:
			request_doors(false,true)
			stage = "collect"
		elif stage == "collect" and player.position.distance_to(Vector2(544,144)) <= 28:
			request_doors(true,false)
			stage = "return"
		elif stage == "return" and player.position.distance_to(Vector2(80,80)) <= 28:
			stage = "complete"
			completions += 1
	queue_redraw()

func navigation_velocity(body: CharacterBody2D, point: Vector2, speed: float) -> Vector2:
	return room_navigation.velocity_for(body,point,speed)

func _draw() -> void:
	draw_rect(Rect2(0,0,640,360),Color("151a24"))
	for x in range(0,641,16): draw_line(Vector2(x,0),Vector2(x,360),Color("202a35"))
	for y in range(0,361,16): draw_line(Vector2(0,y),Vector2(640,y),Color("202a35"))
	if not config.is_empty():
		for wall in config.walls: draw_rect(Rect2(wall[0],wall[1],wall[2],wall[3]),Color("4c4a62"))
	for entry in [{"at":Vector2(80,280),"label":"РЫЧАГ"},{"at":Vector2(544,144),"label":"ЦЕЛЬ"},{"at":Vector2(80,80),"label":"ВЫХОД"}]:
		draw_circle(entry.at,5,Color("ffcc71"))
		draw_string(ThemeDB.fallback_font,entry.at+Vector2(12,0),entry.label,HORIZONTAL_ALIGNMENT_LEFT,-1,12)
	for door in doors.values():
		if not door.shape.disabled: draw_rect(Rect2(door.body.position,Vector2(16,64)),Color("c53c56"))
