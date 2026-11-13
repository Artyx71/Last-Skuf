# P02 — независимый Lead Review, attempt 1

**FAIL.** Reviewer `/root/lead_reviewer`; independent art subreview `/root/lead_reviewer/p01_art_subreview`. Авторы root/gameplay_p02/art_production не использованы как reviewers. Проверенный source `1786633e2d4f366a267ae884e1b2cf6029fbc546`, evidence commit `021c126dc97bf365b95c094236ca34b4fae9b3c2`. [Draft PR #3](https://github.com/Artyx71/Last-Skuf/pull/3). P03 запрещён до отдельного PASS.

Обязательный HIGH: player melee damage происходит в authored wind-up до contact frame. Прежние тесты и actual CI зелёные, но этот контракт не покрывают. Это реальный воспроизведённый defect, не внешняя блокировка.

Прочитаны phase plan/requirements, combat config и code, native tests, installer/cache и export изменения, implementation/environment, source/provenance через отдельный art subreview. Сверены65 source files с source commit, production diff до evidence commit пуст. Lead лично открыл actual lab/melee/fall/contact-sheet frames, свои fresh Linux и Windows/Wine captures и weapon crop; subreviewer открыл все новые PNG/masters/atlases. Фото не загружались; новых likeness permissions не выдумано. Accepted P01 PNG/atlas неизменны.

Независимый `tools/verify.py --references --capture --output reports/phases/P02/reviewer-attempt1`:13/13 command checks PASS; native555/555 assertions (bootstrap6+art90+movement34+combat_art300+combat35+AI32+restart58). Дополнительно original Linux smoke/render и Windows PE render под Wine выполнены reviewer:3/3 PASS. Native Windows **не проверен**; Wine compatibility не выдаётся за Windows host QA.

Author artifact hashes66/66 совпали. Оба новых art inventories33/33 проверены independent art subreviewer. Оригинальные66 outputs и inventory сохранены в reviewer-owned snapshots: `author_snapshot_map.json` указывает original→snapshot, большие builds в ignored build/author-snapshot. Это позволяет сохранить FAIL evidence при последующих fixes. Source/art bytes восстанавливаются из указанного Git commit и source_snapshot_hashes.json.

[CI43387775768](https://github.com/Artyx71/Last-Skuf/actions/runs/43387775768) independently confirmed SUCCESS на source1786633. Reviewer сам получил job log/API и ZIP artifact14019361649: SHA256 `fc5f1d196e7258f1fe1610fc5fd2588bf785fd7df891542690321a418aca537f`, совпадает API digest. Eleven CI checks PASS, artifact скачан/инвентаризован; API runners0/variables0. Это реальный ephemeral self-hosted Linux job, не hosted Ubuntu/native Windows. Локальный privacy/reference checker PASS, raw refs не входят в артефакты игры. Wine использует локальный prefix; P00/P01 builds не перезаписывались reviewer.

Escape evidence действительно использует native input и active AI:386frames,0kills/0shots,3detections; separate training kit явно помечен и не объявлен campaign kit. Replay содержит настоящую AI death/R retry и reset snapshots. Ten-reset suite реально прошёл с cached latency <1s; это измерение конкретной машины, не performance guarantee. Авторский movie/contact sheet сам по себе **не** доказывает ранний damage: в нём движущийся patrol входит в reach около contact pose.

Поэтому выполнен дополнительный независимый native probe с заранее находящейся внутри reach целью health3 и настоящим Input.action_press. `timing_probe.json`: frame0/hits0/health3 на tick0; **frame0/hits1/health2 на tick1,27.729ms**; frame1 впервые sampled на tick6,117.509ms. Atlas объявляет contact_column1,12FPS. `timing_probe.gd` и точный log сохранены, проверка exit1. Существующие555 assertions не опровергают новую regression failure.

## Fix tickets

1. **CMB-P02-01 HIGH** — `combat_player.gd:137`, `combat_system.gd:65`, actions_atlas contact_column1. Отложить live hit window до согласованной contact фазы; не задерживать отзывчивое начало animation. Сохранить once-per-target, expiry, LOS/muzzle edge behavior и reset clearing. Добавить no-damage-in-windup/contact regression и повторить native probe.
2. **ART-P02-01 MEDIUM** — weapon overlays `combat_player.gd:188/192` висят у стоп при руке выше. Реальные crop/movie подтверждают. Ввести directional/per-action frame hand/muzzle sockets и согласованный draw order/projection; проверить held melee/ranged во всех4 направлениях. Одного изменения y без проверки руки/пули недостаточно.
3. **ART-P02-02 MEDIUM** — shooter idle→walk меняет высоту каски/корпуса на5–6px (down12→6,up11→6 при sole58). Согласовать позы, сохранить intentional small bob, обновить PNG/source/atlas/evidence.
4. **ART-P02-03 MEDIUM** — defeated guards стоят в paused tinted idle/walk. Дать однозначный defeat cue/transition либо compact prone pose; большой новый action pack не требуется. Обновить actual capture/state check.

Подробный независимый art report и precise frames: `art_subreview.md`. Базовые оригинальные guard designs, overhead/pixel structure и Yakuza identity пригодны; вопрос в action integration/state readability. P01 MEDIUM jitter/LOW atlas-note остаются прежними nonblocking tickets.

Следующий шаг — fixes внутри P02, новые affected hashes/builds/replay и actual CI, затем attempt2 в отдельном reviewer-attempt2 output. Не перезаписывать snapshots попытки1. Повторная проверка обязательна для timing/weapon/defeat fixes и релевантных regressions, не для постороннего P03/кампании. Reviewer code/art не исправлял, commit/push/merge не делал; public release/voice/merge прав это решение не выдаёт.
