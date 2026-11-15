# Независимый Gameplay Review: Timka present disengage

**FAIL — компонент пока не принят.** Frozen source: `69ffc58c7ff2dedd773bd58b137553c3666ad1da`. Движение, фазы, запреты действий, swept wall collision и отмена проходят проверку. Блокирующее замечание GP-TIM-PRES-01 относится к обязательному доказательству отсутствия неуязвимости: существующий зелёный death-check вызывает `receive_hit()` напрямую, а реальные Core contacts во всём present replay отсутствуют. Фактического бага иммунитета в production-коде reviewer не обнаружил; показанного теста недостаточно для его приёмки.

Область — один present/disengage компонент P06-CBT-03 и его negative/cancel условия. Это не приёмка prime, полной present/prime визуальной разницы, всех героев, full P06, readiness, P07, merge, export или CI. Reviewer — отдельный агент от автора, игровой код и WORK не менял, Godot/builders/controller/network не запускал. Все записи сделаны только в этой папке ROOT.

## Исходники и привязка

Прочитаны actor/frame loader/CharacterLab, inherited CombatPlayer, Core, scene policy/catalog, replay/helper/verifier и требования. Сохранён diff от принятого Oleg HEAD f844e4d. Native validation привязан к69ffc58; независимо сверены1108 source hashes и34 evidence hashes, расхождений нет. В report скопированы actual evidence, source snapshot, MP4 и переносимый inventory.

Present конструируется только по registered key `timka_present`; KEY3 проходит production selection. Loader требует WORLD/ACTION с собственными clothing sockets; FINISHER для present не загружается.32 runtime clips:12 WORLD +16 ACTION +4 disengage. Six references на направление: shove0 → walk3,2,1,0 → shove2. Это явное повторное использование собственных рисунков, а не новые source cells и не доказательство отдельного от prime художественного набора. Prime не входит в implemented ability map, отказ сохраняет прежний actor и generation.

F фиксирует aim/scene authority/ability, останавливает обычную locomotion на время действия. Тайминги0,12 guard →0,24 backward move →0,18 recovery, cooldown1,8; скорость140, теоретический путь33,6px. Перемещение интегрирует только часть физического тика внутри active и идёт через `move_and_collide(-action_aim*speed*step)`. Damage jobs и invulnerability flags disengage не создаёт; collision layer/mask не меняются. Новый `_present_action` делегирует все прежние non-disengage действия в прежнюю реализацию. Gabar/Oleg timing/contact body и Core этим diff не изменены; это source-level оценка сохранности, не новый самостоятельный runtime regression на69ffc58.

## Независимый пересчёт фактических traces

Native live:98/98 checks и26 PNG; native MovieMaker:72/72; прежний headless02:72/72. В каждом889 trace samples. `factual-proofs.json` содержит независимую проверку математического пути, каждой фазы, wall-stop и interruption tails; всего2667 samples. Данные не сгенерированы reviewer, движок повторно не запускался.

Для первой полной Input F последовательности в каждом из четырёх направлений повторно рассчитано `position = start - aim * 140 * clamp(clock-0.12,0,0.24)`. Ошибок сверх0,001px нет; фазы sprite/action совпадают с независимой разметкой во всех action samples. Итог33,59993–33,60013px; максимальный шаг2,33335px за tick. Подготовка не перемещает body, active проходит четыре reverse walk рисунка, recovery останавливает body. В live начала/концы полных действий: down21→54, left156→189, right291→324, up426→459. Длительность квантована физикой60Hz: завершение через33 тика (~0,55с) для nominal0,54с.

Заявленная начальная+12px перестановка down fixture и reset placements исключены из measured action path. Это не Input movement и не объявляется отсутствием телепортов во всём fixture setup. Старый headless01 сохранён:70/72, ошибки ожидания36 вместо32 clips и down-path остановка реальным arena divider на25,996px. Headless02 поправляет setup/ожидание; последний native заново подтверждает полный путь и отдельный wall-case.

Wall-case останавливается на11,99629px вместо33,6, body остаётся перед4px collider; тестовая стена — declared QA fixture. Отдельные C/revoke/reopen/owner replacement после clock0,1667 прекращают motion, затем не менее12 последовательных samples сохраняют позицию. Direct hurt/death дают hit/fall и также останавливают шаг. R очищает action/cooldown/distance, не выдаёт prime. Pause имеет15 подряд одинаковых action-clock/position samples; after resume путь заканчивается на33,6px. Cooldown/recovery конечны, повторный F до cooldown отвергается. Full/Reduced результаты совпадают. Нулевые outgoing contacts/damage/score согласуются с отсутствием attack job.

## Native чтение движения

Непосредственно осмотрены все26 native PNG: по6 фаз на4 направления, wall stop и готовность после restart. Направление взгляда удерживается, actor последовательно отходит назад, подготовка/четыре шага/восстановление читаются без мгновенной перестановки. HUD обозначает «Тимка / настоящее», «Мирный Тимка · без оружия и добиваний», F как отступление спиной и C как отмену. Пять finisher categories/equipment и ranged отвергнуты; loaded clips не содержат fire/finish/special. Полная выразительность и различие двух Timka contexts остаются открытым gate.

MP4 — actual1280×720,60fps,904 кадра/15,0667с. FFmpeg извлёк8 неизменённых кадров, все осмотрены; index/PTS перечислены в `video-frame-inventory.json`. Они показывают right guard/reverse steps/recovery и wall segment. Совместно с непрерывным movie trace это подтверждает переходы; отдельные reset PNG сами по себе не считаются последовательностью. MovieMaker фиксирует60fps и не измеряет wall-frame performance или аппаратную задержку.

## GP-TIM-PRES-01: неверный метод проверки no-invulnerability

В `game/tests/timka_present_replay.gd:120–124` hurt/death вводятся прямым `player.receive_hit()`. Это проверяет нижележащую реакцию, но минует collision query, Core receipt reservation, defense dispatch и ordinary incoming contact. Во всех трёх actual present results `contacts=[]`; нет ни одного enemy contact по present Timka. Название зелёного `death_has_own_fall_no_invulnerability` шире фактического доказательства. Исходники не содержат специального иммунитета, но одного static reading недостаточно для запрошенной actual-contact проверки.

Точный исправляющий ticket и критерии находятся в `action-tickets.json`: genuine production enemy melee с удержанным overlap в guard/active/recovery; pre-contact clock/geometry, actual player receipt, health/hits/hurt/fall, прекращение движения и отсутствие counter/score, затем fresh headless/native на новом SHA. Existing direct reaction checks сохранить с точным названием. Это устранимый дефект coverage/acceptance, а не внешний tooling blocker. До нового evidence no-invulnerability portion не принимается.

Субъективное ощущение управления, natural NPC encounter balance, физическая latency, новый audio/listening, native Windows и полный performance gate не оценивались. Более широкие CI/QA вопросы ведёт отдельный reviewer. Решение относится только к текущему frozen source/evidence; будущий исправленный replay требует отдельного отчёта и не переписывает этот.
