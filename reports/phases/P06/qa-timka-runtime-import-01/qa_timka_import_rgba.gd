extends SceneTree
const Frames = preload("res://scripts/actors/character_frames.gd")
const OldFrames = preload("res://tests/qa_old_character_frames.gd")
var checks: Array[Dictionary] = []
var imports: Dictionary = {}
func _initialize() -> void: call_deferred("run")
func check(label: String, passed: bool) -> void:
	checks.append({"name":label,"passed":passed})
	if not passed: push_error("FAIL QA_TIMKA_IMPORT "+label)
func clone_data(image: Image, data: PackedByteArray) -> Image:
	return Image.create_from_data(image.get_width(),image.get_height(),false,Image.FORMAT_RGBA8,data)
func run() -> void:
	var source := ProjectSettings.globalize_path("res://").path_join("../assets/source_art/characters/timka").simplify_path()
	for kind in ["world","action","finisher"]:
		var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(source.path_join(kind+"_manifest_supported_v1.json")))
		var raw := Image.load_from_file(source.path_join(kind+"_native_supported_v1.png"))
		raw.convert(Image.FORMAT_RGBA8)
		check(kind+":raw_source_exact_under_old_and_new",OldFrames._valid_sheet_pixels(raw,layout) and Frames._valid_sheet_pixels(raw,layout))
		var data := raw.get_data()
		var visible := -1
		var last_visible := -1
		var hidden := -1
		for offset in range(0,data.size(),4):
			if data[offset+3]>0:
				if visible<0: visible=offset
				last_visible=offset
			elif hidden<0: hidden=offset
		check(kind+":actual_visible_and_hidden_pixels_exist",visible>=0 and hidden>=0)
		var all_hidden := data.duplicate()
		var hidden_count := 0
		for offset in range(0,all_hidden.size(),4):
			if all_hidden[offset+3]==0:
				all_hidden[offset]=193
				all_hidden[offset+1]=71
				all_hidden[offset+2]=251
				hidden_count+=1
		check(kind+":all_hidden_RGB_changes_allowed",hidden_count>0 and Frames._valid_sheet_pixels(clone_data(raw,all_hidden),layout))
		var alpha_one := data.duplicate();alpha_one[hidden+3]=1
		check(kind+":transparent_alpha0_to1_rejected",not Frames._valid_sheet_pixels(clone_data(raw,alpha_one),layout))
		var opaque_alpha := data.duplicate();opaque_alpha[visible+3]=254
		check(kind+":opaque_alpha255_to254_rejected",not Frames._valid_sheet_pixels(clone_data(raw,opaque_alpha),layout))
		var erase := data.duplicate();erase[visible+3]=0
		check(kind+":erase_visible_alpha_to0_rejected",not Frames._valid_sheet_pixels(clone_data(raw,erase),layout))
		var last_rgb := data.duplicate();last_rgb[last_visible]=(int(last_rgb[last_visible])+1)%256
		check(kind+":last_visible_pixel_RGB_tamper_rejected",not Frames._valid_sheet_pixels(clone_data(raw,last_rgb),layout))
		var mixed := all_hidden.duplicate();mixed[visible]=(int(mixed[visible])+1)%256
		check(kind+":hidden_RGB_permission_does_not_mask_visible_tamper",not Frames._valid_sheet_pixels(clone_data(raw,mixed),layout))
		if kind!="finisher":
			var texture: Texture2D = load("res://assets/art/characters/timka/"+kind+"_sheet.png")
			var imported := texture.get_image()
			imported.convert(Image.FORMAT_RGBA8)
			var actual := imported.get_data()
			var alpha_differences := 0
			var visible_differences := 0
			var hidden_differences := 0
			for offset in range(0,data.size(),4):
				if data[offset+3]!=actual[offset+3]:alpha_differences+=1
				elif data[offset]!=actual[offset] or data[offset+1]!=actual[offset+1] or data[offset+2]!=actual[offset+2]:
					if data[offset+3]==0:hidden_differences+=1
					else:visible_differences+=1
			var old_rejected := not OldFrames._valid_sheet_pixels(imported,layout)
			var start := Time.get_ticks_usec()
			var new_accepted := Frames._valid_sheet_pixels(imported,layout)
			var microseconds := Time.get_ticks_usec()-start
			imports[kind]={"visible_RGB_mismatches":visible_differences,"alpha_mismatches":alpha_differences,"hidden_RGB_mismatches":hidden_differences,"old_validator_rejected":old_rejected,"new_validator_accepted":new_accepted,"single_validation_usec_diagnostic_only":microseconds}
			check(kind+":fresh_import_only_hidden_RGB_changed",alpha_differences==0 and visible_differences==0 and hidden_differences>0)
			check(kind+":actual_old_rejection_and_new_acceptance",old_rejected and new_accepted)
	check("actual_runtime_world_and_action_load",Frames.world_frames("timka")!=null and Frames.action_frames("timka")!=null)
	check("FIN_and_complete_combat_still_unavailable",Frames.finisher_frames("timka")==null and Frames.combat_frames("timka")==null)
	var passed := checks.all(func(item: Dictionary):return item.passed)
	var output := OS.get_environment("AYAY_QA_RGBA_OUTPUT")
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"schema":1,"scope":"HIDDEN_RGB_IMPORT_AND_ALPHA_VISIBLE_INTEGRITY_ONLY","passed":passed,"checks":checks,"actual_fresh_imports":imports,"phase_approval":false},"  "))
	file.close()
	print("RESULT QA_TIMKA_IMPORT passed=%d failed=%d" % [checks.filter(func(item: Dictionary):return item.passed).size(),checks.filter(func(item: Dictionary):return not item.passed).size()])
	print(JSON.stringify(imports))
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0 if passed else 1)
