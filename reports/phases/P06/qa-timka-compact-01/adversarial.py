"""Independent temporary-project probes. Never invokes actual Timka adoption."""
from pathlib import Path
import sys,os,json,hashlib,copy,contextlib,io
from unittest.mock import patch
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;W=O.parents[3]/'.autopilot/worktrees/P06';sys.path.insert(0,str(W/'assets/source_art/characters'));sys.path.insert(0,str(O/'code-freeze/assets/source_art/characters'));import test_timka_supported as suite;import adopt_timka_supported as a;import compact_timka as c;suite.PROJECT=W
records=[];sha=c.sha

def invoke(t):
 try:
  with contextlib.redirect_stdout(io.StringIO()):a.adopt(t.kind,'supported_v1',str(t.review_path.relative_to(t.root)))
  return {'accepted':True,'error':None}
 except (ValueError,KeyError,TypeError,FileNotFoundError,OSError) as e:return {'accepted':False,'error':type(e).__name__+': '+str(e)}

def fixture(name,fn,kind='action'):
 t=suite.AdopterTests();t.setUp()
 try:
  t.fixture(kind);row={'name':name,'scope':'FAKE_REVIEW_AND_RUNTIME_ONLY_IN_TEMP_PROJECT'};row.update(fn(t));records.append(row)
 finally:t.doCleanups()

def rebound(t):t.rebind_modified_candidate_for_test()

def owner_profile(t):
 owner=t.root/t.manifest['source_compaction']['owner_decision'];d=json.loads(owner.read_text());d['profile']='UNAPPROVED_OTHER_LAYOUT';owner.write_text(json.dumps(d));t.manifest['source_compaction']['owner_decision_sha256']=sha(owner);rebound(t);before=t.runtime_snapshot();result=invoke(t);return result|{'owner_profile':d['profile'],'expected':'REJECT_OWNER_PROFILE_MISMATCH','runtime_changed':before!=t.runtime_snapshot()}
fixture('owner_profile_mismatch',owner_profile)

def stale_script(t):
 t.manifest['source_compaction']['script_sha256']='0'*64;rebound(t);result=invoke(t);return result|{'recorded_compactor_script_sha':'0'*64,'actual_compactor_script_sha':sha(t.root/t.manifest['source_compaction']['script']),'expected':'REJECT_FALSE_PROVENANCE_DIGEST'}
fixture('stale_provenance_script_digest',stale_script)

def stale_temp(t):
 p=t.target.with_suffix('.png.migrating');p.write_bytes(b'previous interrupted file, do not overwrite');before=t.runtime_snapshot();result=invoke(t);back=t.source/'runtime_before_supported_v1';return result|{'runtime_unchanged':before==t.runtime_snapshot(),'staging_unchanged':p.read_bytes()==b'previous interrupted file, do not overwrite','snapshots_created_before_staging_refusal':sorted(x.name for x in back.glob('*')),'retry':invoke(t),'expected':'REJECT_AND_PRESERVE_STAGING_RUNTIME'}
fixture('existing_staging_collision',stale_temp)

def interrupted(t):
 before=t.runtime_snapshot();replace=Path.replace
 def stop_json(path,target):
  if path==t.target_meta.with_suffix('.json.migrating'):raise OSError('QA simulated stop after PNG replacement before JSON replacement')
  return replace(path,target)
 with patch.object(Path,'replace',stop_json):first=invoke(t)
 png_new=t.target.read_bytes()==t.native.read_bytes();meta_old=t.target_meta.read_bytes()==before[str(t.target_meta.relative_to(t.root/'game'))];backup=t.source/'runtime_before_supported_v1';png_backup=(backup/t.target.name).read_bytes()==before[str(t.target.relative_to(t.root/'game'))];json_backup=(backup/t.target_meta.name).read_bytes()==before[str(t.target_meta.relative_to(t.root/'game'))];stage=t.target_meta.with_suffix('.json.migrating');stage_before=stage.read_bytes();snapshot={str(x.relative_to(t.root)):x.read_bytes() for x in t.root.rglob('*') if x.is_file()};retry=invoke(t);after={str(x.relative_to(t.root)):x.read_bytes() for x in t.root.rglob('*') if x.is_file()};assert not retry['accepted'] and snapshot==after and stage.read_bytes()==stage_before and png_backup and json_backup
 return {'first_call':first,'new_PNG_old_JSON_partial_pair':png_new and meta_old,'both_legacy_backups_byte_exact':png_backup and json_backup,'pending_json_preserved':True,'retry':retry,'retry_did_not_mutate_any_fixture_file':True,'expected':'FAIL_CLOSED_REQUIRES_EXPLICIT_MANUAL_RECONCILIATION_NO_AUTOMATIC_ROLLBACK'}
fixture('interrupt_between_png_and_json_replace',interrupted)

def backup_collision(t):
 b=t.source/'runtime_before_supported_v1';b.mkdir();p=b/t.target.name;p.write_bytes(b'immutable earlier snapshot');before={str(x.relative_to(t.root)):x.read_bytes() for x in t.root.rglob('*') if x.is_file()};result=invoke(t);after={str(x.relative_to(t.root)):x.read_bytes() for x in t.root.rglob('*') if x.is_file()};assert not result['accepted'] and before==after;return result|{'all_fixture_files_unchanged':True,'expected':'REJECT_PRESERVE_EXISTING_SNAPSHOT'}
fixture('existing_backup_collision',backup_collision)

def partial_legacy(t):
 t.target_meta.unlink();before=t.runtime_snapshot();result=invoke(t);assert not result['accepted'] and before==t.runtime_snapshot();return result|{'runtime_unchanged':True,'expected':'REJECT_PARTIAL_OLD_RUNTIME'}
fixture('partial_legacy_pair',partial_legacy)

(O/'adversarial-results.json').write_text(json.dumps({'schema':1,'actual_ART_review_or_adoption':False,'records':records},indent=2)+'\n');print(json.dumps(records,indent=2))
