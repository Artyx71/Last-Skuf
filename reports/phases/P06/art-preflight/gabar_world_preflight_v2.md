# P06 — Gabar world source preflight v2

**FAIL_SOURCE_MOVEMENT_SEMANTICS, повторный source-кандидат.** V2 улучшает passingposes, но side contacts и runphase reversal по-прежнему не исправлены, eastwatch остаётся на неправильной руке. V1FAIL и его hashes/report сохраняются; это не runtime/phase decision.

Проверены actual master, actual native48×64, inspection3x и4новых диагностических NN4xfilmstrips всех32 клеток. Ревьюер `/root/art_review_p06` не запускал Godot/controller/generator/Git и не менял source. Изменены/созданы только собственные reports artifacts.

Точный native `3b1126fd51712883045fb9ec2b2725c017050e0a00fffdf91dc439f9f2c02571`. Master `06597e527a219f358055d3920f44f5f0340356a1e3d3d54ef4e9cf290aed8516`. Сохранённый `world_native_v1.png` по-прежнему имеет прежний SHA `166827e8c90cbd6e88118f330368178c165efee5419c2a2fdbd5ea98c7983c1a`. Column IDs далее0-based: idle0–1, walk2–5, run6–7.

## Исправлено частично

В side left/right cols3 и5 теперь действительно содержат более узкое положение ног под тазом/поднятое колено. Это заметная wholepose разница по сравнению с V1; её нельзя списать на pixelnoise. Ритм wide→narrow→wide→narrow теперь визуально присутствует. Down/upwalk также лучше отделяют contacts от более узких проходных поз; противоположное положение стоп читается лучше, чем в V1. Эти улучшения не дают автоматического approval полного цикла, когда две стороны тела ещё не обмениваются ролями.

## Сохраняющиеся blockers

**GABAR-WORLD-01 / HIGH, PARTIALLY_REMEDIATED_NOT_CLOSED.** В side rows left/right контакты cols2 и4 всё ещё показывают **одну и ту же ближнюю ногу вперёд и дальнюю назад**; watch-bearing neararm остаётся сзади/внизу, другая рука спереди. Passing3 и5 тоже принадлежат одной leg/weightfamily. Поэтому sidecycle читается как contactA→passingA→contactA→passingA, а не contactA→passingA→contactB→passingB. Нужен настоящий oppositelead contact4 с обменом ближней/дальней ноги и reciprocal arms, затем matching passing5 с другой опорной ногой/поднимающимся коленом. Определять фазу по label/prompt или уникальному SHA нельзя — оценивается видимая anatomy.

**GABAR-WORLD-02 / HIGH, OPEN.** Side run cols6 и7 остаются той же contactfamily: ближняя нога вытянута в facingdirection, дальняя согнута сзади; руки не обмениваются. Это не полноценная runA/runB пара. Во фронтальном/заднем run также нет достаточно ясной противоположной arm/legphase: тот же крупный arm/lean silhouette доминирует в обеих клетках. Принимать run2 для4направлений нельзя. Две новые позы могут оставаться компактным2frame budget, но обмен ведущей ноги/рук должен быть явно виден в каждом направлении. Нельзя чинить это ускорением, reorder или переменным движением всей клетки.

**GABAR-WORLD-03 / MEDIUM, OPEN.** Right/east row по-прежнему рисует серебряные часы на ближней нижней руке, которая является anatomicalright при этом facing. Нужно держать watch на anatomicalleft дальней руке или естественно скрывать его телом; не рисовать часы на ближнем запястье для симметрии. Front/down screenright и back/up screenleft соответствуют левой руке; westneararm допустим. Требуется новая правильная wholepose anatomy, не procedural wrist/limb compositing или mirrorfix.

## Anchors и пригодные части

Left run headtop теперь9→8px вместо V1 10→7: прежний3px pogo значительно уменьшен, само по себе это уже не отдельный blocker. По walkleft tops9/8/8/8px, right7/7/6/7px; эти небольшие изменения надо проверить как осмысленный bob в runtime после исправления gait, а не объявлять stablemotion только по sole58.

Сохраняются узнаваемые Gabar glasses/brownhair/burgundytee, athletic silhouette и общая accepted topdown/chibi camera language. Identity не требует переделки в этом preflight. Nativehardpixel clarity пригодна, видимого clipping/background contamination нет. Source master1536×1024, atlas384×256,32cells48×64, alpha0/255,39 непрозрачных цветов. Все32 source bounds/clearcell margins/framehashes/native bounds совпали; master/prompt/inputrole provenance hashes совпали. WholecellNN packer не реконструирует anatomy.32разных hashes остаются техническим фактом, не доказательством32корректных фаз.

## Следующая ограниченная попытка

Предложенная автором стратегия **4отдельных direction-specific8pose sources (4×2cells)** разумна как способ снизить неоднозначность одного32cellgrid. Это предложение по bounded remediation в существующем scope, **не предварительная арт-приёмка**. Сначала independentlyinspect contrasting contactA/contactB и runA/runB каждой стороны/handedness, затем четыре sequentialwalk phases и wholepose packing. Для стороны должны явно меняться местами near/far leadleg и armforward/back; passingposes не заменяют oppositecontact. Не генерировать остальных героев по V2posepattern и не ослаблять gaitcriteria. Не нужны anatomical reconstruction/нарезка/склейка частей тела; новые цельные authoredposes остаются обязательными.

После sourceисправления нужны actual nativeworld playback/input/floor/groundcontact проверки. Runtime/worldactions/finishers и fullP06 остаются вне этой оценки. V1/V2 failures сохраняются как история, исправления не получают PASS только из generation receipt.

Exact metrics/provenance: `gabar_world_preflight_v2_metrics.json`. Evidencefilmstrips: `gabar_world_down_v2_4x.png`, `gabar_world_left_v2_4x.png`, `gabar_world_right_v2_4x.png`, `gabar_world_up_v2_4x.png`. Подписи ожидаемыхфаз диагностические; `CONTACT B?`/`RUN B?` подчёркивают, что название клетки не доказывает правильную позу.
