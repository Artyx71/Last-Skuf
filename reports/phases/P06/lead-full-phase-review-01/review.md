# P06 — independent Lead: PASS

Полная P06 принята на **`37a0aa5995e65d6577338e80c7aacc9a7f60d893`**, main/base **`be4d59e9f68f32833719c82dee36bf731bb43ad0`**, PR11. Обязательных исправлений в согласованном объёме P06 нет. Это независимый итог `/root/art_olezhka_recovery`, не авторское self-PASS. На момент решения PR ещё draft/open/unmerged: фактический merge выполняет только ROOT executor после повторных server-side checks.

Принят прототип расширения персонажей, а не полная кампания или release. Существующий CombatSystem сохранён: шесть новых героев используют его единый damage/score/receipt path, слабый Якудза и CH01 не заменены. Catalog/context/factory отделяют playable и supporting роли; sandbox не выдаёт сюжетных unlocks. У Габара swept-выпад; у Олега настоящий successful-defense→counter; у Тимки раздельные present-disengage и prime-clinch; у Рыжика восьмифазный collision-aware roll; у Теги реальный зарегистрированный physical prop; у Паши выстрел на ходу, конечный общий боезапас и HUD.

## Согласованный объём

Owner decision `58abd098…` переносит в P08 только оставшуюся дополнительную NPC hero-style визуализацию, supporting presentation routing и reviews новых clips. Базовые три NPC archetypes, восемь состояний, category contacts/priority/once/lifecycle/settings и собственные player рисунки/механики/звук/HUD остаются P06 и проверены. Старые C09 source FAIL/toolblock не превращены в выполненную работу. Owner Timka84 `01029237…` сохраняет compact32/28/24, явные собственные shared references и запрещённые категории; present не получает prime-способности.

## Независимая оценка

Три финальных domain reports лично прочитаны, их SHA сверены; все относятся к нынешнему owner-amended объёму и имеют пустой must-fix:

| Domain | Решение | Доказательства |
|---|---|---|
| ART | PASS_ART_P06_CURRENT_SCOPE, `e084b0e5…` | 628 source cells/628 sockets, десять правильных local photo pairs,90 pixel-exact cast captures,244 реальных decoded frames восьми movies;37 прежних reviews и current-critical source bindings |
| Gameplay | PASS, `e43c3422…` | Actual contacts/once clocks,768 held-input samples, distinct contexts/abilities,15 factorized NPC category pairs,50 personally viewed movie frames и19 PNG |
| QA | PASS_FULL_QA_P06_CURRENT_SCOPE, `2df9528c…` | CBT01..10 matrix;51 final audit checks,1456 exact source keys,905 retained proof pins и1131 completed C5 files; итоговое69b completion |

| Gate | Итог Lead |
|---|---|
| CBT01 — собственные FIN/style/audio | Собственные player drawings/различимые timings и20 новых original cues плюс5 legacy; общий NPC category art разрешён только owner amendment |
| CBT02 — Олег | Старый настоящий front melee parry0.06–0.26s, один incoming contact, отдельный Core counter; HUD читает тот же predicate |
| CBT03 — Тимка | Два доверенных контекста, разные stance/stride/actions; present получает обычный входящий урон, не получает FIN/prime grant |
| CBT04 — Паша | Восемь moving-shot фаз, spend на muzzle3, магазин4, общий firearm-FIN cost, refill/recovery/HUD и callback/lifecycle guards |
| CBT05 — Якудза | Campaign escape/nonlethal kit; долгие прерываемые training FIN не разрешаются в CH01 |
| CBT06 — Габар | Направленный collision sweep, contact pose и конечный recovery; LOS/wall/per-recipient authority checks |
| CBT07 — Рыжик | Реальные промежуточные roll drawings, swept path, landing6 и отсутствие неоговорённой invulnerability |
| CBT08 — Тега | Реальный prop, range/facing/LOS/foot revalidation с текущими transforms; cleanup epoch+authority+id сохраняет заменившее действие |
| CBT09 — NPC | Факторизованное покрытие всех15 archetype/category пар, contact1→corpse2, AI priority/once/FullReduced; не выдуманная600-case новая style matrix |
| CBT10 — lifecycle/settings/performance | Cancel/hurt/death/reset/revoke/replace/once/settings/pools и фактические non-Movie wall frames подтверждены |

Самостоятельно прочитаны current Catalog/ScenePolicy/profiles, CharacterPlayer/Frames, Core/legacy grants, signature strategies/runtime helpers, campaign viewing guard, guard/ranged HUD, dialogue/audio/export changes и main-base diff. Factory готовит complete context до замены текущего actor. Core остаётся единственным местом damage/score. Tega current-query sync и epoch/id cleanup действительно соответствуют отдельно подтверждённым historical counterexamples. Pasha проверяет authority/strategy/action serial около launch/cost/callback. Произвольный lifecycle-mutating `weapon_melee` observer обсуждён как nonblocking observation: текущий единственный production listener занимается audio; применимого runtime defect не установлено. Новый scope ради гипотетического listener не добавлен.

## Реальное исполнение и сохранение FAIL

Это **составная приёмка13 стадий**, не один заново успешный13-stage invocation. Сохранены семь завершённых current-critical controller/native/movie стадий; Паша использует accepted651 controlled-input corpus плюс strict7a guard recomputation; cast normal/large, C01 и NPC дополнены actual tail02. Старые остановленные full/tail, Pasha held-motion FAIL и cast line-ahead FAIL не переписаны. Их первоначальные причины не объявлены доказанной OS/focus/launcher причиной.

Последний atomic combat5766… завершился **130**, а не PASS. Но до interruption реально завершились Full/Reduced/Movie/Linux/Wine: каждый413/413 checks,218 PNG,20 FIN и600 samples; encode и пять category clips exit0. Его partial validation содержит30 положительных rows; nested P04 успел только четыре. Отдельное canonical **69b305de0c5c4e65a1fa90433c4c7e97** закончило недостающие existing wrappers exit0/523.955s, без live orphan children. P04 actual24 typed rows, пять real profiles по59 checks/nine captures/ten AI deaths; route_warps0, escape score1000, shots/kills0, retry максимум554.483ms. Movie metadata/mission.mp4 и actual Linux/PE-Wine exports есть. Existing C5 analyzer дал29 typed positive checks на точных пяти сохранённых PCM. Original130/old FAIL и прежние905/1131 pins сохранены. C5 и первые12 не переснимались.

Мой собственный bounded result/material check:615 C5 source inputs и затем все1456 source keys совпали; ELF/PE SHA и magic проверены; лично просмотрены четыре фактических MP4 frame, восемь C5 PNG и четыре новых P04 captures. Две первоначальные diagnostic ошибки (системный Python без Pillow; предположение array вместо dictionary P04 checks) исправлены в reviewer-only inspector до записи завершённого proof. Они не product failures. Godot/генераторы/Controller/Git mutations/signals/cleanup этим reviewer не запускались. Independent QA ранее выполнял реальные отдельные engine subsets, отрицательные controls и actual receipt/source audits; дополнительный повтор неизменных тестов не требуется.

## Производительность, платформы, аудио

Non-Movie C5 stress:32actors/4800contacts/600monotonic process frames/~9.96s, X11, Ryzen53600/GTX1050Ti. P95 Full16.896ms, Reduced16.923, Linux export16.894, PE/Wine16.886; P99 соответственно17.030/17.030/17.044/17.075. Это ограниченный API-driven workload, не обещание FPS для любого будущего уровня. Movie fixed60/capture overhead и старые simulation-delta P04 timing summaries **не** используются как live FPS. Сырые600 intervals не сохранены, percentiles заново из raw не пересчитывались. Hardware latency/live difficulty не приняты.

Фактически проверенные export SHA: Linux `f0f6d1d724d7dc07bea83ea5f0568053e5e913898f0f1ae1fe207e97a25fbecb`; PE `5db18be8adc4d620af915372a9fbdf3f733ec74d7b62b4d6d05d5bf1d73b0003`. DEV09 — самостоятельно перепроверенные standalone byte-exact copies этих файлов, не новый export/run. Launchers используют отдельные profile paths. Native Windows **NOT_TESTED**; Wine — отдельный реальный runtime.

C01 owner response `3b6b3c69…` буквально «Прослушал, принимаю для прототипа P06» относится к исходным solo/runtime. Сохранённая215/215 numerical приёмка трёх свежих PCM имеет TP−6.3/−5.9/−1.9dBTP,0rails, source NCC≥.989945, quiet old/new NCC1/gainΔ0. Для пяти C5 PCM:29positive checks, TP−3.9/−4.4/−4.3/−4.8/−4.5, clipping0. Reviewer **не слышал** аудио; новое subjective stress listening не заявляется. Prototype content owner acceptance и technical signal analysis — разные основания. Reused music/fictional non-identifying bleeps не выдаются за новые реальные голоса или полный campaign soundtrack.

## Финальный source, приватность и CI

Fa869→37a0aa diff самостоятельно проверен:1739 paths=README1+reports1738; Game/tools/assets/audio/art/config/contracts не изменились. Все1456 keys exact, inventory `6836bce1…`. READMEcontrols/DEV09/current prototype limits согласованы с реальной реализацией. Перенос source-equivalent evidence не называется свежим исполнением37. Девять статичных portrait expressions selector sets не объявляются animation каждой реплики; ART собственные all-cells/source и recorded-motion observations не заменены только проверкой количества файлов.

Privacy05 actual35/35,11 current raw identities,18656 reachable Git objects, ROOTindex2328/WORK23429,0 additional matches на37; op1726d94f… receipt0. Это exact known raw-SHA/path/index/ref проверка, не доказательство отсутствия всех re-encodes/retired inputs/unlisted secrets/PCK content и не storefront/voice rights clearance. Raw/private manifest/helperlogs в packet не копировались. Documented public-repository/image_gen/conditional merge permissions уже существуют; broad release не выводится из них.

После archive выполнены **свежие независимые primary connector и actual installed ROOT read-only policy queries**. PR11 head37/basebe4, stateopen/draft, mergeable/CLEAN; rules/protection inspected, threads complete/unresolved0, required bootstrap. Check actual `github-actions`, app15368, exact37 **completed/success**: run43983165690/job133704512046. Лично прочитан terminal result всех steps, включая49-regression, unittest gates, audio, P04G/P05, exports/upload/cleanup. Старый CI fa869 не используется как текущий. Squash/write доступны; manual approvals/merge queue текущими rules не требуются. Draft всё ещё запрещает непосредственный guarded merge до обычного ready-перехода. Эти queries ничего не публиковали/не мержили.

## Разрешённое продолжение

Разрешено импортировать этот независимый **full P06 PASS**, перевести PR11 из draft обычным авторизованным путём и вызвать штатный guarded squash: две свежие head/base/rules/CI/threads проверки, server expected SHA, подтверждение MERGED/одного parent. При любом drift, новых findings или GitHub restriction — остановить merge, без bypass. Reviewer сам merge не выполнял.

После подтверждённого merge сохранить authority/resume state и **stopP06**. Отдельные safe ROOT/Work handoff C02, FULL Production Readiness и21 утверждённых MDS до массового P07 остаются обязательными и этим PASS не закрыты. Последняя принятая база main на момент решения P05/PR10; текущий P06 formal attempt1/legacyglobal2 не сброшены. ТолькоCH01 playable;21 глав и7–9h не измерены и не приняты. P07/P08 execution, ROOT installation и release этим решением не разрешаются.
