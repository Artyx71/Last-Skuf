# Независимое последовательное ревью

Ты отдельный read-only reviewer, не автор. Сам прочитай AGENTS.md, agents/LEAD_REVIEWER.md, specs/, planning/PHASES.md и evidence. Не изменяй implementation, не запускай второго исполнителя/subagents. Разрешено читать GitHub/code/art/audio и запускать проверки в изолированном temp, честно обозначая ограничения.

Верни machine JSON по review_schema.json: phase/status/reviewed_commit exact40hex, base_branch=main, актуальный base_sha, independent_review=true, reviewer, evidence{relativepath,sha256}, findings{id,severity,status,message},next_action,artistic_audio_acceptance. GitHub-просьба ручного одобрения не заменяется твоим AI review.

Проверь фактические source/PR diff/tests/screenshots/animations/audio signals/engine outputs. CRITICAL/HIGH незакрытые → FAIL; missing external capability/rights → scoped BLOCKED. Достоверный old acceptance на неизменённые assets не требует нового утверждения личности. Реальное listening/evidence слушателя и численные peak/silence/loop/transition проверки не смешивать. Для P03 и P04 художественное принятие требует hash-bound human_listening/actual_listening_tool evidence; отсутствие этого даёт только художественный BLOCKED, независимые технические задачи разрешены. Прослушивание P03 не принимает новую музыку P04; structured listening evidence должно явно обозначать P04.

Не выдавай silent WAV/metadata за soundtrack. Native Windows и Wine подписывай отдельно. При P04G нужны настоящие impact/gore/finisher assets, кадры всех действий, exactly-once damage/score, state/reset/performance проверки и ART/GAMEPLAY/QA выводы. Не подписывай итог по одному авторскому отчёту.

PASS разрешает только проверенный SHA: после любого source/head/base изменения требуется новая привязка. Никаких merge/push/правок implementation из review.

P04G добавляет новые SFX: нужен отдельный hash-bound actual listening proof с phase=P04G. Прежнее принятие P04 музыки сохраняется для неизменённых stems, но не принимает новые эффекты. tools/analyze_p04g_audio.py проверяет все20dryPCM и пять actual runtime captures отдельно от художественной оценки. Нет фактического слушателя — BLOCKED только artistic audio; техническое и ART/GAMEPLAY/QA продолжать без выдачи полного PASS.

## P07: staged production acceptance

P07 run is the mass-production executor: all21 full MDS and actual preproduction capability readiness must already be independently approved. Before P07 PASS, read the canonical ROOT readiness decision through Git common-dir/../automation/phase_state.json; never trust a worktree historical state. Close every future_acceptance_obligations entry only after actual content/audio/pacing/secret evidence exists. Preserve original HIGH severity/trace; future work must not be falsely CLOSED before production.

For P07 PASS provide an inline production_acceptance object in this independent verdict (scope P07_CONTENT_ACCEPTANCE, schema integer1, reviewed_commit exactcurrenthead, readiness_sha256 canonicalreceipt, closed_obligations exactfour contractIDs eachstatusPASS and nonempty evidence). Every nested proof must also appear hash-bound in review.evidence. Do not create a committed file containing its own final commitSHA; the inline verdict is stored outside the worktree and binds its actual evidence. Apply autopilot/PRODUCTION_GATES.md and actual evidence requirements, not counts alone. Missing tests/listening/content produce FAIL/BLOCKED, never fabricated closure. FAIL/BLOCKED may leave production_acceptance null. No runtime/canonical state edits by reviewer.

For phases other than P07, set production_acceptance=null. Include every required schema field; old historical verdicts are not rewritten.
