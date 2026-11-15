extends Control
## Read-only ammo/refill/cooldown view of the actual Pasha strategy.
var lab: Node2D
var title: Label
var detail: Label
var meter: ProgressBar
var displayed_feedback: Dictionary = {}

func _ready() -> void:
	position=Vector2(380,27)
	size=Vector2(244,54)
	z_index=20
	process_priority=100
	mouse_filter=Control.MOUSE_FILTER_IGNORE
	title=Label.new()
	title.add_theme_font_size_override("font_size",11)
	title.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(title)
	detail=Label.new()
	detail.position=Vector2(0,17)
	detail.add_theme_font_size_override("font_size",10)
	detail.mouse_filter=Control.MOUSE_FILTER_IGNORE
	add_child(detail)
	meter=ProgressBar.new()
	meter.position=Vector2(0,36)
	meter.max_value=1.0
	meter.step=0.0
	meter.show_percentage=false
	meter.mouse_filter=Control.MOUSE_FILTER_IGNORE
	var background:=StyleBoxFlat.new()
	background.bg_color=Color("343342")
	var fill:=StyleBoxFlat.new()
	fill.bg_color=Color("e3b36c")
	meter.add_theme_stylebox_override("background",background)
	meter.add_theme_stylebox_override("fill",fill)
	add_child(meter)
	meter.size=Vector2(244,5)

func _process(_delta: float) -> void:
	if not is_instance_valid(lab) or not is_instance_valid(lab.player):hide();return
	displayed_feedback=lab.player.ranged_feedback()
	visible=displayed_feedback.phase!="hidden"
	if not visible:return
	var state:String=displayed_feedback.phase
	title.text="ПИСТОЛЕТ · %d / %d"%[displayed_feedback.ammo,displayed_feedback.clip]
	detail.text={"ready":"F / ПКМ · ВЫСТРЕЛ НА ХОДУ","firing":"ВЫСТРЕЛ · МОЖНО ДВИГАТЬСЯ",
		"busy":"ПРИЁМ ЗАНЯТ","paused":"ПАУЗА","dead":"ПОГИБ · R: ПОВТОР",
		"unavailable":"СТРЕЛЬБА НЕДОСТУПНА"}.get(state,"")
	if state=="cooldown":detail.text="ПОВТОР ЧЕРЕЗ %.1f с"%float(displayed_feedback.cooldown)
	if state=="empty":detail.text="ПУСТО · ПАТРОН ЧЕРЕЗ %.1f с"%float(displayed_feedback.refill_seconds)
	if displayed_feedback.ammo<displayed_feedback.clip:
		meter.value=displayed_feedback.refill
		if state=="ready":detail.text+=" · +1 ЧЕРЕЗ %.1f с"%float(displayed_feedback.refill_seconds)
	else:meter.value=1.0-float(displayed_feedback.cooldown)/float(displayed_feedback.cooldown_total)
	title.add_theme_color_override("font_color",Color("edb16c") if state=="empty" else Color("d8d6e8"))
