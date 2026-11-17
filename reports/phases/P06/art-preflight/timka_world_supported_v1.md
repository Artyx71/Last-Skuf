# Независимое schema2 SOURCE ART review — Timka WORLD32

**ACCEPTABLE_SUPPORTED_LAYOUT_SOURCE_CANDIDATE.** Принят только исходный WORLD32 компонент профиля`timka_supported_v1`. Все32 обязательных поз заново осмотрены; это не runtime, не две реализованные способности, не FIN24 и не P06/mergePASS.

Reviewer `/root/art_timka_recovery`, `independent_of_author=true`: отдельный независимый контекст, не автор assets/compactor/loader/tests. WORK только прочитан; собственные записи только ROOT под `timka_world_supported_v1*`. Godot/Git/controller/runner/генераторы/сеть не запускались. Никакие WORK/game/source файлы не менялись. Сырые фото не читались/не копировались/не передавались; ownпортрет используется для artworkcontinuity, не новой humanlikenessприёмки.

## Утверждённый контракт и точные bytes

Прочитаны immutable ownerdecision`automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json`, обе сохранённые proposals и текущая SDD. Decision APPROVED содержит32+28+24=84 и явное отсутствие fire/sharp/firearm для Тимки, но phase/merge/implementationcomplete=false. SHA обоих proposals совпадают с immutabledecision. Старые proposed/FAIL тексты не переписаны; исключение84 само по себе не принимает ни один компонент.

Schema2/layout_profile`timka_supported_v1`, kind`world`, source_cells=32, source_column_mapping=[0, 1, 2, 3, 4, 5, 6, 7], native[384, 256],48×64/pivot24,58/4directions проверены строго. PNG SHA `8e505380e88fb538988310a364c6b16a135cb69b94d136fe00307c8a49a99cea`; manifest SHA `fed2f79ac370ce44eefd873cfa2af3452a067d805a70da61976de2095d91a72e`; master SHA `79ab1a0ebd2e06e4793d83c8ed1d2f336f502d37228f3df1e8fb590ff8c114c0`. Master остаётся исходным32клеточным архивом; фактический бюджет этого листа —32, без фиктивных reservedcells.

Независимо проверена selection/compaction каждая целая RGBAячейка и её mapping/index/direction/rect/pivot against originalnative+manifest. Все32 совпадают байт-в-байт; frame metadata сохраняет правильные source_rect/source_column/bounds/DY. Заново восстановлен каждый выбранный192×256source→48×64native NN/палитра/alpha128/зафиксированный rowDY; полныеRGBA совпали с кандидатами без opaquealignmentloss. Нет anatomyedit/painting/зеркала/перестановки частей тела в компактизации. WORLD дополнительно проверен как byte-exactencoded PNG, не только decodeRGBA.

Native35opaque colors,alpha0/255, прозрачныеRGBzero, unique32; периметр каждой nativeячейки прозрачный. Цифры и SHA подтверждают целостность, не заменяют визуальную приёмку.

## Свежая визуальная оценка

Проверены все32native на светлом/тёмном фоне, ownпортрет и12ordered idle0/1,walk2/3/4/5,run6/7 source-последовательностей. Видно самостоятельное противоположное ведение ног на обеих сторонах с непрерывными hip→thigh→knee→shoe цепями и противоположными руками; DOWN/UP также чередуются. Кисти/рукава, hooddown, crown/борода/лицо, charcoalpants/greytrainers сохраняют собственного Тимку. RIGHT7 имеет более сильную forwardrun проекцию; это допустимая source-поза с обязательной nativejoin проверкой. Старые исправленные LEFT7/RIGHT4/RIGHT7 осмотрены как часть нового полного набора, не приняты только по hash/названию.

Source-only strips/wholecellcomposites — диагностика исходных поз, не actualGodotplayback/cadence/physics/contact/footlocking. Новое качество звука не заявлено. Положительное решение не наследуется автоматически от прежнего schema1 или nativepreview.

## Поля и прежний запрос генерации

Сохранённый `world_v1_prompt.txt` просит source-поля>=16px. Фактический v4c/master имеет9отклонений: DOWN2/4=8, DOWN6/7=6, RIGHT6=12, UP2/4=14, UP6=13, UP7=10px. Это не скрыто и **>=16дляWORLD не заявляется**. Во всех исходных клетках alpha>=128 support строго внутри границ; native оставляет минимум3прозрачных пикселя, непрозрачных пикселей на периметре/потери от alignment нет.

При классификации просмотрены действующие ART_BIBLE/SDD/ownerdecision и прежнее явное SOURCE/nativecomponent решение. Обязательного численного source16 gate для этого существующего WORLD в них не задано; numeric16 здесь — сохранённый запрос генерации, отличающийся от измеренного результата. Обязательные сохранность целой фигуры/фиксированная сетка/alpha/bounds/согласованность проверены заново. Поэтому отклонение записано как NON_BLOCKING_OBSERVATION; оно не оправдывается отменой hardgate через owner84. Явный текущий контракт сохраняет WORLDPNG byte-exact. Ни историческое source-решение, ни историческая nativeзапись не заменяют свежий осмотр и не дают текущийruntimePASS.

## Решение и последующие gates

`schema=2`, `layout_profile=timka_supported_v1`, `source_cells=32`, `reviewed_cell_indices=0..31`, `all_required_cells_freshly_reviewed=true`, `source_only_acceptance=true`, `must_fix=[]`. Legacyуниверсальный флаг32не используется. `runtime_approval=false`, `full_phase_approval=false`, `phase_approval=false`.

Прочитан финальный strict`adopt_timka_supported.py`, включая reviewer:string/independent_of_author и обязательныеoriginalnative+manifest+master/owner/script hashes. Его SHA связан с inventory. Сам adopter/compactor не исполнялись, миграция gameфайлов не делалась. Inventory включает только source/profile/reference/instruction/provenance inputs; изменяемые`character_frames.gd`/loader/tests не frozen. Текущая runtimeготовность из приёмки не выводится.

FIN24 не просматривался/не принят: прежний environmental finding остаётся отдельным обязательным блокером. Реальный disengage (guard→reversewalk→recover), collision/clock/cooldown/cancel/sceneauthority, primeclinch, clothing sockets и gameplayжесты требуют своих доказательств. Новыеиндексы/ширина/profile должны пройти реальные native/ART/GAMEPLAY/QA/Lead и build/CI gates. Историческая nativecomponentacceptance остаётся исторической, не текущим schema2runtimePASS.
