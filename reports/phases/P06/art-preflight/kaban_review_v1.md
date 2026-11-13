# P06 — независимый ART preflight: Kaban v1

**ACCEPTABLE_STATIC_CANDIDATE**, frames0–4, с оговоркой **LOW_MARGIN_NEUTRAL_ANGRY_SEPARATION** для runtime review. Must-fix source likeness/wardrobe finding нет. Это ранняя проверка реальных source/native изображений и собственного фото, не PASS P06, не runtime approval и не окончательная frozen-SHA приёмка.

Проверенный native SHA `522fdb3196b4e8c62632479b0344a18a69eb69181ec383584155465cf66c933c`. Master `0e58aa75959a51afbebc63ef2f7a333efe9a25fbdc4b1f301fa740dd91cb5f03`. Собственный `kaban_ref01.png`, SHA `eae4ddb26ce1a101d73c8ae279c42914936e2e65e0c0c9882b6f108fbe165487`, сверен локально. Generation reference/prompt/master hashes совпали с файлами.

## Likeness, роль и выражения

Very short cropped hair с receding temples, широкий округлый лоб, небольшие тяжёлые глаза, короткий широкий нос, асимметрично сжатые губы, мягкие широкие щёки/подбородок и толстая шея хорошо соответствуют собственному фото. Рисунок усиливает складки лба и объём нижней части лица в рамках заданной карикатуры. Серый tee и простая серебряная цепочка согласованы между5 выражениями. Нет оружия, suit/mafia costume, incriminating props, татуировок или постоянных шрамов. Портрет показывает обычного сурового отца; сам по себе не утверждает реальную криминальную роль. Сюжетное fiction disclosure и spoiler handling runtime этим не проверены.

Frames0–4: neutral — разочарованный закрытый рот/тяжёлый взгляд; angry — усиленный scolding frown; surprise — поднятые брови, раскрытые глаза и небольшой открытый рот; hurt — фиолетовый односторонний bruise и болезненный взгляд без видимой крови; catchphrase — открытый рот/сведённые брови, stern talking/scolding. Последние3 легко различимы в native160×160.

**Нейтральный0 и angry1 имеют самый небольшой визуальный разрыв среди просмотренных наборов.** Оба уже суровые, рот/головная поза почти одинаковы. Angry отличается более глубоким внутренним brow V и тёмной вертикальной складкой у переносицы; в actual160px эти изменения видны. Это обоснованное усиление канонического disappointed stare, а не два точных дубликата. Source-only оснований требовать новую генерацию сейчас нет, но пару обязательно проверить рядом и при реальном переключении в intended-size dialogue UI. Если UI уменьшает портрет так, что brow difference пропадает, concrete fix — новые целые рисунки neutral/angry с более ясным различием выражений и повторный независимый review. Процедурное изменение лица/бровей не разрешается. Уникальные SHA не заменяют проверку видимого различия.

## Native и provenance

Master1254×1254, actual atlas1440×160, alpha0/255,37 непрозрачных цветов,9 уникальных RGBA рисунков. Проверены master/inspection2x/actualnative; hard square pixels, без фотофрагментов, bilinear blur, checkerboard/panels и соседних рисунков в клетке. Мелкая stipple skin/crown texture читается как пиксельная фактура; постоянных новых facial symbols не найдено.

Реальные partitions x`[0,425,818,1254]`, y`[0,421,830,1254]`; все9 `source_rect` независимо подтверждены как полные alpha-bbox. Общий NN scale0.40860215053763443 и baseline158, без face reconstruction. Все9 frame hashes/bounds совпали с manifest. Базовые bounds `[4,6,155,158]`, surprise right156; нет непреднамеренного clipping. Metadata честно содержит5 static expressions, пустой motion mapping, unused5–8. Extra4 не одобрены как анимация.

Остаются actual dialogue captures всех5 и особенно0↔1, speaker/filtering/intended size, сохранение supporting/nonplayable роли, final frozen-source gates. Godot/controller/Git/source изменения и генерация ревьюером не выполнялись. Фото только локально просмотрено, не копировалось/не загружалось; записаны только разрешённые отчёты и derived игровые strips.

Полная SHA256-инвентаризация/проверки: `kaban_metrics_v1.json`; strips `kaban_static5_v1_native.png`, `kaban_static5_v1_2x.png`.
