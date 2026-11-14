# P06 — Gabar ACTION raw source preflight v1

**FAIL_SOURCE_CELL_BOUNDARIES_AND_CHARACTER_CONTINUITY.** Actual32 wholeposes есть и различают действия, но fixed8×4 native packing безопасно не получается: RIGHT contact и interact пересекают клетки. Несколько поз нарушают anatomicalLEFTwatch, а LEFT hurt теряет читаемую прямоугольную оправу. Никакого native/runtime/action/phase approval; placeholder или procedural repair не предлагается.

Reviewer `/root/art_review_p06`: actual fullmaster32, all four fullpose panels2x, face/wrist diagnostics и uncropped RIGHTcontact boundary region3x; source alpha128 whole-row connected-component bounds. Все32 оценены заново, не переносится world acceptance на action. Godot/controller/Git commands/source edits/generation/subagents не выполнялись; записи только permittedROOTart-preflight. После parent instruction repeat-file checking не продолжалось; последний шаг — фиксация уже проверенных фактов.

Master1536×1024 SHA `eadd532bc8e4017323a87663034635e643a50434efa292da138ff6b2e535c082`; prompt/metadata/input-role hashes фактически совпали. Inputs own Gabar world camera template + own approved portrait, rawphotofalse. Native `action_native_v1.png` и runtime `action_sheet.png` при inventory отсутствуют. Claimed author strictpack failure independently corroborated geometry; никаких safe native outputs reviewer не создавал.

## Geometric must-fix — не скрывать crop

В alpha128 у каждой whole row ровно8 connected fullfigure components; следовательно crossing — реальная часть фигуры, не background matte как у Olezhka v2. RIGHT contact index1 whole component bbox **row(206,31,400,233)**, внутри nominalcol1[192,384) этоlocalx14..208,width194. Fist выходит на16sourcepixels в recovery cell2. В cellcrop1 bbox(14,31,192,233) обрывается по краю; cellcrop2 содержит хвост чужого кулака наx0. Uncropped master сохраняет fist полностью, но fixed-cell slicing отрезает его и загрязняет соседа.

RIGHT interact index3 также пересекает границу: **row bbox(594,31,770,242)**, nominalcell3[576,768),localx18..194. Open fingertips выходят на2sourcepixels в hurt cell4. Поэтому nominalcells1/2/3/4 не имеют clear margins, а не только первый упавший pack cell. Other28 nominalcells alpha128 margins clear. Мастер за внешнюю границу canvas не обрезан; это не разрешает production slicing.

Bounded action: redraw WHOLE RIGHT contact/interact compactly inside intendedcells с clear transparent gutters, сохраняя camera/body/root/weapon-free contact. Нельзя замаскировать выход crop, обрезать fist/fingers, придвинуть только forearm или выдать component extraction за anatomical fix. Для194px-wide contact при original1/4 native scale ширина48.5px уже больше48 без margin; необходимо согласованное wholepose redraw/scale strategy, не silent cutoff.

## Anatomical watch и glasses — exact0-based indices

В upright views reference rule: DOWNLEFTwatch screenRIGHT, UPscreenLEFT, LEFTneararm, RIGHTfararm/occluded. Для crossed fire grip и rolled death правило screen-position само по себе недостаточно: прослеживалось соединение видимого forearm с sleeve/shoulder; неоднозначность не выдаётся за доказанную wrongarm.

| Direction | Concrete required correction | Positive/uncertain observations |
|---|---|---|
| DOWN | **1contact:** silverband на punching anatomicalRIGHT/screenLEFTwrist. **3interact:** RIGHT reaching wrist silverband плюсLEFTguardband. **7fire:** banded обе wrist вокруг pistol — duplicate accessory. |0/2/4/5 LEFTwatch совместим;6 curled exposed wrist совместимLEFT, сложный roll не выводится только из rowlabel. |
| LEFT | **4hurt:** visible near rectangular lens rims больше не читаются; thin diagonal temple/closed-eye strokes могут остаться. Нельзя считать rectangularglasses preserved по одному blackeyestroke. |0/1/2/3/5/6/7 watch наnearLEFTлибо compatiblecurl. Fire7 muzzleлево, overlapping twohand grip plausible, finalnative readability pending. |
| RIGHT | **1contact:** watch на extendednearRIGHTforearm. **2recovery:** watch наnearRIGHTguard. **7fire:** watched visibleforearm читается attached to nearRIGHTsleeve; LEFTsupport ownership должен стать анатомическиясным. **1/3cellbounds** выше. |0farwrist partlyoccluded, watch не обязан бытьвидим.3bare nearRIGHTreach compatible.4frontturnedhurt glasses/LEFTguard compatible.5groundednearRIGHTbare, farLEFTwrist hidden.6curledbody exposesnear/lowerwatchedforearm but rolledshoulder assignment uncertain; review не утверждает definitiveRIGHT только по row. Clarify in wholepose refresh. |
| UP | **0windup/3interact/5knockdown:** LEFT/screenLEFTwrist открыто голая безwatch, включая groundedpalm5. **4hurt:** watch наscreenRIGHT/anatomicalRIGHTguard. **7fire:** watchedforearm connects/readablyalignsRIGHTshoulder, LEFTsupport ownership неясна. |1contact/2recovery LEFTwatch screenLEFT coherent.6death wristsoccluded, отсутствиеwatch не объявляетсяошибкой. |

Это whole-pose corrections, без Python wrist paint, перемещения часов, face reconstruction или automaticmirror. Особенно fire: LEFTsupport может пересекать screenmidline, но исходник должен ясно разделять arms/shoulder ownership; нельзя просто поменятьband screenX. RIGHTdeath6 указан как unresolved anatomical reading, а не invented definite handedness defect.

## Порядок, likeness/camera, gun и reactions

Rows DOWN/LEFT/RIGHT/UP и eight indices соблюдены:0windup,1meleecontact,2recovery,3openhandinteract,4hurt,5knockdown,6deathhold,7fire. Windup cocked fist, extendedcontact и returnedguard recovery actualwholeposes distinct; это реальные артикуляции, не32hash duplicates. Hurt chestflinch, kneeling/palm-supported knockdown и curledcollapsed deathhold различимы. Deathhold честно static pose, не multi-frame falling animation.

Crown/shouldertop/shortforeshortenedlegs остаются Gabar overhead family; hair/burgundytee/charcoalpants/trainers и большинство glasses сохраняют identity. LEFT4 eyewear readability — отдельная конкретная регрессия. Hurt faces могут поворачиваться внутрьcamera, но общее действие сохраняется; полного direction timing/playability изrawsheet не выводится.

Fire7 содержитsmallpistol, muzzle видим в нужном direction: down frontbarrel, left/right sideprofile, UPaboveRIGHTshoulder. UPgun не спрятан целиком заcrown. Нет bakedflash/projectile/target илиblood/wounds. Twohandgrips partlyoverlap наside/upviews; после wholepose handedness corrections и nativepack их читаемость проверяется заново. No nativegun/muzzle-position acceptance сейчас — unavailable nativeatlas и sourcecell failure это исключают.

## Можно ли сохранить LEFT8 целыми позами

**Технически да, ART-приёмка всех8 — нет.** Все8 LEFT nominalcells имеют clear alpha128 margins. Самый широкий contact1 localbbox(5,30,190,241), ширина185sourcepixels, внутри192безcut. Otherleftcomponentbboxes записанывmetrics. Можно read whole192×256cell, NN2→384×512 и переставить исходныецелыеcells в4×2canvas1536×1024, сохранив source rect/hash/ordering. При дальнейшей48×64 packing net uniformscale1/4 original; никаких feature edits/poses reconstruction не требуется. Это permissible whole-source rearrangement/provenance, не одобрениеанимации.

Однако LEFT4 needswholepose eyewear correction. Поэтому retained reference candidates — LEFTindices0/1/2/3/5/6/7, а не all8approved. Если новый direction8source складывается из7original wholeposes+1authoredwholepose, provenance должен явно отражать каждуюклетку, originalsourcepreserved; независимый native/anchor/cadence review после сборки обязателен. Reviewer не писал такойasset вsource/runtime и не создавал authorapproval.

Следующийbounded шаг по parentplan: separate whole8poses per direction corrections, с прозрачными margins/watchownership/eyewear, затем independentnative source review. Runtime Olezhka evidence и новый ACTION task могут идти отдельно; это не разрешение self-PASS или повторного sourcecheck до задания.

Evidence: `gabar_action_preflight_v1_metrics.json`; four `gabar_action_v1_{direction}_wholecell_panels_2x.png` (diagnostic fixedcellcrops помечены mayclip, не candidates), four fullwidthrowgrid images, `gabar_action_v1_right_contact_boundary_uncropped_3x.png`. Prior world/source/runtime failures and accepted hashes не меняются. FullP06/combat/gameplay readiness не одобрены.
