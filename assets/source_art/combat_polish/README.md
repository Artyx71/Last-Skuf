# P04G — авторские integer pixel recipes

`render.py` создаёт новые PNG на сетке 48×64. Утверждённые P01–P03 sheets и P04 chapter не перезаписываются. Головы/центральные мотивы одежды — из собственных approved runtime rasters; суставы, кисти, согнутые колени, лежащие части тела, оружие и пятна заданы целочисленными авторскими координатами. Нет random shapes, фото, генератора или расходов. Это raster source recipes и реальные native PNG, а не Aseprite layers.

Восемь состояний × три key poses × четыре направления для каждого patrol/rusher/shooter. Пять категорий × три позы × четыре направления отдельно для Якудзы и каждого противника. Упавшие позы собираются из заново расположенных частей тела; весь спрайт не масштабируется/сдвигается для подмены реакции. Общие фазы collapse/final corpse намеренно переиспользуются; контактные жесты/оружие/раны различаются по категориям. Ограничения: три ключевые позы, общий анатомический язык, самостоятельное ART acceptance ещё требуется.

`effects.png`: четыре временных spray keys на четыре направления, floor/clothing/finisher variants, wall drips и не-кровавый reduced cue. Источник не использует RNG; runtime cosmetic RNG выбирает только готовые варианты. `yakuza_damage.png` добавляет bruised/wounded overlays к исходному neutral portrait, сохраняя лицо; исходник неизменён. Новые герои P06 не создавались.

Запуск: `<root>/.tools/art-venv/bin/python assets/source_art/combat_polish/render.py` (Pillow уже установлен на host; в worktree возможен абсолютный путь к тому же venv). `provenance.json` содержит входные/выходные SHA256. `author_board.png` — реальный авторский inspection board, не engine evidence. Независимое сравнение лица и фактических native кадров выполняет ART reviewer.

`*_reduced.png` — производные neutral palette variants тех же поз: три blood-цвета заменены неброскими серыми scuff-цветами. Это не дополнительные уникальные позы. Runtime меняет только atlas texture, сохраняя animation/frame/anchors и contact clock. Все новые import settings отключают alpha-border RGB dilation; actual imported pixels проходят clean-alpha check.
