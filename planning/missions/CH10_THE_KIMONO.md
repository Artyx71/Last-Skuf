# CH10 — Кимоно
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Полный общий контракт — MISSION_DESIGN_TEMPLATE/PRE_P07_REQUIREMENTS; новые scenes/maps/policy/checkpoints/art/audio не созданы.

## Канон, POV и решение
CH10_THE_KIMONO / EV_CH10_COMPLETE; presentation10/chronology10, present, OLEZHKA→YAKUZA; prerequisite EV_CH09_COMPLETE; timestamp пустой/production_pending. Олег сталкивается с ложным предлогом Некита о кимоно/дзюдо: Олег на дзюдо не ходил. Он18летний преимущественно нормальный человек, а не невероятный мастер. Дорога к разговору использует освоенную защиту, сам братский спор не является боем/добиванием.

D01 делает Якудза в безопасной сцене после смены POV. EV_D01 accept: flags.kimono_truth=true и relationships.yakuza_olezhka+1; refuse: false и−1. Значимый эффект сейчас — реакция/дистанция братьев, позже CH17/21 разные доступы и поддержка. Доставать D06 раньшеCH17, улику отцовства/15тысяч/организатора здесь нельзя. Эллана не оправдание лжи.

## Карта и игровые эпизоды
Мир1920×1152, grid16/camera640×360. Между секторами стены кроме порталов; внешний периметр закрыт.

| Зона/bounds | Связи и постановка |
|---|---|
| KM0_COURT 0,0,768,576 | Олегspawn160,416; east768,y320..448→KM1; cover384,224,128,128 |
| KM1_PASSAGE 768,0,1152,576 | cover1056,256,96,160; south576,x1536..1664→KM2 |
| KM2_LANDING 768,576,1152,576 | stairs1536,768; west768,y832..960→KM3; physicaldoor(768,832,16,128) |
| KM3_FLAT 0,576,768,576 | стол416,800; Некит(544,928); выход(128,1024,96,64), safeconversation |

Олег KM0→KM1→KM2→KM3. E1COURT patrol(608,416), frontalmelee показывает parry и конечный recovery. E2PASSAGE shooter(1664,192)+rusher(1376,416) разнесены укрытием: пулю не парировать, боковую угрозу не блокировать спиной. Это анонимное вымышленное давление людей, ищущих Некита, не обвинение конкретного реального человека. Оба finite, реальныйLOS/дистанции, предупреждение перед поворотом. В KM3 нет hostile actor/атаки на брата.

Олег speed106, existing training_counter с фронтальным окном0.06..0.26 actionclock, только реальный melee, не afterdeath. Стартunarmed, без выдачиknife/firearm. Trustedcampaignfactory/scenegrant High до уровня. Нет новых боевых умений. Путьвквартиру не требуетанимацииказнибрата.

## Смена POV и сохранение
CP0: Олегначальныйhealth1/cooldown0/NPCspawns. Передразговором E1/E2 должны быть завершеныdeadIDs/nojobs, дверь KM2→KM3 закрыта enabledcollision, внутриKM3нетугроз. Только тогда CP1: активенЯкудзаcampaignescape, оба брата на authoredпозициях, боевые действия в диалоге отозваны, generationстарогоОлегаотменена. Квартирные прочиеграницы стены; угрозы не могутобойтисценучерезоткрытыйальтернативныйвход. Не считать invulnerability открытымубежищем.

D01фиксируетсяexistingStoryState once до CP2. Failurewrite оставляет UI без ложного признания/изменений отношений. CP2 втойжебезопаснойквартире, sealedD01, relevantdialoguebeat, никакихtransientcontacts. Loadне возвращаетвыбор, resumeнепревращаетSpaceвудар. Победа:alive/сценаисходаD01/выход, complete_chapteronce. Replay не меняет исход. Нет обязательнойновойсилы/снаряжения Якудзе.

EV_KIMONO_RECORD — optional F у стола(416,864) до EV_CH10_COMPLETE: записан факт слов Олега/показан предмет, flags.kimono_record=true once. Оба исходаD01 позволяют запись; признание не является условием флага, иначе REAL_PRIME получил бы выдуманный новый gate. Не включать реальную запись голоса/чужой документ; постановочный текст/оригинальныйprop. После выхода можно получить пропущенный эпизод только разрешённым replay/forkprotocol, не записью в закрытуюглаву.

## Ритм, ресурсы и критерии
Вводнаяцельнайтибрата→frontal/parry иcover/ranged→тишинавквартире→признание/ложь иреакция→уход. KM10_APPROACH, KM10_NEVER_JUDO, KM10_D01, KM10_RECORD, KM10_EXIT_ACCEPT/REFUSE NOT_CREATED. Олег: «Я на дзюдо не хожу. Ты зачем моё имя приплёл?» Якудза: разные короткие оправдания/признание безкарикатурногоинтеллектаОлега.

Оригинальный NEXT REP дляподхода, спокойныйнизкий LAST SKUF фрагментдляразговора; EXPLORE/SUSPICION/COMBAT/CLEAR, dialogue duck/skip/retry не обнуляютtransport. Newkimono/квартира/двор/сцены/стемы нужны, P06bodies/портреты/counterreuse. План15–25min NOT_MEASURED; не растягивать разговор или драку. ОтличияCH17: здесь конкретнаяложь и D01, там ответственностьD06/действительнаяпомощь; CH05совместнаяработа, несемейныйспор.

ActualQAпослеproduction: двеугрозы/обходпули/parrywindow, trustedPOVswitch+closeddoor, всеD01/recordcombinations, CP1до/CP2послевыбораfreshprocess, writefailure/no relfarm/no friendlydamage/skip/pause/FullReduced, реальныеinput/retry/wallframes/music/ART/Linux+Windows и независимые reviewers. До этого только paperdesign, HIGHpipeline/assets open.
