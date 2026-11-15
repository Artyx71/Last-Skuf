**FAIL_COMPONENT — независимый технический QA Теги.** Блокирующее замечание `TEG-Q03` (Lead `TEGA-L01`): после синхронного аудиоколбэка runtime повторно проверяет идентичность и полномочия, но не фактическую досягаемость предмета. До исправления компонент не принят. Полная P06, readiness, merge и release не разрешаются.

Проверены runtime/арт из `6a0224e016e53e13ddb1e6fde747b66e7f75447b` и точечные исправления тестов/preview в `084026895f2ffb1b51b438cbf87e8a97440d7b77`. Независимо сохранены 1242 source SHA и отдельная физическая копия game/tools/source_art без raw-фото и изменяемых ссылок. Godot скопирован и сверён с lock: `8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e`. QA не менял WORK, игру, Git или каноническое состояние. Родитель запускал подготовленные QA entry points через единственный канонический Controller.stage; 22 engine calls прошли последовательно в отдельной ROOT-копии с отдельными XDG/save-профилями. Эти авторизованные stage-записи меняли состояние Controller обычным образом: утверждения о неизменности всего ROOT/state нет.

`TEG-Q03` квалифицирован настоящим Godot Input replay, а не только чтением кода. При первом foot-audio событии listener перемещает **тот же включённый зарегистрированный** верстак на +100 px либо героя на −100 px. Расстояние становится 128 px. Physics observer с priority 1000 после Core измеряет состояние **того же physics tick**, сверяя tick с записью непосредственно внутри callback. В обоих случаях герой и предмет затем сдвигаются ещё на `0.70001220703125` px, а job остаётся активным. Clock `0.183333333333333`, pose 1; ticks 19 и 48. Урон/receipts остаются 0, masks 1/6 и exclusions не меняются. Фактического удалённого попадания в этих пробах не было; оно не заявляется. Результат `callback-geometry-05`: **6/8, exit 1**. `result.json` содержит полные координаты до/после, `run.log` — обе ошибки; source integrity сохранилась.

Причина видна в `environment_kick_runtime.gd`: до callback вызывается `_near_foot`, после `_wall_contact` и `make_noise` проверяются membership/`_valid_job`, где нет spatial eligibility. Требование P06-CBT-08 включает настоящий доступный объект, range/facing/LOS. Нужно повторить **полную** проверку foot overlap/range/facing/LOS после внешних callbacks и до движения/контакта, сохранив lifetime/authority/registry guards; безопасно отменить утративший eligibility job. Затем нужны новые source freeze, фактические отрицательные пробы и актуальные компонентные/native evidence. Reviewer код не исправлял.

Свежие независимые headless результаты на 6a:

| Проверка | Результат |
|---|---:|
| Tega strengthened Input replay | 296/296 |
| Базовая боёвка | 43/43 |
| Contact timing | 48/48 |
| P04G impact/finishers | 695/695 |
| Yakuza finisher authority | 21/21 |
| Restart | 68/68 |
| Gabar | 124/124 |
| Oleg | 164/164 |
| Timka present | 104/104 |
| Timka prime | 214/214 |
| Ryzhik roll | 311/311 |
| Readiness/refusal | 74/74 |
| Timka layout | 102/102 |
| Roll layout | 33/33 |

Это 14 зелёных suites / 2297 assertions, включая Тегу, плюс fresh import. Они подтверждают перечисленное поведение, но не покрыли обнаруженный позднее callback geometry gap. Полный тест всей фазы/удалённый GitHub CI не выполнялся.

Первый actual Oleg HUD regression дал **51/57, exit 1**: тест недоступного героя нажимал KEY6, который теперь выбирает Тегу. Автор в 084 заменил только KEY6→KEY7, оставив assertions. Точечный независимый повтор дал **57/57**. `TEG-Q01` закрыт; старый FAIL сохранён. В том же 084 исправлен будущий DEV smoke: реальный выбор Теги/Input F/движение верстака/masks, затем отказ недоступному Паше KEY7. Actual source bootstrap headless дал **29/29**. Это запуск проекта из исходников, хотя общий harness JSON называет scope PACKAGED; он **не доказывает** экспортированный билд. `TEG-Q02` закрыт только для source/wiring. Новый actual packaged export остаётся отдельным gate. Source delta — ровно три файла: counter replay, preview smoke, export helper; остальные 1239 ключей, runtime и арт совпадают с 6a.

Дополнительные независимые пробы: metadata corruption/missing ACTION/FIN/wrong identity/stale sockets с сохранением настоящей pending Gabar action/options; чужой strategy instance; immediate/queued free самого игрока из audio callback; атомарная замена активного тела; повторное открытие authority; cancel→retry без refund. Финальные **23 assertions** прошли. Ещё **3** проверки подтвердили реальное движение при custom mask 74 и заранее непустых peer/посторонних exclusions, их точное восстановление и R-transform restoration. Actor-only wall проверен отдельно **4/4**: ray/foot target остаётся валидным, sweep героя блокируется, sweep предмета свободен; допустимый первый частичный шаг 0.700012 px предшествует actual `actor_blocked`, затем оба тела остаются неподвижны 45 ticks без урона. Это не заменяет отрицательные callback geometry пробы.

Собственные диагностические ошибки сохранены честно. Первый QA probe **20/23** пропустил исходное подключение audio signal, поэтому первый immediate-free случай не исполнился; второе задание добавило соединение. Второй probe **28/29** ошибочно требовал нулевой суммарный путь до actor-only wall; отдельный observer установил допустимый частичный шаг перед блокировкой. Это ошибки QA fixtures, не product bugs. Файлы и реальные первые результаты не перезаписаны.

Независимо пересчитаны фактические native evidence автора: 136 artifact SHA, 1242 source SHA, **128 PNG**, live **424/424**, movie **296/296**. Saved ffprobe указывает 4649 кадров; сам QA повторно видео не декодировал. MP4 SHA `5546870556a6500ec9c45b8ada00f3ef4fda717e2a46965ec5917695d22c1cb7`. Просмотрены две реальные PNG для проверки интеграции; это не художественная/feel приёмка всех кадров. Actual source hash map native01 совпал с независимым 6a inventory. После изменения трёх файлов 084 это исторический валидный runtime corpus, а не current-source cache.

Numeric audit собственного headless, native live и movie: в каждом 66 уникальных `(epoch,id,target)` Core tokens; 24 FIN = 12 Full + 12 Reduced, собственная contact pose 1, финальные trace damage_events=2/score=100, 12 Full/Reduced outcome checks; 6 настоящих incoming Core hurt/fatal cases во всех трёх фазах; 12 clothing socket/TTL proofs; 8 audio callback pairs. Full/Reduced связаны с реальными вызовами OptionsStore в frozen replay; отдельный независимый mode-observer здесь не запускался. Эти результаты не подтверждают отсутствующий callback spatial guard.

Чистые Python проверки: **16/16** predicate cases на копиях реальных JSON (scope/strict booleans/renderer/mode/check failures/presence), **3/3** actual common verify.main routing/exit/fatal-log propagation с замоканными subprocess и **3/3** actual export helper metadata cases с замоканными export/smoke. Новый mapping даёт 6 fixtures/5 heroes при обоих успешных профилях, исключает только Тегу при недостающем Windows Tega check и даёт пустой список при failed Windows smoke. Это не actual CI/export, и predicate tests не объявляются полной семантической валидацией произвольных trace JSON.

Read-only privacy: канонический manifest **11 references/0 errors**, canonical Git audit **7 probes, 2332 tracked, 0 errors**, WORK Git audit **7 probes, 13548 tracked, 0 errors**. Raw фото не копировались и не отправлялись. Проверены реальные durable receipts/log SHA пяти независимых QA stages; собственные первоначальные process identities завершены. P05 остаётся PASS, P06 IMPLEMENTING/formal attempt 1. Исторические headless01 FAIL (140 assertions, но freed typed argument SCRIPT ERROR/exit0), headless03 parse FAIL/0 assertions, а также собственные FAIL сохранены. Проверяемые прежние QA decisions Ryzhik/Timka не изменены.

Нет разрешения на полную P06, readiness/campaign, merge/release. Не проверены новое музыкальное качество/фактическое прослушивание, уникальное audio всех семи, hardware FPS/latency, native Windows и новый packaged Tega export. ART/Gameplay/Lead принимают свои отдельные решения. Следующее действие — авторское исправление `TEG-Q03` и новый независимый closure packet; этот FAIL-пакет остаётся неизменным.
