extends SceneTree
## Resource integrity only; does not accept anatomy, movement or gameplay feel.
const Frames = preload("res://scripts/actors/character_frames.gd")
var checks: Array[Dictionary]=[]
func _initialize() -> void:call_deferred("run")
func check(label:String,ok:bool) -> void:
	checks.append({"name":label,"passed":ok})
	if not ok:push_error("FAIL RYZHIK_ROLL_LAYOUT "+label)
func run() -> void:
	var layout:Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/art/characters/ryzhik/roll.json"))
	var source:=Image.load_from_file("res://assets/art/characters/ryzhik/roll_sheet.png")
	check("actual32_metadata",Frames._valid_layout(layout,"ryzhik","roll"))
	check("actual32_RGBA",Frames._valid_sheet_pixels(source,layout))
	check("base_layout_budget_unchanged",Frames.SHEET_COLUMNS.size()==3 and Frames.SHEET_COLUMNS.has("world") and Frames.SHEET_COLUMNS.has("action") and Frames.SHEET_COLUMNS.has("finisher"))
	var clips:=Frames.roll_frames("ryzhik")
	check("actual4direction_8drawings_loaded",clips!=null and clips.get_animation_names().size()==4)
	if clips!=null:
		for direction in Frames.DIRECTIONS:
			var name:=StringName("roll_"+direction);var good:=clips.get_frame_count(name)==8 and not clips.get_animation_loop(name)
			for f in clips.get_frame_count(name):
				var t:=clips.get_frame_texture(name,f)
				good=good and t.get_meta("character_id","")=="ryzhik" and t.get_meta("source_kind","")=="roll" and t.get_meta("source_column",-1)==f and t.has_meta("clothing_socket")
			check("own_bound_clips_"+direction,good)
	for id in ["timka","gabar","olezhka","pasha","tega","unknown"]:
		var bad:Dictionary=layout.duplicate(true);bad.actor_id=id
		check("roll_not_given_to_"+id,not Frames._valid_layout(bad,id,"roll") and Frames.roll_frames(id)==null)
	for field in ["schema","frame_size","pivot","dimensions","source_cells","frames","animations_source_columns","sha256","master_sha256"]:
		var bad:Dictionary=layout.duplicate(true);bad.erase(field)
		check("required_field_"+field,not Frames._valid_layout(bad,"ryzhik","roll"))
	for field in ["frame_size","pivot","dimensions"]:
		var bad:Dictionary=layout.duplicate(true);bad[field][0]=true
		check("no_boolean_numeric_"+field,not Frames._valid_layout(bad,"ryzhik","roll"))
	var bad:Dictionary=layout.duplicate(true);bad.frames.pop_back();check("missing_cell_denied",not Frames._valid_layout(bad,"ryzhik","roll"))
	bad=layout.duplicate(true);bad.frames[3].column=2;check("duplicated_column_denied",not Frames._valid_layout(bad,"ryzhik","roll"))
	bad=layout.duplicate(true);bad.frames[24].direction="down";check("wrong_UP_camera_row_denied",not Frames._valid_layout(bad,"ryzhik","roll"))
	bad=layout.duplicate(true);bad.animations_source_columns.roll=[0,1,2];check("missing_animation_poses_denied",not Frames._valid_layout(bad,"ryzhik","roll"))
	bad=layout.duplicate(true);bad.frames[31].rgba_sha256="0".repeat(64);check("changed_last_frame_digest_denied",not Frames._valid_sheet_pixels(source,bad))
	var changed:=source.duplicate();changed.set_pixel(0,0,Color.MAGENTA);check("opaque_corruption_denied",not Frames._valid_sheet_pixels(changed,layout))
	changed=source.duplicate();changed.set_pixel(0,0,Color(1,0,1,0));check("import_hidden_RGB_only_allowed",Frames._valid_sheet_pixels(changed,layout))
	var failed:=checks.filter(func(x:Dictionary):return not x.passed).size();var out:=OS.get_environment("AYAY_P06_RYZHIK_LAYOUT_OUTPUT")
	if not out.is_empty():
		DirAccess.make_dir_recursive_absolute(out);var f:=FileAccess.open(out.path_join("result.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"scope":"ROLL_RESOURCE_INTEGRITY_ONLY","phase_approval":false,"passed":failed==0,"checks":checks},"  "));f.close()
	print("RESULT RYZHIK_ROLL_LAYOUT passed=%d failed=%d"%[checks.size()-failed,failed]);preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if failed==0 else 1)
