# H04: калибровка измерений

1. Подготовить наблюдатель в существующем native test host. Сохранить исходные physics/post-draw timestamps, software Input requests, контакты Core, реальные смерти/рестарты и размеченные паузы. Игровую механику не менять.
2. Выполнить отдельный baseline на восьми контекстах. Это калибровка, не приёмка производительности. Представить исходные ряды и численные предложения независимым QA/Lead.
3. Зафиксировать контракт, его SHA и независимое решение ДО acceptance run. Изменённый код/контракт или отсутствующее решение запрещают acceptance. Исходный death→control <1000ms не ослаблять. Calibration ограничена абсолютными потолками: accepted p95 ≤50ms, rendered-change p95 ≤83.334ms, frame p95 ≤25ms / p99 ≤33.334ms. Внутри потолков предложение строится по baseline; независимый Lead оценивает уместность, не автоматическое авторское PASS.
4. Выполнить новый native acceptance с теми же hardware/backend/settings, сохранить raw и пересчитываемые метрики. Записать короткий camera/movement фрагмент настоящей CH01. Отдельный Gameplay/Lead review определяет достаточность непрерывной читаемости; метрики не заменяют оценку ощущений.

Accepted означает наблюдение после игрового actor physics callback; rendered change — первый frame_post_draw с изменившейся позой/положением sprite. Это верхние программные оценки, не OS-key/hardware/photon latency. Намеренный windup/contact измеряется отдельно. См. официальные Node.process_physics_priority и RenderingServer.frame_post_draw:
https://docs.godotengine.org/en/stable/classes/class_node.html#class-node-property-process-physics-priority
https://docs.godotengine.org/en/stable/classes/class_renderingserver.html#class-renderingserver-signal-frame-post-draw

Frame-time ряд берётся по monotonic post_draw. Readback видео и явно размеченные setup/idle/death-wait участки не входят в performance budget; все исходные данные остаются доступны, исключения зафиксированы в контракте. Движение и прогресс считаются по реальным physics positions; staged AI death проверяет настоящий контакт, не прямой вызов receive_hit.

Это компонент readiness pipeline, не измерение длительности ещё не созданных глав, не новый сюжетный уровень и не FULL Readiness/P07 PASS. Старые принятые H02/аудио/MDS решения сохраняются.
