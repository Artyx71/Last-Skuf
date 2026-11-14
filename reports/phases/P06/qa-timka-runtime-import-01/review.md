# Timka actual import — независимый bounded QA

**PASS_COMPONENT: runtime import integrity only.** Исправление CharacterFrames сравнивает alpha и весь видимый RGB точно; только RGB при alpha==0 обнуляется перед SHA. После настоящего свежего импорта в ROOT-копии прошли actual frames2207/2207, structural102/102 и независимые targetedRGBA30/30, без Godot ошибок/утечек. Это не визуальная приёмка, готовность способностей/FIN, FPS, P06 или merge approval.

## Причина и фактическая проверка исправления

Изолированная game-копия создана без .godot. Собственный headless editor import выполнился с чистым cache за4.371с, exit0. Runtime WORLD/ACTION PNG и .import settings скопированы точно из frozen набора; raw PNG не изменялись. Из fresh imported Texture2D.get_image() и actual raw PNG независимо посчитаны различия: WORLD25045 и ACTION21830 пикселей различаются только скрытым RGB при alpha0; alpha differences0 и visible RGB differences0. Это совпало с сохранённым авторским диагнозом и воспроизведено самим QA, без доверия одному отчёту.

Старый CharacterFrames helper взят побайтно из сохранённого QA2 code-freeze и загружен отдельным res://tests/qa_old_character_frames.gd только в ROOT-копии. Старый validator действительно отвергает обе свежие imported textures, но принимает raw source PNG. Новый validator принимает raw и imported. Diff production helper ограничен комментарием и обнулением data[offset..offset+2] только при data[offset+3]==0; размер, schema/profile, mapping и comparison digest не ослаблены. Для schema1 других героев новая canonicalization не включается.

Независимые30 checks по WORLD32/ACTION28/FIN24 проверяют raw under old/new, наличие видимых/прозрачных пикселей, произвольную замену RGB всех полностью прозрачных пикселей, alpha0→1, alpha255→254, удаление видимого пикселя через alpha→0, изменение последнего видимого RGB, а также одновременно hiddenRGB changes + visibleRGB tamper. Разрешена только первая невидимая замена при неизменном alpha. Все alpha/visible tamper случаи отвергнуты. Дополнительно проверены old rejection/new acceptance actual imported WORLD/ACTION и фактическая доступность этих двух листов, при FIN/combat_frames null. FIN здесь — только source helper contract, не ART/runtime adoption.

Новый штатный structural102 test добавил hiddenRGB positive и visibleRGB negative для каждого source kind. Наш independent probe отдельно проверяет alpha и поздний пиксель, поэтому корректность не основана только на зеркальном повторе добавленных автором assertions. Логи содержат actual checks/result, argv/env и binary SHA pinned Godot4.7.2.

## Raw approval и резервные копии

Adopter остаётся exact b1b8d3d72536947715234c99003c047c3bc8d368c97d5fd652b67a5ac7842b8c из QA2. Его строгий exact PNG/wholecell RGBA gate не менялся и в этом review не запускался. Фактические runtime WORLD/ACTION PNG побайтно совпадают с source native, принятым ARTv2 review PNG SHA и source_adoption bindings. Metadata status по-прежнему SOURCE_ACCEPTED_RUNTIME_VALIDATION_PENDING; прежний source-only review не превращён в runtime/phase approval.

Все4 actual legacy backup файла независимо сверены сразу с migration before.json и с настоящими priorQA2 isolated-project legacy bytes, захваченными до переноса, а не только с migration verified.json. WORLD/ACTION old PNG+JSON hashes совпали во всех трёх источниках. Backup и actual adoption повторно не выполнялись. FIN runtime отсутствует. Initial real frames failure runtime-01 с1939 pass/2FAIL сохранён; исправленный результат не переписал историю.

## Дополнительная evidence и ограничения

Actual saved author after-regression logs/results просмотрены: Timka headless70+strict672, Gabar124, Oleg164, isolation25+fresh-process result. Проверены командные log SHA, exit0/error-free logs и saved result passed. Эти регрессии QA заново не запускал и не присваивает себе. Собственные actual запуски — только fresh import, frames2207, structural102 иRGBA30.

Single validator calls в независимом probe заняли примерно7.5ms WORLD и6.6ms ACTION. Это один диагностический замер на текущем headless host, не benchmark, не FPS acceptance, не native/GPU performance и не доказательство отсутствия allocation hitches. Исправление работает при построении/проверке atlas; полноценные gameplay/native/performance gates остаются отдельно. Визуальная анимация, root/floor/grid/input transitions, clothing sockets, context abilities и открытый FIN finding здесь не приняты.

Все4 code keys и9 runtime files до/после соответствуют timka-runtime-import-code-freeze-01.json.421 исходный файл ROOT-copy после fresh import не изменился; добавлены только два QA GDScript внутри ROOT. XDG config/data/cache/state/runtime и saves изолированы, display variables убраны. WORK project Godot не открывался, WORK файлы reviewer не изменял. Source/adopter QA2 decision и все26 artifacts повторно проверены неизменными. Локальный preview/bootstrap/export/filter/smoke workflow и CH01 изменения автора за пределами scope; их acceptance не заявляется.

Публикуемые code/diff/probe/log/result/SHA inventories перечислены в artifacts.json; ROOT-only game cache/raster copies не публикуются. Нерешённых замечаний в ограниченном исправлении import integrity не найдено. Дальнейшие independent runtime ART/GAMEPLAY/QA/Lead и phase/build/CI gates сохраняются.
