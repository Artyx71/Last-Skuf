"""Select fourteen complete generated cells and ten unchanged reviewed cells.
Atlas assembly only. Never splice anatomy, move weapons, paint or mask a body.
"""
from pathlib import Path
import json,hashlib
from PIL import Image
HERE=Path(__file__).resolve().parent
OLD=HERE/'source-v2/master.png';NEW=HERE/'source-v3/raw-edit.png';OUT=HERE/'source-v3/master.png'
assert not OUT.exists()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=Image.open(OLD).convert('RGBA');new=Image.open(NEW).convert('RGBA')
assert old.size==new.size==(1024,1536)
out=Image.new('RGBA',old.size);cells=[]
for row in range(6):
 for col in range(4):
  rect=(col*256,row*256,(col+1)*256,(row+1)*256)
  replacement=row%2==0 or (row in [3,5] and col==0)
  whole=(new if replacement else old).crop(rect)
  out.paste(whole,(col*256,row*256))
  assert out.crop(rect).tobytes()==whole.tobytes()
  cells.append({'row':row,'column':col,'rect':list(rect),'from':'raw-edit-v3' if replacement else 'exact-retained-v2','rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest()})
out.save(OUT)
record={'schema':1,'scope':'C09_GABAR_WHOLECELL_SOURCE_REPAIR_ONLY','method':'14new wholefigures (12contact+2DOWNrelease) plus10exactretainedrelease complete256cells; no masks/anatomy/mirror/rotation','previous_source_sha256':sha(OLD),'new_raw_sha256':sha(NEW),'master_sha256':sha(OUT),'recipe_sha256':sha(Path(__file__)),'source_ART_FAIL_sha256':'985592e6d599a9c1abc13703f4c7f71bd5385e5441e2dca688f821b4b4d7376e','cells':cells,'new_wholefigures':14,'retained_wholefigures':10,'raw_photo_uploads':0,'runtime_integration':False,'independent_ART':'PENDING','phase_approval':False}
(OUT.parent/'assembly.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print('wholecell master saved',record['master_sha256'])
