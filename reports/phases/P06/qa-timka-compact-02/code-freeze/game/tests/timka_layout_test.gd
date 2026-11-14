extends SceneTree
## Structural/pixel integrity only, not garment placement, likeness or combat QA.
const Frames = preload("res://scripts/actors/character_frames.gd")
var checks: Array[Dictionary] = []

func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL TIMKA_SUPPORTED_LAYOUT "+label)

func sockets_for(layout: Dictionary) -> Dictionary:
	var entries: Array = []
	for frame in layout.frames:
		# TEST ONLY numeric anchors; not authored clothing sockets or art evidence.
		entries.append({"index":frame.index,"direction":frame.direction,"column":frame.column,
			"source_column":frame.source_column,"clothing":[24,36]})
	return {"schema":2,"actor_id":"timka","kind":layout.kind,"layout_profile":Frames.TIMKA_PROFILE,
		"source_cells":layout.source_cells,"source_column_mapping":layout.source_column_mapping.duplicate(),
		"sheet_sha256":layout.sha256,"frames":entries}

func run() -> void:
	var source := ProjectSettings.globalize_path("res://").path_join("../assets/source_art/characters/timka").simplify_path()
	for kind in ["world","action","finisher"]:
		var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source.path_join(kind+"_manifest_supported_v1.json")))
		var image := Image.load_from_file(source.path_join(kind+"_native_supported_v1.png"))
		var count: int = {"world":32,"action":28,"finisher":24}[kind]
		check(kind+":all_required_metadata",Frames._valid_layout(layout,"timka",kind) and layout.source_cells==count)
		check(kind+":all_required_RGBA",Frames._valid_sheet_pixels(image,layout))
		var bad: Dictionary = layout.duplicate(true)
		bad.schema=1
		check(kind+":no_legacy_fallback",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.layout_profile="unknown"
		check(kind+":unknown_profile_denied",not Frames._valid_layout(bad,"timka",kind))
		for actor in ["unknown","gabar","olezhka","pasha"]:
			bad=layout.duplicate(true);bad.actor_id=actor
			check(kind+":compact_profile_not_given_to:"+actor,not Frames._valid_layout(bad,actor,kind))
		for field in ["dimensions","frame_size","pivot","source_column_mapping"]:
			bad=layout.duplicate(true);bad[field][0]=false
			check(kind+":boolean_not_numeric:"+field,not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.source_cells=count+4
		check(kind+":wrong_budget_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames.pop_back()
		check(kind+":missing_cell_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames[1].index=0
		check(kind+":duplicate_index_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames[0].index=false
		check(kind+":boolean_index_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames[0].source_column=7
		check(kind+":wrong_original_column_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames[0].rect[2]=47.5
		check(kind+":fractional_bounds_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.sha256="not a PNG digest"
		check(kind+":invalid_digest_denied",not Frames._valid_layout(bad,"timka",kind))
		bad=layout.duplicate(true);bad.frames[0].rgba_sha256="0".repeat(64)
		check(kind+":wrong_RGBA_denied",not Frames._valid_sheet_pixels(image,bad))
		var modified := Image.create_from_data(image.get_width(),image.get_height(),false,Image.FORMAT_RGBA8,image.get_data())
		modified.set_pixel(0,0,Color.MAGENTA)
		check(kind+":changed_pixel_denied",not Frames._valid_sheet_pixels(modified,layout))
		check(kind+":wrong_image_dimensions_denied",not Frames._valid_sheet_pixels(Image.create(48,64,false,Image.FORMAT_RGBA8),layout))
		if kind!="world":
			bad=layout.duplicate(true);bad.animations_source_columns.fire=[7]
			check(kind+":unsupported_fire_clip_denied",not Frames._valid_layout(bad,"timka",kind))
		var sockets := sockets_for(layout)
		check(kind+":exact_socket_count_mapping",Frames._valid_sockets(sockets,layout))
		for field in ["schema","layout_profile","sheet_sha256","source_cells"]:
			var broken: Dictionary = sockets.duplicate(true)
			broken[field]=1 if field=="schema" else (count+4 if field=="source_cells" else "wrong")
			check(kind+":old_or_wrong_socket_binding:"+field,not Frames._valid_sockets(broken,layout))
		var broken: Dictionary = sockets.duplicate(true)
		broken.frames.pop_back()
		check(kind+":missing_socket_denied",not Frames._valid_sockets(broken,layout))
		broken=sockets.duplicate(true);broken.frames[count-1].source_column=0
		check(kind+":last_socket_row_stride_denied",not Frames._valid_sockets(broken,layout))
		broken=sockets.duplicate(true);broken.frames[0].clothing=[24,true]
		check(kind+":boolean_socket_denied",not Frames._valid_sockets(broken,layout))
		broken=sockets.duplicate(true);broken.frames[0].clothing=[24,64]
		check(kind+":out_of_cell_socket_denied",not Frames._valid_sockets(broken,layout))
	check("no_FIN_adoption_or_complete_combat_claim",not FileAccess.file_exists("res://assets/art/characters/timka/finisher.json") and Frames.combat_frames("timka")==null)
	var passed := checks.all(func(item: Dictionary):return item.passed)
	var output := OS.get_environment("AYAY_TIMKA_LAYOUT_OUTPUT")
	if not output.is_empty():
		DirAccess.make_dir_recursive_absolute(output)
		var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
		file.store_string(JSON.stringify({"schema":1,"scope":"TIMKA_LAYOUT_PIXEL_AND_SOCKET_CONTRACT_ONLY","passed":passed,"phase_approval":false,"checks":checks},"  "))
		file.close()
	print("RESULT TIMKA_SUPPORTED_LAYOUT passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
