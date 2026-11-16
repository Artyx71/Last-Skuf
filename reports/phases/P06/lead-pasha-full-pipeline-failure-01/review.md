# Targeted Lead review: остановка full native pipeline на Паше

**FAIL_COMPONENT — текущая полнота/достоверность evidence stage8.** Root cause потери held-run **UNKNOWN**, product/input-source defect не установлен. Это не новый full-phase verdict/attempt, не отмена исторического ограниченного b359 acceptance и не разрешение менять механику.

## Что самостоятельно проверено

Исходный frozen HEAD beb30f319b2cf86a1799672ed24837c4640a9bee; canonical operation8e8ab4a27ccd47ebacf5a66dd3b6780c завершился exit1, old aggregate passed=false/sourceHEADunchanged/sourceinventoryunchanged. Первые7 stages реально exit0/childvalidation true: Gabar/Oleg/guard/Timka present/prime/Ryzhik/Tega. Pasha stage8 live581/581 с188PNG, movie389/393 и exit1; остальные5 stages не исполнены. Actual typed reports/commands прочитаны, а не только пересказ автора.

Сопоставлены все8movement cases ×3 реальных run traces: current failed Movie, current passing live и accepted b359 Movie. Во всех по32 последовательных trace samples и все8поз0..7. Failed Movie physics ranges для Reduced down196..227 и left230..261 **те же**, что в accepted b359. Обычная ошибка ожидания idle/process frame или количество sampled physics ticks эти четыре FAIL не объясняют. Capture() в Movie возвращает без screenshot waits; сравнение old/current Movie одинаково. Live имеет другую стартовую tick offset, но те же32 samples/case.

Реальный failing AVI сохранён без перекодирования/trim:6ac42ef8d9a2053acddf4687c335d9080cae6cafd966895ae6a5c5095989881d,400255102B. ffprobe header сообщает5662 video frames/60fps/94.366667s; это header observation, не независимый fulldecode/FPS performance measurement. Самостоятельно декодированы6реальных кадров, лично осмотрен montage. Видны настоящие shooting/contact/recovery состояния в открытой зоне; invisible wall blockage этими кадрами не подтверждается. AVI frame index не отождествляется с physics tick. Файлы и точные decode commands сохранены; никаких Godot/native jobs reviewer не запускал.

## Подтверждённый finding PAS-PIPE-L01 (MEDIUM, OPEN)

Ожидание source replay lines169..191: key movement+Shift held, F, all8poses, завершение в run, physical displacement>70, непрерывный путь; release запланирован только после frames24 вline180. Фактически:

- Reduced down: ticks196..207 скорость180, tick208 скорость0 при active pose5, затем остаётся0; final y236 вместо296. От исходной fixture(380,200) фактическое перемещение36px. Action проходит позы0..7, завершается в idle_down.
- Reduced left: ticks230..236 скорость180, tick237→125, tick253→0; final x245.6665802 вместо204. От исходной fixture(300,240) перемещение54.3334198px. Action проходит0..7, после recovery сначала walk_left, затем idle_left.
- Остальные6cases и все8current live/accepted b359 Movie заканчиваются run с96px от fixture initial position. Максимальный continuity-bound excess −0.01 во всех случаях: это не обнаруженный teleport.

Поэтому оба predicates правомерно FAIL на каждой из2строк. All8poses не отсутствуют; проверка состава poses сама по себе проходит. В trace есть idle/slow samples **до** запланированного release, поэтому простое перенесение source check до release не доказывает исправление. FullReduced damage/ammo/once checks этих cases остаются green. Приватные Input/vector/run/focus/event поля не записаны; из velocity180→125/0 можно выдвинуть гипотезу потери Input-state, но нельзя доказать внешний OS input/focus loss, обвинить пользовательскую клавиатуру или production controller.

Иммутабельные Git blobs b359 и beb лично сравнены по11critical files: Pasha replay, Gabar inherited frames/key/tap/capture, CharacterPlayer/CombatPlayer/Yakuza movement, moving-shot ability/runtime, Core, CharacterLab/Input bindings и wrapper — byteexact; captured source inventory подтверждает эти SHA.9shared recorded global keys поменялись (audio/export/shared wrappers),54новых keys добавились. Это честный dependency comparison, не all-source-equivalence claim. При финализации WORK Pasha replay уже стал WIP telemetry candidate; он **исключён** из этого failure review. Собственные snapshots frozen-beb-sources/ защищают от подмены старой версии новым исправлением.

## Минимальная диагностика и допустимый fix

Нужна свежая isolated sequential ROOT запись с прежними oracle/assertions, плюс пассивная telemetry: actual Input vector/character_run/physical-key state на каждом physics sample, planned fixture key events/sequence/pressed/echo/device/monotonic time и segment, window flags/focus notifications. Полезен expected-held contract: пока сам fixture не отпустил направление/Shift, прекращение actual held-state объявляет запись INVALID_INPUT_CONTRACT, а не зелёный gameplay PASS.

Можно проверить Movie-only FLAG_NO_FOCUS как контролируемую **гипотезу изоляции** (существующий WORLD precedent). Requested/read-back flag не равен доказанной эффективности; нужен реальный новый run и negative control. Не менять production Input/персонажа, пока причинность не доказана. Нельзя удерживать keys повторными reassertions каждый frame, опускать>70, удалять held-run assertion, объявлять Reduced иначе/пропускать down/left, искусственно принимать отсутствие всех8поз или force score.

Контролируемый mid-hold release/focus negative должен оставаться обнаруживаемым. Реальное новое evidence должно пройти оригинальные393Movie/581live при исходных разрешённых source semantics и дополнительных held-input checks. Source telemetry-only scope и различия runtime/test/window явно разделить.

## Безопасное адресное продолжение

Old8/13 failure и все7positive child artifacts/receipts не менять. У current verify_p06.py нет resume interface; изменение old validation passed=false наtrue запрещено. После qualified fix — отдельный fresh Pasha live+Movie и remaining5: cast,cast_large_text,finisher_audio,npc_baseline,combat_baseline. Сохраняются exports/movie flags, actual export/PCM/performance правила.

Новый composed13 manifest обязан честно обозначить7reused +6fresh, единственные stageIDs, исходные operation/receipt/source/artifact/log/typedresult hashes. Любой изменённый production/critical first7 dependency требует адресной проверки affected stage, не автоматического reuse. Если fixture-only Pasha telemetry не загружается первыми7, точные body/shared harness dependencies позволяют сохранить их завершённую работу при явно проверенном nonruntime delta. Нельзя восстановить всю функцию на основании одного успеха debug probe. Новый resume/composition механизм нуждается в независимых pure negative checks и Lead разрешении перед исполнением; настоящего13-stage PASS пока нет.

ART source/исторические component PASS/old FAIL сохраняются. ПолныйP06, safe Root handoff, licensing/privacy raw11, remote current-head/base PR/CI/protection/merge, readiness/MDS/P07 остаются вне этого решения. Реальный Windows native host/listening/hardwareinput/FPS этим просмотром не проверены.
