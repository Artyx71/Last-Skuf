"""TEST_ONLY export-metadata unit fixture: every export/smoke subprocess mocked."""
from pathlib import Path
import sys,runpy,json,hashlib,contextlib,io,shutil
from unittest.mock import patch
from types import SimpleNamespace
Q=Path(__file__).resolve().parent;sys.path.insert(0,str(Q/'isolated-project/tools'));mod=runpy.run_path(str(Q/'code-freeze/tools/export_p06_preview.py'),run_name='qa_frozen_export_metadata');G=mod['main'].__globals__;fixture=Q/'TEST_ONLY-metadata-fixture';(fixture/'tools').mkdir(parents=True);shutil.copyfile(Q/'isolated-project/tools/toolchain.lock.json',fixture/'tools/toolchain.lock.json');engine=json.loads((Q/'engine-copy.json').read_text());G['ROOT']=fixture;G['GODOT']=Q/engine['path'];G['sources']=lambda:{'TEST_ONLY_metadata_scope':'source_provenance_not_under_test'}
names={'gabar_training':['Gabar_actual_complete_body_loaded','Gabar_ability_Input_starts'],'olezhka_training':['Oleg_selection_actual_complete_body','Oleg_ability_Input_starts'],'timka_present':['present_Timka_selects_own_context_and_body','present_disengage_starts_from_Input','present_disengage_moves_without_prime_damage'],'timka_prime':['prime_Timka_selects_separate_body_contract','prime_cannot_grab_without_vulnerable_target'],'ryzhik_training':['Ryzhik_selects_complete_own_roll_body','Ryzhik_roll_starts_from_Input','Ryzhik_roll_moves_with_live_collision']};results=[]
for case in ['both_platforms_complete','windows_missing_ryzhik_check','windows_smoke_fails']:
 out=fixture/'reports'/case;build=fixture/'build'/case;captured=[]
 def fake_run(argv,**kw):
  argv=list(map(str,argv));captured.append(argv)
  if '--export-release' in argv:
   path=Path(argv[-1]);path.write_bytes((b'MZ' if path.suffix=='.exe' else b'\x7fELF')+b'TEST_ONLY_NOT_A_REAL_BUILD');return SimpleNamespace(returncode=0,stdout='TEST_ONLY mocked export\n',stderr='')
  windows='wine' in Path(argv[0]).name
  if windows and case=='windows_smoke_fails':return SimpleNamespace(returncode=9,stdout='TEST_ONLY controlled smoke failure\n',stderr='')
  dest=kw['env']['AYAY_OWNER_PREVIEW_SMOKE_OUTPUT'];dest=dest[2:].replace('\\','/') if dest.startswith('Z:') else dest;dest=Path(dest);dest.mkdir(parents=True,exist_ok=True)
  checks=[{'name':name,'passed':True} for group in names.values() for name in group]
  if windows and case=='windows_missing_ryzhik_check':checks=[c for c in checks if c['name']!='Ryzhik_roll_moves_with_live_collision']
  (dest/'result.json').write_text(json.dumps({'passed':True,'checks':checks,'scope':'TEST_ONLY_METADATA_UNIT_FIXTURE'}));return SimpleNamespace(returncode=0,stdout='TEST_ONLY mocked smoke\n',stderr='')
 text=io.StringIO()
 with patch.object(sys,'argv',['tools/export_p06_preview.py','--output',str(out.relative_to(fixture)),'--build-output',str(build.relative_to(fixture))]),patch.object(G['subprocess'],'run',side_effect=fake_run),patch.object(G['subprocess'],'check_output',return_value='TEST_ONLY_frozen_source\n'),contextlib.redirect_stdout(text):
  status=G['main']()
 report=json.loads((out/'preview.json').read_text());expected=sorted(names) if case=='both_platforms_complete' else (sorted(set(names)-{'ryzhik_training'}) if case=='windows_missing_ryzhik_check' else [])
 assert report['available_combat_fixtures']==expected
 assert report['available_combat_heroes']==sorted({s.split('_',1)[0] for s in expected})
 assert report['passed']==(case!='windows_smoke_fails') and bool(status)==(case=='windows_smoke_fails')
 results.append({'case':case,'actual_main_return':status,'actual_available_fixtures':report['available_combat_fixtures'],'actual_available_heroes':report['available_combat_heroes'],'per_platform_fixtures':[e.get('verified_combat_fixtures',[]) for e in report['exports']],'mocked_calls':len(captured),'all_expected':True});(Q/('metadata-'+case+'.log')).write_text(text.getvalue())
(Q/'export-metadata-probe-results.json').write_text(json.dumps({'scope':'TEST_ONLY_ACTUAL_FROZEN_EXPORT_MAIN_METADATA_LOGIC_WITH_ALL_EXPORT_SMOKE_COMMANDS_MOCKED','actual_export_or_runtime_executed':False,'source_sha256':hashlib.sha256((Q/'code-freeze/tools/export_p06_preview.py').read_bytes()).hexdigest(),'cases':results},indent=2)+'\n');print('PASS3/3 metadata per-platform intersection/gating probes; no actual export/smoke/engine executed')
