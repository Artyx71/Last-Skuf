# Передача единственному контроллеру

Автор завершил source/evidence stage, но не phase review. Последний source: `bc9f7e6ba9fa9780b5456b3b5a07fc8051ba7444`; source hashes — `source_freeze_final_02.json`. Итоговая evidence commit/branch tip и SHA256 bundle находятся в ignored `.tools/p04g-handoff/receipt.json`, создаваемом после evidence commit. Bundle: `.tools/p04g-author.bundle`. Local object store: `.tools/p04g-author-git`; использует read-only alternates к основному object store и содержит собственные новые объекты.

Обычный common-dir Git запрещён окружением: см. `logs/git_common_dir_denial.log`. Actual phase branch/ref/index в общем `.git` не продвинуты. Не считать clean publication guard выполненным и не публиковать dirty base. На host сначала проверить bundle (`git bundle verify <absolute-bundle-path>`), parent `3de67a00f508e95d1e024fe833f877f93aee671d`, цепочку маленьких коммитов и hashes рабочих source/evidence. Затем импортировать candidate ref из bundle и установить авторскую phase/* историю/index только если исходная phase-ветка всё ещё на этой базе и файлы совпадают с candidate. Сохранить любые посторонние пользовательские изменения; не применять reset --hard/force push. Main и canonical automation state автор не менял.

Следующие проверки идут последовательно в одном worktree:

1. `python3 tools/verify.py --output reports/phases/P04G/attempt1/regression-host-01`
2. `python3 tools/verify_p04g.py --exports --movie --output reports/phases/P04G/attempt1/native-host-01 --build-output build/P04G/native-host-01`
3. Осмотр реальных Full/Reduced action/reaction PNG/engine frames, всех пяти finisher clips и 3 AI архетипов; native stress timings. Важно проверить новый integer-art набор художественно, не по hash/count.
4. Фактическое listening по `../listening_request.json`: новые20 SFX, actual mixer WAV, synchronized video, stress/reset. P04 music unchanged/accepted не является автоматическим принятием новых SFX.
5. Раздельные read-only ART/GAMEPLAY/QA/Lead на текущем SHA/build hashes, затем controller privacy/CI/publication/conditional merge gates. Автор не пишет decision/scorecard и не запускает reviewers.

Все output folders fresh; tools отказываются затирать существующий evidence. Не брать ранние export/native/headless artifacts за текущий exact-SHA rendered proof. Final sandbox artifacts — regression-final-04, technical-final-04, exports-final-04; native-sandbox-01 доказывает только display denial. Wine server bind denial сохранён один раз; следующая попытка имеет смысл на host с разрешёнными sockets. Native Windows NOT_TESTED остаётся явным ограничением даже при успешном Wine.

Open LOW P04-QA-MOVIE-FLAG исправлен в коде через Engine.get_write_movie_path(); actual true + MP4 proof ещё требуется и уже проверяется native tool в P04 regression. Headless всегда false и не считается закрытием finding.
