# P06 — Gabar RIGHT world preflight v4b

**ACCEPTABLE_RIGHT_DIRECTION_SOURCE_CANDIDATE.** Targetedwholepose edit делает oppositeleg roles читаемыми в actualnative48×64, сохраняя overheadcamera и farleftwatch. Нового sourceblocker для RIGHT не найдено. Ограниченный sourcefinding не является runtime/fullworld/P06approval; V4FAIL и предыдущая история сохраняются.

Ревьюер `/root/art_review_p06`: actualmaster/native8frames/inspection4x, targetedactualnative8x contact/runpairs, walk4filmstrip, V4→V4bcontactBcomparison. Godot/controller/generator/Git/source изменения не выполнялись; записаны только разрешённые отчёты/deriveddiagnostics. Soleexecutor не затрагивался.

Native SHA `663ab5b1f274f696abca552234fa3039988d6111404f9417acb00f9e4e30932c`. Master `f75f7900f82f1b1bb7b6b27640f05545f892574fc708141de492268d5f90e1c5`. Источник1536×1024/4×2целые384×512cells, native384×64. Manifest CANDIDATE_NOT_IN_PRODUCTION; при итоговом inventorycheck productionpath `game/assets/art/characters/gabar/world_sheet.png` отсутствует, поэтому прежнее утверждение «production всё ещё V2» в этом отчёте не делается. Sourcecandidate доступен и проверен независимо от текущей reorganizing authorworkspace.

## Исправление gaitreadability

ContactA2 сохраняет светлую foregroundnearRIGHTleg впереди справа и тёмную farLEFTleg сзади слева, nearbareRIGHTarm сзади/farwatchLEFTarm спереди. ContactB4 теперь явно имеет **тёмную farLEFTshin/rightfrontshoe**, а ближняя светлее выделенная RIGHTleg уходит назад влево. Перекрытие у таза/значения trouserramps позволяют прочитать противоположную leadingleg в конечном native, вместе с уже правильным обменом рук.

RunA6/RunB7 дают тот же различимый near/farexchange: вB тёмная дальняя нога вытянута вперёд, светлее выделенная ближняя согнута и поднята сзади. Frame7 перестал читаться прежним highlightedforegroundshin stance при смене одних рук. PassingB5 согласует darkfarweightleg и brighternearknee; passing3/5 существенно уже contacts. Последовательность contactA→passingA→contactB→passingB и runA↔B теперь читается как sourcegait. Внешняя sidecontactсилуэтная форма закономерно похожа, различение ролей дают coherenthip/legocclusion и стабильные near/farvalues, а не label/количествоhashes.

## Камера, часы, anchors

Крупная видимая crown/shouldertop, broadbody и короткие legs остаются в LEFTv3bfamily. Idle LEFT24×52px, RIGHT24×51px, без platformerdrift. Sweptbrownhair/rectangularglasses/burgundytee/darkpants и athleticshoulders сохраняют Gabaridentity.

Eastviewwatch остаётся только на дальней anatomicalLEFTруке: forwardfarwrist в2/6, задняяfarwrist в4/7; ближняя RIGHTрука голая. Нет новой neararmwatch ошибки. Это положительный handednessfinding только для нового candidate, история wrongV2productionrow не переписывается.

Exclusivebottom58 во всех8 клетках; headtops `[7,7,8,8,7,6,8,8]`. Walkrange2px, run8→8px, спокойныеidle7→7px. Нет sourcepogo/clippingblocker. Actualplayback всё ещё должен проверить footslide, loopcut, idle↔walk↔runtransition и мелкую textureboil.

## Integrity и scope

Native alpha0/255,35непрозрачных цветов,8уникальных RGBAклеток. Все8sourceRects/clearcellmargins/bounds/framehashes совпали; generationprompt/master/inputroles hashes фактически сверены. Hardpixel source без photo remnants/backgroundpanels, wholeposeimageedit provenance не заявляет proceduralanatomy.

Prompt просил сохранять5нетаргетныхпоз. Их фактические nativehashes изменились вместе с3targetposes; поэтому **повторно осмотрены все8**, а не перенесено V4approval по предположению о byteidentity. Поиндексные changedpixelcounts сохранены в metrics. Camera/identity/handedness regressions визуально не выявлены; sourcevariety не выдаётся за доказанную animationstability.

Следующая граница: DOWN/UP независимо, затем единый4directionnativeworld/пивоты/масштаб и actualruntimecycles/input. До этих доказательств полноценной world/animationприёмки нет. SourceRIGHTv4b пригоден для дальнейшей boundedintegration; новый indefinite generationloop по этому исправленному finding не требуется.

Evidence: `gabar_world_right_preflight_v4b_metrics.json`, `gabar_world_right_v4b_phase_pairs_8x.png`, `gabar_world_right_v4b_walk4_4x.png`, `gabar_world_right_v4_v4b_contactB_comparison_8x.png`.
