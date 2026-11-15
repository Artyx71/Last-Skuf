# Статус проекта

Последняя полная **PASS/MERGED — P05**, PR10 https://github.com/Artyx71/Last-Skuf/pull/10, main be4d59e9f68f32833719c82dee36bf731bb43ad0. **P06 IMPLEMENTING, formal attempt1**; full Lead PASS/PR/merge ещё нет. Прежние PASS и исторические FAIL сохранены.

## Реальный DEV build для владельца

ROOT/build/P06_DEV_20261115_02/PLAY_LINUX.sh и PLAY_WINDOWS.cmd. Linux ELF и Windows PE реально экспортированы из frozen sourcef844e4d3cb2c5a7d851337fdf49a00bf51c67b6c. Actual Linux X11 smoke22/22 +4PNG; actual WindowsPE под Wine headless18/18. Native Windows NOT_TESTED. Source game после этого не менялся. Сборка/профили/лицензии и launcher README находятся в build; hashes/evidence — reports/phases/P06/owner-preview-20261115-02. Предыдущая DEV01 сохранена. Это DEV preview, не P06 acceptance/release.

F5 открывает sandbox Габара/Олежки; F6 —9портретных/диалоговых наборов. CH01/journal доступны из меню. Остальные новые combat heroes корректно не выбираются до готовности. Preview не доказывает sevenhero combat/fullcampaign/FPS/listening.

## Независимый PRE-P07 audit

**FAIL только по Production Readiness**, decision b76fa63b5c45a53d3ad7d3d491ba8faea6c9bc3c2d464bd26a49da8366ca0870, reports/pre_p07/lead-readiness-01. Все8систем проверены по реальному source/evidence; Lead отдельно выполнил261headless assertions, декодировал28legacy audiofiles без заявления о слушании, сверил actual exports/4PNG/исторические ограничения performance. P06 attempt/старые PASS не изменены.

Девять задач READINESS-C01/C02/H01..H05/M01/L01 добавлены в AUTOPILOT с критериями. Critical: полнаяP06/sevenstyles; fullverify_p06.py и безопасная передача ROOT/candidate runner. High:21полныеMDS, multiroomnavigation, music/hero cues, calibratedpilotmetrics, новаяbonus integration. Optional cosmetics отдельно planning/P08_TECH_DEBT.md.

Единый MDS template и production registry21main+7secret готовы как подготовительные документы. Полных новых MDS пока нет:20ещёотсутствуют, CH01нуждается вP07дополнениях,0of21Lead-approved. В runtime только CH01playable/20planned и5canonicalsecrets. Target7–9h NOT_MEASURED; не заменяется суммой оценок.

Владелец разрешил два необязательных предложения. SECRET_OFFLINE_BUILD/SECRET_COUNTER_LESSON получили отдельные Narrative f047ffba… и Lead179ae29f… **CONCEPT_ONLY PASS**, не canon/MDS/runtime/readiness approval. Исходные рассмотренные drafts сохранены; четыре follow-up в planning/missions/OPTIONAL_CONCEPT_REVIEW_FOLLOWUPS.md. Основной сюжет/пятьsecrets/концовки не изменены.

## P06: реализованное и оставшееся

Габар/Oleg реальные lunge/parry handlers переиспользуются. Timka owner84 решение automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json:WORLD32+ACTION28 уже source-accepted/adopted,FIN24 ещёне adopted. Четыре exact legacy backups сохранены; миграцию не повторять. Independent compact QA b9484565 и import QA c50b9b92 — ограниченные component PASS, не abilities/ART/fullphase. Hidden RGB только при alpha0 канонизирован, видимые пиксели/alpha строго сверяются. WORLD padding generation-request deviations явно записаны, не заявлен>=16 hardgate.

HIGH legacyYakuza finisher leak воспроизведён и исправлен; independent2a8da1c7 подтверждает baseline11pass/10fail→801afterfix assertions; training authority и слабый campaignYakuza сохранены. Gameplay audit fcefbeae… остаётся историческим ограниченным аудитом, не fullP06review.

До P06 PASS обязательны Timka FINenv/distinct present-prime drawings/abilities/sockets; Ryzhik original ACTION/FIN+actualroll; Tega actualenvironment; Pasha movingshot/finiteammo/cd/recoveryHUD; собственные7hero finisher poses/timings/sounds/NPCreactions и полная Input/native/settings/restart/build/performance matrix. Source/world/9staticportraits не заменяют это. См.specs/P06_COMBAT_ACCEPTANCE.md.

## Принятый компонент P06: индикация защиты Олежки

Независимые ART7666fcc6…/Gameplaya896505e…/QAe8783576…/Leadb1d552b2… приняли scoped PASS_COMPONENT для f844e4d. Shared live predicate прежнего guard0.06–0.26s, прежние windup/active/recovery/cooldown, pre-damage incomingblock→отдельныйCorecounter сохранены. Новый HUD показывает подготовку, окно спереди, блок/ответ, recovery/CD, pause/death/revocation; Gabarего не получает, Rубирает старуюошибкувыбора.

Final57headless/78native с21PNG иmovie57; independentQA freshimport+57+31boundary/purity+164oldOleg. Actual27pxthemeoverlap найден наnative01 и сохранён сvisualFAIL; finalUI5px внеарены подтверждёнactualrect/pixelanalysis/286movieframes. Old/full combat regрессии иfinalrestart/readiness/isolation passed. Нет newraster/audio/таймера/уронаизUI; physicalkeyboardlatency/FPS/listening/fullP6 не приняты. Отчёты *-guard-feedback-01 и guard-feedback-01/implementation.md. DEV02actualLinux22+4PNG/Wineheadless18 сновойпанелью упакован.

## AUTOPILOT и возобновление

Условное разрешение P07: automation/decisions/P07_CONDITIONAL_CONTINUATION.json. Требуются fullP06PASS/обязательныйCI/confirmedprotectedmerge +independent readinessPASS, все21MDSLead-approved передmassproduction. Кандидат guard проверяет typed FULL approvals/currenthashes/frozenGitgame/21uniqueMDS. Фактические предпроизводственные capabilities отделены от HIGH OPEN будущих content obligations; полная P07 приёмка и оба fresh merge checks требуют closure по canonicalReadinessSHA/currentP07head/exactIDs/actualhashevidence. StrictJSON отвергает повторные decodedkeys/NaN/Infinity, phasefindings требуютarray. Final v4: **independentQA f2c1d176… и Lead de1fb9f5… PASS_COMPONENT**, actual55+47tests и16ingress/23stage/10oldprobes. Исторические FAIL/снимки сохранены. Это не Root installation/fullreadiness/phase approval. Протокол autopilot/PRODUCTION_GATES.md. **ROOT runner не заменён, stopP06 сохраняется**, безопасный handoff/fullverifier ещёне готовы. P08/release/purchases не разрешены. GitHub merge guards/SHA/CI/protection не обходятся.

Authority только ROOT/automation/phase_state.json. Статус единственного author lease/PID проверять в canonical state и kernel перед resume; последние code/checkpoint/receipt сохранены, одному Markdown не доверять. Последний ownerpreview02 job9a94401ac76c49189e6403fb4c50dc7c CONSUMED_EXIT0 (старыйaa420…такжепотреблён), повторный запуск запрещён. Нет pending generators. ROOT dirty/stashes/private ignoredphotos сохранять. Постоянный daemon не настроен.

Resume: reports/phases/P06/resume/decision.json и current-operation.json. Новые отчёты/коммиты не означают разрешение перехода фазы.
