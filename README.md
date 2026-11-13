# АЫАЫ: Последний скуф — SDD v1.0

**Статус исполнения:** P00–P04G PASS и merged. P04G: независимый accepted decision для `9128605`, squash PR9 `7560546`, human acceptance сохранены в `reports/phases/P04G/`. P05 story infrastructure реализуется как отдельный кандидат: реестр21плановых глав, StoryState, D01–D06, планы маршрутов и игровой журнал; phase PASS ещё не заявлен. Только CH01 имеет готовую playable scene. Полная кампания ещё не готова.
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

Команды/state/recovery/защищённый squash workflow: [docs/AUTOPILOT.md](docs/AUTOPILOT.md). Репозиторий публичный по явному разрешению владельца; rawphotos исключены. Авторизация merge условная: независимый exact-SHA PASS + mandatory CI + GitHub approval/rules без bypass. Combat & Gore запланирован как [P04G](specs/COMBAT_GORE_POLISH_SPEC.md) после vertical slice и обязателен до P07. P04G принят и merged; P05 ожидает собственных native evidence и независимых Narrative/QA/Lead gates.


P05: `python3 tools/verify_p05.py --headless --output <новая-папка>` — story/schema/migration/graph и реальные Input replay, без rendered/listening claims. Хост: `python3 tools/verify_p05.py --exports --movie --output reports/phases/P05/attempt1/native-host-01 --build-output build/P05/native-host-01`. Детальные границы и conservative defaults: [P05 design](reports/phases/P05/attempt1/design.md). Три primary routes + REAL_PRIME post-story overlay — eligibility/production plans, не готовые финальные уровни.
