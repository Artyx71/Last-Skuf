# Независимый ART: Тимка present/prime, native01

**FAIL по coverage визуальной приёмки двух контекстов.** Проверяемый corpus — frozen source `3a9ff811fd3550ab7e91c3b3f042744936111bda`. Production-спрайты этим заключением не отвергнуты; компонент не получает runtime ART PASS до исправления двух измеримых пропусков и завершённой записи.

Reviewer `/root/art_timka_fin_v4` не автор controller/clip assembly/harness. WORK только прочитан. Godot/builders/controller/Git mutations/network/generation не запускались; записи — только ROOT `reports/phases/P06/art-timka-prime-01`. Личные фото не читались/не передавались. Прежние ART/Lead решения сохранены.

## Проверенные реальные данные

Live native01 действительно завершён: result248/248,66 actual viewport PNG,49 реальных contact records. Проверены source digests production-корпуса: character loader/player/presentation, parent controller, NPC, PolishFrames/Core/policy и все9 Timka WORLD/ACTION/FIN PNG/metadata/sockets. Это ограниченная проверка точного указанного corpus, не неизменность всей текущей ветки после последующей авторской работы.

Просмотрены реальные right-facing relaxed present и guarded prime, FIN24 anchor board, все24 полные финальные рисунка с ring-markers, затем16 native трёхкадровых полос F×4 и V×3категории×4, а также полные viewport с HUD/environment и2входящими hurt/death контактами. Все полосы извлечены из настоящих native PNG, не собраны из подставленных source sprites. Общее image evidence не выдаётся за проигранную полную анимацию.

На game-size присутствует собственная фигура Тимки, тёмный худи/макушка/обувь совпадают с принятой семьёй. В F контактном рисунке руки/пальцы отличаются от безоружного V palmpress; тупой предмет и environmental brace различимы в своих направлениях. Source UP environmental v4a сохраняется. NPC действительно показывают реакцию и затем отдельную неподвижную death-позу на этих native strips; найденная ранее headless 1→2 смена кадра не требует фиктивного переписывания NPC. Входящий удар заменяет F на собственный hurt/fall. HUD подписывает настоящее/прайм раздельно, оружие и F/V по контексту; видимой обрезки текста/персонажа на рассмотренных viewport нет. Это фактические положительные наблюдения, но они не закрывают нижеописанные пропуски.

## Ограниченно принятые FIN24 annotations

Все24 FIN clothing points проверены заново: schema2/profile/actor/kind, count24 и mapping `[0,1,2,5,6,7]`, direction/index/compact/source columns, actual frame RGBA SHA, sheet SHA, integral in-bounds coordinates, alpha255. FIN PNG SHA `26aa10f81a3d4d3197133983d7e117f976278420f40919b4d9a27e3c204e57ae`, неизменный относительно принятого source FIN24 f3f8e29f… . Во всех24 целых рисунках центр marker находится на собственной одежде (включая пояс/брюки у front-ready), не на коже/волосах/пустом фоне. Видимая классификация выполнена отдельно от автоматического palette-centroid метода. Это **приёмка source-аннотаций24**, не runtime-анимаций/полного actor integration. Предыдущие WORLD/ACTION60 annotations не пересматривались визуально повторно; данный корпус сохраняет их изображения/точки.

## ART-TIMKA-CTX-STANCE-COVERAGE-01 — HIGH

Expected: реальные направленные idle0/1 обоих контекстов и сравнение стойки при общем направлении. Observed: все8 capture names `present|prime_locomotion_down|left|right|up_stance` содержат actual animation=`idle_right`, frame0. Это непосредственно записано в result.captures и видно на PNG. Fixture `set_aim(direction)` не означает смену неподвижного facing. Trace после краткой реальной ходьбы иногда успевает показать правильный idle направления, но только frame0; второго idle reference не предъявлено.

Minimal fix: реальный Input по направлению → release/settle → assert `idle_<direction>`; дать idle пройти оба references0/1, захватить их и сохранить observed graph. Проверить обе стойки в каждом из4 направлений. Исправить capture/harness, не перерисовывать персонажа ради неверной подписи и не выставлять sprite.frame вручную вместо Input.

## ART-TIMKA-CTX-STRIDE-COVERAGE-02 — HIGH

Expected: наблюдаемая полная походка обоих контекстов, чтобы оценить читаемость переходов и реальное различие движения. Observed: held Input всего8ticks (~0.133s). У prime walk6fps период одной ссылки~0.167s; все4 prime walk-captures показывают frame0, trace также frame0. Present trace показывает frame0, post-draw capture успевает frame1, но полный4frame цикл не показан. Метаданные `world6/7` против `world2..5` доказывают выбор source, а не хорошую анимацию походки.

Minimal fix: реальный held Input хотя бы2 полных цикла с достаточным запасом (~42ticks или фактически проверяемое полное окно), assert/capture все4 present и2 prime walk references, затем возврат к направленному idle. Отдельно увидеть переходы и повторный цикл в завершённой записи. При доказанном визуальном дефекте потребуются конкретные собственные рисунки; сейчас такого вывода по одному frame0 не делаю.

## ART-TIMKA-RECORDING-EVIDENCE-03 — BLOCKED_EVIDENCE

ROOT durable receipt operation `e5426991ddf44791b8713777dcccba6e` имеет exit130, log только `live PASS`; receipt log SHA и argv SHA проверены. В `native-01` отсутствуют `movie/result.json` и `validation.json`. Частичный AVI сохранён автором и не выдан за полную запись; первопричина остановки не установлена. Не делаю выводов о crash/пользовательском закрытии/таймауте без доказательств.

Minimal remedy: после потребления прежнего operation и исправления coverage — новый bounded job с новыми output/build paths, достаточным timeout, complete movie result/probe/validation и source integrity receipt. Старый operation не повторять и старые файлы не перезаписывать. Отдельная locomotion съёмка допустима, если exact production art/controller bindings прежнего finisher corpus сохранены; для temporal приёмки F/V/Space всё равно требуется завершённая реальная запись, включая contact и recovery.

## Решение

`status=FAIL` относится только к текущей ART coverage компонента; третья зависимость ограничена missing complete recording. Full P06 attempt/status, старые PASS и source FIN24 acceptance не изменяются. Новые рисунки на основании этих coverage failures не назначаю: сначала исправляется доказательство. После нового точного evidence ART заново оценит две стойки/полные циклы/контактные последовательности и даст PASS_COMPONENT либо конкретный визуальный FAIL.

`runtime_approval=false`, `phase_approval=false`, `full_phase_approval=false`. Нет приёмки Gameplay feel/баланса, нового звука/слушания, FPS/physical latency, native Windows, DEV03/new exports, readiness/P07/merge.
