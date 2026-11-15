extends RefCounted
## Align only the visual transform; physics position, collision and clocks stay exact.
static func align(visual: Node2D, body: Node2D, authored_offset: Vector2) -> void:
 var canvas := body.get_global_transform_with_canvas()
 var correction: Vector2 = canvas.affine_inverse()*canvas.origin.round()
 visual.position = authored_offset+correction
