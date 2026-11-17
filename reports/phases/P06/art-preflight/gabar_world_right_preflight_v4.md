# P06 — Gabar RIGHT world preflight v4

**FAIL_OPPOSITE_LEG_PHASE_READABILITY.** Камера/пропорции и anatomicalleftwatch исправлены в этом sourcecandidate, armswing меняется, но oppositelead ног недостаточно ясно читается в intendednative48×64. Не принимать wholeRIGHTgait только по watch/arms или8уникальным hashes. Это sourceonly review, не runtime/phase decision; LEFTv3b sourcefinding и прежние failures сохраняются.

Ревьюер `/root/art_review_p06` просмотрел actualmaster, native8frames, inspection4x, targetedactualnative8x контакты/бег, masterlegcloseups и LEFT/RIGHTidlecomparison. Godot/controller/source/Git/generation не запускались/не изменялись; записаны только разрешённые собственные reports/diagnostics. Soleauthorlease не затрагивался.

Native SHA `47010cbd8864fb79fae3e32bc1219b677cfeb4c40a9393b4b3bee0e95f73aad0`. Master `b9c3989b95034c5c62a76d00f2b47354d8237c56198bcb9d52eca3c548a4d6b2`. Source1536×1024/4×2целые384×512cells, flattenednative384×64. Candidate пока не в production: productionworldsheet остаётся V2SHA `3b1126fd51712883045fb9ec2b2725c017050e0a00fffdf91dc439f9f2c02571`.

## Пригодные/исправленные части

Крупная голова с видимой crown, широкие upperplanes плеч и укороченные ноги согласованы с LEFTv3b; platformercamera drift нет. Idle0 LEFT24×52px/right24×51px, boundsright `[14,7,38,58]` противleft `[13,6,37,58]`:1pxheight/position difference не меняет bodymodel. Сохраняются Gabar brownhair/rectangularglasses/burgundytee/athleticshoulders и тёмная одежда.

В eastview ближняя anatomicalRIGHT рука теперь **без часов**. Часы правильно на дальней anatomicalLEFT: forward/upper farwrist виден в2/6, задняя fararm/wrist видна в4/7; вidle/accessory частично occluded. Это исправляет sourcehandednessfinding GABAR-WORLD-03 для данного нового candidate; wrongV2productionrow автоматически не становится исправленной.

Nearrightarm swingsback в2/6 иforward в4/7; farleftwatcharm делает reciprocal movement. Passing3/5 действительно уже contacts: nativewidths2/3/4/5 `34/25/33/26px`, согнутые колени видны. Headtops `[7,7,8,8,7,6,7,8]`, walkrange2px, runrange1px; exclusivebottom58 везде. Sourceanchor/pogo blocker не найден, actualplayback footslide/loop ещё не проверены.

## MUST FIX / HIGH — смена ведущей ноги не закреплена в native

Сравнение2↔4 и6↔7: arms/watch убедительно меняют фазу, но обе пары сохраняют очень похожее чтение **крупная светлее выделенная передняя голень/стопа справа + затенённая trailingleg слева**. Особенно contact4 не даёт столь же ясного обмена near/farlegs, как исправленный LEFTv3b: передняя голень по-прежнему выглядит foregroundhighlighted, задняя — recessed. Run7 меняет руки/объём согнутого колена, но контраст/перекрытие не делают farleftlead однозначным при48×64.

В master есть небольшие различия hip/thighoverlap и объёма trailingknee; это **не утверждение, что ноги являются точными дубликатами или доказанно имеют один и тот же скрытыйrig**. Проблема приёмки — visiblephase ambiguity в конечных nativepixels. Нельзя выводить правильную leganatomy только из того, что watcharm уже поменял сторону. Sourceprompt отдельно требует unmistakablelegreversal, не только arm/outline shadingchanges.

Concrete boundedremedy: цельно перерисовать oppositephase contactB4 и runB7 (и согласованный passingB5, если меняется опорная нога), сохранив нынешние camera/headscale/watch. ВB должна ясно читаться ближняя RIGHTleg сзади/foreground и дальняя LEFTleg впереди/behind nearleg у таза, с согласованными nearbright/fardark ramps и видимым knee/hipocclusion. Не добавлять новые цветные эмблемы/аксессуары ради маркировки ноги; не выполнять procedurallegswap/compositing или простое переименование фаз. Повторный source/nativepairreview нужен до wholeRIGHT approval. Новая camera correction не требуется.

## Integrity и граница

Nativealpha0/255,35непрозрачных цветов,8уникальных RGBAклеток. Все8 sourceRects/clearmargins/nativebounds/framehashes совпадают с manifest; generationprompt/master/inputroles hashes сверены. Hardpixel structure без visibleclipping/backgroundpanels, но технические8hashes не являются доказательством правильной походки. Metadata CANDIDATE_NOT_IN_PRODUCTION честна.

Остаются readableoppositelegs sourcefix, затем otherdirections/all4world/nativeplayback/groundalignment и actualcontrols. Fullworld/runtime/P06approval не выдан. Дополнительные публичные/приватные referenceuploads не выполнялись.

Evidence: `gabar_world_right_preflight_v4_metrics.json`, `gabar_world_right_v4_phase_pairs_8x.png`, `gabar_world_right_v4_master_leg_pairs.png`, `gabar_world_right_v4_walk4_4x.png`, `gabar_world_left_v3b_right_v4_camera_comparison_8x.png`.
