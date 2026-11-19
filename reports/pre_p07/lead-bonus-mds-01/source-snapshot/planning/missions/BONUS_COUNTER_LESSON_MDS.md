# BONUS_COUNTER_LESSON — Пауза между ударами

DRAFT_FOR_FULL_MDS_REVIEW / DESIGN_NOT_RUNTIME_TESTED / OPTIONAL_NONCANONICAL.
Развивает сохранённый SECRET_COUNTER_LESSON CONCEPT_ONLY. Основные21 MDS и runtime registry не меняются. Scene, bonus store/журнал, chapter policy и новые ассеты ещё не реализованы; READINESS-H05 и общий gate закрыты.

## Идентичность и обещание игроку

ID BONUS_COUNTER_LESSON, OLEZHKA. Доступ после durable CH10_THE_KIMONO через «Бонусы · вне основной истории». Нет canonical event/даты/нового D01, отношений, награды или сведений о PRIME. Олег18лет, освоил ограниченную защиту, по-прежнему не ходит на дзюдо. Противники — анонимные постановочные угрозы самостоятельного упражнения; это не бой с братом и не реальное насилие на тренировке.

Три радиальных сектора вокруг центра: фронтальный melee, укрытие от пули, затем смешанный угол атаки. Габар по связи напоминает отличать окно ответа от неуязвимости. Порядок секторов фиксирован, внутри есть обходы. Защита полезна, но обычный удар и отход остаются допустимыми: не нужно умирать или исполнять серию обязательных parry.

## Геометрия и пути

Мир1792×1280, grid16, камера640×360. Bounds x,y,w,h, shared/perimeter walls16 кроме перечисленных порталов. Все размеры DESIGN_NOT_RUNTIME_TESTED; clearance, LOS и реальный pathfinding ещё требуют проверки.

| Зона | Bounds | Связи и объекты |
|---|---|---|
| CL0_HUB |512,512,768,512|spawn(896,800), exit(832,928,128,64); west x512 y704..832→CL1; north y512 x832..960→CL2; east x1280 y704..832→CL3|
| CL1_GUARD |0,512,512,512|east→hub; cover(208,624,64,96); marker1(144,864); нижний обход y928|
| CL2_COVER |512,0,768,512|south→hub; cover(832,256,128,96), cover(608,192,64,128); marker2(1056,128); левый/правый подход|
| CL3_RECOVERY |1280,512,512,512|west→hub; cover(1504,640,64,128); marker3(1680,896); нижний путь y944, верхний y576|

Остальной мир — solid, без пустой прогулочной площади. Door rectangles: west(496,704,16,128), north(832,496,128,16), east(1264,704,16,128). Вначале открыт west. Marker1 открывает north, marker2 — east. Путь назад из активного сектора не закрывается до его разрешения; провал не запирает игрока. После clear/marker соответствующая дверь закрывается, cohort удалён, поэтому предыдущий сектор не нужно проходить снова. Exit всегда позволяет cancel, completion только после всех трёх markers. Нет других связей между секторами — это radial hub, а не кольцо Габара.

Открытый hub не объявляется безопасным убежищем: NPC вправе пройти в него тем же порталом. Checkpoint/диалог только после actual clear/nojobs и закрытия двери пройденного сектора; следующий сектор до его открытия не активен. Нет невидимой границы для AI или invulnerability вместо геометрии. Слишком раннее возвращение в hub не сохраняет checkpoint.

## Встречи и способности

| Встреча | Spawn/сценарий | Решения и условие перехода |
|---|---|---|
| E1 CL1 |patrol(192,768), путь(192,768)↔(320,768); читаемый фронтальный замах, без ranged|guard+counter либо обход cover и обычный удар; marker1 после defeated NPC/nojobs|
| E2 CL2 |shooter(1088,160), rusher(656,128); central cover разрывает LOS|левый обход ближе к melee либо правый с предупреждённым прострелом; marker2 после разрешения обоих/nojobs|
| E3 CL3 |patrol(1392,816), shooter(1696,592); cover разделяет углы|guard против melee и нижний отход либо верхний обход/обычные атаки; marker3 после обоих/nojobs|

Каждый конечный cohort активируется при первом входе в свой сектор после предупреждения у его двери. Предупреждение не заменяет обычный NPC telegraph; нет выстрела из занятого spawn или из-за невидимой стены. Сложность — углы/укрытия/сочетание врагов, не повышение HP/бесконечные волны. Боссов и новых архетипов нет. Финальная сцена сочетает уже известные решения, не требует обязательного finisher или счётчика идеальных parry.

Олег speed106, существующий training_counter: guard0.06..0.26s по action clock, windup0.28/active0.10/recovery0.34/cooldown2.0 из текущего CharacterPlayer. Изменение этих значений требует нового timing review. Пуля, удар со спины/сбоку и смертельное попадание не дают контратаки. HUD показывает ready/preparing/guard/closed/recovery/cooldown. У marker один F потребляется interaction, вне prompt — counter; это будущий adapter/test, не уже готовая функция. Старт unarmed; нет дзюдо-суперсилы, огнестрела, акробатики Рыжика. Trusted bonus scene grant использует существующую ability, save не выдаёт policy. Finishers и NPC reactions — собственные принятые P06 кадры/тайминги после проверки host integration.

## Checkpoints, смерть и завершение

Checkpoint и markers — локальная память попытки, не поля campaign/sidecar. Fresh process начинает CP0. CP0 — hub, markerfalse, health1/unarmed/CD0. После marker1 игрок сам идёт назад в hub; только пересечение hub после clear E1 закрывает west, удаляет E1/jobs и создаёт CP1(marker1true, north готов). После marker2 такой же пеший возврат даёт CP2(marker1/2true, west/north closed, east готов). Телепортации к checkpoint нет. Закрытие двери возможно лишь после actual clear; это не ловушка и не принудительный выход под удар.

Смерть до CP1→CP0, между CP1/2→CP1, в E3→CP2. R сбрасывает generation/jobs/временные окна защиты и восстанавливает нужные двери/cohorts. Никакого checkpoint при NPC в hub, контактах или активном finisher. Сохранённый бонусный completion не сбрасывается смертью. Cancel возвращает в безопасный журнал без ложной награды.

Победа alive/all3markers/exit/nojobs, короткое завершение и atomic sidecar commit одного ID. Старый exit callback, replay, skip интро или поддельный completed не обходят prerequisite/scene authority. Write failure сохраняет прежние bytes/state и допускает повтор exit с сообщением. Основная история и D01 остаются неизменными; действуют BP01–BP10 BONUS_PROGRESS_CONTRACT.

## Постановка и звук

Предлагаемые ресурсы BC_INTRO — Олег «Я не сказал, что всё умею», Габар «Я сказал — не лезь под второй»; BC_E2_HINT — «Пулю не лови» только в безопасном hub до открытия E2; BC_EXIT — Олег «Вот так понятнее». Ресурсы NOT_CREATED, новые реплики не отменяют кимоно/прежний образ. Skip не ставит markers. Разговоры только при закрытых дверях/clear/nojobs, не freeze во время чужой атаки.

EXPLORE в hub→SUSPICION при предупреждении→COMBAT→CLEAR после actual resolve, затем EXPLORE. Один score предпочтительнее трёх резких restart; retry сохраняет transport. Нужны реальные duck/loop/state transition/scene-reload тесты и запись. Новые theme/stems/ambient/prop cues REQUIRED_NOT_CREATED; signal/mixer QA и слушание обязательны. Прежнее P06 owner listening не является приёмкой нового score, AudioDirector не делает crossfade разных score.

Нужны оригинальные room tiles, cover, три различимых marker props, двери/предупреждения, недостающие портретные реакции. P06 bodies/reactions/SFX можно переиспользовать с точной policy/provenance проверкой. Новые ассеты и ART review не готовы; debug формы не принимаются за итоговое окружение.

## Уникальность, длительность и приёмка

CH10_THE_KIMONO — путь к квартире, смена POV и D01; здесь radial hub и самостоятельное упражнение без братского спора. CH17_THE_LAST_JUDO — семейное раскрытие/помощь/D06, здесь обучение ограниченной защите без новых фактов. BONUS_OFFLINE_BUILD — физическая петля/узлы/lunge; здесь три сектора, защита/отход и checkpoint после clear.

План5–10мин с retry — NOT_MEASURED. Шесть конечных NPC не обещают10мин: более короткое содержательное прохождение допустимо. Не увеличивать HP/ожидания/обязательные повторы parry ради длительности. Optional время не включать в обязательную кампанию. После реализации измерить first-play/маршруты/ошибки защиты/deaths/causes/restart/бой-диалог-перемещение-AFK/input/frame/music по H04; subjective feel отдельно.

До производства — Narrative/Gameplay/Lead по полной MDS. После — обе ветки каждого сектора/LOS/pathfinding; реальный проход NPC в hub; запрет checkpoint до clear; CP1/2 reset; sidecar/once/old saves/stale event/replay/старые5 секретов/концовки; frontal guard до lethal, все углы/пуля/recovery/конфликты состояний; F arbitration; finisher contact/NPC reactions/FullReduced; native Input/captures/короткая запись/ART/signal+listening/Linux+Windows builds и независимые QA/Gameplay/Lead. Ни одного PASS, готовой сцены или измеренной длительности документ не заявляет.
