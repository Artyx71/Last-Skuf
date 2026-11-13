# P06 — GAMEPLAY / policy boundary preflight, v3

Статус: **REGISTERED_POLICY_COMPONENT_VERIFIED_HOST_GAMEPLAY_PENDING**. Независимо прочитан HEAD `79fa2ec645edf1ba4446f353f864b26c93362db3`. Это scoped infrastructure review, не полный GAMEPLAY PASS и не PASS P06. Reviewer `/root/gameplay_review_p06` не запускал Godot/controller/native/генерацию, не менял source или Git. Записаны только versioned v3 файлы в корневой gameplay-preflight; v1/v2 сохранены. Sole controller lease остаётся у native art stage02 автора.

## Подтверждено исходниками

`character_scene_policy.gd:10–24` загружает packaged `sandbox_scenes.json` schema1, проверяет scene_id/actor/context и subset catalog equipment, возвращает глубокую копию. Семь definitions представляют шесть новых героев с отдельными Timka present/prime; supporting/Yakuza не подменяются. `open(scene_id: String):26–31` не принимает dictionary actor/context и не интерпретирует save text как definition. Unknown key очищает active authority. Getter definition и authority возвращают независимые данные; изменение полученной копии не меняет scene owner.

`finisher_authority:40–44` связывает actor с active fixture и требует requested category == selected category. Это закрывает прямой environmental request при selected unarmed, несмотря на общий weapon=unarmed в legacy base. Actual weapon/range/LOS/earned target/environment geometry по-прежнему проверяет unchanged CombatSystem; JSON category не заменяет эти проверки.

Snapshot включает generation, увеличиваемую при каждом open/invalidate, и scene_instance=get_instance_id(). Reopen того же key и замена owner с той же generation дают другую authority. Общий CombatSystem из v2 сравнивает весь dictionary на pre-contact eligibility: новый snapshot отменяет старый pending job. Profile resolver получает context от resource-owned policy. movement_speed/ability_id выбирают context metadata (Timka present84/disengage, prime118/clinch), но не исполняют movement/ability.

## Проверенные доказательства

Unit source `character_scene_policy_test.gd` проверяет семь fixtures×categories, actor substitution, returned-copy mutation, present/prime metadata, authority copies, generation/reopen, owner identity, unknown/context/raw JSON text, selected tool mismatch и invalidate.

Integration source `character_policy_integration_test.gd:120–150` использует unchanged production CharacterScenePolicy и CombatSystem через явно **test-only** RegisteredPolicyActor (`fixtures/character_policy_lab.gd:51–62`), наследующий legacy CombatPlayer/art. Новые cases: prime→present и повторный start; same-key reopen; owner replacement при одинаковом generation с отличающимся scene_instance; прямой category bypass; JSON save-text revoke. После потери authority проверяются ноль hit/damage/score. Ранние45 checks сохранены. Это реальная policy→Core integration, но не production CharacterLab/factory/новый hero body.

Reviewer независимо пересчитал **156 SHA256 entries** из `registered-policy-regression-02.json`: **0 mismatches** с текущим WORK. Прочитаны три log files: unit **99/0**, integration **57/0**, world preview **70/0**, всего **226**. RESULT совпадают с JSON; reported exit0, errors пусты, ERROR/WARNING lines отсутствуют. Все команды headless/fixed-fps60. Reviewer runtime rerun не выполнялся. source_unchanged=true о ходе run — statement автора; current-file→inventory совпадение проверено независимо.

Shared CombatSystem, CombatLab default factory, CombatPlayer, catalog/profile и base finishers имеют те же hashes, что в v2 inventory. Старые combat/contact/P04G regressions здесь повторно не запускались и не заявляются как свежие v3 результаты. Их прежнее evidence относится к unchanged Core, а не к ещё не существующему production actor.

## Оставшийся host contract

**Production registry/policy component теперь существует; соответствующая часть ограничения v2 закрыта.** Registered key — идентификатор разрешённого sandbox fixture, не credential. open("timka_prime") намеренно разрешён. Отказ для JSON dictionary text доказывает отсутствие parsing, но не доказывает, что будущий host не передаст валидный timka_prime из произвольного save/UI поля. Production host должен владеть routing: явный sandbox selection начинает новый registered fixture; campaign/save loading не назначает prime strength; unknown/missing state безопасно отказывает. Это оставшийся integration contract, не новый дефект компонента.

Host обязан вызвать CombatSystem.reset перед actor/context/fixture switch и очистить transient props/actions/effects/references/cost/cooldowns по manifest. Policy generation/equality обеспечивают pre-contact revocation без reset, но сами не очищают scene/cooldowns/projectiles/presentation. Integration tests меняют owner без reset для проверки guard; это не образец production lifecycle. Новые actors обязаны подключать policy hooks, а не попадать в legacy fallback.

## Preview и следующая проверка

PixelPresentation.align меняет visual.position, а не body.position/velocity/clock. World preview использует отдельный PreviewActor и InputEventKey→Input→physics movement; continuous sequence не делает fixture teleports между сегментами. Его grid/fractional-physics checks — evidence art fixture. Registered policy/combat в PreviewActor не подключены. Он явно пишет WORLD_ART_MOVEMENT_PREVIEW_ONLY и NOT_IMPLEMENTED_IN_THIS_PREVIEW. Headless70 не доказывает gait/likeness/camera feel/rendered contact readability; actual native stage02 здесь не оценивался.

По-прежнему нужны production CharacterLab/factory, шесть distinct abilities/actions/personal finishers, Input/contact/cancel/cost/recovery contracts, 8-cell renderer mapping и реальные per-hero/four-direction native captures. Требуются sandbox save/CH01 isolation/process restart, per-action once-hit/score/reset/reload/settings invariance, exports/platform/runtime/performance и независимые ART/GAMEPLAY/QA/Lead gates. Catalog max equipment не означает actual предмет в scene, ability_id не исполняет ability.

Новых HIGH findings в рассмотренном policy component не найдено. Его infrastructure subtask подтверждён в описанной области; phase/ability/ART/native-feel PASS этим отчётом не выдан.
