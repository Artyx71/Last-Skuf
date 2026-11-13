# P00 — независимый Lead Review, попытка 2

**Решение: PASS.** Reviewer: `/root/lead_reviewer`; автор реализации: `/root`. Проверенный implementation commit: `d2f3fd9a751a268ea621c30b9cb12bffac9f360c`. [Draft PR #1](https://github.com/Artyx71/Last-Skuf/pull/1). Это разрешение перехода к P01, не merge или release approval.

Историческая попытка 1 по fd746b6 остаётся BLOCKED: `review-attempt1.md` и `decision-attempt1.json` сохранены, все их evidence hashes повторно проверены без расхождений. Локальная техническая проверка первой попытки остаётся действительной: Godot, сцена, тесты, installer, export presets и lock не менялись. Сверены diff fd746b6..d2f3fd9 и hashes production исходников; working tree совпадает с проверенным commit для game/tools/workflow/.gitignore.

## Закрытие findings

**B-P00-01 закрыт фактическим CI execution.** [Run 43316247166](https://github.com/Artyx71/Last-Skuf/actions/runs/43316247166) на head d2f3fd9 завершён SUCCESS. Самостоятельно получены API и полный job log; завершены все восемь service/workflow steps: setup, checkout, pinned install, verify, Linux/Windows exports с Linux smoke, upload, checkout cleanup и complete. CI выполнялась на временном self-hosted Linux runner текущей машины, не на GitHub-hosted Ubuntu и не на Windows. Наличие настоящего GitHub job подтверждено API; локальный запуск не выдан за hosted CI.

Из artifact `13987953143` reviewer самостоятельно скачал ZIP и получил SHA256 `06006b9a9468dadbaea6f5f4a1838904755b57b0f7b00bf6ff6294a6f692a8f8`, в точности равный API digest. Просмотрены все 8 файлов: два build и шесть validation/log файлов. References или посторонних файлов в artifact нет. `validation.json`: privacy, version, import, smoke, integration — 5/5 PASS; native SceneTree — 6/6 assertions PASS. Скачанный из GitHub Linux executable дополнительно запущен reviewer: headless smoke exit 0, без ошибок.

**D-P00-02 закрыт.** Новые SESSION_HANDOFF/P00_TASKS описывают private remote, draft PR и реальный CI. Актуальные working-tree STATUS/NEXT_ACTION/phase_state и implementation-attempt2 описывают attempt1 и временный runner; исторический toolchain_audit явно сохранён как snapshot. Reviewer сохраняет копии актуальных файлов в `reviewer-attempt2/snapshot_*`; меняющиеся controller-файлы не включены в evidence напрямую.

## Runner lifecycle и privacy

Изменение workflow ограничено выбором `vars.AYAY_RUNNER` с default ubuntu-24.04 и устранением двойного push/PR запуска. Pinned checkout/upload actions и permission `contents: read` сохранены.

Самостоятельно проверены официальный [actions/runner v2.338.2](https://github.com/actions/runner/releases/tag/v2.338.2) release digest и реально скачанный tar: SHA256 `baebf204307bac6193480852732f0aba2ae97b6c5597c244f4d5558390147c40`. Перед окончанием job API показывал единственный занятый runner `last-skuf-session-p00`; после завершения и cleanup reviewer повторно получил runners `total_count=0`, variables `total_count=0`. Процессы Runner.Listener/Runner.Worker отсутствуют, `.runner`, `.credentials*` и `.service` отсутствуют. Конфиг до удаления не удалось прочитать; auto-removal не доказывается одним author report, однако итоговое отсутствие регистрации/credentials/process/service подтверждено независимо. Постоянный runner не остаётся.

Отдельный checkout — merge commit `601f72fd215ab1bbf360c1e7ace2163627a96166` с parents main 5c66c28 и проверенным d2f3fd9. `assets/references` в checkout отсутствует; совпадений raw reference Git blob hashes нет; Git HTTP extraheader credentials отсутствуют. После cleanup повторён privacy checker — PASS. В новых reviewer evidence не найдены проверяемые credential patterns. Raw фото не загружались reviewer и не включены в artifact. Разрешение владельца на image_gen не заменяет likeness signoff.

## Разные hashes CI и первоначальных builds

CI build SHA256: Linux `6592253329680278ad96612bd62b59f92647089cfff7000bedaa9aaa5c69800f`; Windows `ebf22b6e5947de1a007ce97ab888d3a8bea8f794985430efddd753df93da1cc2`.

Эти hashes отличаются от первоначальных local exports. Reviewer проверил embedded PCK по [официальному формату Godot 4.7.2](https://github.com/godotengine/godot/blob/4.7.2-stable/core/io/file_access_pack.cpp): 9 ресурсов, 8 полностью одинаковы; в bootstrap.scn отличаются ровно 4 байта. Оба binary scene дополнительно загружены нативным Godot, получены `_bundled` dumps: единственное различие — `node_ids` 880746999 против 1603180361. Все names, nodes, variants, script UID и другие данные совпадают. Bytecode, project.binary, remaps, UID cache, оба license notices равны. Original Windows PCK равен original Linux PCK по resource hashes; CI Windows PCK равен CI Linux PCK. Tests и references в PCK отсутствуют. Функционального расхождения не найдено. Детерминированность экспортов между чистыми imports не требуется P00; нельзя называть эти разные builds побайтно одинаковыми.

Evidence: `reviewer-attempt2/ci_run.json`, `ci_job.log`, `ci_artifact_api.json`, `ci_artifact_verified.json`, `ci_*.log`, `downloaded_linux_smoke.log`, `runner_audit_before.json`, `runner_cleanup_audit.json`, `reviewed_source_hashes.json`, `pck_inventory.json`, `scene_binary_difference.json`, оба `*_scene_bundle.txt`, `payload_semantic_audit.json`. Скачанные ZIP/builds в ignored `reviewer-attempt2/build/`, их hashes зафиксированы в decision; не добавлять большие outputs в Git.

## Scope и ограничения

P00 bootstrap удовлетворяет headless/privacy/toolchain/exports/review/CI gate. В первой попытке reviewer сам открыл bootstrap.png и export_linux.png, проверил читаемость disclaimer и отсутствие лиц; файлы/сцена не изменились, их hashes сохранены. Никакого повторного art/audio/gameplay signoff не заявляется.

Windows runtime **не проверен**; PE export не заменяет Windows запуск. Для P00 это документированный предел; перед соответствующим vertical-slice gate потребуется реальная Windows QA. Hosted account billing остаётся ограничением будущих hosted запусков: variable удалена, default workflow снова выбирает ubuntu-24.04. Для следующего CI потребуется доступный разрешённый runner или восстановленный hosted account; это не отменяет фактически выполненный текущий job и не обещает постоянного фонового исполнения.

Открытых CRITICAL/HIGH findings нет. LOW observation N-P00-03: hashes чистых exports меняются из-за generated scene node ID; хранить hashes каждого реально проверенного build, не утверждать cross-import byte reproducibility.

## Handoff

Активному исполнителю разрешён P01 по planning/PHASES: один настоящий pixel portrait Якудзы и согласованный top-down sprite, исходники, native test scene и первое движение; независимая photo-likeness/pixel/engine QA. Не расширять scope до P02/P03 и не считать разрешение на image_gen или этот PASS художественным signoff. Сохранить P00 PR без merge до отдельной авторизации. Обновить controller/STATUS/NEXT_ACTION на основании decision PASS; raw references не включать в Git. Reviewer код не исправлял, commit/push/merge не выполнял.
