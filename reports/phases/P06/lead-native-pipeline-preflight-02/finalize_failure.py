from pathlib import Path
import json,hashlib,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');O=R/'reports/phases/P06/lead-native-pipeline-preflight-02';Q=R/'reports/phases/P06/qa-native-pipeline-preflight-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
assert sha(Q/'decision.json')=='14055fc56a8c29eb1bd6260b21b8b0976a458a38fe96ce72f036915440d2f729';d=read(Q/'decision.json');assert d['status']=='FAIL_COMPONENT' and sha(O/'frozen-11f-verify_p06.py')==d['source_sha256']
refs=[]
for e in read(Q/'artifacts.json')['files']:
 p=Q/e['path'];assert sha(p)==e['sha256'] and p.stat().st_size==e['bytes'];refs.append({'ROOT_relative_path':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size})
D=O/'independent-QA02';D.mkdir(exist_ok=True)
for n in ['decision.json','review.md','artifacts.json','FINAL_HASHES.json']:shutil.copyfile(Q/n,D/n)
put('QA02-reference-bindings.json',{'files':refs,'actual_source_sha256':d['source_sha256']})
put('findings.json',{'schema':1,'closed':[{'id':'NPIPE-L01','QA':'PIPE-Q01','status':'CLOSED_IN_TESTED_PROCESS_SCOPE','proof':'own-terminal-cleanup-proofs.json; inheritedpipe timeout124, silentexit0FAIL, silentexit7FAIL, nochildrenleft and ordinarypositivecontrol'}],'must_fix':[{'id':'NPIPE-L02','QA':'PIPE-Q02','severity':'MEDIUM','status':'PARTIALLY_REMEDIATED_STILL_BLOCKING_EXECUTION','proof':'own-parser-remaining-proofs.json + independentQA02report-boundary-results','actual_remaining_unsafe_acceptances':'finiteoverflow1e309/-1e309; legacynameint/list; legacylogint; argvnonstringitems','fix':'Rejectfiniteoverflowthroughparse_float/recursivevalidation; require meaningfulstringname/log/argvitems; samecasesplusgenuineactualformats.'}],'new_Game_requirements':False})
(O/'review.md').write_text('''# Fixed11f native pipeline — independent Lead closure02

**FAIL_COMPONENT / NO-GO** for11f0666d7f9c62896f57a3980c1c4b1d2c9eb1af. This is separate from original454e FAIL56625a6d… and from the newer8e candidate; neither original report is rewritten. Full P06, Root installation, merge and full native execution are not approved.

The process-ownership repair closes NPIPE-L01 within the tested Linux scope. I read the actual subreaper/identity/cleanup code and ran only three pure terminal fixtures plus an ordinary positive control: inherited-pipe child after wrapperexit0 returns structured124; silent child after wrapperexit0 is cleaned and makes passed=false; silent child after wrapperexit7 is cleaned and staysfailed. There are no live residual children or emergency cleanup. The code keeps canonical worker process-group containment. These are Python process lifecycle checks, not Godot/native execution, physical hardware or a guarantee about unkillable kernel processes.

NPIPE-L02 remains MEDIUM and blocks the long run. LiteralNaN/Infinity, decoded duplicate keys, contradictoryexit and barelegacy rejection were improved, but parser still accepts1e309→inf and malformedtyped payloads. My independent pure fixtures confirm overflow, argv[null,{}], integerlegacyname and integerlegacylog accepted. Independent QA02 tested18 cases:12correct and6unsafe, additionally negativeoverflow and listlegacyname. The minimal remedy is finite-number decoding and nonempty string type checks, not a new gameplay requirement or looser test.

I also passed the fixed parser over twelve existing real child-report formats: eleven historical positiveformats accept, while the genuinely failed native02 validation rejects. This is format compatibility only, not a new source/runtime approval or fresh engine run. The13stage/native-vs-headless plan remains the intended real composition; phase_approval=false/noRootinstall scope is preserved.

QA02 decision14055fc5… is immutable FAIL_COMPONENT; I read it and its review and verified all26portablefiles against the manifest. It uses the exacte065 source, agrees with the process closure and leaves the six parser cases open. No engines or full13pipeline were run. My only writes are this reviewer-owned ROOT report and synthetic fixture outputs. No Game/tools/state/Controller/Git mutations occurred.

New8e closes these parser cases in a separately prepared draft, with process functions unchanged. That candidate requires its own immutable QA03 and independent Lead decision before any GO. Preserving this11fFAIL does not reopen accepted P06 art/abilities/audio or consume a formal phase attempt.
''')
put('metrics.json',{'source_commit':d['source_commit'],'process_negative_cases':3,'ordinary_positive_control':1,'process_orphans_remaining':0,'own_remaining_parser_unsafe_cases':4,'own_real_report_format_cases':12,'independent_QA02_cases':18,'independent_QA02_unsafe_cases':6,'QA02_portable_files_verified':26,'Game_or_full_pipeline_executions':0,'phase_attempt_consumed':False})
files=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name not in ['decision.json','artifacts.json','FINAL_HASHES.json']:files.append({'path':str(p.relative_to(O)),'sha256':sha(p),'bytes':p.stat().st_size})
put('artifacts.json',{'schema':1,'base':'manifestdirectory','files':files,'negativeJSON_and_purePythonfixtures_only':True,'Game_orenginecopies':False})
put('decision.json',{'schema':1,'status':'FAIL_COMPONENT','role':'INDEPENDENT_LEAD','scope':'Fixed11f native pipeline process/report contract closure only','source_commit':d['source_commit'],'source_sha256':d['source_sha256'],'closed':['NPIPE-L01'],'must_fix':['NPIPE-L02'],'QA02_decision_sha256':sha(Q/'decision.json'),'permission_to_execute_full_native_pipeline':False,'new8e_candidate_approval':False,'phase_approval':False,'full_P06_approval':False,'merge_approval':False,'ROOT_installation_or_handoff_approval':False,'formal_phase_attempt_consumed':False,'native_engine_runs_by_reviewer':0,'proofs':{n:sha(O/n) for n in ['review.md','findings.json','metrics.json','artifacts.json','own-terminal-cleanup-proofs.json','own-parser-remaining-proofs.json','genuine-report-format-compatibility.json','QA02-reference-bindings.json']},'next_action':'Separate8e strictfinite/stringtype closure with unchangedprocess-function binding and immutableQA03 beforeLead GO.'})
put('FINAL_HASHES.json',{n:sha(O/n) for n in ['decision.json','review.md','artifacts.json','findings.json']})
for e in files:assert sha(O/e['path'])==e['sha256']
print(json.dumps({'status':'FAIL_COMPONENT','files':len(files),'bytes':sum(e['bytes'] for e in files),'hashes':read(O/'FINAL_HASHES.json')},indent=2))
