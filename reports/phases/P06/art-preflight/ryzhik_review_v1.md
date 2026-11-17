# P06 — независимый ART preflight: Ryzhik v1

**ACCEPTABLE_STATIC_CANDIDATE**, только frames0–4. Must-fix likeness/expression/gore findings отсутствуют. Это review реальных master/native изображений и собственного локального фото, не вывод из имени файла; не PASS P06, не runtime approval и не frozen-SHA final gate.

Проверенный native `37f2aaa4bb2654b6290770b7a1e66dafc9f0d17c3c65319c65ed2e98bcde5320`. Master `42115ed2c2aa169bf989b13e3bbcb3568af9763363a497fe18c5da52f9f319c1`. Собственный `ryzhik_ref01.png`, SHA `47ee7fbcba70b7a6c01b7b18b09ce564365c030b9e57a11507047e73ed5aab95`, просмотрен локально. Generation reference/prompt/master hashes совпали с фактическими файлами.

## Что видно на изображениях

Узнаваемость держится на тёмных сильно зачёсанных набок волосах с длинной прядью над лбом, более коротком боку, вытянутом стройном лице, прямом заметном носе, тёмных бровях и короткой щетине вдоль челюсти/подбородка. Направление головы/взгляда соответствует доступному фото. Это не рыжеволосый персонаж по прозвищу. Волосы имеют преувеличенный spiky объём и тёплые plum highlights, но остаются почти чёрной массой, а не ginger. Челюсть стилизованно угловатее фото; при заданном гротеске не требует новой генерации. Фото низкого разрешения и с сильным цветным освещением; точный оттенок радужки/кожи не выдаётся за установленный факт.

Свободная тёмная crewneck одежда/плечи передают baggy silhouette; в source есть приглушённый teal, в native общий palette даёт тёмный charcoal/plum. Это согласовано между базовыми5 и не нарушает wardrobe anchor. Не добавлены читаемые tattoo patterns, надписи, очки, постоянные шрамы/родинки или чужие facial features. Отсутствующие подтверждённые tattoo details не выдумываются.

Frames0–4: neutral — закрытый рот и беспокойный боковой взгляд; angry — резкие сдвинутые брови/сжатый рот; surprise — расширенные глаза и открытый рот; hurt — отёкший/прищуренный глаз с фиолетовым синяком, напряжённые губы и видимые зубы; catchphrase — озорная асимметричная улыбка с наклоном головы. Все5 различимы в native160×160. У catchphrase намеренно меняется наклон головы/плеч, что допустимо как отдельная статичная эмоция и не доказывает стабильный motion loop.

Hurt не содержит видимой капли/дорожки/брызг крови в master или native. Тёплая коричнево-розовая линия нижней губы читается как губа/тень у напряжённого рта, а не как blood trail. Фиолетовое пятно у глаза читается как bruise. Поэтому заявка prompt «bruised no blood» не требует конкретной коррекции по этому изображению. Разбитый зуб как постоянный gag не выдуман; он не является обязательным состоянием каждого портрета.

## Native и упаковка

Осмотрены master1254×1254, actual atlas1440×160, inspection2x и native strip. Native alpha строго0/255,38 непрозрачных цветов,9 уникальных RGBA-клеток. Hard square edges, нет фотофрагментов, bilinear blur, checkerboard/panels или загрязнения соседним портретом. Реальные partitions x`[0,426,817,1254]`, y`[0,422,841,1254]`; каждый из9 `source_rect` независимо подтверждён как полный alpha-bbox своего рисунка. Общий NN scale0.38578680203045684, baseline158; никаких внутренних face edits. Все9 frame hashes/bounds совпали с manifest.

Base bounds0–2 `[8,7,152,158]`,3–4 `[8,6,152,158]`; в целой голове/плечах нет непреднамеренного clipping. Metadata верно перечисляет5 static expressions, пустой `shared_animation_references`, unused indices5–8. Эти4 extra рисунка учитываются как source, а не одобренная анимация.

Остаются runtime dialogue5expression captures, speaker/filtering/intended-screen-size, world/portrait consistency, actual controls и final independent gates на frozen source. Никакие Godot/controller/Git/source изменения или generation ревьюер не выполнял. Приватное фото не копировалось в отчёт/артефакты и не загружалось. Записаны только отчёты и игровые derived strips разрешённого art-preflight каталога.

Полная SHA256-инвентаризация/проверки: `ryzhik_metrics_v1.json`; игровые strips: `ryzhik_static5_v1_native.png`, `ryzhik_static5_v1_2x.png`.
