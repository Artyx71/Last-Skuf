extends Node2D
## Visual hand sockets only; damage uses the corresponding ground-plane volume.
var player: CharacterBody2D


func _draw() -> void:
	if player.health <= 0 or player.weapon_kind.is_empty() or player.action_timer <= 0:
		return
	var grip: Vector2 = player.weapon_socket()
	var aim: Vector2 = player.action_aim
	var sideways := Vector2(-aim.y, aim.x)
	var data: Dictionary = player.lab.visual_config
	if player.weapon_kind == "knife":
		var handle := float(data.knife.grip)
		var blade := float(data.knife.blade)
		draw_line(grip, grip + aim * handle, Color("896b4d"), 3)
		draw_line(grip + aim * handle - sideways * 2, grip + aim * handle + sideways * 2, Color("c5bca2"), 2)
		draw_line(grip + aim * handle, grip + aim * (handle + blade), Color("e9edf2"), 2)
	elif player.weapon_kind == "pistol":
		var muzzle := grip + aim * float(data.pistol.barrel)
		draw_line(grip - aim * 2, muzzle, Color("738ba3"), 4)
		draw_line(grip + sideways * 4, grip + aim * 3, Color("3b424e"), 3)
		draw_line(muzzle - aim * 4, muzzle, Color("e9edf2"), 2)
		if player.action_elapsed < float(data.pistol.flash_duration):
			draw_line(muzzle + aim * 2, muzzle + aim * 7, Color("ffe7a0"), 3)
