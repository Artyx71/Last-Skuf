#!/usr/bin/env python3
"""Compose four reviewed whole direction rows; does not certify runtime animation."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
DIRECTIONS=['down','left','right','up']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def assemble(actor,versions,output_version):
 source=ROOT/'assets/source_art/characters'/actor
 index_path=ROOT/'reports/phases/P06/art-preflight'/f'{actor}_world_direction_source_index_v1.json';index=json.loads(index_path.read_text())
 assert index['status']=='FOUR_DIRECTION_SOURCE_CANDIDATES_ACCEPTABLE_FOR_NATIVE_PREVIEW'
 reviewed={entry['direction']:entry for entry in index['directions']};assert set(reviewed)==set(DIRECTIONS)
 output=Image.new('RGBA',(384,256));frames=[];references=[]
 for row,(direction,version) in enumerate(zip(DIRECTIONS,versions)):
  native=source/f'world_{direction}_native_{version}.png';manifest=source/f'world_{direction}_manifest_{version}.json';m=json.loads(manifest.read_text())
  review=ROOT/'reports/phases/P06/art-preflight'/f'{actor}_world_{direction}_preflight_{version}.json';r=json.loads(review.read_text())
  assert r['reviewer']=='/root/art_review_p06'
  entry=reviewed[direction];report=review.parent/r['report']
  assert entry['native_path']==str(native.relative_to(ROOT)) and entry['review']==r['report'] and sha(report)==entry['review_sha256']
  assert r.get('actor_id',actor)==actor and r.get('direction',direction)==direction
  assert r['status']==f'ACCEPTABLE_{direction.upper()}_DIRECTION_SOURCE_CANDIDATE' and not r.get('blocking_findings')
  assert sha(native)==m['sha256']==r['native_sha256']==entry['native_sha256']
  im=Image.open(native).convert('RGBA');assert im.size==(384,64)
  for col in range(8):
   frame=im.crop((col*48,0,(col+1)*48,64));entry=m['frames'][col];assert frame.getbbox()
   assert hashlib.sha256(frame.tobytes()).hexdigest()==entry['rgba_sha256']
   frames.append({'direction':direction,'column':col,'rect':[col*48,row*64,48,64],'pivot':[24,58],'bounds':frame.getbbox(),'rgba_sha256':entry['rgba_sha256'],'source_native':str(native.relative_to(ROOT)),'source_frame':entry})
  output.paste(im,(0,row*64));references.append({'direction':direction,'version':version,'native':str(native.relative_to(ROOT)),'sha256':sha(native),'manifest':str(manifest.relative_to(ROOT)),'manifest_sha256':sha(manifest),'independent_source_review':str(review.relative_to(ROOT)),'review_sha256':sha(review),'runtime_approval':False})
 dest=ROOT/'game/assets/art/characters'/actor;dest.mkdir(parents=True,exist_ok=True)
 target=dest/'world_sheet.png';assert not target.exists(),'Do not silently overwrite existing production candidate'
 output.save(target);output.save(source/f'world_native_{output_version}.png')
 m={'schema':1,'actor_id':actor,'kind':'world','status':'REVIEWED_SOURCE_CANDIDATE_RUNTIME_PENDING','file':target.name,'sha256':sha(target),'frame_size':[48,64],'dimensions':[384,256],'pivot':[24,58],'directions':DIRECTIONS,'source_cells':32,'unique_native_drawings':len({f['rgba_sha256'] for f in frames}),'frames':frames,'animations_source_columns':{'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]},'animation_reference_count':32,'assembled_from':references,'packing':'exact RGBA direction rows; no additional scaling/repainting/mirroring','review':{'source_only':True,'actual_animation':'PENDING','contact_alignment':'NOT_APPLICABLE_WORLD_ONLY','phase_approval':False}}
 (dest/'world.json').write_text(json.dumps(m,indent=2)+'\n');(source/f'world_assembly_{output_version}.json').write_text(json.dumps(m,indent=2)+'\n')
 board=Image.new('RGBA',output.size,(36,48,44,255));board.alpha_composite(output);board.resize((1152,768),Image.Resampling.NEAREST).save(source/f'world_inspection_{output_version}_3x.png')
 print(actor,m['sha256'],'REVIEWED_SOURCE_CANDIDATE_RUNTIME_PENDING')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('actor');p.add_argument('--versions',nargs=4,required=True,metavar=('DOWN','LEFT','RIGHT','UP'));p.add_argument('--output-version',required=True);a=p.parse_args();assemble(a.actor,a.versions,a.output_version)
