extends Node2D
## A render plane only. The existing impact owner retains pools, caps, TTL and RNG.
var impact: Node2D

func _process(_delta: float) -> void:
	queue_redraw()

func _draw() -> void:
	if not is_instance_valid(impact) or not impact.texture or impact.reduced(): return
	if impact.options and not impact.options.values.get("decals",true): return
	for decal in impact.decals:
		var surface := ""
		match int(decal.column):
			4,5: surface="floor"
			8,9: surface="finisher"
			10: surface="wall"
		if surface.is_empty(): continue
		var pivot: Vector2 = impact.effect_pivots[surface]
		draw_texture_rect_region(impact.texture,Rect2(decal.at-pivot,Vector2(48,64)),
			Rect2(decal.column*48,decal.row*64,48,64))
