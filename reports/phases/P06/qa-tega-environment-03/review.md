**PASS_COMPONENT — техническое закрытие `TEG-Q03` / Lead `TEGA-L01` и `TEG-Q04` на `20cbc322441a80675907bf407f12962778c6c084`.** Это scoped QA Теги; P06/readiness/campaign/merge/release не принимаются. Исходные QA01/02 FAIL-решения сохранены, не заменены новым verdict.

Production исправление — два файла относительно c8: resolver и его replay. `_near_foot` синхронизирует текущие source/object transforms перед spatial query; `_stop_job` сравнивает encounter epoch, pinned authority и numeric ID. Сам QA не менял production. Сохранены 1242 source SHA, отдельная физическая ROOT-копия game/tools/source_art без private фото/ссылок на mutable WORK, pinned copied Godot и isolated XDG/save profiles. Последовательный job08 запустил родитель через единственный Controller.stage; сам reviewer не запускал Controller/WORK engines и не менял Git. Нормальные stage/state updates родителя разрешены, глобальная неизменность ROOT state не заявляется.

Actual job08 — fresh import и девять headless suites, **461/461 assertions**:

| Проверка | Результат |
|---|---:|
| Новый clean unforced geometry observer | 5/5 |
| Исходные far-transform assertions | 8/8 |
| Direct geometry/PhysicsServer/reset-epoch qualification | 15/15 |
| LOS/footshape/new-shove control | 12/12 |
| Metadata/lifetime/callback/masks/exceptions/reset negatives | 26/26 |
| Actor-only wall boundary | 4/4 |
| Production Tega replay | 305/305 |
| Oleg counter HUD | 57/57 |
| Source bootstrap headless smoke | 29/29 |

Пять прежних независимых probe-файлов скопированы **byte-exact**, assertions не ослаблены. Их SHA и production inputs проверены job до/после; все совпали. Entry SHA `0e9841ad0cff83fe3871e26caa25f9dd6267c2a9bab43bd1242b780541597360`, manifest `580393bfb35a269373472323c45b690d1cbc271c455d4ca977599aa843ea0d91`; после PREPARED они не менялись. Все engine calls завершены, реальные receipt/log SHA сверены.

`TEG-Q03` закрыт отдельной **невмешивающейся** пробой. Clean callback только меняет `bench.position += (0,16)` и читает Node/PhysicsServer/direct Shape2D/world query. Он не вызывает `_near_foot` или `force_update_transform`. Непосредственно после callback direct collision с актуальным Node shape уже false, Node body y256, PhysicsServer ещё y240 и world overlap true. Observer priority 1000 **после Core того же tick** видит PhysicsServer y256, согласованный с Node, world overlap false, actor/prop delta0 и jobs0; masks/exceptions/receipts не меняются. Значит синхронизацию и отказ выполнил production postcallback path. Эта чистая проба выполнялась первой после import, раньше других instrumented cases.

Важное ограничение сравнительных 15 assertions сохранено явно: старый `shape_proof()` сначала снимает Node/PhysicsServer/direct collision/world query, затем **последним** вызывает production `_near_foot`. Новая версия helper намеренно синхронизирует физику, поэтому ранние поля словаря описывают состояние до helper, а поздний bool может описывать состояние после него. Эти telemetry fields не объявляются одним атомарным snapshot. Сравнительный15 сам по себе не доказывал бы расположение вызова в Core; поэтому clean5 обязателен. Это соответствует документированному поведению накопленных transforms и явного physics update у [`CanvasItem.force_update_transform`](https://docs.godotengine.org/en/stable/classes/class_canvasitem.html#class-canvasitem-method-force-update-transform). Документация проверена read-only public GET, без отправки проекта/фото.

`TEG-Q04` закрыт тем же неизменённым фактическим сценарием: callback делает нормальные `combat.reset()` + `player.reset(current_position)` + `use_ability()`, без прямого изменения cooldown. Новый F получает новый epoch при повторном numeric id1. Observer после Core теперь сохраняет `special`, новый epoch/id1 и ровно новый job1. В c8 тот же probe показывал action empty/id0/jobs0. Дополнительный listener с новым shove также остаётся авторизованным с реальной Core reservation. Production replay проверил, что новый F затем заканчивает настоящее ограниченное движение. Старые immediate/queued free, reset/revoke/body replacement, metadata atomic refusal, cooldown и custom masks/exclusions/reset cases прошли.

Свежие native03 автора проверены по настоящим файлам: **136 artifact SHA, 1242 source SHA exact20c, 128 PNG, live433/movie305**, без ошибок в логах, оба engine exit0. Root operation `b6bf331f70f24a168026aa89842b6110` завершён, receipt/log SHA совпали. Validation SHA `57da4543532eb476fc066fd026637fe2fc8742a027e6dd029421fb8d0ff72946`, source inventory `ad485e36292ef14131ec1cbb02390aa1a66ec0b34fc57bbcf83c41e448f89c23`. MP4 SHA `59c65f1c654ef84cfd79bbbb51090980ac879c544c5e23281f284dffa402fa60`; saved ffprobe — 4810 кадров/80.166667s. QA видео не декодировал повторно. Две actual native PNG просмотрены и сохранены для технической интеграции, не для ART/feel приёмки всех кадров. Runtime durations81.24s/155.966s и movie frame count не являются измерением host FPS.

Numeric audit собственного production305, native и movie подтвердил в каждом 66 уникальных `(epoch,id,target)` Core tokens и 24 FIN (12 Full/12 Reduced), собственные contact frames. Актуальные settings/clothing/incoming/once cases остаются в production replay. Арт и общий CharacterPlayer/CombatSystem не менялись: c8→20c отличаются два ключа, 6a→20c — пять. Прежние 14 зелёных suites/2297 assertions на6a используются только как связанная hashes история неизменного общего кода, **не как новые20c запуски**. После узкого Tega resolver fix их не повторяли.

Все 188 portable файлов QA01 и 78 файлов QA02 заново rehashed и совпали. Их исходные FAIL-вердикты, actual negative traces и диагностические ошибки QA сохранены. Privacy11/7probes и mocked CI/export-metadata results относятся к прежнему QA01 на соответствующих неизменных файлах; свежие такие проверки здесь не заявляются. Source bootstrap29 остаётся проверкой исходного проекта, хотя общий harness JSON называет scope PACKAGED; нового exported build reviewer не запускал.

Blocking findings в этом компонентном scope закрыты. Независимые ART/Gameplay/Lead принимают свои решения по реальным evidence. Новые packaged Linux/Windows-PE exports требуют отдельной проверки; native Windows, hardware FPS/latency, субъективное аудиопрослушивание, новое качество музыки, вся матрица семи героев и полная P06/readiness/merge/release здесь не приняты.
