from pathlib import Path
import json,hashlib,subprocess,re
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P07';O=Path(__file__).resolve().parent;OLD=R/'reports/pre_p07/qa-bonus-pilot-01'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
refs=[]
def keep(p,name):
 q=O/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes());refs.append({'origin':str(p.relative_to(R)),'copy':name,'sha256':h(p),'bytes':p.stat().st_size})
# Bind both historical core and final fixture explicitly, not a fictional full rerun at final HEAD.
for rev,dest in [('3a3645e8c74e74520f37c2085b58ccc560091961','core-source3a'),('c4b9b4ea473e11e14b88a820374e442bff5615d7','final-source')]:
 for n in ['tools/fixtures/p07_bonus_progress.gd','tools/fixtures/p07_bonus_contract.gd','tools/fixtures/p07_bonus_host.gd','tools/p07_bonus_pilot.py']:
  b=subprocess.check_output(['git','show',rev+':'+n],cwd=W);q=O/dest/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(b)
assert h(O/'core-source3a/tools/fixtures/p07_bonus_progress.gd')==h(O/'final-source/tools/fixtures/p07_bonus_progress.gd')=='d4656c3cf5bd03a7baa3df82331e05ad96b14825607143fcd9633aea758dff22'
summary={}
for dirname,expected in [('bonus-compatibility-06',{'checks':98,'prepare':1,'recover_before':3,'recover_after':3}),('bonus-goal-fixture-01',{'goals':8})]:
 d=W/'reports/pre_p07'/dirname;v=j(d/'validation.json');a=j(d/'source_before.json');b=j(d/'source_after.json');assert v['passed']is True and a==b and len(a)==620
 if dirname=='bonus-goal-fixture-01':
  for n,digest in a.items():assert h(W/n)==digest,n
  assert v['focused_goal_fixture_probe_only']is True
 else:assert len(v['runs'])==10
 for run in v['runs']:
  p=d/(run['name']+'.log');assert h(p)==run['log_sha256']and run['passed']is True
  if run['name']in['before_rename','after_rename']:
   assert run['exit_code']==-9 and(d/(run['name']+'-boundary.txt')).read_text()==run['name']and not(d/(run['name']+'-result.json')).exists()
  else:assert run['exit_code']==0 and not any(x in p.read_text()for x in ['SCRIPT ERROR:','Parse Error:','ERROR:'])
 for name,count in expected.items():
  x=j(d/(name+'-result.json'));cs=x['checks'];assert len(cs)==count==x['passed']and x['failed']==0 and len({v['check']for v in cs})==count and all(v['passed']is True for v in cs)
 for p in d.iterdir():
  if p.is_file()and p.suffix in ['.json','.log','.txt']:keep(p,'actual-evidence/'+dirname+'/'+p.name)
 summary[dirname]={'source_count':620,'before_after_exact':True,'stage_exit_codes':{x['name']:x['exit_code']for x in v['runs']},'typed_counts_recomputed':expected}
# Full core to final source delta: exactly goal getter/driver and focused runner option.
base=j(W/'reports/pre_p07/bonus-compatibility-06/source_before.json');final=j(W/'reports/pre_p07/bonus-goal-fixture-01/source_before.json');changed=sorted(n for n in final if final[n]!=base[n]);assert changed==['tools/fixtures/p07_bonus_contract.gd','tools/fixtures/p07_bonus_host.gd','tools/p07_bonus_pilot.py']
for n in base:
 if n not in changed:assert base[n]==final[n]
# All production Game inputs are still the pre-bonus actual H04 inputs.
pre=j(R/'reports/pre_p07/qa-pacing-acceptance-01/actual-evidence/source_before.json');game=[n for n in pre if n.startswith('game/')];assert all(final[n]==pre[n]for n in game)
# Preserve exact old independent probe: changed only implementation, not its assertions.
D=W/'reports/pre_p07/bonus-namespace-witness-02';old=j(OLD/'namespace-witness/witness.json');fixed=j(D/'witness.json');assert h(D/'namespace_alias_probe.gd')=='3bc7f8978c2ec9c1ca5b98cd22e0f0dfa1fe4988c309db574e1cc81a0596aa24'
for oldrow,row in zip(old['rows'],fixed['rows']):
 assert oldrow['case']==row['case']and oldrow['main_before_utf8']==row['main_before_utf8']
 assert row['began']is False and row['committed']is False and row['main_exists_after']is True and row['main_bytes_preserved']is True and row['main_valid_after']is True
 assert row['main_before_utf8']==row['main_after_utf8']and j(Path(row['main_path']))['domain']=='campaign'
for f in ['p07_bonus_progress.gd','p07_bonus_contract.gd','p07_bonus_host.gd']:assert(D/'isolated_project/game/tests'/f).read_bytes()==(O/'core-source3a/tools/fixtures'/f).read_bytes()
for p in D.iterdir():
 if p.is_file():keep(p,'actual-evidence/namespace-witness-fixed/'+p.name)
operations=[]
for op in ['df473ff47e2946b29d50ff1237805ace','967cd3206eb943b98a2ba2208e33e52b','a625621894894a618db1853f02baebe8']:
 d=R/'.autopilot/jobs'/op;inp=j(d/'input.json');receipt=j(d/'receipt.json');assert receipt['exit_code']==0 and receipt['argv_sha256']==inp['argv_sha256']==hashlib.sha256(json.dumps(inp['argv']).encode()).hexdigest()and receipt['log_sha256']==h(d/'output.log')
 operations.append(receipt)
 for n in ['input.json','receipt.json','output.log']:keep(d/n,'actual-evidence/operations/'+op+'/'+n)
# Independent physical evidence of namespace guard and ordinary once state.
P=W/'reports/pre_p07/bonus-compatibility-06/profile_evidence'
for n in ['A/story_v2.json','A/bonus_progress_v1.json','crash/story_v2.json','crash/bonus_progress_v1.json','main_is_tmp/bonus_progress_v1.json.tmp','main_is_final/bonus_progress_v1.json','main_created_after_candidate/bonus_progress_v1.json']:
 p=P/n;x=j(p)
 if n.endswith('story_v2.json')or n.startswith('main_'):assert x['schema']==2 and x['domain']=='campaign'
 else:assert x['schema']==1 and x['domain']=='bonus_profile'and len(x['history'])==2 and len(set(x['history']))==2 and all(x['completed'].values())
 keep(p,'actual-evidence/selected-profile-files/'+n)
# Parse actual old-story counts rather than trusting a wrapper boolean.
D=W/'reports/pre_p07/bonus-compatibility-06';counts={}
for name,count in [('story_state',40),('story_graph',662778),('story_integration',11)]:
 text=(D/(name+'.log')).read_text();assert re.search(r'checks='+str(count)+r'\b',text)and'failures=0'in text;counts[name]=count
assert'paths=6344'in(D/'story_graph.log').read_text()
audit={'schema':1,'scope':'ISOLATED_H05_CORE_PILOT_CLOSURE_NOT_LIVE_INTEGRATION','core_source_head':'3a3645e8c74e74520f37c2085b58ccc560091961','final_fixture_head':'c4b9b4ea473e11e14b88a820374e442bff5615d7','Progress_core_sha256':'d4656c3cf5bd03a7baa3df82331e05ad96b14825607143fcd9633aea758dff22','Progress_core_identical':True,'final_source_changes_only':changed,'current_physical_source_pins_verified':620,'production_Game_source_pins_unchanged':len(game),'actual_runs':summary,'exact_independent_probe_before_after_verified':True,'namespace_fixed_cases':[{k:v for k,v in x.items()if'utf8'not in k}for x in fixed['rows']],'old_story_checks':counts,'old_story_graph_scenario_paths':6344,'actual_canonical_receipts':operations,'normal98_not_rerun_at_final_fixture_head':True,'engine_runs_by_reviewer':0,'real_current_campaign_positive_bonus_unlock':False,'all_BP01_to_BP09_closed':False,'full_Readiness_P07_phase_approval':False}
(O/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n');(O/'input-inventory.json').write_text(json.dumps({'schema':1,'inputs':refs},indent=2)+'\n');print(json.dumps({k:v for k,v in audit.items()if k not in ['actual_canonical_receipts','namespace_fixed_cases']},ensure_ascii=False))
