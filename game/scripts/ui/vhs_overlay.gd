extends Node2D
## Bounded world-only scanline effect. Dialogue/UI render above it, at integer pixels.
var enabled := true
var reduced_motion := false
var phase := 0.0
func _process(delta: float) -> void:
 if not reduced_motion: phase = fmod(phase + delta * 8.0, 4.0)
 queue_redraw()
func _draw() -> void:
 if not enabled: return
 for y in range(62, 202, 4):
  draw_line(Vector2(20, y), Vector2(620, y), Color(0.01, 0.02, 0.05, 0.16))
 if not reduced_motion:
  var y := 100 + int(phase) * 24
  draw_rect(Rect2(20, y, 600, 1), Color(0.20, 0.8, 0.7, 0.09))
