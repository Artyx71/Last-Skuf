# Независимый Lead02 — Тега, кандидат c8

**FAIL_COMPONENT.** Исходные два дальних переноса теперь корректно отвергаются, но весь контракт TEGA-L01 пока не закрыт. На `c8f465840ec970e6abdcb9d41e1f0cbed8fc38bd` фактически воспроизведены **TEGA-L02** (устаревшая физическая форма вместо актуального Node geometry) и **TEGA-L03** (старый job отменяет новый приём после смены epoch). Оба MEDIUM/must-fix. Это review02 компонента, не новый phase attempt; Lead01 FAIL остаётся неизменным.

Последующий `20cbc322441a80675907bf407f12962778c6c084` не принимается данным решением. Его исправление и новые результаты должны получить отдельное Lead03. P06 остаётся IMPLEMENTING/attempt1, last full PASS=P05. Перехода P07, merge или release нет.

## TEGA-L02 / QA TEG-Q03: world query видит прежний shape

c8 добавляет `_contact_eligible`: membership, `_valid_job` и повторный `_near_foot` после audio/noise callbacks и перед contact. Это закрывает сохранённые исходные128px случаи: byte-exact independent geometry probe прошёл8/8; fresh production replay300/300 и live428/128PNG/movie300 завершены. Однако `_near_foot` смешивает current Node position для range/facing с DirectSpaceState collider overlap, который внутри того же frame ещё использует прежний PhysicsServer transform.

В actual QA07 callback смещает **тот же** верстак с `(308,240)` на `(308,256)`. Current CollisionShape2D находится `(308,250)`, foot Circle8 — `(303,234)`. Независимый прямой `Shape2D.collide` с current Node global_transform возвращает false. Lead дополнительно пересчитал circle/Rectangle20×12: ближайшая точка текущего прямоугольника на10px от центра круга при radius8, то есть miss2px. Range≈32.249px/facing≈.868 ещё допустимы; именно shape eligibility должна отказать.

В тот же момент PhysicsServer body/shape остаются `(308,240)`/`(308,234)`. Collision на server transform, DirectSpaceState и production `_near_foot` возвращают true. Priority1000 observer после Core в том же tick19 фиксирует ещё `+0.70001220703125px` у героя и предмета на новой Node позиции, job1. После Core текущие формы всё ещё не пересекаются. Это квалификация настоящего geometry defect; первоначальный extended10/12, где не прошла проверка предусловия, сам по себе таким доказательством не объявлен.

Отдельный forced-transform контроль синхронизирует server с Node: обе формы/query дают false, job0, actor/prop delta0. Он показывает причину расхождения, но force только в тесте не является исправлением production.

Минимальный remedy: до spatial eligibility обеспечить согласованную актуальную геометрию source/object и их настоящих collision shapes — корректная синхронизация либо эквивалентная точная проверка текущих collider transforms, без подмены формы условной дистанцией/AABB. Сохранить range/facing/LOS/registry/instance/epoch guards после обоих callbacks и до движения/contact. В actual negative хотя бы один listener должен только менять Node position; наблюдатель не должен заранее вызывать production synchronizer/force и тем самым лечить состояние вместо Core. Сохранить forced контроль отдельно.

## TEGA-L03 / QA TEG-Q04: повтор ID после reset

`CombatSystem.reset()` увеличивает encounter_epoch и сбрасывает next_attack_id в0. Callback через обычные production APIs делает `combat.reset()`, `player.reset(current_position)`, затем `use_ability()`. QA07 наблюдает old epoch6/id1 → **new epoch7/id1**, `new_action_started=true`, action special, новый job1.

Старый `_stop_job` c8 удаляет прежний dictionary, затем сравнивает только `_authorized_source` и numeric melee_attack_id. Оба предиката истинны для нового F с повторным id1. Он вызывает cancel_action и отменяет новое действие: в том же tick137 afterCore action пустой/id0/jobs0. Другая проверенная ветка cancelF→newshove проходит, но она не покрывает новое действие того же kind между epochs.

Минимальный remedy: перед отменой сверять полную принадлежность **старому** действию: encounter epoch, pinned authority/action context и attackID, плюс сохранённые lifetime/actor guards. Устаревший job не должен отменять новый same-kind action. Не обходить defect отказом законному reset/newF или удалением проверок. Actual unchanged15 qualification assertions должны сохранять new epoch7/id1 special/job1 после Core, при этом старое действие не двигается и не наносит повторный урон. Старые cancel/free/revoke/replace/reset случаи должны остаться рабочими.

Оба defect воспроизведены независимым QA на отдельной ROOT-копии pinned Godot, result **13/15, exit1**. Lead прочитал оригинальный script, result, command и log, пересчитал Node/server различия, deltas и смену epoch/id. **Никакого урона, receipts, лишних очков или повреждения masks/exceptions в этих двух пробах не наблюдалось.** Более тяжёлые последствия не заявляются.

## Что сохранилось и как проверены доказательства

Lead самостоятельно прочитал c8 resolver и83-line diff относительно084. Изменены только resolver/replay; все1242 native02 input hashes совпали при freeze. Critical source snapshots сохранены до начала20c fix. По сравнению с первоначальным6a изменения включают также три ранее объявленных test/export пути; не утверждается, что весь6a→c8 delta состоит из двух файлов.

Для headless05/live02/movie02 проверены300/428/300 actual assertions и raw JSON: каждый содержит4699 actor/4638 object observations,66 Core contacts. Все128 новых native PNG побайтово совпали с ранее фактически просмотренными native01 PNG; это точная связь прежних пикселей, не новый просмотр всех128. Собственные96 master/native/socket proofs и семантическая ART-приёмка review01 остаются привязаны неизменным asset SHA.

Lead заново декодировал20 whole frames настоящего native02 MP4 и просмотрел их через обозначенные crops: четыре special0/1/2 маршрута, четыре unarmed FIN contacts и четыре blood special1. Видимые положительные действия и одежда не получили нового дефекта. Независимый полный ffprobe decode-count —**4717 frames,78.616667s**,1280×720,60/1, movie SHA `5ce602d1850f328da9990be9f9172c1f0996cf8bdb97fb2b0d901145b4407984`. Это fixed movie cadence, не host FPS.

ART02 PASS_COMPONENT относится к визуальному regression scope, не к новым negative cases. Его23 portable entries плюс сам manifest связаны SHA. Lead проверил136 native artifact hashes. QA02 immutable FAIL_COMPONENT `8ff09cfdd22e91b0be70cb4b3620526957a91ee853e4baec2d4efb6f2edee679` прочитан с findings/metrics/исходными07 данными. Fresh QA06 также имеет8geometry,26negative/custommask,4actor-wall,300production,57counter,29source-bootstrap; extended10/12 сохранён как диагностический этап. Старые2297 green assertions на6a не объявляются новыми c8 запусками. Ни source-bootstrap smoke, ни mocks не являются actual packaged exports/GitHubCI.

Формальный Gameplay02 также завершён **FAIL_COMPONENT**, SHA `9f96a1208a91294b17a5c34aa3b478cf4fea676567e529b35292999f96335b26`, с теми же L02/L03 и partial L01. Lead прочитал completed report/findings/raw extraction и сверил все483 portable entries;78 QA02 entries/FINAL_HASHES тоже совпали. Это дополнительные независимые заключения, а собственное решение основано на прочитанном control-flow и actual QA07 координатах/формах/epoch. Все728 уникальных external reference bindings перепроверены; c8 snapshots и original native02 остаются привязаны точным hash. Producer receipts/argv/log SHA отдельно проверены для successful native02 и failed QA07.

Ревью независимо от автора. Lead не запускал Godot, native renderer или exporter, не менял WORK/Git refs/controller/state/queue и не загружал фото. Heavy originals связаны ROOT-relative SHA/bytes, не продублированы целиком. Новых image/audio assets в этом guard-fix нет; новые licensing/privacy/listening проверки не симулируются.

Следующее действие — исправление L02/L03 внутри существующей P06 и новый source-bound QA/native/Lead03, сохранив оба FAIL и прежние ART/Gameplay решения. Полные семьгеройные sound/NPC matrix, Паша, verifier/ROOT safe handoff, полная phase review, readiness, P07, exports, native Windows, listening, FPS/hardware latency и release этим решением не принимаются.
