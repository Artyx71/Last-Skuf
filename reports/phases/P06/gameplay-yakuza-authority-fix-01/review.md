# Независимый follow-up — граница добиваний Якудзы

**GP-P06-YAKUZA-SCOPE-01 CLOSED_SCOPED_FIX_VERIFIED.** Исходный дефект независимо воспроизведён настоящим headless Godot в ROOT-копии; исправление проверено тем же неизменённым тестом и целевыми регрессиями. Это закрытие одной находки. Семь героев/P06 ещё не готовы к полному gate; фазового PASS, новой попытки, ART/audio/merge/next-phase разрешения нет. Исходный GAP-аудит и все48 его artifacts сохранены неизменными.

Reviewer `/root/art_olezhka_recovery` независим от автора. WORK только читался. Две полноценные game-копии созданы внутри этого ROOT report каталога, без symlinks и без копирования WORK .godot. В before заменены только2 production files на сохранённые автором pre-fix версии; test script byte-exact тот же. Pinned Godot SHA сверён с toolchain lock. Все headless editor/import/test команды выполнялись только с --path этих ROOT-копий. Config/data/cache/runtime/tmp, четыре save paths и output разделены по каждой команде; унаследованные AYAY/GODOT overrides удалены, audio driver Dummy. WORK/native/display/Controller/Git/network/generator не запускались/не менялись.

## Изменение по коду

`CombatLab.legacy_finishers_allowed(source)` выдаёт legacy grant только если config_path равен точному prototype training path **и** source является player этого host. Production CH01 hardcodes иной config path, поэтому подмена player.kit/finisher_weapon/finisher_category не выдаёт разрешение сцены.

В `CombatSystem.eligible` новая проверка находится в legacy else-ветке: host без метода/без grant отклоняется до definition geometry, reservation, cancel_action и contact. Проверка выполняется и при старте, и при последующей eligibility revalidation. Opt-in character-resolver authority ветка осталась прежней. Глобальные Yakuza damage/clocks, слабый escape kit, прочие способности и once pipeline не переписывались. Полный reviewed diff сохранён в production-diff.txt;4 проверенных current source SHA и412 input game files — в inputs.json.

## Независимая дифференциальная проверка

| ROOT isolated run | Результат |
| --- | --- |
| Before: archived Core/Lab + тот же новый тест | exit1;11PASS/10FAIL — ожидаемое воспроизведение дефекта |
| After: current Core/Lab + тот же тест | exit0;21/21PASS |
| After P04G |695/695PASS|
| After character policy integration |57/57PASS|
| After mission test |28/28PASS|

После исправления независимо выполнены **801 assertion/0fail** в4 тестах; до исправления отдельный negative-control run дал ожидаемые10fail. Два fresh headless imports завершились exit0. Всего7 engine invocations:2imports+5test runs. Команды, exit codes, отдельные profiles, логи и hashes находятся в reviewer-commands.json; actual before/after result JSON сохранены отдельно.

Тест использует реальные InputEventKey Space/V/C и настоящий production Core. Target AI активен, stun зарабатывается damage0 shove, здоровье/stun напрямую не назначаются. Другие угрозы выключены и актёры расставлены fixture; intro завершён служебным director._finish. Поэтому это реальная проверка конкретного контакта/авторизации, **не полный playthrough CH01 и не физическая клавиатура**.

Before в Full и Reduced фактическое V создавало finisher job; target становился finisher_reaction. Восемь direct-Core checks для forged unarmed/blunt/sharp/firearm также обнаруживали grant/reservation. Environmental уже отклонялся отсутствием допустимого prop; его успешное отрицательное before поведение не выдаётся за доказательство прежней scope-защиты. Тест немедленно чистит запрещённые before jobs, чтобы закончить experiment; он подтверждает неразрешённое создание job, не записанное завершённое убийство в кампании.

After в Full и Reduced actual V не создал job; target остался живым stunned. Прямые попытки всех5 categories при forged training kit/equipment отказаны с неизменным snapshot jobs/history/next_attack_id/receipts/action/clock/kills/score. Позднего damage/reward нет. Отдельный настоящий training host по-прежнему запускает unarmed finisher после earned Input shove; C отменяет его. P04G695 дополнительно сохраняет все5 training categories, once/interrupt/state/settings/lifetime/caps поведение; policy57 проверяет прежнюю character-authority ветку; mission28 сохраняет сценарную инфраструктуру/weak weapons/retry/settings/completion smoke. Последние28 не выдаются за новый полный no-kill маршрут.

## Связь с авторским evidence и CI

Прочитаны и SHA-проверены авторские archived before source/result/log/command и все9 after regression commands/logs (exit0). Их полный набор не приписан reviewer-run: независимо повторены только4 after tests, перечисленные выше. Current Core/Lab/test/verify SHA не менялись в ходе review; test registration `yakuza_finisher_authority` присутствует в tools/verify.py ровно один раз. Удалённый GitHub CI/branch protection/current PR SHA этим offline follow-up не проверялись.

Fresh editor import автоматически нормализовал default_bus_layout.tres **одинаково в обеих ROOT-копиях** (serialization/default fields/UID). Это единственный изменённый импортом файл из исходных412 input game files; оба Core/Lab/test и WORK bus layout сохранены. Изменение записано в metrics с обоими SHA; оно не скрыто и не трактуется как audio test/приёмка. Generated import caches остаются локальными runtime artifacts, не доказательством source готовности.

## Граница закрытия

Закрыта только HIGH находка про legacy campaign finisher grant на указанных source hashes. Метод scope grant — доверенный host API, не сохранённый player field; будущие host/scene изменения обязаны сохранять fail-closed policy. Новые механики/анимации/звук/реакции/HUD остальных героев, distinct Timka contexts, прочие7 GAP tickets, полный current-source native/gameplay/art/QA/Lead/exports/performance/listening и обязательный CI остаются отдельными gates. Никакой фазовый attempt не расходуется/не сбрасывается; перехода вP07/merge этот документ не разрешает.
