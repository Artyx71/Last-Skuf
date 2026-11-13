extends RefCounted
## Drain the asynchronous mixer before freeing OGG playback references on native or Dummy drivers.
static func quit_clean(tree: SceneTree, exit_code := 0) -> void:
 var audio := tree.root.get_node_or_null("AudioDirector")
 tree.paused = true
 # An immediate test can finish before the first audio mix. Give queued playback
 # startup one mixer block, then stop and drain before releasing engine resources.
 # Timers also let callers return and release local Image references before quit.
 if audio:
  tree.create_timer(0.05, true).timeout.connect(audio.shutdown, CONNECT_ONE_SHOT)
 tree.create_timer(0.20, true).timeout.connect(tree.quit.bind(exit_code), CONNECT_ONE_SHOT)
