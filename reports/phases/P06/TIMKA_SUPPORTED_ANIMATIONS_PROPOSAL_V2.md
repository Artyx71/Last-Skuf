# Тимка: уточнённый технический контракт исключения

PROPOSED_V2, НЕ ПРИМЕНЕНО. Решение владельца по исключению ещё не получено. V1 сохранён без изменения; данный документ отвечает только на HIGH/MEDIUM findings независимого `timka-scope-proposal-review-01`, не является фазовым PASS и не заменяет owner consent.

Предмет решения прежний: не производить/не включать неразрешённые Тимке sharp/firearm/normal-fire анимации. Сохраняются все оставшиеся требования, включая непринятый environmental контакт, две настоящие способности, source/runtime review и глобальные пять категорий P04G.

## Реальный арт и две контекстные способности

Базовый бюджет остаётся84 реальных runtime клетки: WORLD32, ACTION28, FINISHER24. Это не96 и не обещание новых уникальных рисунков за счёт ссылок. При необходимости дополнительных настоящих рисунков их число фиксируется отдельно; ими не заменяется никакой обязательный gate.

| Контекст | Необходимое представление | Обязательные условия |
|---|---|---|
| peaceful_present | WORLD + ACTION без fire; собственный disengage: guard из ACTION0 → четыре собственные WORLD walk-фазы в обратном временном порядке → ACTION2 recovery | Честное повторное использование существующих целых рисунков; это не новые уникальные клетки и не prime special. Нужны настоящее ограниченное движение назад через collision, clock/cooldown/cancel/authority, без урона/неуязвимости/добиваний; ART/GAMEPLAY должны принять реальные переходы. |
| athletic_prime | WORLD + ACTION + три FINISHER category contacts и отдельный primeclinch | Собственные unarmed/blunt/environmental, действительная target/context eligibility и настоящий clinch через Core; никаких sharp/firearm. Непринятый UP environment остаётся FAIL и после переиндексации. |

Для disengage выше предложена проверяемая хореография на существующих рисунках, а не автоматическая художественная приёмка. Если реальные переходы/обратный шаг не читаются, необходим отдельный собственный лист; не подменять его prime-клинчем, пустыми кадрами или внезапным движением без соответствующего рисунка. Точные тайминги/скорость устанавливаются при реализации и проверяются на реальном Input. Фазовая P06 требует готовности обоих контекстов независимо от возможности раньше осмотреть полностью готовый present-контекст.

## Строго разрешённые раскладки

Только Timka получает отдельный allowlisted профиль. Никакой свободной карты анимаций из save/внешнего словаря. Unknown actor/kind/profile/schema/context/cell запрещены. Все другие герои сохраняют строгий существующий schema1 8×4 и утверждённые Source gates.

| Лист Тимки | Native PNG | Фактические целые клетки/ряд | Карты кадров |
|---|---|---|---|
| WORLD | 384×256 | 8, прежние0–7 | idle0,1; walk2,3,4,5; run6,7 |
| ACTION | 336×256 | 7, прежние0–6 | shove0,1,2; interact3; hit4; fall5,6; fire отсутствует |
| FINISHER | 288×256 | 6, из прежних0,1,2,5,6,7 | prep0; unarmed[0,1,4]; blunt[0,2,4]; environmental[0,3,4]; special/clinch[0,5,4] |

Размер отдельной клетки48×64, pivot24,58, четыре прежних направления. Не вставлять пустые reserved-колонки и не добавлять неподдерживаемые clips. Обычные action/finish clocks и Core receipts не меняются из-за раскладки. Производные disengage-ссылки в WORLD/ACTION считаются отдельно от84 исходных клеток.

Метаданные нового профиля обязаны отдельно фиксировать actor/kind/profile/schema, точный размер PNG, source→native mapping, количество/координаты реальных клеток, PNG SHA и RGBA SHA каждой клетки. Предлагается schema2 только для allowlisted Timka layout; при неправильной версии/ширине/карте/персонаже проверка отвергает набор, не подставляет legacy8×4 или Yakuza. Существующий TimkaWORLD PNG может остаться byte-exact, но его metadata migration всё равно проходит проверку.

Adopter schema2 принимает только свежий независимый source review всех обязательных24/28/32 клеток конкретного профиля: строгий список индексов/карт и SHA source/native/review/artifacts, must_fix[], runtime/fullphasefalse. Не использовать ложный all32_fresh=true для компактных24/28. Все discarded/raw/FAIL masters остаются в source archive. Компактные изображения собираются целыми клетками; не анатомическим Python монтажом.

Garment sockets мигрируются с новым sheetSHA и реальным количеством32/28/24, строго поindex и source mapping, с bounds и целочисленными точками на своей одежде. Старые96 записей и старый sheetSHA не подходят84 новым клеткам. Нужны независимые static-overlay и реальные gameplay overlay доказательства; наличие JSON их не заменяет.

## Фабрика до изменения действующей сцены

Вместо actor-only readiness кандидат заранее подготавливается для зарегистрированного scene key из `sandbox_scenes.json`: доверенные actor/context, allowlisted layout, все необходимые этому контексту реальные clips/sockets и реализованный ability handler. Никакого `open` из сохранённого context-словаря.

До Core.reset/scene_policy.invalidate/removal текущего actor: проверить весь требуемый контекстный набор и готовность механики. При отказе старые actor/authority/epoch/projectiles/receipts/story сохраняются. После успешной подготовки: reset → invalidate → open того же registered key → bind с повторной сверкой подготовленных actor/context/ability; несоответствие fail-closed. Один свежий scene-instance/generation авторизует только свои новые действия. Наличие арта не выдаёт ещё не реализованную способность.

Present обязан отвергать finisher API/пули/prime special до попытки обращения к отсутствующему clip. Prime — sharp/firearm/fire. Все context/unsupported-clip negative cases проверяются, включая forged saved context, смену policy/fixture во время действия, cancel/hurt/death/reset и повторные callbacks.

## Приёмка

Обязательны проверка компактных schemas/неверных размеров/карт/SHA/socketcount, per-context atomic readiness, корректный once-clock/damage/reward, настройки без влияния на механику, отсутствие регрессий Gabar/Oleg/Yakuza/CH01, фактические Input/native captures обоих контекстов, ART/GAMEPLAY/QA/Lead на frozen source, Linux/Wine exports и текущий обязательный GitHub CI/branch protections. Только полный P06 PASS открывает guarded squash. Owner approval исключения не даёт ни одного из этих PASS.
