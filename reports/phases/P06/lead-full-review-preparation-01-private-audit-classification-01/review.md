# Классификация privacy initial guard failure

Решение: **FORWARD_HYGIENE_REQUIRED_NONPRODUCTION_DEBUG_KEYS**. Это не full P06/privacy PASS. Первая serial privacy job b4283cfd80c2442db3d2577d46b98374 завершилась exit1 до raw11/object scan; отсутствие фото в shared Git этой попыткой не доказано. Исходный request f54cfabc и attempt01 не меняются.

## Реально осмотрено

В ROOT и WORK index находятся одни и те же4 объекта reports/phases/P04G/attempt1/{regression-final-02,regression-final-03,regression-final-04,regression-sandbox-01}/isolated_saves/data/godot/keystores/debug.keystore. Точные paths/OIDs/SHA получены read-only Git ls-files и локальным SHA; размеры2714B каждый. Эти файлы лежат вне Game/export content.

По каждому фактически выполнен только keytool -list -v. У каждого PKCS12/SUN, одна запись PrivateKeyEntry, alias androiddebugkey, self-signed subject/issuer CN=Godot, OU=Godot Engine, O=Stichting Godot, C=NL; создание13ноября2026 совпадает с отдельными P04G isolated runs. Известный стандартный debug store password принят. Это **настоящие приватные debug signing keys**, а не просто безобидные метаданные. Приватные key bytes не экспортировались, не печатались и не копировались в report.

Реальный tools/verify.py задаёт отдельные XDG_CONFIG_HOME/XDG_DATA_HOME в isolated_saves. game/export_presets.cfg содержит только Linux и Windows Desktop. Read-only поиск game/tools/autopilot/docs/specs/automation не нашёл production references к keystore/androiddebugkey. Короткая история exact-path относит файлы к P04G evidence commits; это не чтение всех Git blobs. Контекст и certificate metadata подтверждают nonproduction generated debug artifacts. Они не являются photo inputs, и факта утечки фото этот finding не устанавливает. Нельзя из этого вывести отсутствие любых иных production credentials.

## Минимальная дальнейшая гигиена

Автору: сохранить local4files и исторические reports/FAIL/PASS, убрать только эти4пути из текущего ROOT/WORK index, добавить *.keystore ignore в обоих деревьях. Сохранить чужие staged/dirty изменения; не делать add/commit всех ROOT файлов и не менять старые manifests/verdicts. В WORK это должен быть маленький forward hygiene change с явным erratum/index evidence. Не переписывать историю/force push. Старые blobs остаются воспроизводимой историей debug-only keys; их нельзя использовать/объявлять production signing credentials или выдать за удалённые из reachable history. Новое production signing всегда требует других ключей, если такая платформа вообще появится.

Рекомендация не требует нового owner-вопроса: это удаление неиспользуемых generated signing material из будущей публикации; новые права/стоимость не запрашиваются. Reviewer сам Game/Git/index/ignore/state не менял.

## Новый serial request v2

request-v2/run_after_native_v2.py SHA **6d879a5f12da9435946980c92b5ee86fc48413fefac9c1e010cd98b817fdd89b**. Fresh output final-private11-audit-02. Добавлены явные keystore ignore probes; при ранней AssertionError сохраняется validation.json passed=false со всеми guard checks и отдельные private failure details. Helpers/manifest pins и raw11 identity scope прежние; raw photos не копируются. Старый f54 не исправлен задним числом.

Сам actual audit v2 пока **не выполнен**. Выполнена отдельная чисто синтетическая AST-execution проверка initial failure: mocked ROOT/WORK index содержат TEST_ONLY keystore, guard правильно падает, оба отказа сохранены, validation passed=false, private metadata существует, commands=[], никакой subprocess/Git/engine/helper/raw scan не запускался. Временные TEST_ONLY fixture inputs удалены после сохранения sanitised output; это не реальные private files. См. guard-persistence-synthetic-proof.json и synthetic-initial-guard-output/.

После реальной forward hygiene автор запускает request-v2 через единственный ROOT stage, с released author/no Git writers и новым output. Нужны действительный canonical receipt и результат, не этот proposal. Результат ограничен exact11 rawSHA/path probes/sharedreachable/index identity; transforms/crops/reencodes/unlisted retired inputs/PCK/произвольные secrets/коммерческие права им не доказываются.
