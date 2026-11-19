# CH18 — Предательство
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Применяется общий MDS/Readiness контракт; maps/host/assets/music/сцены не созданы.

## Канон, сохранённое знание и POV
CH18_THE_BETRAYAL / EV_CH18_COMPLETE; presentation18/chronology18, present, GABAR→PASHA; prerequisiteEV_CH17_COMPLETE; timestamp пустой/production_pending. Утёкшее название GABAR PRIME ENGINE выглядит обвинением, группа раскалывается. Использование опубликованного кода без согласия не превращает Габара в организатора. Кабана здесь не раскрывать.

Если D04/open_source_origin/flags.gabar_exonerated ужеtrue, друзья не забывают проверкуCH14: спорятобутечке/поступкахПаши, а внешнийвбросотбиваютпубличнымпоказомимеющихсяматериалов. Если proofнет, подозрениеостаётся; сценаневыдаётD04заднимчислом. D02предыдущаяпередачаbackup определяетналичиекопиидляпубликации, не вторуюпопыткувыбора/отношений. D03warnedменяетдоступкбоковомувходу, подготовленномупоставщиком/РыжикомпослеCH13; unwarnedвходзанят, не«РыжиквнезапноненавидитПашу».

## Карта и цели
Мир2816×1536, grid16/camera640×360, стеныкромепорталов.

| Зона/bounds | Связи/задача |
|---|---|
| BT0_MEET 0,0,768,768 | Габарspawn192,576; east768,y448..576→BT1; south768,x256..384→BT2 |
| BT1_UPLINK 768,0,1280,768 | terminal1376,320; cover1120,448,96,192; east2048,y448..576→BT3 |
| BT2_BACKSTREET 0,768,2048,768 | Пашаspawn256,1312; cover1088,1024,128,192; east2048,y1216..1344→BT4 |
| BT3_SAFE 2048,0,768,768 | Габарrefuge(2496,576); south768,x2432..2560→BT4 |
| BT4_EXIT 2048,768,768,768 | relay2304,1024; exit2688,1408,96,80 |

Габар MEET→UPLINK смотритвброс, затемSAFE. Его задача приD04true — передатьужеимеющийсяproofpacket, приfalse — сохранитьсообщениевброса/контекстбезподаркаevidence. UplinkF—сценовыйконечныйbeat без«ждите50%». Паша BACKSTREET→EXIT обеспечиваетфизическийвыход/relay; D03trueбоковойвходоткрыт, D03falseдоступчерезконкретныйE3front, цельтаже. Дваразныхтипаинформации не записываютновыйunknownflag.

## Encounter и безопасная смена
E1MEET patrol(608,576) meleeотправляетвпуть, E2UPLINK shooter(1792,192)+rusher(1536,576) разнесеныcover, lungeнепроходитстену. ТолькоE1/E2dead/nojobsиобедвериSAFEenabled:west(2032,448,16,128),south(2432,752,128,16) — ГабарпередаётконтрольПаше. ВсеостальныеграницыSAFEстены, обходчерезBT2непробиваетубежище.

E3BACKSTREET толькоD03false:patrol(1664,1312), егонадопройтиподприкрытием/контролем; true—этаbranchсвободна, не тотжеврагпереименованный. E4EXIT общий:Pashamoving-shotчерездиагональныеуглы:rusher(2400,1280)+shooter(2688,896), реальныйsight/cover(2368,1088,96,128). Finitecohorts, warning/seed/телеграфы, небесконечныесилы«разгневаннойгруппы».

Габар110/lungeunarmed; Паша125/moving_shotfirearm,4/.9passiveammo, noauto damage. ВходвПашуразрешаеттолькоегоscenegrant/ammoресурсы, неснаряжениеГабара. Другиемини-игры/взлом/crowdAIне нужны.

## State/разные последствия
CP0Габарначальный. CP1послеuplink/refuge:packet_type=`verified_origin|unverified_leak` изsealedD04, копиядоступнапоD02, обаSAFEdoorclosed, E1/E2dead, ПашаBT2health1/ammo4/CD0. E3/E4 resourcecohortsnotyetinstantiated, spawnonceпослевходавсоответствующийsegment. Restoreнепревращаетunverifiedвverified и не даётevidence.pashas_backupifD02refuse. Невалидныйpacket/saveотвергаетсяссохранениемисходника.

BT18_ACCUSATION_VERIFIED/UNVERIFIED, BT18_UPLOAD, BT18_PASHA_REPLY_SHARED/WITHHELD, BT18_ESCAPE NOT_CREATED. Приprooftrue «Мы это уже сверяли. Кто снова выкинул эту папку?»; безproof «Это твой проект?» — разныйконфликт. ПашадолженпризнатьпоследствиеотправкиизCH12, нестановитсяавторомкода. Результатглавы — группауходитссоответствующимзнанием/отношениями, новыхcanonical±/Dнет.

Победа:Пашаalive, relayисполнен, E3(ifpresent)/E4resolved/nojobs, дверьSAFEоткрытапослеочисткидвора иГабардошёлвclearedmeeting, финальнаясцена/exit→EV_CH18_COMPLETEonce. Friendbodyнеживётвоткрытойаренесиммунитетом. Приwritefail—безопасныйповторвыхода; CP1/switch/seen-skip/deathнеотправляютсообщениеповторно/нефармятотношения.

## Ресурсы и quality
OPERATOR OVERDRIVE→CAFFEINE RUNAWAY наединомtransport/согласованнойсменеPOV; SUSPICIONвспоре/COMBATнаулице/CLEARпослевыхода. Originalвброс/mockUI/город/сцены/стемыNOT_CREATED; portraits/FIN/своиP06stylesreuse. ОтличиеCH12—утечкауже случилась/разныестепенизнакомствасправдой, невыборbackup; CH05—публичноеклеймо/расколвместопервогоинтересакрекламе.

План25–40minNOT_MEASURED, не растягиватьаплоад/двойнойзачисткой. ActualD04×D02×D03матрица/physicalrefuge/safehandoff/realHUD/oncecohorts/freshsave/badwrite/replay/FullReduced, Input/retry/idle/causes/wallframes/music/listening/ART/Linux+Windows послеproduction; Hightrustedpolicies/checkpoints/dataUI/assetsостаютсяоткрыты.
