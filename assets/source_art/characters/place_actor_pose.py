#!/usr/bin/env python3
"""Place one complete generated figure in an atlas cell, without anatomy edits.

The complete figure at the atlas pipeline's alpha>=128 support is uniformly
resized with NEAREST to the reference pose's height. Subthreshold alpha speckle
outside that rectangle is discarded, as in pack_actor_sheet. No opaque limbs
or tools are cropped during placement. This is source preparation only.
"""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def rgba(image):return hashlib.sha256(image.tobytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('actor');p.add_argument('kind',choices=['world','action','finisher'])
 p.add_argument('--base',required=True);p.add_argument('--pose',required=True);p.add_argument('--output-version',required=True)
 p.add_argument('--reference-version',required=True);p.add_argument('--reference-column',required=True,type=int,choices=range(8))
 p.add_argument('--row',required=True,type=int,choices=range(4));p.add_argument('--column',required=True,type=int,choices=range(8));a=p.parse_args()
 folder=(ROOT/'assets/source_art/characters'/a.actor).resolve();assert folder.is_relative_to(ROOT/'assets/source_art/characters')
 base=folder/f'{a.kind}_master_{a.base}.png';pose=(folder/a.pose).resolve();assert pose.is_relative_to(folder)
 ref=folder/f'{a.kind}_master_{a.reference_version}.png';target=folder/f'{a.kind}_master_{a.output_version}.png';recipe=folder/f'{a.kind}_{a.output_version}_assembly.json';assert not target.exists() and not recipe.exists()
 old=Image.open(base).convert('RGBA');reference=Image.open(ref).convert('RGBA');figure=Image.open(pose).convert('RGBA');assert old.size==reference.size==(1536,1024)
 bounds=figure.getchannel('A').point(lambda alpha:255 if alpha>=128 else 0).getbbox();assert bounds
 refcell=reference.crop((a.reference_column*192,a.row*256,(a.reference_column+1)*192,(a.row+1)*256));refbounds=refcell.getchannel('A').point(lambda alpha:255 if alpha>=128 else 0).getbbox();assert refbounds
 height=refbounds[3]-refbounds[1];scale=height/(bounds[3]-bounds[1]);width=round((bounds[2]-bounds[0])*scale)
 assert 1<=width<=160 and 1<=height<=224,'Whole figure must fit source gutters without cropping'
 complete=figure.crop(bounds);resized=complete.resize((width,height),Image.Resampling.NEAREST)
 x=(192-width)//2;y=refbounds[3]-height;assert x>=16 and y>0 and x+width<192 and y+height<256
 cell=Image.new('RGBA',(192,256));cell.paste(resized,(x,y));assert sum(cell.getchannel('A').get_flattened_data())==sum(resized.getchannel('A').get_flattened_data()),'No resized opaque figure pixels may be lost'
 output=old.copy();box=(a.column*192,a.row*256,(a.column+1)*192,(a.row+1)*256);output.paste(cell,box[:2])
 unchanged=[]
 for index in range(32):
  row,col=divmod(index,8);rect=(col*192,row*256,(col+1)*192,(row+1)*256)
  if index!=a.row*8+a.column:assert output.crop(rect).tobytes()==old.crop(rect).tobytes();unchanged.append(index)
 output.save(target)
 data={'schema':1,'actor_id':a.actor,'kind':a.kind,'operation':'one complete generated figure alpha bounding rectangle, uniform NEAREST whole-pose scale and placement; no body-part edits/mirror/painting','figure_support_alpha_threshold':128,'subthreshold_speckle_outside_support':'discarded consistently with pack_actor_sheet alpha128 policy','base':str(base.relative_to(ROOT)),'base_sha256':sha(base),'pose':str(pose.relative_to(ROOT)),'pose_sha256':sha(pose),'pose_canvas':list(figure.size),'complete_figure_bounds':list(bounds),'reference':str(ref.relative_to(ROOT)),'reference_sha256':sha(ref),'reference_cell':[a.row,a.reference_column],'reference_bounds':list(refbounds),'uniform_scale':scale,'resized_complete_figure':[width,height],'resized_rgba_sha256':rgba(resized),'placement':[x,y],'changed_cell':[a.row,a.column],'unchanged_cells':unchanged,'all_other31_cells_byte_exact':True,'no_opaque_placement_loss':True,'output_sha256':sha(target),'output_cell_rgba_sha256':rgba(cell),'anatomy_edits':False,'status':'CANDIDATE_REQUIRES_INDEPENDENT_ART','phase_approval':False}
 recipe.write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'sha256':sha(target),'source_cell':[a.row,a.column],'complete_figure_bounds':bounds,'resize':[width,height],'placement':[x,y]}))
if __name__=='__main__':main()
