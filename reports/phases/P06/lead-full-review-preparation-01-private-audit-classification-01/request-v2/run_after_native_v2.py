#!/usr/bin/env python3
"""Read-only local reference/Git privacy audit. Run serially after native workload.
No engine, network, Git mutation, source edit, raw photo copy or publication.
"""
from pathlib import Path
import argparse,hashlib,json,os,re,subprocess,sys,time
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06'
MANIFEST_SHA='fa6f407946c3d4f60c526f22af142452c230874b725862dabf29fbf6ab1e8400'
AUDIT_CONTEXT={}
HELPERS={'tools/validate_pack.py':'7dc35e6be95705fcbfbc87d95796840b1fb39c2d5b69244a9b8d676dbd7bb384','tools/check_privacy.py':'5d4e99e05442a262cc4134a0090ad68c223d5c5ff3deb8903d4d0ed0be847380'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def git(cwd,*args):
 return subprocess.check_output(['git',*args],cwd=cwd,env=os.environ|{'GIT_OPTIONAL_LOCKS':'0'})
def common(cwd):
 p=Path(os.fsdecode(git(cwd,'rev-parse','--git-common-dir')).strip());return (cwd/p).resolve() if not p.is_absolute() else p.resolve()
def index(cwd):
 raw=git(cwd,'ls-files','--stage','-z');rows=[]
 for b in raw.split(b'\0'):
  if not b:continue
  head,path=b.split(b'\t',1);mode,oid,stage=head.split();rows.append({'mode':mode.decode(),'oid':oid.decode(),'stage':int(stage),'path':os.fsdecode(path)})
 return raw,rows
def forbidden(path):
 p=Path(path);return ('references' in p.parts or 'private' in p.parts or '.secrets' in p.parts or p.suffix.lower() in {'.zip','.pem','.key','.keystore'} or p.name=='.env' or p.name.startswith('.env.'))
def identity_blob(cwd,oid):
 # Read one object at a time without printing/copying its bytes. Extra Work index only.
 kind=git(cwd,'cat-file','-t',oid).strip();assert kind==b'blob','Unexpected index object type'
 p=subprocess.Popen(['git','cat-file','blob',oid],cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=os.environ|{'GIT_OPTIONAL_LOCKS':'0'});h=hashlib.sha256()
 for b in iter(lambda:p.stdout.read(1048576),b''):h.update(b)
 error=p.stderr.read();assert p.wait()==0,'Cannot read candidate object: '+error.decode(errors='replace')
 return h.hexdigest()
def main():
 a=argparse.ArgumentParser(description=__doc__);a.add_argument('--output',type=Path,required=True);opt=a.parse_args();out=opt.output.resolve()
 assert out.is_relative_to(R/'reports/phases/P06') and not out.is_symlink(),'Use fresh reviewer report output'
 assert not out.exists(),'Never overwrite previous audit'
 out.mkdir(parents=True);private=out/'private';private.mkdir();checks=[];details=[];commands=[]
 def check(name,ok):checks.append({'name':name,'passed':bool(ok)})
 started=time.monotonic();AUDIT_CONTEXT.update({'out':out,'private':private,'checks':checks,'details':details,'commands':commands,'started':started});refs_before=git(R,'for-each-ref','--format=%(refname) %(objectname)');ri,rrows=index(R);wi,wrows=index(W)
 manifest=R/'assets/references/manifest.json';check('pinned_local_private_manifest',sha(manifest)==MANIFEST_SHA);items=json.loads(manifest.read_text());check('eleven_reference_records',len(items)==11 and len({x['id'] for x in items})==11)
 assert all(c['passed'] for c in checks),'Private input manifest changed; review before scanning'
 seeds={x['sha256'] for x in items};assert all(re.fullmatch('[0-9a-f]{64}',h) for h in seeds)
 check('same_shared_Git_common_directory',common(R)==common(W))
 for rel,expected in HELPERS.items():check('pinned_ROOT_helper:'+rel,sha(R/rel)==expected)
 for folder,label in [(R,'ROOT'),(W,'WORK')]:
  for rel in ['assets/references/characters/yakuza_ref01.png','bundle.zip','.env','.env.local','.secrets/token','.tools/test','reports/phases/P06/private/test.png','debug.keystore','reports/phases/P06/isolated_saves/data/godot/keystores/debug.keystore']:
   result=subprocess.run(['git','check-ignore','--no-index','-q',rel],cwd=folder);check(label+':ignored:'+rel,result.returncode==0)
 for label,rows in [('ROOT',rrows),('WORK',wrows)]:
  bad=[x['path'] for x in rows if forbidden(x['path']) or x['stage']!=0];check(label+':no_sensitive_index_paths_or_conflicts',not bad)
  if bad:details.append({'class':'sensitive_index_path_or_unmerged_stage','index':label,'paths':bad})
 assert all(c['passed'] for c in checks),'Initial privacy/identity gate failed'
 # Existing validated helper covers ROOTmanifest11 + actualbytes, all shared reachable objects and ROOT index.
 for rel in ['tools/validate_pack.py','tools/check_privacy.py']:
  t=time.monotonic();argv=[sys.executable,str(R/rel)];p=subprocess.run(argv,cwd=R,capture_output=True,text=True,timeout=540);text=p.stdout+p.stderr;log=private/(Path(rel).stem+'.log');log.write_text(text+'\nexit_code='+str(p.returncode)+'\n');ok=p.returncode==0 and 'FAIL:' not in text
  commands.append({'name':Path(rel).stem,'argv':argv,'exit_code':p.returncode,'passed':ok,'seconds':time.monotonic()-t,'private_log_sha256':sha(log)})
  check('actual_ROOT:'+rel,ok)
 # Root helper does not see the other worktree's independently staged, unreachable index blobs.
 reachable={line.split(b' ',1)[0].decode() for line in git(R,'rev-list','--objects','--all').splitlines()};covered=reachable|{r['oid'] for r in rrows};extra={r['oid'] for r in wrows if r['oid'] not in covered}
 extra_matches=[]
 for oid in sorted(extra):
  if identity_blob(R,oid) in seeds:extra_matches.append(oid)
 check('WORK_extra_unreachable_index_raw_identity_absent',not extra_matches)
 if extra_matches:details.append({'class':'extra_WORK_index_raw_reference_identity','object_ids':extra_matches})
 # Validate current raw files again and never copy raw bytes into evidence.
 good=0
 for item in items:
  p=(R/item['path']).resolve();ok=p.is_relative_to((R/'assets/references').resolve()) and p.is_file() and sha(p)==item['sha256'];good+=bool(ok)
  if not ok:details.append({'class':'missing_or_changed_private_reference','id':item['id']})
 check('all_eleven_current_private_files_match_manifest',good==11)
 check('private_manifest_unchanged',sha(manifest)==MANIFEST_SHA)
 check('all_refs_unchanged_during_scan',refs_before==git(R,'for-each-ref','--format=%(refname) %(objectname)'))
 check('ROOT_index_unchanged_during_scan',ri==index(R)[0]);check('WORK_index_unchanged_during_scan',wi==index(W)[0])
 for rel,expected in HELPERS.items():check('helper_unchanged:'+rel,sha(R/rel)==expected)
 # Path-only/byte-identity scope, not arbitrary secret or transformed-photo recognition.
 result={'schema':1,'scope':'LOCAL_ROOT_PRIVATE11_AND_SHARED_GIT_RAW_IDENTITY_PRIVACY_ONLY','passed':all(x['passed'] for x in checks),'checks':checks,'commands':commands,'reference_manifest_sha256':MANIFEST_SHA,'reference_records':len(items),'validated_current_raw_files':good,'unique_declared_raw_SHA256':len(seeds),'raw_seed_set_sha256':hashlib.sha256('\n'.join(sorted(seeds)).encode()).hexdigest(),'shared_reachable_object_ids':len(reachable),'ROOT_index_entries':len(rrows),'WORK_index_entries':len(wrows),'additional_unreachable_WORK_index_objects_checked':len(extra),'additional_raw_identity_matches':len(extra_matches),'refs_snapshot_sha256':hashlib.sha256(refs_before).hexdigest(),'ROOT_HEAD':git(R,'rev-parse','HEAD').decode().strip(),'WORK_HEAD':git(W,'rev-parse','HEAD').decode().strip(),'seconds':time.monotonic()-started,'private_reference_or_raw_blob_bytes_copied':False,'private_helper_logs_not_for_public_copy':True,'not_proven':['Absence of transformed/re-encoded/cropped photos','Absence of every unlisted retired/private input','Absence of arbitrary renamed secrets by semantic inspection','Storefront/voice/public-release rights clearance','Embedded exported PCK content/privacy extraction'],'phase_approval':False,'publication_approval':False,'release_approval':False,'Game_or_Controller_or_Git_mutation':False}
 (private/'details.json').write_text(json.dumps(details,ensure_ascii=True,indent=2)+'\n');(out/'validation.json').write_text(json.dumps(result,ensure_ascii=True,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'references_validated':good,'checks':len(checks),'extra_index_objects':len(extra)}));return 0 if result['passed'] else 1
if __name__=='__main__':
 try:sys.exit(main())
 except Exception as e:
  # Preserve failed initial gates, without exposing private paths/bytes in public output.
  if AUDIT_CONTEXT:
   c=AUDIT_CONTEXT;out=c['out'];private=c['private']
   failure={'schema':1,'scope':'LOCAL_ROOT_PRIVATE11_AND_SHARED_GIT_RAW_IDENTITY_PRIVACY_ONLY','passed':False,'checks':c['checks'],'commands':c['commands'],'failure_class':type(e).__name__,'initial_or_runtime_guard_failed':True,'current_raw_identity_scan_completion':'NOT_PROVEN_CHECK_COMMANDS','seconds':time.monotonic()-c['started'],'phase_approval':False,'publication_approval':False,'release_approval':False,'private_reference_or_raw_blob_bytes_copied':False,'Game_or_Controller_or_Git_mutation':False}
   if not (out/'validation.json').exists():(out/'validation.json').write_text(json.dumps(failure,ensure_ascii=True,indent=2)+'\n')
   (private/'failure.json').write_text(json.dumps({'exception':type(e).__name__,'message':str(e),'details':c['details']},ensure_ascii=True,indent=2)+'\n')
  print('AUDIT_FAILED',type(e).__name__,str(e),file=sys.stderr);raise
