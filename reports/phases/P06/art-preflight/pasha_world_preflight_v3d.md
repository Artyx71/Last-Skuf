# Независимое ART SOURCE review — Pasha WORLD v3d

**ACCEPTABLE_FOUR_DIRECTION_SOURCE_CANDIDATE.** Все32 исходные позы Паши и12упорядоченных source-циклов просмотрены заново. Блокирующих SOURCE ART findings не осталось: корректны противоположные боковые ноги, согласованность камеры/корпуса и поля. Это приёмка исходного WORLD-компонента; runtime, фазаP06 и merge не принимаются.

Reviewer `/root/art_timka_recovery` независим от автора/сборщика/controller. WORK только прочитан, записи только ROOT `reports/phases/P06/art-preflight/pasha_world_preflight_v3d*`. Godot/builders/runner/Git/controller/network/generator/authorhelper не запускались. Сырые фото не читались/не копировались/не передавались; сравнивался собственный принятый портретный арт. Это continuity персонажа, не новая human-photo likeness оценка. V1/v2e FAIL и boundedcell12decision сохранены.

Master SHA `851fffeecb2b36dc5f65eb255170dc925bf3583d75c28723069e5b4f7d2c8715`; native SHA `5be839b79f4b588f0c88d4038bec5fe633e59a1dac88ed2062742062fd5ad094`.

## Независимая точная проверка

Заново реконструированы4raw wholefigure placementsv3a/b/c/d из сохранённых rawposes: alpha>=128bounds, единыйNNscale, resize/placement, resized/outputRGBA и промежуточные masters. Совпали полные RGBA-байты всех32 ячеек на каждом шаге; каждый шаг меняет только одну целую клетку. Четыре call prompts/meta/referenceSHA сверены; оба reference каждого вызова — точные NN4 целые **собственные** v2eB и v1A клетки. Другой персонаж не использован в этих camera-edit вызовах. Pixel-lock отдельных ног/рук не заявляется: generated completefigure заново нормализованNN, а ownership проверен глазами.

Итоговая v3d меняет относительноv2e ровно[12,15,20,23] в source **и** native; остальные28byte-exact. Все8idle0/1 source-byte-exactv1. Ранее принятая отдельно12 не стала автоматическим основанием для остальных;15/20/23 фактически просмотрены в финальном листе и непосредственных сравнениях ownA/oldB/newB/neighbor.

Унаследованные8wholefigure переносов v2d→v2e снова независимо реконструированы по32before/afterRGBA/support bounds. Число alpha>=128 и байты supportrect сохранены, уменьшения/покраски/зеркала нет. Эти перенесённые клетки byte-exact сохранены вv3d.

| Index | Translation sourcepx |
|---:|---|
| 2 | [0, -5] |
| 4 | [0, -5] |
| 6 | [0, -6] |
| 7 | [0, -5] |
| 26 | [0, -3] |
| 28 | [0, -3] |
| 30 | [0, -1] |
| 31 | [0, -5] |

Exactnativepack восстановлен32/32: whole192×256NN→48×64, фиксированная палитра/alpha128/fixedcolumn0 rowanchor. ВсеRGBA bytes/32cellSHA/весь384×256native совпали.35opaque colors,alpha0/255,32unique; sourcegutterминимум16 во32, nativeпериметры прозрачны, opaqueplacement/alignmentlossnone. Точные LRmirrorcols отсутствуют; это техническая проверка, дополненная визуальным просмотром.

## Визуальный вывод

Просмотрены master и все32native на светлом/тёмном фоне, собственный портрет, целые SIDE2/4/6/7 при равном display scale, ownA/v2eB/v3dB/neighbor сравнение4исправленных поз и все12ordered source strips: idle0→1,walk2→3→4→5,run6↔7 в четырёх направлениях. GIF250ms/кадр сохранены только как диагностические source aids; они не подтверждают productioncadence и не выдаются за реальную игру.

Сохраняются собственные объёмные взъерошенные тёмно-русые/светло-коричневые волосы, узкое лицо/короткая щетина, компактный худощавый взрослый силуэт. Long darkcrewneck остаётся безhood, tinybluecollar/полные рукава/брюки/обувь согласованы; новые татуировки/предметы/способности не добавлены.

На обеих сторонах B4/B7 дальняя нога ведёт от более высокого hip вперёд, ближняя/нижняя уходит назад; видны две непрерывные hip→thigh→knee→shoe цепи и противоположная работа рук. Это действительное чередование относительно A2/A6, не только смена тени/кулаков. DOWN/UP также чередуют ноги/руки. Passing3/5 имеют различимые kneepassing/arm фазы; исходная четырёхкадровая последовательность с новой4 читается согласованно. Это не доказательство физического footlocking или productionскорости.

Все4Bcamera edits теперь согласованы с собственной A/idle/passing family: ракурсно сокращённое лицо, более короткая шея, высокий collar, компактнее/шире shoulder/crewneck footprint. Исправленные15/20/23 не возвращают прежнюю плоскую узкую bodyfamily;12 также заново проверена внутри целого листа. Сохраняется надголовная crown/shouldertop подача, нет новой серьёзной подмены одежды/масштаба/конечности/камеры. Допустимые authoredhead/hair/pose вариации всё ещё должны показать себя в реальном native loop.

**Закрыты SOURCE findings:** PASHA-WORLD-SOURCE-SIDEGAIT-01, PASHA-WORLD-SOURCE-GUTTER-01, PASHA-WORLD-SOURCE-SIDE-CAMERA-FAMILY-02. Must-fix пуст.

## Обязательные последующие gates

`all32_freshly_reviewed=true`, `source_only_acceptance=true`, `runtime_approval=false`, `full_phase_approval=false`, `phase_approval=false`. Прочитан актуальный строгийadopt_world.py: status/schema1/actorpasha/kindworld/report/metrics/master/native/inventories соответствуют его read-onlyпроверяемому контракту. Сам adopter не запускался; SOURCE принятие допускает следующий штатный компонентный шаг, не означает завершённую интеграцию.

Нужны отдельные реальные Godotloops с32phase captures/native movie и настоящим cadence; side2→3→4→5/run6↔7 head/crown/collar/body continuity, pixelgrid/fractionalbody и непрерывныйInput. Для inherited8translations тело сдвинуто целиком на1–6sourcepx; фиксация строки не доказывает floorjoin.

Фактические nativebottom-exclusive по колонкам сохранены: DOWN[58,58,60,58,60,60,60,60];LEFTall58;RIGHT[58,58,59,58,59,59,59,59];UP[58,57,59,58,59,58,59,59]. RowDYdown0/left0/right0/up−1, не per-frame sole58. Будущий runtime review обязан увидеть эти проекции, а не скрыто переякорить каждую стопу. Аудио/gameplayfeel/contact/способности/боёвка/FPS/exports/полнаяP06/Lead/merge этим SOURCEрешением не принимались.
