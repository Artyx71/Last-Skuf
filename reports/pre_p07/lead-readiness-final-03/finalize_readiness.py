from pathlib import Path
import json,hashlib,shutil,datetime
O=Path(__file__).resolve().parent;R=O.parents[2];W=R/'.autopilot/worktrees/P07'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def copy(p,rel):
 q=O/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
# Final independent QA must actually exist and be immutable before this full judgement.
q=R/'reports/pre_p07/qa-readiness-aggregate-03';qd=load(q/'decision.json')
assert h(q/'decision.json')=='52578ecfb0b2211fab708ca5a425a80970d62c08b798df58957876beb73c1889'
assert qd['ready_for_independent_Lead'] is True and qd['must_fix']==[] and qd['FULL_Readiness_Lead_approval'] is False
manifest_counts={}
for folder,filename in [('qa-readiness-aggregate-03','artifacts.json'),('lead-canonical-source-C-installed-01','artifacts.json'),('lead-second-pilot-01','artifacts.json'),('audio-pipeline-readiness-audit-01','SHA256-manifest.json'),('lead-pacing-acceptance-01','artifacts.json'),('lead-bonus-escalation-adjudication-01','artifacts.json')]:
 base=R/'reports/pre_p07'/folder;m=load(base/filename)
 for row in m['files']:
  p=base/row['path'];assert p.is_file() and not p.is_symlink() and h(p)==row['sha256'],str(p)
  if 'bytes' in row:assert p.stat().st_size==row['bytes']
 manifest_counts[folder]=len(m['files'])
for f in ['decision.json','REVIEW.md','artifacts.json','source-and-gate-verification.json','eight-domain-assessment.json','reviewed-source-inventory.json']:
 copy(q/f,'independent-QA/'+f)
# The author index remains historically pending. Supersede its candidate H05 references explicitly.
cap_paths={
 'full_p06':['reports/phases/P06/decision.json','reports/phases/P06/lead-full-phase-review-01/review.md','reports/phases/P06/lead-full-phase-review-01/metrics.json','automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json'],
 'safe_handoff':['reports/pre_p07/lead-canonical-source-C-installed-01/handoff-capability-decision.json','reports/pre_p07/lead-canonical-source-C-installed-01/decision.json','reports/pre_p07/lead-canonical-source-C-installed-01/C02-technical-evidence-matrix.json','reports/pre_p07/lead-runtime-bundle-B-installed-01/decision.json','reports/pre_p07/qa-runtime-fence-02/decision.json','reports/pre_p07/lead-production-guard-03/decision.json'],
 'navigation_pilot':['reports/pre_p07/lead-second-pilot-01/decision.json','reports/pre_p07/lead-second-pilot-01/factual-proofs.json','reports/pre_p07/lead-second-pilot-01/remaining-scope.json','reports/pre_p07/lead-pacing-acceptance-01/decision.json','reports/pre_p07/gameplay-pacing-readability-01/correction-01/decision.json'],
 'audio_playback_pipeline':['reports/pre_p07/audio-pipeline-readiness-audit-01/decision.json','reports/pre_p07/audio-pipeline-readiness-audit-01/review.md','reports/pre_p07/audio-pipeline-readiness-audit-01/P06-current-byte-comparison.json','reports/pre_p07/audio-pipeline-readiness-audit-01/runtime-evidence-audit.json'],
 'pacing_instrumentation':['reports/pre_p07/lead-pacing-acceptance-01/decision.json','reports/pre_p07/lead-pacing-acceptance-01/own-assessment.json','reports/pre_p07/lead-pacing-calibration-02/decision.json','reports/pre_p07/qa-pacing-acceptance-01/actual-evidence/raw.json','reports/pre_p07/qa-pacing-acceptance-01/scope-erratum.json'],
 'secret_integration_contract':['reports/pre_p07/lead-bonus-escalation-adjudication-01/decision.json','reports/pre_p07/lead-bonus-escalation-adjudication-01/REVIEW.md','reports/pre_p07/lead-bonus-escalation-adjudication-01/BP-coverage.json','reports/pre_p07/lead-bonus-escalation-adjudication-01/own-material-audit.json','reports/pre_p07/lead-bonus-mds-02/decision.json','reports/pre_p07/qa-bonus-legacy-supplement-01/decision.json']}
assert h(R/cap_paths['secret_integration_contract'][0])=='076c4dc3fadd948ac54101d4b1c1e8ba7595e8c8d54eed2c5bd0cbc55e70080f'
owner=W/'reports/phases/P06/character-finisher-audio-01/owner-listening-acceptance.json';assert h(owner)=='3b6b3c69004668ea73a5cc1102263e80abf2d2757952876dfbd234a4526752d9'
copy(owner,'historical-evidence/owner-listening-P06.json')
cap_paths['audio_playback_pipeline'].append(str((O/'historical-evidence/owner-listening-P06.json').relative_to(R)))
# No current Game/guard source edits; freezes keep future WORK production outside this receipt's input graph.
source=load(O/'own-source-verification.json')
assert source['root_Game']==533 and source['canonical_tools_Git_blobs_verified']==54 and source['complete_delta_is_frozen9']
capabilities={k:{'status':'PASS','evidence':[{'path':p,'sha256':h(R/p)} for p in paths],'acceptance_scope':'Actual preproduction capability; future production acceptance remains separately mandatory.'} for k,paths in cap_paths.items()}
capabilities['navigation_pilot']['acceptance_scope']='Two representative layouts/production CH01 and later bounded H04 sampled movement/camera readback; no full-campaign or party/crowd/shape-universal claim.'
capabilities['secret_integration_contract']['acceptance_scope']='BP01–09 preproduction contract, actual core/live adapters/manual finite supplement; explicit eligibility double and CLI seed, production scene paths empty; BP10 future HIGH.'
capabilities['audio_playback_pipeline']['acceptance_scope']='Existing prototype original audio, actual mixer/loop/retry and original owner listening; no new chapter audio, dedicated reload acoustic continuity or new listening.'
capabilities['pacing_instrumentation']['acceptance_scope']='Previously calibrated df7 fresh native software timings and sampled105-frame CH01 route, not fresh a0ab measurements or whole-campaign feel/FPS/duration.'
future={
 'chapter_delivery_21':{'severity':'HIGH','status':'OPEN','enforce_at':'P07_LEAD_PASS_AND_MERGE','requirement':'Implement and independently accept all21 authored chapters from the exact approved MDS: distinct geometry/encounters and justified mechanics; trusted scene/hero/context grants, physical doors/props/party/clearance/LOS and AI priorities; once/death/cancel/retry/checkpoint/old-save/POV/skip; real original ART/animation/contact/text/HUD/settings, real native inputs and affected platform builds/performance. Main MDS and fixtures are design/capability evidence, never completed levels. The owner-deferred additional C09 NPC visual polish remains P08; baseline NPC reaction correctness is not deferred. Require relevant Narrative/ART/Gameplay/QA/Lead acceptance as content is made.','source_findings':['READINESS-C01','READINESS-H01','READINESS-H02','READINESS-M01']},
 'campaign_pacing_actual':{'severity':'HIGH','status':'OPEN','enforce_at':'P07_LEAD_PASS_AND_MERGE','requirement':'After content exists, measure actual first-play primary campaign and per-chapter/routes/story/traversal/death-retry/skip/AFK distributions against420–540min, without summing mutually exclusive endings or optional all-secret runs and without padding. Preserve software input/contact/windup/restart separation and native monotonic frame/raw/calibrated thresholds; evaluate load-specific effects/camera/telegraph/encounter readability and death causes. H04 small controlled windows and P06 API stress are not campaign duration/FPS/hardware latency guarantees.','source_findings':['READINESS-H04','H02-NEXT-READABILITY','P07-ACTUAL-PACING']},
 'new_audio_acceptance':{'severity':'HIGH','status':'OPEN','enforce_at':'P07_LEAD_PASS_AND_MERGE','requirement':'For every new chapter score/stem/cue/mix provide real original files/provenance, decode/signal/loop/loudness/headroom/clipping, actual Godot playback/typed contact/mixer/beat-bar/duck/retry/scene-reload acoustic continuity and deliberately staged inter-score transitions, followed by a real listener for that new material and affected export/platform evidence. Existing P06 owner prototype listening does not accept future material; select_music stop/play fade-in is not seamless crossfade.','source_findings':['READINESS-H03']},
 'secret_delivery_7':{'severity':'HIGH','status':'OPEN','enforce_at':'P07_LEAD_PASS_AND_MERGE','requirement':'Deliver five canonical secret episodes and two distinct optional noncanonical bonus levels with actual scenes/assets/legitimate hero authority/objective hosts/geometry/pacing/checkpoints/live UI/return-before-CLI/default-false/profile/generation/once/replay/old-save/crash compatibility and actual ART/audio/native playthrough/platform role acceptance. Prove real positive CH10/14 eligibility only after trusted chapter production admission, without fixture doubles. Preserve main21 history/rewards/relationships and existing five REAL_PRIME predicates/WIFE_CALLING; BP10 remains unbuilt until that actual evidence exists.','source_findings':['READINESS-H05','NS01-INTEGRATION','BP10']}}
write(O/'future-HIGH-obligations.json',{'schema':1,'future_acceptance_obligations':future,'author_may_close_or_downgrade':False,'enforcement':'Independent exact-head P07 content acceptance and both fresh guarded merge snapshots via installed readiness/github; per-content independent reviews remain mandatory.'})
write(O/'capability-evidence-matrix.json',{'schema':1,'preproduction_capabilities':capabilities,'actual_QA_final_sha256':h(q/'decision.json'),'underlying_manifest_entries_rehashed':manifest_counts,'draft_H05_pending_is_historical':True,'actual_H05_manual_receipt_substituted':True})
review='''# FULL Production Readiness — independent Lead

**PASS — FULL preproduction readiness.** The six required capabilities are supported and no current Critical/High must-fix remains. This is a new independent judgement; the original readiness FAIL and all historical component failures remain unchanged. It is permission for the existing Controller to admit sequential P07 production after its ordinary checks, not a P07 phase PASS or acceptance of unbuilt content.

## Actual inputs and independence

I read the project Lead/review/gate protocol, original READINESS-C01/C02/H01–05, the actual installed readiness/runner/github flow, tests, existing phase/component proofs and the submission. The author table and INPUTS.DRAFT are pointers, not verdicts. In particular, their historical pending-H05 text is superseded only by actual manual receipt076c4dc3…; it does not become self-approval.

My read-only audit inventories all533 canonical ROOT Game files with no extras/missing files/symlinks and recomputes both SHA256 and Git-blob SHA1 against the independently validated frozen f832 catalog. All54 canonical tools likewise match that source. Installed guard code, modes and owners match the accepted runtime baseline; its strict readiness schema, six-capability/four-obligation contract, all21-MDS/source checks and phase/merge closure calls were read directly. ROOT Git HEAD is deliberately still be4d59… while physically installed Game/tools are f832: no reset or ref/index rewrite is implied.

WORK has536 Game files: exactly three additions/six changes, all nine equal the immutable submitted copies;527 existing files are unchanged. The reviewed runtime is a0ab23a9838d9308ee9acc38d3ef2cdc91cedfc4, later archives are not new execution. New navigation/bonus source is accepted as tested WORK capability and is not installed into ROOT by this decision. All43 inputs of the full21-MDS receipt rehash correctly; its21 IDs/paths/hashes are distinct and match the canonical registry. I also rechecked233 existing audio/source files against their saved f832 blob/SHA identities and read109 WAV headers, without listening.

The actual independent QA aggregate52578ecf… was awaited, read with its eight-domain assessment, and its30 manifest entries rehashed. It supports the evidence with no must-fix but explicitly leaves FULL Lead admission to this decision. My own full-tree/blob/source/guard/manifest observations are separate from its Git queries. No new engine, Controller, Git, network, actual state/source mutation or listening was performed by this reviewer. Existing risky paths already have actual independent tests; unchanged measurements are reused under exact source bindings instead of gratuitous reruns.

## Eight domains

`eight-domain-assessment.json` gives implemented behaviour, actual tests/proofs and each remaining boundary. Combat/player animation/HUD and baseline three-NPC category feedback are the full accepted P06 prototype, not only component votes. P06 has independent ART/Gameplay/QA/Lead, mandatory CI and confirmed PR11 squash f832. Own art/socket/contact/settings evidence remains source-exact. The owner's58abd098 scope amendment defers only additional hero-linked NPC visual polish/routing/new-clip reviews to P08; no baseline correctness or player mechanism/audio/HUD was waived. New chapter/boss/AKIMBO69 animated QTE assets remain uncreated.

Navigation now has real obstacle/door/alternate-route/LOS/reset/clearance evidence across two representative layouts and production CH01. The actual cache-loop witness was corrected;121headless/102native plus navigation70 and CH01 room18/mission28/native58 are accepted within their scopes. Seven own-F test contexts represent six heroes with Timka twice; Yakuza receives no F ability. The second-pilot receipt left continuous readback/H04 open. Later accepted H04 supplies actual sampled CH01 movement/turn/camera evidence, closing that *representative preproduction* gap. It does not approve all-room combat readability, arbitrary shapes, peer avoidance or automatic party followers. Those remain affected-mission gates.

Dialogue/story direction has actual P05/P06 ledger/skip/cast/replay and CH01 native compatibility plus21 fully reviewed paper MDS. Twenty future main chapters are designs, not delivered missions. The canonical four story/registry files and schema2/five-secret ending predicates remain unchanged. H05 manual076c accepts the actual BP01–09 namespace/IO/atomic rename/crash/profile/once/live-owner/journal/Bootstrap/CLI compatibility: core101 and actual two SIGKILL/fresh recovery, retained stages21/4/38/5 and the finite41+nested49 with10 actual deaths/retries. Positive CH10/14 eligibility/scene remains an explicit double, CLI return precondition is seeded and production bonus scene paths remain empty. BP10 is future HIGH. The broad three-cycle loop stays STOPPED; only one authorised finite supplement was used, with no fourth broad PASS or budget reset.

Existing audio has two real four-stem scores/66SFX, actual single-player mixer loops/beat-bar commits/duck/retry, typed FIN cues, technical signal closure and bounded original owner prototype listening. New chapter themes and dedicated scene-reload acoustic continuity are not accepted by reuse. `select_music` stops/starts with fade-in and is not a seamless inter-score crossfade. No agent hearing is claimed. UI/settings/VHS and mandatory HUD have actual Full/Reduced/off and native evidence; the new journal has real Down/Enter and viewport-local mouse/backend denial/once-return evidence. These are640×360 software-event texture observations, not physical device/window/DPI coverage.

Performance/effects has P06 bounded pool/TTL/reset stress and the later calibrated H04 raw instrumentation. Contract4eb9… was approved by9966… *before* the fresh acceptance. The five comparisons17.914/18.876/17.093/17.567/16.722ms pass34/60/24/33/1000, with48 requests, eight outgoing/eight lethal Core contacts and958 controlled draw intervals separate from239 idle intervals. The measurements remain df7/hardware-profile measurements, not fresh a0ab runs. The actual105-frame CH01 clip is sampled, not a full combat playthrough; NPC motion is present because resume re-enables physics, as the independent erratum states. First changed pose at post-draw is not first pixel/photon. P06 stored600-frame stress summaries lack raw interval arrays and are not independently recomputed or promoted into a campaign guarantee.

## Original findings and staged obligations

`original-findings-closure.json` resolves current preproduction parts of C01/C02/H01–05 with actual evidence. It does not erase their future-content requirements. C02's technical A/B/C handoff is complete; the current final records/stop gate are deliberately not bypassed. H01's21 design prerequisite is complete independently; H02/H04 pilot and instrumentation are now sufficient before mass affected production. H03 existing playback and H05 actual integration contract have passed, while unmade content remains open.

The four explicit future obligations remain severity HIGH, status OPEN and enforce_at=P07_LEAD_PASS_AND_MERGE: `chapter_delivery_21`, `campaign_pacing_actual`, `new_audio_acceptance`, `secret_delivery_7`. Their exact substantive requirements and original finding traces are in the decision and separate JSON. In particular,420–540min first-play duration, load/feel of real encounters, new audio/real listening and seven actual secret episodes are NOT_MEASURED/NOT_DELIVERED. No padding, sum of exclusive endings or invented actual unlock is allowed. Medium/Low optional styling/P08 debt remains open and unimplemented; mandatory scene/HUD/functionality cannot hide there.

The installed guard requires a full independent exact-source readiness record plus the separate full21-MDS record and P06 PASS/MERGED; whole canonical Game is also checked against Git at entry. It rejects missing/component/concept/FAIL/BLOCKED/stale/unresolved Critical/High or untracked source. A future P07 PASS must close exactly these four obligations with hash-bound real evidence against current P07 head and canonical readiness SHA. `github.validate_review` and both fresh merge snapshots perform that check while keeping mandatory CI/current head/base/protection/manual-approval/server-SHA confirmation rules. No external GitHub policy or CI for a future P07 commit is approved here.

## Controlled continuation

`ready_for_p07=true` means the Readiness prerequisite is satisfied by this exact receipt. The executor must validate it with installed `require_p07_production`, exact canonical main21 receipt and current source; end the old preproduction lease/process; register the genuine receipt under normal exclusive ownership; make only the authorised cold stopP06→P07 policy update preserving every other key; then start a fresh Controller and repeat prerequisites before one sequential author proceeds in the existing WORK. Config fingerprint changes must not be used through an old loaded controller. No A/B/C reapply, Root Game replacement, parallel executor or reset is authorised.

The final source inventory contains all533 canonical Game files, canonical tools/current guard code and immutable review/runtime snapshots. It deliberately excludes mutable authority, active configuration and future WORK source to avoid checkpoint/policy changes invalidating the receipt or creating a self-SHA cycle; their relevant observed state/policy is snapshotted only. This does not remove the Controller's current live checks. It grants no P07 phase PASS/merge/release, new ROOT installation, real bonus/chapter acceptance, native Windows, physical latency, full-campaign performance/duration or new listening approval.
'''
(O/'REVIEW.md').write_text(review)
# Inventory the whole canonical production source, selected installed code, and immutable evidence.
inv=load(O/'root-game-inventory.json')
catalog=load(R/'reports/pre_p07/canonical-source-actual-C-01/plan.json')
for rel,row in catalog['target_catalog'].items():
 if rel.startswith('tools/'):inv[rel]=h(R/rel)
for rel in source['guard_code_sha256']:inv[rel]=h(R/rel)
mds_path='reports/pre_p07/lead-mds-global21-01/decision.json';mds=load(R/mds_path)
inv[mds_path]=h(R/mds_path)
for rel,sha in mds['source_inventory_sha256'].items():assert h(R/rel)==sha;inv[rel]=sha
for paths in cap_paths.values():
 for rel in paths:inv[rel]=h(R/rel)
for rel in ['reports/pre_p07/qa-readiness-aggregate-03/decision.json','reports/pre_p07/qa-readiness-aggregate-03/artifacts.json','reports/pre_p07/lead-readiness-01/decision.json','reports/pre_p07/canonical-source-actual-C-01/plan.json','reports/pre_p07/lead-production-guard-03/input-inventory.json','reports/pre_p07/qa-production-guard-04/decision.json','reports/pre_p07/lead-canonical-source-C-installed-01/post-C-runtime-baseline.json']:
 inv[rel]=h(R/rel)
# Snapshot static policy rather than pinning mutable active config.
copy(R/'autopilot/config.json','policy-snapshot/config-at-review.json')
for p in O.rglob('*'):
 if p.is_file() and p.name not in ['decision.json','artifacts.json','FINAL_HASHES.json','reviewed-source-inventory.json']:
  inv[str(p.relative_to(R))]=h(p)
# Add copied QA decisions too (excluded by basename filter above only to avoid own self-reference).
inv[str((O/'independent-QA/decision.json').relative_to(R))]=h(O/'independent-QA/decision.json')
write(O/'reviewed-source-inventory.json',{'schema':1,'source_inventory_sha256':dict(sorted(inv.items())),'whole_ROOT_Game_files':533,'future_WORK_source_and_live_state_config_pinned':False})
closures=load(O/'original-findings-closure.json')
findings=closures['findings']+closures['optional_debt']
decision={'schema':1,'status':'PASS','scope':'PRE_P07_PRODUCTION_READINESS','acceptance_level':'FULL','role':'LEAD_REVIEWER','reviewer':'/root/art_olezhka_recovery','independent_of_author':True,'reviewed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'p06_base_head':'f8325212381d67a469b5d9a6dffbf3d244bc9933','ready_for_p07':True,'must_fix':[],'findings':findings,'preproduction_capabilities':capabilities,'future_acceptance_obligations':future,'source_inventory_sha256':dict(sorted(inv.items())),'main21_MDS_gate':{'path':mds_path,'sha256':h(R/mds_path)},'independent_QA_final':{'path':'reports/pre_p07/qa-readiness-aggregate-03/decision.json','sha256':h(q/'decision.json')},'domains_reviewed':8,'whole_canonical_ROOT_Game_files_verified':533,'WORK_Game_files':536,'WORK_frozen_changed_or_added_Game_files':9,'WORK_runtime_source_head':'a0ab23a9838d9308ee9acc38d3ef2cdc91cedfc4','older_FAILURES_immutable':True,'H05_original_broad_loop_status':'STOPPED','H05_broad_budget_reset':False,'H05_finite_supplements_used':1,'H05_finite_supplements_maximum':1,'new_Engine_Controller_Git_network_or_listening_calls_by_reviewer':0,'actual_p07_execution_started':False,'phase_approval':False,'merge_approval':False,'release_approval':False,'new_ROOT_runtime_or_Game_installation_approval':False,'actual_new_chapter_or_bonus_level_approval':False,'actual_campaign_420_540min_measured':False,'native_Windows_accepted':False,'hardware_latency_accepted':False,'next_action':'Validate this exact FULL Readiness and separate canonical21MDS via installed guard; terminate old preproduction lease/process, register genuine receipt, cold authorised stop-only P06→P07 policy update, fresh Controller recheck, then one sequential P07 author in existing WORK. Keep all four HIGH future obligations enforced; no phase PASS/merge/release.','evidence':[{'path':str((O/f).relative_to(R)),'sha256':h(O/f)} for f in ['REVIEW.md','own-source-verification.json','eight-domain-assessment.json','original-findings-closure.json','future-HIGH-obligations.json','capability-evidence-matrix.json']]}
assert set(capabilities)=={'full_p06','safe_handoff','navigation_pilot','audio_playback_pipeline','pacing_instrumentation','secret_integration_contract'}
assert set(future)=={'chapter_delivery_21','campaign_pacing_actual','new_audio_acceptance','secret_delivery_7'}
for c in capabilities.values():
 for e in c['evidence']:assert inv[e['path']]==e['sha256']==h(R/e['path'])
assert set(load(O/'root-game-inventory.json')).issubset(inv)
for rel,sha in inv.items():assert h(R/rel)==sha,rel
write(O/'decision.json',decision)
files=[{'path':str(p.relative_to(O)),'sha256':h(p),'bytes':p.stat().st_size} for p in sorted(O.rglob('*')) if p.is_file() and p.name not in ['artifacts.json','FINAL_HASHES.json']]
write(O/'artifacts.json',{'schema':1,'immutable_after_completion':True,'files':files,'file_count':len(files),'bytes':sum(v['bytes'] for v in files)})
write(O/'FINAL_HASHES.json',{'schema':1,'status':'PASS','acceptance_level':'FULL','decision_sha256':h(O/'decision.json'),'review_sha256':h(O/'REVIEW.md'),'artifacts_sha256':h(O/'artifacts.json'),'reviewed_source_inventory_keys':len(inv),'portable_files':len(files)})
print((O/'FINAL_HASHES.json').read_text())
