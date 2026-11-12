# P00 — реализация, ожидает независимого решения

Автор: `/root`. Это инфраструктура, не готовая игра и не vertical slice.

Реализованы задачи `planning/P00_TASKS.md`: локальная приватность, Godot stable 4.7.2 с SHA512 lock официальных архивов и SHA256 бинарника, bootstrap 640×360 с nearest/integer scaling и предупреждением о вымысле, native SceneTree integration harness (без внешних зависимостей), CI workflow с pinned GitHub Actions, Linux/Windows release presets и локальный export runner. Никаких raw-фото, ZIP, image/audio ассетов игры в Git.

Проверки: `python3 tools/verify.py --references --capture` — 7 команд успешно, в integration — 6 assertions. Manifest — 11/11 hashes. Реальные логи в `logs/`, `validation.json`. Скриншот `bootstrap.png` сделан Godot OpenGL на GTX 1050 Ti, не нарисован вручную; автор просмотрел читаемость текста. Независимый reviewer должен открыть его сам.

`python3 tools/export_bootstrap.py` — экспорт Linux ELF и Windows PE с embedded PCK, exit 0; Linux headless smoke и OpenGL render экспортированного бинарника exit 0 (`export_linux.png`). Оба файла в `build/`, hashes в `exports.json` и `artifacts.json`. Windows runtime **BLOCKED**: Windows host и Wine отсутствуют. Это не gameplay validation. Лицензия Godot и third-party notices включены в game/LICENSES и export.

Приватность: `tools/check_privacy.py` проверяет index, reachable history, ignore probes, совпадение raw-фото по Git blob hashes даже при переименовании. Отдельный локальный manifest checker не запускается в публичном CI, где приватных references нет. Screenshot P00 не содержит лиц. Установка только `.tools/`, без sudo и платных API.

GitHub сначала дал connector 422 / gh 404. Владелец затем явно разрешил создать приватный репозиторий и push проверенных файлов без фото. Remote/PR и GitHub CI пока готовятся; это не успешный CI run. Владелец разрешил image_gen с фото всех, но генератор ещё не вызывался: P01 не начат.

Независимый review: выделить отдельный context с `fork_turns=none`, прочитать правила, rerun проверки в `reports/phases/P00/reviewer/`, проверить hashes/diff/screenshots/builds; решение пишет только reviewer. Текущая сессия не постоянный runner.

Известные пределы: нативный test runner пока покрывает только bootstrap; save/combat/story/input-проверки появятся при реализации соответствующих фаз. Аудио/анимации к P00 не относятся и не выдаются за проверенные.
