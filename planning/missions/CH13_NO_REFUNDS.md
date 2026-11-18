# CH13 — Без возврата
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Общие gates MISSION_DESIGN_TEMPLATE/PRE_P07_REQUIREMENTS действуют. Новые map/director/assets/audio NOT_CREATED.

## Канон и различие D03
CH13_NO_REFUNDS / EV_CH13_COMPLETE; presentation13/chronology13, present, RYZHIK; prerequisiteEV_CH12_COMPLETE; timestamp пустой/production_pending. Рыжик проверяет обман поставщика, а не решает всю схему PRIME. Переплата/накладная относятся к его поставкам; verified operations/source/father не выдаются. D03 изCH06 sealed, повторноговыбора/повторных±отношенийнет.

Предупреждённый получает служебныйдоступ к кабинету поставок через ещё не захваченный прилавок. Непредупреждённый приходит к занятому главномувходу и возвращает оставленную накладную черезсоседнийпавильон. Контактпоставщика/схемацен понятнее, но не появляется новый globalevidenceID. ВCH18 реакция Рыжика/доступ к его подходу меняется по томуже D03; глава13 не «исправляет» факт, чтоНекитумолчал.

## Карта: торговый ряд и перекрытие пути
Мир2560×1152, grid16/camera640×360, стены между секторами кроме порталов.

| Зона/bounds | Связи/предметы |
|---|---|
| RF0_FRONT 0,0,640,640 | refuse spawn160,480; east640,y384..512→RF1; south640,x192..320→RF3 |
| RF1_STALLS 640,0,1280,640 | дваразныхпрохода вокругcover1056,192,128,224; east1920,y192..320→RF2 |
| RF2_OFFICE 1920,0,640,640 | ledger2240,224; south640,x2176..2304→RF4; safeCP1 |
| RF3_LOADING 0,640,1280,512 | accept spawn256,928; east1280,y832..960→RF4; receipt896,864 |
| RF4_BACK_ROW 1280,640,1280,512 | cover1664,800,128,160; связьизRF1 черезsouth640,x1536..1664; exit2432,1008,96,80 |

Accept начинаетRF3, затемRF4→RF2; refuse RF0→RF1 (документу(768,480))→RF2. Накладная localinstance расположена в зависимостиD03, не перемещается послеpickup. Цель обоих: сравнить её сledger вRF2 и уйти. Два выходаRF2/RF1 вRF4 позволяют не повторятьодинкоридор.

После сравнения объявление/лампа показываютзакрытие основного прохода RF1↔RF4, реальная shutter(1536,624,128,16). Открыта запасная связьRF2↔RF4. Если footprint/активныйконтакт встворке, закрытие ждётclear, безcrush/teleport; survivalне зависит отрандомногощелчка. РучнойFoverride вRF2(2144,560) доступен без расходуемогоключа, reopenпуть не запирает игрока.

## Encounter design и герой
E1_FRONT толькоrefuse: patrol(480,480), frontmelee/узкийзаход. E2_STALLS: shooter(1696,160)+rusher(1280,480), разные north/southlinesвокругcover; acceptможетобойтиэтотсектор, не проходитьради длительности. E3_BACK общийпослеwarning/shutter: rusher(1888,960)+patrol(2304,816), движениепоперёкрыночногоряда, выборвходаизофисаилиручногоoverride. Одинfinitecohort, не бесконечныйrespawn. Босса/HPspongeнет.

Ryzhik120/roll0.08+.32+.16/CD1.2, sweptbodyбезиммунитета, unarmed+optionalblunt(2112,480); environmentalтолькоеслибудетконкретныйregisteredprop — вэтойверсии такихнет. НельзяразрешатьFINулюбойвитрины. Обходдоступенбезготовогоролла, shooterпулинепрошиваютcover. Campaignpolicy/binding HighNOT_IMPLEMENTED.

## State, сцены и завершение
CP0 входvariant, sealedD03, receiptисходный, unarmed/CD0; двеветкине суммируются. CP1толькоreceipt_taken&&ledger_compared, hero(2304,512), RF2очищен, **обе** границывопасныекомнаты физическизакрыты: west(1904,192,16,128), south(2176,624,128,16), nojobs/hostilesinside. ВсеE3доCP1 существуют толькокакresourcecohort; instantiateonceпослевыходаизофиса/предупреждения. LateCP1послеактивацииE3запрещён. Restore:drawerfacts/завершённыеdeadIDs/двери/variant, E3notyetspawned, closedphysicaloffice, инструментworldoptionalне клонируется, armedstateunarmed. Неоткрыватьвсепутирадипочинкиневалидногоsave.

RF13_ARGUMENT, RF13_LEDGER, RF13_SHUTTER, RF13_EXIT_WARNED/UNWARNED NOT_CREATED. «Ты мне возврат обещал» / «У тебя теперь другая цена?» Конкретныйзнакомый/реальнаяфирманеобъявляютсямошенниками; сцены вымышленны. Последняя сцена послеE3dead/nojobs наexit:alive/receipt/ledgerchecked, complete_chapteronce. Нет второгоEV_D03/подареннойevidence/фармарепутации. Writefailure — повтор Fбезпотерипредмета; сохранённыйвыборD03неоткатывается.

## Ресурсы/темп/приёмка
BREAK THE ROUTE — новыйраскладритмаузкихрядов→широкогозаднегопрохода; shuttercueслышенсразу, не ждётбар. Новыеoriginalстол/торговыйряд/шторка/ledger/диалоги/стемыNOT_CREATED; P06roll/body/reactionsreuse. СравнениеCH06: там предупреждение/первыйзаходкпоставщику, здесьзаранеепринятыйвыбор, проверкацен иизменениедоступногопрохода; CH16—физическийносительПаши/данные, здеськоммерческийспор/ролл иручнойoverride.

План20–35min NOT_MEASURED. Runtimeгейт: обеD03ветки/meaningfulencounters, обеofficeдвери/footclearshutter/нетdeadlock/optionaltool, lateCP1/noE3respawn, writefailure/freshprocess/skip/FullReduced, Input/retry<1000ms/idle/deathcauses/wallframes/music/listening/ART иactualплатформы. Порогидоacceptancerun, ненафизическомdelta; безискусственнойзадержкивозвратаденег/HP/пустыхперемещений.
