# Independent QA — Pasha controlled Input closure

**PASS_COMPONENT** для нового controlled replay и узкого исправления diagnostic guard. Это не полный P06/native13, не выяснение старой OS-причины и не разрешение на merge/P07/ROOT installation. Исходный full01 FAIL c46d и651 static preflight FAIL fa6b остаются неизменными.

Реально выполнены отдельные canonical jobs: headless2d814544…exit0 и native/moviec0d32773…exit0 на651d730b. Самостоятельно сверены input/receipt/started/log SHA, argv digests и canonical completion events. Creation-time input сохраняет consumed=false; completion history и текущая native operation подтверждают завершение/consumption отдельно. Проверены200actual child artifact hashes, clean exit0 raw logs и source inventories. Участвующие headless/native maps одинаковы:1368records; по отношению к исходному full01 единственная изменённая общая запись — Pasha QA replay.532Gamefiles за исключением этого fixture фактически перечитаны и совпали; actor/Core/resources/audio/assets не менялись.

## Actual Input и прежние проверки

Самостоятельный пересчёт трёх JSON sets — headless, обычный native и MovieMaker. В каждом8routes×32samples, всего **768actual Input observations**. Для каждого проверены типы/конечность vector, правильное направление и run=true. Срезы ammo_trace непрерывны и содержат только свой segment; tick integer/строго возрастающий и точно совпадает с32corresponding physics-trace entries. Поэтому фильтр по имени не скрыл чужую или пропавшую запись внутри интервала.

Все24routes показывают0..7по порядку,180velocity,96px displacement, отсутствие превышения teleport bound и конечный run с завершённым action. Это включает Reduced down/left, проваленные в старом movie. Для каждого route отдельно ровно один launch/cost/lethal Core impact; launch/cost совпадают по epoch/tick и sourcepose3, actor/fixture authorityPasha, ammo4→3, конечный score0. Ballistic impact может быть на более поздней позе; это не ошибочно приравнивалось к muzzle pose. Все105Core contacts/mode имеют уникальный(epoch,id,target); outgoing FIN — player contactpose1.

Counter check names сравнен с исходным full01: все старые393headless/movie predicates и581native predicates присутствуют и проходят. Новые восемь held-input checks не заменили старые условия. Итог401/401 headless,589/589 native и188PNG,401/401 movie. Часть native assertions — сохранение изображения, это не589отдельных gameplay scenarios. Actual MP46096191bytes/5662frames независимо проверен ffprobe и SHA. Это container metadata query, не полный frame decode, не FPS или audio listening.

## Focus и смысл результата

NO_FOCUS_requested=false в headless/native иtrue только в MovieMaker; actual row flags соответствуют режимам. У native во время held routes focus=false; у headless API даётtrue. В movie позднее записаны focus_entered/focus_exited несмотря на выставленный flag. Поэтому принимается только зафиксированный режим/корректный Engine Input в данном запуске; не заявляется гарантированная OS isolation. Прошлая запись не сохраняла Input/focus, и этот новый PASS не доказывает задним числом внешнюю клавиатуру, потерю фокуса или иной root cause. Нет physical keyboard/hardware latency/manual-focus acceptance.

## PASHA-INPUT-Q01 closure

Guard source7a76f7bf, SHA de4067eda5456653c11cf01fa6b12265463ca0d681736f2753d37746cbad8655, добавляет только nonempty interval, совпадение segment и строгое возрастание tick. Все check calls, awaits и key-driver/release строки651сохранены. В чистой Python recomputation логики на точных integer/vector controls все24actual intervals/768samples принимаются; valid control и6negatives проверены: empty, foreign segment, run off, zero vector, duplicate/reversed tick. Пустой набор теперь не принимается. Нет key reassertion, ускорения/телепорта, уменьшения distance, пропуска старых assertions или нового renderer запуска.

На7a не заявляется новый Godot compile/engine replay: native data относятся к651, а усиленный predicate отдельно проверен по source и сохранённым данным. Current coordinator предусматривает отдельный GD parse gate; его реализация/разрешение не входит в этот verdict. Такое разделение позволяет не перерендеривать неизменную боёвку ради additive guard.

## Carry-forward и remaining5

carry-forward-proof.json — typed evidence: семь индивидуальных успешных стадий исходного full01 и новый scoped Pasha corpus с exact hashes/source chain. Исходный aggregate exit1/FAIL сохранён; proof не превращает его в PASS. Runtime inventory исключает ровно один известный QA fixture и не разрешает произвольные новые/изменённые source paths. Новый coordinator742/его tests требуют отдельного независимого preflight.

После такого preflight remaining5 должны выполняться новым canonical serial job после author release, в fresh output, с exact current source/HEAD freeze, неизменёнными process-containment functions, actual receipts/typed child reports и конечным rehash approved contract/decisions. Requested exports/movie scopes сохраняются; реальные native wall-frame samples берутся вне MovieMaker. Cast, large-text, C01, NPC supplement и P04G/export/performance здесь ещё не выполнены. Final composed13 ledger обязан явно назвать reused7/newPasha/fresh5, а не переписать old failed report или заявить один успешный native run. Full Lead/CI/merge gates остаются обязательными.

Все действия QA — read-only обработка реальных файлов и собственные отчёты. Godot/Controller/runner, публикация и изменение production state/code не выполнялись. Новая субъективная оценка музыки/арта/ощущений, native Windows и hardware FPS/latency не приняты.
