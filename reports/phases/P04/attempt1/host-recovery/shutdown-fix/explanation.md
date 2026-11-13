# REC-QA-01 fix candidate

Normal source headless replay reproduced two synchronized-stream leaks despite successful gameplay. Accelerated full replay before fix reproduced40Objects/14resources; after fix clean. Kept original logs, no warning suppression. RuntimeShutdown now waits for monotonic real microseconds while processing frames; simulation timers can expire before an asynchronous mixer drains under fixed-FPS/accelerated execution. A dedicated repeat of the complete normal and accelerated flows is part of verify.py. User-visible combat timing/retry logic is untouched. Full final native rebuild and independent review still required.

Primary engine source inspected for asynchronous server/playback release semantics (no engine patches):
- https://github.com/godotengine/godot/blob/4.7.2-stable/servers/audio/audio_server.cpp
- https://github.com/godotengine/godot/blob/4.7.2-stable/scene/audio/audio_stream_player_internal.cpp
