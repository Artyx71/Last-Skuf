# P03 — независимый review, попытка 1

Reviewer: `/root/lead_reviewer_p03`, отдельный контекст от авторов root/runtime/audio/art. Art subreviewer: `/root/lead_reviewer_p03/art_review`. Исходники reviewer не изменяет; собственные результаты находятся только в этой папке. Итог: **BLOCKED только по AU-P03-01, обязательному человеческому прослушиванию**. Source candidate348e223, actual CI92c8e96 и evidence202ccbc независимо проверены. P04 не разрешён.

Прочитаны AGENTS, роль Lead Reviewer, Project Gates, Review Loop, P03 tasks, PHASES, README, все четыре спецификации, Art/Character Bible, архитектура, asset/art pipeline, privacy policies, P02 PASS attempt2 и P03 handoff. Проверены новые реальные scripts, dialogue JSON, audio manifest, генератор/composition, WAV/runtime OGG, provenance/licenses, native screenshots и replay diagnostics. Ранее принятые P01 pixels сохраняют утверждение; здесь оцениваются ограниченные feature edits и неизменность остального изображения.

## Независимо воспроизведено

- Dialogue44, audio45, options26, contact48, portrait49 assertions: всего212, failed0, exit0; ERROR/WARNING в сохранённых logs отсутствуют. Изолированы userdata/options/dialogue пути. Поведенческие assertions старых tests сохранены, teardown освобождает mixer.
- Все45 entries audio inventory и21 portrait inventory совпадают по SHA-256. Независимый FFmpeg decode4 настоящих runtime OGG:640000 stereo frames при48000Hz каждый, clipping0, длительность13⅓s. Численные проверки не являются слуховой оценкой.
- Внешняя сцена из5 русских реплик имеет стабильные IDs, сдержанную речь Якудзы, правильную связь с Жинькой и не содержит непроверенного осетинского текста. Проверены once-only ledger/rollback, reveal/hold/history/seen-skip/settings input и реальные bus gains. Основной текст остаётся видимым при отключении дополнительных звуковых подписей.
- Native large-text PNG просмотрен непосредственно: длиннейшая реплика максимального размера помещается в2строки, portrait/world видимы. VHS ограничен областью ниже текста. Art subreview независимо смотрит6 настоящих feature frames,16weapon-phase/fire captures и плотные кадры actual native movie.
- Privacy:7probes, tracked761, errors0; tracked assets/references отсутствуют. Авторский локальный синтез не использует recordings/sample packs/модель реального голоса. Разрешение публичного выпуска не заявляется.

## Scoped blocker AU-P03-01

Severity HIGH / внешняя возможность BLOCKED; это не обнаруженный дефект звучания. Требуется реальное прослушивание оригинальных loops, runtime seam, adaptive crossfades/ducking, разборчивости speech/SFX и хвостов10rapid death/retry. Наблюдение: reviewer передал actual `audio_preview_combat.mp3` через `functions.audio` и получил дословно `audio content omitted because you do not support audio input`. Listening/transcription/perception tool не обнаружен. Repro evidence: `audio_independent.json`; авторская capability запись подтверждает тот же исход. Минимальное устранение: владелец/слушатель прослушивает готовые state previews, doubled decoded-runtime loop, SFX montage и окончательный actual runtime capture; фиксирует результат, найденные дефекты исправляются и повторно проверяются. Метрики, процессы playback и waveform этот gate не закрывают. Для перехода к P04 нужен полный P03 PASS.

CRITICAL/HIGH дефектов source/runtime/visual в проверенном объёме пока не найдено. Final source/CI/export verification и native reduced-effects capture завершены; доказательства проверены ниже. Native Windows следует отдельно отмечать от действительного PE runtime под Wine.

## Завершённая техническая проверка

Source/art/runtime commits d99c501/a2c09cb/92c8e96 проверены; все135 game source files совпадают между reviewer, final native и export snapshots. Независимый запуск именно final Linux executable SHAa45d188c… дал exit0 и читаемый native dialogue framebuffer. Final57/57 технических checks (24команды),152 technical artifact hashes проверены, mismatch0. Обе сборки свежие; final WindowsPE SHA5dda9561… действительно исполнялся под Wine11.17 (WASAPI), а native Linux — PulseAudio. Native Windows NOT_TESTED_UNAVAILABLE. Actual runtime replay на каждой платформе завершает сцену ровно один раз, проигрывает4профиля и10реальных death/retry, оставляя1musicplayer/1stemstart и0active voices. WAV не имеют full-scale clipping.

Art subreview завершён: mouth/blink в обеих emotions настоящие и ограничены ROI; actual default/reduced-off movies и standalone PNG читаемы; просмотрены все16weapon poses. **ART-P02-01 CLOSED**. Approved P01 PNG и atlas unchanged; исторические ART-P01-01/META-P01-01 остаются backlog.

Actual CI [43398074747](https://github.com/Artyx71/Last-Skuf/actions/runs/43398074747) на92c8e96 — SUCCESS, [private PR4](https://github.com/Artyx71/Last-Skuf/pull/4). Reviewer независимо получил metadata/joblog/API artifactdigest, сравнил downloadedZIP SHA465f742f… с API, проверил19archive entries и извлечённые файлы,16commands PASS/785assertions/0failed. Runtime идентичен CI; последующая поправка tools/verify_p03.py относится только к локальному техническому verifier и выполнена отдельно, не приписывается этому CI. Ephemeral runner cleanup независимо подтверждён API:0runners, AYAY_RUNNER отсутствует; local .runner/.credentials отсутствуют.

## TEC-P03-01 — LOW, диагностическое ограничение

CI действительно содержит предупреждение `2 ObjectDB instances were leaked at exit`: в artifact smoke.log и в job-step экспортированного `--headless --quit`. Этот engine CLI мгновенно завершает игру в обход app runtime_shutdown и может завершиться до первого mixer block. Это не скрыто и не исправлено путём подавления logs. Actual12assertion suites и normal rendered app/export exits чистые; final local verifier выполняет более содержательный actual bootstrap capture с обычным shutdown и PNG. Поэтому предупреждение не блокирует игру/фазу, но broad zero-warningCI не заявляется. Repro: CIcommands выше. При следующем изменении workflow заменить abrupt smoke на normal app capture и перепроверить CI; сохранять диагностику до отдельного подтверждения. Wine также имеет явно записанные Mesa/SDR environmentwarnings; они не выданы за nativeWindows certification.

Технических CRITICAL/HIGH дефектов после проверки не осталось. Единственный hardgate — AU-P03-01, реальное человеческое прослушивание. Итоговый статус должен оставаться BLOCKED до его закрытия; P04 не начинается.

## Окончательное решение

**P03 BLOCKED, attempt1.** Candidate348e2235c0a8e06eabf2a5a9b7a75eedaa88ee41; actual CI92c8e96912f4db1731dbe3da46c3f99f097e59de; evidence202ccbc38d6154553c42f9102543789c57f3ced1. Дополнительный commit меняет только6строк local verifier; runtime/tests/workflow остаются CI-identical. Все156author artifact hashes перепроверены, mismatch0; reviewer findings и decision исключены из hash cycles.

Закрытие AU-P03-01: владелец прослушивает конкретные неизменённые файлы из LISTENING.md/listening_request.json и передаёт принятие либо clip/time замечания. Нужен результат реального прослушивания, не общая команда продолжать. Затем независимый reviewer проверяет результат на этих hashes, при необходимости инициирует исправление и новую ограниченную проверку, только после полного PASS разрешает P04. Права на public/merge/release/реальный голос этим не меняются.
