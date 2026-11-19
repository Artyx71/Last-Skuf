# Bonus namespace/session pilot01 — independent Lead code/actual-evidence review

**FAIL_COMPONENT** for frozen6ae6128bcb18eef8c916e8ded766f8ecbd82104f. The normal05pilot has genuine positive evidence, but the independently authored namespace witness proves a HIGH main-save preservation defect. This decision concerns the original frozen source; later fixes are not accepted by this verdict.

## Must fix: BONUS-PILOT-L01 HIGH / H05-QA01-NAMESPACE_ALIAS

`_sync_scope` derives sidecar=`campaign_parent/bonus_progress_v1.json`; `_write` opens sidecar+`.tmp` for WRITE and then renames it to sidecar. Neither path is reserved against the canonical main campaign filename. The normal path equality in can_launch checks the sidecar location, not collision with main.

QA authored the exact disposable probe; the sole ROOT executor ran it as actual operationad9dcb1c65bd4ba589b75eb2a6f6b9ea, exit0 in0.903s. I read the exact source/clone/result and checked its receipt/log hash. Two valid campaign files were corrupted in disposable directories:

- **main_is_sidecar_tmp:** the trusted main override itself ends in bonus_progress_v1.json.tmp. Begin/complete both returntrue. Opening the bonus temporary truncates that valid main; successful rename removes its canonical path. The final main does not exist and is invalid.
- **main_created_after_candidate_at_sidecar:** initialize candidate while its computed sidecar/main path is absent, then create the legitimate main at bonus_progress_v1.json. Begin/complete returntrue; the bonus rename replaces that schema2campaign with schema1bonus data. Main bytes/schema are not preserved.

The witness's exit0 means the reproduction ran, not BP acceptance. Actual ordinary user profiles were not touched. Even though the override is trusted and unusual, the profile contract permits custom main paths and promises preservation. This is a demonstrated IO defect, not just missing future UI work.

**Minimal remedy:** reject normalized canonical main equal to sidecar final OR sidecar temporary before sidecar load/begin/write, revoke any colliding binding, and add both original cases plus normalized-path controls. Keep ordinary profiles and once/crash behavior unchanged; do not restrict every main save to one fixed filename or build a new storage framework. Retain old source/witness and verify a separate fixed candidate.

## Genuine normal evidence retained

I read all four new tool/fixture files and connected actual StoryState/Service/journal/Bootstrap sources. Actual normal05operation176056fd4aae4609a3585de4d13092df exited0 in52.444s. Its10stages completed:85mainchecks,1prepare,3recover-before,3recover-after; the two expected child SIGKILLs returned−9 at exact pre/post-rename markers with no result falsely claimed. Fresh-process recovery validates the respective one/two committed facts. Existing actual story_state40, scenario graph6344logicalpaths/662778assertions and story_integration11pass; graph coverage is not6344playable levels or production CH10/14 availability.

All620before/after source keys were compared and rehashed before the later fix. The producer and witness cloned progress/contract/host scripts match my immutable6ae snapshots. I verified both actual receipts and logs, all10normal-stage log digests and typed raw check counts, then rehashed QA01's102portable entries and read its findings. The actual roundtrip rebuilds typed state after JSON floats; old read_error0 and original failures remain preserved, not explained away as EOF. The strict JSON cases and reentrant/queued/freed-host checks remain useful positives. No duplicate renderer/engine/test execution was performed by Lead.

## Precise unaccepted live-adapter boundary

The positive EligibilityDouble overrides future chapter prerequisite and host scene path; Owner/Host are test Nodes. Real canonical StoryState validation and Godot file IO are used, but no legitimately admitted CH10/14 or real bonus scene is played. The base candidate keeps production planned/unknown entries locked even with completed sidecar.

- **BP07:** direct base can_launch/begin denial is checked. Actual StoryJournal bonus rows, mouse/Enter handling, UI-to-StoryService launch boundary and trusted real scene/character grant are not implemented/tested here.
- **BP06/BP09 owner lifecycle:** explicit `revoke()` demonstrates the primitive, not a real NewGame/profile-generation event hook. Same-object NewGame and unobserved A→B→A owner transitions still require the live owner adapter. Old6ae temporary replay/readonly/prerequisite denials do not permanently revoke the token; observed denial→restore→old callback controls should be made fail closed in the fixed candidate, while an entirely unobserved transition still needs the real owner hook.
- **BP09 return:** request_return/consume_return is called directly against an already-created Bootstrap. It does not test an actual scene-return transition, bonus journal restoration or a return intent consumed before Bootstrap._ready dev CLI autoroute. The fixed return owner/predicate is not proof that this adapter is installed.

Thus even a fixed core namespace/session prototype is not allBP01–09closure or the complete H05 capability. Separate isolated live owner/journal/return adapter evidence is required before FULL Readiness/integration. Actual first-completion positive campaign unlock remains unavailable until legitimate CH10/14 admission; test doubles cannot change that. BP10full original bonus levels, real gameplay goals/routes/FullReduced/newART/music/listening/exports remain HIGH future content acceptance, not a demand to build both missions just to test the namespace.

## Continuation

Fix only the namespace guard and bounded session-denial controls, rerun the affected pilot/actual alias negative controls through the sole executor, and obtain separate QA/Lead review. Preserve all old PASS/FAIL raw evidence. After core acceptance, proceed to the isolated live-adapter pilot without production ROOT installation or phase admission. No broad H02/H04/combat rerun is requested. No engine/Controller/Git/WORK/state mutation, process signal, network, photo or generator action was performed by this reviewer. Frozen main24/main21MDS, P06 and prior component scopes are unchanged; Readiness/P07/merge remain unapproved.
