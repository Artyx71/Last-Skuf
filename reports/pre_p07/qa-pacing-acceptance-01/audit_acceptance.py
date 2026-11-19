from pathlib import Path
import json,math,hashlib,collections,ast,subprocess
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P07';O=Path(__file__).resolve().parent;D=W/'reports/pre_p07/pacing-acceptance-01';Q=R/'reports/pre_p07/qa-pacing-calibration-02'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def st(values):
 s=sorted(values);assert s and all(type(v)in[int,float]and math.isfinite(v)and v>=0 for v in s)
 return {'samples':len(s),'p50':s[math.ceil(len(s)*.5)-1],'p95':s[math.ceil(len(s)*.95)-1],'p99':s[math.ceil(len(s)*.99)-1],'max':s[-1]}
raw=read(D/'raw.json');metrics=read(D/'metrics.json');validation=read(D/'validation.json');reported=read(D/'threshold_checks.json');runs=read(D/'runs.json');contract_path=W/'reports/pre_p07/pacing-contract-03/contract.PROPOSED.json';review_path=R/'reports/pre_p07/lead-pacing-calibration-02/decision.json';contract=read(contract_path);review=read(review_path)
assert sha(contract_path)=='4eb9b3f8a3aaa568a32c7b41ae1db80429f7f7f945a020513c206f0c1b23225a'==validation['contract_sha256']
assert sha(review_path)=='9966128fa846201420b9891d751e6f7da060871cdf819e5152337a488a5f5b85'==validation['review_sha256']
assert review['status']=='PASS_COMPONENT'and review['role']=='LEAD_REVIEWER'and review['scope']=='H04_CALIBRATION_CONTRACT'and review['independent_of_author']is True and not review['must_fix']and review['contract_sha256']==sha(contract_path)
assert raw['hardware']==contract['hardware']
before=read(D/'source_before.json');after=read(D/'source_after.json');assert before==after==contract['source_inventory_sha256']and len(before)==616
for n,h in before.items():assert sha(W/n)==h,n
# Exact guard and inherited measurement source match the independently reviewed df snapshot.
for n in ['tools/p07_pacing.py','tools/fixtures/p07_pacing.gd','tools/p07_second_pilot.py','autopilot/readiness.py']:assert sha(W/n)==sha(Q/'final-source-df'/n),n
assert sha(Q/'decision.json')=='3b1a2b8b83b510d49fa39c55cff1d735f029662d678fc53519350062671da7be'
# Evaluate only frozen pure functions: no import/execute of production runner or engine.
ns={'json':json,'math':math,'hashlib':hashlib,'Path':Path,'digest':sha}
t=ast.parse((Q/'final-source-df/autopilot/readiness.py').read_text());exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='strict_json'],type_ignores=[]),'frozen-house','exec'),ns)
t=ast.parse((Q/'final-source-df/tools/p07_pacing.py').read_text());nodes=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name in ['percentile','visual_key','integer_fields','analyze','load_contract','validate_pins']or isinstance(n,ast.Assign)and any(isinstance(v,ast.Name)and v.id=='CONTEXTS'for v in n.targets)];exec(compile(ast.Module(body=nodes,type_ignores=[]),'frozen-df','exec'),ns)
loaded,pins=ns['load_contract'](contract_path,review_path,before);ns['validate_pins'](pins);assert loaded==contract
fixed=ns['analyze'](raw);assert fixed==metrics
# Independent request/state/first-render/contact qualification and nearest-rank statistics.
contexts=['yakuza','gabar_training','olezhka_training','timka_present','timka_prime','ryzhik_training','tega_training','pasha_training'];counts=collections.defaultdict(collections.Counter)
assert type(raw['schema'])is int and raw['schema']==1 and len(raw['checks'])==74 and all(c['passed']is True for c in raw['checks'])and raw['passed']==74 and raw['failed']==0
assert len(raw['requests'])==48 and len(raw['contacts'])==16
for index,a in enumerate(raw['requests']):
 counts[a['context']][a['kind']]+=1
 assert a['context']==contexts[index//6]and a['id']==index+1 and a['kind']==(['move']*4+['melee','restart'])[index%6]
 assert a['input_usec']<=a['accepted_usec']<=a['render_usec']
 p=[v for v in raw['physics']if v['usec']==a['accepted_usec']and v['tick']==a['accepted_tick']];d=[v for v in raw['draws']if v['usec']==a['render_usec']and v['draw']==a['render_draw']]
 assert len(p)==len(d)==1 and p[0]['state']==a['accepted_state']and d[0]['state']==a['render_state']and p[0]['state']['context']==d[0]['state']['context']==a['context']
 end=raw['requests'][index+1]['input_usec']if index+1<48 else raw['ended_usec']
 def eligible(s):
  if s['context']!=a['context']or s['health']<=0 or s['host_state']!='playing':return False
  if a['kind']=='melee':return s['action']=='shove'
  if a['kind']=='restart':return s['position'][0]>80.01 and abs(s['position'][1]-280)<.01
  axis,sign=[(0,1),(1,1),(0,-1),(1,-1)][index%6];delta=[v-u for u,v in zip(a['before_state']['position'],s['position'])];return delta[axis]*sign>.01 and abs(delta[1-axis])<.01
 candidates=[v for v in raw['physics']if a['input_usec']<=v['usec']<end and eligible(v['state'])];assert candidates[0]['usec']==a['accepted_usec']
 changed=[v for v in raw['draws']if a['accepted_usec']<=v['usec']<end and v.get('state',{}).get('context')==a['context']and any(v['state'][k]!=a['before_state'][k]for k in ['draw_position','animation','frame'])];assert changed[0]['usec']==a['render_usec']
 if a['kind']=='melee':assert len([c for c in raw['contacts']if c['context']==a['context']and c['usec']==a['contact_usec']and c['target']!=c['player_id']and c['action']=='shove'and c['action_frame']==1])==1
 if a['kind']=='restart':
  assert len([c for c in raw['contacts']if c['context']==a['context']and c['usec']==a['death_usec']and c['target']==c['player_id']and c['lethal']is True and c['damage']>0])==1
  assert a['before_state']['health']==0 and a['before_state']['host_state']=='dead'and a['accepted_state']['health']==1 and a['accepted_state']['host_state']=='playing'
assert sorted(counts)==sorted(contexts)and all(v=={'move':4,'melee':1,'restart':1}for v in counts.values())
values={'input_accept_ms':[(v['accepted_usec']-v['input_usec'])/1000 for v in raw['requests']],'input_render_ms':[(v['render_usec']-v['input_usec'])/1000 for v in raw['requests']],'death_to_control_ms':[(v['accepted_usec']-v['death_usec'])/1000 for v in raw['requests']if v['kind']=='restart'],'accepted_to_contact_ms':[(v['contact_usec']-v['accepted_usec'])/1000 for v in raw['requests']if v['kind']=='melee'],'movement_frame_ms':[(b['usec']-a['usec'])/1000 for a,b in zip(raw['draws'],raw['draws'][1:])if a['segment']==b['segment']and a['segment']in ['controlled_movement','controlled_melee','controlled_restart']],'idle_frame_ms':[(b['usec']-a['usec'])/1000 for a,b in zip(raw['draws'],raw['draws'][1:])if a['segment']==b['segment']=='idle_calibration']}
rederived={k:st(v)for k,v in values.items()};assert all(metrics[k]==v for k,v in rederived.items())
measured={'accept_p95_ms':rederived['input_accept_ms']['p95'],'render_p95_ms':rederived['input_render_ms']['p95'],'frame_p95_ms':rederived['movement_frame_ms']['p95'],'frame_p99_ms':rederived['movement_frame_ms']['p99'],'restart_max_ms':rederived['death_to_control_ms']['max']};budgets={k:{'actual':v,'limit':contract['limits'][k],'passed':v<contract['limits'][k]}for k,v in measured.items()};assert budgets==reported and all(v['passed']is True for v in budgets.values())
# Fresh captures and fine-timebase VFR: decode timestamps only, not an engine run.
clips=raw['clip_frames'];assert len(clips)==105 and all(c['error']==0 for c in clips)and len({c['path']for c in clips})==105
for c in clips:assert Path(c['path']).is_file()and Path(c['path']).resolve().is_relative_to(D/'native_captures')
ffargv=['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=time_base,nb_frames,duration','-show_entries','frame=best_effort_timestamp_time','-of','json',str(D/'native-camera.mp4')];video=json.loads(subprocess.run(ffargv,capture_output=True,text=True,check=True).stdout);pts=[float(v['best_effort_timestamp_time'])for v in video['frames']];assert len(pts)==len(clips);base=clips[0]['usec'];errors=[abs(t-(v['usec']-base)/1e6)*1000 for t,v in zip(pts,clips)];assert max(errors)<.5
# Canonical terminal evidence: command hash recomputed using actual runner's JSON argv convention.
J=R/'.autopilot/jobs/a75a4330de35414ab87b8a143a28cce0';inp=read(J/'input.json');receipt=read(J/'receipt.json');assert hashlib.sha256(json.dumps(inp['argv']).encode()).hexdigest()==inp['argv_sha256']==receipt['argv_sha256'];assert receipt['operation']==inp['id']and receipt['exit_code']==0 and receipt['log_sha256']==sha(J/'output.log')
assert inp['argv'][-4:]==['--contract',str(contract_path),'--review',str(review_path)]
state=read(R/'automation/phase_state.json');op=state['autopilot']['operation'];assert op['id']==inp['id']and op['consumed']is True and op['exit_code']==0
assert len(runs)==2 and all(v['passed']is True and type(v['exit_code'])is int and v['exit_code']==0 for v in runs);assert '--disable-vsync'in runs[1]['argv']and runs[1]['argv'][runs[1]['argv'].index('--max-fps')+1]=='60'and '--fixed-fps'not in runs[1]['argv']
engine=Path(runs[1]['argv'][0]);assert sha(engine)=='8d106cbe6144c2dc7e881d61d2429c1a8a76e6b22ef48bd5e48dcf934953f71e'
for n in ['import.log','native.log']:assert not any(s in(D/n).read_text()for s in ['SCRIPT ERROR:','Parse Error:','ERROR:'])
assert validation['passed']is True and validation['mode']=='acceptance'and validation['raw_sha256']==sha(D/'raw.json')and validation['source_unchanged']is True
# Save actual evidence selected for portable independent review; no cache/game clone.
refs=[]
def record(p,d):
 q=O/d;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());refs.append({'origin':str(p.relative_to(R)),'copy':d,'sha256':sha(p),'bytes':p.stat().st_size})
for n in ['raw.json','metrics.json','validation.json','threshold_checks.json','source_before.json','source_after.json','runs.json','native.log','import.log','encode.json','encode.log','clip.ffconcat','native-camera.mp4']:record(D/n,'actual-evidence/'+n)
for n in ['input.json','receipt.json','output.log']:record(J/n,'actual-evidence/operation/'+n)
record(contract_path,'approved-inputs/contract.json');record(review_path,'approved-inputs/Lead-decision.json')
for index in [0,52,104]:record(Path(clips[index]['path']),'selected-captures/'+Path(clips[index]['path']).name)
for c in clips:refs.append({'origin':str(Path(c['path']).relative_to(R)),'sha256':sha(Path(c['path'])),'bytes':Path(c['path']).stat().st_size,'retained_in_place':True})
audit={'schema':1,'scope':'INDEPENDENT_CURRENT_H04_NATIVE_TIMING_LIMITS_ONLY','source_code_head':'df7a6eeae8a8e1a440f8d8e35d84a17a20296290','operation':receipt,'canonical_consumed':True,'argv_sha256_independently_recomputed':True,'source_before_after_contract_current_files_exact':616,'guard_and_inherited_driver_match_QA02':True,'initial_contract_and_Lead_pins_match_final_validation':pins,'hardware_equals_approved_contract':raw['hardware'],'actual_checks':74,'actual_context_kind_counts':counts,'actual_request_state_firstphysics_firstdraw_bindings':48,'actual_outgoing_Core_contacts':8,'actual_lethal_Core_contacts_and_restart_states':8,'independently_rederived_stats':rederived,'budgets':budgets,'video':{'frames':len(pts),'maximum_PTS_error_ms':max(errors),'ffprobe_argv':ffargv,'stream':video['streams'],'native_capture_paths_confined':True},'guard_tests_reused_from_immutable_QA02':{'cases':17,'pure_unit_tests':13,'decision_sha256':'3b1a2b8b83b510d49fa39c55cff1d735f029662d678fc53519350062671da7be'},'new_engine_runs_by_reviewer':0,'full_Readiness_campaign_hardware_latency_approval':False}
(O/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(O/'input-inventory.json').write_text(json.dumps({'schema':1,'inputs':refs},indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items()if k not in ['hardware_equals_approved_contract','initial_contract_and_Lead_pins_match_final_validation','independently_rederived_stats','actual_context_kind_counts','video']},ensure_ascii=False));print('newvideo',len(pts),max(errors))
