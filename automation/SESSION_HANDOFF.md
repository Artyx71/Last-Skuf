# Исполнение и независимый review

P00 использует доступный `collaboration.spawn_agent`: отдельный Lead Reviewer с `fork_turns=none`, исходные правила и доказательства он читает самостоятельно с диска. Автор реализации — `/root`; reviewer не исправляет код. У каждого решения есть reviewer ID, attempt, hashes, findings и следующий шаг. Не считать markdown-план review доказательством его выполнения.

Активный исполнитель после PASS читает решение и начинает следующую фазу; после FAIL выполняет конкретные исправления и повторно вызывает того же reviewer. Не более трёх попыток. При BLOCKED сохраняет зависимость и остаётся внутри текущей фазы. Все переходы сохраняются в `automation/phase_state.json`, `reports/STATUS.md`, `reports/NEXT_ACTION.md`.

Команды P00:

```sh
python3 tools/install_deps.py --templates
python3 tools/verify.py --references --capture
python3 tools/package_evidence.py P00
```

Публичный CI не содержит фото и не запускает `validate_pack.py`; приватный локальный прогон обязан запускать `--references`. CI проверяет исходники, экспортирует Linux/Windows bootstrap и запускает Linux headless smoke. CI не является художественным или музыкальным review, и Windows export не заменяет Windows runtime test.

Постоянный агент/runner не установлен. Hosted workflow реально был поставлен в очередь и заблокирован до steps из-за биллинга аккаунта. Приватный remote и PR #1 созданы с разрешения владельца. `AYAY_RUNNER` позволяет временный локальный single-job runner, default — ubuntu-24.04; variable/registration удаляются после проверки, сервиса нет. Коммиты и PR не публикуются автоматически без соответствующих прав. Raw references и любые фото-производные остаются локальными; никакой отправки в генераторы без отдельного согласия.
