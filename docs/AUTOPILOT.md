# AUTOPILOT: состояние, восстановление и PR

Единственный authoritative файл — `automation/phase_state.json`; новый namespace `autopilot` дополняет прежний формат. P00–P02 PASS, P03 attempt1 и все старые findings/решения сохранены. `.autopilot/STATE.json` — только совместимое зеркало, его редактирование не сбрасывает progression. Первичная интеграция делает локальный backup прежнего state; установленный оригинал runner сохранён в `.tools/autopilot-installed-backup`. ROOT вычисляется от runner.py, запуск из родительской директории безопасен.

## Последовательность

```sh
python3 autopilot/runner.py reconcile
python3 autopilot/runner.py status
python3 autopilot/runner.py resume
python3 autopilot/runner.py run --task audio-qa
python3 autopilot/runner.py run --task prepare-p04
python3 autopilot/runner.py pr --phase P03 --pr-action status
python3 autopilot/runner.py run
python3 autopilot/runner.py pause
```

`init`/`reconcile` не создают новую историю поверх существующей и не начинают P00. `resume` не запускает процесс в фоне и не снимает фазовые gates. `run --phase P04` не обходит predecessor PASS/confirmed merge. Автопилот не установлен как постоянная служба. В работающем `run` стадии ограничены таймаутами, после остановки хоста нет обещания дальнейшего исполнения.

Один POSIX flock в `automation/.executor.lock` охватывает controller и единственного bounded worker. Совместимый RUNNING.lock блокирует старую копию runner; PID не служит единственным доказательством lock. При SIGKILL родителя worker сохраняет lease до завершения, второй executor отклоняется. Child result/argv/log SHA и fsync+atomic replace образуют durable receipt; stage checkpoint и consumption фиксируются одной записью. После восстановления завершённая стадия принимается один раз. Изменённые argv/stdin/script inputs или log/receipt не принимаются. Неизвестный исход code implementation требует независимого recovery review, не слепого повторения. Timeout/pause завершают собственную child process group; чужие процессы не затрагиваются.

Тесты с SIGKILL/timeout/двумя competing controllers используют временные fixture processes, не второй Codex/игровой исполнитель. Их PASS не выдаётся за прохождение фазы игры.

## Audio QA и художественное принятие

`tools/audio_qa.py --capture-engine` реально декодирует runtime OGG и source WAV, измеряет sample/true peak, RMS/LUFS, DC, clipping, интервалы тишины, loop frames/стык; анализирует4состояния и12направленных переходов в3ритмических позициях. Отдельный external GDScript fixture запускает настоящий AudioDirector и29s master capture через фактический mixer:4profiles,2loop wraps,pause/dialogue duck. Transition windows привязаны к real mixer clock с записанной latency uncertainty. Retained P03 gameplay capture отдельно подтверждает10реальных смертей, не подаётся как свежий запуск.

`--analysis-only` для headless CI выдаёт **PASS_SIGNAL_ONLY**, никогда полный runtime/listening PASS. Technical policy — широкие guards, не обещание хорошего звучания или определённой субъективной громкости. Реальное прослушивание/приёмка слушателем и signal metrics — раздельные evidence. До настоящего listening результата BLOCKED только artistic gate; audio-qa/подготовка/инфраструктура разрешены внутри текущей фазы. Владелец теперь сообщил, что проверил P03 звук и пока принимает; его точная реплика и hashes исходных clips в reports/autopilot/P03/human_listening.json, решение остаётся независимому Lead.

## Авторизация и squash merge

Владелец явно разрешил public repository и conditional automatic squash merge **Artyx71/Last-Skuf → main**; exact quotes — automation/AUTHORIZATIONS.json. Это не release/real voices/публикация rawphotos/расходы. Исторические private-only формулировки в старых reports/source license snapshots — прежнее состояние, не отмена нового поручения. Existing media remain project assets; новое разрешение не выбирает за владельца open-source license.

`autopilot/github.py` создаёт phase PR после privacy check и обычного push (без force), хранит CI/review blockers и findings для исполнителя, повторяет FAIL→FIX→REVIEW в установленном attempt budget. Независимый reviewer выполняется после автора, в read-only CLI context; автор свой PASS не ставит. Новый worktree на origin/main не стирает прежний checkout или пользовательские изменения.

Merge требует: independent PASS на **точный текущий head SHA и актуальную main base**, hash-bound evidence, нет открытых CRITICAL/HIGH; P03 audio acceptance имеет отдельный реальный listening proof. Обязательные CI из config и GitHub branch/rules должны быть успешны на том же SHA. Pending/failing checks, uninspected review threads, GitHub CHANGES_REQUESTED/REVIEW_REQUIRED, missing approvals, merge queue/неизвестная protection/права — BLOCKED. Draft становится ready только после независимого PASS, без замены требуемого GitHub human approval.

Перед merge remote PR/rules/checks читаются повторно; изменение head/base прекращает попытку. [GitHub merge endpoint](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request) получает `sha=<reviewed current head>`, `merge_method=squash`; при несовпадении SHA сервер отклоняет запрос. Нет --admin, bypass, force push, изменения правил или прямого push в main. После ответа отдельно проверяется merged/head/base; неясный сетевой исход требует reconciliation. Только confirmed MERGED обновляет pipeline и разрешает следующую фазу. При branch/rules API403 не меняются тариф/visibility/правила без отдельного указания владельца.

Старые stacked PR не сливаются по зелёному историческому CI: их актуальные heads требуют нового связывания review/CI. Retarget в main допускается после merge predecessor и инвалидирует прежний review; конфликты не решаются force push. Внешнее ручное approval, если GitHub его требует, автопилот сам себе не выдаёт.

## Combat/Gore очередь

`autopilot/queue.json` и specs/COMBAT_GORE_POLISH_SPEC.md: подфаза **P04G после P04**, обязательная до P07. Существующие CombatSystem/action IDs/physics clock/AI/AudioDirector переиспользуются. Реальные original effects/animation/finishers, exactly-once damage/score, settings invariance, cap/lifetime/performance, ART/GAMEPLAY/QA/Lead evidence обязательны. Пока это очередь, не готовые finishers. Проверка изменённого приватного reference Тимки отдельно блокирует его P06 asset use, не reset P03.

### CI media dependency and receipt ordering

Hosted Ubuntu image не содержит ffprobe/ffmpeg. tools/install_ci_media.py извлекает pinned SHA256-verified ImageIO0.6.0 wheel из PyPI в .tools/ci-media (FFmpeg7.0.2 static), без pip/system/sudo; licenses/provenance сохраняются вне game. AudioQA декодирует floatWAV и читает rate/channels из реального потока, отдельный ffprobe не нужен. Первый failedCI43410070643 сохранён в reports/autopilot/CI/attempt1; forced-kill test теперь ожидает реального освобождения lease после durable receipt, не подменяет эти события.

Merge intent (head/base/checked snapshot/review hash) fsync-сохраняется перед HTTP-запросом. После потери ответа допустима только сверка уже merged PR с этим intent, неизменным review и single-parent commit на проверенной main base. Старые confirmed merges обновляют отдельный delivery_next и не откатывают active_phase/last_pass. Текущая фаза переходит дальше только после её собственного confirmed merge. Tests теперь37, включая обе эти state/race регрессии.

## P04 recovery and publication fixes

Interrupted P04 implementation was preserved at attempt1 and independently cleared for local recovery in `reports/phases/P04/recovery/decision.json`. That scoped SAFE_TO_CONTINUE is not phase acceptance. The controller used ordinary host commits for the preserved files. No author was replayed, progress reset, or second author started.

Implementation uses `workspace-write` with `--add-dir` limited to the same repository's common Git directory. A live restricted-executor probe wrote a harmless object, refreshed the index and created/deleted a temporary probe ref without changing HEAD. A foreign Git repository is rejected. Read-only reviewers receive no writable Git allowance.

Before a push, publication checks the current phase branch and committed SHA. Staged changes, source deletions, renames into reports and nonignored untracked implementation files block publication. Only unstaged/untracked files confined to `reports/` may remain as generated evidence. Privacy checks run, then HEAD/branch/dirty checks run again; Git pushes the verified object ID to the explicit phase ref. No force or protection bypass is used. Dirty publication tests cover zero push and zero PR POST.

P04 validation proceeds through native renderer/audio, reduced settings, MovieMaker, clean exports, Linux and Windows-under-Wine replays before publication. Output directories bind HEAD and attempt; interrupted/nonzero native QA requires evidence inspection, not a blind replay. Detailed audio checks decode original masters/game files, measure loudness/silence/clipping/loops, probe every directed musical transition, and inspect actual runtime PCM. They cannot approve artistic audio. P04 PASS additionally requires hash-bound structured P04 listening evidence; P03 listening cannot satisfy it.

Shutdown uses monotonic wall time while still processing frames so asynchronous audio cleanup also works in accelerated/headless tests. Mandatory regression includes full normal and accelerated mission exits, and fails on leaked-object/resource warnings. Runtime bootstrap smokes use the clean shutdown path; editor import still uses the editor's `--quit`.

Current final candidate paths and gates are recorded in `reports/STATUS.md` and `reports/NEXT_ACTION.md`. A configured active bounded controller is required; this does not install or claim a permanent daemon.
