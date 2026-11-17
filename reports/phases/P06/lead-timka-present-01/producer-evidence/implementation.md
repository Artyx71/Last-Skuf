# P06: Timka FIN24 source и современный disengage

Полная P06 остаётся IMPLEMENTING, formal attempt1; последняя полная PASS/MERGED — P05/PR10. Этот отчёт автора не является решением Lead.

## Реальное изменение

Встроенный image_gen создал новую целую environmental UP-позу Тимки из двух собственных ранее сгенерированных референсов. Новые сырые фото не отправлялись. Raw/prompt/reference hashes/provenance сохранены в assets/source_art/characters/timka/*v4*. Whole-figure uniform NN packing изменил только original cell29; остальные31 source/native32 и23 compact24 клетки byte-exact. Независимый ART source f3f8e29f… заново рассмотрел все24 и принял supported_v2; canonical adopter перенёс только FIN24. Старые WORLD32/ACTION28 и четыре legacy backups не мигрировались повторно. Исторические FAIL/отклонённый weapon request сохранены, исключённый weapon запрос не повторялся. FIN source acceptance не выдаёт prime ability.

В существующий CharacterPlayer добавлен registered timka_present/disengage. Он загружает только свои WORLD/ACTION и60 привязок к одежде. F: guard0.12s → четыре собственных walk-рисунка в обратном порядке в течение0.24s → recovery0.18s; cooldown1.8s, максимум33.6px назад со скоростью140px/s. Это явно объявленное reuse шести references, не шесть новых рисунков. Настоящий move_and_collide использует прежние collision masks. Окно движения интегрируется только в active-части physics tick. Нет исходящего damage, неуязвимости, ranged, finisher или prime grants. C/hurt/death/revoke/reopen/замена scene owner отменяют движение; options сохраняют action/cooldown; restart очищает стоимость и состояние.

Factory подготавливает exact context/ability/все необходимые собственные кадры/sockets до удаления старого actor. Prime, Ryzhik, Tega, Pasha остаются недоступны, сохраняя живой бой при отказе. Gabar/Oleg и CombatSystem не переписывались. В common tools/verify.py зарегистрирован headless Timka replay.

## Проверка и реальные исправления

- headless01:70pass/2fail — неверно посчитанные36 вместо32 clips и тестовый свободный маршрут, пересёкший существующую стену. Исходный результат сохранён; тестовый маршрут исправлен до Input, отдельная wall-проверка осталась.
- headless02:72/72. При самостоятельном просмотре аннотаций обнаружены четыре точки на коже: WORLD6/7 иACTION8/15; исправлены только metadata, первоначальные диагностики сохранены.
- native01 source69ffc58:98/98,26PNG, movie72/72. Независимые Gameplay/QA вернули FAIL покрытия: direct receive_hit не доказывал настоящий incoming Core contact; QA также нашёл отсутствие CI wiring. Старые решения не переписаны.
- исправленный source2780e9e: headless03 —104/104; native02 —137/137,33PNG; movie —104/104. Семь настоящих incoming Core contacts: guard/active/recovery × nonfatal/fatal и projectile во время движения. start_melee → enemy bind/contact pose → live geometry → once receipt/receive_hit. Противники имеют явно заданные начальные позиции и paused AI; это контролируемый Core-тест, не оценка живого AI-боя или физических задержек ввода. Проверены health/hits/hurt/fall, прекращение именно ability motion, отсутствие повторного damage/outgoing hit/counter/score, сброс receipts при рестарте.
- native02 recording: build/P06/timka-present-02/timka-present.mp4, SHA c2394c6809f6e73045a9e1a123588c6e74732551c0570061aa7bfacbcead23e4. Это реальная запись Godot, не расчётные кадры/FPS acceptance.

ART01/02 приняли bounded source/native presentation и60 WORLD/ACTION sockets; FIN sockets и prime этим не приняты. QA01 независимо выполнил554 assertions в собственной копии, сохранил FAIL coverage. Gameplay01 numeric/visual passes ограничены ранее указанным пробелом. Свежие closure reports сохраняются отдельно *-timka-present-02; только независимый Lead может принять компонент после их проверки.

## Проверенные DEV03 builds

Current build source f66995892c8fdf8782e389a76c8ff05d628714d0 отличается от2780e9e только packaged QA smoke script: KEY3 теперь проверяет настоящий present/F/noFIN, KEY4 — безопасный отказ незавершённого prime. Production controller/art/sockets неизменны.

ROOT/build/P06_DEV_20261115_03/PLAY_LINUX.sh и PLAY_WINDOWS.cmd. Linux ELF:77,382,624bytes, SHA f9dccfe24827011b2710a24d45edc4970ee4e8cc55fcac554bd7e678217ff38f, actual renderer26/26+5PNG. Windows PE:113,131,696bytes, SHA6977fa5c9587e064807a89c8f4713256191a302ff8cf53331d81f598bf05b28d, actual Wine headless21/21. Native Windows NOT_TESTED. DEV01/02 и профили сохранены. Это local DEV, не release/full P06. Отдельный availability-erratum исправляет старое hardcoded поле preview.json без перезаписи результата или бинарников.

## Границы и продолжение

Новые звукозаписи/музыка не создавались и не оценивались на слух. Переиспользуются прежние runtime cues; это не приёмка индивидуального P06 sound design. Нет новых утверждений о реальном FPS, physical input latency, live AI feel, полной кампании или Windows на реальном Windows.

Остаются prime stance/movement/actions/clinch/FIN runtime с24 sockets и различимость present/prime; Ryzhik roll и собственные ACTION/FIN; Tega real object; Pasha moving shot/ammo/recovery HUD; sevenhero sounds/NPC reactions/full matrix; full verifier/safe ROOT handoff и полный независимый phase review/current CI/merge. P07 остаётся gated: fullP06PASS/confirmedmerge, independent ReadinessPASS,21MDS Lead-approved перед mass production. Новые компоненты не закрывают весь P06-CBT03.

Все семь новых Controller jobs имеют durable consumed receipts, safe_retry=false; execution-receipts.json и execution_sources/ сохраняют реальные scripts/argv/receipts/logs. Старые jobs/FAIL не повторяются. Фотоприватность ROOTmanifest11 и7ignore/history probes проверены без ошибок. Постоянный runner не заявлен.
