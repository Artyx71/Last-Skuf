extends "res://scripts/core/combat_lab.gd"
## Separate registered sandbox. Unknown/unready actors never substitute Yakuza.
const ScenePolicy = preload("res://scripts/systems/character_scene_policy.gd")
const CharacterPlayer = preload("res://scripts/actors/character_player.gd")
const CharacterCatalog = preload("res://scripts/systems/character_catalog.gd")
var scene_policy := ScenePolicy.new()
var fixture_keys := ["gabar_training","olezhka_training","timka_present","timka_prime","ryzhik_training","tega_training","pasha_training"]
var selection_message := ""

func _ready() -> void:
	var view_guard := preload("res://scripts/systems/campaign_view_guard.gd").new()
	add_child(view_guard)
	if not view_guard.acquire(get_node_or_null("/root/DialogueDirector")):
		state = "blocked"
		set_physics_process(false)
		_add_label("Другой просмотр уже открыт. Esc: меню",Vector2(24,24),14,Color("ffcc71"))
		return
	y_sort_enabled = true # Whole actor bodies sort by floor root, not head height.
	var opened := scene_policy.open("gabar_training")
	assert(opened)
	super._ready()
	for child in get_children():
		if child is Label and child.text.begins_with("P02 /"):
			child.text = "P06 / ПОЛИГОН ПЕРСОНАЖЕЙ · НЕ СЮЖЕТНАЯ ГЛАВА"
	_update_hud()

func _create_player() -> CharacterBody2D:
	var result := CharacterPlayer.new()
	var configured := result.configure(scene_policy.definition().actor_id,scene_policy)
	assert(configured,"Complete authored character required")
	return result

func select_fixture(key: String) -> bool:
	if key not in fixture_keys: return false
	var definition: Dictionary = ScenePolicy.definitions().get(key,{})
	if definition.is_empty(): return false
	# Prepare exactly the complete production body before touching the fixture.
	var candidate := CharacterPlayer.new()
	if not candidate.prepare_art(definition.actor_id):
		candidate.free()
		selection_message = CharacterCatalog.actor(definition.actor_id).display_name+": боевой набор ещё не готов"
		_update_hud()
		return false
	if options_panel.visible: _set_options_visible(false)
	combat.reset() # Revoke old reservations/projectiles BEFORE opening new authority.
	scene_policy.invalidate()
	player.cancel_action()
	remove_child(player)
	player.queue_free()
	var opened := scene_policy.open(key)
	if not opened or not candidate.bind_policy(scene_policy):
		candidate.free()
		state = "blocked"
		push_error("Registered scene could not bind prepared character")
		return false
	player = candidate
	player.lab = self
	add_child(player)
	selection_message = ""
	reset_encounter()
	return true

func reset_encounter() -> void:
	super.reset_encounter()
	gallery_mode = true
	_update_hud()
	last_reset_snapshot = snapshot()

func set_kit(_value: String) -> void:
	# F2 never grants the legacy training knife/ranged kit to another identity.
	player.kit = "escape"
	_update_hud()

func select_equipment(index: int) -> bool:
	var categories := ["unarmed","blunt","sharp","firearm","environmental"]
	if index not in range(5) or not combat.finisher_for(player).is_empty(): return false
	if categories[index] not in scene_policy.definition().get("equipment_categories",[]): return false
	equipment_index = index
	player.finisher_category = categories[index]
	player.finisher_weapon = "unarmed" if index == 4 else categories[index]
	_update_hud()
	return true

func _cycle_equipment() -> void:
	for offset in range(1,6):
		if select_equipment((equipment_index+offset)%5): break

func _update_hud() -> void:
	if not kit_label or not player: return
	var actor: Dictionary = CharacterCatalog.actor(player.actor_id)
	kit_label.text = actor.display_name+" / "+String(scene_policy.definition().get("context",""))+" · "+selection_message
	hint_label.text = "WASD/Shift · Space: толчок · F: приём · V: добивание · Tab: инструмент · O: эффекты"
	status_label.text = "1–7: герой/контекст · R: повтор · Esc: меню · очки %d · приём %.1fс" % [score,player.ability_cooldown]
	if equipment_label:
		equipment_label.text = "Инструмент: "+["Кулаки","Труба","Нож","Пистолет","Верстак"][equipment_index]+" · новый боевой набор: Габар; остальные в работе"
	if damage_portrait:
		damage_portrait.texture = load(actor.portrait_file)
		damage_portrait.region_rect = Rect2(480,0,160,160)
		damage_portrait.visible = player.hits_received > 0

func _unhandled_input(event: InputEvent) -> void:
	if state == "blocked":
		if event.is_action_pressed("ui_cancel"):
			get_viewport().set_input_as_handled()
			get_tree().change_scene_to_file("res://scenes/bootstrap/bootstrap.tscn")
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode >= KEY_1 and event.keycode <= KEY_7:
		select_fixture(fixture_keys[event.keycode-KEY_1])
		get_viewport().set_input_as_handled()
		return
	if event.is_action_pressed("ui_cancel"): get_viewport().set_input_as_handled()
	super._unhandled_input(event)
