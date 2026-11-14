# Независимое ART SOURCE review — Timka FINISHER v2b

**FAIL — исправить две целые позы: UP4/index28 и UP5/index29.** Предыдущие направление UP, own-neck clinch и поля исправлены. Новый all32 просмотр выявил недостаточную различимость firearm-reference от blunt и environmental от unarmed. Все прочие source-находки ниже не являются runtime/P06 приёмкой.

Reviewer `/root/art_timka_recovery` независим от автора/сборщика/controller. WORK только прочитан; записаны исключительно ROOT `reports/phases/P06/art-preflight/timka_finisher_preflight_v2b*`. Godot/builders/Git/controller/сеть/генераторы и авторский helper не запускались. Сырые фотографии не читались/не копировались/не передавались.

Master v2b SHA `87f031b8c639fd0e92c9469eb084e9797c8c84a33837d713565bfa0c7cd84177`; native SHA `0d67c1f19006830ebe3cccfce4cdcd0ab6babbe3e5875421c01ddf1d4f8f7876`. Сверены собственные принятые WORLDv4c/ACTIONv2b/portrait, generation metadata/prompt/references и обе assembly recipes. V1 FAIL сохранён, не переименован в PASS.

## Независимая проверка цепочки

Полностью реконструирован v2a из неизменного v1 и сохранённого rawv2 `13268c8c8c4d39026522dd0d2cd99285a932d39cfe8b19fd92702d9ed0e3da22`. Генератор выдал шесть корректируемых UP-поз в других столбцах; проверены **целые** source-cell mappings24→25,25→26,26→27,27→28,28→29,30→31. Остальные26 ячеек v2a byte-exact v1. Сошлись каждая cell RGBA SHA и весь v2a.

Далее независимо воспроизведён v2b:25 целых ячеек оставлены byte-exact относительно v2a,3 только перемещены,4 получили явный пропорциональный wholefigure NN fit (indices13/21/26/28; масштабы0.969697/0.963855/0.969697/0.982456). Сошлись исходные/resized/support/output SHA и весь master v2b. NN меняет детали/число support-пикселей — сохранение исходных пикселей не заявлено. Полное alpha>=128 support сохранено при переносах; размещение уменьшенных фигур не отрезало пиксели их уменьшенного support. Прежний no-fit authorization rejection/log просмотрен как исторический author artifact; reviewer его не запускал. Его `outputs_created_on_failure=false` не выдаётся за независимо наблюдавшийся в прошлом факт.

Shared0/6 всех четырёх строк остались source-byte-exact v1, включая UP0/UP6. Итоговые изменённые source-индексы против v1 ровно[2,11,13,21,25,26,27,28,29,31]. Во всех32 source-полях минимум16px, native периметры прозрачны. Desired24 не превращён в обязательный gate.

Независимо восстановлены32 полные ячейки192×256→48×64 NN/палитра/alpha128/неизменный фиксированный row reference DY. Все RGBA-байты/32SHA/весь native совпали. Native384×256, pivot24,58,32уникальных рисунка,36 непрозрачных цветов, alpha0/255. Непрозрачной потери от pack/alignment не найдено. Эти числа не доказывают различимость категорий.

## Свежая визуальная оценка и закрытые находки

Просмотрены полный master и все32native на светлом/тёмном фоне с собственными WORLD-позами, все6 source-only последовательностей WORLD→shared0→categorycontact→shared6 в четырёх направлениях, UP0–7 как целые крупные source-ячейки. Own portrait/accepted ACTION остаются identity/reference evidence; настоящий игровой target/contact clock этим не проверен.

UP1–5 теперь тянутся/целятся вперёд вверх экрана от камеры; инструменты продолжаются вверх от хватов, а не за спину к пяткам. **TIMKA-FINISHER-SOURCE-UP-CONTACT-01 закрыт для направления.** UP7 имеет две обращённые внутрь хватательные кисти впереди/выше макушки и место удержания перед собой; собственного плеча/шеи руки больше не касаются. **UP-CLINCH-01 закрыт.** Поля соответствуют mandatory16: **GUTTER-01 закрыт.**

Камера, макушка, swept волосы/короткая борода где видима, худи с длинными рукавами/опущенным капюшоном, брюки/обувь и малые кисти сохраняют собственное семейство Тимки. Нового нарушения анатомии/масштаба от скромных wholefigure fits не обнаружено. DOWN2 сдвинут целиком вверх9sourcepx: это не потеря тела, но его фактический переход/проекция пола потребуют native-проверки. Истинные runtime joins не подменены source-раскадровкой.

## TIMKA-FINISHER-SOURCE-UP-ENV-READABILITY-02 — MAJOR

**UP5/index29** почти повторяет UP1/index25 по поднятым открытым ладоням и силуэту согнутых рук вокруг макушки. Небольшие отличия ног/пикселей не делают требуемый environmental grip/brace отличимым от low palmpress. Ни разные SHA, ни будущий event/category label эту source-проблему не закрывают.

Минимально перерисовать **целую UP5**: сохранить исправленное facingUP и собственную камеру/макушку/пропорции, но показать иной grounded захват/толкание подразумеваемого ledge перед собой — ясный наклон корпуса, упор стойки и согнутые хватающие запястья/предплечья вместо повторения raised open palms UP1. Никакого ledge/сцены/жертвы рисовать не надо; minimum16 и целые рукава/кисти сохранить.

## TIMKA-FINISHER-SOURCE-UP-FIREARM-READABILITY-02 — MAJOR

**UP4/index28** в48×64 даёт практически тот же короткий тёмный округлый вертикальный tube/baton-профиль над двумя кистями, что UP2/index26. Узнаваемая структура пистолета недостаточно читается без подписи; исправленный facing сам по себе не доказывает, что нарисован именно firearm.

Минимально перерисовать **целую UP4** с узнаваемым compact pistol frame: согласованные slide/barrel и grip/frame/trigger-guard cue, переживающие NN до native. Две малые руки поддерживают его; цель остаётся впереди screenTOP. Допустим небольшой forward three-quarter угол для видимости конструкции без разворота facing. Не добавлять flash/projectile/второй предмет/огромное оружие, не двигать/красить отдельные конечности и не зеркалить. Reference не выдаёт Тимке оружие.

Сохранить остальные30 complete cells в следующей версии, если нет новой документированной причины изменения; сохранить raw/v1/v2b/recipes. Эти два targeted wholepose fixes требуют нового all32 review. Исправлять вновь UP7 или другие закрытые клетки только ради одинакового числа поз не требуется.

## Решение и границы

`all32_freshly_reviewed=true`, `source_only_acceptance=false`, `runtime_approval=false`, `full_phase_approval=false`, `phase_approval=false`. Строгое source adoption сейчас запрещено статусом FAIL. Native target/environment alignment, sockets/reach/facing/LOS/contact clock, physics Input/урон/очки, звук/ощущения/FPS/exports/P06/Lead/merge не принимались.

Peaceful_present не получает ни finisher, ни prime. Athletic_prime может в дальнейшем получить только unarmed/blunt/environmental при действующей gameplay authority; sharp/firearm остаются reference. Принятие исходной категории и разрешение игрового действия — разные проверки.
