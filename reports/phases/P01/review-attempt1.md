# P01 — независимый Lead Review, попытка 1

**Решение: BLOCKED.** Reviewer `/root/lead_reviewer`, отдельно от авторов `/root` и `/root/art_production`. Art subreviewer: `/root/lead_reviewer/p01_art_subreview`, новый независимый context. Проверенный commit `fcf399967c563cb77b0cf1fe0f6cdff532d798dd`, base `7cded8bb4bfd7826a8833eaaebeadfc33298bbda`. [Draft PR #2](https://github.com/Artyx71/Last-Skuf/pull/2), base phase/p00-bootstrap; private repo подтверждён API. P00 имеет независимый PASS attempt2.

Техническая часть, наличие настоящего арта и его интеграция подтверждены. Высоких технических или визуальных дефектов не выявлено. Обязательный **человеческий likeness/гротеск signoff отсутствует**; авторский и независимые AI reviews его не заменяют. Поэтому P02 не разрешён. Автор уже запросил оценку владельца; reviewer не создаёт дублирующий вопрос и не ждёт ответа бесконечно.

## Scope и просмотренные материалы

Прочитаны P01_TASKS, implementation, inventories/atlas, author review, source README, оба packing recipes, четыре точных generation prompts и metadata, CONSENT_STATUS, ART_PIPELINE; применены ранее прочитанные AGENTS/specs/ART_BIBLE/gates/review-loop. Сверен полный diff base..HEAD. 43 изменённых non-report source/art/docs файла сверены с проверенным commit; working tree совпадает. Reviewer не исправлял code/art и не делал commit/push/merge.

Lead **лично** открыл локально правильное `assets/references/characters/yakuza_ref01.png`, оба native portrait sheets, world_sheet, все четыре generated masters, author lab present/past/export screenshots, animation contact sheet и точные enlarged world frames subreviewer. Фото никуда reviewer не загружал, в inspection artifacts не вставлял. Также открыты собственные fresh Godot captures present/past/exported Linux lab.

P01 — art/movement lab: не миссия, не combat prototype и не готовая игра. Present world sprite и отдельные present/past portraits соответствуют этому scope; old-era world moveset не требуется текущим планом. Audio, full VO, боёвка и gameplay escape route не представлены и не считаются проверенными.

## Проверки

| Контракт | Независимая evidence / результат |
|---|---|
| VIS-01: настоящий арт и source | Native present/past по пять выражений 160×160; world 32 frames 48×64: down/left/right/up, 2 idle + 6 walk. Все четыре masters побайтно совпали с original provider-generated files из metadata output_hint. Prompts и recipes сохранены, raw photo packer не читает. |
| VIS-01: структура | Независимый native art test: 90/90 assertions. Present 31, past 30, world 24 opaque colors; hard alpha, transparency, frame bounds/pivot, distinct poses. Subreviewer отдельно подтвердил alpha0/255 и transparentRGB0. |
| GP-02: движение | Native movement test 34/34: actual input action/physics movement, normalized diagonal, cardinal facing/animation advance, release-to-idle, outer wall/interior prop collisions, expressions и обе era sources. Код CharacterBody2D, fixed physics callback, speed82, без random stumbling. Bootstrap regression6/6. |
| Повторный runner | `python3 tools/verify.py --references --capture --output reports/phases/P01/reviewer`: 9/9 commands exit0. Итого local native assertions130/130. Отдельно reviewer повторил present/past source render, original Linux smoke и exported lab render: 4/4 PASS. |
| Repro source packing | Обе recipes повторены в отдельном ignored reviewer/build/repro, production originals не тронуты. Обе exit0, все три runtime PNG воспроизведены побайтно. В atlas.json отличается только одна строка review/known_limitations, см. LOW META-P01-01. Runtime atlas fields равны. |
| Source/evidence integrity | Авторский artifacts.json: 34/34 sizes+SHA256; art_inventory: 22/22; provider masters4/4. Scope implementation_commit inventory 7e6ef0b предшествует final evidence commit fcf3999; source/data отдельно привязаны reviewer hashes к final HEAD. |
| Replay | Реальный Movie Maker log прочитан; ffprobe: H264 1280×720, 60FPS, 493frames, 8.216667s, без audio stream. Frames/contact sheet показывают четыре направления и пять **present** expressions. Past подтверждён отдельными captures/tests, в movie past switching не заявляется. Это не измерение реального gameplay FPS. |
| Exports | Исходные Linux/Windows файлы присутствуют и совпадают с inventory hashes. Linux реально запущен и отрендерен reviewer. CI builds также скачаны и проверены отдельно. Windows runtime не проверен. |

## Независимая визуальная оценка

Согласованность portrait/world, black tee/phone, широкая короткая fictional silhouette и густые тёмные волосы подтверждены. В портретах сохранены визуальные опоры соответствующего фото: масса волос, глаза/брови, компактный нос/рот, округлая челюсть и родинки. Present намеренно утяжелён, past имеет более узкие шею/челюсть; обе эпохи и все expressions различимы. Это **AI visual assessment**, не человеческое утверждение максимальной узнаваемости.

На native размерности видны жёсткие pixel clusters и ступенчатые контуры, а не размытая фотография. Highres masters имеют мягкую alpha/неоднородную grid; они не используются как runtime textures. Порог alpha и NN/palette packing дали прозрачные фиксированные native PNG. Визуально photographic remnants/чужие game assets не обнаружены; это не юридическая экспертиза происхождения. На реальном lab фоне matte/белой каймы нет; тёмные волосы читаются с меньшим контрастом, чем лицо/телефон, что требует повторной проверки на будущих authored maps.

World camera показывает верх головы/плеч и укороченные ноги; side rows читаются как overhead profile, up — затылок/спина. HIGH perspective inconsistency не выявлена. Hair/body jitter действительно заметен и описан MEDIUM ticket ниже; fixed foot anchor не доказывает стабильность формы головы. Subreviewer независимо пришёл к тем же severity/ограничениям, его полный отчёт — `reviewer/art_subreview.md`.

## Реальный GitHub CI и privacy

[Run 43319881768](https://github.com/Artyx71/Last-Skuf/actions/runs/43319881768) на проверенном HEAD завершён **SUCCESS**, все steps исполнены на временном self-hosted Linux runner текущей машины. Это не GitHub-hosted Ubuntu validation и не независимая Windows машина. Reviewer сам получил API/job log и скачал artifact13989039062. SHA256 ZIP `a4ffff56588cb30e9284dab80e31c11223795b61387fe02aa5b3aa1da3264251` совпал с API digest. Все10файлов проверены: два builds и семь command logs + validation JSON. CI verify7/7 PASS; native bootstrap6 + art90 + movement34 PASS. Скачанный CI Linux executable дополнительно запущен reviewer headless: exit0, без ошибок.

CI Linux SHA256 `02a3578cb870fa3c77d3b3e2d32cab4294f873fcecf62c2f6f47002360a9a99f`; CI Windows `da00d56e08ab52fe725e545b23833e27acb37449badc1d46b0816c80f78fdf95`. Они отдельно инвентаризованы, не выдаются за исходные local builds; cross-import whole-binary determinism не заявляется. Embedded PCK обоих CI builds проинвентаризован: 24 runtime resources, включая три imported textures, atlas, scripts/scenes и Godot notices; raw references, tests и highres source_art отсутствуют.

CI checkout merge commit5d99cd7 имеет parents base7cded8b и HEADfcf3999. References path в checkout отсутствует; persist-credentials header отсутствует. Самостоятельный аудит Git index/history всех refs: 11 raw reference hashes не совпали ни с одним reachable blob, запрещённых paths и проверяемых credential patterns нет. После job independently confirmed API runners=0/variables=0, процессов Runner.Listener/Worker нет, `.runner`, `.credentials*`, `.service` отсутствуют. Нового постоянного сервиса нет. Hosted billing остаётся ограничением будущих default hosted runs; это не обещание постоянного runner.

## Findings / tickets

**HUMAN-P01-01 / HIGH / external evidence dependency — человеческий signoff PENDING.** Основание: `planning/P01_TASKS.md:10`, ART_BIBLE visual acceptance5. Repro: прочитать `human_art_review_request.json`: response_received_at_checkpoint=false; owner/authorized-human approval record отсутствует. Hashes всех четырёх request previews/replay совпали с фактическими файлами. Required: владелец/уполномоченный человек сравнивает **правильное** фото с present/past expressions/world, подтверждает узнаваемость и степень гротеска либо формулирует правки. Записать человека, дату, решение и точные hashes утверждённых runtime assets/previews. Не заменять ответ silent timeout, author approval, image_gen authorization или AI comparison. До этого BLOCKED, P02 не начинать. Public likeness/name/voice distribution rights остаются отдельным невыданным разрешением.

**ART-P01-01 / MEDIUM / nonblocking polish — hair/body jitter.** Файл `game/assets/art/yakuza/world_sheet.png`; idle down_0 rect(0,0,48,64) ↔ down_1 rect(48,0,48,64), up_0 rect(0,192,48,64) ↔ up_1 rect(48,192,48,64). Repro: `reviewer/world_inspection_4x.png` или неподвижный actor вниз/вверх при3FPS. Hair top7→9px/down и6→9px/up при y58 sole; меняются масса волос/посадка головы/шея, не только согласованный bob. Fix: стабилизировать hair silhouette и положение головы в down_1/up_1, сохранить малое дыхание и pivot; walk проверить при8FPS. После правки обновить source/native PNG, atlas hashes и реальные animation evidence. Уровень MEDIUM, не причина технического FAIL P01; учитывать при human polish review/следующей доработке.

**META-P01-01 / LOW — atlas byte reproduction отличается review-note.** Файлы `assets/source_art/yakuza/build_assets.py:122`, `game/assets/art/yakuza/atlas.json`. Repro: две recipes на scratch copy, `reviewer/integrity_and_source_repro.json` и `atlas_repro_differences.json`. Все3PNG совпали, atlas JSON отличается только дополнительным known_limitations предложением о present world/past portraits. Fix: привести emitted review metadata к committed atlas либо явно ограничить claim воспроизводимости runtime asset fields/PNG. Не заявлять exact atlas bytes без этой оговорки. Функциональные atlas данные не расходятся.

## Следующий шаг

Остаёмся в **P01 BLOCKED** до HUMAN-P01-01. Полученный human ответ сохранить отдельным immutable record, исходный request checkpoint не менять. При замечаниях исправить только нужный арт внутри P01, обновить hashes/затронутые evidence; при одобрении неизменённых assets проверяются ответ и точные hashes, без бессмысленного повторения всей уже прошедшей технической валидации. Независимый reviewer затем выполняет attempt2. MEDIUM/LOW tickets переданы исполнителю; они не повышены до HIGH ради блокировки.

P02, merge и release не разрешены этим решением. Боёвка и музыка вне P01. Reviewer source/code/art не менял, raw фото не загружал, commit/push/merge не делал.
