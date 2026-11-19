# CH04 — независимый Narrative / paper-contract review01

**CHANGES_REQUESTED_COMPONENT_DRAFT_REVIEW_ONLY.** Канон вербовки, подписи и ограниченности Якудзы согласован; один MEDIUM требует замкнуть описанный физический барьер ниши E3. Полной фазе/реализации FAIL не выставляется.

Объект — CH04 SHA `4707f5fe3723bf979b9757c5c6a8de6ea5b2a3169de6965e9e8c4301a0108423`, заявленный WORK HEAD prefix `b40d7308`. Git не вызывался; authority — actual bytes/SHA и snapshots. Автор — ROOT, reviewer не исправлял источник. Проверены STORY/GAMEPLAY/AUDIO/CHARACTER, actual registry/routes/StoryState, слабый kit в missed_fight config, CombatPlayer и investigate source.

## Подтверждено

CH04/EV_CH04_COMPLETE,4/4,present,YAKUZA,EV_CH03_COMPLETE и пустая production_pending дата совпадают с registry. Набор и соглашение заполняют approved slot: Макс показан рекламным публичным лицом/кажущимся хозяином, поздняя роль Кабана/код Габара/операции/15000 как доказательство не раскрыты. Бумаги не равняются доказанной вине героя. Эллана не сделана организатором или оправданием его решения; лёгкий заработок/возвращение формы — собственный мотив Некита.

Подпись линейного canon beat подтверждается отдельным действием, а не seen-skip/просмотром; можно отложить, но не получить фиктивный отказной финал. Слово «выбор» здесь читается как conscious UI confirmation, не новый D01/D06 или обещание развилки. EV_PRIME_SIGNED действительно отсутствует; документ правильно оставляет signed/paper_taken/dispatched локальными typed stages и закрепляет canonical знание одним EV_CH04_COMPLETE. Нет реального договора, персональных данных, оплаты или сетевой регистрации. Опасный рекламный trial честно вымышленный и не назван безвредным knockout.

Weak kit соответствует конфигу/коду:82/health1, damage0/stun1.15/cooldown1.2,0.083333/0.14/0.083333; E3.2 и investigate2.1. Chapter FIN/training оружие не выданы. Две линии вокруг coverA и западный обход coverB на бумаге связаны с папкой/южным порталом; их actual viability на82px/s ещё должен принять Gameplay. В отличие от CH01 это recruitment/signature/delivery-loop, а не куртка/служебный ключ/Жинька; отличие от будущей CH08 честно оставлено отдельному полному MDS review.

CP1 до угрозы/подписанная локальная стадия, повтор папки сCP1 доdispatch, один local instance, alive+signed+dispatch+EXIT→complete once заданы. Save schema/director/UI ещё High. Safe DISPATCH требует неактивной угрозы и проверенного запрета преследования вSK4; source не выдаёт текущую FSM за готовый room-return policy и прямо оставляет эту production dependency открытой. Её реализация/справедливость не принималась.

## N-MDS-CH04-01 — MEDIUM

Строка45 задаёт interior x1792..1888,y480..592 с верхней/нижней/правой стенами и дверь(1776,480,16,64). Дверь перекрывает левый край только y480..544; ниже y544..592 остаётся48px без указанного левого wall. Межзоновые стены общего правила не закрывают внутреннюю нишу вSK3. Поэтому перечисленная схема ещё не соответствует обещанному физически закрытому до PAPER_TAKEN отсеку43/45.

Минимум: добавить left wall(1776,544,16,48) либо согласованно изменить door/bounds, замкнув левую границу. Никакой новой способности/FSM/арены не требуется. Наблюдение — об источнике room design, не о доказанной runtime атаке: phase inactive может запретить AI, но не создаёт отсутствующий физический барьер. После doc fix замкнутость можно перепроверить чтением; реальные collision/LOS/nav отдельно Gameplay/H02.

## Предел решения

Новых canon или globalflag конфликтов не обнаружено. Арт/реклама/папка/ниша/документы/музыка NOT_CREATED, reuse не назван новым.8–15min — NOT_MEASURED, без padding; audio/listening/native остаются обязанностями. Другие главы/прежние PASS не переоткрыты.

Текущая CH04 ещё не получает NARRATIVE_REVIEWED из-за одного paper fix. Нет Gameplay/ART/Audio/QA/Lead/all21/Readiness/runtime/production/phase/merge/release PASS. Source/registry/status не менялись reviewer; engine/Controller/generator/network/Git не запускались. Записи только в owned report, источники freeze/end и FINAL_HASHES сохранены; после verdict packet immutable.
