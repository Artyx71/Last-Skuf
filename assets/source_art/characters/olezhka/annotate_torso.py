#!/usr/bin/env python3
"""Explicit whole-pose torso metadata targets; never changes authored sprite pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
ROOT=Path(__file__).resolve().parents[4]
POINTS={
'world':[(24,36),(24,36),(23,34),(25,35),(24,36),(24,34),(25,36),(25,38),(21,38),(22,35),(22,35),(24,36),(24,36),(26,37),(23,34),(25,35),(25,35),(25,36),(23,36),(25,35),(22,35),(22,35),(23,33),(22,34),(25,37),(24,38),(24,37),(25,38),(24,36),(27,37),(24,36),(24,37)],
'action':[(25,34),(24,36),(24,35),(25,37),(24,35),(25,40),(28,46),(25,36),(26,35),(27,35),(24,36),(28,35),(28,36),(27,42),(27,44),(26,36),(21,35),(24,35),(23,35),(22,35),(22,37),(23,42),(22,44),(23,35),(24,35),(24,35),(24,35),(24,35),(25,38),(24,42),(25,43),(24,35)],
'finisher':[(24,34),(25,35),(25,34),(25,34),(25,35),(24,35),(24,37),(25,35),(28,35),(28,35),(28,33),(28,35),(29,35),(28,36),(28,35),(29,35),(23,36),(22,36),(22,36),(22,36),(22,36),(22,36),(22,36),(23,36),(24,40),(24,39),(24,39),(24,39),(24,39),(24,39),(24,40),(24,38)]}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 folder=ROOT/'game/assets/art/characters/olezhka';out=ROOT/'reports/phases/P06/author-checks/olezhka-socket-candidates-03'
 assert not out.exists(),'Preserve all candidates'
 recipe_path=Path(__file__).with_name('clothing_socket_annotations_v2.json');assert not recipe_path.exists()
 recipe={'schema':1,'actor_id':'olezhka','purpose':'manual torso-guided clothing annotations; palette-only candidates incorrectly selected trousers/one shoe','bitmap_changes':False,'phase_approval':False,'sheets':{}}
 shirt={(76,60,86),(53,43,61),(117,69,95)};prepared=[]
 for kind,anchors in POINTS.items():
  path=folder/(kind+'.sockets.json');old=path.read_bytes();prior=json.loads(old);assert prior.get('revision',1)==1
  image_path=folder/(kind+'_sheet.png');assert sha(image_path)==prior['sheet_sha256']
  im=Image.open(image_path).convert('RGBA');board=Image.new('RGBA',im.size,(36,48,44,255));board.alpha_composite(im);draw=ImageDraw.Draw(board)
  for index,desired in enumerate(anchors):
   x,y=index%8*48,index//8*64
   choices=[(px,py) for py in range(max(0,desired[1]-5),min(64,desired[1]+6)) for px in range(max(0,desired[0]-5),min(48,desired[0]+6)) if im.getpixel((x+px,y+py))[3] and im.getpixel((x+px,y+py))[:3] in shirt]
   assert choices,(kind,index,desired)
   chosen=min(choices,key=lambda p:((p[0]-desired[0])**2+(p[1]-desired[1])**2,p[1],p[0]));entry=prior['frames'][index];entry['palette_candidate_clothing']=entry['clothing'];entry['manual_torso_target']=list(desired);entry['clothing']=list(chosen);entry['annotation_note']='Manual whole-pose torso target, nearest existing garment pixel within5; actual overlay review pending'
   px,py=x+chosen[0],y+chosen[1];draw.line((px-2,py,px+2,py),fill='#7bd2df');draw.line((px,py-2,px,py+2),fill='#7bd2df')
  prior.update(method='manual torso target per whole pose, nearest existing garment pixel within5; no bitmap edits',revision=2,previous_annotation_sha256=hashlib.sha256(old).hexdigest())
  data=(json.dumps(prior,indent=2)+'\n').encode();prepared.append((kind,path,old,data,board))
  recipe['sheets'][kind]={'sheet_sha256':prior['sheet_sha256'],'previous_annotation_sha256':prior['previous_annotation_sha256'],'manual_torso_targets':anchors,'actual_chosen':[e['clothing'] for e in prior['frames']],'annotation_sha256':hashlib.sha256(data).hexdigest()}
 # Validate all96 before replacing any runtime metadata.
 out.mkdir()
 for kind,path,old,data,board in prepared:
  (out/(kind+'.sockets.before.json')).write_bytes(old);path.write_bytes(data);board.resize((1536,1024),Image.Resampling.NEAREST).save(out/(kind+'_anchors_4x.png'))
 recipe_path.write_text(json.dumps(recipe,indent=2)+'\n');print('96 torso-guided metadata anchors; prior candidates retained; no bitmap changes')
if __name__=='__main__':main()
