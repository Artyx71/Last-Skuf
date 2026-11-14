# P06 — combat sandbox / CH01 view isolation preflight v1

Статус: **CAMPAIGN_VIEW_ISOLATION_REMEDIATION_VERIFIED_COMPONENT_ONLY**. Reviewer `/root/gameplay_review_p06` независимо прочитал guard/lab/session/director/audio/test/wrapper/CI routing и реальные before/after logs; пересчитал source/artifact hashes. Godot/controller/tests/Git commands/build/generation не запускались; source/authority не менялись. Записи только эти versioned lab-isolation-preflight-v1.md/json в корневой gameplay-preflight. Native feel, ART, exports и full P06 PASS не выдаются.

## Исходный leak и исправление

Historical lab-isolation-before-01 содержит реальный command exit1, **12pass/6fail**: processing CH01 не был paused на входе; typing/autosave меняли viewing snapshot во время combat/options/retry/reopen/exit. Frozen source inventory в этом историческом run отсутствует; его нельзя выдать за exact-current-source repro. Он сохранён как failure history.

`campaign_view_guard.gd:7–15` получает ownership только при valid global DialogueDirector и отсутствии существующего p06_viewing_session token. Сохраняет prior is_processing, устанавливает собственный instance ID и отключает только campaign._process. Guard не load/start/reveal/advance/autosave/restore campaign; serialized save не передаёт ему ownership. `DialogueDirector` планирует typing/bleeps/пунктуационный autosave именно из _process, поэтому это устраняет найденный скрытый progress path.

`release:17–25` меняет processing/token/audio только если owns_pause и live token всё ещё принадлежит этому экземпляру. Повторный/nonowner/stale-owner release не снимает чужой pause. _exit_tree автоматически освобождает ownership; queued old actor replacement/reset внутри того же lab не освобождает guard, так как guard живёт у lab. Guard.acquire выключает dialogue duck/scheduling через существующий audio API; accepted короткий speech tail может естественно завершиться: AudioDirector.stop_speech намеренно не обрывает waveform. Ни новых campaign bleeps, ни forced campaign save здесь не создаётся. Subjective audio acceptance не проверялось.

`CharacterLab._ready:10–21` получает guard **до** production combat setup. Если другим владельцем уже занят shared token, lab показывает blocked message, выключает physics и возвращается без создания combat/player. _unhandled_input:101–106 в blocked разрешает Esc в menu, прочие gameplay/selector inputs игнорирует. Нет перехвата ownership CastViewer/CharacterDialogueSession. При нормальном входе guard удерживается во время Space/F/O/R/reopen; exit возвращает именно prior processing true/false.

Existing CharacterDialogueSession и CastViewer имеют прежние hashes и не изменялись. Они используют тот же token protocol и same-owner release. Guard не расширяет save parsing, не создаёт story flags/events и не передаёт raw/private data наружу.

## Actual proof

В `character_lab_isolation_test.gd` реальные production Lab и InputEventKey проходят Space/F, effects panel O, R retry и registered actor reopen. Snapshot сравнивает campaign resource/line/visible text count/char timer/line elapsed/history/ledger/flags, реальные dialogue-file bytes и логический StoryState.store.state. Это не отдельное сравнение bytes story.json: факт logical story equality не выдаётся за disk-file byte proof.

Для prior processing true и false проверяются paused active CH01, неизменный snapshot внутри lab и восстановление только prior processing на root.remove_child(lab). Сразу после exit probe временно останавливает campaign до следующего frame, чтобы нормальное возобновление typing не спутать с leak. Затем проверяются duplicate/nonowner/stale-owner releases и повторное acquire.

Actual after02: **25/25**, sandbox exit0, no ERROR/WARNING. Wrapper tools/verify_p06_lab_isolation.py запускает sandbox и restore отдельными subprocess, с изолированными dialogue/story/options/XDG paths; fresh evidence directory обязателен. Второй процесс действительно восстановил **missed_fight_intro.json line1, active=true**, campaign file unchanged, exit0. Это process restart viewing proof, не только создание второго Director в одном process.

Ограничение: ownership conflict в25 checks проверяется двумя real guard nodes/shared token, не отдельным full CastViewer+blockedLab UI replay. Code blocked branch рассмотрен; нельзя утверждать, что этот UI case был нативно проигран. Snapshot не утверждает сохранение char_timer через process restore: таймер проверяется внутри lab, новый процесс проверяет resource/line/file.

Current gabar-view-guard-01 отдельно даёт **124/124** actual headless Input checks,37 contacts,0 rendered captures, exit0. Это подтверждает controller continuation с новым guard, не real-time feel/native ART. `tools/verify.py:57–64` добавляет isolation wrapper в общую CI validation sequence вместе с P06 components и bounded Gabar wrapper; conditional code path есть, но полный CI suite здесь reviewer не запускал.

## Source/evidence boundary

Git HEAD label, прочитанный без Git commands, и оба run source_head — **8f30222dd054ef7b605ecc654500aa2eb1a1ef3a**. Один label не доказывает committed exact-tree freeze: candidate guard отличается от старого native render config. Actual native02 ART acceptance не используется как evidence новой isolation logic.

При первом независимом сравнении все **675 записанных source hashes** обоих after02/Gabar inventories совпали с WORK. Все6 isolation artifact hashes и4 Gabar artifact hashes совпали. При final check **674/675** совпадают: отдельно автор изменил `assets/source_art/characters/adopt_world.py` для Olezhka source adoption. Guard/lab/tests/harness/verify.py и проверенные lifecycle dependencies сохранили hashes. Новые Oleg source files вне этого review; whole current worktree/HEAD freeze не заявляется. Авторское source_unchanged=true относится к before==after конкретного run.

Новых actionable findings в рассмотренной guard/isolation logic не найдено. Найденный CH01 processing/autosave leak устранён в указанной области. Полная campaign/save isolation всего P06, чужие будущие sandbox entry paths, native settings/feel/ART, остальные герои и full exports/phase gates остаются отдельной работой.
