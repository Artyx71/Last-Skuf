"""Independent read-only filesystem/blob-identity audit; no Git/engine/Controller imports."""
from pathlib import Path
import hashlib,json,os,stat,shutil,wave
O=Path(__file__).resolve().parent;R=O.parents[2];W=R/'.autopilot/worktrees/P07'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def copy(p,rel):
 q=O/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
def production(root):
 result={}
 for directory,dirs,files in os.walk(root/'game',followlinks=False):
  dirs[:]=[d for d in dirs if d not in ['.godot','__pycache__']]
  for name in dirs+files:assert not (Path(directory)/name).is_symlink()
  for name in files:
   p=Path(directory)/name;result[str(p.relative_to(root))]=h(p)
 return result
catalog_path=R/'reports/pre_p07/canonical-source-actual-C-01/plan.json';plan=load(catalog_path)
assert plan['target_git']=='f8325212381d67a469b5d9a6dffbf3d244bc9933'
rootgame=production(R);workgame=production(W);expected={p:e for p,e in plan['target_catalog'].items() if p.startswith('game/')}
assert set(rootgame)==set(expected) and len(rootgame)==533
for rel,row in expected.items():
 p=R/rel;b=p.read_bytes();assert rootgame[rel]==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['blob']
 assert bool(p.stat().st_mode&0o111)==(row['mode']=='100755')
bundle_path=R/'reports/pre_p07/readiness-submission-03/runtime-bundle.json';bundle=load(bundle_path)
changed={p:s for p,s in workgame.items() if rootgame.get(p)!=s}
assert changed==bundle['changed_Game_files'] and len(changed)==9
assert not set(rootgame)-set(workgame) and len(workgame)==536
for rel,sha in changed.items():
 p=R/'reports/pre_p07/readiness-submission-03/frozen-work-runtime'/rel;assert h(p)==sha
 copy(p,'frozen-work-runtime/'+rel)
# Main21 full design authority: verify its complete immutable input inventory and unique chapter mapping.
mds_path=R/'reports/pre_p07/lead-mds-global21-01/decision.json';mds=load(mds_path)
assert h(mds_path)=='c8123ab206fcb78fa8b80a82ece68af51b28fdde467b9946ba32e5e3326951d2'
assert mds['status']=='PASS' and mds['acceptance_level']=='FULL' and mds['must_fix']==[]
for rel,sha in mds['source_inventory_sha256'].items():assert h(R/rel)==sha,rel
assert len(mds['mission_specs'])==21 and len({v['sha256'] for v in mds['mission_specs'].values()})==21
ids={c['id'] for c in load(R/'game/resources/story/registry.json')['chapters']};assert ids==set(mds['mission_specs'])
# Installed guard source matches independent component and actual-install baselines.
guard=load(R/'reports/pre_p07/lead-production-guard-03/decision.json')['reviewed_source_inventory_sha256']
for rel in ['autopilot/readiness.py','autopilot/github.py','autopilot/review_schema.json','autopilot/prompts/INDEPENDENT_REVIEW.md','autopilot/PRODUCTION_GATES.md','tools/tests/test_production_readiness.py']:
 assert h(R/rel)==guard[rel],rel
baseline=load(R/'reports/pre_p07/lead-canonical-source-C-installed-01/post-C-runtime-baseline.json')
# Recheck the canonical installed tools against the same Git catalog, not just the game.
tools_expected={p:e for p,e in plan['target_catalog'].items() if p.startswith('tools/')}
for rel,row in tools_expected.items():
 b=(R/rel).read_bytes();assert h(R/rel)==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['blob']
for rel,row in baseline['runtime_files'].items():
 if rel!='autopilot/config.json':
  p=R/rel;st=p.stat();assert h(p)==row['sha256']
  assert stat.S_IMODE(st.st_mode)==row['mode'] and st.st_uid==row['uid'] and st.st_gid==row['gid']
# Compare only immutable code, never pin active configuration/state.
code=['autopilot/readiness.py','autopilot/github.py','autopilot/runner.py','autopilot/worker.py','autopilot/review_schema.json','autopilot/prompts/INDEPENDENT_REVIEW.md','autopilot/PRODUCTION_GATES.md','tools/verify.py','tools/verify_p06.py','tools/tests/test_production_readiness.py']
for rel in code:copy(R/rel,'installed-control-source/'+rel)
fence=load(R/'reports/pre_p07/qa-runtime-fence-02/decision.json');assert h(R/'autopilot/runner.py')==fence['runner_sha256']
# Actual inventory/media continuity from the independently reviewed existing audio pipeline.
audio=load(R/'reports/pre_p07/audio-pipeline-readiness-audit-01/P06-current-byte-comparison.json');arows=[]
for row in audio['files']:
 p=W/row['path'];assert h(p)==row['P06_sha256']==row['reviewed_P06_sha256']
 b=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['P06_git_blob']
 if p.suffix.lower()=='.wav':
  with wave.open(str(p)) as wav:arows.append({'path':row['path'],'channels':wav.getnchannels(),'sample_width':wav.getsampwidth(),'sample_rate':wav.getframerate(),'frames':wav.getnframes()})
# Explicit observation only: active state/config are not final decision input pins.
state=load(R/'automation/phase_state.json');cfg=load(R/'autopilot/config.json');p06=state['autopilot']['phases']['P06'];p07=state['autopilot']['phases']['P07']
assert p06['status']=='PASS' and p06['merge']['status']=='MERGED' and p06['merge']['merge_sha']==plan['target_git']
assert p07['attempts']==0 and cfg['stop_after_phase']=='P06'
assert 'readiness' not in state['autopilot']['production_gates']
write(O/'root-game-inventory.json',rootgame)
write(O/'own-source-verification.json',{'schema':1,'method':'Whole filesystem inventory; current SHA256 and Git blob SHA1 recomputed against independently validated frozen f832 catalog; no Git process','root_Game':len(rootgame),'root_Game_exact_f832':True,'root_Game_no_extra_missing_or_symlink':True,'Git_catalog_path':str(catalog_path.relative_to(R)),'Git_catalog_sha256':h(catalog_path),'work_Game':len(workgame),'changed_or_added_Work_Game':changed,'unchanged_Work_vs_ROOT_files':len(rootgame)-sum(p in rootgame for p in changed),'complete_delta_is_frozen9':True,'all21_main_design_exact':True,'main_MDS_inventory_keys_rehashed':len(mds['source_inventory_sha256']),'installed_guard_test_pins_match':True,'canonical_tools_Git_blobs_verified':len(tools_expected),'post_C_runtime_code_mode_owner_verified':True,'guard_code_sha256':{p:h(R/p) for p in code},'audio_sources_rehashed':len(audio['files']),'audio_WAV_headers_read':len(arows),'actual_reviewer_engine_Controller_Git_network_calls':0,'source_or_state_mutations':False})
write(O/'audio-header-observation.json',{'schema':1,'existing_source_only':True,'hearing_performed':False,'WAVs':arows})
write(O/'authority-observation-not-live-input.json',{'schema':1,'kind':'READ_ONLY_BOOKKEEPING_OBSERVATION_NOT_SOURCE_INVENTORY_TARGET','P06':p06,'P07_status':p07['status'],'P07_formal_attempts':p07['attempts'],'legacy_attempts':state.get('attempts'),'stop_after_phase':cfg['stop_after_phase'],'production_gate_names':sorted(state['autopilot']['production_gates']),'live_state_and_config_not_pinned':True})
copy(bundle_path,'submission-snapshot/runtime-bundle.json');copy(R/'reports/pre_p07/readiness-submission-03/INPUTS.DRAFT.json','submission-snapshot/INPUTS.DRAFT.json');copy(R/'reports/pre_p07/readiness-submission-03/DOMAINS_AUTHOR.md','submission-snapshot/DOMAINS_AUTHOR.md')
print(json.dumps({'root533':len(rootgame),'work536':len(workgame),'delta9':len(changed),'MDS_inventory':len(mds['source_inventory_sha256']),'audio_sources':len(audio['files']),'WAVheaders':len(arows),'all_passed':True}))
