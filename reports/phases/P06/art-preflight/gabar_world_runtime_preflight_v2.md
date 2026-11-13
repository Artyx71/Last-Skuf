# P06 — Gabar world runtime ART preflight v2 / native02

**VISUAL_MOVEMENT_ACCEPTABLE_FOR_CAPTURED_CONFIGURATION.** Оба ограниченных finding native01 закрыты новым evidence: unstable pixel raster исправлен, семь реальных непрерывных state/direction joins показаны без fixture resets. Четыре direction SOURCE acceptance сохраняются. Это оценка записанного ART/movement fixture, не fullworld/gameplay/combat/P06 approval и не real-time feel assessment.

## Evidence и независимость

Source HEAD `79fa2ec645edf1ba4446f353f864b26c93362db3` corroborated read-only `.git`/HEAD/ref files, без Git commands. Все508 frozen source inventory hashes и49 validation artifact hashes совпали. Авторская native02 validation110/110 liveX11,40actualPNG(32phase+8transition), sourceunchanged/cleanexit; operation0454b8a10ded4c8ba00cfe12d0906806 consumed, по author record. Reviewer не запускал Godot/controller/build/generation/source edits/subagents. Только разрешённые reports/derived diagnostics.

Production atlas SHA `1fe0754e2d974d205ed21b02bd1bf2c712725263b9b87506f028f3e7f9419bdd` не изменился от native01; принятые rows DOWNv5a/LEFTv3b/RIGHTv4b/UPv6c сохраняются. Native02 MP4 SHA `b12c080a0ee466ecddba34be1461304f34065c8cd463d21cedf8c9293a00ce17`,1280×720,H26460fps,750frames/12.5s. Для temporal review декодирован original MovieMaker AVI1280×720; все750frames прочитаны, визуально оценены98 phase-onset/loop frames в20 strips,77 adjacent join frames(7×11),five within-contact frames и actual world-position crops. **Real-time playback не выполнялся**; movie feel/perceived smoothness/audio не заявляются. Lossy movie texture не используется для exact native pixel comparison.

## Native01 raster finding закрыт

Все40 native PNG640×360 показывают correct atlas animation/phase и **zero opaque-RGB mismatch** при traced visual origin; проверка не предполагает равенство floor/background pixels. Все32phase и8transition captures осмотрены; ни wrong frame mapping, ни новое handedness/likeness/clipping несоответствие не найдено.

В native01 `walk_right_0` имел229/1016 opaque pixel mismatches. В native02 та же pose при near-half-pixel physicsroot325.50003 имеет0. Actual PNG и atlas рядом в `gabar_world_runtime_v2_walk_right0_fixed_raster_8x.png`: crown/glasses/shin clusters теперь точны. Original movie frames321–325 внутри contactA показывают стабильный внешний рисунок; compression artifacts не выдаются за источник новых atlas pixels.

Read-only source inspection подтверждает render-only child offset через PixelPresentation, без round physics/collision. Обе trace содержат672samples, maximum visual grid error0; movie396samples сохраняют fractional physics. Maximum visual-root rounding distance0.60077px, внутри диагонального half-pixel bound. Это коррекция presentation, не правка анатомии/atlas или дискретизация движения тела.

Native01 не перезаписан: старые validationSHA и все41artifact hashes повторно совпали; исторический report с229badpixels остаётся FAIL/limited finding. Новый результат supersedes этот finding только для native02 source/captured configuration.

## Циклы, опора и читаемость

Изолированные12cycles подтверждены trace и extracted phase sequences. Cyclic phase order правильный: idle0→1→0, walk0→1→2→3→0, run0→1→0. Interior full holds idle20physics ticks, walk7/8, run5 при60Hz соответствуют3/8/12fps. Boundary holds короче из-за sampling, не cadence defect. Root integration внутри постоянных segments не показывает непредусмотренных jumps; native01 cadence findings воспроизведены на том же atlas.

Near/far legs и reciprocal arms различимы вactual contacts/run, passing позы узкие и отдельные. LEFTwatch остаётся leftviewnear/rightviewfar/downscreenRIGHT/upscreenLEFT. Gabar hairstyle/glasses/burgundytee/athletic build coherent во всех направлениях; повторного platformer drift, incorrect accessory или source animation blocker нет. Мелкая authored pixel variation между позами видна; на extracted повторениях нет нового whole-body jitter. Real-time boil/fast two-pose run feel без playback не одобряются и не отвергаются.

Standing root24,58 и front/up perspective strides сохраняют читаемую геометрию. DOWN RunA opaque last row y63 полностью видна вactual capture, без cutsole; source feet below standing pivot остаются authored depth extension, не усечением atlas. Walk/run не возвращают прежний packing-induced headpogo; DOWNheadtop8walk/9run, UP5. Idle apparent heights50/52/51/53px находятся в общей overhead family; на поворотах нет нового грубого scale/camera jump.

Measurement floor подтверждает отсутствие ошибочного root teleport/обрезки, но не проверяет CH01 occluders, shadows, sorting, obstacle collisions или precise foot planting. Held pixel poses перемещаются с root между animation phases; gameplay stride-speed feel требует actual real-time playtest, не выводится из таблицы trace.

## Непрерывные joins подтверждены в заданной последовательности

Новый continuous block имеет единственную initialorigin установку, затем не присваивает position/facing; движение/направление определяет actualInput.192continuous trace samples содержат8segments: idle_up → walk_right → run_right → idle_right → walk_down → run_left → walk_up → idle_up. В7joins нет reset к320,180; все root steps bounded velocity×elapsedphysics, с floating tolerance0.001px. Например right walk заканчиваетсяx367.66693, run идёт до436.30731 и idle сохраняет эту позицию; поворот DOWN сохраняетx и изменяетy, LEFT/UP продолжают из достигнутой точки.

В actual movie join strips видна соответствующая смена poses без возврата кcentre/скачка root. Instant direction changes и отсутствие blending соответствуют discrete pixel SpriteFrames; нового отрыва тела от root или неверной facing не видно. Эти7observed joins приемлемы в captured fixture; все возможные пары/диагонали/боевые transitions не объявляются проверенными. Несколько gap ticks между trace samples отмечены `*` в diagnostics: их movie content реальный, ближайший trace origin использован только для широкого crop; interpolated numeric trace не выдумывался.

Неблокирующее ограничение fixture: поздний изолированный UP путь заходит верхней частью actor в область status-label, поэтому белые UI glyphs появляются в некоторых movie crops. Это UI/grid path overlap, не white pixels вatlas и не актёрская anatomical ошибка. Для чистого promotional movie нужен иной framing; для этой технической проверки он не скрывает смену ног/цикл. Native phase PNG и continuous endpoint sprites чистые.

## Scope и артефакты

Дополнительной source regeneration или render correction по проверенному Gabar evidence не требуется. Combat/новые способности явно NOT_IMPLEMENTED вfixture и отмечены UI; это не playable-hero readiness. Muted movie не даёт audio/listening acceptance. NativeWindows/exports/fullP06 не одобрены. Native01 и все прежние source FAIL/version histories сохранены.

Основные доказательства: `gabar_world_runtime_preflight_v2_metrics.json`, `gabar_world_runtime_v2_movie_extraction.json`, четыре `gabar_world_runtime_v2_{direction}_all8_2x.png`, `gabar_world_runtime_v2_continuous_endpoints_2x.png`, targeted fixed-raster PNG/movie strips, seven `gabar_world_runtime_v2_movie_join*.png`, four movie phase review pages и `gabar_world_runtime_v2_movie_continuous_world_positions.png`.
