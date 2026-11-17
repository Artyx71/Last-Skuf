from pathlib import Path
import json,hashlib,subprocess,shutil
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/lead-npc-visual-deferral-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(n,d):(O/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def read(p):return json.loads(p.read_text())
S='automation/decisions/P06_NPC_VISUAL_POLISH_TO_P08.json';expected='58abd098c446842d8f2ae8ccb8859757f218afe64714ec1780197eb432a9923a'
assert sha(R/S)==sha(W/S)==expected;decision=read(W/S)
assert decision['owner_quote']=='как можем это дописать к п08 а по остальному п06 вроде уже норм' and decision['kind']=='OWNER_APPROVED_SCOPE_DEFERRAL_NOT_PHASE_ACCEPTANCE' and decision['baseline_shared_NPC_category_clips_allowed_for_P06'] is True
for k in ['P06_approval','phase_approval','merge_approval','P07_entry_approval','P08_execution_approval','release_approval','new_rejected_art_adopted','old_FAIL_reports_rewritten','deferred_work_accepted_as_implemented']:assert decision[k] is False
assert (R/'autopilot/queue.json').read_bytes()==(W/'autopilot/queue.json').read_bytes()
queue=read(W/'autopilot/queue.json');now={t['id']:t for t in queue['tasks']};oldq=json.loads(subprocess.check_output(['git','-C',str(W),'show','HEAD:autopilot/queue.json'],text=True));old={t['id']:t for t in oldq['tasks']}
assert len(now)==len(queue['tasks']) and set(old)<=set(now)
oldids=['P06/C09-npc-presentation-contract','P06/C09-npc-style-art','P06/C09-npc-style-integration','P06/C09-npc-style-review'];newids=['P08/npc-style-contract','P08/npc-style-art','P08/npc-style-integration','P08/npc-style-review'];changed={i for i in old if now[i]!=old[i]}
assert set(now)-set(old)==set(newids) and changed==set(oldids+['P06/seven-hero-finisher-art-sound-reactions','PREP07/READINESS-C01'])
for a,b in zip(oldids,newids):
 t=now[a];u=now[b]
 assert t['status']=='DEFERRED_BY_OWNER_TO_P08' and t['must_pass_before_P07'] is False and t['blocking_for_P06'] is False and t['phase_approval'] is False
 assert t['status_before_owner_deferral']==old[a]['status'] and t['scope_before_owner_deferral']==old[a]['scope'] and t['deferred_to']==b and t['owner_scope_decision_sha256']==expected
 assert u['historical_task']==a and u['debt_id']=='P08-NPC-STYLE-01' and u['severity']=='HIGH' and u['status']=='DEFERRED_NOT_IMPLEMENTED_NOT_ACCEPTED' and u['safe_retry'] is False and u['P08_execution_approval'] is False and u['phase_approval'] is False and u['owner_scope_decision_sha256']==expected
 assert u['depends_on']==(['P07:PASS','P07:MERGED'] if b==newids[0] else [newids[newids.index(b)-1]])
 assert u['gate']=='BEFORE_P08_FINAL_ACCEPTANCE_AND_RELEASE'
parent=now['P06/seven-hero-finisher-art-sound-reactions'];assert parent['status']=='PENDING' and parent['must_pass_before_P07'] is True and parent['phase_approval'] is False
assert set(old[parent['id']]['depends_on'])-set(parent['depends_on'])=={'P06/C09-npc-style-review'} and set(parent['depends_on'])<=set(old[parent['id']]['depends_on'])
reach=set();stack=list(parent['depends_on'])
while stack:
 i=stack.pop()
 if i in reach:continue
 reach.add(i);stack.extend(now.get(i,{}).get('depends_on',[]))
assert not reach.intersection(oldids+newids)
blockedlinks=[]
for t in queue['tasks']:
 ds=set(t.get('depends_on',[])).intersection(oldids)
 if ds:assert t['id'] in oldids and t['status']=='DEFERRED_BY_OWNER_TO_P08';blockedlinks.append({'id':t['id'],'dependencies':sorted(ds)})
r=now['PREP07/READINESS-C01'];assert r['status']=='OPEN' and r['severity']=='CRITICAL' and r['gate']=='BEFORE_P07_ENTRY' and r['phase_approval'] is False
assert r['acceptance']==old[r['id']]['acceptance'] and r['scope_before_owner_NPC_deferral']==old[r['id']]['scope']
put('queue-proofs.json',{'ROOT_WORK_queue_byte_exact':True,'tasks_before':len(old),'tasks_after':len(now),'added':newids,'removed':[],'only_changed_existing':sorted(changed),'old_statuses_preserved_as_metadata':True,'no_non_deferred_task_depends_on_deferred_ids':True,'deferred_chain_internal_links_only':blockedlinks,'P06_parent_transitive_dependencies':sorted(reach),'P06_parent_pending_required':True,'READINESS_C01_still_OPEN_CRITICAL_original_acceptance':True,'P08_gates':{i:now[i] for i in newids},'canonical_runtime_scope_import_executed_by_Lead':False})
# Bind all current amendment documents and the complete actual diff.
paths=['README.md','docs/PROJECT_GATES.md','planning/P08_TECH_DEBT.md','planning/P06_C09_TASKS.md','planning/P06_TASKS.md','planning/PHASES.md','specs/CHARACTER_EXPANSION_SPEC.md','specs/P06_COMBAT_ACCEPTANCE.md','autopilot/queue.json',S,'reports/STATUS.md','reports/NEXT_ACTION.md','reports/phases/P06/resume/decision.json','autopilot/config.json','assets/source_art/npc_styles/gabar/partial-source-ledger.json']
inputs={}
for k in paths:
 p=W/k;dest=O/'WORK-snapshot'/k;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);inputs[k]={'sha256':sha(p),'bytes':p.stat().st_size}
for k in ['autopilot/queue.json',S,'autopilot/config.json']:
 p=R/k;dest=O/'ROOT-snapshot'/k;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
put('input-freeze.json',{'WORK_head':subprocess.check_output(['git','-C',str(W),'rev-parse','HEAD'],text=True).strip(),'WORK_files':inputs,'ROOT_mirrors':{k:sha(R/k) for k in ['autopilot/queue.json',S,'autopilot/config.json']},'not_whole_future_tree_freeze':True})
(O/'amendment.diff').write_bytes(subprocess.check_output(['git','-C',str(W),'diff','--']+paths))
# Baseline not mutated; separate generic CI harness modification is not this scope receipt's runtime acceptance.
f=read(R/'reports/phases/P06/lead-character-finisher-audio-01/source-freeze.json');delta=[k for k,v in f['source_hashes'].items() if sha(W/k)!=v];assert delta==['tools/verify.py']
(O/'separate-contact-timing-harness.diff').write_bytes(subprocess.check_output(['git','-C',str(W),'diff','--','tools/verify.py']))
assert not subprocess.check_output(['git','-C',str(W),'diff','--','game','assets/source_audio'])
assert '--fixed-fps' in (W/'tools/verify.py').read_text() and sha(W/'game/tests/contact_timing_test.gd')==f['source_hashes']['game/tests/contact_timing_test.gd']
put('production-integrity.json',{'C01_0dd_recorded_keys':1465,'unchanged_recorded_keys':1464,'exception':'tools/verify.py','exception_current_sha256':sha(W/'tools/verify.py'),'exception_is_separate_declared_headless_contact_timing_clock_alignment':True,'Game_and_SourceAudio_unmodified':True,'contact_test_oracle_exact':True,'harness_execution_by_Lead':False,'harness_runtime_acceptance_granted':False,'new_NPC_source_runtime_adoption':False})
ledger=read(W/'assets/source_art/npc_styles/gabar/partial-source-ledger.json');assert ledger['counts']=={'retained_new_source_wholeposes':19,'existing_P04_release_refs':1,'missing_contact_wholeposes':4,'expected_total_role_slots':24};assert ledger['complete'] is False and ledger['ready_for_runtime'] is False and ledger['phase_approval'] is False
history=[]
for k,h in zip(['art-c09-gabar-source-01','art-c09-gabar-source-02','art-c09-gabar-reuse-feasibility-01'],decision['historical_source_reviews']):
 p=W/f'reports/phases/P06/{k}/decision.json';assert sha(p)==h;d=read(p);dest=O/'historical-decisions';dest.mkdir(exist_ok=True);shutil.copyfile(p,dest/(k+'.json'));history.append({'id':k,'sha256':h,'status':d.get('status')})
put('unaccepted-source-history.json',{'decisions':history,'ledger_counts':ledger['counts'],'runtime_ready':False,'historical_tool_block_request':decision['tool_block_request_id'],'tool_retries_or_generation_by_Lead':0})
# Read-only authority observations: never normalize existing runner counters into formal review count.
state=read(R/'automation/phase_state.json');assert state['active_phase']=='P06' and state['status']=='IMPLEMENTING' and state['last_pass']=='P05'
assert read(R/'autopilot/config.json')['stop_after_phase']==read(W/'autopilot/config.json')['stop_after_phase']=='P06'
phase_attempt=state['autopilot']['phases']['P06']['attempts'];assert phase_attempt==1
resume=read(W/'reports/phases/P06/resume/decision.json');assert resume['formal_attempt']==1 and resume['phase_approval'] is False and resume['merge_allowed'] is False
put('authority-observation.json',{'canonical_state_sha256_at_read':sha(R/'automation/phase_state.json'),'active_phase':state['active_phase'],'status':state['status'],'last_pass':state['last_pass'],'canonical_existing_runner_attempts_counter':state['attempts'],'canonical_autopilot_P06_phase_attempts':phase_attempt,'WORK_formal_phase_attempt':resume['formal_attempt'],'counter_reset_or_reinterpretation':False,'ROOT_and_WORK_stop_after':'P06','canonical_scope_import':'NOT_EXECUTED_OR_APPROVED_BY_THIS_REVIEW','controller_execution_by_Lead':False,'current_or_future_ROOT_installation_approval':False})
for k,v in inputs.items():assert sha(W/k)==v['sha256'],k
print('SCOPE_CHECKS_COMPLETE',len(old),'→',len(now),'changed6/add4; production1464+separate1harness; no baselinewaiver')
