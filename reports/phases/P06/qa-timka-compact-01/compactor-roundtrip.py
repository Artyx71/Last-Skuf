"""Execute the actual compactor only in temporary ROOT report fixtures."""
from pathlib import Path
import sys,tempfile,json,shutil,hashlib,contextlib,io
from unittest.mock import patch
from PIL import Image
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;W=O.parents[3]/'.autopilot/worktrees/P06';sys.path.insert(0,str(W/'assets/source_art/characters'));import compact_timka as c
rows=[]
for kind,cols in [('world',list(range(8))),('action',list(range(7))),('finisher',[0,1,2,5,6,7])]:
 with tempfile.TemporaryDirectory(prefix='qa-compact-real-',dir=O/'tmp') as td:
  root=Path(td);source=root/'assets/source_art/characters/timka';source.mkdir(parents=True);actual=W/'assets/source_art/characters/timka';supported=json.loads((actual/f'{kind}_manifest_supported_v1.json').read_text());prov=supported['source_compaction'];original_manifest=json.loads((W/prov['input_manifest']).read_text());inputs=[prov['input_native'],prov['input_manifest'],original_manifest['master'],'automation/decisions/P06_TIMKA_SUPPORTED_ANIMATIONS.json','assets/source_art/characters/compact_timka.py']
  for rel in inputs:
   dest=root/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(W/rel,dest)
  old_name=Path(prov['input_native']).name;base=old_name[len(kind+'_native_'):-4]
  with patch.object(c,'ROOT',root),patch.object(c,'__file__',str(root/'assets/source_art/characters/compact_timka.py')),contextlib.redirect_stdout(io.StringIO()):c.compact(kind,base,'qa_roundtrip')
  image=Image.open(source/f'{kind}_native_qa_roundtrip.png').convert('RGBA');original=Image.open(root/prov['input_native']).convert('RGBA');expected=Image.new('RGBA',(len(cols)*48,256))
  for row in range(4):
   for col,oldcol in enumerate(cols):expected.paste(original.crop((oldcol*48,row*64,oldcol*48+48,row*64+64)),(col*48,row*64))
  assert image.tobytes()==expected.tobytes();manifest=json.loads((source/f'{kind}_manifest_qa_roundtrip.json').read_text());assert manifest['source_cells']==len(cols)*4;assert manifest['source_column_mapping']==cols
  if kind=='world':assert (source/f'{kind}_native_qa_roundtrip.png').read_bytes()==(root/prov['input_native']).read_bytes()
  rows.append({'kind':kind,'actual_compactor_executed_in_temp':True,'required_cells':len(cols)*4,'original_columns':cols,'independent_wholecell_RGBA_reconstruction_exact':True,'world_PNG_bytes_preserved':True if kind=='world' else None,'ART_or_runtime_approval':False})
(O/'compactor-roundtrip-results.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
