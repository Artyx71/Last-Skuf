"""Source-only whole-cell technical export, following accepted P04 packing.
No Game writes, generated anatomy/part edits/rotation/mirroring or new drawings.
"""
from pathlib import Path
import hashlib,json
from PIL import Image, ImageOps

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=HERE/'source-v2/master.png'
OUT=HERE/'preview-v2'
assert not OUT.exists(), 'Keep previous source proofs; use a new version'
OUT.mkdir()
image=Image.open(SOURCE).convert('RGBA')
assert image.size==(1024,1536)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
palette_path=ROOT/'game/assets/art/enemies/atlas.json'
colors=json.loads(palette_path.read_text())['palette']['rgb_hex']+['#ffe4a3','#936241','#ce9a62']
rgb=[tuple(bytes.fromhex(c.lstrip('#'))) for c in colors]
palette=Image.new('P',(1,1));palette.putpalette([v for c in rgb for v in c]+list(rgb[0])*(256-len(rgb)))
atlas=Image.new('RGBA',(192,384))
frames=[]
for row in range(6):
 for col,direction in enumerate(['down','left','right','up']):
  rect=(col*256,row*256,(col+1)*256,(row+1)*256)
  cell=image.crop(rect)
  support=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
  bounds=support.getbbox()
  assert bounds and bounds[0]>0 and bounds[1]>0 and bounds[2]<256 and bounds[3]<256, ('Clipped source figure',row,col,bounds)
  cell=cell.resize((64,64),Image.Resampling.NEAREST)
  alpha=cell.getchannel('A').point(lambda a:255 if a>=128 else 0)
  assert alpha.getpixel((0,0))==0
  # Native64 cell has eight empty columns on either side of the48x64 actor.
  # This crops padding only, with equality of all opaque samples verified.
  cell.putalpha(alpha)
  kept=cell.crop((8,0,56,64))
  assert sum(kept.getchannel('A').histogram()[1:])==sum(alpha.histogram()[1:]), 'Whole figure must fit; never silently clip limbs/weapons'
  alpha=kept.getchannel('A')
  bottom=alpha.getbbox()[3];dy=58-bottom
  limited=kept.convert('RGB').quantize(palette=palette,dither=Image.Dither.NONE).convert('RGBA')
  limited.putalpha(alpha);limited.paste((0,0,0,0),(0,0),ImageOps.invert(alpha))
  frame=Image.new('RGBA',(48,64));frame.paste(limited,(0,dy))
  assert sum(frame.getchannel('A').histogram()[1:])==sum(alpha.histogram()[1:]), 'Whole-figure anchor translation may not clip'
  atlas.paste(frame,(col*48,row*64))
  frames.append({'archetype':['patrol','rusher','shooter'][row//2],'role':'contact' if row%2==0 else 'release','direction':direction,'source_rect':list(rect),'source_whole_bounds':list(bounds),'native_rect':[col*48,row*64,48,64],'native_bounds':list(frame.getbbox()),'translate':[0,dy],'pivot':[24,58],'native_rgba_sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
atlas.save(OUT/'gabar_npc_native.png')
board=Image.new('RGBA',atlas.size,(36,48,44,255));board.alpha_composite(atlas)
board.resize((576,1152),Image.Resampling.NEAREST).save(OUT/'inspection_3x.png')
manifest={'schema':1,'scope':'C09_GABAR_NPC_SOURCE_PREVIEW_ONLY','status':'PENDING_INDEPENDENT_ART_NOT_IN_RUNTIME','master_sha256':sha(SOURCE),'recipe_sha256':sha(Path(__file__)),'palette_source_sha256':sha(palette_path),'actual_whole_drawings':24,'actual_unique_native_RGBA':len({f['native_rgba_sha256'] for f in frames}),'new_FIN_role_refs':'contact/release only; no fabricated hold/corpse; compatibility pending','native_sha256':sha(OUT/'gabar_npc_native.png'),'dimensions':[192,384],'frame_size':[48,64],'frames':frames,'technical_conversion':{'wholecell_NN':'256x256 to64x64, remove transparent8px sidepadding only','alpha_threshold':128,'palette':colors,'limited_palette_dither':False,'whole_figure_vertical_anchor':58,'anatomical_reconstruction':False,'new_poses_generated_by_recipe':False,'raw_photos_read':False},'independent_ART':'PENDING','native_animation_review':'NOT_RUN','runtime_integration':False,'phase_approval':False}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:manifest[k] for k in ['scope','status','actual_whole_drawings','actual_unique_native_RGBA','native_sha256']}))
