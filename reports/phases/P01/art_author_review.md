# P01 — авторская проверка арта

**DRAFT_REQUIRES_LIKENESS_REVIEW**, не решение фазы. Исполнитель art production; независимый reviewer и человек ещё должны подтвердить качество.

Готовы реальные исходники/пять портретов/32 directional frames, atlas сfps/pivot/bounds/hashes, точные prompts/metadata и воспроизводимая техническая packing. Выполнены четыре встроенных image_gen вызова (present, world, past, targeted past cleanup), фото yakuza_ref01.png локально просмотрено; разрешение владельца на передачу генератору дано явно. Raw фото в source/game не копировались. Generative outputs не содержат обнаруженных мной фотографических фрагментов; сторонние game assets не использовались.

Автор открыл оба master и оба native-sheet preview. Для проверки alpha скомпоновал original masters на сплошной зелёный: RGB gradient фон исчезает, corner alpha0/1. Native production PNG имеет alpha строго0/255 и нулевой RGB transparent pixels; фона/матовой каймы при checkerboard composite не видно. Hurt cheek bruise, cyanphone и restrained rim сохранены deliberate shared31-color palette. Автоматический adaptive вариант был заменён до передачи runtime: он терял эти акценты. Один native pixel является минимальным жёстким элементом; используется только nearest scaling.

Результат структурной проверки: `art_structural_check.json`. Проверены800×160/384×256, transparency, controlled palette,32distinct full-body frames, все5expressions и подошва y58. Это не проверка личности, сходства, художественной анатомии или качества ходьбы.

Preview evidence: `portraits_preview_2x.png` и `world_preview_3x.png`. Фон preview только проверочный; его нет в game PNG. Hair/face/clothes наблюдаемо согласованы с правильным reference и между портретом/спрайтом. Все4направления и смена ног читаются. Up row зеркально отражён при packing для anatomically left-handphone во всех направлениях.

Открытые замечания: variation волос/объёма/высоты между frames, немного сильнееidle2; likeness требует человеческого решения; past/flashback версия создана отдельным portraits_past.png; optionaltalk отсутствует; движение/пиксельные тени нуждаются в оценке на реальном game background. Root выполняет Godot integration, screenshots и runtime tests отдельно. Никаких claims о PASS, runtime test или публичной лицензии здесь нет.


Past evidence: `portraits_past_preview_2x.png` и `art_past_structural_check.json`. Native PNG имеет 800×160, пять выражений, 30 фактически используемых цветов из общей 31-цветной палитры, alpha только 0/255, transparent RGB нулевой. Первый past master имел белёсую кайму; targeted built-in edit исправил её, финальный master v2 и native preview повторно открыты автором. Корневой executor получил финальные пути и SHA256. Present/world PNG при создании past-версии не менялись.
