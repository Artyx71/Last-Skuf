# Bootstrap A fixed9e5 — independent Lead: FAIL_COMPONENT

Frozen source9e5e7c303f1ea5f89024063a529ad70d7dc57fb6; ROOT remains uninstalled old02b. This separate review preserves original6c FAIL. The actual author runb4606f5751ff4029a5089e32edaa4d13 exit0 and argv/log hashes were verified; saved validation220/220 is genuine author evidence, not a new run by Lead.

The exact original five probes were repeated against the frozen helper. **All5 now pass.** The only adaptation is moving the two immutable-field mutations from journal.json to intent.json; all old expected outcomes/control assertions remain. Static protected-map/mode corruption now refuses; before_commit canonical-lock substitution refuses and retains marker; after_commit protected drift refuses and retains recovery evidence. BA-L02/03 are closed for these tested cases; the direct static BA-L01 cases are fixed. Generated legacy+guard runner remains exactlyd1c347… . No new engine/Game/bundle-B scope is requested.

## BA-L04 — HIGH: verified hash and parsed immutable intent are different reads

`load()` computes `sha(intent.read_bytes())`, checks journal binding, and then calls `readjson(intent)`, which reopens the path with read_text. Therefore it does not bind the bytes actually parsed to the prepared digest.

`probe_same_bytes.py` provides a deterministic **pure fake-root read-interleaving fault injection**, not a concurrently launched Controller. A wrapper around the real parser temporarily writes protected={} into the actual fixture intent file exactly when readjson opens it, calls the unchanged real parser, then restores the original bytes. Marker and journal are untouched. Unknown protected state is present. At all four load calls the hashed bytes have the prepared SHA, while the parser consumes a different file SHA and an empty protected map. `finish()` returns VERIFIED, removes the marker and returns protected=[]; original intent bytes are restored at the end. The unknown state is neither repaired nor rejected.

This is not a three-file rebinding threat or a claim that a hostile process exists in actual ROOT. It is the concrete read/parse boundary required by the previous remedy: hash and parse **the same immutable blob**. Actual facts are in same-bytes-results.json; the complete parser call still executes against real temporary filesystem bytes. No Controller/worker/engine/network/Git or real ROOT mutation occurs.

Minimum remedy: read immutable intent bytes once, compute digest and strict-decode that exact byte sequence. Carry the verified digest through commit rather than reopening the path to choose a possibly different digest. Keep original5 and this read-interleaving counterexample unchanged for the next candidate; source inspection must confirm that the duplicate-read window is removed. No extra native tests or larger installer framework are needed.

Installation/execution remains NOT_APPROVED pending a new frozen candidate and independent review, plus the separate actual plan/quiescence/protected-input/backup prerequisites. Full B, C02, GameSync, FULL Readiness and P07 remain separate and open. P06 PASS/MERGED and canonical progress were not modified. Completed files are immutable.
