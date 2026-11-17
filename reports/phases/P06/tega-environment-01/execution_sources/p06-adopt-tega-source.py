from pathlib import Path
import json,hashlib,shutil,sys,csv
r=Path.cwd();w=r/'.autopilot/worktrees/P06';kind=sys.argv[1];assert kind in ['action','finisher'];expected=sys.argv[2];version=sys.argv[3];d=r/'.tools/art-pending/tega'/f'{kind}-v1';review=r/'reports/phases/P06/art-preflight'/f'tega_{kind}_{version}_source.json';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();j=json.loads(review.read_text());assert sha(review)==expected;assert j['source_only_acceptance'] is True and j['all32_freshly_reviewed'] is True and not j['must_fix'];src=d/'preview-project/assets/source_art/characters/tega';dst=w/'assets/source_art/characters/tega';runtime=w/'game/assets/art/characters/tega';mp=src/f'{kind}_manifest_{version}.json';m=json.loads(mp.read_text());assert sha(src/f'{kind}_native_{version}.png')==j['native_sha256'];assert sha(d/f'{kind}_master_{version}.png')==j['master_sha256'];assert sha(mp)==j['manifest_sha256']
for p in d.iterdir():
 if not p.is_file():continue
 name=p.name if p.name.startswith(kind+'_') else kind+'_v1_'+p.name
 q=dst/name;assert not q.exists(),name;shutil.copyfile(p,q)
for fn in [f'{kind}_native_{version}.png',f'{kind}_manifest_{version}.json',f'{kind}_inspection_{version}_3x.png']:
 assert not (dst/fn).exists();shutil.copyfile(src/fn,dst/fn)
manifest=review.with_name(f'tega_{kind}_{version}_transfer_manifest.json');files=json.loads(manifest.read_text())['files']
for fn,h in files.items():
 h=h['sha256'] if isinstance(h,dict) else h;p=manifest.parent/fn;assert sha(p)==h;q=w/'reports/phases/P06/art-preflight'/fn;assert not q.exists();shutil.copyfile(p,q)
shutil.copyfile(manifest,w/'reports/phases/P06/art-preflight'/manifest.name)
assert not (runtime/f'{kind}_sheet.png').exists();assert not (runtime/f'{kind}.json').exists();shutil.copyfile(src/f'{kind}_native_{version}.png',runtime/f'{kind}_sheet.png');m.update(file=f'{kind}_sheet.png',status='SOURCE_ACCEPTED_REQUIRES_ACTUAL_ANIMATION_AND_GAMEPLAY',source_review_sha256=sha(review));(runtime/f'{kind}.json').write_text(json.dumps(m,indent=2)+'\n')
(dst/f'{kind}_{version}_adoption.json').write_text(json.dumps({'source_review_sha256':sha(review),'native_sha256':j['native_sha256'],'runtime_layout_sha256':sha(runtime/f'{kind}.json'),'source_only_approval':True,'runtime_approval':False,'phase_approval':False,'note':'Exact independently accepted native bytes; original generation/failedraw/normalization reports preserved; no ability granted'},indent=2)+'\n')
with (w/'licenses/ASSET_LICENSES.csv').open('a') as f:csv.writer(f).writerow([f'p06_tega_{kind}_{version}','pixel_actor_atlas','Codex built-in image_gen; own generated art references; complete-figure NN normalization and whole-cell packing',f'local:assets/source_art/characters/tega/{kind}_v1_generation.json','Original AI-assisted project art; owner-authorized public repository; no new photos uploaded','NO_THIRD_PARTY_MEDIA','UNVERIFIED_FOR_COMMERCIAL_RELEASE','PUBLIC_PROJECT_REPOSITORY_AUTHORIZED;RAW_PHOTOS_EXCLUDED',f'reports/phases/P06/art-preflight/tega_{kind}_v1a_source.json','INDEPENDENT_SOURCE_ART_ACCEPTED;RUNTIME_AND_PHASE_PENDING'])
print('Exact independently source-accepted',kind,'adopted; not runtime/phase acceptance')

if kind=='action':
 extra=r/'.tools/art-pending/tega/action-left-fire-v2'
 for p in extra.iterdir():
  if p.is_file():
   q=dst/('action_left_fire_v2_'+p.name);assert not q.exists();shutil.copyfile(p,q)
