# Независимый Gameplay Review: Ryzhik roll

**FAIL** на frozen `407f9a1df6c3d8ed110ab908b234fad4750b622d`. Два исправления обязательны: GP-RYZ-01 — направление UP roll visual entry/exit противоречит реальному движению; GP-RYZ-02 —12 FIN routes не имеют Reduced coverage. Physics/control/once/cancel положительные результаты сохранены, но не заменяют actual movement readability.

Это review одного registered Ryzhik training компонента по P06-CBT-07 и связанным bounded FIN/settings требованиям. Не full P06, не все NPC archetypes/7 героев, readiness, P07, merge/release/export. Reviewer — отдельный от автора агент; Godot/engines/builders/controller/Git/network не запускал, WORK/source/state/queue не менял. Записи сделаны только в этой ROOT review-папке. Все прежние reviews остаются неизменными.

## Источники и проверенные материалы

Прочитаны ground_roll strategy, CharacterPlayer/frame loader, live scene authority, base physics/action/hit и прежний Core/NPC, replay, resources и acceptance specs. Roll зарегистрирован только как dance_step Рыжика; остальные актеры не получают strategy. Core/NPC относительно принятой Timka реализации не изменены. Native frozen inventory1182 files и92 listed artifacts независимо сверены без расхождений. Actual validation/live/movie/source-map и MP4 hashes совпадают с producer handoff; см. `source-inventory.json`.

Author evidence: headless202/202 на96f9 (407 добавляет preview/tool coverage без handler изменений), actual native286/286/84PNG, movie202/202. Во всех трёх2198 trace samples и36 Core contacts. Reviewer независимо пересчитал последовательность фаз, путь и контакты из actual JSON; не считает author summary доказательством сам по себе. Raw native/movie + compact source snapshot сохранены локально, полного проекта/engine/raw AVI копий нет.

Непосредственно осмотрены59 из84 native PNG: все40 четырёх WORLD/ROLL/WORLD последовательностей,12 FIN contacts,6 genuine incoming hurt/fatal и wall-case. Отдельно просмотрены фактические ROLL/FIN source sheets. Из actual MP41280×720/60fps/2215 кадров/36,916667с извлечены8 неизменённых UP-кадров; все осмотрены. Их frame index/PTS не приравниваются к game physics tick.

## Положительные gameplay результаты

F фиксирует live action aim/authority и проигрывает8 собственных рисунков: nominal0,08 windup/0,32 motion/0,16 recovery, cooldown1,2. Обычная locomotion на время roll остановлена; body перемещается `move_and_collide` по active fraction каждого physics tick, без teleport, смены collision layer/mask или immunity. Путь57,6px при180px/s, а не visual-only эффект. Во всех4 directions независимый интеграл `start + aim*180*clamp(clock-0.08,0,0.32)` совпадает с body position с ошибкой<0,002px; все фазы0..7 показаны по порядку. Нет fixture reset внутри измеряемого roll; setup перестановки помечены отдельно.

WORLD/ROLL/WORLD replay использует короткий directional Input до и после действия: walk→idle→roll→idle→walk→idle; это не доказательство непрерывно удержанного движения через весь roll. Actual trace подтверждает возвращение правильных walk/idle направлений без reset. DOWN/LEFT/RIGHT читаются как последовательные tuck/rotation/landing; source/world outfit и ground support в них не дают нового blocking замечания.

Реальный landing control не наносит health damage и не начисляет score: один Core damage0/stun0,45 contact на pose6, reach18/radius13. До pose6 нет damage event; переданный animation callback не наносит урон. Actual landing clock0,416667 во всех прогонах — после nominal0,40 из-за сетки60Hz и накопленного float boundary; pose5 sample может сериализоваться как0,4. Независимая проверка phase intervals учитывает1e-9 rounding tolerance, а actual pose6/contact записан отдельно. Recovery конечен; после него cooldown ещё запрещает F и затем истекает. Wall swept-body case останавливает путь перед collider без tunnelling.

C/revoke/reopen/owner replacement останавливают action и Core job, нет pending control hit/score; direct hurt/death checks отдельно подтверждают нижележащую реакцию. Более сильная проверка действительно присутствует:6 production enemy melee contacts в windup/active/recovery ×hurt/fatal проходят actual Core overlap/once receipt, заменяют roll на own hit/fall и не парируются. После них ability-distance больше не растёт; nonfatal body может двигаться от обычного Core knockback, что не является ghost roll. R очищает cost/receipts/action. Pause держит clock/cost/position; resume завершает конечный путь. Full/Reduced roll outcomes совпадают.

Все12 allowed FIN category×direction routes используют настоящий Input shove с damage0 и stun при baseline NPC HP1, затем NPC physics включён через contact/death. Независимо найдены ровно shove receipt и один lethal finisher receipt на собственном player frame1, score100/hits2; actual checks/contacts подтверждают NPC contact1→corpse2 и отсутствие повторного reward/job. Sharp/firearm остаются запрещёнными несмотря на latent drawings. Это положительное Full-only доказательство, не закрытие GP-RYZ-02.

## GP-RYZ-01 — UP visual direction

Собственная проверка actual native UP0..7, source rowUP и декодированного movie подтверждает blocking неоднозначность, ранее отмеченную ART. При native UP2 body=[280,259,4], при UP5=[280,223,4]: путь направлен к SCREEN TOP. Но entry crown/palms UP2 и return/ground-support UP5 остаются на SCREEN BOTTOM/trailing стороне силуэта. С учётом соседних UP3/4 это выглядит как обратный либо скользящий кувырок вверх, а не ясно направленный вперед roll. Наличие правильного y-интеграла и rear camera не исправляет этот визуальный сигнал.

Особенно показательны native `walk_roll_walk_up_roll2/5.png` и реальные MP4 n335..338 /n347..350. Требуется переработка whole UP2/source26 и UP5/source29, затем просмотр полного UP1→2→3/4→5→6 и обоих WORLD joins на реальном TOP path. Проверять следует читаемость направления/опоры, не только сохранение rear-camera одежды. Это visual-gameplay дефект, не обнаруженная ошибка collision math.

## GP-RYZ-02 — FIN Full/Reduced

В source replay цикл12 FIN находится до изменения reduced_gore. Поздние settings_false/true выполняют только F-roll и сравнивают health/score/damage0-control. Ни один actual FIN contact не маркирован Reduced; сравнение roll0damage не доказывает invariance lethal FIN/реакций/once и Reduced temporal presentation. Поэтому требуются24 mode-bound FIN случая —12 Full +12 Reduced — с реальными option values, тем же Input-earned stun, actual NPC contact1→corpse2, совпадением health/hits/damage/score/kills/recovery/once и native/movie обеих настроек. Подробные action tickets сохранены отдельно.

## Край FIN13, регрессии и границы

Disclosed FIN source cell13 (LEFT environmental, col5) действительно касается local x0: opaque pixels y31/32 подтверждены независимым PNG decode. Actual native environmental LEFT contact осмотрен: новое заметное bleeding соседней клетки не выявлено; palette/hand/front остаются в контактной области. Это не утверждение о свободной alpha border или доказательство наличия padding за границей рисунка. Два edge pixels сохранены в `FIN-cell13-edge-proof.json`; нового отдельного gameplay ticket по ним нет.

Прочитаны actual independent QA result/command files: roll202, roll-layout33, readiness70, Gabar124, Oleg164, counter57, present104, prime214, Timka-layout102 и18 owned-negative проходят. В `independent-QA-regression-results.json` записаны реальные counts/command/result hashes. Это отдельные QA engine runs, не собственные прогоны Gameplay и не финальный QA verdict. Они поддерживают сохранность прежних механик, но не закрывают два visual/settings finding.

Точный новый fix/rerun указан в `action-tickets.json`; старый407 evidence не переписывать. После исправления нужен новый frozen source и delta review UP visuals +12FIN обеих настроек, с сохранением положительной physics/negative matrix. Нельзя выдавать full P06, native Windows, слушание, FPS, hardware input latency или subjective/live-AI difficulty по этим scripted fixtures. Новых gameplay source fixes reviewer не делал.
