extends RefCounted
## Give the asynchronous mixer real time to drain, including accelerated/headless QA.
static func quit_clean(tree: SceneTree, exit_code := 0) -> void:
 if tree.has_meta("runtime_shutdown_pending"): return
 tree.set_meta("runtime_shutdown_pending", true)
 var audio := tree.root.get_node_or_null("AudioDirector")
 tree.paused = true
 # SceneTreeTimer follows simulation time. Fixed-FPS/movie/headless test runs can
 # consume a 200ms timer before the audio thread has mixed even one real block.
 # Keep processing frames for deferred main-thread releases while waiting on the
 # monotonic wall clock; never busy-block the main thread or stop the audio driver.
 var ready_at := Time.get_ticks_usec() + 50000
 while Time.get_ticks_usec() < ready_at: await tree.process_frame
 if is_instance_valid(audio): audio.shutdown()
 var drained_at := Time.get_ticks_usec() + 250000
 while Time.get_ticks_usec() < drained_at: await tree.process_frame
 tree.quit(exit_code)
