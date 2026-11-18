# CH14 — Рой агентов
DRAFT / DESIGN_NOT_RUNTIME_TESTED. Общие MDS/Readiness/privacy/metrics gates действуют; новые scenes/props/music и productionhost ещё не созданы.

## Идентичность, знание и D04
CH14_AGENT_SWARM / EV_CH14_COMPLETE; presentation14/chronology14, present, GABAR; prerequisiteEV_CH13_COMPLETE; timestamp пустой/production_pending. Габар сопоставляет проверяемую историю своего публичного пародийного проекта с тем, как код использовала PRIME. Он не автор преступнойсхемы; узнаваниеUI вCH05 и архивCH12 сами этого не доказывали. Разоблачение Кабана остаётсяCH20.

EV_D04 accept — игрок физически собрал/сопоставил verifiablehistory: evidence.open_source_origin=true и flags.gabar_exonerated=true. Refuse effects{}: не стирает старое доказательство и не даёт новыефлаги. Не заменять проверку «нажатьскачать» с бессмысленнымтаймером. D04после просмотра минимум2согласованныхисточников: опубликованныйстарыйcommitlog и ограниченный CX12_FRAGMENT_RETAINED из сценыB6: preview собственного пародийного фрагмента/дата/идентификатор сборки, сохранённыеГабаром в обоих D02. Оригинальныеигровыефайлы/хэши, не реальныеprivateGitтокены/API. Источник не требует pashas_backup/tegas_phone: этоограниченныйиндекс/preview, не полныйархивопераций. ПриD02refuseоригинальныйполныйноситель остаётсяпоCH12/16, аD04иосновнойвыход всёравнодействительно доступны. Canonicalдоказательство выдаётсяоднимexistingevent, не сыройстрокойизUI.

Если tegas_phone=true и open_source_origin=true, отдельная законченнаясцена PHONE_COMPARE может записать EV_PHONE_DECODED: flags.phone_decoded=true, evidence.illegal_operations=true. Иначе оставить телефон/копиикакесть, не даритьproof. Это обходнойисточникverifiedoperations доCH20. Если D04пропущен, CH18 невыдаётего заднимчислом. Если принят, позднееобвинение вCH18 спорно длявнешних, а друзья не забываютужеизвестное.

## Карта: работающие фланги и центр проверки
Мир2432×1536, grid16/camera640×360, стены кроме порталов.

| Зона/bounds | Связи/цель |
|---|---|
| AS0_ENTRY 0,512,512,1024 | spawn160,1312; east512,y1152..1280→AS1; north512,x192..320→AS2 |
| AS1_ARCHIVE 512,512,960,1024 | первыйисточникterminal864,1248; cover1056,960,96,192; east1472,y1152..1280→AS4 черезphysicalgate(1456,1152,16,128), закрытдоsealedD04 |
| AS2_PUBLIC 0,0,1472,512 | опубликованныйлог864,224; east1472,y192..320→AS3; south512,x1152..1280→AS1 |
| AS3_COMPARE 1472,0,960,768 | compare1936,352; south768,x1920..2048→AS4; safeD04 |
| AS4_EXIT 1472,768,960,768 | cover1792,1024,128,128; exit2272,1376,96,80 |

Игрок может сначала AS1 илиAS2, но смысловая проверка требует обоих источников, а не двухкопийодногофайла. AS3входизAS2east закрываетсяфизическойдверью(1456,192,16,128); связьсAS4 south тоже имеетдверь(1920,752,128,16). БезопасныйD04толькообедверизакрыты/insideclear/nojobs. Нельзя «поставить Габара в терминал» приоткрытойсоседнейарене. После sealedD04 оба входаAS4 (AS3south и AS1east) получают разрешение обычногоFоткрытия. E3ещёнет до первогоactualAS4enter/warning с любойстороны; связьAS1→AS4доэтогофизическизакрыта, обходневыпускаетигрокадообработанногоD04. После выборавыходвAS4доступен, отказнеобъявляетchapterнепроходимой.

## Encounter progression
E1 AS1 patrol(1184,1280)+rusher(768,864): чередование точногоlunge и укрытия, не ударthroughterminal. E2 AS2 shooter(1248,176) заcover(1088,96,96,160): сближение черездвапролёта/боковойпроход. E3 AS4 **послеD04иwarning** shooter(2240,928)+patrol(1760,1344), иначеAS4предметно закрыт дообработанногоchoice. Внешние «агенты» здесь конечные NPCохраны, термин «рой» не означает бесконечныеволны или новыеAIсущества.

Gabar110/existinglunge, стартunarmed, optionalfirearm послефактическогоподборау(1376,1376)допустимо толькочерезtrustedchaptergrant/инструмент. Пропускоружиянеблокируетвыход; base Gabar не получает moving_shotПаши. FINcategory+vulnerability/once/Coreкакраньше. Enemyshooterнеимеет выдуманногоammocounter.

## State, optional memorabilia и dream
CP0 AS0. CP1 передD04: оба локальныхsourcechecked, E1/E2dead, внутриAS3clear, обедвериenabled, player(1936,464), health1/unarmed/CD0. E3наэтотмоменттолькоresourcecohort/noinstances. D04durable→CP2сsealedисходом/phonecomparedstate иследующейсценой; E3создаётсяonceпослепервогосознательноговыходаизAS3/warning, позднийCP1/CP2послеегоактивациизапрещён. Не сохранять live attack/stun windows; resetjobs/epoch/propsresourcesдоуправления. Failedwrite не выдаётложныйD04/phoneproof, выборанеповторятьпослеуспешногокоммита.

OptionalFпредмет(1344,320)вAS2: EV_MEMORABILIA_3→flags.memorabilia_3=true once до EV_CH14_COMPLETE. Вместесmemorabilia1изCH03/2изCH09 он делаетдоступным отдельный секретныйсонТеги, а не даёт Габарупушку. SECRET_SUPPOSITORY_CANNON — самостоятельнаяoptionalсценаТеги/Ахшара со slapstickрикошетомвмонитор, безреальнойтравмыбрата. Запусктолькоизбезопасноговiewmode доchaptercomplete; временныйPOVсоннеявляетсясменойбоевогоГабара, основнойworldзаморожен/ограждён, по выходу точныйstateвозвращается. EV_SECRET_SUPPOSITORY_CANNON записываетсятолькопослереальнозавершённогоотдельногоэпизода/разрешённогоseen-skip иall3flags; не отодногокликапоиконке. Это Highfuturesecretproduction, несозданныйуровень; еслисонпоканеimplementedUIневыдаётcompletion. Основнойвыход не требуетсекрет/телефон/D04accept.

AS14_LOG, AS14_ARTIFACT, AS14_D04, AS14_PHONE_VALID/UNAVAILABLE, AS14_EXIT ресурсыNOT_CREATED. «Публикация раньше их проекта. Вот дата, а вот что они вырезали» — конкретноепоказательство, не магическое«ИИвсёдоказал». БезличныеAItoolsвлоре не подключают реальныесервисы/платныезапросы.

Победаalive/обаисточникаосмотрены/D04sealed(любой)/E3resolved/nojobs/exit+сцена, complete_chapteronce. Материалы попытки не подменяютevidenceфлаги, sealedD04неотменяетсяdeath. Phoneoptionalнеблокируетmainroute, badsavepreserve. СравнениеCH05—здесьдоказательство, не сходстворекламы; CH12—проверкастаройистории, не созданиеbackup; CH18—последствиеизвестногофакта, не повторD04.

## Ресурсы и actual gates
Новыеoriginalterminalprops/наглядныефрагментылога/комнаты/кадры/OPERATOR OVERDRIVE score иloopsNOT_CREATED, P06lunge/bodyreuse. MusicEXPLORE/SUSPICION/COMBAT/CLEAR/duck, сравнение/выход/phone имеют разныечитаемыеbeat, retrytransportсохраняется. План25–40minNOT_MEASURED, не ждать«анализ100%»/не суммироватьсон/AFKкакобязательнуюдлительность.

ActualматрицаD04×phonepresent/absent×3memorabilia/пропуски×skip/reload×allvisualsettings; sourceverifiability, обедвери/необходимыеfootprints, safechoice, onceE3/latecheckpoint/noevidencefarm, отказиmissingsecretпроходимы. Input→accepted/visible, смерти/причины/idle/retry<1000ms/wallframes/music/listening/ART/платформы и независимыйLeadпослереализации. Highhost/checkpoints/secretview/assetsне закрытыpaperтекстом.
