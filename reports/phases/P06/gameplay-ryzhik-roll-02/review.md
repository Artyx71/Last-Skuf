# Независимое Gameplay closure: Ryzhik roll, round2

**PASS_COMPONENT** на frozen `8ad1729984321fbd646e96bbe9762a8c4cca689e`. GP-RYZ-01 и GP-RYZ-02 закрыты новым actual native/movie03. Прежний407 FAIL сохранён без изменения: decision SHA256 `199b981dca95c001e118a0b1859fd1452719c7b19c2f466ab33743d2ad073cac`.

Область — Ryzhik training roll/readability и24 Full/Reduced FIN случая. Это не full P06/семь героев/all-archetype matrix, readiness, P07, merge, export или релиз. Reviewer независимо назначен от автора; Godot/engines/builders/controller/Git/network не запускал и WORK/code/state/queue не менял. Записи ограничены этой ROOT report-папкой. ART source/runtime verdict не использован вместо собственного просмотра.

## Frozen delta и evidence

Собственное raw RGBA decode-сравнение407→v2 подтвердило изменения только двух целых ROLL cells26/29 (UP2/UP5), остальные30 byte-exact; изменены лишь их два clothing anchors. Новый sheet SHA256 `494fdee20295ebcefe6ef84cd1a6dab5de84386590430bc9b01d1e3c4991590e`. Assets между8c10 и8ad неизменны. Production GroundRoll/controller/loader/Core/NPC code относительно407 не менялся. Последний delta добавляет replay coverage/persistent blood и bounded120s live/180s movie timeout.

Предыдущий8c10 native02 live418/418/120PNG был валиден, но movie завершился timeout124 на100s без MP4; этот stage сохранён в `earlier-timeout-02/`, не объявлен complete-media PASS. Новая03 запись полностью завершена на8ad: headless04 **311/311**, native **439/439 с128PNG**, movie **311/311**. Каждый actual result содержит3483 trace samples и61 Core contact;8 clothing-overlay records получены из живого effect pool. Reviewer самостоятельно пересчитал пути/фазы/контакты/FIN пары/TTL, не доверял summary как единственному доказательству.

Все1195 recorded source hashes и136 listed artifact hashes сверены с фактическими файлами без расхождений. Validation/live/movie/source-map hashes совпадают с producer handoff. Actual MP4 SHA256 `b32d70789ff24bf6afc997a65222e7da66779d2124d16ef7862ee721d67e9fa6`:1280×720/60fps,3513 кадров/58,55с. Critical source, actual native/movie data и portable manifest сохранены локально без engine/full-project/raw-AVI копий.

## GP-RYZ-01: UP направление и непрерывность — CLOSED

Непосредственно просмотрены native UP WORLD/0..7/WORLD и обе новые позы, затем18 неизменённых decoded movie frames: весь UP cycle с дополнительными кадрами на входе/выходе, Full/Reduced environmental UP contact/corpse и actual blood на новых позах. Видеокадры имеют собственный index/PTS; они не приравниваются к game physics tick.

UP2 теперь вытягивает руки/leading support к SCREEN TOP с задней камерой; UP5 возвращает head/torso/support к тому же направлению. В actual движении entry→компактные3/4→unfold5→landing6→stand7 больше не читается как обратный или sled-like кувырок. Изменение длины силуэта2→3 соответствует tuck, а краткое опускание5→6 читается как landing compression с последующим подъёмом7. Новый blocking bob/continuity дефект не выявлен. Вывод основан на renderer/movie, а не на совпадении метаданных.

Body path по-прежнему монотонный UP; во всех4 направлениях независимый интеграл `start + aim*180*clamp(clock-0.08,0,0.32)` совпадает с actual position с ошибкой<0,002px, путь57,6px, восемь own poses по порядку. Actual landing contact только на pose6/clock0,416667, damage0/stun control без score. Ранних контактов нет. JSON phase interval boundary0,4 проверялся с1e-9 tolerance из-за округления accumulated float; actual contact6 отдельно зафиксирован.

WORLD joins сохраняют прежнюю точную границу доказательства: короткий actual walk→idle→roll→idle→walk, без fixture reset внутри действия; непрерывно удержанный walk через весь roll не заявляется. DOWN/LEFT/RIGHT source cells и production clocks не менялись, положительные407 proofs сохранены; fresh03 заново проходит четыре route/contact/finite recovery/cooldown assertions. Wall/cancel/authority/reopen/replace/pause/reset и genuine incoming hurt/fatal сохраняются. Независимо проверены6 actual incoming Core receipts: damage1, hit_right/fall_right, не parry/не иммунитет.

## GP-RYZ-02: все12 FIN в обоих режимах — CLOSED

Новый replay действительно устанавливает reduced_gore через production OptionsStore перед каждым mode block, оставляя decals enabled для наблюдаемого сравнения. Выполнены24 явных route labels:12 Full(false) +12 Reduced(true). У каждого — Input-earned shove stun при HP1, включённый затем NPC physics, один lethal Core finisher receipt на own category/direction frame1, NPC contact1→corpse2, score100 и отсутствие повторного job/reward. Metadata-only подмены настройки не выявлено: в native/movie реально различаются blood/decals, при тех же player/NPC poses.

Для всех12 пар независимо проверены одинаковые actual outcomes `[enemy_health0,hits2,score100,damage_events2,player_health1,jobs0]`, одинаковые contact clock/damage и правильные category/direction receipts. Это измеренная once health/score invariance, а не сравнение только roll0damage из первого FAIL. Отдельный raw kills counter в outcome array не записан и здесь не объявляется измеренным; один lethal receipt/смерть/награда подтверждены.

Все48 FIN contact/corpse PNG Full/Reduced непосредственно осмотрены. Они были просмотрены в завершённой live02 записи; их bytes полностью совпадают с completed03 counterparts, что независимо сверено и перечислено в `visual-identity-proofs.json`. Те же10 UP PNG также byte-identical. Поэтому58 visual observations сохранены на точных файлах completed03 без ложного заявления о повторном просмотре каждой одинаковой картинки. Ещё8 fresh blood PNG просмотрены отдельно: всего66 наблюдаемых native03 images из128.

## Реальный persistent blood после hurt

Дополнительный controlled case наносит настоящий nonfatal Core melee hit, ждёт завершения hurt и затем запускает F UP без restart/очистки effect pool. В actual contacts здесь ровно один incoming damage1; health остаётся1, hits_received1, score0 и новых ghost contacts при roll нет. Retry cleanup проверен после полного случая.

Все8 live clothing-overlay records показывают `roll_up`, frames/source columns0..7, положительный TTL и decal position в пределах3,2px от live clothing offset. У новых source2/5 anchors `[23,31]`/`[23,33]`; raw TTL около17,57/17,37с. Native PNG всех8 фаз и movie новые2/5 осмотрены: след остаётся на ткани, не зависает в пространстве и не скрывает направление/опору. Это реальный engine effect после Core damage, не нарисованная поверх mock-схема. Artistic garment acceptance остаётся самостоятельным ART verdict.

## Наследуемые положительные результаты и границы

Предыдущие407 independent QA Gabar/Oleg/counter/Timka/layout/readiness/negative результаты и собственные raw-contact proofs остаются исторически сохранёнными; полные независимые QA reruns на8ad этот Gameplay reviewer не выполнял. Production code/assets этих других героев не менялись. Новый Lead/QA отдельно связывает current source, обязательный CI, exports и всю фазовую матрицу. Дисклозированный FIN13 local x0 edge тоже не менялся;407 actual sampling observation и отсутствие all-clear-border claim сохранены.

Открытых Gameplay findings в проверенном компоненте нет; дополнительных remediation tasks не требуется. Не измерялись subjective/live-AI difficulty, hardware input latency, wall-frame FPS, native Windows или художественное слушание. Fixed60 MovieMaker не доказывает live performance. Решение закрывает два конкретных407 замечания и не переписывает старый FAIL/timeout history или более широкие незавершённые gates.
