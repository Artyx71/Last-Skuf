# P04 — реализация THE MISSED FIGHT, attempt 1

Авторский implementation handoff, **не решение Lead и не PASS фазы**. Работа выполнена только в `phase/p04-implementation`, база `5ad9251eadbd90654123c6e197f8b370cadc45c3`. Основной контроллер: `/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0/automation/phase_state.json`; он остаётся authoritative, P04 attempt 1. P00–P03 PASS/attempts/артефакты и snapshot состояния не сбрасывались. Входные findings: `[]`.

## Реализованный результат

Enter из стартового экрана открывает главу 01 `CH01_THE_MISSED_FIGHT`, прошлое, 14.10.2023 22:18, POV Якудзы. Центральная драка за дверью не выигрывается: герой уходит через туалет/служебку/двор. Нет скрытого forced damage или неуязвимого противника. Игрок забирает куртку с ключом, открывает две реальные двери, отвлекает противника, отвечает Жиньке и выходит. Уход без убийств даёт 1000 очков; насилие не вознаграждается. Следующие главы не реализовывались.

Карта 1152×640, камера 640×360, собственные tiles/props/двери/окружение, коллизии стен и предметов, внешние русские intro/phone/outro, animated portrait P03, история/ускорение/пропуск просмотренного текста, пауза и настройки. Checkpoint записывается после пересечения служебной двери; retry возвращает seed, AI, ключ, двери и чистый CombatSystem. Отдельный atomic save хранит прогресс одной главы, лучший результат и once-only completion. Повреждённый save сохраняется для восстановления; неудачная запись не выдаётся за завершение главы. Replay не сбрасывает canonical completion.

Архитектура сохранена: `missed_fight.gd` наследует `combat_lab.gd`; CombatSystem/contact clock, CombatPlayer и EnemyActor не менялись. В CombatLab добавлен только путь config. AudioDirector получил выбор главы через тот же synchronized player, без второго микшера; retry не перезапускает stem. OptionsStore получил обратно совместимый `reduced_gore`: сейчас это только цвет смерти Якудзы. Gore/finishers/reactions — будущая P04G, её критерии не менялись.

Дизайн/управление: [P04_MISSION_DESIGN.md](../../../planning/P04_MISSION_DESIGN.md). Исходники: `game/scripts/levels/`, `game/scripts/ui/mission_ui.gd`, `game/resources/chapters/`, `game/resources/dialogue/missed_fight_*.json`.

## Assets и provenance

- `assets/source_art/missed_fight/render.py`: оригинальные явно нарисованные пиксельные элементы через Pillow 13.0.0, палитра 32 цвета, без ресемплинга/фото/внешнего генератора/чужих изображений. Runtime: `game/assets/art/missed_fight/{tiles,props,doors,world}.png`, atlas JSON. `provenance.json` содержит размеры/метод/SHA-256. Это реальные raster assets с исходником; художественная production-приёмка **ожидается**, качество не самоутверждено. Просмотренный автором `world.png` — source preview, не engine capture.
- `assets/source_audio/missed_fight/`: настоящие 24-bit WAV masters, новая партитура E minor, 144 BPM, 8 тактов / 640000 frames / 48 kHz; четыре OGG stem и новый door SFX. DSP развивает собственный P03 renderer; чужие samples/записи/реальные голоса не используются. Source и provenance сохранены; listening новых файлов не выполнялся.
- Повторно использованные P01–P03 sprites/портреты/enemy art/аудио и три combat/actor/AI скрипта проверены побайтово: **33 файла не изменены**, [reused_source_integrity.json](attempt1/reused_source_integrity.json). Ранее полученная приёмка P03 не переносится на новый трек или новый игровой mix.
- В `licenses/ASSET_LICENSES.csv` добавлены 9 отдельных asset entries. Публичный репозиторий разрешён; отдельный game release не разрешён. Rawphotos/секреты/ZIP не добавлялись, расходы/real voice cloning/генераторы/установки/sudo отсутствуют.

## Проверки и реальные ограничения

| Контракт | Доказательство | Наблюдение |
|---|---|---|
| T-GP02-004: реальный nonlethal маршрут | [engine replay](attempt1/technical-final/engine_replay.json), [reduced replay](attempt1/technical-final/reduced_visual_replay.json), [Linux export replay](attempt1/technical-final/linux_export_replay.json) | Все **50** checks в каждом прогоне; настоящий Godot Input/controller/AI, не отдельная симуляция, route warps = 0, kills = 0. Все прогоны **headless**, не ручной playtest |
| T-GP01-004: AI death/retry/determinism | те же replay JSON, `deaths` и `deterministic_reset_*` | В каждом прогоне 10 смертей от настоящего AI; полный reset snapshot одинаков после каждого retry. Наблюдавшийся death-to-control **260.476–267.750 мс** на этом окружении, не гарантия для другого ПК |
| T-DL01-004: диалог/пауза/безопасный skip | `dialogue_freezes_actor_clock`, `dialogue_space_does_not_attack`, `pause_freezes_world_dialogue` в replay | Актёры/physics/action clock останавливаются; Space после последней строки не инициирует толчок. UI/animated portrait требуют визуальной проверки |
| T-TEC01-004: save/checkpoint/failed I/O | [mission.log](attempt1/regression-final/logs/mission.log) | **28/28**: locked/open collision rays, key, checkpoint, failed completion I/O, corrupt-save preservation, fresh load, once-only completion и replay |
| T-VIS02-004: options compatibility/noninterference | [options.log](attempt1/regression-final/logs/options.log), [comparison](attempt1/visual_option_noninterference.json) | **28/28** options tests; P03 save получает default нового поля. Full/reduced/VHS-off/reduced-motion дают одинаковые seed/RNG/health/position/score/canonical result |
| Regression P00–P04 | [validation.json](attempt1/regression-final/validation.json), [summary](attempt1/regression-final-summary.log) | **815 Godot assertions**, **16/17** command checks. Единственный неуспех — editor import: локальный TCP listen запрещён sandbox; assets при этом импортируются. Итоговый exit **1**, не выдаётся за полностью зелёный CI |
| T-AU01-004: actual decoded signals | [audio_signal.json](attempt1/audio_signal.json) | **5 OGG + 5 mixes**: декодирование, exact loop length, конечные samples, RMS, clipping, seam bounds. Отдельные mixer WAV в technical-final — Dummy-driver numerical capture, **не realtime playback/listening** |
| Native Linux/Windows export | [exports.json](attempt1/technical-final/exports.json), [validation](attempt1/technical-final/validation.json) | ELF и PE созданы, hashes/sizes записаны. Linux ELF выполняет все 50 replay checks и завершает работу без resource-leak errors. Export commands exit 0, но журналы содержат sandbox TCP errors: export log checks не зелёные |
| Windows runtime | [Wine probe](attempt1/technical-final/logs/windows_wine_probe.log) | **BLOCKED**: `wineserver: bind: Operation not permitted`; native Windows **NOT_TESTED_UNAVAILABLE**. Экспорт PE не подменяет запуск |
| Actual engine captures / GPU performance | [native probe](attempt1/environment/native_capture_probe.log), [status](attempt1/environment/native_capture_status.json) | **BLOCKED**: X11 unavailable / Wayland connection refused sandbox. Новых runtime PNG/видео **нет**. Headless frame timings не являются графическим FPS benchmark |
| Exact source identity | [source_hashes.json](attempt1/technical-final/source_hashes.json), `sources_unchanged` | Game files не менялись во время final technical run. Это content hashes грязного worktree, **не exact-commit review/CI receipt** |

Финальный technical runner: **13/16** checks зелёные; 3 открытых — export_linux/export_windows local TCP errors и Windows Wine socket probe. Итоговый exit **1**, missing renderer/listening дополнительно отражены явно. Исторические development и intermediate technical проверки сохранены, не подменены финальными логами.

## Исправления, подтверждённые проверками

Первый авторский прогон обнаружил движение sprite/action state в паузе и преждевременную проверку phone trigger. Freeze теперь отключает обработку актёров вместе с дочерними animations; replay проходит в глубину phone zone. Добавлены запрет утечки Space в melee и полная остановка во время диалога. Коррумпированный JSON разбирается без глобального error-log при ожидаемой невалидности. Options regression обновлён под обратно совместимое двенадцатое поле.

Intermediate Linux export обнаружил resource leaks при возврате к P03 score после shutdown. `select_music` теперь отказывает после shutdown/отсутствия готового mixer. Final Linux export повторил полный маршрут/10 deaths/retry и вышел без этих ошибок. Неудачные результаты сохранены: `attempt1/dev-headless/`, `attempt1/development/`, `attempt1/regression/`, `attempt1/technical/`. Это development evidence внутри attempt 1, не fabricated Lead FAIL и не новые review attempts.

## Коммиты, review и следующий шаг

**Коммит не создан.** `git add` exit 128: общий `.git/worktrees/P04/index.lock` находится на read-only filesystem ([probe](attempt1/environment/git_add_probe.log)). В этом managed executor approval policy = never; обхода через альтернативные ref/index/object directories не было. Все source/evidence лежат в worktree. Список файлов/группы для коммитов — `staging_manifest.json`; helper `commit_source_and_evidence.py` предназначен контроллеру с записью в общий gitdir. Build binaries остаются в ignored cache, SHA/размеры — в evidence. Не включать >100 MB Windows PE в Git.

**INDEPENDENCE_BLOCKED_IN_EXECUTOR.** Subagents, второй Codex и recursive runner явно запрещены. Автор не создавал `review.md`/`decision.json`, не утверждал P04, не запускал CI/PR/push/merge и не менял gates/state/visibility/protection/billing. Отдельный read-only Lead назначается контроллером после настоящих captures/listening/Windows runtime и commit; затем обязательный CI текущего SHA.

Точные внешние work orders: [required_followup.md](attempt1/environment/required_followup.md), [listening_request.json](attempt1/listening_request.json). До их выполнения P04 не может получить PASS; P04G/P05/P07 не запускались. Полный inventory actual source/evidence/build hashes — `artifacts.json`. Владелец не должен переносить отчёты в другой чат: контроллер читает эти файлы напрямую.
