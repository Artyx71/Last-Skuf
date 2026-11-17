extends TextureRect
## Authored expression cells only. New P06 portraits are explicitly static.
const Characters = preload("res://scripts/systems/character_catalog.gd")
var actor_id := ""
var expression := ""

func show_line(line: Dictionary) -> bool:
 var character := Characters.speaker(String(line.get("speaker", "")))
 var emotion := String(line.get("emotion", ""))
 if character.is_empty() or not Characters.valid_line(String(line.speaker), emotion) or not Characters.presentation_ready(character.actor_id):
  texture = null
  return false
 actor_id = character.actor_id
 expression = emotion
 var region := AtlasTexture.new()
 region.atlas = load(character.portrait_file)
 # P01 Yakuza uses the same five expression positions, including its 'surprised' cell.
 var index: int = Characters.EXPRESSIONS.find(emotion)
 region.region = Rect2(index * 160, 0, 160, 160)
 texture = region
 texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
 return true
