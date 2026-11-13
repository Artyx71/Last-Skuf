# Возобновление

Рабочая ветка phase/p03-dialogue-audio. Последний независимый PASS P02attempt2; текущий runtime a2c09cb, original assets d99c501. P03 план planning/P03_TASKS.md. Все утверждённые P01 PNG неизменны. Не перезаписывать старые P02 evidence/builds.

Довести текущие frozen-source проверки: tools/verify.py --references --output reports/phases/P03/regression; tools/verify_p03.py native/MovieMaker/16weaponphases/exports в reports/phases/P03 и build/P03. BuildQA /root/p03_build_qa, независимый Lead /root/lead_reviewer_p03. Root добавляет actualCI/PR/implementation/artifacts после проверок. Lead должен сам проверить файлы и написать решение. FAIL→fix→review; PASS→P04.

Единственный известный внешний gate — реальные loop/transition/death/SFX listening: audio input эмпирически не поддержан Root и Lead. Дождаться конкретного проверяемого пакета, затем спросить владельца одним вопросом с actualpreview/enginecapture links; не выдавать waveform/ffplay за прослушивание. Без результата P03 scoped BLOCKED, не PASS. Техническую работу внутри P03 продолжать.

Privatepush/PR разрешены без rawphotos. Не merge/release/publish/billing/sudo; Windows Wine обозначать отдельно от native Windows. CI runner single-job ephemeral user-local разрешён с обязательным удалением variable/runner/credentials; постоянного сервиса нет.
