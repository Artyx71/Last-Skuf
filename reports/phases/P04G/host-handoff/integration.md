# Host integration P04G attempt1

Author receipt827794abae4f469eb68195232b348063 completed exit0; no replay/reset. Nine local commits adopted from SHA256-verified bundle, exact434changed paths and336frozen source hashes matched, no raw-reference matches. Branch CAS3de67a00→9185bf15 and index alignment preserved every working file; transfer.json records evidence. Nested Git index remains capability-limited despite --add-dir; host adoption is explicit, not a claim that every future nested writer can commit.

Native probe defect reproduced on host: forced --quit-after3 returned0 but leaked2AudioStreamSynchronized references (old_forced_probe.log). Corrected to normal -- --smoke-bootstrap; clean OpenGL bootstrap exit verified (clean_probe.log). No gameplay source changed by this host correction.

Added detailed numerical QA of all20original PCM16/44.1k mono SFX: unity mono→stereo sample duplication preserves native peak/RMS; original PCM rails checked separately, including positive32767 below float1. DC, silence, endpoint steps, true peak and RMS/loudness recorded. Short-cue gated LUFS is informational. Existing P03/P04 music loop/transition checks remain mandatory. Fresh native QA will analyze five actual runtime mixes; analysis cannot accept artistic quality.

Gate requires a distinct P04G actual-listening proof; P04 score acceptance does not accept new effects. Real silent, positive-rail and discontinuous-WAV negative fixtures plus old-phase proof with zero merge requests and unity decode test pass; full Python73/73. Dry analysis23/23 PASS_SIGNAL_ONLY. No actual hearing claimed.

Still pending: host21-command regression, real Full/Reduced/Movie/Linux/Wine captures, exact binaries/video/frame performance, actual listening, independent ART/GAMEPLAY/QA/Lead, exact-SHA CI. No phase PASS or publication.
