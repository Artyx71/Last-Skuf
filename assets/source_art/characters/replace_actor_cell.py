#!/usr/bin/env python3
"""Versioned whole-cell RGBA replacement from built-in generated character art.

Never edits anatomy, resizes, mirrors or combines body parts. Every source cell
is copied byte-for-byte, including its complete transparent gutter.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('actor');p.add_argument('kind',choices=['world','action','finisher'])
 p.add_argument('--base',required=True);p.add_argument('--replacement',required=True);p.add_argument('--output-version',required=True)
 p.add_argument('--row',required=True,type=int,choices=range(4));p.add_argument('--column',required=True,type=int,choices=range(8));a=p.parse_args()
 folder=(ROOT/'assets/source_art/characters'/a.actor).resolve()
 assert folder.is_relative_to(ROOT/'assets/source_art/characters')
 base=folder/f'{a.kind}_master_{a.base}.png';replacement=folder/f'{a.kind}_master_{a.replacement}.png'
 target=folder/f'{a.kind}_master_{a.output_version}.png';recipe=folder/f'{a.kind}_{a.output_version}_assembly.json'
 assert not target.exists() and not recipe.exists(),'Preserve all masters/recipes'
 old=Image.open(base).convert('RGBA');new=Image.open(replacement).convert('RGBA')
 assert old.size==new.size==(1536,1024)
 output=old.copy();rect=(a.column*192,a.row*256,(a.column+1)*192,(a.row+1)*256)
 output.paste(new.crop(rect),rect[:2])
 cells=[]
 for index in range(32):
  row,column=divmod(index,8);box=(column*192,row*256,(column+1)*192,(row+1)*256)
  source=replacement if (row,column)==(a.row,a.column) else base
  expected=(new if source==replacement else old).crop(box).tobytes()
  assert output.crop(box).tobytes()==expected
  cells.append({'index':index,'source':str(source.relative_to(ROOT)),'rect':list(box),'rgba_sha256':hashlib.sha256(expected).hexdigest()})
 output.save(target)
 data={'schema':1,'operation':'exact complete192x256 RGBA cell replacement; no anatomy/pixel edits','actor_id':a.actor,'kind':a.kind,'base_sha256':sha(base),'replacement_sha256':sha(replacement),'output_sha256':sha(target),'changed_cell':[a.row,a.column],'all_other_cells_exactly_preserved':True,'cells':cells,'status':'ASSEMBLY_REQUIRES_INDEPENDENT_SOURCE_REVIEW','phase_approval':False}
 recipe.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'output':str(target.relative_to(ROOT)),'sha256':sha(target),'changed_cell':[a.row,a.column]}))
if __name__=='__main__':main()
