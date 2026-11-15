# P06-CBT-02 — читаемое парирование Олежки

IN_PROGRESS; это компонент P06, не phase PASS. Базовый Core/приём/авторские спрайты сохраняются. Из существующего defense hook выделен тот же live predicate (0.06–0.26с, прежние0.28/0.10/0.34s и cooldown2s); HUD использует read-only снимок именно этой шкалы. Никакого второго таймера/урона от UI.

Новый HUD в верхней служебной полосе показывает готовность, подготовку, открытое окно только спереди, успешный блок/ответ, промах, recovery/cooldown, pause/death/revocation. Полоса не занимает игровую арену; Gabar её не получает. Ошибка выбора неготового героя видна в нижней строке.

Нужные evidence: actual Input/live enemy Core contact, неизменные здоровье/once score/damage, границы окна/negative cases, pause/cancel/restart/authority, FullReduced/flashes/shake/VHS, process-frame HUD/model parity, actual screenshots/short video, oldOlezhka/Gabar/contact/restart regression и independentGameplay/ART/QA/Lead component review. Фикстуры явно задают стартовые позиции/health и выключают AI там, где контролируется момент удара; это не first-play/hardwarelatency/FPS measurement.

Новых raster/audio/photos здесь нет; существующие approved sprites/cues переиспользуются без заявления об индивидуальном7hero sound design. FullP06/P07/exports/merge этим компонентом не принимаются. Runtime statuses/test results будут записаны после фактических запусков в новых папках, не поверх старых отчётов.
