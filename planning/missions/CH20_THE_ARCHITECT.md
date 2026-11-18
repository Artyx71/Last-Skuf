# CH20 — Архитектор
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Многоэтапный PRIME-комплекс/финальное разоблачение, не готовая карта или босс. Общие MDS/Readinessконтракты обязательны.

## Канон и роль улик
CH20_THE_ARCHITECT / EV_CH20_COMPLETE; presentation20/chronology20, present, YAKUZA→OLEZHKA; prerequisiteEV_CH19_COMPLETE; timestamp пустой/production_pending. Здесь Денис«Кабан»раскрываетсякаквымышленныйорганизатор/отецбратьев. Макс — публичнаявитрина, не тайныйподлинныйвладелец. Сценапоказываетконтроль/давление, не «похожлицомзначитвиноват». Сатираявноfiction, реальныхлюдейнеобвинять.

Verifiedoperationsoptional: если evidence.founding_records && flags.witness_transfer, осмысленныйFсверкиполномочий/передачи можетrecord EV_VERIFIED_OPERATIONS→evidence.illegal_operations=true. Безэтихусловий/безэтогодействияскриптфлагневыдаёт. УжеполученноеизphoneCH14доказательствонеудаляется. Обязательнаясценаidentity/reveal неавтоматическийverifiedrecord: FAMILY_BUSINESS должнаостатьсядоступнойприотсутствииобеихулик/≥2refusals. D01/D06неповторять/неподменятьновымфинальным«хороший/плохой».

## Карта трёхэтапного комплекса
Мир3328×2048, grid16/camera640×360; физическиразделённыесектора, толькоуказанныепорталы.

| Зона/bounds | Связи/смысл |
|---|---|
| AR0_PERIMETER 0,1024,768,1024 | Якудзаspawn192,1760; east768,y1536..1664→AR1 |
| AR1_SERVICE 768,1024,1280,1024 | cover1152,1376,128,160; north1024,x1536..1664→AR2; east2048,y1664..1792→AR5 |
| AR2_SWITCH 768,0,1280,1024 | механическийрубильник1280,448; west768,y384..512→AR3; east2048,y640..768→AR4 |
| AR3_OLEG_ENTRY 0,0,768,1024 | Олегspawn192,768; cover384,320,128,160; связьвAR2 |
| AR4_CONTROL 2048,0,1280,1024 | защищённаякабинаКабана(2816,224); optionalrecords2560,640; south1024,x2816..2944→AR5 |
| AR5_EGRESS 2048,1024,1280,1024 | cover2560,1376,128,160; exit3168,1888,96,80 |

ЭтапAЯкудзаAR0→AR1→AR2внепубличнойлинии; этапBОлегAR3→AR2 отключаетуправляемыеставни; этапCбратьяAR4/reveal→AR5. Между A/B Якудза возвращается в cleared AR0, а не остаётся в будущей аренеAR2. Единственный AR0↔AR1 portal закрывается реальной дверью(752,1536,16,128); CP1 требует nohostile/jobsinsideAR0 и свободнуюстворку. E1patrolвAR1 остаётсяснаружи, Якудза82 быстрееегоchase67/имеетcoin иcover для возврата. ЕслиE1успелвAR0, CP1неставится/дверьнедавитактёра: нужен обычныйвозвратугрозынаружу, безwarp/иммунитета. ОлегAR3входитвAR2и играет E2, физическиотделённыйбратостаётсяAR0. ПослеE2иотключенияконтроляОлегспускаетсявAR1, завершаетоставшийсяE1еслижив ивыпускаетбрата. Тогда оба проходятпо ужеочищеннымAR1/AR2вAR4 дляreveal. Это конкретныйsafejoin, не escortчерезживуюарену.

## Сценовый босс: контроль пространства, не большой HP
Кабануправляетдвумя finiteконтурамиохраны/дверейиззакрытойкабины. Стадии — защёлка/подход→сменалиний→срывконтроля/разговор. ОннепуленепробиваемыйActorсневидимымфлагом: кабинаимеетреальныестены/стеклосworldcollision, доразговоранеактивнаяcombatмишень. Братьянеобязанызабитьотцакуламидляраскрытия. НоваяbossstagingHigh, не новыйdamageengine.

A_E1SERVICE: толькопосленачальногоwarning; защёлкаоткрываетобычнуюwestдверьAR3↔AR2дляОлега, неотключаетбоссакнопкой/нетаймергонки. patrol(1536,1760), coin/LOSобходЯкудзы82безFIN/оружия. B_E2SWITCH: Олег106,patrol(1056,768)+shooter(1792,288), coverотпули/counterтолькомelee. ПервыйFрубильнику выключаетпервыйконтур, после1.2sвидимого/слышимогопредупрежденияставнязакрываетоднулиниюAR2, ноостаётсяпоказанныйобходчерезcover; footprintвстворкеждётclear, crush/телепортанет. ВторойFмеханическойзащёлке(1920,864) открываетвходAR4послеочисткиE2, нетpatternпулибезcue. C_E3EGRESS общийфинальныйfinitecohort rusher(2496,1856)+shooter(3072,1216), двеcoverлинии, анеочередные100HP.

Точная AR2геометрия: fixedpartitionx1456,w16 разбита наsegments(1456,32,16,224),(1456,384,16,384),(1456,896,16,96). Междуними northportal y256..384 среальнойставней(1456,256,16,128) иsouthportal y768..896 беззакрывающействорки, всегда128px. CoverA(1088,288,128,128), CoverB(1568,448,128,192), rightapproachcover(1664,352,96,128). До команды севернаялиния: (1376,320)→(1536,320); послеwarning/occupancyclearnorthзакрывается, остаётся южная: (1376,832)→(1536,832)→(1920,864). Switch(1280,448) westотpartition, latch(1920,864)east. Ниодин актор не запираетсянасвоейполовине: southalwaysopen, door не наносит crush. Прямоугольники не являются готовымart и требуют actual LOS/footprint/native proof после реализации.

Порядоккомандбосса/позицииодинаковыприretry, survivalнеждётмузыкальногобара. ДобратьсякрубильникамможнонаbaseОлегебезновогооружия; Якудзавсегдануждаетсявприкрытии/route, нестановитсясупергероем. Переходыактивногогероя толькобезстарыхjobs/сновойtrustedgeneration. Друзьявsafeсекторахнеполучаютпроизвольнойlocalinvulnerability.

## Сцены и checkpoints
AR20_ARRIVAL, AR20_COMMAND_A/B, AR20_FACE, AR20_AUTHORITY_OPTIONAL, AR20_EGRESS NOT_CREATED. «Не Макс это придумал» → реакциядвухбратьев → конкретныесловаКабана/подписанныеполномочия, нерассказвсезнающегонаблюдателя. Обязательныйrevealнепропускаетсяпервойпулей; seen-skipсохраняеттожеположениеоткрытыхдверей/конечныхcohorts.

CP0Якудзапериметр. CP1 только AR0refuge с одной enabledдверью/insideclear/attacksempty: активенОлегAR3health1/unarmed/CD0, Якудза(192,1760)вAR0, E1вAR1снаружи(либоdead), E2initialвAR2. DoorAR2north/west/eaststatesсохраненыобычно, ониневыдаютсязазащитуЯкудзывнутриE2арены. CP2 после E2dead/controlsdisabled и safejoin (E1тожеdead, оба прошлиclearedсекторы)/reveal: обаAR4safe, входыAR2↔AR4иAR4↔AR5closed/enabled, optionalverifiedrecordсохранёнтолькопоactualevent. E3доCP2resource/noinstances, onceпослепервоговыходавAR5/warning; позднийCP2послеE3forbidden. ОтказоткопийнеблокируетCP2/exit. Initrestoreневыдаётниprimaryending,ниавтоматическойevidence.

Финалaliveактивныйгерой,identitysceneвидена,controlsdisabled,E3resolved/nojobs,оба вышлиизопасногосектораиexitbeat→complete_chapteronce. Бойбосса/фаза нетаймерыожиданияUI; writefailure/invalidstageсохраняетисходныйsave и повторяемуюбезопаснуюзапись. ДверьalternateAR1→AR5закрытадоcontrolsdisabled; еёконкретнаяshape(2032,1664,16,128) предотвращаетраннийbypassreveal/босса.

## Assets и actual acceptance
Originalкомплекс/рубильники/ставни/кабина/мировойКабан/постановочныекадрыещёнесозданы; P06portraitКабана неготовыйbossworldsprite. FAMILYBUSINESSthreatmotif+NEXTREP/LASTSKUFсоответствуютPOV, bar/duck/retry/bosscommandsSFXбезобрывов, signal/mixer/listeningпослерендера. Highдиректорбосса/physicalgeometry/typedCP/policies/новыйартмузыкаостаютсяopen.

План35–50minNOT_MEASURED, многоэтапностьнеоправдываетпустыеэтажи/повторволн/HPinflation. Actualтриэтапа/baseweak/finiteконтуры/всепорталы/всепрерванныеF/occupancyshutters, optionalproof×старыеулик×refusalsсохраняютWIFEalways/FAMILYreachable/BROTHERHOODусловно. Реальныеinput/retry/wallframes/idle/deathcauses/music/art/платформы, независимыйGameplay/QA/Lead. ОтличиеCH19—раскрытыйконтроль/familyconfrontation,непоисквзноса; CH21—подготовкаразвязки,невыборprimaryиэпилогов.
