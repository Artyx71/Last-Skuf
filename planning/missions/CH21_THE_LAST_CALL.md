# CH21 — Последний звонок
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Три полноценные игровые primaryветки и отдельный optionaloverlay. Ниоднаещёнепостроена. ОбщиеMDS/Readinessконтракты/actualacceptance обязательны.

## Идентичность и неизменные predicates
CH21_THE_LAST_CALL / EV_CH21_COMPLETE; presentation21/chronology21, present, POVвregistryвсесемь; prerequisiteEV_CH20_COMPLETE; timestampпустой/production_pending. Выборосновываетсянараннихпоступках, ане заменяетиходнимпозднимопросом. ИспользоватьтекущийStoryState.eligible/routes.json безновыхусловий:
- ENDING_WIFE_CALLING →21B_EVIDENCE_ESCAPE, доступнавсегда/каноническая. ЯкудзауходитпослезвонкаЭлланы, оставшиесяшестьпродолжаютвыбираться; этомиссия, не мгновенныйконецпо«уйти».
- ENDING_BROTHERHOOD →21A_BROTHERS_EXPOSURE, толькоkimono_truth && yakuza_accepted_responsibility && illegal_operations.
- ENDING_FAMILY_BUSINESS →21C_COVER_UP_ESCAPE, минимум2explicitrefuseизchoicesD01/D03/D06 и **нет** illegal_operations **и нет** founding_records. ПредложениеКабананеоткрываетпутьвобходэтогоpredicate. Моральноосуждённыйисход, негoodending.
- ENDING_REAL_PRIME — POST_STORY_RESCUE послеоднойprimaryиусловийoverlay:5evidence,5canonicalsecrets,kimono_record,phone_decodedкакroutes.json. Не четвёртаяprimary/необходнедостающихусловий. FAMILYиэтотoverlayнесовместимыиз-заevidencepredicates; не«исправлять»этоудалениемусловий.

НикакихновыхD/глобальныхотношенийвместоexistingrouteoutcomes. ФинальныйзвонокнеобвиняетЖинькувпреступлениях; Элянетотзвонящий/организатор. Тимкаpresentнеполучаетprimeдажевфинале.

## Карта веток
Мир4096×2304, grid16/camera640×360; каждаястрокареальнаяотдельнаясериякомнат/doors/cover, неперекраскаоднойарены. Внешнийпериметр и границы закрытыкромеуказанныхпорталов.

| Сектор/bounds | Назначение/связи |
|---|---|
| LC0_CALL 0,0,768,768 | safeprologue/звонок, Якудзаspawn192,512; east768,y448..576→LC_A; south768,x256..384→LC_B0; отдельныйвыходвLC_Cчерезлокальнуюсценуещёнеending |
| LC_A 768,0,1664,1152 | Aбратья:cover1120,256,128,192, switch1920,832, выходeast2432,y832..960→LC_FINAL |
| LC_B0 0,768,768,1536 | BвыходЯкудзыу(192,2112); relay/сбордрузей, east768,y1792..1920→LC_B1 |
| LC_B1 768,1152,1664,1152 | Bдвесвязанныебоевыелинииcover1152,1472,128,192 и1792,1856,128,128; north1152,x2112..2240→LC_A(запертодляB), east2432,y1920..2048→LC_FINAL |
| LC_C 2432,0,1664,1152 | Cслужебныйcover-up:закрытьчужойдоступ/Fпанель(3072,448), узкийэвакуационныйкоридор, exit3968,960,96,80; entryизLC0черезотдельныйсценовыйпереход |
| LC_FINAL 2432,1152,1664,1152 | A/Bразныецели/выходы; safeendingroom(3712,1984); отдельныеphysicalgates наихвходах |

LC_CнепритворяетсясоседнейсLC0 геометрически: переходсценычерезпоказанныйслужебныйкоридор/дверь выполняетпереносмеждузагруженнымисегментами,нетелепортврамкахбоевогомаршрута. ДляA/Bпереходы непрерывные, дляCвходпривязанкbranchresourceсвоейкарты. Неиспользуемыеbranchdoorphysicallylocked, hiddenпунктUIнесоздаётпатчвусловиях.

## Разные игровые маршруты
A BROTHERHOOD: ОлегLC_Aсfrontalpatrol(1280,704)+shooter(2144,256), cover/counterнепули; затемЯкудзаоткрываетмеханическуюсвязь(1920,832)поclearedsafeapproach, неубиваетотца. ВLC_FINALОлегдержитфронтпротивrusher(2944,1664), Якудза82добираетсякприёмуимеющихсяevidence/выходузаcover(3200,1856,128,160). Цель—помочьбрату/довестипубличноеизобличение, не создатьнедостающуюillegalflag. Финалbrothers_confront_father; yakuza_olezhka_accountability, эпилогиyakuza_accepts_debt/olezhka_supports_truth.

B WIFE_CALLING: ЯкудзаLC_B0проходитживойслабыйexitпослезвонка, затемконтрольпоследовательноостальнымшести. Gabar—точныйlungeвLC_B1первомпроходеpatrol(1056,1856); Olezhka—фронтальныйmeleeу(1536,1728); Pasha—движущийсяогоньпоshooter(2144,1312)изреальныхcover; Ryzhik—короткийlateralroll/обходдляручноговыхода(2208,2144); Tega—зарегистрированнаялёгкаятележкау(1984,2016)реальносдвигаетbodyиприкрываетлинию, невымышленнаявзрывнаяпушка; Timkapeaceful—отход/dоручканаclearedфинальномподходе, неclinch. Целиразные,не6повторныхзачисток. СледующийstageневызываетубитыхNPCзаново. НепоследовательныефинальныеотрядывLC_FINAL:patrol(2816,1920)+rusher(3328,1408), finite, отдельныеwarnedспавныпоступени. Финалwife_call_departure; дистанцияyakuza_olezhka_distance; yakuza_home_unresolved/olezhka_handles_aftermath. D03true—заранееподготовленныйбоковойdoorдоступвB1, false—добавочныйpatrolнаосновномвходе(864,1984), другиецели/контактысохраняются.

C FAMILY_BUSINESS: Якудзаостаётсясотцом, Fпанельзакрываетпоказанныйдоступдрузей, затемсамуходитчерезкоридорLC_Cсpatrol(3328,800), cover(3520,512,96,192)иальтернативнойпетлёйвокругнего. No-killpathобязателен, «работанасемью»неделаетгероясильным. Последствиепредательствавидночереззакрытуюдверь/реакциидрузей; негенерироватьдружественныхвраговдлярасстрела. Финалfather_pact_condemned; yakuza_friends_estranged; yakuza_complicit_isolation/olezhka_breaks_contact. Негероическаяпобеда/награда,неподменённыйAэпилог.

СменаA/Bактёровлибоallcurrentsegmentdead/nojobs, либо inactiveпартнёрыфизическивзакрытойsafeячейке; art/directorобязанысоздатьтакиеячейки вfinalresourceдоacceptance, несохранитьшестерыхнаоткрытомполуподиммунитетом. Trustedchaptergrantsbounded:Габар/Олег/Ryzhik/Tegaunarmed+тольковыданныйинструмент, Pashafirearm4/.9, Тимкаpresentбезоружия/FIN, Якудзаescape. Ниammoниpendingactionнепереходятдругомугерою.

## Branchcheckpoint и двухшаговый commit
CP0LC0, всеустойчивыеисторическиеD/evidenceпровереныexistingresolver. Во времясценывыбираетсяlocalroute_pendingсeligibleподсказками, **не** finish_story: текущийAPIразрешаетendingтолькопослеcompleteCH21. Внесённыйвsaveнеeligible routeотвергается, WIFEвсегдаостаётсядоступна. Послеосмысленнойсцены/выбораCP1хранитroute_pending/segmentID/playerID/cleareddeadIDs/physicaldoors/ресурсы/authoredsafeorigin. КаждаяноваяступеньA/B имеетsafecheckpointсemptyjobs/никакихживыхугрозвкомнате; будущиекогортыещёнесозданы, activationoncebysegment. Повторподгружаеттолькоещёнезавершённыйsegment,неиграетзвонок/отправку/мертвыхшестикратно.

Послефактическойпобедыветки(allrequiredphysicalgoals/alive/exit/endingdialogue)typedcheckpointbranch_done/durablecompletionproof, затемexistingcomplete_chapter(CH21...), затемfinish_story(route_pending)once. Есливторойwriteнепрошёл, mainchapterужеcomplete,primaryещёempty: следующаязагрузкапродолжает**валидированныйpendingfinishвrealstore**, анеавтоматическийreplayforkи невыбордругойветки. Требуетсяexplicitdirectorподдержкаэтогосостоянияпередproduction; старыйStoryService.begin_chapterforkдляcompleteнельзязватьвслепую. Невалидныйpendingproofневосстанавливаетprimary«угадыванием», сохраняетисходныйфайл/показываетошибку. ЭтонеобходимыйHighintegration, не новыйendingresolver.

ВсеepilogueIDs/relationshipoutcomesберутсяизroutes.jsonпослеcommit; ещёодинcallbackнетповторногореварда/сменыprimary. Death/cancelдоbranch_doneвосстанавливаетпоследнююsafeступень/тотжеeligiblebranch, ненаслаиваетmusic/SFX. Inputпоследнейрепликиневыстреливаетпривозобновлении.

## Optional REAL PRIME и ресурсы
POST_STORY_RESCUE—отдельнаяoptionalигроваяспасательнаяпостановкагруппы/взаимнойответственности, затемmutual_accountability/tega_dream_recontextualized/friends_optional_rescue. Онаещёнесоздана; выполненные5секретовнеравныпройденнойновоймиссии. Когдаactualэпизодзавершён иoverlay_eligibleпоexistingAPI, finish_overlayonce. НельзяотменитьуходЯкудзывWIFEилиперевестиТимкувprime; PRIMARYнепереписывается. ДваadditionaloptionalconceptsнестановятсяновымиусловиямиREAL_PRIME.

Новыеветки/финальныекадры/персональныедиалоги/тележка/соответствующаяregisteredphysics/doorячейки/стемыNOT_CREATED. СерьёзныйLASTSKUF/FAMILYBUSINESS/ансамбльмотивов, отчётливыйINCOMINGCALLбезлишнегозвуковогорезкогообрыва; realtimeSFXнеждутбар. Art/Audioпроверяютреальныефайлы/анимации/loop/переходы/listening; староеP06owneracceptanceнеявляетсяполнымсаундтрекомфинала.

## Пейсинг и actual gate
Планмаршрута35–55minNOT_MEASURED; счёткасаетсяоднойprimary, не A+B+C+overlayсуммой. Никакихдлинныхлифтов/бесконечныхволн/«погрузка100%»для7–9h. Важныекороткиеэмоциональныесценыоставляются, seen-skip/переходыс быстрымretry<1000ms.

Полнаяactualматрицаeligibleсостояний/отсутствующихproof/2из3refuse/FAMILYreachable/WIFEalways, каждогоbranchphysicalobjective/каждогоactor/presentpolicy идвухepilogues. Saveмеждуcompleteиfinish/неуспешныйwrite/restart/replay/primarylocked/overlayonce/FullReduced, дублиcallback/oldgeneration/jobcost, softwareInput/idle/deaths/actualchapterwalltime/wallframes/music/ART/QA/nativeLinux/Windowsдоступнымспособом. ПапкаMDSиStorygraphсимуляциинеравныпройденнымветкам; full21дизайн/Readiness/P07contentacceptanceразныеgates.
