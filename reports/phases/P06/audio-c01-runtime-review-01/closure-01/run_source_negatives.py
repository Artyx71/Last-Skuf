"""Independent offline/temp source-binding negatives. No engine, WORK mutations or network."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,tempfile,wave
Q=Path(__file__).resolve().parent
BASE=Q/'source-binding-fixture'
OUT=Q/'source-negative-results.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def jread(root,path):return json.loads((root/path).read_text())
def jwrite(root,path,value):(root/path).write_text(json.dumps(value,indent=2)+'\n')
M='game/assets/audio/character_finishers.json';A='assets/source_audio/character_finishers/adoption.json';C='finish_gabar_unarmed';W=C+'.wav'
SOURCE='assets/source_audio/character_finishers/'+W;RUNTIME='game/assets/audio/character_finishers/'+W
spec=importlib.util.spec_from_file_location('frozen_c01_verifier',Q/'source/tools/verify_character_finisher_audio.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def rebind(root):
 a=jread(root,A);a['runtime_manifest_sha256']=sha(root/M);jwrite(root,A,a)
def manifest_edit(root,fn):
 m=jread(root,M);fn(m);jwrite(root,M,m);rebind(root)
def entry(root,field,value):manifest_edit(root,lambda m:m['sfx'][C].__setitem__(field,value))
def replace_wave(root,paths):
 data=(root/'game/assets/audio/character_finishers/finish_pasha_unarmed.wav').read_bytes()
 for path in paths:(root/path).write_bytes(data)
def coherent_replace(root):
 replace_wave(root,[SOURCE,RUNTIME]);entry(root,'source_sha256',sha(root/RUNTIME))
def collision(root,path):
 data=jread(root,path);data['sfx'][C]={'path':'res://assets/audio/combat_polish/finish_unarmed.wav','bus':'SFX','gain_db':0.0};jwrite(root,path,data)
def wave_payload_change(root):
 for path in [SOURCE,RUNTIME]:
  b=bytearray((root/path).read_bytes());b[-100]^=1;(root/path).write_bytes(b)
 entry(root,'source_sha256',sha(root/RUNTIME))
cases=[('control',lambda r:None,True),
 ('runtime_other_valid_WAV',lambda r:replace_wave(r,[RUNTIME]),False),
 ('source_other_valid_WAV',lambda r:replace_wave(r,[SOURCE]),False),
 ('coherent_source_runtime_manifest_adoption_rebind',coherent_replace,False),
 ('coherent_one_PCM_payload_bit_rebind',wave_payload_change,False),
 ('wrong_entry_SHA',lambda r:entry(r,'source_sha256','0'*64),False),
 ('empty_entry_SHA',lambda r:entry(r,'source_sha256',''),False),
 ('missing_entry_SHA',lambda r:manifest_edit(r,lambda m:m['sfx'][C].pop('source_sha256')),False),
 ('wrong_decision_binding',lambda r:manifest_edit(r,lambda m:m.__setitem__('source_signal_decision_sha256','0'*64)),False),
 ('missing_decision_binding',lambda r:manifest_edit(r,lambda m:m.pop('source_signal_decision_sha256')),False),
 ('wrong_recipe_binding',lambda r:manifest_edit(r,lambda m:m.__setitem__('source_recipe_sha256','0'*64)),False),
 ('recipe_bytes_changed',lambda r:(r/'assets/source_audio/character_finishers/render.py').write_text('# substituted\n'),False),
 ('provenance_bytes_changed',lambda r:(r/'assets/source_audio/character_finishers/provenance.json').write_text('{}\n'),False),
 ('base_registry_collision',lambda r:collision(r,'game/assets/audio/manifest.json'),False),
 ('polish_registry_collision',lambda r:collision(r,'game/assets/audio/combat_polish.json'),False),
 ('wrong_actor',lambda r:entry(r,'actor_id','pasha'),False),
 ('wrong_context',lambda r:entry(r,'context','athletic_prime'),False),
 ('wrong_category',lambda r:entry(r,'category','blunt'),False),
 ('wrong_bus',lambda r:entry(r,'bus','Music'),False),
 ('bool_gain',lambda r:entry(r,'gain_db',True),False),
 ('NaN_gain',lambda r:entry(r,'gain_db',float('nan')),False),
 ('Inf_gain',lambda r:entry(r,'gain_db',float('inf')),False),
 ('too_loud_gain',lambda r:entry(r,'gain_db',1.0),False),
 ('missing_cue',lambda r:manifest_edit(r,lambda m:m['sfx'].pop(C)),False),
 ('extra_forbidden_timka_firearm',lambda r:manifest_edit(r,lambda m:m['sfx'].__setitem__('finish_timka_prime_firearm',m['sfx'][C])),False),
 ('schema_bool',lambda r:manifest_edit(r,lambda m:m.__setitem__('schema',True)),False),
 ('schema_float',lambda r:manifest_edit(r,lambda m:m.__setitem__('schema',1.0)),False),
 ('catalog_changed',lambda r:(r/'game/resources/characters/catalog.json').write_text('{}\n'),False),
 ('independent_decision_tampered',lambda r:(r/'reports/phases/P06/audio-c01-signal-review-01/decision.json').write_text('{}\n'),False),
 ('independent_freeze_tampered',lambda r:(r/'reports/phases/P06/audio-c01-signal-review-01/input-freeze.json').write_text('{}\n'),False),
 ('legacy_WAV_changed',lambda r:(r/'game/assets/audio/combat_polish/finish_unarmed.wav').write_bytes(b'not the reviewed legacy'),False),
 ('adoption_manifest_stale',lambda r:jwrite(r,A,{'source_signal_decision_sha256':module.SIGNAL_SHA,'runtime_manifest_sha256':'0'*64}),False),
 ('adoption_decision_stale',lambda r:jwrite(r,A,{'source_signal_decision_sha256':'0'*64,'runtime_manifest_sha256':sha(r/M)}),False)]
assert not OUT.exists(),'Preserve immutable first results; use new folder for rerun'
before={str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*') if p.is_file()}
results=[]
for label,mutate,expected in cases:
 with tempfile.TemporaryDirectory(prefix='c01-source-qa-',dir=Q) as tmp:
  root=Path(tmp)/'fixture';shutil.copytree(BASE,root);mutate(root)
  checks=module.verify(root);actual=bool(checks) and all(x['passed'] for x in checks)
  assert actual==expected,(label,actual,expected,checks)
  results.append({'label':label,'expected_accepted':expected,'actual_accepted':actual,'passed':actual==expected,'checks':checks})
after={str(p.relative_to(BASE)):sha(p) for p in BASE.rglob('*') if p.is_file()};assert before==after
result={'scope':'INDEPENDENT_TEMP_FIXTURE_SOURCE_BINDING_ONLY_NOT_RUNTIME','verifier_sha256':sha(Q/'source/tools/verify_character_finisher_audio.py'),'cases':results,'case_count':len(results),'all_expected_outcomes':True,'source_fixture_unchanged':True,'Godot_executed':False,'WORK_mutations':False,'actual_listening':False}
OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'cases':len(results),'PASS':True,'control_checks':len(results[0]['checks']),'negative_denials':len(results)-1,'source_fixture_unchanged':True}))
