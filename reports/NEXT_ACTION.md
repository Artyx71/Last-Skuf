# Возобновление

Прочитать AGENTS.md, specs, planning/PHASES.md, automation/phase_state.json и reports/phases/P00/decision-attempt2.json (PASS). Последняя PASS P00. Следующая P01: реальный пиксельный Якудза (портреты/4-way idle+walk), native movement sandbox, animation capture, structural tests, независимое сравнение с правильным фото и человеческий likeness signoff. До P01 PASS не начинать P02.

Разрешения владельца: private Artyx71/Last-Skuf и push проверенных файлов без raw фото; image_gen с фото всех. Не merge/release, не публиковать raw фото. P00 PR: https://github.com/Artyx71/Last-Skuf/pull/1. Дальнейшие PR делать stacked без самовольного merge. Raw references исключены из Git и exports.

Сборки P00: build/linux/last-skuf.x86_64 (runtime/render PASS), build/windows/last-skuf.exe (export PASS, runtime не проверен). CI 43316247166 SUCCESS с downloaded artifacts в build/ci-P00. Временный runner полностью завершён, API registrations=0, AYAY_RUNNER удалена. Для будущего GitHub CI нужен новый явно временный user-local runner либо восстановленный hosted account; постоянного агента/daemon нет. Платёжные настройки не менять.
