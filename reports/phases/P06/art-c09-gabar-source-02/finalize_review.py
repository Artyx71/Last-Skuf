from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');O=R/'reports/phases/P06/art-c09-gabar-source-02';W=R/'.autopilot/worktrees/P06';S=W/'assets/source_art/npc_styles/gabar';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
frozen=json.loads((O/'source-freeze.json').read_text());changed=[f['path'] for f in frozen['files'] if sha(R/f['path'])!=f['sha256']];assert not changed,changed
met=json.loads((O/'independent-metrics.json').read_text());man=json.loads((S/'preview-v3/manifest.json').read_text());assert all(f['native_rgba_sha256']==man['frames'][i]['native_rgba_sha256'] for i,f in enumerate(met['frames']))
write('source-after-check.json',{'files_checked':len(frozen['files']),'changed_files':changed,'all_snapshots_match_frozen_SHA':all(sha(O/'source-snapshot'/f['path'])==f['sha256'] for f in frozen['files']),'all24_manifest_native_frame_SHA_match':True,'prior_review01_decision_sha256':sha(R/'reports/phases/P06/art-c09-gabar-source-01/decision.json')})
fail=['R5C1','R5C2','R5C3','R5C4','R6C1'];descriptions={
'R5C1':'DOWN weapon is a long narrow light taper below fist, no legible perpendicular pistol grip/short slide; reads like rusher blade.',
'R5C2':'LEFT hanging weapon repeats narrow light pointed strip with fist at upper end; compact handgun silhouette missing.',
'R5C3':'RIGHT hanging object has a rounder/capsule-like end than the other cells, but remains a narrow rod without recognizable offset grip/slide profile; not legible as the own compact pistol at source/native scale.',
'R5C4':'UP weapon beside anatomical right hip reads as long tapered blade; no independently readable handgun geometry.',
'R6C1':'New DOWN release preserves anatomical right hand, but the object below that fist is a slim straight light blade/rod, not a recognizable compact pistol.'}
cells=[]
for f in met['frames']:
 d={k:f[k] for k in ['cell','archetype','role','direction','new_or_retained','source_rect_xyxy','native_bounds','native_rgba_sha256']}
 d.update(status='FAIL_WEAPON_IDENTITY' if f['cell'] in fail else 'RETAINABLE_SOURCE_WHOLEPOSE_ONLY',finding_id='ART-C09-GAB-03' if f['cell'] in fail else None,observation=descriptions.get(f['cell'],'Recoil or supported buckle meets source pose brief; exact bytes may be retained. Runtime paired geometry/terminal continuity not approved.'))
 cells.append(d)
write('cell-review.json',{'indexing':'1-based; columns DOWN LEFT RIGHT UP; rows patrol contact/release,rusher contact/release,shooter contact/release','whole_cells':cells,'wholefigure_redraw_cells':fail,'retainable_source_wholecells':[c['cell'] for c in cells if c['cell'] not in fail],'old_findings':{'ART-C09-GAB-01':'CLOSED_SOURCE_READABILITY: all12 contacts now show noncombat open/slack arm silhouette and grounded recoil.','ART-C09-GAB-02':'CLOSED_HAND_OWNERSHIP: both newDOWN releases now keep original right/screen-left weapon hand and free left/screen-right floor hand. Shooter weapon identity fails separately.'}})
mat=[]
for kind in ['patrol','rusher','shooter']:
 for di in ['down','left','right','up']:
  contact=next(c for c in cells if c['archetype']==kind and c['direction']==di and c['role']=='contact');release=next(c for c in cells if c['archetype']==kind and c['direction']==di and c['role']=='release')
  for cat,col in [('unarmed',1),('blunt',2),('firearm',4)]:
   mat.append({'actor':'gabar','category':cat,'NPC_archetype':kind,'NPC_direction':di,'contact_cell':contact['cell'],'release_cell':release['cell'],'player_FIN_contact_column':col,'static_result':'FAIL_TARGET_EQUIPMENT_IDENTITY' if kind=='shooter' else 'SOURCE_RECOIL_SHAPE_ELIGIBLE_FOR_PAIRED_PREPARATION','actual_pair_approval':False})
write('category-compatibility-matrix.json',{'static_bindings':36,'shooter_source_rejected_bindings':12,'other_source_shape_eligible_not_runtime_approved_bindings':24,'runtime_cases_executed':0,'entries':mat,'next_evidence':'Actual player fist/blunt/muzzle contact against matched target chest/shoulder socket, locked positions/facing and same tick, then supported release and compatible explicit terminal; source may share refs only when actual paired geometry agrees.'})
write('visual-inspection-inventory.json',{'method':'actual tools.view_image, source masters and native, owned nearest-neighbor wholecell comparison boards','input_images_viewed':['assets/source_art/npc_styles/gabar/source-v3/raw-edit.png','assets/source_art/npc_styles/gabar/source-v3/master.png','assets/source_art/npc_styles/gabar/preview-v3/gabar_npc_native.png','assets/source_art/npc_styles/gabar/preview-v3/inspection_3x.png','game/assets/art/enemies/shooter_sheet.png','game/assets/art/characters/gabar/finisher_sheet.png'],'owned_diagnostics_viewed':['weapon-identity-comparison-4x.png','shooter-source-native-wholecells.png'],'baseline_reaudit':False,'engine_runs':0,'image_generation_calls':0})
review='''# C09 Gabar source repair v3 — независимый ART review02

**FAIL_SOURCE_ART / FIVE_SHOOTER_WHOLEPOSE_REPAIRS_REQUIRED.** Review01 `985592e6…` остаётся immutable. Результат02 ограничен новым v3 source/packing; исторические baseline tests, generator или Godot не запускались. Производственные Game, SourceAudio, Git/Controller не менялись. Только новые owned outputs в этой папке.

Осмотрены actual raw-edit, assembled master, native PNG и inspection3x, затем собственные NN wholecell boards рядом с принятым shooter handgun и rusher knife. Дополнительно лично осмотрены прежние shooter WORLD и Gabar FIN для identity/category сверки. Это8 PNG views, не runtime captures. Прочитаны новые prompt/generation/assembly и оба recipe; предыдущие gate criteria и review01 действуют. Все31 frozen inputs и snapshot copies совпадают при after-check. Старое decision01 по-прежнему SHA `985592e6d599a9c1abc13703f4c7f71bd5385e5441e2dca688f821b4b4d7376e`.

## Что исправлено

**ART-C09-GAB-01 закрыт на source уровне:** все12 contact теперь дают читаемый recoil — голова/грудь отведены относительно согнутых опирающихся ног, руки раскрыты/ослаблены, две готовые атакующие кисти и прежний aimed-pistol силуэт устранены. UP остаётся настоящей задней проекцией; руки асимметричны, корпус/ноги показывают off-balance. Новые формы отличаются от старого enemy idle/attack. Не требуется снова переделывать эти позы ради большей театральности.

**ART-C09-GAB-02 закрыт по handedness:** rusher R4C1 и shooter R6C1 сохраняют оружие в исходной анатомической правой / screen-left руке, пустая левая / screen-right кисть поддерживает падение. Они целые supported knee-buckles. Исправление shooter ownership само по себе не доказывает правильность типа оружия.

Все24 фигуры целые, четыре проекции читаются, UP без front face, не найдено обрезанных рук/пальцев/оружия, новых конечностей или fake corpse. Release остаётся промежуточным оседанием; окончательное тело должно быть отдельной явно связанной совместимой corpse role. Архетипные цвета/hood/armor сохраняются. Дополнительный wardrobe/baseline redraw не запрашивается.

## Единственный открытый defect: ART-C09-GAB-03

**Пять новых shooter wholefigures теряют читаемость компактного пистолета.** Это observable identity defect исходника, а не предположение по названию manifest и не требование поменять стрелковую механику. Индексы 1-based; C1 DOWN,C2 LEFT,C3 RIGHT,C4 UP; R5 shooter contact,R6 shooter release.

| Cell | Source rect xyxy | Наблюдение |
|---|---|---|
| R5C1 DOWN contact | [0,1024,256,1280] | Длинная узкая светлая полоса с зауженным концом под кулаком; не читаются короткий slide и поперечная рукоять. Почти тот же ножевой силуэт, что у rusher. |
| R5C2 LEFT contact | [256,1024,512,1280] | Свисающий pointed strip, кулак на верхнем конце; компактная геометрия handgun исчезла. |
| R5C3 RIGHT contact | [512,1024,768,1280] | Конец более округлый, чем у остальных; предмет читается узким rod/capsule, без различимой offset рукояти и short slide. Это не основание называть его ножом с уверенностью, но собственный пистолет всё равно не узнаётся. |
| R5C4 UP contact | [768,1024,1024,1280] | У правого бедра длинный светлый taper, читающийся blade; отдельная handgun геометрия отсутствует. |
| R6C1 DOWN release | [0,1280,256,1536] | Рука уже правильная, но предмет под ней — узкий прямой blade/rod, не компактный pistol. |

Evidence: **weapon-identity-comparison-4x.png** показывает все четыре направления target рядом с реальным принятым P04 handgun и rusher knife; **shooter-source-native-wholecells.png** показывает целые raw и native клетки. Ошибка заметна уже в raw/master до scale. Нельзя объяснять её только квантованием/.24 export. Поза может держать pistol muzzle вниз и всё равно сохранять собственную короткую slide/barrel массу и рукоять; сейчас этих признаков недостаточно при native размере.

Минимальный fix: **только эти5 новых целых shooter figures**, с прежними recoil/grounded buckle, направлением, опорой и анатомической правой оружейной рукой. Сохранить узнаваемый собственный компактный handgun после штатного уменьшения: короткий массивный slide/barrel, раздельная offset/perpendicular рукоять/запястье и читаемый muzzle, без длинного светлого ножевого taper. Ствол опущен/отведён из боевой линии, свободная кисть не превращается обратно в aiming support. Не приклеивать отдельно пистолет или кисть к bitmap, не перерисовывать принятый P04 baseline. Новое source wholebody generation/technical assembly — root.

**Остальные19 source wholecells можно сохранить byteexact**: все patrol/rusher contact/release и shooter R6C2–C4. Это8 новых допустимых contact, новый rusher DOWN release и10 старых retained release. Их точные SHA в cell-review.json. Не требуется повторно генерировать эти19; новый fix не должен случайно их менять. Это локальное сохранение source для следующего review, не package adoption PASS.

## Техническая конверсия

Raw SHA `a7af3e81…`; assembled master `510c7869…`; native `00955ed9…`. Независимая RGBA проверка assembly подтверждает14 new whole256cells и10 exact v2 cells. Все10 retained native release также byteexact прежнему preview. Текущий atlas содержит24 уникальных RGBA cells — не38 новых финальных поз;24 текущих drawings и новый repair provenance считаются отдельно.

Независимая реконструкция export **совпала побайтно** без исполнения авторского recipe. Contact берётся целым alpha128 bbox, uniform .24 по обеим осям для всех12, NN; размер34–45px шириной /37–44px высотой, целиком вкладывается в48×64. Clamp embed сохраняет все sampled opaque pixels. Это uniform wholefigure scaling, а не изменение анатомии. Release сохраняет .25 whole256cell NN и crop8px только пустых боков. Anchor bottom58/pivot24,58, no dither, palette35+3; actual native33 RGB, alpha только0/255,21524 opaque pixels. Ни размещение, ни anchor не обрезают выбранную opaque область; все24 manifest frame SHA совпадают. Source master сам semi-transparent alpha0..254 и не должен называться уже бинарным pixel master.

Переход с .25 на .24 у contact допустим технически и не является причиной нового weapon defect. Разница масштаба с release/baseline и точный torso socket должны проверяться в реальной паре позднее. Этот source review не утверждает runtime pivot/центр массы или clothing/depth alignment.

## Категории и scope

Gabar FIN сохраняет разные contact columns1 unarmed /2 blunt /4 firearm, все четыре направления. Для patrol/rusher recoil форма source-совместима с подготовкой paired проверки этих категорий; каждый actual fist/tool/muzzle контакт обязан попасть в согласованный chest/shoulder объём. У shooter дефект собственного оружия относится ко всем трём incoming категориям, поэтому нельзя принять его лишь в unarmed или firearm route.

Матрица36 static bindings:24 patrol/rusher source shapes eligible для paired preparation,12 shooter bindings отклонены. Ни одна из36 не получила runtime physical compatibility approval: sheets не задают locked source/target positions и same-tick contact sockets. Shared contact может стать явным ref нескольких категорий только после этого доказательства. Нужны actual windup/contact/release/terminal, правильные facing, Full/Reduced, прежний authoritative Core и отдельные ART/Gameplay/QA/Lead gates. F-lunge не принят этим FIN review.

Package v3 пока **не разрешён к adoption preparation**. Следующий шаг —5 wholefigure repairs и свежий immutable source review. Pasha/Tega/C01 component решения не переоткрываются; full C09/P06/P07/merge и runtime не приняты. Report02 и все bound outputs не переписываются после verdict.
'''
p=O/'review.md';assert not p.exists();p.write_text(review)
dec={'schema':1,'status':'FAIL_SOURCE_ART','disposition':'FIVE_SHOOTER_WHOLEPOSE_REPAIRS_REQUIRED','role':'independent_ART_reviewer_not_author','created_at':datetime.now(timezone.utc).isoformat(),'scope':'C09_GABAR_V3_SOURCE_REPAIR_ONLY','source_art_package_approval':False,'source_adoption_preparation_approval':False,'runtime_approval':False,'C09_approval':False,'full_P06_approval':False,'P07_approval':False,'merge_approval':False,'phase_attempt_consumed':False,'previous_decision_sha256':'985592e6d599a9c1abc13703f4c7f71bd5385e5441e2dca688f821b4b4d7376e','old_findings_source_closed':['ART-C09-GAB-01','ART-C09-GAB-02'],'open_finding':'ART-C09-GAB-03','wholefigure_redraw_cells':fail,'retainable_source_cells':[c['cell'] for c in cells if c['cell'] not in fail],'retainable_count':19,'raw_sha256':met['raw_sha256'],'master_sha256':met['master_sha256'],'native_sha256':met['native_sha256'],'technical_conversion_valid':True,'assembly14new10old_exact':True,'retained10_native_byteexact':True,'native24_unique_cells':True,'engine_runs':0,'image_generation_calls':0,'subagents_spawned':0,'WORK_Game_Git_Controller_writes':0,'review_sha256':sha(O/'review.md'),'source_freeze_sha256':sha(O/'source-freeze.json'),'metrics_sha256':sha(O/'independent-metrics.json'),'required_next':'Only5shooter wholefigure source fixes, preserve19 exactcells, then fresh independent source review.'}
write('decision.json',dec);write('FINAL_HASHES.json',{p.name:sha(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='FINAL_HASHES.json'})
print(json.dumps({'decision_sha256':sha(O/'decision.json'),'review_sha256':sha(O/'review.md'),'final_manifest_sha256':sha(O/'FINAL_HASHES.json'),'status':dec['status'],'required_redraw':fail,'retainable':19}))
