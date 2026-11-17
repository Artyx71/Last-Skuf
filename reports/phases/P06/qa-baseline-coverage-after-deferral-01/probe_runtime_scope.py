"""Pure AST-extracted production selector/temp filename fixtures. NO engine/decoder/playback."""
from pathlib import Path
import ast,hashlib,json,tempfile
Q=Path(__file__).resolve().parent
source=Q/'scope-closure-source/tools/analyze_p04g_audio.py'
tree=ast.parse(source.read_text());nodes=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ['BASE_RUNTIME_NAMES','EXPORT_RUNTIME_NAMES','FULL_RUNTIME_NAMES'] for x in n.targets) or isinstance(n,ast.FunctionDef) and n.name=='runtime_capture_plan']
assert len(nodes)==4
namespace={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),namespace)
plan=namespace['runtime_capture_plan'];base=('full_replay','reduced_replay');exports=('linux_export_replay','wine_export_replay');full=base+('movie_replay',)+exports
results=[]
def case(label,files,names,expected_exact=None,expected_error=False):
 with tempfile.TemporaryDirectory(prefix='scope-filenames-',dir=Q) as d:
  root=Path(d)
  for name in files:(root/(name+'.wav')).write_bytes(b'SELECTOR_FILENAME_FIXTURE_NOT_AUDIO')
  try:
   selected,paths,exact=plan(root,names);assert not expected_error and exact is expected_exact,(label,exact,expected_exact)
   results.append({'label':label,'passed':True,'selected':list(selected),'actual':[p.stem for p in paths],'exact':exact,'audio_decoded':False})
  except ValueError as error:
   assert expected_error,(label,error)
   results.append({'label':label,'passed':True,'rejected':str(error),'audio_decoded':False})
for names in [base,base+('movie_replay',),base+exports,full]:case('valid_scope_'+str(len(names)),[n for n in names],names,True)
case('default_all5',full,None,True)
case('default5_does_not_accept_only2',base,None,False)
case('missing_required_file',base[:1],base,False)
case('samecount_wrong_filename',['full_replay','unknown_replay'],base,False)
case('unexpected_moviefile_not_silently_ignored',base+('movie_replay',),base,False)
for label,names in [('duplicate',base+('full_replay',)),('partial_Linux_export',base+exports[:1]),('partial_Wine_export',base+exports[1:]),('missing_base',('movie_replay',)),('unknown',base+('unknown_replay',)),('path_escape',base+('../full_replay',)),('empty_request',())]:case(label,base,names,expected_error=True)
actual=Q.parents[3]/'.autopilot/worktrees/P06/reports/phases/P06/native-baseline-after-deferral-02'
# The actual trusted capture dir is explicit; this final observation only reads names.
assert actual.is_dir(),actual
for names,wanted,label in [(base,True,'actual_native02_twofiles_explicit_accept'),(None,False,'actual_native02_default5_stillreject')]:
 selected,paths,exact=plan(actual,names);assert exact is wanted;results.append({'label':label,'passed':True,'selected':list(selected),'actual':[p.stem for p in paths],'exact':exact,'actual_PCM_redecoded':False})
old=ast.parse((Q/'inputs-before/analyze_p04g_audio.py').read_text());old_asset=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='analyze_asset');new_asset=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='analyze_asset');assert ast.dump(old_asset,include_attributes=False)==ast.dump(new_asset,include_attributes=False)
out={'scope':'INDEPENDENT_PURE_RUNTIME_FILENAME_SCOPE_SELECTOR_NOT_SIGNAL_QA','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'production_function_AST_executed_without_module_import':True,'cases':results,'case_count':len(results),'all_passed':True,'old_new_analyze_asset_AST_unchanged':True,'source_signal_thresholds_not_weakened':True,'no_Godot_runner_decoder_network_or_Game_mutation':True}
(Q/'independent-runtime-scope-selector-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'passed':True,'pureselector_cases':len(results),'analyze_asset_AST_unchanged':True}))
