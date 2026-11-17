# Независимый ART source review: Рыжик FIN32 v1a

**FAIL_SOURCE_ONLY.** Блокируют три signature contact клетки: **LEFT7/index15, RIGHT7/index23, UP7/index31**. Их направление вытянутой ударной ноги не соответствует направлению строки. Whole-sheet source adoption не разрешён. Остальные29 поз не имеют обнаруженных содержательных ART must-fix; это не приёмка runtime/всей P06.

Reviewer `/root/art_timka_fin_v4` независим от генерации/normalizer. WORK и pending source только прочитаны, картинки не исправлялись. Godot/builders/controller/Git mutations/generation/network не запускались. Диагностики и этот packet созданы только ROOT `reports/phases/P06/art-preflight/ryzhik_finisher_v1a_*`. Фотографии не читались/не передавались; ownWORLD и ownportraits сверены по SHA и визуально.

## Реальные32 позы и источник находки

Просмотрены raw/normalized sheet/native1x, четыре ownWORLD comparison, все32native клетки на тёмном фоне,24 ordered SOURCE_ONLY последовательности0→category contact→6, четыре whole-source signature увеличения и отдельные1-vs-7 direction comparisons. Клетки действительно содержат разные полные тела; метод вращения стоящего actor для искусственного roll не наблюдается в технической цепочке. В целом сохранены тёмные side-swept волосы, собственная голова/щетина, baggy navy/charcoal одежда, светлая обувь и overhead camera. Другая личность/рыжая макушка не введены.

Готовность0, обычная низкая kick1, blunt2, sharp3, firearm4, environmental5 и recover6 различимы во всех направлениях. UP сохраняет crown/back. Weapon reference позы не дают ability grant. DOWN7 показывает palm-supported low sweep с ударной ногой вперёд по диагонали к BOTTOM; отдельной содержательной source-находки у него нет. У других signature направлений ниже — реальное несоответствие contact direction, которое числом уникальных рисунков/точной упаковкой не исправляется.

## Blocking source findings

**RYZHIK-FIN-SIGNATURE-LEFT-DIRECTION-01 — HIGH, index15(row1,col7).** Лицо/корпус ориентированы LEFT, опорная ладонь находится слева/под передней стороной, но вытянутая нога и её крупная светлая подошва уходят вправо от таза. В declared forward LEFT contact отсутствует ударная стопа перед лицевой стороной. Обычная unarmed1 этой же строки показывает верное противоположное направление ноги. См. `left_signature_direction_comparison` и `left_special_SOURCE_ONLY`.

**RYZHIK-FIN-SIGNATURE-RIGHT-DIRECTION-02 — HIGH, index23(row2,col7).** Лицо направлено RIGHT, опорная ладонь справа, вытянутая нога уходит влево/назад. Это не читаемый forward RIGHT sweep contact. См. симметричный по смыслу whole-cell comparison и последовательность0→7→6; исправление должно быть самостоятельно нарисованной целой позой, не зеркалом LEFT.

**RYZHIK-FIN-SIGNATURE-UP-DIRECTION-03 — HIGH, index31(row3,col7).** Rear camera и palm support присутствуют, но вытянутая стопа уходит в правый бок. Заявленный контакт к screenTOP не читается; собственная unarmed1 показывает, как вперёд/TOP отличается от текущего бокового выноса. Само вращательное движение между отсутствующими кадрами нельзя предполагать как доказательство контакта на имеющейся contact cell7.

Минимальный результат исправления: **три новые целые coherent poses**, со своими торсом/опорной ладонью/сложенной второй ногой/вытянутой низкой ударной стопой в заданном LEFT/RIGHT/UP направлении, прежней личностью/камерой/масштабом. Нельзя переворачивать aim/hitbox/target eligibility ради рисунка, переставлять отдельные конечности, зеркалить/вращать готовую позу или выдавать предполагаемую невидимую промежуточную анимацию за contact. Сохранить остальные29 v1a master/native cells exact, затем свежий whole32 source review новой версии. Этот reviewer генерацию/исправления не выполнял.

## Независимая provenance/grid проверка

Raw SHA `cb284be8aae067d6dbc68d8d092cb6edbf2156bc7d3960c052591cd78411587e`; normalized master SHA `0c466833d9eb3dd91a62711a71434d765f2c8d496844b65e5725955cc530e604`; native SHA `885c32153baced7a2c202c0b773500a36c8cc158741299b1626307f3ae705c67`.

Заново построены full-row cuts, проверено покрытие всего alpha>=128 support, whole-source rect/hash, scale/size/placement семи фигур и восстановлен весь normalized RGBA. Семь indices10/11/20/22/23/30/31 обработаны целиком. Только31 имеет uniform NN scale0.9839572193→184×177, другие6 scale1; отдельной анатомической обработки/масок/рисования/rotation/mirror нет. Остальные25 полных raw source cells byte-exact. Clear gutters означают alpha128 support, не обязательно alpha0: максимальный alpha в выбранных cut columns по строкам1/24/112/5. Subthreshold fringe не выдана за отсутствующие пиксели; original raw/NOT_PACKED metadata сохранены.

Независимо восстановлен весь native32:384×256,48×64,pivot24,58,32unique,35palette colors, alpha0/255,zeroRGB приalpha0, fixedrow DY `[0,1,2,3]`. Все frame SHA/columns/directions/rects/mapping совпали. Placement/resampling/baseline не скрывают вырезанные части; после NN resampling нет дополнительной потери opaque при размещении. Это технический успех, не ART PASS трёх неверных направлений.

## Неблокирующие source/будущие runtime замечания

Requested16sourcepx gutter не соблюдён в18клетках; полный список в metrics. В особенности LEFT environmental13 имеет raw minimum2px и native bounds `[0,12,40,58]`: ладонь доходит доx=0. Дополнительная строгая reviewer-проверка «всегда свободный native border» поэтому не прошла; canonical source-inside/opaque-loss проверки проходят. По whole raw/native ладонь полная, доказанного отрезанного пальца не найдено. Это раскрытый source-padding/будущий atlas-sampling риск, не четвёртая blocking pose и не утверждение «всеnativeborder свободны». Actual edge sampling должен быть отдельно проверен перед runtime ART PASS; padding16 не объявляется выполненным.

Неблокирующий статус остальных29 относится к содержанию текущих целых source poses, включая DOWN7, с указанным sampling ограничением13. Кровь/жертвы/реакции NPC/контактная геометрия/тайминги/звук здесь не интегрировались и не принимались.

`source_only_acceptance=false`, `whole_sheet_approved=false`, `runtime_approval=false`, `phase_approval=false`, `full_phase_approval=false`. Предыдущие ROLL/ACTION source acceptance и открытый ROLL UP2..5 runtime gate не изменены. Нет приёмки Gamefixture/ability/художественного аудио/fullP06/readiness/merge.
