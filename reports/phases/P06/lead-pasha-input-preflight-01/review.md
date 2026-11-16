# Pasha Input fixture: targeted execution preflight

**PASS_DIAGNOSTIC_EXECUTION_ONLY** для frozen651d730bfdf6750d92511b841256435eed2f6dd9: один serial ROOT headless, и только после его реального PASS — один fresh Pasha live+Movie. Никаких13-stage rerun, автоматического continuation или product/full-phase acceptance из этого документа.

Самостоятельно прочитан actual Git diff и frozen source. Единственный изменённый Game/tools/assets путь — game/tests/pasha_moving_shot_replay.gd.10прочих critical runtime/inherited fixture/wrapper Git blobs byteexact старому beb. Старый failure96b837… и AVI/trace остаются immutable. Production Input/controller/Core/physics/audio/damage не менялись.

Добавлены8strict held-input checks: каждая запись ammo_trace от declared hold-start до end sample должна иметь ожидаемый Input vector и character_run=true. Записываются vector/run/root.has_focus/NO_FOCUS flag и реальные focus-enter/exit события. Исходные393checks, temporal count и release order, all8poses/run/displacement>70/continuity/lifecycle не ослаблены. Никаких per-frame Input reassertions. NO_FOCUS запрашивается только в non-headless Movie, с явным field; обычный live его не получает. Это соответствует уже применённому WORLD test isolation precedent, не изменяет production game window.

По чтению кандидат разумно использовать для контролируемой диагностики. Он ещё не исполнялся reviewer и не считается компилированным/успешным; headless сначала квалифицирует real Godot syntax/runtime. Прогноз при том же составе8extra:401headless/401Movie/589live. Это не фактические счётчики.

Bounded условия: fresh output/profile/build, source freeze/soleRootstage/released author, после каждого реального результата сохранять raw logs/results/source inventory; при FAIL не продолжать/не relaxed thresholds. Фактические held Input samples и original displacement/animation checks обязательны. При пустой/отсутствующей telemetry или новых drops — сохранять FAIL и дополнить event provenance. До принятия отрицательных controls составной full gate не закрывается.

Root cause старой потери held-run всё ещё UNKNOWN. Requested/readback NO_FOCUS и положительный повтор не доказывают причину external keyboard/focus; исходная запись не содержит этих полей. Новый outcome следует назвать controlled Movie-input evidence, не доказательством вины ОС/владельца. Для causal isolation нужны controlled release/focus negative/raw event observations. Здесь GO разрешает получить эти факты и прогнать прежние assertions, а не провозглашает исправление production bug.

Адресное продолжение remaining5/strict composed13 остаётся отдельным кандидатом/review. First7positive source-bound evidence сохраняется; old failed aggregate не изменять. ПолныйP06/privacy/handoff/GitHubCI/merge/readiness/P07/P08/release/listening/nativeWindows/FPS не одобрены. Reviewer engine starts0, Work/Git/state changes0; прочитаны только code/diff, написаны собственные ROOT reports.
