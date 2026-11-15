extends Control
## Presentation only: exact live defense window, no input/damage/timers here.
const TEXT := {
	"ready":"F · ПАРИРОВАНИЕ ГОТОВО", "preparing":"ПОДГОТОВКА К БЛОКУ",
	"guard":"БЛОК СПЕРЕДИ · ОКНО ОТКРЫТО", "counter":"БЛОК! · ОТВЕТНЫЙ УДАР",
	"closed":"ОКНО БЛОКА ЗАКРЫТО", "recovery":"ВОССТАНОВЛЕНИЕ",
	"paused":"ПАУЗА", "dead":"ПОГИБ · R: ПОВТОР", "busy":"ПРИЁМ ЗАНЯТ",
	"unavailable":"ПАРИРОВАНИЕ НЕДОСТУПНО"
}
const COLORS := {
	"ready":Color("99dcd8"), "preparing":Color("ffcc71"), "guard":Color("91f2ac"),
	"counter":Color("9cefff"), "recovery":Color("ffcc71"), "cooldown":Color("c8c5da")
}
var lab: Node2D
var title: Label
var meter: ProgressBar
var displayed_feedback: Dictionary = {}
var fill_style: StyleBoxFlat

func _ready() -> void:
	position = Vector2(350,28)
	size = Vector2(274,31)
	z_index = 20
	process_priority = 100 # After the simulation, before this frame is drawn.
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	title = Label.new()
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	title.add_theme_font_size_override("font_size",11)
	add_child(title)
	title.size = Vector2(274,18)
	meter = ProgressBar.new()
	meter.position = Vector2(0,22)
	meter.max_value = 1.0
	meter.step = 0.0
	meter.show_percentage = false
	meter.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var background := StyleBoxFlat.new()
	background.bg_color = Color("343342")
	fill_style = StyleBoxFlat.new()
	meter.add_theme_stylebox_override("background",background)
	meter.add_theme_stylebox_override("fill",fill_style)
	add_child(meter)
	# Set the rect AFTER disabling percentage/theme minima; the default theme
	# otherwise clamps an early 5px assignment to its 27px text minimum.
	meter.size = Vector2(274,5)

func _process(_delta: float) -> void:
	if not is_instance_valid(lab) or not is_instance_valid(lab.player):
		hide()
		return
	displayed_feedback = lab.player.counter_feedback()
	visible = displayed_feedback.phase != "hidden"
	if not visible: return
	var phase: String = displayed_feedback.phase
	title.text = TEXT.get(phase,"")
	if phase == "cooldown": title.text = "ПОВТОР ЧЕРЕЗ %.1f с" % float(displayed_feedback.cooldown)
	var color: Color = COLORS.get(phase,Color("a7a6bd"))
	title.add_theme_color_override("font_color",color)
	fill_style.bg_color = color
	meter.value = displayed_feedback.progress
