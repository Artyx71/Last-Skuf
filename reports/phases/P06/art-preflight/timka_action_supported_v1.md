# Независимое schema2 SOURCE ART review — Timka ACTION28

**ACCEPTABLE_SUPPORTED_LAYOUT_SOURCE_CANDIDATE.** Принят только исходный ACTION28 компонент профиля`timka_supported_v1`. Все28 обязательных поз заново осмотрены; это не runtime, не две реализованные способности, не FIN24 и не P06/mergePASS.

Reviewer `/root/art_timka_recovery`, `independent_of_author=true`: отдельный независимый контекст, не автор assets/compactor/loader/tests. WORK только прочитан; собственные записи только ROOT под `timka_action_supported_v1*`. Godot/Git/controller/runner/генераторы/сеть не запускались. Никакие WORK/game/source файлы не менялись. Сырые фото не читались/не копировались/не передавались; ownпортрет используется для artworkcontinuity, не новой humanlikenessприёмки.

## Утверждённый контракт и точные bytes

Прочитаны immutable ownerdecision`automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json`, обе сохранённые proposals и текущая SDD. Decision APPROVED содержит32+28+24=84 и явное отсутствие fire/sharp/firearm для Тимки, но phase/merge/implementationcomplete=false. SHA обоих proposals совпадают с immutabledecision. Старые proposed/FAIL тексты не переписаны; исключение84 само по себе не принимает ни один компонент.

Schema2/layout_profile`timka_supported_v1`, kind`action`, source_cells=28, source_column_mapping=[0, 1, 2, 3, 4, 5, 6], native[336, 256],48×64/pivot24,58/4directions проверены строго. PNG SHA `542dfe10459d04d1d0725c495965bd2f04bb25db701a16b8acff7d4fd2000d2c`; manifest SHA `cf349a08c4a91a7950522f7e610dabe269bb257447bc078d7ed1c9d47f2b015a`; master SHA `806abc3d2fe470c92a3910b8dca364372693639e06c50e5235b313b32e245b7a`. Master остаётся исходным32клеточным архивом; фактический бюджет этого листа —28, без фиктивных reservedcells.

Независимо проверена selection/compaction каждая целая RGBAячейка и её mapping/index/direction/rect/pivot against originalnative+manifest. Все28 совпадают байт-в-байт; frame metadata сохраняет правильные source_rect/source_column/bounds/DY. Заново восстановлен каждый выбранный192×256source→48×64native NN/палитра/alpha128/зафиксированный rowDY; полныеRGBA совпали с кандидатами без opaquealignmentloss. Нет anatomyedit/painting/зеркала/перестановки частей тела в компактизации. WORLD дополнительно проверен как byte-exactencoded PNG, не только decodeRGBA.

Native34opaque colors,alpha0/255, прозрачныеRGBzero, unique28; периметр каждой nativeячейки прозрачный. Цифры и SHA подтверждают целостность, не заменяют визуальную приёмку.

## Свежая визуальная оценка

Заново просмотрены28required cells на светлом/тёмном фоне и собственный принятый портрет. Отдельно рассмотрены WORLD→ACTION0/1/2 в четырёх направлениях, interaction3, hurt4 и whole-source hurt4/fall5/death6 сравнения. Контакты читаются как осторожный толчок открытой ладонью по facing с recover, а не primegrab. Interaction тянется к ненарисованному объекту, hurt имеет recoil, fall поддерживается рукой/согнутыми ногами, death — цельное инертное curledbody. Crown/борода/hooddown/длинные рукава/малые руки/брюки/обувь согласованы с WORLD. Смерть6 является static hold, не самостоятельным многофреймовым циклом.

Source-only strips/wholecellcomposites — диагностика исходных поз, не actualGodotplayback/cadence/physics/contact/footlocking. Новое качество звука не заявлено. Положительное решение не наследуется автоматически от прежнего schema1 или nativepreview.

## Поля и охват

Все28 выбранных sourceклеток имеют поля>=16px, native минимум4px и прозрачный периметр. Исключена только старая колонка7/fire во всех4строках; огнестрельное reference-изображение не заменено пустотой/дубликатом/чужой фигурой и не принято в новом наборе. Старые32клетки проверены по SHA только как целостность исходного файла; свежая ART-приёмка касается именно0..27новыхиндексов/старыхsourcecols0..6.

## Решение и последующие gates

`schema=2`, `layout_profile=timka_supported_v1`, `source_cells=28`, `reviewed_cell_indices=0..27`, `all_required_cells_freshly_reviewed=true`, `source_only_acceptance=true`, `must_fix=[]`. Legacyуниверсальный флаг32не используется. `runtime_approval=false`, `full_phase_approval=false`, `phase_approval=false`.

Прочитан финальный strict`adopt_timka_supported.py`, включая reviewer:string/independent_of_author и обязательныеoriginalnative+manifest+master/owner/script hashes. Его SHA связан с inventory. Сам adopter/compactor не исполнялись, миграция gameфайлов не делалась. Inventory включает только source/profile/reference/instruction/provenance inputs; изменяемые`character_frames.gd`/loader/tests не frozen. Текущая runtimeготовность из приёмки не выводится.

FIN24 не просматривался/не принят: прежний environmental finding остаётся отдельным обязательным блокером. Реальный disengage (guard→reversewalk→recover), collision/clock/cooldown/cancel/sceneauthority, primeclinch, clothing sockets и gameplayжесты требуют своих доказательств. Новыеиндексы/ширина/profile должны пройти реальные native/ART/GAMEPLAY/QA/Lead и build/CI gates. Историческая nativecomponentacceptance остаётся исторической, не текущим schema2runtimePASS.
