extends SceneTree
func _initialize() -> void: call_deferred("run")
func run() -> void:
 var result: Dictionary={}
 for kind in ["world","action"]:
  var path: String="res://assets/art/characters/timka/"+kind+"_sheet.png"
  var raw:=Image.load_from_file(ProjectSettings.globalize_path(path))
  var texture: Texture2D=load(path)
  var imported:=texture.get_image()
  raw.convert(Image.FORMAT_RGBA8);imported.convert(Image.FORMAT_RGBA8)
  var opaque:=0;var transparent:=0;var alpha:=0
  for y in raw.get_height():
   for x in raw.get_width():
    var a:=raw.get_pixel(x,y);var b:=imported.get_pixel(x,y)
    if a.a!=b.a: alpha+=1
    elif a.a==0 and a!=b: transparent+=1
    elif a!=b: opaque+=1
  var layout: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path.get_base_dir().path_join(kind+".json")))
  result[kind]={"opaque_pixel_mismatches":opaque,"transparent_RGB_mismatches":transparent,"alpha_mismatches":alpha,"dimensions":str(imported.get_size()),"layout_valid":preload("res://scripts/actors/character_frames.gd")._valid_layout(layout,"timka",kind),"raw_pixels_valid":preload("res://scripts/actors/character_frames.gd")._valid_sheet_pixels(raw,layout),"imported_pixels_valid":preload("res://scripts/actors/character_frames.gd")._valid_sheet_pixels(imported,layout)}
 print(JSON.stringify(result))
 preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,0)
