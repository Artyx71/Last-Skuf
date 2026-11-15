from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');O=R/'reports/phases/P06/art-c09-gabar-reuse-feasibility-01';h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
frozen=json.loads((O/'source-freeze.json').read_text());changes=[f['path'] for f in frozen['files'] if h(R/f['path'])!=f['sha256']];assert not changes,changes
pool=json.loads((O/'pool-inventory.json').read_text());candidate=next(f for f in pool['reaction_pool'] if f['state']=='knockdown' and f['direction']=='down' and f['frame']==1)
write('source-after-check.json',{'frozen_files_checked':len(frozen['files']),'changed_files':changes,'snapshot_SHA_all_match':all(h(O/'source-snapshot'/f['path'])==f['sha256'] for f in frozen['files']),'review02_decision_SHA':h(R/'reports/phases/P06/art-c09-gabar-source-02/decision.json')})
reasons={
 ('telegraph',0):'attack_ready',('telegraph',1):'attack_ready',('telegraph',2):'attack_ready',
 ('attack',0):'actual_outgoing_muzzleflash',('attack',1):'actual_outgoing_muzzleflash',('attack',2):'actual_outgoing_muzzleflash',
 ('recovery',0):'outgoing_shot_recovery_still_aimed_or_gun_centered',('recovery',1):'outgoing_shot_recovery_still_aimed_or_gun_centered',('recovery',2):'outgoing_shot_recovery_still_aimed_or_gun_centered',
 ('hurt',0):'exact_legacy_firearm_contact',('hurt',1):'exact_legacy_unarmed_contact',('hurt',2):'closest_unused_contact_but_insufficient_style_geometry',
 ('stun',0):'standing_hunched_stun_not_power_recoil_or_supported_release',('stun',1):'standing_hunched_stun_not_power_recoil_or_supported_release',('stun',2):'standing_hunched_stun_not_power_recoil_or_supported_release',
 ('knockdown',0):'exact_legacy_environmental_contact',('knockdown',1):'supported_fall_intermediate_not_contact;DOWN_release_candidate',('knockdown',2):'prone_terminal_not_contact_or_buckle',
 ('death',0):'exact_legacy_blunt_contact',('death',1):'near_prone_late_fall_not_contact_or_requested_compact_buckle',('death',2):'terminal_corpse',
 ('finisher_reaction',0):'legacy_restrained_hold_not_power_contact',('finisher_reaction',1):'exact_legacy_sharp_contact',('finisher_reaction',2):'terminal_corpse'}
reviewed=[]
for f in pool['reaction_pool']:
 d=f.copy();d['feasibility_reason']=reasons[(f['state'],f['frame'])];d['authorized_new_Gabar_contact_ref']=False;d['requested_DOWN_release_candidate']=f==candidate;reviewed.append(d)
write('reuse-assessment.json',{'all96_source_pose_assessments':reviewed,'replacement_cells':[
 {'cell':f'R5C{i+1}','direction':di,'role':'contact','status':'ART_BLOCKED_NO_COMPATIBLE_EXISTING_WHOLEPOSE','replacement_ref':None} for i,di in enumerate(['down','left','right','up'])]+[{'cell':'R6C1','direction':'down','role':'release','status':'EXISTING_WHOLEPOSE_SOURCE_REUSE_ELIGIBLE_PENDING_NEW_PACKAGE_AND_RUNTIME','replacement_ref':{'sheet':'game/assets/art/combat_polish/shooter_reactions.png','state':'knockdown','direction':'down','frame':1,'rect_xywh':candidate['rect'],'bounds':candidate['bounds'],'rgba_sha256':candidate['rgba_sha256']},'new_drawing':False,'legacy_category_contact_RGBA_match':False,'actual_pair_approval':False}]})
write('visual-inspection-inventory.json',{'actual_view_image_owned_boards':['shooter-all-states-down-3x.png','shooter-all-states-left-3x.png','shooter-all-states-right-3x.png','shooter-all-states-up-3x.png','closest-unused-candidates-5x.png'],'all96_wholefigures_personally_viewed':True,'closest8_extra_wholecell_views':True,'no_edited_weapon_or_anatomical_parts':True,'method':'Read-only atlas cell extraction, matte compositing and NN enlargement in owned report only; no production mutation or art generation.'})
review='''# C09 Gabar — existing shooter wholepose reuse feasibility01

**ART_BLOCKED: четыре contact остаются без совместимого wholepose. Один DOWN release пригоден как explicit existing ref.** Это feasibility audit, не review03 нового готового пакета, не source package/runtime/C09/P06 PASS. Два прежних FAIL сохраняются. Запрещённый moderation_blocked imagegen request не повторялся; reviewer не вызывал генератор, Godot, runner, Git/Controller и не менял Game/WORK. Причину toolblock здесь не переоцениваем.

Лично через actual view_image осмотрены **все96 shooter reaction wholecells**:8states×3frames×4directions. Четыре диагностических3x board содержат каждую фигуру; дополнительный5x board показывает четыре unused hurt2 и ближайшие DOWN release. Это реальный осмотр poses, а не поиск по именам состояний. Все96 RGBA hashes совпадают с atlas metadata,96 уникальны. Exact equality с shooter FIN определяет20 reaction cells, уже используемых как legacy category contacts; это не новые Gabar drawings. Прочитаны pack_generated mapping/исторический source README; принятый P04 baseline не переоткрывается.22 frozen inputs/snapshots после audit неизменны.

## Пригодный existing ref — только R6C1 DOWN release

`game/assets/art/combat_polish/shooter_reactions.png`, **state=knockdown, direction=down, frame=1**, rect **[768,0,48,64]**, bounds **[6,22,44,58]**, exact RGBA SHA **cd63f61ba646433b1a42b157e700bbb8444601af38ce795f68f0507736c466d1**.

Это целиком уже нарисованный NPC, с опущенным корпусом/головой, согнутой опорной ногой и компактным боковым оседанием; он ещё не лежит terminal corpse. Читается настоящий короткий handgun с slide/muzzle и offset grip. Оружие остаётся в анатомической правой / screen-left руке, опущенной к полу; другая сторона тела/колено поддерживают buckle. Он не повторяет ни одного legacy category contact по RGBA. Отличие от текущей v3 release — опора распределена между низкой оружейной рукой и коленом, вместо явно раскрытой пустой ладони у пола. Эта уже полноценная grounded поза физически допустима как shared промежуточный release; требовать совпадения каждой кисти с v3 шаблоном не нужно.

Разрешён лишь **source preparation с целым exact ref**, без вырезания пистолета, перехвата руки, зеркала/вращения или pixel paint. Это не новый рисунок и не новый Gabar contact. Shared release не должен выдавать standalone style uniqueness: новые compatible contact ещё отсутствуют. Будущий полный source пакет обязан явно записать этот ref, а actual paired runtime подтвердить переход из собственного Gabar contact к этому buckle и далее совместимому held corpse, alignment/depth/cloth в Full/Reduced. Сам fallback не меняет death/AI/score clock.

## Почему четыре contact не закрываются existing pool

**R5C1 DOWN, R5C2 LEFT, R5C3 RIGHT, R5C4 UP — ART_BLOCKED.** Нет предложенного разрешённого replacement_ref. Причины по всему пулу закреплены в reuse-assessment.json.

- Telegraph/attack/recovery (36poses) показывают готовность, выстрел с muzzle flash или выход из собственного прицеливания. Это outgoing enemy action, а не полученная Gabar chest/shoulder compression. Переназвать recovery в victim contact означало бы вернуть исправленный defect01.
- Hurt0/1 (8poses), death0 (4), finisher_reaction1 (4), knockdown0 (4) — **ровно20 прежних category contacts**: firearm/unarmed/blunt/sharp/environmental. Копирование/ретайм в новый style slot не даёт нового характерного Gabar contact. Shared ordinary reactions допустимы при честном ledger, но ими нельзя объявить закрытым этот конкретный отсутствующий style brief.
- **Unused hurt2** — ближайшие реальные кандидаты. DOWN [528,0,48,64], SHA96bd1a2b…: корпус собран вперёд, руки и gun близко перед животом, это короткий обычный flinch, не новый chest-back power recoil. LEFT [528,64,48,64], SHA16ee17d3… и RIGHT [528,128,48,64], SHAd03aa06d…: голова немного отклонена, но pistol всё ещё представлен вперёд и руки сохраняют aimed silhouette; отличия от legacy hurt1 слишком малы для требуемого собственного контакта. UP [528,192,48,64], SHAa34c0666…: почти вертикальная спина и собранные плечи, нет читаемой displaced noncombat arm/recoil формы. Наличие иных SHA не устраняет эти наблюдения.
- Stun0..2 (12poses) — standing/hunched neutral loss of readiness, а не короткий grounded chest impact; они не заменяют recoil и в DOWN не дают requested supported release.
- Knockdown1 (4poses) — уже falling intermediates, тело значительно ниже/впереди contact. Только DOWN релевантен открытому release slot; три остальных не следует ставить в contact ради gun identity. Death1 (4poses) уже почти лежит, а knockdown2/death2/finisher_reaction2 (12poses) — лежащие terminal figures. Они не могут быть контактной грудной компрессией или компактным промежуточным buckle.
- Finisher_reaction0 (4poses) — прежний restrained hold; он не изображает силовой hit. Перенос его в contact не добавляет необходимого движения.

Недостаточность source-пары не исправляется сменой speed, role label, category routing, montage или hitbox. Воспроизводимость baseline и читаемый pistol сами по себе не доказывают характерную реакцию на стиль. Category unarmed/blunt/firearm Габара имеет разные fist/tool/muzzle trajectories; здесь не найден даже полный four-way source contact набор, который был бы готов к такой paired проверке.

## Точный итог и ledger

Из пяти defect03 cells **один имеет легитимный existing wholepose release ref**, четыре contact остаются отсутствующими. Нельзя собирать ledger19new+5existing как завершённый пакет: подтверждено только **19 сохранённых C09 source cells +1 existing P04 release ref +4 missing contact cells**. Existing ref не увеличивает unique new drawing count. Source03 формального prepared package review **NOT_STARTED**.19 retainable cells из immutable review02 сохраняются побайтно; новый source master/atlas этим audit не создавался.

Полный source ART gate остаётся BLOCKED до фактических совместимых wholefigure contact drawings. Toolblock не основание ослаблять критерии или подставлять placeholder. Source adoption текущего v3, actual paired runtime, C09/fullP06/P07/merge этим отчётом не разрешены. Все output bytes после decision immutable.
'''
p=O/'review.md';assert not p.exists();p.write_text(review)
d={'schema':1,'status':'ART_BLOCKED_CONTACT4_WITH_ONE_RELEASE_REUSE_REF','role':'independent_ART_reviewer_not_author','scope':'READ_ONLY_EXISTING_P04_SHOOTER_WHOLEPOSE_REUSE_FEASIBILITY','created_at':datetime.now(timezone.utc).isoformat(),'formal_source03_review':'NOT_STARTED','source_package_approval':False,'current_v3_adoption_approval':False,'runtime_approval':False,'C09_approval':False,'full_P06_approval':False,'P07_approval':False,'merge_approval':False,'four_contact_replacement_refs':None,'blocked_cells':['R5C1','R5C2','R5C3','R5C4'],'source_reuse_release_cell':'R6C1','source_reuse_release_ref':{'sheet':'game/assets/art/combat_polish/shooter_reactions.png','state':'knockdown','direction':'down','frame':1,'rect_xywh':[768,0,48,64],'rgba_sha256':candidate['rgba_sha256']},'source_reuse_release_is_new_drawing':False,'retained_C09_source_cells':19,'new_P04_existing_refs_feasible':1,'missing_contact_cells':4,'all96_existing_reaction_wholecells_actual_viewed':True,'engine_runs':0,'image_generation_calls':0,'subagents_spawned':0,'WORK_Game_Git_Controller_writes':0,'review02_decision_sha256':'073430cdbf7c500d29d0eb4a57d1099cbc16e9d1d8289ebda0027d83e39e61c1','review_sha256':h(O/'review.md'),'source_freeze_sha256':h(O/'source-freeze.json'),'required_next':'Preserve19 sourcecells. At most prepare1exactexistingrelease ref. Four compatible contact wholeposes remain required; no finished package or source03 review exists.'}
write('decision.json',d);write('FINAL_HASHES.json',{p.name:h(p) for p in sorted(O.iterdir()) if p.is_file() and p.name!='FINAL_HASHES.json'})
print(json.dumps({'decision_sha256':h(O/'decision.json'),'review_sha256':h(O/'review.md'),'final_manifest_sha256':h(O/'FINAL_HASHES.json'),'status':d['status']}))
