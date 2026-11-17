# Статус проекта

P00–P06 PASS/MERGED. P06 принята независимыми ART/Gameplay/QA/Lead; mandatory CI reviewed37a0aa5 прошёл. [PR11](https://github.com/Artyx71/Last-Skuf/pull/11) squash f8325212381d67a469b5d9a6dffbf3d244bc9933 подтверждён. Старые FAIL и прерывание130 сохранены.

Сейчас PRE-P07: P07 PENDING/attempt0, массовое производство закрыто. Работает один ROOT executor; независимые reviewers не реализуют код. Нового P07 PR, push или CI пока нет.

Техническая передача AUTOPILOT и исходников A/B/C завершена и независимо принята. ROOT runner d700e88e/schema12, frozen P06 Game533/tools54 из Git f832. Source587, state/index/refs и пользовательские профили сохранены; RootHEAD be4 остаётся controlplane metadata. Fresh canonical import/boot0 и SOURCE actualInput72/72. Independent actual C и отдельный technical safe_handoff PASS: reports/pre_p07/lead-canonical-source-C-installed-01. Это не FULL Readiness. A/B/C apply не повторять. Guard и stop_after_phase=P06 сохраняются.

В PRE-P07 навигационном baseline все3 архетипа проходили open, но застревали у U-wall. В существующий _walk_to добавлен optional host hook, без переписывания FSM/LOS/contact. Source0712e3de исправляет выявленный independent QA boundary defect. Реальные новые проверки: open/U6/6; door/choke/alternate/dynamic/restart/bounds/actualLOScontact70/70; existing character/cast actualInput72/72 на обычном host. Все с изолированными Godot/XDG проектами и pinned engine4.7.2; headless/fixed-fps ticks не означают FPS, native визуальный review, экспорт или hardware latency. ROOT Game и DEV09 не заменялись этим прототипом.

Independent QA02 PASS_COMPONENT (NAV-Q01 закрыт), старый QA01 FAIL сохранён. Независимый Lead PASS_COMPONENT по фактическим70+6+72; reports/pre_p07/lead-navigation-router-01. Полный H02 OPEN: нужны production-host/реальная карта, clearance всех разрешённых героев, движущаяся цель/cached-detour barrier/несколько NPC, investigate/pursue/LOS reacquisition, реальный mission retry/save и native движение/производительность. См. planning/PRE_P07_NAVIGATION_PILOT.md в WorkP07.

Подготовлены4 отдельные substantive draftMDS: CH01/CH09/CH12/CH16. Все4 имеют Narrative component PASS; полных Gameplay/Lead-approved MDS0/21. Ещё нужны17main MDS, полный review21, pacing instrumentation/calibrated pilot, audio playback pipeline и bonus integration contract/FULL Readiness. Только CH01 сейчас сюжетно playable;7–9часов TARGET_NOT_MEASURED.

Живая сборка DEV09: build/P06_DEV_20261117_09/PLAY_LINUX.sh; Windows PLAY_WINDOWS.cmd рядом. Это ранее проверенные P06 Linux/Wine C5 exports,413checks каждый; native Windows NOT_TESTED. F5бой/1–7герои, F6портреты, EnterCH01. Owner принял P06 prototype audio; нового agent listening не заявляется. P08-NPC-STYLE-01 действует.

Последняя privacy35/35:11currentrawrefs,18656reachableGitobjects,0rawidentitymatches. Нового push не было. Фото/manifest остаются приватными; generated isolated projects/profiles/cache/debugkeys не добавлены в Git. Отчёты навигации и независимые decisions сохранены отдельным archive commit.

Resume: reports/phases/P07/resume/decision.json. Authority automation/phase_state.json, mirror .autopilot/STATE.json. Постоянный daemon не настроен.
