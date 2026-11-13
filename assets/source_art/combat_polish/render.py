#!/usr/bin/env python3
"""Original generated actor drawings with technical pixel packing.
Approved artwork is read-only identity/style input; complete bodies are drawn, not cropped anatomy.
Run with Pillow; never writes earlier assets or reports. Author review != independent ART.
"""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'game/assets/art/combat_polish'
SRC=Path(__file__).parent
DIRECTIONS=['down','left','right','up']
STATES=['telegraph','attack','recovery','hurt','stun','knockdown','death','finisher_reaction']
CATEGORIES=['unarmed','blunt','sharp','firearm','environmental']
from pack_generated import pose, clothing_socket, INPUTS, PACKING, SOCKETS
COLORS={'outline':'#151824','pants':'#262b39','boot':'#151824','skin':'#bf947c','highlight':'#e0b89b','blood':'#9d3047','lightblood':'#cf5260','clot':'#542838','metal':'#99a6b5','wood':'#936241'}
inputs={}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
frames=[]
def sheet(name,kind,states,reaction=False):
 im=Image.new('RGBA',(len(states)*3*48,256))
 for row,direction in enumerate(DIRECTIONS):
  for si,state in enumerate(states):
   for f in range(3):
    frame=pose(kind,row,state,f,reaction)
    prone=(state in ['death','knockdown','finisher_reaction'] and f==2) or (reaction and f==2)
    SOCKETS.setdefault(name,{}).setdefault(str(row),{})[str(si*3+f)]=list(clothing_socket(frame,prone))
    im.alpha_composite(frame,((si*3+f)*48,row*64))
    frames.append({'sheet':name,'kind':kind,'state':state,'direction':direction,'frame':f,'rect':[(si*3+f)*48,row*64,48,64],'bounds':frame.getbbox(),'sha256':hashlib.sha256(frame.tobytes()).hexdigest()})
 im.save(OUT/name)
for kind in ['patrol','rusher','shooter']:
 sheet(kind+'_reactions.png',kind,STATES)
 sheet(kind+'_finishers.png',kind,CATEGORIES,True)
sheet('yakuza_finishers.png','yakuza',CATEGORIES)
# Blood clusters explicitly placed with limited dark red palette. Four authored direction
# layouts; no RNG, no polygon cloud. Four time keys: compact, arc, separation, droplets.
SPRAYS=[[(23,26),(25,28),(20,31),(27,34),(18,37),(24,40),(30,43)],[(23,27),(18,25),(15,30),(12,24),(9,32),(6,27),(4,36)],[(25,27),(30,25),(33,30),(36,24),(39,32),(42,27),(44,36)],[(23,26),(26,22),(20,20),(28,16),(18,13),(25,10),(30,7)]]
effects=Image.new('RGBA',(12*48,4*64))
for row in range(4):
 for col in range(12):
  cell=Image.new('RGBA',(48,64));d=ImageDraw.Draw(cell)
  if col<4:
   for i,(x,y) in enumerate(SPRAYS[row][:4+col]):
    # Designed hooked droplet with shadow root, lit edge, isolated satellite.
    d.line([(x-1,y),(x,y+1),(x+2,y+1),(x+2,y+3)],fill=COLORS['clot'],width=2)
    d.line([(x,y),(x+1,y+1),(x+1,y+2)],fill=COLORS['blood'],width=2)
    d.point((x,y),fill=COLORS['lightblood'])
    if col>1:d.point((x-2,y+4),fill=COLORS['blood'])
  elif col in [4,5,8,9]:
   # Jagged pooled stain, crescent edge and boot-shaped drag. Integer rows, no ellipses.
   points=[(11,48),(17,46),(20,47),(25,44),(29,46),(35,46),(37,49),(34,51),(30,51),(28,54),(21,53),(18,55),(13,52),(9,51)]
   if col in [5,9]:points=[(x+1 if i%3==0 else x,y-2 if i%4==0 else y) for i,(x,y) in enumerate(points)]
   d.polygon(points,fill=COLORS['clot']);d.line([(14,49),(21,48),(28,48),(33,50)],fill=COLORS['blood'],width=2)
   d.line([(17,52),(23,51),(27,52)],fill=COLORS['lightblood'],width=1)
   if col>=8:
    d.line([(26,48),(33,43),(39,43)],fill=COLORS['blood'],width=2)
    d.rectangle((8,46,10,47),fill=COLORS['blood']);d.point((38,48),fill=COLORS['blood'])
  elif col in [6,7]:
   d.line([(20,26),(24,28),(22,31),(27,33),(26,36)],fill=COLORS['clot'],width=3)
   d.line([(21,26),(24,29),(23,32),(26,34)],fill=COLORS['blood'],width=2)
   d.point((28,30 if col==6 else 38),fill=COLORS['lightblood'])
  elif col==10:
   d.line([(17,24),(23,27),(26,26),(30,29),(31,33)],fill=COLORS['blood'],width=3)
   d.line([(21,29),(21,38),(22,40)],fill=COLORS['clot'],width=2)
   d.line([(28,31),(28,43)],fill=COLORS['blood'],width=1)
  else:
   # Reduced mode: same readable contact direction without red.
   d.line([(19,27),(22,24),(24,25)],fill='#edcf82',width=1)
   d.line([(28,31),(31,28),(33,29)],fill='#f3ead8',width=1)
  effects.alpha_composite(cell,(col*48,row*64))
effects.save(OUT/'effects.png')
# Approved portrait is immutable. Small injuries overlay the existing face planes only.
portrait_path=ROOT/'game/assets/art/yakuza/portraits.png';inputs[str(portrait_path.relative_to(ROOT))]=sha(portrait_path)
base=Image.open(portrait_path).convert('RGBA').crop((0,0,160,160))
portraits=Image.new('RGBA',(480,160))
for i in range(3):
 im=base.copy();d=ImageDraw.Draw(im)
 if i>0:
  d.polygon([(98,64),(105,65),(108,69),(104,72),(98,70)],fill='#693d55')
  d.line([(101,65),(106,67)],fill='#995767',width=2)
  d.line([(51,83),(54,87),(53,91)],fill='#9d3047',width=2)
 if i>1:
  d.line([(104,70),(106,77),(104,82)],fill='#9d3047',width=2)
  d.line([(75,106),(80,108),(84,106)],fill='#542838',width=2)
  d.line([(79,110),(78,114)],fill='#9d3047',width=2)
 portraits.alpha_composite(im,(i*160,0))
portraits.save(OUT/'yakuza_damage.png')
# Registered training wall/bench, a new object, not a campaign map replacement.
prop=Image.new('RGBA',(48,64));d=ImageDraw.Draw(prop)
d.rectangle((5,22,42,50),fill='#252a39');d.rectangle((7,24,40,44),fill='#706578');d.rectangle((9,25,38,28),fill='#b4a4a3')
for x in [13,25,37]:d.line([(x,30),(x,42)],fill='#4a4256',width=1)
d.rectangle((9,49,14,58),fill='#393c50');d.rectangle((34,49,39,58),fill='#393c50');d.line([(10,50),(38,50)],fill='#b4a4a3',width=2)
prop.save(OUT/'training_bench.png')
# Reduced artwork uses the identical poses/anchors and neutral contact scuffs.
# This is a derived palette variant, not additional independently authored poses.
reduced_sheets={}
for name in [kind+'_'+suffix+'.png' for kind in ['patrol','rusher','shooter'] for suffix in ['reactions','finishers']]+['yakuza_finishers.png']:
 im=Image.open(OUT/name).convert('RGBA')
 replacements={(157,48,71,255):(74,80,97,255),(207,82,96,255):(153,166,181,255),(84,40,56,255):(38,43,57,255)}
 im.putdata([replacements.get(pixel,pixel) for pixel in im.get_flattened_data()])
 reduced_name=name.replace('.png','_reduced.png');im.save(OUT/reduced_name)
 reduced_sheets[name]=reduced_name
atlas={'schema':1,'frame_size':[48,64],'pivot':[24,58],'directions':DIRECTIONS,'states':STATES,'categories':CATEGORIES,'frames':frames,'effects_columns':['spray0','spray1','spray2','spray3','floor0','floor1','clothing0','clothing1','finish0','finish1','wall','reduced'],'portrait_variants':['baseline','bruised','wounded'],'reduced_sheets':reduced_sheets,'clothing_sockets':SOCKETS,'drawing_scope':'528 actor atlas slots; generated key drawings and intentional reaction/corpse reuse, not528 unique poses'}
(OUT/'atlas.json').write_text(json.dumps(atlas,indent=2)+'\n')
# A real native source copy of each newly authored raster, not a fake layered project.
for p in OUT.glob('*.png'):(SRC/(p.stem+'_native_source.png')).write_bytes(p.read_bytes())
inputs.update(INPUTS)
for name in ['yakuza/world_sheet.png','yakuza/action_sheet.png','enemies/patrol_sheet.png','enemies/rusher_sheet.png','enemies/shooter_sheet.png']:
 p=ROOT/'game/assets/art'/name
 inputs[str(p.relative_to(ROOT))]=sha(p)
inputs[str((SRC/'pack_generated.py').relative_to(ROOT))]=sha(SRC/'pack_generated.py')
for p in sorted((SRC/'attempt2').glob('*')):
 if p.suffix in ['.txt','.json'] and p.name!='packing.json':inputs[str(p.relative_to(ROOT))]=sha(p)
(SRC/'attempt2'/'packing.json').write_text(json.dumps(PACKING,indent=2)+'\n')
provenance={'schema':2,'method':'built-in image_gen original complete actor drawings from approved project artwork; alpha component recovery, fixed character scale, nearest sampling and approved palette; unchanged integer effects recipe','license':'Original project art; same owner-controlled rights as approved inputs; independent ART acceptance pending','private_photos_read':False,'inputs':inputs,'recipe_sha256':sha(Path(__file__)),'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.suffix in ['.png','.json']}}
(SRC/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n')
# Inspection board, not runtime art.
board=Image.new('RGBA',(13*48,8*64),'#353744')
for i,state in enumerate(STATES+CATEGORIES):
 kind='patrol' if i<8 else 'yakuza'
 for f in range(3):board.alpha_composite(pose(kind,2,state,f), (i*48,f*64))
for i,state in enumerate(CATEGORIES):
 for f in range(3):board.alpha_composite(pose('rusher',2,state,f,True),(i*48,(f+4)*64))
board.save(SRC/'author_board.png')
print('authored',len(frames),'actor frames')
