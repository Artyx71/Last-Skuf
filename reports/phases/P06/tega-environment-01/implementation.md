# Тега — проверяемый кандидат P06

Исходный игровой коммит: `6a0224e016e53e13ddb1e6fde747b66e7f75447b`. Отчёт автора, не решение Lead.

Собственные WORLD32/ACTION32/FIN32: 96 рисунков, 56 клипов, 96 аннотаций одежды. Независимые SOURCE ART: ACTION ef71ab4c, FIN bb18d080. Все генерации, неудачные упаковки и технические операции над целыми фигурами сохранены; ручной дорисовки частей тела нет. В латентной LEFT sharp позе 11 остаётся один крайний пиксель ножа, исходник полный. Категория запрещена. Общий PASS по отступам не заявляется. Исходные кандидаты sockets и шесть поправок с брюк на худи сохранены отдельно.

F двигает настоящий зарегистрированный верстак. Короткий foot overlap, LOS/facing/range, pinned object/authority/epoch, swept движение предмета и героя. Стена или первый NPC останавливают предмет; только реальное столкновение передаёт один контакт в прежний CombatSystem. Damage1/stun0.55 без finisher reward. Windup0.18/active0.18/recovery0.32/cooldown2.4, максимум37.8px. Параметры реализации не доказывают субъективное ощущение игры. Маски/exceptions восстанавливаются синхронно до событий; после foot-audio callbacks полномочия перепроверяются. Reset возвращает реально сдвинутые предметы.

Фактические проверки:

- import01 PASS: ровно пять ожидаемых UID/import файлов.
- headless01: 140 assertions без провала, общий FAIL из-за freed-object SCRIPT ERROR. Исправлено проверкой Variant до приведения к типу. headless02: 140/140 без ошибок.
- headless03: FAIL до assertions из-за вывода типа Vector2 в replay. Исправлен явным типом.
- headless04: 296/296, 4631 trace, 66 Core contacts, 12 clothing records.
- native01 live: 424/424 и 128 реальных PNG.
- native01 MovieMaker: 296/296, MP4 4649 кадров / 77.483333s. Live walltime78.625s, movie render148.579s — это не измерение FPS/latency игры.

Проверены object hits4dir×Full/Reduced,24 earned finishers3category×4dir×Full/Reduced, incoming Core3phases×hurt/fatal, реальные nonfatal blood→special0/1/2 в4dir, callbacks cancel/revoke/reset/disable/free/directcancel/unregister/replace, windup/active interruptions, LOS/стена/пауза/R. Урон совпадает с собственным кадром1, NPC finisher1→corpse2, повторного урона/награды нет. Clothing live lag≤3px при движении раскрыт.

Индивидуальные звуки всех7 героев и полная NPC matrix ещё открыты. Здесь переиспользуются существующие category SFX; фактическое прослушивание новых звуков не заявляется. Host FPS/hardware latency, native Windows, полный P06 и FULL Readiness не приняты. Независимые runtime ART/Gameplay/QA ожидаются. Владелец предварительно одобрил Тегу и следующего Пашу. DEV05 остаётся прежней пользовательской сборкой; Тега в неё ещё не добавлен.

Дополнительное независимое QA выполнено в изолированной копии через ROOT Controller, последовательно. Свежие исходники1242 файлов проверены до/после. Пройдены Tega296, combat43, contact48, P04G695, Yakuza authority21, restart68, Gabar124, Oleg164, present104, prime214, Ryzhik311, readiness74, Timka layout102, roll layout33. Первый Oleg feedback тест51/57 использовал старую недоступную клавишу6; в0840268 она заменена7, точечный повтор57/57. На084 также source owner smoke29/29, это не packaged export. Только3QA/export файла изменены после6a, productionruntime/art без изменений.

Первые собственные QA probes20/23 (отсутствовало подключение сигнала в самом QA) и28/29 (неверное ожидание нулевого общего пути перед препятствием) сохранены. В новых отдельных evidence исходные23негативных случая прошли, custom mask/nonempty exceptions/reset3/3 прошли, точечный actor-only wall4/4 доказал допустимый первый путь0.700012px и отсутствие последующего движения. Это исправление QA измерения, не снижение игрового критерия: оба тела останавливаются при первом препятствии.

Независимый ART PASS_COMPONENT:75e2a6fc (96поз/96sockets/128PNG/469фактически просмотренных кадров). Фактический свободный путь при60Hz около35.7px;37.8px — верхний предел. Автор не выставляет итоговую приёмку; Gameplay/QA/Lead финализируются. Пакет ART дляGit55файлов6.9MB,1075отдельных декодированных кадров остаются в ROOT cache сSHA.
