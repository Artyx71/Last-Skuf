# Тега: принятый компонент P06

Игровой коммит20cbc322441a80675907bf407f12962778c6c084. Независимый Lead03 PASS_COMPONENT8d7e4bdfead1cc5cbd7b702780bee711f3faa6ab3b85afcfdfdc8c90eba46e7a разрешает продолжение Паши внутриP06. Полная фаза и переходP07 не приняты.

Созданы собственные ACTION32/FIN32, добавлены к прежнему WORLD32:96рисунков,56клипов,96аннотаций одежды. Исходники генераций, неудачные pack/нормализация и полные технические рецепты сохранены. Никакие фотографии в этих генерациях не отправлялись: только собственные утверждённые WORLD/портреты. Все креативные исправления сделаны встроенным image_gen, техническая упаковка использует только полные фигуры/ячейки иNN.

F реально толкает существующий зарегистрированный верстак. Короткий foot overlap/range/facing/LOS, pinned object/scene authority/epoch, swept движение предмета и героя, физическое столкновение с NPC/стеной и один Core receipt. Windup0.18/active0.18/recovery0.32/cooldown2.4;37.8px — потолок, фактический свободный путь при60Hz35.700012px. Damage1/stun0.55, без finisher reward. Пауза/отмена/ранение/смерть/утрата объекта или полномочий останавливают job; reset восстанавливает действительно сдвинутый предмет, маски/exceptions сохраняются.

История независимого review:

- Lead01 FAIL88896295: после synchronous audio callback тот же предмет или источник переносились на128px, но успевал stale step0.700012px. Урон/receipts не возникали. Вc8 введена полная повторная spatial eligibility после callbacks/до движения и commit.
- Lead02 FAILa21bf982: Node transform и PhysicsServer внутри кадра расходились, короткий боковой перенос обходил overlap; старый cleanup отменял новоеF послеreset/new epoch с повторным numericID1. В20c production query явно синхронизирует transform обоих тел; cleanup сверяет epoch/authority/id.
- Lead03 PASS8d7e4bdf: L01/L02/L03 закрыты. Прежние FAIL/сырые измерения не переписывались. QA clean callback не вызывает eligibilityhelper/force и доказывает production sync причинно, а не подлечивает тест. Сравнительные старые15checks имеют отдельно раскрытый порядок telemetry.

Фактический итог20c: headless305/305; native live433/433 и128PNG; MovieMaker305/305,4810кадров/80.166667s. Независимый QA03:461/461 +freshimport, source1242/пробы неизменны. Native live walltime81.24s, movie render155.966s не являются измерением FPS. Свежие положительные пути/24earnedFIN FullReduced/NPC1→corpse2/66контактов/12clothingposes проверены ART/Gameplay/QA/Lead.

Решения: ARTef5ec882, Gameplay90526622, QA34b65dc2, Lead8d7e4bdf. Все exact полные SHA и manifests лежат в соответствующих *-tega-environment-03. Компактные reviewer-owned shipping proofsets сохраняют pixel-equivalent boards иSHAссылки вместо тысяч дублирующих PNG; полный localcache остаётсяROOT.

Открыто за пределами этого компонента: индивидуальные7heroSFX/полная NPC style matrix, hostFPS/hardwarelatency, новые packagedexports/nativeWindows, полный P06 и FULL readiness. ExistingcategorySFX переиспользованы, прослушивание новых звуков не заявляется. DEV05 не перезаписан и Тегу не содержит.
