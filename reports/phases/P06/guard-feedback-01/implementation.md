# P06-CBT-02 — читаемое парирование Олежки

PASS_COMPONENT после независимых ART/Gameplay/QA/Lead; это не полный P06 PASS. Базовый Core/приём/авторские спрайты сохраняются. Из существующего defense hook выделен тот же live predicate (0.06–0.26с, прежние0.28/0.10/0.34s и cooldown2s); HUD использует read-only снимок именно этой шкалы. Никакого второго таймера/урона от UI.

Новый HUD в верхней служебной полосе показывает готовность, подготовку, открытое окно только спереди, успешный блок/ответ, промах, recovery/cooldown, pause/death/revocation. Полоса не занимает игровую арену; Gabar её не получает. Ошибка выбора неготового героя видна в нижней строке.

Нужные evidence: actual Input/live enemy Core contact, неизменные здоровье/once score/damage, границы окна/negative cases, pause/cancel/restart/authority, FullReduced/flashes/shake/VHS, process-frame HUD/model parity, actual screenshots/short video, oldOlezhka/Gabar/contact/restart regression и independentGameplay/ART/QA/Lead component review. Фикстуры явно задают стартовые позиции/health и выключают AI там, где контролируется момент удара; это не first-play/hardwarelatency/FPS measurement.

Новых raster/audio/photos здесь нет; существующие approved sprites/cues переиспользуются без заявления об индивидуальном7hero sound design. FullP06/P07/exports/merge этим компонентом не принимаются. Runtime statuses/test results будут записаны после фактических запусков в новых папках, не поверх старых отчётов.

## Фактический результат

Frozen tested gameplay source f844e4d3cb2c5a7d851337fdf49a00bf51c67b6c. Final headless03:57/57; native03:78/78 с21PNG, movie57/57. Source unchanged. Первая native01 проверка логики была зелёной, но actualPNG показал27px defaultthemebar и заход на арену: авторский visualFAIL сохранён, исправление проверено на actualchildrect5px в02/03; не выдавать01 за ART PASS. Retry также очищает старое предупреждение о неподдерживаемом выборе.

Независимые отчёты отдельно: art-guard-feedback-01 PASS_UI_COMPONENT (21PNG/286decodedHUDframes); gameplay-guard-feedback-01 PASS_COMPONENT (812реальныхнаблюдений/четыренаправления/actualnexttickcontacts); qa-guard-feedback-01 PASS_COMPONENT (freshimport,57new+31ownboundary/purity+164oldOleg); lead-guard-feedback-01 PASS_COMPONENT после actualaggregate/code/media/build inspection. Все source/evidence/portable hashes сверены перед копированием. Новых creative raster/audio нет, subjectivehumanfeel/physicalkeyboardlatency/FPS/listening не принимались.

Ранее regression01:Ole164/Gabar124/contact48/restart68/readiness56/policy/Yakuza21/options31/P04G695 и lab isolation+actualprocessreload passed; final03 повторил restart68/readiness56/isolation после reset-warning UI patch. Headless не nativegameplay/FPS proof, Movie fixedfps не liveperformance. Все поля rawresults/старыеFAIL остаются неизменными.

Actual DEVpreview02 exports f844e4d: LinuxELF77,298,816bytes ca44b646… (renderer/Input22/22+4PNG), WindowsPE113,047,888bytes f0bef4aa… (actualWineheadless18/18). NativeWindows NOT_TESTED. ROOT/build/P06_DEV_20261115_02 launchers используют отдельный profile; предыдущая01 сохранена. ActualpackagedOlegPNG содержитновыйHUD. Отчёты reports/phases/P06/owner-preview-20261115-02. Это неrelease/fullphase.

Все builderjobs завершеныиconsumed:headless01 ee6f0c99c4274385bab6c4f107e93f9e;import01 bcb580045bfe48cca612130bf3a4128b;native01 9da57ae88352488781e56f18ea4010af;native02 8bc1d082b3c7415780925216931f86a6;final03 3decbaaafcec4597a33b2fcff1613f18;preview02 9a94401ac76c49189e6403fb4c50dc7c. Receipt/log/argv integrity проверена; jobs не replay. Source/import создалтолько2UIDfiles, существующиеfilesнепереписывались.

P06 ещёIMPLEMENTING attempt1, lastfullPASS P05. Новые остальныеheroabilities/7uniquefinisher+sfx+NPC matrix, fullverify_p06.py/safeROOThandoff/readiness/21MDS остаются за отдельными gates; component не разрешает P07/merge.
