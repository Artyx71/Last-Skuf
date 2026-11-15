# Независимый Gameplay Review: Timka prime и два контекста

**PASS_COMPONENT** на frozen `db84b39711181bb93b6ce58ac4bb7a244dee032b` для registered present/prime gameplay в training sandbox: различимые стойки/ходьба, prime heavy control, clinch, разрешённые V finishers и проверенные отмены/authority. Production handler/art/Core/NPC остаются byte-identical исходному prime3a9ff811; последующая поправка меняет harness/tooling. Это отдельное компонентное решение, не full P06, seven-hero combat, readiness, P07, merge, CI, export или релиз.

Reviewer независимо назначен после автора. Изучены production actor/frame loader, policy/profile, Core finisher/eligibility/contact, NPC reaction, replay/helper и actual traces/PNG/MP4. Reviewer не запускал Godot, builders, controller, Git mutations или network, не менял WORK/source/state/queue. Все записи ограничены этой ROOT review-папкой; прежние reviews сохранены.

## Источники и сила доказательств

Fresh headless03:214/214. Native02 live:304/304,90 actual PNG,3589 trace samples. Movie-only02:214/214,3585 trace samples,49 real contacts и настоящий MP41280×720/60fps/3600 кадров/60,0с. Headless03 также содержит3585 samples и49 contacts. Независимый пересчёт route speed/frames/cycles, damage order/geometry и cancel events сохранён в `factual-proofs.json`. Headless использован как дополнительная численная проверка, не визуальное доказательство.

В момент фиксации независимо сверены1112 recorded source hashes без расхождений,94 listed live artifacts и все listed movie artifacts. Movie source inventory равен live inventory; его ссылка на live validation SHA256 `442e43fdb4019b413835c181c5e1644473ed8b26b6766e6c6f1eb41dc142eaca` совпадает с фактическим файлом. Источники-critical snapshot взят с exact Git commit; полный проект/engine/raw AVI не копировались. Portable manifest содержит локальные evidence/source copies и их hashes.

Ранее native01 завершил live248/248/66PNG, но не movie validation; parent сообщил consumed exit130 операцииe5426991ddf44791b8713777dcccba6e. Причина не установлена, timeout reviewer не объявляет. Восемь старых stance-capture records действительно имели `idle_right`, а8 held ticks не покрывали цикл prime6fps. Эти старые материалы сохранены как история и не используются для приёмки locomotion. В новом harness реальный directional Input устанавливает facing; снимаются idle0/1 и все walk frames с двумя wrap. Native02 закрывает эту наблюдаемую coverage-ошибку.

## Различимость и управление

KEY3/KEY4 выбирают разные registered contexts одного Timka: present/disengage со speed84/32 clips и prime/clinch со speed118/48 clips. Present idle — расслабленные собственные WORLD0/1; prime idle — собственные FIN0 и ACTION0 с поднятыми руками. Present walk использует четыре WORLD2..5, prime walk — два реально иных WORLD6/7 при6fps. Это явное reuse существующих84 drawings, не новые source cells и не ускоренная копия present walk.

Непосредственно осмотрены все40 новых locomotion PNG:16 directional idle +16 present walk +8 prime stride. Все направления фактически правильные; расслабленная и боевая стойки читаются, полные циклы не теряют персонажа/направление. Для каждого из8 routes независимо подтверждены оба idle frame, весь frame set и минимум2 walk wraps. Скорость по каждому соседнему tick соответствует84/118 с ошибкой<0,002px; setup placements вынесены из measured Input. Position меняется плавно; смена fixture/reset не объявляется непрерывным маршрутом.

HUD явно различает «настоящее»/«прайм», present отход спиной без weapons/finishers и prime Space/F/V. Same-actor policy reopen в другой context не выдаёт старому prepared body новые F/Space/FIN или движение. `_prepared_policy_matches_live()` сравнивает exact prepared definition и ability; корректную работу восстанавливает atomic Host switch. Этот новый guard применяется и к Gabar/Oleg; их полного runtime regression этот Gameplay отчёт самостоятельно не выполняет — QA ведёт отдельную проверку. Legacy Yakuza/Core не переписаны.

## Heavy control → настоящий clinch

Prime Space использует собственный prime_strike clip и один Core melee contact: damage0/stun1,25/strong85, windup0,20/active0,12/recovery0,28/cooldown0,9. Сила здесь — control/knockback, а не увеличенный HP NPC. Во всех4 F-cases настоящий active NPC начинает с обычного HP1, после Space остаётся HP1/hits1/stunned. Входящие/исходящие контакты идут прежним Core, не animation callback.

F разрешён лишь с пустыми руками по реально vulnerable stunned/knockdown target, с range/facing/LOS и live authority. Сохраняется категория Core job unarmed; собственный special clip использует contact из original FIN7. Reservation проходит до cooldown2,4/ability-use cost; failed healthy/range/facing/wall/tool не тратят стоимость и не создают job. Успешный цикл:0,48 windup/0,12 active/0,38 recovery.

Для каждого F-направления независимо найдены ровно два исходящих receipt: Space damage0 на clock0,20 и один lethal F damage1 на clock0,483333. До F-contact damage_events остаётся1 от Space и score0. На damage tick player action/sprite frame1 и special правильного направления; NPC contact frame1, далее dead hold2. Расстояние до victim после реального knockback ~31,8889px в пределах range35. Никакого нового damage/reward в recovery; итог kills1/score100/hits2. Повторный callback отвергается. Clinch конечен: guard→contact→recovery→idle, cooldown восстанавливается.

Осмотрены12 новых F PNG:guard/contact/recovery во всех4 направлениях. Контактная поза, направленность и NPC reaction согласованы с damage tick; нового point-pose/range/rhythm дефекта не выявлено. Это короткий controlled grapple/finisher, не утверждение о человеческом ощущении живого боя.

## V, отмены и реакции

По12 комбинациям unarmed/blunt/environmental ×4 directions заново проверены real Space stun, разрешённое equipment, соответствующая own category/direction pose, единственный lethal receipt и reward. Environmental обращается к настоящему registered/enabled training bench, а не к выдуманному target. Все12 contact PNG осмотрены; actual checks фиксируют NPC frame1 на contact и dead/frame2 после. Полный archetype-wide P06-CBT-09 этим не принимается.

C, движение, revoke, reopen, restart отменяют pre-contact clinch без finisher receipt/reward. Genuine incoming Core melee от второго NPC отдельно вызывает hurt/death: один incoming damage1, никакого parry/контрудара, pending clinch убран, score0. Cost отменённого уже резервированного F не возвращается; R очищает cost/receipts. Full/Reduced сохраняют одинаковые механические outcomes. Переключение контекста не переносит prime grants на present. Настоящие контакты здесь контролируются fixture; где AI остановлен, это явно видно в replay, естественная сложность encounter не измерялась.

## Временная native проверка и границы

Всего непосредственно осмотрены64 из90 native02 PNG:40 locomotion,12 F phases,12 V contacts. Из настоящего MP4 извлечены20 неизменённых кадров; все осмотрены — повторяющиеся present/prime walk, F preparation→contact→recovery, incoming hurt/death и environmental UP contact. Frame index/PTS перечислены отдельно и не приравниваются к game physics tick. В сочетании с непрерывным trace это подтверждает actual transitions; reset screenshots сами по себе переходами не считаются.

Python completed-live cache validator получил отдельное MEDIUM QA замечание к rebound toy fixtures уже после этих actual runs. Этот Gameplay verdict не принимает helper/cache safety, его будущий fix/new HEAD или reuse в новых jobs. Actual02 data здесь сверены непосредственно по source/artifact hashes и actual runtime content; Lead/QA отдельно свяжут tool-only fix и fresh03. Новая ART garment/source приёмка также остаётся отдельным verdict.

Открытых Gameplay defects внутри проверенного компонента нет. Отдельных remediation tickets не требуется. Не измерялись аппаратная input latency, субъективный gameplay feel/live AI difficulty, wall-frame FPS, новый audio/listening, native Windows или campaign readiness; не принимаются full P06 и merge/export. Earlier present PASS/FAIL history не переписывается.
