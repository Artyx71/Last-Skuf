import sys,subprocess,json,shutil
from pathlib import Path
w=Path.cwd();r=w.parents[2];sys.path.insert(0,str(w/'tools'))
from verify_p06_cast import sources,write,sha
base=w/'reports/phases/P06/owner-preview-20261115-05';build=w/'build/P06/owner-preview-20261115-05';friendly=r/'build/P06_DEV_20261115_05';assert not friendly.exists() and not friendly.is_symlink()
frozen=json.loads((w/'reports/phases/P06/ryzhik-roll-01/native-03/source_hashes.json').read_text());assert sources()==frozen,'Export must match complete reviewed native03 source exactly'
argv=[sys.executable,'tools/export_p06_preview.py','--output',str(base),'--build-output',str(build)];code=subprocess.run(argv,cwd=w).returncode
if code:raise SystemExit(code)
preview=json.loads((base/'preview.json').read_text());linux=json.loads((base/'linux_smoke/result.json').read_text());win=json.loads((base/'windows_smoke/result.json').read_text());expected={'gabar_training','olezhka_training','timka_present','timka_prime','ryzhik_training'};assert set(preview['available_combat_fixtures'])==expected;assert linux['renderer']=='X11' and win['renderer']=='headless';assert preview['source_unchanged'] and sources()==frozen
old=w/'build/P06/owner-preview-20261115-04'
for name in ['PLAY_LINUX.sh','PLAY_WINDOWS.cmd','GODOT_COPYRIGHT.txt','GODOT_LICENSE.txt']:shutil.copy2(old/name,build/name)
(build/'ПРОЧТИ_МЕНЯ.txt').write_text('АЫАЫ: Последний скуф — DEV preview 2026-11-15 / 05\n\nЭто прототип P06, не готовая кампания и не релиз.\nPLAY_LINUX.sh / PLAY_WINDOWS.cmd открывают полигон. Папку переносить целиком; профиль этой сборки отдельный, прежние DEV01–04 сохранены.\n1: Габар. 2: Олежка с окном блока. 3: современный Тимка. 4: Тимка в прайме. 5: Рыжик. 6–7 пока не готовы и сохраняют выбранного героя.\nWASD/Shift: движение; Space: толчок; F: приём; C: отмена; V: добивание; Tab: инструмент; R: повтор; O: эффекты; Esc: меню.\nРыжик: F — перекат вперёд по направлению взгляда, со столкновениями со стенами и коротким оглушением рядом при приземлении. Неуязвимости нет, удар может прервать перекат. На добивание нужно успеть к уязвимому противнику; Space помогает его оглушить.\nСовременный Тимка: F — шаг назад без неуязвимости и добиваний. Прайм: Space — тяжёлый контроль; F — захват близкого уязвимого противника без оружия. В настоящем силы прайма не появляются.\nОлежка: F — ограниченное окно блока спереди с последующим ответом при успешной защите; панель показывает окно и восстановление. Габар: F — направленный силовой выпад.\nМеню: F5 полигон, F6 портреты/диалоги; CH01 и журнал доступны из меню. Полигон не открывает сюжетные главы и не выдаёт способности кампании.\nLinux проверяется настоящим рендером; Windows PE — под Wine headless. Native Windows не проверен. Новых аудиотреков в этой сборке не добавлено; аппаратная задержка и FPS ещё не оценены.\n')
assert subprocess.run(['bash','-n',str(build/'PLAY_LINUX.sh')]).returncode==0
cmd=(build/'PLAY_WINDOWS.cmd').read_bytes();assert cmd.count(b'\r\n')==10 and b'\\r\\n' not in cmd
files=[{'path':str(p.relative_to(build)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(build.rglob('*')) if p.is_file()]
handoff={'schema':1,'scope':'LOCAL_OWNER_DEV_PREVIEW','phase_approval':False,'release_approval':False,'source_head':preview['source_head'],'reviewed_game_source':'8ad1729984321fbd646e96bbe9762a8c4cca689e','friendly_directory':str(friendly),'friendly_is_standalone_copy':True,'files':files,'available_combat_fixtures':preview['available_combat_fixtures'],'available_combat_heroes':preview['available_combat_heroes'],'linux_checks':len(linux['checks']),'Linux_actual_PNG':len(list((base/'linux_smoke').glob('*.png'))),'Wine_headless_checks':len(win['checks']),'native_windows':'NOT_TESTED','new_feature':'Ryzhik original128drawings and physical interruptible roll; 5fixtures/4actorIDs, full P06 pending'}
write(base/'owner-handoff.json',handoff);write(build/'BUILD_MANIFEST.json',handoff)
# Standalone owner copy survives worktree cleanup. Old previews untouched.
shutil.copytree(build,friendly)
for item in files:assert sha(build/item['path'])==item['sha256'] and sha(friendly/item['path'])==item['sha256']
assert sha(build/'BUILD_MANIFEST.json')==sha(friendly/'BUILD_MANIFEST.json')
print('OWNER_PREVIEW_READY',friendly,'Linux',len(linux['checks']),'Wineheadless',len(win['checks']),flush=True)
