# Независимый Lead03 — Тега, закрытие замечаний

**PASS_COMPONENT** для frozen `20cbc322441a80675907bf407f12962778c6c084`. TEGA-L01/L02/L03 закрыты в проверенном компонентном scope: настоящий зарегистрированный предмет, callback geometry, epoch-qualified cleanup, собственные анимации/разрешённые FIN и проверенные once/reset/settings сценарии. Разрешено продолжить Пашу **внутри P06**. Это не полный P06, не переход P07/readiness, не merge, экспорт или релиз.

Lead работал отдельно от автора, только read-only WORK/Git queries и собственные ROOT reports. Godot/native/export/Controller не запускались, source/assets/state/queue/Git refs не изменялись. Все предыдущие FAIL сохранены. Last full PASS=P05; P06 остаётся IMPLEMENTING/attempt1, этот component review03 не расходует новый formal phase attempt.

## Проверка исправлений по фактической причине

Прочитаны точные source и diff c8→20c: меняются только `environment_kick_runtime.gd` и его production replay. `_near_foot` после проверки живого предмета синхронизирует source/object transforms перед реальным physics query. Range12..38, facing.85, foot-circle overlap, LOS, registered identity и lifetime/authority guards сохраняются. `_contact_eligible` по-прежнему проверяет их после обоих внешних callbacks, после presentation и до commit. Существующий CharacterPlayer/Core damage/receipts, арты, sockets и остальные combat handlers побайтово сохранены.

Lead самостоятельно прочитал новый clean probe, его унаследованный observer и raw actual result. Callback только сдвигает Node верстака на `(0,16)` и читает геометрию; он и observer не вызывают production `_near_foot` или `force_update_transform`. Он выполнен **первым после fresh import**, что подтверждает реальный command order QA08.

Внутри callback текущий Nodebody `(308,256)`/shape `(308,250)` уже не пересекает foot Circle8 `(303,234)`, но PhysicsServer body ещё `(308,240)` и world query true. После production Core в **том же tick19** server body стал `(308,256)`, совпал с Node, direct/current/server/world collision false. Actor и prop postcallback deltas0, jobs0, damage/receipts0; masks/exceptions неизменны. Это фактическое причинное закрытие L01/L02, не результат тестового предварительного flush.

Сравнительные15 assertions сохранены без ослабления. Их telemetry имеет раскрытое ограничение: `shape_proof` читает ранние поля, затем последним вызывает production helper, который теперь синхронизирует физику. Это последовательные наблюдения, не один атомарный snapshot. Сами эти15 не доказывали бы правильный Core callsite; вывод опирается на отдельные clean5.

Для L03 `_stop_job` теперь проверяет старые encounter epoch, pinned authority и attackID перед cancel. Lead заново сопоставил raw unchanged reset/newF probe: normal `combat.reset`/`player.reset`/`use_ability` создаёт old epoch6/id1→new epoch7/id1, новый special/job1; afterCore того же tick137 он сохраняется, авторизован, job epoch7/id1. Старый cleanup не отменяет его. В c8 тот же сценарий давал empty/id0/jobs0. Прямой правки cooldown/allocator в probe нет.

Свежие production traces во всех трёх записях подтверждают, что новый F затем проходит собственную подготовку, конечный путь **35.700012px** и recovery без старого ghost-step, лишнего damage/score. Это фактическая дистанция,37.8px остаётся верхним пределом. Sideways case оставляет героя на месте и не выполняет дополнительный ability-step после внешнего переноса предмета.

## Самостоятельная проверка текущих доказательств

При freeze совпали все1242 recorded source keys; сохранены critical20c snapshots и точный diff. От c8 отличаются два объявленных ключа, от первоначального6a — пять, включая прежние три QA/export corrections. Не выдаётся утверждение об общем source-delta только из двух файлов на всём историческом диапазоне.

Lead прочитал/recomputed actual headless06, native03 live и movie JSON: **305/433/305 assertions**, в каждом4792 actor observations,4731 object observations,66 уникальных `(epoch,id,target)` Core contacts,24FIN и12blood poses. В восьми Full/Reduced object-hit paths относительное смещение actor/prop сохраняется (<.02px error), контакт один/environmental damage1/собственная pose1/score0. В24FIN сегментах один earned shove0 и один lethal FIN1, собственный contactframe1, конечные damage_events2/score100, без повторного контакта;12 Full/Reduced равенств сохранены. Шесть real Core incoming hurt/fatal и четыре настоящих nonfatal clothing-hit сценария остаются в replay. Все12 blood TTL положительны; actual live/movie lag≤3px раскрыт,0px не заявляется.

Все128 свежих native03PNG независимо сравнены и byte-exact native02/принятой native01. Это точная связь прежних реально просмотренных пикселей, а не повторный личный просмотр128 изображений. Ранее собственноручно проверенные96 complete-cell master/native RGBA и96 garment sockets переиспользованы только через неизменные asset SHA. Новые latent sharp/firearm разрешения не выдаются, FIN11 border reservation сохраняется.

Из настоящего native03 MP4 Lead самостоятельно декодировал и просмотрел **32 whole frames** через явно обозначенные crops/nearest diagnostic boards: four-direction special0/1/2, четыре FIN contacts, четыре blood poses, четыре границы sideways abort и восемь reset/newF переходов. Видны собственная подготовка, работа стопы/верстака, прерывание бокового случая и законченное новое действие после reset. Внешний adversarial перенос предмета не выдан за игровой teleport. Полный независимый ffprobe decode-count —**4810 frames,80.166667s**,1280×720,60/1. Movie SHA `59c65f1c654ef84cfd79bbbb51090980ac879c544c5e23281f284dffa402fa60`; fixed movie cadence не является host-FPS измерением.

Проверены136 native03 artifact hashes, validation SHA `57da4543532eb476fc066fd026637fe2fc8742a027e6dd029421fb8d0ff72946`, source map `ad485e36292ef14131ec1cbb02390aa1a66ec0b34fc57bbcf83c41e448f89c23`. Actual native producer `b6bf331f70f24a168026aa89842b6110` и independent QA08 `5e6c8e910ada4441a8d16eb5a95218af`: argv/receipt/output-log hashes совпали, exit0. Это не лично повторно выполненные Lead engine jobs.

## Независимые решения и границы приёмки

Формальные ART03 `ef5ec8823424a4409059f0544e7ba3a2379e07dfe2d7bca5e4cd933d7eb5dfbd`, Gameplay03 `905266220c728741b0fb1a93a1b6c8d2400cdeed970092380e65492e7a957916` и QA03 `34b65dc23c7236faf975f690d9f72473cac294826d3658abb2e4d71361220c27` — PASS_COMPONENT на том же20c. Прочитаны настоящие completed reports/findings и исходные proofs. Проверены23 ART portable entries,563 Gameplay local entries,82 QA portable entries и QA FINAL_HASHES. Они дополняют собственную проверку, а не заменяют её голосованием.

QA08 фактически исполнил461/461: clean5, исходные geometry8, comparative15, extended12, negative/custommask26, wall4, production305, counter57, source-bootstrap29, плюс fresh import. Пять прежних independent probe-файлов Lead отдельно сравнил byte-exact с QA02. Старые2297 более широких assertions на6a остаются историческими проверками неизменного shared code, не новыми20c прогонами. Source-bootstrap29, mock routing и metadata tests не названы packaged exports или GitHubCI.

Пересчитаны FINAL_HASHES и каждый portable file старых Lead01/02 (128/67) и QA01/02 (188/78); решения и actual failures не изменились. PASS03 закрывает их замечания на новом SHA, не переписывает историю. Общий original source/art корпус не дублирован: critical code/raw causal proofs/32selected frames локальны, тяжёлые originals и completed subreviews связаны ROOT-relative SHA/bytes. Новых generation/photo/audio assets в этом fix нет; новых privacy/licensing/listening запусков не выдумывается.

Открытых must-fix в этом **bounded** компоненте нет. Следующий разрешённый шаг — Паша внутри текущей P06; при его интеграции нужно актуализировать временные unsupported-selection/preview fixtures, сохраняя atomic-refusal assertions и не помечая готового героя недоступным. Общие sevenhero sound/NPC matrix, полный verifier/ROOT safe handoff и полная phase Lead review остаются обязательными. Новые Linux/Windows-PE exports потребуют своей проверки; native Windows, subjective listening/feel, hardware FPS/latency, полная P06/readiness/P07/merge/релиз здесь не приняты.
