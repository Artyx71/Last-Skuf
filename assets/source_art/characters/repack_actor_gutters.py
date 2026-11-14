#!/usr/bin/env python3
"""Repack complete isolated poses by fixed column translations; retain raw master.

No rescaling, limb reconstruction or bitmap painting. All source foreground pixels
must survive exactly once. The result still requires independent source ART review.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('actor');p.add_argument('kind',choices=['action','finisher']);p.add_argument('--version',required=True);p.add_argument('--output-version',required=True);p.add_argument('--shifts',nargs=8,type=int,required=True);args=p.parse_args()
 folder=ROOT/'assets/source_art/characters'/args.actor
 source=folder/f'{args.kind}_master_{args.version}.png';target=folder/f'{args.kind}_master_{args.output_version}.png';recipe=folder/f'{args.kind}_{args.output_version}_assembly.json'
 assert not target.exists() and not recipe.exists(),'Preserve existing candidates'
 image=Image.open(source).convert('RGBA');assert image.size==(1536,1024)
 alpha=image.getchannel('A').point(lambda value:255 if value>=128 else 0)
 output=Image.new('RGBA',image.size);entries=[]
 for row in range(4):
  runs=[]
  for x in range(1536):
   if not alpha.crop((x,row*256,x+1,(row+1)*256)).getbbox():continue
   if runs and x==runs[-1][1]:runs[-1][1]=x+1
   else:runs.append([x,x+1])
  assert len(runs)==8,(row,'Need eight isolated whole-pose horizontal extents',runs)
  for column,(left,right) in enumerate(runs):
   shift=args.shifts[column];dest_left=left+shift;dest_right=right+shift
   assert column*192<dest_left<dest_right<(column+1)*192,(row,column,'Keep complete pose within its own cell')
   rect=[left,row*256,right,(row+1)*256];dest=[dest_left,row*256,dest_right,(row+1)*256]
   whole=image.crop(rect);output.paste(whole,(dest_left,row*256))
   assert output.crop(dest).tobytes()==whole.tobytes()
   foreground=sum(value>=128 for value in whole.getchannel('A').get_flattened_data())
   entries.append({'row':row,'column':column,'source_rect':rect,'destination_rect':dest,'translation':[shift,0],'whole_rgba_sha256':hashlib.sha256(whole.tobytes()).hexdigest(),'foreground_pixels_preserved':foreground})
 before=sum(value>=128 for value in image.getchannel('A').get_flattened_data());after=sum(value>=128 for value in output.getchannel('A').get_flattened_data())
 assert before==after==sum(e['foreground_pixels_preserved'] for e in entries)
 output.save(target)
 data={'schema':1,'status':'WHOLE_POSE_LAYOUT_CANDIDATE_INDEPENDENT_ART_PENDING','actor_id':args.actor,'kind':args.kind,'source':str(source.relative_to(ROOT)),'source_sha256':sha(source),'output':str(target.relative_to(ROOT)),'output_sha256':sha(target),'fixed_column_translations':args.shifts,'source_pose_isolation':'eight disjoint alpha>=128 horizontal extents per direction row; complete256px cell height','foreground_alpha_threshold':128,'source_foreground_pixels':before,'output_foreground_pixels':after,'anatomy_redrawn':False,'rescaled':False,'mirrored':False,'entries':entries}
 recipe.write_text(json.dumps(data,indent=2)+'\n');print(args.actor,args.kind,args.output_version,sha(target),'opaque retained',after)
if __name__=='__main__':main()
