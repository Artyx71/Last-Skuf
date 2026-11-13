extends SceneTree
## Raster structure, palette, bounds and articulation. Does not certify artistic quality.
var passed := 0
var failed := 0
func _initialize() -> void: call_deferred("run")
func check(value: bool,title: String) -> void:
	if value: passed+=1
	else:
		failed+=1
		push_error("FAIL: "+title)
func run() -> void:
	var root_path := "res://assets/art/combat_polish/"
	var atlas: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(root_path+"atlas.json"))
	var sheets := {}
	for frame in atlas.frames:
		if not sheets.has(frame.sheet): sheets[frame.sheet] = (load(root_path+frame.sheet) as Texture2D).get_image()
		var image: Image = sheets[frame.sheet]
		var rect := Rect2i(frame.rect[0],frame.rect[1],48,64)
		check(Rect2i(Vector2i.ZERO,image.get_size()).encloses(rect),"atlas frame in sheet "+frame.sheet)
		var cell := image.get_region(rect)
		var bounds := cell.get_used_rect()
		check(bounds.has_area(),"nonempty authored frame "+frame.sheet+frame.state)
		check(bounds.position.x>0 and bounds.position.y>0 and bounds.end.x<48 and bounds.end.y<64,"unclipped authored frame "+frame.sheet+frame.state)
	for file in ["effects.png","yakuza_damage.png","training_bench.png"]:
		sheets[file] = (load(root_path+file) as Texture2D).get_image()
	for name in sheets:
		var image: Image = sheets[name]
		var colors := {};var partial := 0;var dirty_alpha := 0
		for y in image.get_height():
			for x in image.get_width():
				var pixel := image.get_pixel(x,y)
				if pixel.a==0:
					if pixel.r!=0 or pixel.g!=0 or pixel.b!=0: dirty_alpha+=1
				elif pixel.a==1: colors[pixel.to_rgba32()]=true
				else: partial+=1
		check(partial==0 and dirty_alpha==0,"binary clean alpha "+name)
		check(colors.size()<=64,"limited palette "+name)
		print("RASTER ",name," ",image.get_size()," colors=",colors.size())
	check(atlas.frames.size()==528,"528 real actor key poses")
	for row in 4:
		for column in 12:
			check(sheets["effects.png"].get_region(Rect2i(column*48,row*64,48,64)).get_used_rect().has_area(),"effect cell present")
	var portrait: Image = sheets["yakuza_damage.png"]
	check(portrait.get_size()==Vector2i(480,160),"three 160x160 portrait variants")
	check(hash(portrait.get_region(Rect2i(0,0,160,160)).get_data())!=hash(portrait.get_region(Rect2i(160,0,160,160)).get_data()),"real bruised overlay differs")
	print("RESULT passed=%d failed=%d"%[passed,failed])
	preload("res://scripts/core/runtime_shutdown.gd").quit_clean(self,1 if failed else 0)
