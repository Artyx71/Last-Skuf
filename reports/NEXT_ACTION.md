# Возобновление

Прочитать AGENTS.md, specs, planning/PHASES.md, automation/phase_state.json, reports/phases/P01/decision.json (если готов) и последний P00 PASS decision-attempt2.json. P01 BLOCKED, attempt 1: независимый Lead Reviewer завершил review, обязательный человеческий signoff сходства/гротеска PENDING. Decision: reports/phases/P01/decision-attempt1.json. Все 103 evidence-хеша совпали, технических HIGH/CRITICAL нет. Не переходить P02 до P01 PASS.

Владелец должен только оценить готовые previews, не пересылать отчёты: reports/phases/P01/portraits_preview_2x.png, portraits_past_preview_2x.png, world_preview_3x.png; video movement_replay.mp4. Запрос/хеши: human_art_review_request.json. В активной сессии задан async вопрос. После фактического ответа сохранить human_art_review_response.json с точным вердиктом и hashes; не менять архив request checkpoint. При художественных замечаниях передать art production и повторить независимый review в пределах 3 попыток. Не считать разрешение на image_gen человеческим art approval.

Команды: python3 tools/verify_p01.py (author final files переписывает — для нового attempt использовать отдельный каталог/снимок); reviewer rerun python3 tools/verify.py --references --capture --output reports/phases/P01/reviewer-attemptN. Сборки: build/P01/linux/last-skuf.x86_64 и build/P01/windows/last-skuf.exe. Запуск Linux и Enter открывает lab; WASD/стрелки, 1–5 — эмоции, Tab — эпоха, Esc — выход. Windows runtime не проверен.

PR #2 https://github.com/Artyx71/Last-Skuf/pull/2; base phase/p00-bootstrap; no merge. P01 CI 43319881768 SUCCESS, проверенный source HEAD fcf3999; скачанные artifacts в build/ci-P01, logs/session_ci.log и session_ci_result.json. Временный runner завершён; AYAY_RUNNER/registrations/credentials удалены. Постоянного runner/daemon нет, после сессии исполнения не обещать.

Разрешения: создать private repo и push проверенных файлов без raw фото; image_gen с фото всех. Raw references не публиковать, private repo не делать public, не merge/release/менять платежи. Публичные likeness/voice права не получены. Без P01 PASS не начинать combat/audio; последняя PASS-фаза — P00.

После ответа человека не повторять всю техническую валидацию без изменения исходников: проверить фактический ответ и точные hashes, передать отдельному Lead Reviewer на attempt 2. Если человек требует правки — исправить арт, обновить только затронутое evidence и повторить review. Nonblocking ART-P01-01/META-P01-01 описаны в review-attempt1.md.
