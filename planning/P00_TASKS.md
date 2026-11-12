# P00 — атомарные задачи

| ID | Результат | Проверка |
|---|---|---|
| P00-01 / PRI-01 | Локальный Git, исключения фото, ZIP, секретов | T-PRI-001: 11 hashes; T-PRI-002: index/history + ignore probes |
| P00-02 / TEC-01 | Godot stable 4.7.2, SHA-512 lock, installer без sudo | T-TEC-001: binary checksum + exact version |
| P00-03 / TEC-01 | Нативная bootstrap-сцена 640×360, disclaimer | T-TEC-002: import, headless smoke, SceneTree tests, реальный render |
| P00-04 / TEC-01 | CI, Linux/Windows export presets, platform audit | T-TEC-003: локальный runner; exports только при наличии templates |
| P00-05 / OPS-01 | Evidence с hashes, diff, отдельный Lead Reviewer, resume | T-OPS-001: reviewer сам читает файлы и запускает проверки |

Не считать bootstrap игровой сценой, рисунком или музыкальным прототипом. P01 начинается только после независимого PASS P00. Репозиторий недоступен через connector (422) и gh (404): remote/PR — внешняя зависимость, ничего не создавать и не публиковать.

Минимальная установка: скачать официальный Godot Linux 4.7.2 в `.tools/`, сверить официальный SHA512-SUMS, распаковать только локально. Export templates — того же релиза; Python stdlib достаточен для P00. Нет sudo, платных API и системных изменений.
