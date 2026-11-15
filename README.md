# АЫАЫ: Последний скуф — SDD v1.0

**Статус исполнения:** P00–P05 PASS/MERGED; P05 [PR10](https://github.com/Artyx71/Last-Skuf/pull/10). P06 в работе: боевой полигон Габара/Олежки и9 portrait/dialogue sets доступны, остальные персонажные механики ещё не завершены. Только CH01 — готовая сюжетная playable scene;21 глава и7 secret slots — производственный план, не готовая кампания. P06 full PASS не выдан. P07 разрешена условно после полного P06/merge и independent Production Readiness PASS; Lead должен принять21MDS перед массовым производством.
**Цель:** качественный Godot 4 / GDScript single-player Windows/Linux top-down action с собственным pixel-art, сильным саундтреком, драматургией и локальными шутками. Репозиторий: `Artyx71/Last-Skuf` (доступ/существование проверяет Codex, без самовольной публикации).

## С чего начать
1. **Прочитать `AGENTS.md` и `prompts/CODEX_MASTER_PROMPT.md`**. Запустить Codex в рабочей папке, распаковать **в приватный локальный workspace**; не загружать фото публично.
2. Инициализировать проект Godot по `docs/TECH_ARCHITECTURE.md`; локально установить только необходимый софт после проверки наличия и полномочий (без автоматических sudo/платных API).
3. Основной исполняющий агент реализует задания по `planning/PHASES.md`. После каждой фазы строго вызывается независимый `agents/LEAD_REVIEWER.md`; он читает артефакты, логи, скриншоты, музыку и отчёт, затем PASS/FAIL. При FAIL исполнитель чинит и повторяет review в рамках сессии; при PASS назначается следующая фаза.
4. Переход между фазами допускается **только** при наличии evidence и decision-файла. Никаких фиктивных заявлений об успехе. Код/арт/музыка должны быть проверены на деле.
5. Приватные фото используются только как ориентиры для авторского арта. Для публикации чужого изображения/голоса, публичного репо, расходов, внешнего генератора с отправкой фото — требуется разрешение правообладателей/людей и согласование.

## Индекс
- `specs/GAMEPLAY_SPEC.md`, `specs/STORY_SPEC.md`, `specs/DIALOGUE_SPEC.md`, `specs/AUDIO_SPEC.md`: утверждённые направления и тестовые контракты.
- `docs/CHARACTER_BIBLE.md`, `docs/ART_BIBLE.md`, `docs/TECH_ARCHITECTURE.md`, `docs/ASSET_PIPELINE.md`, `docs/PROJECT_GATES.md`, `docs/SECURITY_AND_RIGHTS.md`.
- `planning/PHASES.md`, `planning/TRACEABILITY.md`, `agents/*.md`, `automation/REVIEW_LOOP.md`.
- `prompts/CODEX_MASTER_PROMPT.md`: мастер-поручение Codex.
- `assets/references/characters`: **10 оригинальных фото**. `assets/references/ui`: визуальный референс интерфейса (НЕ копировать в игру).
- `assets/references/manifest.json`: ID, пути, SHA-256. `tools/validate_pack.py`: контроль пакета.

## Ключевые утверждения
- Сильный гротеск у всех, максимальная узнаваемость по фотографиям. Исключительно пиксельная графика в финальных ассетах; предыдущие генерированные коллажи НЕ входят в production baseline.
- VHS и графическое насилие с пользовательским переключателем; читаемость/управление не должны деградировать.
- 7 игровых героев, 3 важных второстепенных героя на фото; 21 главная сюжетная позиция как план, нелинейное повествование, выборы с действительно разными игровыми ветками и концовками. `WIFE CALLING` — канонический путь.
- Криминал вокруг PRIME и Кабана — **сугубо вымышленный сюжет**, не заявление о реальном человеке.
- Godot 4 / GDScript, Windows+Linux с первого vertical slice, атомарные коммиты и PR по фазам.
- **Не путать** Элю (Тимка) с Элланой/Жинькой (Якудза). Никогда не копировать чужие спрайты, саундтрек, диалоги или игру Hotline Miami.

## Локальная проверка прототипа

Принятые исторические сборки P04: `build/P04/native-host-03/linux/last-skuf.x86_64`, `build/P04/native-host-03/windows/last-skuf.exe` (локальные экспортные артефакты, не релиз). В текущем прототипе Enter открывает главу01, J/F4 — журнал глав. Запуск доступен только дляCH01; повтор сохраняет canonical story. В главе01: забрать куртку у раковины, открыть служебку и уйти во двор. WASD/стрелки — движение; F — действие, E — отвлечение, Space/ЛКМ — слабый толчок; R — retry/повтор; O/Esc — пауза, Q в паузе — меню. В диалоге Space раскрывает/продвигает текст, Shift ускоряет, H показывает журнал, K пропускает просмотренное. F1/F2/F3 из меню сохраняют арт/бой/диалог P01–P03.

`python3 tools/verify.py --output <новая-папка>` — regression. `python3 tools/analyze_p04_audio.py --output <новый-json>` — сигнальный анализ, **не listening**. `python3 tools/verify_p04.py --output <новая-папка> --exports --movie` — реальные captures/replay/exports в окружении с разрешёнными display/audio/Wine sockets; `--headless` проверяет Input/AI/save без графических доказательств. Старые P03 evidence/decisions сохранены. Билды Windows должны проверяться отдельно; экспорт PE не считается запуском.

## Последовательный AUTOPILOT

Команды/state/recovery/защищённый squash workflow: [docs/AUTOPILOT.md](docs/AUTOPILOT.md). Репозиторий публичный по явному разрешению владельца; rawphotos исключены. Авторизация merge условная: независимый exact-SHA PASS + mandatory CI + GitHub approval/rules без bypass. Combat & Gore запланирован как [P04G](specs/COMBAT_GORE_POLISH_SPEC.md) после vertical slice и обязателен до P07. P04G и P05 приняты и merged. P06 и новая Production Readiness/планирование P07 продолжаются по отдельным gates; см. reports/STATUS.md и planning/PRE_P07_REQUIREMENTS.md.


P05: `python3 tools/verify_p05.py --headless --output <новая-папка>` — story/schema/migration/graph и реальные Input replay, без rendered/listening claims. Хост: `python3 tools/verify_p05.py --exports --movie --output reports/phases/P05/attempt1/native-host-01 --build-output build/P05/native-host-01`. Детальные границы и conservative defaults: [P05 design](reports/phases/P05/attempt1/design.md). Три primary routes + REAL_PRIME post-story overlay — eligibility/production plans, не готовые финальные уровни.

Для каждого повторного прогона нужна новая папка evidence. Native P05 QA задаёт `--disable-vsync --max-fps 60` для воспроизводимого темпа отображения, сохраняя реальные часы физики и лимит retry <1000 мс. MovieMaker отдельно записывает при fixed-fps60; он не заменяет live-проверки. P04-процентили physics delta не доказывают wall-frame FPS. Перед `--exports` подключите существующий разрешённый `.tools/wine/usr/bin/wine`; проверка наличия не заменяет фактический запуск PE. Условия и история FAIL сохранены в [attempt2 remediation](reports/phases/P05/attempt2/remediation.md).

## Текущий тестовый полигон P06

F5 из меню открывает бой персонажей (сейчас готовы Габар/Олежка), F6 —9 portrait/dialogue наборов. В бою:1/2 выбор готового героя, WASD/Shift движение, Space толчок, F особый приём, V добивание по уязвимой цели, Tab разрешённый инструмент, C отмена до контакта, O настройки, R повтор, Esc меню. Неготовые герои не подставляют другой спрайт/способность. Это DEV-прототип, не полный P06 и не релиз. У Олежки HUD показывает подготовку, живое окно фронтального парирования, успешный блок/ответ, восстановление и cooldown; отмена/смерть/пауза не оставляют ложное открытое окно. Scoped ART/Gameplay/QA/Lead evidence: reports/phases/P06/guard-feedback-01 и *-guard-feedback-01. Локальный обновлённый build: build/P06_DEV_20261115_02 в ROOT (Linux renderer22/Wine headless18; native Windows отдельно NOT_TESTED).

Локальный preview exporter: `python3 tools/export_p06_preview.py --output <новая-папка-evidence> --build-output <новая-папка-build>`. Он реально экспортирует Linux/Windows и проверяет packaged menu/готовые fixtures: Linux с renderer, PE под Wine headless; native Windows отдельно NOT_TESTED. Сборка не даёт phase PASS, FPS или слуховую приёмку.
