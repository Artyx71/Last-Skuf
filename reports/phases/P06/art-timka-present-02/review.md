# ART addendum: Тимка present, настоящие входящие контакты

**PASS_COMPONENT**, frozen replay/source `2780e9e2a8e177e88b892d6abe91d9e141bf04de`. Это дополнение к ART01 (`69ffc…`, decision SHA `573c87c62447f66d38df9a0856a6d8098326b253b68b304f7207e7c647c21ab2`), а не полная P06 или текущая целая ветка.

Reviewer `/root/art_timka_fin_v4` независим от автора. WORK не изменён; Godot/builders/controller/Git mutations/network/generation не запускались. Новые файлы — только ROOT `reports/phases/P06/art-timka-present-02`. Raw photos не читались/не копировались/не передавались. Предыдущие source/native ART решения и diagnostics сохранены.

## Замороженный корпус и изменившаяся coverage

Независимо сопоставлены source inventories native01/native02: ровно два изменения — `game/tests/timka_present_replay.gd` и `tools/verify.py`. Все production bindings ART01 (WORLD/ACTION PNG/metadata/sockets60, character loader/controller/presentation, scene policy, lab) совпали. Поэтому прежнее принятие одежды и шести собственных disengage references во всех направлениях переносится только на этот неизменный corpus; второго визуального исследования всех60 точек не заявляю. FIN sockets и prime по-прежнему не приняты.

Native02 `validation.json`: passed/source_unchanged=true, source2780, actual Input, live137/137, movie104/104,33 PNG. Проверены41 сохранённых artifact digests. При проверке WORK после frozen run1107/1108 записанных source digests всё ещё совпадали. Единственная поздняя авторская разница — `game/scripts/qa/owner_preview_smoke.gd`: recorded1958d164… → currente2fdaf09…; она записана в metrics и находится вне этого ART-компонента. Нельзя объявлять native02 доказательством всего последующего HEAD/нового owner build. Fresh build/Lead проверка нужны отдельно.

Harness прочитан непосредственно. Новые случаи используют production `CombatSystem.start_melee`/`fire`, реальную overlap/contact receipt и собственную attack pose противника при контролируемых стартовых позициях и paused AI. Это исправляет отсутствие такой coverage в native01; они не выданы за полный свободный бой/AI telegraph acceptance. ART01 ручные receive_hit cases не переименованы в Core tests.

## Фактические новые кадры

Просмотрены семь новых native viewport PNG: guard/active/recovery × hurt/fatal и projectile interruption; дополнительно native02 wall и окончательный restart. Каждый Core contact заменяет текущий защитный/шаговый рисунок собственным hurt либо началом падения. Кожа/волосы/худи сохраняют идентичность, нет внезапного чужого тела, невидимой фигуры, отрезанных конечностей или неподвижного «шага», продолжающегося под падением. Короткий контактный эффект/кровь присутствуют рядом с воздействием, не заменяют собственную реакцию тела.

Независимо декодирован реальный MP4 SHA `c2394c6809f6e73045a9e1a123588c6e74732551c0570061aa7bfacbcead23e4`. Запись1113кадров/60fps; отдельно извлечён интервал video n755…963 (209 кадров) с новыми7сценариями. Вручную оценены выбранные whole-actor кадры и все семь `*_ALIGNED.png` последовательностей. Не заявляю ручной просмотр каждого1113 или209 кадра. Подписи video n=tick−1 согласованы с ранее pixel-validated pipeline и фактическими новыми переходами; исходные спрайты не накладывались поверх записи.

Guard hurt: собственная защита → собственный hurt → собственный idle. Guard fatal: защита → первая и вторая собственные fall poses → восстановленный персонаж после R. Active случаи содержат реальные промежуточные walk references перед hurt/fall. Recovery случаи показывают все6 disengage references, затем hurt либо оба fall рисунка и restart. Projectile sequence показывает существующий projectile/weapon cue, прекращение шага и собственный hurt. Во всех новых контактных последовательностях реальные противники изображены рядом и в attack pose; source/damage correspondence поддержан семью production contact records в каждом live/movie run. Точная механика, eligibility, once damage, баланс и invulnerability остаются предметом Gameplay/QA, не подменяются ART мнением.

На финальном restart видна собственная фигура Тимки и рабочая панель present, cooldown сброшен. Верхний/нижний HUD находятся в viewport, подпись не обещает prime/оружие/добивания. В wall capture фигура остаётся целой и перед стеной. Новых обязательных source drawings для этого bounded короткого backstep при данной сборке не выявлено.

## Решение и ограничения

ART must-fix по дополненным incoming-contact visuals отсутствуют. Подтверждается **ART PASS_COMPONENT** для неизменной present art/controller сборки +новой реальной контактной coverage frozen2780. Gameplay Reviewer/QA/Lead должны независимо завершить своё решение; этот пакет не закрывает их предыдущие findings самостоятельно.

Не принимаются owner DEV03 и новый smoke test по одному этому отчёту, full-current-HEAD gate, prime и различия двух контекстов, FIN sockets/finisher mechanics, P06 в целом, readiness/P07/merge, физическая задержка ввода/FPS/balance, новая музыка или аудиослушание, native Windows. Оригинальная запись и native result/log/source inventories связаны хешами; переносимый пакет перечислен в `transfer_manifest.json`, полный воспроизводимый decode cache в Git копировать не требуется.
