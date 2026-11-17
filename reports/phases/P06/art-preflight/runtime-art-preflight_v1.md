# P06 — независимый ART runtime-capture preflight v1

**VISUAL_PRESENTATION_ACCEPTABLE_FOR_CAPTURED_CONFIGURATION.** Все45 actual runtime portraits читаемы и показывают правильные5 статичных выражений всех9 персонажей. Kaban neutral/angry reservation разрешена для этого UI: отличие brow/bridgefurrow видно при160×160. Это ограниченная приёмка визуальной подачи предоставленных captures, **не полный P06 PASS**, не независимый controls/QA gate, не review world/actions/finishers или exports.

Ревьюер `/root/art_review_p06`, read-only source/runtime evidence. Godot/controller/Git/генерация не запускались, исходники не изменялись; созданные artifacts только в разрешённом art-preflight каталоге.

## Основание и целостность

Финальные evidence: WORK `reports/phases/P06/attempt1/cast-native-02`, sourcehead из validation `9be2d7270a67e74b44bcf40fd4a5d44eddb062df`, совпадает с переданным автором. Независимо пересчитаны все410 файлов capture source inventory: текущие hashes совпали без расхождений. Все9 atlas hashes совпали одновременно с предыдущим portrait source preflight и inventory native02. Все45 PNG hashes соответствуют validation.

Native02 validation имеет `passed:true`, `phase_approval:false`, X11,193/193 checks,45 captures, sourceunchanged, actualnewprocessreload true. Оба command receipts exit0/passedtrue; просмотрены cast-replay/process-reload logs, SCRIPTERROR/ERROR/WARNING/leak сообщений не найдено. Отдельный reload receipt сообщает actualnewprocess=true, неизменный campaignfile и восстановленный CH01 resource/line1; эта новая проверка headless. Ревьюер не запускал её и не выдаёт прочитанные авторские чеки за собственный livecontrols тест.

Исторический native01 на source `12afd55388959fc3663ffc67d3dfe3213bd29f00` остаётся FAIL из-за Esc `_unhandled_input`→nullviewport после удаления scene, хотя193 checks внутри result были true. Он не стал PASS задним числом. Все45 native02PNG **byte-identical** к native01PNG, поэтому сделанные из первых screenshots contact sheets точно соответствуют финальному изображению; image artifacts и исторические metrics сохранены, основной review ссылается на02.

Capturefiles имеют **640×360**, portraitrect `[20,128,160,160]`. Project config задаёт viewport640×360/windowoverride1280×720/integer stretch; этот review оценивает фактический160px portrait в сохранённом render, а не отдельный внешний screenshot physical1280×720 desktopwindow. Это ограничение доказательства отмечено явно; признаков потери pixels/readability в сохранённой картинке нет.

## Что осмотрено

Независимо просмотрены fullUI individual samples Kaban neutral/angry, Ellana calling, Elya hurt, Gabar angry и Tega catchphrase; затем все45 portrait+speaker+text regions через9 contact sheets без уменьшения (native1:1). Для каждой картинки отдельно взят actual portraitrect и сравнен со своим правильным atlas frame0–4 поверх фактического UI background RGB16,21,34: **0 differing RGBpixels во всех45**. Это независимо подтверждает правильную expressionmapping, отсутствие фильтрового blur/искажения/дополнительного clipping и неизменность уже проверенного likeness. Сопоставление не подменяет человеческий осмотр: просмотрены реальные лица/текст всех45.

| Actor | Captured presentation |
|---|---|
| Gabar | Все5 читаемы; rectangularglasses/burgundy/shortswepthair сохранены; shout явно отличается. |
| Olezhka | Все5 читаемы; молодой cleanface/shortfringe/darktrainingwear, правильный speaker. |
| Timka | Все5 читаемы; нейтральный закрытыйрот и catchphrase smirk различимы, тёмный hoodie/борода сохраняются. |
| Ryzhik | Все5 читаемы; тёмный sidefringe/stubble/baggycrewneck, grin/headtilt честно static. |
| Tega | Все5 читаемы; tired bags отличимы от hurtbruise, greyhood/buzzcut, scream читается. |
| Pasha | Все5 читаемы; высокая lightbrownhair/leanface, excitedlaugh/shout, правильный speaker. |
| Kaban | Все5 читаемы; neutral/angry остаются близкими, но центральныйbrowV/bridgefurrow ясно усиливается в actualUI; regen сейчас не нужен. |
| Ellana | Все5 читаемы; ivoryblouse/longnose/darkwaves, нет nativehemfringe/halo. |
| Elya | Все5 читаемы; softshorternose/darkVtop/headtilt/foreheadmarks, нет greybackground/halo; не перепутана с Ellana. |

Проверенные ранее собственные private-reference associations сохраняются: actual rendered portraits побитно совпали с принятыми sourcecandidates. Повторный rawphoto upload/copy не выполнялся.

## UI и замечания

В полном UI видны понятный заголовок полигона, selector/повтор/back, fiction/sandbox disclaimer, отдельный speaker и основной текст, затем кнопки advance/history/skip. Текст контрастный, Cyrillic glyphs читаемы, имена всех9 соответствуют лицам; основные реплики занимают1–2 строки, не режутся справа/снизу и не перекрывают портрет/кнопки. Портреты полностью помещаются в160×160 area, head/hair не обрезаны; тёмные волосы имеют достаточные pixelhighlights на фоне. All5 expressions реально показаны, а не заменены переменой имени/текста.

**Minor, необязательное улучшение:** у Tega catchphrase очень широкий scream, а строка «Вон лавка. Сначала посмотри, что под ногами.» выглядит сравнительно сдержанно по пунктуации. Это правильный frame4 и может читаться как раздражённый окрик; sourcefix не требуется. При narrative polish можно усилить характерный shouting accent в реплике, сохраняя естественную речь. Это не блокирующий expressionmapping defect.

Kaban reservation закрыта только для предоставленного layout/scale. Если портрет станет меньше/изменится filtering, проверку0↔1 повторить. Статичные45 screenshots не подтверждают animationtiming; newcharacters намеренно статичны, motion здесь не заявляется. Existingbleeps не прослушивались.

## Ограничения и дальнейшие gates

Предоставленный native02 visual evidence принимается в своей границе. World/portrait consistency, движения/actions/finishers6playables, actualcombat/readability/cancel, settings variants/reduced effects/textscales, physical display scales, Linux/Wine exports и nativeWindows не проверены этим ART preflight. Windows в author validation NOTTESTED. FullP06 independent ART/GAMEPLAY/QA/Lead на frozen source/evidence остаётся необходимым. Новые source/art/UI изменения после этого hashinventory требуют повторного corroboration/review по затронутой части.

Exact hashes45captures/evidence и410source corroboration: `runtime_art_preflight_v1_metrics.json`. Historicalfailedrun: `runtime_art_preflight_native01_metrics.json`. Derived sheets `runtime_<actor>_contact_v1.png` содержат реальные screenshot regions1:1; нулевые PNGdiff между01/02 зафиксированы в metrics.
