# P06 — Gabar controller remediation preflight v2

Статус: **GP_GABAR_01_02_CLOSED_SCOPED_INTEGRATION_ONLY**. HEAD `9b6ac50440670759d0131debf32f4e9bf774061f` независимо прочитан из metadata files без Git commands. Reviewer `/root/gameplay_review_p06` прочитал actual source, targeted replay и regression/unit logs, пересчитал inventories. Godot/controller/tests/Git/build/generation не запускались; source не менялся. Записи только versioned gabar-controller-preflight-v2.md/json; исторический v1 сохранён. Это не полный P06, native gameplay/ART/real-time feel/FPS/export approval.

## GP-GABAR-01 — CLOSED

`CharacterScenePolicy.action_authority:40–43` теперь выдаёт отдельный scene snapshot actor/context/fixture/generation/owner instance, без случайной зависимости special от выбранного finisher tool. `CharacterPlayer._play_action:106–109` фиксирует его для shove/special и отдельно фиксирует ability_id для special. `_action_authorized:111–114` сравнивает live snapshot и capability; `_physics_process:67–72` отменяет action до advance/travel, а `melee_phase:150–156` повторно отказывает до Core contact.

`CombatSystem:156–159` вызывает optional authorize_melee_contact **для каждого recipient** в shape-query loop, до _apply_hit. Поэтому invalidate в callback первого contact не оставляет разрешения второму recipient в той же physics iteration. При отказе pending attack удаляется. Legacy Yakuza/enemy без нового optional method сохраняют прежний path. Damage/receipts/epochs/score по-прежнему выдаёт общий Core; renderer/audio не добавляют authority.

В actual Input replay проверены Space/F×invalidate/reopen до windup contact, ноль damage/travel от pending action; first real active contact→same-key generation change→late second target получает0hits; contact callback invalidates policy между двумя recipients→ровно1hit total и attack очищен. Это закрывает исходный ghost-hit сценарий и same-tick reentry. Snapshot содержит owner/context, так что source logic также отзывает owner/context replacement; targeted Gabar replay проверяет invalidate/reopen и callback, не выдаётся за отдельный production Timka replay.

## GP-GABAR-02 — CLOSED для normal registered selection

`CharacterPlayer.prepare_art:19–29` выполняет тот же complete three-sheet+clothing_socket construction, что configure; bind_policy отдельно проверяет identity (`:31–34`). `CharacterLab.select_fixture:25–35` сначала создаёт candidate и вызывает именно prepare_art. При отказе освобождается candidate и возвращается false, ещё до combat.reset/invalidate/remove old actor. После подготовки идут reset→invalidate→oldremove→registered open→bind prepared candidate→add/reset (`:36–53`). Повторное чтение atlas после удаления current actor не требуется; configure side effects не спрятаны в assert.

Actual replay сохраняет existing actor/epoch при unready Olezhka и unknown fixture, отвергает supporting configure и успешно переоткрывает готового Gabar с новым epoch/authority. Frames unit проверяет complete composite и required authored clothing metadata. Source control flow прямо устраняет mismatch full readiness versus preflight. Отдельного live missing-socket selection fixture в replay нет; closure опирается на общую prepare_art branch, реальные unavailable/complete cases и951 atlas/socket unit checks, а не на вымышленный negative runtime case.

Startup _create_player всё ещё считает packaged Gabar assets обязательными и использует assert(configured). Это не silent Yakuza fallback и не прежний mid-selection defect; graceful corruption/missing-boot-asset screen здесь не реализован/не принят. Unexpected registered open/bind failure после подготовки переводится в blocked и требует recovery. Shipping robustness этих внешних failure paths нельзя считать доказанной этим bounded review.

## Дополнительная integration coverage

Actual Input replay теперь непрерывно держит run key через run→special→recovery→run в четырёх направлениях без fixture teleports между этапами. Physics trace bounds подтверждают ограниченное перемещение; этого недостаточно для subjective motion/readability. Проверены C/incoming hit/death до special contact, конечные cooldown/recovery, real earned Space stun→V contact для3categories×4directions, cancellation/policy revoke/reset, retry restoring speed/health/cooldown, visual-only pixel snap и Full/Reduced/VHS/shake/flashes/decals outcomes с одинаковыми hit/state/score/distance/use count/collision layers. Held death достигает реального fall frame1, а не несуществующего третьего рисунка. Pause во время special, полный process-reload и все будущие геройские actions ещё требуют отдельных production evidence.

## Привязка evidence к source

`gabar-combat-03/live.log` и result: **124/124**, actual Input, headless/fixed-fps60, exit0,37 contact events,0 rendered captures/no movie/no exports. Все4 artifact hashes из validation.json совпали. Reviewer независимо сравнил **652 source hashes** (game/tools/source_art characters) с текущим WORK при чтении и перед записью отчёта: **0 mismatches**. Значит просмотренный current source content соответствует run inventory. Авторское source_unchanged=true — before==after во время run; current match проверен независимо.

Run validation.source_head содержит **f14ad4765ac0e9446668a50e90ab8f770edb62e2**, потому что запуск был до нового commit. Это не exact-Git-HEAD execution на9b6ac504; report различает Git label и hash-bound source contents. Нового exact-head native/CI/Lead decision этим не возникает.

Прочитаны P06 component logs: profile61, scene policy99, policy integration57, dialogue22, Frames951 — **1190/1190**, пять reported exits0, no ERROR/WARNING. Их отдельный inventory **378 entries** также совпал с current source. Прочитаны все25 controller-regression command logs и validation:25reported exit0/true, без ERROR/WARNING; включены movement34,combat43,AI32,contact48,P04G695,CH01 exit paths и story. Этот regression receipt не содержит отдельного source_hash inventory: он подтверждает прочитанные авторские команды/логи, не самостоятельный exact-head freeze. Hashes ключевых receipts/logs сохранены ниже в JSON. Reviewer ничего не перезапускал.

Новых HIGH/MEDIUM findings в исправленных controller/contact/switch paths не найдено. Закрыты две исходные bounded findings. Пять других bodies/abilities, actual native actor/target/readability/socket ART, wall-frame performance, sandbox/CH01 full save isolation, Windows/Linux exports и независимые полные gates остаются pending. Полный harness tools/verify_p06.py и phase PASS этим отчётом не заменяются.
