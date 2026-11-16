from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-native-pipeline-preflight-03';Q=R/'reports/phases/P06/qa-native-pipeline-preflight-03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert sha(Q/'decision.json')=='745469b173586b580a9f938eee645e6517e433aa23c7c36004ded758ba2352b8';qd=read(Q/'decision.json');assert qd['status']=='PASS_COMPONENT' and qd['open_findings']==[] and qd['source_commit']=='8e17546f15a9ca563afbfa0fdd0ac9558f3eed30'
assert sha(O/'frozen-8e-verify_p06.py')==qd['source_sha256']==sha(W/'tools/verify_p06.py')
refs=[]
for e in read(Q/'artifacts.json')['files']:
 p=Q/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'];refs.append({'ROOT_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
D=O/'independent-QA03';D.mkdir(exist_ok=True)
for n in ['decision.json','review.md','artifacts.json','FINAL_HASHES.json']:
 shutil.copyfile(Q/n,D/n);refs.append({'ROOT_relative_path':str((Q/n).relative_to(R)),'sha256':sha(Q/n),'bytes':(Q/n).stat().st_size})
put('QA03-reference-bindings.json',{'files':refs,'own_hash_checks':True})
old1=R/'reports/phases/P06/lead-native-pipeline-preflight-01';old2=R/'reports/phases/P06/lead-native-pipeline-preflight-02';assert sha(old1/'decision.json')=='56625a6d5139105367716e046305ff61b678ce5efe7b2e2307056192b7b48fdf' and sha(old2/'decision.json')=='e52df1cd8d584853602552233898b059ffe3413d188cafb3bb6221eda70c38e4'
for p in [old2/'own-terminal-cleanup-proofs.json',old2/'frozen-11f-verify_p06.py',old1/'own-probe-result.json',old1/'silent-orphan-result.json']:
 refs.append({'ROOT_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
closure=read(O/'own-parser-closure.json');assert all(x['actual']==x['expected'] for x in closure['unchanged_raw_QA02_parser_cases']) and closure['source_freeze_main_logic_exact_to11f']
current_head=subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip();assert not subprocess.check_output(['git','-C',str(W),'diff','8e17546f15a9ca563afbfa0fdd0ac9558f3eed30..HEAD','--','game','tools','autopilot/config.json'])
assert not subprocess.check_output(['git','-C',str(W),'diff','0dd1cc4dad9379c457e277969b721fcc23a14fe3..HEAD','--','game','assets/source_audio'])
source={}
for k in ['tools/verify_p06.py','tools/verify_p06_npc_baseline.py','tools/probes/p06_npc_category_baseline.gd','tools/tests/test_p06_pipeline.py','autopilot/config.json','tools/verify_p04g.py','tools/verify_p04.py','tools/analyze_p04g_audio.py']:
 p=W/k;dest=O/'source-snapshot'/k;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);source[k]={'sha256':sha(p),'bytes':p.stat().st_size}
assert read(W/'autopilot/config.json')['native_qa_timeout_seconds']==7200 and read(W/'autopilot/config.json')['stop_after_phase']=='P06'
put('source-freeze.json',{'code_commit':'8e17546f15a9ca563afbfa0fdd0ac9558f3eed30','HEAD_at_review':current_head,'files':source,'Game_SourceAudio_exact_accepted0dd':True,'metadata_only_archival_commit_condition':'Before execution recheck these exactbytes and freeze actual executionHEAD; no commits/writers duringjob. Metadataarchivesdo notapprove code changes.'})
put('findings-closure.json',{'schema':1,'closed':[{'id':'NPIPE-L01','QA':'PIPE-Q01','scope':'TestedLinuxprocessownership','proof':'Threeactual11fterminalorphan negatives+ordinarycontrol; fiveprocessfunctions exactlyidenticalin8e; no processcasesfalselyrerun'},{'id':'NPIPE-L02','QA':'PIPE-Q02','scope':'Strictfinite/decodedduplicate/typedreport boundaries','proof':'Own18unchangedpriorcasescorrect; QA03all34correct; own12realformatcontrolsincludingoldfailedreportrejection; QA03actual16compatiblecurrentpositiveformats'}],'open_must_fix_findings':[],'old01_02_FAILs_unchanged':True,'actual_full13_run_done':False})
(O/'review.md').write_text('''# Native P06 pipeline — independent Lead preflight03

**PASS_COMPONENT_EXECUTION_ONLY. GO for one frozen canonical serial technical13-stage native run**, using reviewed8e17546f15a9ca563afbfa0fdd0ac9558f3eed30 code. This is permission to execute the verification, not acceptance of its future results, full P06, merge, P07 or ROOT installation.

## Independently verified closure

I read the actual8e diff and control flow. The only change from11f is finite float decoding plus strict nonempty string checks for names/logs/argv. My own pure probe reuses all18 exact prior QA02 raw JSON inputs: every expected accept/reject now matches. Positive/negative exponent overflow no longer slips through parse_constant; decoded duplicate keys, literal NaN/Infinity, malformed typed fields and contradictory exits remain rejected. I also independently checked12 real historical child-report formats:11 positives accept and the actual failed native02 report rejects. This is format compatibility, not fresh native execution or a current-source approval for those old captures.

The five process functions enable_subreaper/owned_descendants/live_descendants/stop_descendants/run_command are text-byte-identical to the separately and actually tested11f implementation. I independently compared their source-segment hashes. Therefore the actual inherited-pipe timeout, silent-success orphan, silent-nonzero orphan and ordinary positive control proofs are reused, not rerun or falsely called new process tests. They demonstrate bounded structured failure/cleanup and no live child left in the tested Linux cases; no guarantee about unkillable kernel processes or hostile escapes is claimed. The actual source HEAD/inventory freeze logic is unchanged.

QA03 is immutable PASS_COMPONENT745469b1…. I loaded its decision/review and independently rehashed all49 portable files. QA executed34/34 pure parser cases (the18 old plus16 additional), independently read/hashed16 genuine retained reports and ran3 selected existing pure parser unit tests. Its five-function text/AST identity and raw process-proof inspection agree with my own checks. No Game/Godot/full pipeline was executed by these reviewers. Old Lead01FAIL56625a6d… and Lead02FAILe52df1cd… are hash-verified unchanged; they are not replaced retroactively.

## Reviewed execution scope

The plan contains13 distinct native stages: eight current mechanic verifiers, normal and large-text cast, targeted C01 headroom, the exact independently accepted204-assertion NPC supplement, and P04G Full/Reduced/P04 regression/stress. --exports and --movie are forwarded to real helpers/artifacts. The separate49 technical stage is not repeated by the native plan; six accepted WORLD/art sets are not gratuitously regenerated. C01 headroom3 contacts are not represented as a fresh45-route run. Headless remains a separate technical-only plan and cannot be combined with requested native exports/movie. The author summary explicitly grants no phase or native acceptance.

I checked actual helper flag declarations and the source/plan changes. Current Game and SourceAudio remain byte-exact to accepted0dd; the new maintained NPC probe is the existing independently executed baseline oracle, not new deferred C09 artwork or a new damage engine. Input scope and all remaining phase gates are unchanged.

## Conditions for this one run

Use the sole canonical ROOT worker after releasing the author lease, working directory WORK, exact reviewed code/toolchain/inputs, and fresh immutable output/build directories. Suggested interface: python3 tools/verify_p06.py --exports --movie --output <fresh-output> --build-output <fresh-build>. Record the actual execution HEAD and before/after inventory; permit no commit/source writer during the job. Any metadata-only archive before dispatch requires rechecking the exact reviewed source bytes. This does not authorize code drift.

Use the declared7200-second overall budget. Child maximums sum8520s;7200 is an outer cap, not a promise of completion under every slow condition. If interrupted/timed out/failed, preserve actual partial evidence/receipts, do not claim all stages passed or automatically rerun consumed work. Stop on failed containment or remaining live owned children. Linux subreaper ownership assumes a dedicated verifier process with no unrelated child jobs sharing it. Existing ROOT worker process-group containment must remain intact.

After the run, inspect every actual stage result, exact source/log/artifact bindings, real movies/PCM/export/runtime/performance scopes and any failure. Existing static ART/world/likeness decisions retain their original bounds; fresh native technical success is not a new subjective visual/audio or gameplay feel approval. Wine is not native Windows; MovieMaker/forced simulation timing is not wall-frame performance.

## Limits

No full13-stage execution has happened under this preflight. Full independent ART/Gameplay/QA/Lead, mandatory current-SHA remote CI/protection/approval/thread checks and guarded delivery remain required. READINESS-C02 safe ROOT/WORK installation and later Production Readiness/21MDS remain separate. C09 visual work remains P08 debt. No phase attempt is consumed, state/stop-limit changed, source installed into ROOT, merge/publication/release granted, agent hearing/FPS/hardware latency/native Windows acceptance invented. My writes are limited to this ROOT report and synthetic proof data; no Game/tools/state/Controller/Git mutation or engine run occurred.
''')
put('metrics.json',{'source_commit':'8e17546f15a9ca563afbfa0fdd0ac9558f3eed30','own_unchanged_QA02_raw_cases':18,'own_existing_real_format_controls':12,'QA03_actual_parser_cases':34,'QA03_real_report_controls':16,'QA03_selected_parser_units':3,'QA03_portable_files_verified':49,'identical_process_functions':5,'reused_actual11f_terminal_negatives':3,'reused_actual11f_positive':1,'native_stages_planned':13,'actual_full13_executions':0,'engines_run_by_Lead':0,'outer_budget_seconds':7200,'sum_child_max_seconds':8520})
put('external-reference-bindings.json',{'base':'ROOT','records':refs})
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['decision.json','artifacts.json','FINAL_HASHES.json']:files.append({'path':str(p.relative_to(O)),'sha256':sha(p),'bytes':p.stat().st_size})
put('artifacts.json',{'schema':1,'base':'manifestdirectory','files':files,'negativeJSON_test_fixtures_included':True,'raw_photos_or_engines_orGamecopy':False})
put('decision.json',{'schema':1,'role':'INDEPENDENT_LEAD','status':'PASS_COMPONENT_EXECUTION_ONLY','scope':'8e native pipeline harness preflight only; one canonical frozen serial technical13-stage run','source_code_commit':'8e17546f15a9ca563afbfa0fdd0ac9558f3eed30','source_module_sha256':sha(W/'tools/verify_p06.py'),'HEAD_at_review':current_head,'QA03_decision_sha256':sha(Q/'decision.json'),'permission_to_execute_one_frozen_full_native_pipeline':True,'execution_scope':'SOLE_CANONICAL_ROOT_WORKER_FRESH_IMMUTABLE_PATHS_AUTHOR_RELEASED','outer_timeout_seconds':7200,'source_freeze_required':True,'automatic_retry_authorized':False,'open_must_fix_findings':[],'closed':['NPIPE-L01','NPIPE-L02'],'phase_approval':False,'native_acceptance_approval':False,'full_P06_approval':False,'P07_approval':False,'P08_approval':False,'merge_approval':False,'release_approval':False,'ROOT_installation_or_handoff_approval':False,'readiness_approval':False,'formal_phase_attempt_consumed':False,'actual13_execution_done':False,'proofs':{n:sha(O/n) for n in ['review.md','findings-closure.json','metrics.json','artifacts.json','source-freeze.json','own-parser-closure.json','QA03-reference-bindings.json','external-reference-bindings.json']},'next_action':'Root may stage exactlyonefrozenserialtechnicalnative13run, then separatelyreviewactualoutcomes; no phaseadvance/merge basedonthispreflight.'})
put('FINAL_HASHES.json',{n:sha(O/n) for n in ['decision.json','review.md','artifacts.json','findings-closure.json','metrics.json','source-freeze.json']})
for e in files:assert sha(O/e['path'])==e['sha256']
print(json.dumps({'status':'PASS_COMPONENT_EXECUTION_ONLY','files':len(files),'bytes':sum(e['bytes'] for e in files),'hashes':read(O/'FINAL_HASHES.json')},indent=2))
