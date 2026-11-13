extends SceneTree
## Negative QA fixture: contaminate idle Input after one real AI death/reset.
class Injector extends Node:
 var injected := false
 func _physics_process(_delta: float) -> void:
  if injected: return
  var mission := get_tree().current_scene
  if not mission or not mission.get_script(): return
  if mission.get_script().resource_path != "res://scripts/levels/missed_fight.gd": return
  if mission.checkpoint == "service" and int(mission.progress.data.deaths) == 1 and not mission.auto_retry and mission.state == "playing":
   Input.action_press("move_right")
   injected = true

func _initialize() -> void: call_deferred("run")
func run() -> void:
 root.add_child(Injector.new())
 change_scene_to_file("res://scenes/levels/missed_fight.tscn")
