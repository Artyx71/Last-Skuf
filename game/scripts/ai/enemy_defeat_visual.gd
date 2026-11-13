extends Node2D
## Explicit transient defeat mark; stands in for neither a corpse nor a fall animation.
var actor: CharacterBody2D


func _draw() -> void:
	if actor.health > 0:
		return
	var duration := float(actor.lab.visual_config.enemy_defeat.cue_seconds)
	if actor.defeat_elapsed >= duration:
		return
	var center := Vector2(0, -25)
	var color := Color("ffddad")
	color.a = 1.0 - actor.defeat_elapsed / duration
	draw_arc(center, 9 + actor.defeat_elapsed * 11, 0, TAU, 16, color, 1.5)
	draw_line(center + Vector2(-5, -5), center + Vector2(5, 5), color, 2)
	draw_line(center + Vector2(5, -5), center + Vector2(-5, 5), color, 2)
