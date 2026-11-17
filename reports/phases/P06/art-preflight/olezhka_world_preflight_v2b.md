# P06 — Olezhka world source preflight v2b / alpha240

**ACCEPTABLE_FOUR_DIRECTION_SOURCE_CANDIDATE.** Исправленные RIGHT near/far phases читаются, а oneglobalalpha240 убирает широкую residualmatte кайму/flatcrownbar v2a без обнаруженной утраты кистей, стоп или coreface. Все32 actual poses проверены заново. Нового обязательного sourceblocker не найдено; кандидат пригоден для native movement preview. Runtime/world/gameplay/P06 acceptance не выдаётся.

Native SHA `516a65e2f3ae0448857a3e43b03b0f64514bdd363a9bdebafca885caf92fad3b`; unchanged master v2 SHA `b3d0decc7ef9b80445097a7515409a1cffb912a33355c7b4c2655bb352e8f3b1`. Reviewer `/root/art_review_p06`: fullnative32/master/inspection3x, light/dark fullatlas2x, four actual contact/runpairs8x, side walk4strips4x и v1→208→240 targeted light-background comparison. Собственная private photo/approved portrait association ранее сверена для v1 и не подменена template identity. Raw photo не копировалась в отчёты.

## Gait correction и all32 review

RIGHT A2/6 ведёт bright NEARRIGHT leg вперёд screenRIGHT, FARLEFT отведена назад. ВB4/7 теперь явно dark FARLEFT forward shin/frontshoe, brighter NEARRIGHT leg backleft с другой hip/knee occlusion. Reciprocal arms согласованы с ногами; passingB5 narrower, near-knee/weight exchange различим относительно passingA3. Это фактическое изображение source/native, не вывод из pose labels или hashes.

LEFT A2/6 highlighted near leg forwardscreenLEFT; B4/7 darker far leading leg с near leg сзади, противоположными руками и более узкими3/5. Разделение по values ниже контрастом, чем DOWN/UP, но не обнаружен повтор v1 RIGHT samelegfamily. DOWN lowerleading shoe screenLEFT вA2/6 меняется на screenRIGHT вB4/7; UP forward-away knee/trailing sole роли противоположны вA/B. UP/ DOWN passing poses distinct и уже contacts. RunA/B во всех4 directions дают противоположные anatomical leads.

Все32 поменялись относительно v1 и v2a; approval не перенесён на29нетаргетных клеток по prompt promise. Camera crown/shouldertop, foreshortenedshortlegs и stocky youngbuild сохраняют overhead family; platformer drift нет. Own cleanface/shortbrowncrop/darktee/pants/trainers продолжают approved Olezhka portrait. Glasses/watch/Gabarburgundyshirt, новых marks/tattoo/crest/weapon не найдено. Shortcrop crown остаётся стилизованно текстурной/объёмной относительно фото, отдельный likeness mustfix не требуется.

## Alpha/contour честно

На actual light/dark v2b больше нет conspicuous broad brownmatte ring или flat bar над LEFTidle crown, которые блокировали208. Небольшие тёплые hair/skin edge pixels остаются частью ramp; непрерывного широкого внешнего panel/fringe не видно при native/2x/targeted8x. Контуры заметно тоньше/местами светлее, чем вv1, особенно bare arms и face; это видимая stylistic variation, не заявляется byte-identical outline restoration. На светлом фоне силуэт остаётся читаемым; all32 one8connected, detached fragments или split limbs нет. Удалённой кисти/подошвы/facecore по actualview не найдено.

240 одобряется только для THIS master/THIS native hash после полного просмотра. Это не универсальный автоthreshold и не доказательство сохранности каждого rawalpha pixel. Diagnostic248/250 показывает реальные losses, такие threshold не одобрены. Без semantic masks, bodypart editing, arbitrary pixel paint или compositing: один порог применяется всему unchangedmaster, затем целые клетки pack.

Независимая reconstruction всех32 cells:192×256→48×64 NN, palette43/alpha240, onefixedYperrow. Exact finalRGBA совпадает; sourceRects/sourcealpha240bounds/clear margins/framehashes/manifest/prompt/master/metadata/inputroles verified. Ни одна POST-THRESHOLD opaque pixel не потеряна при placement. Native alpha0/255,34opaque colors,32unique — статистика дополнительно к image review, не animation proof.

## Geometry и следующая граница

Headtops DOWN `[8,8,8,8,8,8,8,10]`, LEFT `[6,6,8,8,8,8,8,8]`, RIGHT `[6,6,7,7,6,5,7,7]`, UP `[5,5,5,5,5,5,5,5]`. Walk bob0/0/2/0px, run2/0/0/0px; источник не добавляет >2pxwholeheadpogo. DOWNRunB имеет2px head difference и требует actual cadence check, не оценивается толькоhashами. Idle heights DOWN50/LEFT51–52/RIGHT52/UP53 соответствуют общей family. FixedYDOWN0/LEFT0/RIGHT0/UP+1.

Standing pivot24,58 сохраняется; LEFTidle0 sole57 противidle1 sole58 —1px subtlebreath/shapevariation с общимanchor, не perpose recentering. Depthstrides DOWNexclusivebottomдо63, UPдо62; весь maskedfigure внутри48×64, нет opaque crop. Как у Gabar, actual movement fixture ещё должен проверить floor/root, framecadence/loopcut, side leg readability, textureboil и непрерывные state/direction joins. Не переносить Gabar runtimeapproval на нового героя.

Runtime Olezhka world_sheet отсутствует; source-only manifest честный. V1 RIGHTgait FAIL, strict128packfailure иv2a208contour FAIL сохранены. Новой threshold/generation итерации по текущему принятому sourcefinding не запрашивается. Combat/newabilities/audio/exports/fullP06 не одобрены.

Reviewer не запускал Godot/controller/Git commands/generation/source edits/subagents; записи only permittedROOTart-preflight. Evidence: `olezhka_world_preflight_v2b_metrics.json`, `olezhka_world_v2b_light_dark_2x.png`, four phasepairs8x/fourwalk4strips4x и targeted contour comparisons.
