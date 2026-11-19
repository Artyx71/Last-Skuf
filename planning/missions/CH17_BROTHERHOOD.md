# CH17 — Братство
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Общий MDS/Readiness контракт обязателен; новый host/карта/сцены/assets ещё NOT_CREATED.

## Канон и решения
CH17_BROTHERHOOD / EV_CH17_COMPLETE; presentation17/chronology17, present, OLEZHKA→YAKUZA; prerequisiteEV_CH16_COMPLETE; timestamp пустой/production_pending. Олег вновь confrontsНекита, теперь об ответственности за долги/ложь и опасность для друзей. Конкретнаяложь/кимоно и D01 ужеCH10; неигратьпризнаниеповторно. Кабан какорганизатор ещёне раскрыт.

D01accept даёт Олегу совместный вход/доступ к общейвстрече, refuse — отдельный подвал и дополнительный E1; это последствиестарогоотношения, не повтор±. EV_D06 в безопаснойсцене подконтролемЯкудзы: accept flags.yakuza_accepted_responsibility=true, refuse=false. Никакихновыхrelationshipincrements. Принятиеответственности за собственныепоступки не означает признания в преступленииорганизатора и не ставитfounding_records/illegal_operations.

## Карта и разные поступки
Мир2304×1408, grid16/camera640×360; walls междузонамикромепорталов.

| Зона/bounds | Связи/объекты |
|---|---|
| BH0_ENTRY 0,0,640,640 | acceptОлегspawn160,480; east640,y384..512→BH1; south640,x192..320→BH2 |
| BH1_STAIRS 640,0,1024,640 | cover1056,224,96,160; east1664,y384..512→BH3 |
| BH2_BASEMENT 0,640,1664,768 | refuseОлегspawn256,1152; north640,x1280..1408→BH1; east1664,y1088..1216→BH4 |
| BH3_MEETING 1664,0,640,768 | Некит(2016,512); south768,x1920..2048→BH4; safedialogue |
| BH4_DEPARTURE 1664,768,640,640 | lever1856,1088; exit2176,1248,96,80 |

ДоD06ОлегидётBH0/BH2→BH1→BH3. Встречаотделяетсядвумя дверьми west(1648,384,16,128) и south(1920,752,128,16), остальныеграницыстены. E1BASEMENT толькоD01refuse: patrol(928,1152), тесныйфронт. E2STAIRS shooter(1408,176)+rusher(1152,480): укрытие/контратакапоmelee, неparryпули. SafeсменаPOVтолькокогдапосещённыйsegmentdeadIDs/nojobs иобедверизакрыты/внутриBH3clear.

ПослеD06вBH4создаётсяодин E3patrol(2080,960), warningдоактивации. Accept: Якудза выходитчерезюжнуюдверь, Fмеханическийрычаг открывает связь BH2↔BH4 для Олега; освобожденная створканезакрываетсяподтелом. Олег проходитсобственнымbodyпоочищенномумаршруту, встречаютсяуexit. Refuse: НекитвыбираетличныйбыстрыйвыходчерезBH4безрычага, ОлегиспользуетзаранеепоказанныйотдельныйвыходBH2 у(1504,1248), дополнительныйегоscriptedобходнеиграетсякаквторойPOVзачистка. Обаalive, разница впомощи/дистанции, не вновомфлагеубийства. Этовидимыйпоступок, а не двеодинаковыереплики.

Олег106/counter, startunarmed; Якудза82/escape/noFIN/nolethalgrant. E3разрешаетшум/LOSобход, убийствоЯкудзойнеявляетсяpredicate. Двери BH4→BH2initialзакрыты, дополнительныйживойE1изнепосещённогоподвала не можетворватьсячерезнеоткрытуюдверь. ДляacceptлинияОлегаочищаетсядоD06: еслиbranchBH0оставилBH2непосещённым, E1тамвообще не создавался, онтолькоrefuseD01cohort.

## Checkpoint/финал
CP0выбранныйD01вход. CP1доD06:безопаснаяBH3, активенЯкудза, ОлегвclearedBH1заclosedwestdoor; roster/visiteddeadIDs/doorstates/unarmed/CD0, E3ресурсбезinstances. D06atomic→CP2sealedchoice, возвращениеприdeathнепредлагаетизменитьрешение. E3onceпослересюмирования/южнойдвери, позднийCP2послеегоактивациизапрещён. Actor/generation/actionsпередсменойсбрасываются, noresourcecrosscarry.

Finalalive && D06sealed && (accept:lever_open&&Oleghas_arrived || refuse:Olegseparate_exit_seen) && exit/dialogue. EV_CH17_COMPLETEonce, friendlybrotherнецельCore. Еслиwrite/close-bodycheckfailed — прежняябезопаснаясцена/повторF, не выдачапомощи/победы. ReplayнепереигрываетD01/D06, повреждённыйsaveне«лечится»лучшимиотношениями.

## Режиссура/контент/приёмка
BH17_APPROACH_ACCEPT/REFUSE, BH17_ARGUMENT, BH17_D06, BH17_HELP/LEAVE, BH17_EXIT NOT_CREATED. «Ты хоть сейчас скажи, что сам наделал» / «Я разберусь» имеетразныйпоступокпослеподтверждения. Этоэмоциональныйповорот, важнуюсценунесокращатьрадиKPI. NEXT REP→тихийLASTSKUF→напряжённыйвыход, bar/duck/retryбезrestart. Originalподвал/лестница/рычаг/сцены/music покаHigh; P06body/контактыreuse, ниодногоощущенияотновойглавынепроверено.

План20–30minNOT_MEASURED. ОтличиеCH10—некимоно/признаниефакта, а ответственность/физическаяпомощь; CH21—неокончательнаяразвилкаотца, а еёусловие. ActualматрицаD01×D06/дваподхода/разныедействия/некровавыйЯкудза, safePOV/двери/noE3respawn, freshCP1/CP2/writefailure/skip/pause/once/FullReduced, softwareInput/retry/wallframes/music/listening/nativeplatforms и независимыеART/Gameplay/QA/Leadпослепроизводства.
