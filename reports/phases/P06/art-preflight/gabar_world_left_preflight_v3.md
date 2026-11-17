# P06 — Gabar LEFT world preflight v3

**FAIL_CAMERA_PROPORTION_CONSISTENCY.** Gaitsemantics теперь читаются как настоящий left contactA→passingA→contactB→passingB и runA↔B sourcecandidate. Но камера/пропорции ушли в side-on platformer и не согласованы с V1/V2/принятой worldlanguage. Не переносить в production. V1/V2FAIL сохраняются, этот single-direction review их не отменяет.

Ревьюер `/root/art_review_p06`: actual master, actual48×64 native8frames, inspection4x, targetednative8x contact/runpairs и V2/V3idlecomparison. Godot/controller/generator/Git/source изменения не выполнялись; только собственные отчёты/derived diagnosticfiles.

Native SHA `dc54fa0b15f87ab7af22b048a747e14690f0435fbefccdd91111a8fcc22a6c4d`. Master `a6626b0f44f31fab9f2a94f291e6ab45c56ef3a1df26455b608d4fb4976948e0`. Source4×2 на1536×1024, целые384×512cells, flattenednative8×1/384×64. Manifest CANDIDATE_NOT_IN_PRODUCTION соответствует факту: production `world_sheet.png` по-прежнему V2SHA `3b1126fd51712883045fb9ec2b2725c017050e0a00fffdf91dc439f9f2c02571`.

## Гейт движения: заметный прогресс

Индексы0-based. Контакт2 имеет brighternear/anatomicalLEFTleg вперёд и darkerfarRIGHTleg назад, watchbearingneararm сзади. Контакт4 действительно меняет роли: darkfarleg вперёд, brighternearleg назад и watcharm спереди. При первом общем просмотре legreversal слабее armreversal, но targeted8x actualnative и master подтверждают различие trouserramps/перекрытий. Это не просто новая позиция часов поверх прежней шагающей картинки.

Passing3/5 имеют узкие ноги под тазом, разную опорную/согнутую ногу и разные near/far shadingroles. Run6/7 также меняют near/far legroles и reciprocal arms; wristwatch перемещается вместе с одной anatomicalleft рукой, а не переезжает на другую. На leftdirection читаемый A/passA/B/passB и A/Brun появился. Это ограниченное положительное sourcefinding, **не runtime animation approval**; никакая East-handedness проблема ещё не закрыта, потому что eastframes здесь отсутствуют. Idle2 breathingmotion не одобрена только по двум похожим рисункам.

## MUST FIX / HIGH: camera и bodymodel

V3 показывает почти строгий боковой профиль: горизонтальный взгляд/нос, мало видимой верхней поверхности головы/плеч, вертикальный длинный torso, длинные голени и маленькая голова. Получается высокий стройный platformer actor вместо прежнего широкого укороченного overhead/chibi Gabar. Разница явна уже в native48×64 и сильнее на сравнительном8x.

Измеримый пример: V2leftidle0 opaque bounds `[11,7,37,58]`, width26/height51; V3leftidle0 `[16,2,32,58]`, width16/height56. При той же48×64cell V3на38% уже и примерно10% выше; crown почти упирается в верхний margin. Это не простой intentionalbreathingbob или другой leadfoot: меняется весь bodymodel/camera между directions. Голова/очки получают меньше nativepixels, identityanchors хуже читаются, хотя hair/glasses/burgundytee/watch в source узнаваемы.

Требуется цельная авторская camera/proportion correction всех8leftposes: вернуть pitch/видимость crown и shoulder tops, более крупную голову, укороченный perspective torso/legs и robustwidth **по V2wholeidle reference**, сохранив Gabar athleticwaist. Нельзя исправить camera одной overallrescale или anisotropic squash, bodypartcompositing, mirroring либо укладкой высокого человека в более широкий bbox — такие операции не создадут правильную перспективу.

Предложенный targetedwholepose imageedit с одним увеличенным V2leftidle0 как чётким camera/bodyreference разумен. При этом явно сохранить исправленные anatomicalphase roles2/3/4/5/6/7, near/far shading и anatomicalleftwatch; после edit заново сверить всеnativeframes. Это способ remediation, не предварительная приёмка результата. Не генерировать3остальные directionsets и другихгероев из V3platformer proportions.

## Technical integrity и ограничения

Alpha native0/255,32непрозрачных цвета,8уникальных RGBAклеток. Все8 sourceRects корректно flattened4×2, bodies имеют clearcell margins, nativebounds/hashes совпали с manifest. Master/prompt/inputrole hashes совпали с metadata; rawphoto для этого generationcall не заявлен. WholeposeNN/verticalsole58 не реконструирует anatomy. Pixelstructure честная, но технически правильные8hashes не доказывают камеру или фазу; положительный gaitfinding основан на реальных ногах/руках.

После wholeposecameraedit нужны повторный source review и actualnativeworld playback/groundcontact. Полный32frame4directionworld, eastwatch, gameplaymovement/actions/finishers и fullP06 gates остаются незавершёнными. Rawphotos не добавлялись/не загружались, source/runtime не изменены.

Evidence: `gabar_world_left_preflight_v3_metrics.json`, `gabar_world_left_v3_phase_pairs_8x.png`, `gabar_world_left_v2_v3_camera_comparison_8x.png`. Последние два содержат неизменённые nativecells с NNupscale/подписями.
