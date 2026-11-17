"""Independent v1 reproductions plus new v2 guard branches; fake TempDir only."""
from pathlib import Path
import sys,json,contextlib,io,shutil
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;W=O.parents[3]/'.autopilot/worktrees/P06';sys.path.insert(0,str(W/'assets/source_art/characters'));sys.path.insert(0,str(O/'code-freeze/assets/source_art/characters'));import test_timka_supported as suite;import adopt_timka_supported as a;import compact_timka as c;suite.PROJECT=W
records=[]
def snapshot(root):return {str(p.relative_to(root)):c.sha(p) for p in root.rglob('*') if p.is_file()}
def owner_change(t,key,value):
 owner=t.root/t.manifest['source_compaction']['owner_decision'];data=json.loads(owner.read_text());data[key]=value;owner.write_text(json.dumps(data));t.manifest['source_compaction']['owner_decision_sha256']=c.sha(owner);t.rebind_modified_candidate_for_test()
def bad_digest(t):t.manifest['source_compaction']['script_sha256']='0'*64;t.rebind_modified_candidate_for_test()
def bad_script_path(t):
 old=t.root/t.manifest['source_compaction']['script'];new=old.with_name('OTHER_compact_timka.py');shutil.copyfile(old,new);t.manifest['source_compaction']['script']=str(new.relative_to(t.root));t.review['source_inventory_sha256'][str(new.relative_to(t.root))]=c.sha(new);t.rebind_modified_candidate_for_test()
cases=[('TC-C01_original_wrong_owner_profile',lambda t:owner_change(t,'profile','UNAPPROVED_OTHER_LAYOUT')),('TC-C02_original_zero_recorded_script_digest',bad_digest),('wrong_compactor_canonical_path_same_bytes',bad_script_path),('wrong_owner_kind',lambda t:owner_change(t,'kind','OTHER_APPROVAL')),('wrong_owner_phase',lambda t:owner_change(t,'phase','P07')),('wrong_owner_total84_float',lambda t:owner_change(t,'total_source_cells',84.0)),('wrong_owner_budget_float',lambda t:owner_change(t,'source_cells',{'world':32,'action':28.0,'finisher':24})),('wrong_owner_excluded_scope',lambda t:owner_change(t,'excluded',['fire'])),('wrong_owner_phase_approval',lambda t:owner_change(t,'phase_approval',True)),('wrong_owner_merge_approval',lambda t:owner_change(t,'merge_approval',True))]
for name,mutate in cases:
 t=suite.AdopterTests();t.setUp()
 try:
  t.fixture();mutate(t);before=snapshot(t.root);error=None
  try:
   with contextlib.redirect_stdout(io.StringIO()):a.adopt(t.kind,'supported_v1',str(t.review_path.relative_to(t.root)))
  except (ValueError,KeyError,TypeError,FileNotFoundError) as e:error=type(e).__name__+': '+str(e)
  after=snapshot(t.root);row={'name':name,'accepted':error is None,'error':error,'all_fixture_files_unchanged_after_refusal':before==after,'passed':error is not None and before==after,'scope':'FAKE_REVIEW_TEMP_ONLY_NOT_ART_APPROVAL'};records.append(row);assert row['passed'],row
 finally:t.doCleanups()
(O/'adversarial-results.json').write_text(json.dumps({'schema':1,'actual_implementation_sha256':c.sha(Path(a.__file__)),'actual_ART_or_production_adoption':False,'cases':records,'passed':all(r['passed'] for r in records)},indent=2)+'\n');print(json.dumps(records,indent=2))
