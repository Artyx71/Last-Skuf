# P06 — независимый ART preflight: Olezhka v1

**ACCEPTABLE_STATIC_CANDIDATE**, frames0–4. Must-fix likeness/expression findings отсутствуют. Это локальный review раннего source/native кандидата; не PASS P06, не runtime approval и не окончательная frozen-SHA приёмка.

Точный production native SHA256: `6dc278dd2cc6c2956e5878e65a638bf9c7516fa594c7c29a70200fd047c1e29c`. Master: `22fa1de0c663acb13185ff32b1121d29ecf498a5b583e92c01e7b65409b40268`. Сопоставлен собственный приватный `olezhka_ref01.png`, SHA `39023a7f29083adeda60646f404dbfd3f20a1f2c8fdc47e707850f49ffa075e0`; reference/prompt/master hashes в generation metadata совпадают с фактическими файлами.

## Likeness и статичные выражения

Сохраняются короткие коричневые волосы с короткими боками и небольшим forward fringe, сильные прямые брови, молодой чисто выбритый широкий нижний овал лица, полные губы и устойчивый слегка скептический взгляд. Тёмная тренировочная футболка и широкие молодые плечи соответствуют canonical identity и собственному фото. Нет переноса чёрных волос/полного тела Yakuza, очков Gabar или бороды Timka. Волосы в рисунке чуть длиннее/пышнее и челюсть более угловатая, чем на фото; это minor caricature difference, не ошибка идентичности. Не обнаружены выдуманные татуировки, постоянные шрамы/родинки, борода, очки, брендовое слово или читаемый скопированный логотип. Серые линии футболки читаются как абстрактный рисунок/складки, не обязательная реальная марка.

Frames0–4 визуально соответствуют manifest: neutral — закрытый рот/спокойный взгляд; angry — сдвинутые брови и напряжённые губы; surprise — расширенные глаза, поднятые брови и открытый рот; hurt — синяк/припухшее веко и боль без крови; catchphrase — энергичный крик с нахмуренными бровями. Angry и catchphrase различимы по открытому рту и выраженной форме крика. Синяк не переносится на остальные выражения. Возраст не меняется на middle-aged; выраженные складки в angry/catchphrase служат эмоции, не постоянным возрастным чертам.

## Native/packing

Осмотрены master, inspection2x, фактический1440×160 atlas и derived strip пяти кадров в native160×160. Упакованные edges жёсткие, alpha только0/255,38 непрозрачных цветов,9 уникальных рисунков. Нет фотофрагментов, встроенного smooth blur, checkerboard/panels или соседнего портрета в клетке. Мелкая точечная фактура волос/одежды не мешает facial anchors. Все5 читаемы без upscale. Top native bounds базовых выражений17–18px оставляют несколько больше воздуха сверху, чем Gabar/Timka; это ожидаемо для более короткой причёски и более широкой плечевой композиции, не clipped head.

Фактический master1280×1229. Реальные partitions x`[0,437,839,1280]`, y`[0,409,799,1229]`; проверено, что каждый из9 `source_rect` содержит полный alpha-bbox соответствующего рисунка. Один общий NN scale0.3989501312335958 и baseline158, без face reconstruction. Все9 frame hashes и bounds совпали с manifest. Base bounds: neutral/angry `[5,17,155,158]`, surprise `[4,17,155,158]`, hurt/catchphrase `[4,18,155,158]`; разница1px допустима в статичной подаче. Metadata честно указывает5 static expressions, пустое motion mapping и unused indices5–8. Эти extra drawings не получили motion approval; факт уникальности9 клеток не доказывает анимацию.

Дальше нужны native dialogue captures всех5, проверка speaker/filtering/intended screen size, согласованность с world art, actual controls и финальные независимые gates на frozen source. Никаких Godot/controller/Git/source изменений или генерации ревьюер не выполнял. Приватное фото просмотрено только локально; в отчёты не скопировано и не загружено. Записаны только артефакты разрешённого art-preflight каталога.

Проверки и полная SHA256-инвентаризация: `olezhka_metrics_v1.json`. Derived игровые strips: `olezhka_static5_v1_native.png`, `olezhka_static5_v1_2x.png`.
