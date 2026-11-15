# P06 — атомарное расширение персонажей

База be4d59e9f68f32833719c82dee36bf731bb43ad0, P05 PASS/MERGED (PR10). Владелец разрешил ограниченное продолжение «давай дальше?». Граница P06; P07/release не запускаются. Один автор/билдер, независимые read-only ART/GAMEPLAY/QA/Lead; максимум три попытки review. Это план, не свидетельство готовности.

1. **P06-01 / contract**: CharacterCatalog и SDD, точные canonical/context/weapon constraints, отдельный sandbox. Сохранённый scope review reports/phases/P06/scope-review-initial не является PASS.
2. **P06-02 / portraits**: девять оригинальных наборов из своих проверенных фото: gabar,olezhka,timka,ryzhik,tega,pasha,kaban,ellana,elya. По пять эмоций; motion только при наличии дополнительных настоящих рисунков. Built-in image_gen; raw остаётся private. Каждый master/prompt/hash/provenance сохраняется; ART сравнивает с правильным фото локально.
3. **P06-03 / actors**: шесть новых согласованных 4-way world/action/finisher sheets. Референсный бюджет 96 source cells/герой, кроме утверждённого Timka84 (WORLD32/ACTION28/FIN24; specs/CHARACTER_EXPANSION_SPEC.md): world32 (idle2/walk4/run2 ×4), action32, finisher32. Shared/mirrored/exact-duplicate подсчитываются отдельно; не выдавать ссылки за уникальные рисунки. Дополнительные сложные переходы требуют реальных кадров.
4. **P06-04 / integration**: composable catalog/frames/factory и способности через существующий CombatSystem; персонажный resolver не мутирует глобальные Yakuza definitions. Пять финальных категорий имеют отдельные контакты, eligibility ограничивается equipment/context. Только CombatSystem выдаёт damage/score.
5. **P06-05 / presentation**: настоящий selectable character sandbox с Input, отдельным DialogueDirector viewing-state и девятью говорящими/пятью эмоциями. Принятые non-identifying bleeps переиспользуются явно; новые голоса/музыка не заявляются. CH01 и его незавершённый диалог сохраняются, включая restart процесса.
6. **P06-06 / verification**: headless catalog/context/eligibility/once ledger/regressions; native Input/captures всех направлений/action/special/finisher/cancel/reset; реальные Linux/Wine exports с честным native-Windows NOT_TESTED. Full/Reduced/settings не меняют физику. Wall-frame performance измеряется отдельно от physics delta.
7. **P06-07 / independent gates**: независимые ART/GAMEPLAY/QA + Lead на frozen SHA/base, обязательный CI exact SHA; FAIL→конечные исправления, BLOCKED→точная причина. Только полный PASS и свежие GitHub protections/checks/threads разрешают conditional squash. После MERGED обновить authority, остановиться на P06.

## Canonical mechanics

| Hero | Отличимая способность | Ограничения / finisher style |
|---|---|---|
| Gabar | короткий направленный силовой выпад с конечным recovery | быстрые силовые контакты; без телепортации/неуязвимости |
| Olezhka | тренировочный counter в ограниченном окне | learned technique gated training; нет внезапных способностей |
| Timka | disengage в peaceful_present; clinch в athletic_prime | prime только из доверенной scene fixture; unknown context запрещает силу; present мирный |
| Ryzhik | управляемый dance-step с читаемым путём | акробатический контакт требует реального промежуточного движения/кадров |
| Tega | использование реального доступного объекта окружения | нет magick/shockwave; cannon dream-only, не часть P06 |
| Pasha | мобильный рискованный ranged приём с ammo/cooldown | конечный cost/recovery, без случайного обязательного самоубийства |

Kaban/Ellana/Elya supporting, не playable. Ellana — партнёр Yakuza, Elya — Timka. Kaban/PRIME fictional. Не придумывать tattoo text/осетинские переводы. Yakuza остаётся прежним слабым персонажем. Новые герои в sandbox не выдают сюжетные unlocks и не создают 20 фиктивных глав.

## P06-TIMKA84 — утверждённая зависимая подзадача

1. Зафиксировать owner approval в SDD/authorization/queue; сохранить предложения/старые FAIL.
2. Реализовать allowlisted schema2 compact packing/loader/adopter, строгие отрицательные tests и per-layout socket count; остальные герои schema1 без изменения.
3. Подготовить WORLD32/ACTION28/FIN24 source candidates целыми клетками без placeholders. Исправить environmental family/readability. Получить fresh independent source review каждого необходимого набора и только затем explicit version migration с rollback snapshot/hash binding.
4. Раздельно реализовать peaceful_present disengage и athletic_prime clinch на готовых context resources, через существующий controller/Core. Readiness registry разрешает только реальные обработчики. Отказ сохраняет текущие authority/jobs/receipts/options.
5. Реальные Input/native доказательства двух контекстов, ART/GAMEPLAY/QA и последующая полная Lead приёмка P06. Scope approval не выдаёт PASS/merge.

## P06-CBT — уточнение всех7 стилей

Обязательны P06-CBT-01..10 из specs/P06_COMBAT_ACCEPTANCE.md: audit existing Gabar/Oleg/Yakuza без дублирования; Ryzhik real roll; Timka context stance/movement/actions; Pasha resources HUD; Tega actual object; own finisher sound/animation/reaction matrix всех7; settings/death/restart и independent Gameplay/ART/QA/Lead. Дополнительная декоративная вариативность P08 имеет отдельный debt, не заменяет этот gate.

## Принятый компонент Олежки: читаемое окно защиты

Guard feedback на f844e4d принят независимыми ART/Gameplay/QA/Lead как PASS_COMPONENT. Прежний actualpre-damageparry остаётся0.06–0.26s, один incomingcontact, counterчерезCore. Read-only HUDсостояния/sharedpredicate,5pxbar внеарены, authority/death/cancel/pause/restart/settings проверены. Final57headless/78native+21PNG/movie57; independent57+31+164. DEVpreview02 Linux22/Wine18 существует. FullP06/остальныегерои/7uniqueaudio/finishermatrix иnativeWindows не приняты; не повторять готовый компонент без новых дефектов.

### Тега — текущий атомарный пакет

- [x] Создать оригинальные ACTION32 и FIN32; независимый source ART: ACTION v2a `ef71ab4c`, FIN v1a `bb18d080` (только исходный арт).
- [ ] Проверить actual Input F: физический верстак, все четыре направления, NPC/wall collisions, отмена и потеря объекта/полномочий, once receipts, восстановление R.
- [ ] Проверить собственные unarmed/blunt/environmental добивания, hurt/death/restart, persistent clothing overlays, Full/Reduced.
- [ ] Снять native кадры и запись; независимые ART/Gameplay/QA/Lead принимают только замороженный исходный код и реальные материалы.
- [ ] Обновить пользовательский DEV после scoped приёмки. Не считать этот пакет полным PASS P06.
