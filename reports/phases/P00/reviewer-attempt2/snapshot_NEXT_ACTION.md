# Возобновление

Прочитать AGENTS.md, specs, planning/PHASES.md и automation/phase_state.json. Последний независимый gate: reports/phases/P00/decision-attempt1.json — BLOCKED. Никакого P01 до PASS.

Проверить `gh run view 43316247166 --repo Artyx71/Last-Skuf --json status,conclusion,jobs`. Временный single-job runner запущен в .tools/actions-runner, service не установлен. После job убедиться, что repo registration удалена (`gh api repos/Artyx71/Last-Skuf/actions/runners`), удалить repo variable AYAY_RUNNER (`gh variable delete AYAY_RUNNER --repo Artyx71/Last-Skuf`). При оставшейся регистрации удалить её API, не сохранять token в reports. Собрать реальные logs/artifacts нового CI и запросить отдельный reviewer attempt2; не перезаписывать исходные logs/artifacts.json попытки1.

Приватный repo и draft PR #1 доступны: https://github.com/Artyx71/Last-Skuf/pull/1. Разрешения владельца: создать private repo и push проверенных файлов без raw фото; использовать image_gen с фото всех. Merge/release не разрешены. Билды P00: build/linux/last-skuf.x86_64 (runtime/render проверены) и build/windows/last-skuf.exe (export проверен, runtime нет). Это bootstrap, не playable slice.
