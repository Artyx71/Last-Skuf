# P06 — Gabar LEFT world preflight v3b

**ACCEPTABLE_LEFT_DIRECTION_SOURCE_CANDIDATE.** Wholepose camera correction восстановила совместимые overhead/chibi пропорции и сохранила читаемые противоположные gaitphases. Для этого leftsource новых mustfixfindings нет. Это пригодный источник/ориентир для следующей ограниченной работы над3остальными направлениями, **не fullworld/runtime/P06 approval**. V1/V2/V3failures сохраняются как история, production пока не меняется.

Ревьюер `/root/art_review_p06`: actualmaster, actual48×64 native8frames, sourceinspection4x, targetedactualnative8xcontacts/runpairs, walk4filmstrip и V2/V3/V3bidlecomparison. Godot/controller/generator/Git/source изменения не выполнялись; созданы только разрешённые reports/deriveddiagnostics.

Native SHA `fb168cfa677cb28525f65b77635caa1be722a6cfe0da33d511e6a85506b01553`. Master `5286bfe7d3f631ab966af32d34bb2b835a31b6c6327cdf0f294daf9bc3d3c87e`. Источник1536×1024/4×2 целые384×512cells, native384×64/8×1. Camera reference SHA `00640188cf107c373d59f769672fc0945ad9301385d0f242948fb77a6f2a1c33` независимо подтверждён как **целая V2leftidle0 mastercell, только NNresize**, без anatomywarp/partcompositing.

## Камера и внешний вид

Вновь видны широкая crown/hairtop, upperplanes плеч, крупная голова, укороченные torso/legs и robust athleticwidth; исчез строгий platformerprofile длинного телаV3. Nativeidle bounds: V2reference `[11,7,37,58]` width26/height51; V3FAIL `[16,2,32,58]` width16/height56; V3b `[13,6,37,58]` width24/height52. V3b близок правильной bodyfamily, а не попытка вместить высокого человека простымscale. Hair/glasses/burgundytee/darkpants/trainers согласованы с portraitidentity; широкие плечи не превращены в Yakuza obese body.

Sourcecartoonfeatures в native маленькие, но rectangularglasses/светлое лицо и sweptbrownhair читаются примерно на уровне исходного V2worldreference. Перспектива сопоставима с принятой topdown/chibi language. Actualfloor/другие направления ещё нужны для окончательной consistency.

## Реальные gaitphases сохранены

Индексы0-based. Contact2: brighternear/anatomicalLEFTleg вперёд, darkerfarRIGHTleg назад; nearLEFTwatcharm назад. Contact4: darkfarRIGHTleg вперёд, brighternearLEFTleg назад; nearwatcharm вперёд. Actualnative8x и master показывают обмен near/far legroles/перекрытий вместе с reciprocalarmphase; это не только перемещение часов или новая фактура прежнего stance.

Passing3 и5 имеют более узкое положение стоп под тазом и различимые опорную/поднимающуюся ноги с согласованными near/far highlights. Widths actualnativewalk2/3/4/5:35/23/32/24px, что подтверждает видимое wide/narrow/wide/narrow, но positivefinding основан также на knee/legroles, не одной ширинеbbox. Последовательность A/passA/B/passB читается.

Run6/7 сохраняют противоположные near/farlegs и arms с более широким stride/forwardlean; watcharm действительно swingsback→forward с одной anatomicalleft руки. Currentleft wristcorrect. East-handedness GABAR-WORLD-03 этим **не закрыт**, потому что east здесь нет. Twoidleposes содержат quietvariation; animationfeel/breathing утверждается только после runtime, не по8uniquehashes.

## Feet/head consistency

Exclusive solebottom58 во всех8клетках, no opaque clipping; X технически не перемещался. Headtop0–7 `[6,6,9,8,8,7,8,8]`: idle стабильны, walk имеет2pxrange9→7, run8→8. Прежний left-run3pxpogo исчез. Walk имеет небольшой bob/переход idle→movement до3px, допустимый для sourcecandidate при этих разных наклонах/ногах, но actualplayback должен проверить отсутствие нежелательного скачка на loop/restart. Soleanchor — техническое условие, не автоматическое доказательство отсутствия footslide.

## Integrity и дальнейшая граница

Native alpha0/255,34непрозрачных цвета,8разных RGBAклеток. SourceRectflattening/bounds/clearcell margins и framehashes совпали; prompt/master/inputroles hashes совпали. Nativehardpixel edges без photo remnants/backgroundpanels, никакой proceduralanatomy/mirror в техническом packmanifest не заявлен. Уникальные8hashes — только structuralcheck, gait/camera оценены по изображению.

Productionworld по-прежнему V2SHA `3b1126fd51712883045fb9ec2b2725c017050e0a00fffdf91dc439f9f2c02571`; V3bmanifest CANDIDATE_NOT_IN_PRODUCTION соответствует факту. Исторические reports не переписываются. Следующие3direction-specificsources могут использовать V3b как ясный gait/bodytemplate и собственную целую V2directionidle как camerareference; каждый новый результат нужно независимо сверить, особенно farleftwatch в east. Не считать оставшиеся направления зеркалами/копиями одобренными заранее.

Для fullworld нужны реальные4directionnativeanimations, ground/pivot/scale consistency и liveworldmovement/loop/idle↔walk↔run captures. Actions/finishers и fullP06 gates остаются вне этой оценки. Никакого runtime/полногоworldPASS пока нет.

Artifacts: `gabar_world_left_preflight_v3b_metrics.json`, `gabar_world_left_v3b_phase_pairs_8x.png`, `gabar_world_left_v3b_walk4_4x.png`, `gabar_world_left_v2_v3_v3b_camera_comparison_8x.png`.
