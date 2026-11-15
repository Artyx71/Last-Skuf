import pathlib,json,hashlib,subprocess,re
R=pathlib.Path(__file__).resolve().parents[4];W=R/'.autopilot/worktrees/P06';Q=pathlib.Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,j):(Q/n).write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n')
frozen=json.loads((Q/'source-freeze.json').read_text());wanted='3decbaaafcec4597a33b2fcff1613f18';job=R/'.autopilot/jobs'/wanted
receipt=json.loads((job/'receipt.json').read_text());inp=json.loads((job/'input.json').read_text());assert receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log') and receipt['argv_sha256']==inp['argv_sha256']
state=json.loads((R/'.autopilot/STATE.json').read_text());hist=state.get('autopilot',{}).get('history',[]);matches=[e for e in hist if wanted in json.dumps(e)]
save('producer-receipt-verification.json',{'operation':wanted,'receipt':receipt,'receipt_sha256':h(job/'receipt.json'),'input_sha256':h(job/'input.json'),'actual_log_sha256':h(job/'output.log'),'verified_exit0_log_and_argv':True,'prior_readonly_observation':'Operation 3decbaaafcec4597a33b2fcff1613f18 was observed COMPLETED and consumed=true before a later author checkpoint advanced current operation.','history_matches':matches,'state_policy':'Current operation and global state bytes may advance. No Controller called.'})
art=[];summ=[]
for kind in ['headless-03','native-03']:
 p=W/'reports/phases/P06/guard-feedback-01'/kind/'validation.json';j=json.loads(p.read_text());assert j['passed'] and j['source_unchanged'] and j['source_head']==frozen['frozen_HEAD'];assert all(c['exit_code']==0 and c['passed'] for c in j['commands'])
 for a in j['artifacts']:
  assert h(W/a['path'])==a['sha256'],a['path'];art.append(a)
 sj=json.loads((p.parent/'source_hashes.json').read_text())
 for key,sha in frozen['files_sha256'].items():
  if key in sj:assert sj[key]==sha,key
 summ.append({'kind':kind,'validation_sha256':h(p),'checks':j['checks'],'captures':j['actual_captures'],'artifacts_verified':len(j['artifacts']),'matching_frozen_keys_in_source_inventory':len(set(sj)&set(frozen['files_sha256']))})
save('author-final03-artifacts.json',{'actual_work_artifacts':art,'validation_summaries':summ,'method':'Actual SHA256 compared to author inventory. Inspection of author runs, not a rerun.'})
p=W/'reports/phases/P06/guard-feedback-01/final-validation-03/result.json';j=json.loads(p.read_text());assert j['passed'] and j['source_unchanged'] and all(c['passed'] and c['exit_code']==0 for c in j['commands']);logs=[]
for f in sorted(p.parent.rglob('*.log')):
 text=f.read_text(errors='replace');bad=[x for x in text.splitlines() if re.search(r'(^|\s)(SCRIPT ERROR:|ERROR:|WARNING:.*leak)',x)];assert not bad,(f,bad);logs.append({'path':str(f.relative_to(W)),'sha256':h(f),'error_leak_lines':bad})
save('author-regressions-inspected.json',{'result_sha256':h(p),'result':j,'logs':logs,'execution':'Author runs inspected; not independently rerun. Independent subset separately recorded.'})
movie=W/'build/P06/guard-feedback-01/native-03/counter-feedback.mp4';proc=subprocess.run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)],capture_output=True,text=True,timeout=30);assert proc.returncode==0
save('actual-native-movie-probe.json',{'path':str(movie.relative_to(W)),'sha256':h(movie),'bytes':movie.stat().st_size,'ffprobe_exit_code':proc.returncode,'probe':json.loads(proc.stdout),'limitation':'Container/stream verification only; no independent native replay, FPS performance, listening or full-video visual acceptance.'})
copy=json.loads((Q/'copy-inputs.json').read_text())
for key,sha in copy.items():assert h(Q/'isolated-project'/key)==sha,key
for key,sha in frozen['files_sha256'].items():assert h(W/key)==sha and h(Q/'code-freeze'/key)==sha,key
save('post-run-integrity.json',{'frozen_6_work_and_snapshots_exact':True,'isolated_original_files_byte_exact':len(copy),'extra_isolated_probe_only':'game/tests/qa_counter_boundary.gd','work_mutations_by_qa':False,'canonical_state_mutations_by_qa':False})
print(json.dumps({'receipt':True,'author_artifacts':len(art),'logs':len(logs),'movie_bytes':movie.stat().st_size,'copy_unchanged':len(copy),'history_matches':len(matches)}))
