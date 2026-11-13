# P06 — Gabar world runtime ART preflight v1

**LIMITED_RENDER_FIX_REQUIRED_AND_TRANSITIONS_UNPROVEN.** В evidence `world-native-01` подтверждаются правильная сборка/отображение32 поз, семантика gait, стабильный root и cadence. Найдена ограниченная ошибка native pixel raster в одном capture; нужен render-only fix и новое доказательство. Четыре direction SOURCE acceptance сохраняются. Полного world/runtime/P06 approval здесь нет, новых artwork generations finding не требует.

## Scope и способ просмотра

Ревьюер `/root/art_review_p06` работал read-only: Godot/controller/Git commands/generation/source edits/subagents не выполнялись. Единственные записи — этот разрешённый reportdir и derived diagnostics. Проверены actual32 PNG640×360, все8 поз каждого направления визуально в contact sheets2x, один fullviewport и targeted anomalous crop8x. Из реального MovieMaker AVI декодированы542 кадра; визуально просмотрены68 phase-onset/loop frames во всех12 состояниях, дополнительные timing/fullviewport и five within-contact frames в original1280×720 raster. **Видео не смотрелось в реальном времени**: нет утверждения о feel, perceived smoothness или real-time viewing. Temporal findings основаны на extracted actual video frames + trace, не на синтетическом проигрывании atlas.

Авторский fixture явно пишет «БОЙ ЕЩЁ НЕ ПОДКЛЮЧЁН». Combat/newhero abilities, audio/listening, gameplay integration, exports/Windows и full P06 не проверены и не одобрены. MP4 muted; source AVI содержит MovieMaker audio stream, но это не audio acceptance.

## Integrity и mapping

Frozen HEAD `e6c32921d9f419cc54f807992fe65dbccca3f4d5` независимо corroborated read-only `.git`/HEAD/ref files без Git commands. Все494 source inventory hashes совпали с текущими файлами; все41 validation artifact hash совпали. Авторская validation фиксирует91/91 liveX11 checks,32captures, cleanexit/sourceunchanged и operation45be711a822d447981f8d0d21cc2aadc; reviewer не повторял executor run.

Production atlas SHA `1fe0754e2d974d205ed21b02bd1bf2c712725263b9b87506f028f3e7f9419bdd`. Его четыре RGBA rows byte-identical принятым DOWNv5a, LEFTv3b, RIGHTv4b, UPv6c. Теперь production atlas действительно существует; прошлые source отчёты честно фиксировали его отсутствие в тот момент. Все32 capture identities/phases визуально соответствуют нужному source atlas; у31 PNG opaque template pixels совпали RGB точно после integer translation. Один correct-pose capture имеет raster discrepancy, описанный ниже; это не wrong expression/phase mapping.

MP4 SHA `2ffa9bdf505765aba1040fd84633464b84dc92cfdaf6333aa7ce942dc6bcc78d`,1280×720,H264,60fps,542frames/9.033333s. Original AVI MJPEG1280×720/60fps использован для extraction. Оба artifact SHA, validation/result/source hashes и full capture inventory сохранены в metrics. Alignment video index = physics_tick−1 подтверждён pose-template offset probe (наименьший mean masked RGB error14.20 против29.31 для offset0); не использовалось неточное wall-clock movie timestamp.

## Ограниченный render finding — требуется исправление

`live/walk_right_0.png` SHA `86bcd682fbfd337bdf09e7575458b66bb8e3fc3f12f7e019cb0241b97bfa5307`: animation walk_right phase0/contactA, trace root `[325.500030517578,180]`, best integer render origin `[302,122]`. **229 из1016 opaque template pixels** отличаются от correct atlas cell row2/col2, даже после поиска соседних offsets. В actual PNG видны dropped/duplicated pixel-column детали crown/glasses/shin. Все229 local coordinates/expected/actualRGB записаны в metrics; diagnostic `gabar_world_runtime_v1_walk_right0_raster_check_8x.png` показывает actual рядом с source.

Связь с fractional near-half-pixel root очевидна как корреляция, но конкретная GPU sampling/downsample причина этим review не доказана. В original1280 AVI отдельно просмотрены frames321–325 внутри одной contactA phase; первая соответствует root325.5. Они не заменяют exact PNG comparison: MJPEG/H264 lossy и дают compression texture noise. Поэтому не заявляется229 movie bad pixels или доказанное persistent corruption всего видео.

Bounded action: стабилизировать только visual transform/pixel sampling с сохранением fractional physics; повторить actual native run и exact opaque-template comparison, особенно near-half-pixel horizontal position. Новая анатомия/перегенерация не нужны. Evidence01 и его hashes должны остаться immutable; исправление требует новой source/capture версии. До такого доказательства crisp native raster не принимается полностью.

## Gait, cadence, floor/root и scale

Все12 live/movie trace segments имеют корректный cyclic phase order; walk0→1→2→3→0, run0→1→0, idle0→1→0. Interior full holds: idle20physics ticks, walk7/8 alternating, run5; при60Hz это3/8/12fps. Начальные/конечные holds короче из-за границ sampling, не объявляются cadence defects. Live и movie имеют480 samples каждая; root integration maxerror менее0.000015px. Idle root неподвижен, walk110px/s, run158.400009px/s в правильной оси без непредусмотренных скачков внутри каждого измеряемого segment.

На actual extracted sequences читаются противоположные anatomical legs и reciprocal arms контактов/run, distinct narrowed passing poses. LEFTwatch: leftviewnear, rightviewfar/occluded, downscreenRIGHT, upscreenLEFT; прежняя wrong UP RunA watch не возвращается. Gabar hair/glasses/burgundytee/широкие плечи сохраняют identity; source camera остаётся overhead, без platformer drift. Native idle heights DOWN50/LEFT52/RIGHT51/UP53 и видимые тела в fixture не показывают нового грубого scale jump.

DOWN walk headtop8 во всех4 фазах, run9 в обеих, UP5 во всех8 — прежний packing pogo устранён. Side walk bob до2px; texture changes внутри authored pose family видны, но не обнаружено нового source-anatomy blocker. Idle в целом меняет небольшие руки/лицо детали без whole-body jitter. Real-time texture boil/fast two-pose run feel не оцениваются по contact sheets; raster anomaly и compression не смешиваются с source texture variation.

DOWN RunA source last opaque row y63 реально виден в capture; shoe не обрезан нижним краем atlas. Standing pivot24,58 остаётся общей root точкой, а front/up stride feet ниже standing baseline: DOWN exclusivebottom58..64, UP58..61. На measurement floor нет сплошной платформы, в которую стопы должны упираться; perspective stride around root сам по себе не clipping. Во время segments root движется линейно, прежнего вертикального подскакивания всей головы нет. Однако это fixture без world occluders/shadows/collisions: sorting/contact в CH01 и exact foot planting не доказаны. Удерживаемые sprite poses перемещаются вместе с root между фазами; скорость/длину шага для gameplay feel reviewer не одобряет без real-time просмотра.

## Непроверенные joins — нужно конкретное новое evidence

Source fixture `character_world_preview.gd` перед каждым idle/walk/run явно делает `actor.position=Vector2(320,180)`; перед новым направлением прямо присваивает `actor.facing`. Между состояниями отпускает клавиши на2 frames. Поэтому jumps к centre в movie — искусственные fixture resets. Они не являются обнаруженным movement bug и не доказывают плавность transition.

Для завершения transition review нужен короткий continuous actualInput segment без position resets/direct facing assignment: idle→walk→run→walk→idle, затем смена направления движением. Записать соответствующие trace/captures/movie; проверить root continuity и визуальные joins на тех же atlas hashes. Current12 isolated cycles подтверждены, continuous joins остаются UNPROVEN.

Evidence: `gabar_world_runtime_preflight_v1_metrics.json`, `gabar_world_runtime_v1_movie_extraction.json`, четыре `gabar_world_runtime_v1_{direction}_all8_2x.png`, двенадцать `gabar_world_runtime_v1_movie_{state}_{direction}_phase_sequence.png`, targeted raster/timing diagnostics. Предыдущие V1/V2/V3/V4/source packing/watch FAIL сохранены; новый runtime finding их не стирает.
