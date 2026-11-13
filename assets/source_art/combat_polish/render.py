#!/usr/bin/env python3
"""Original integer pixel recipes. Approved rasters supply head/clothing motifs only.
Art is authored with explicit joint/cluster coordinates, no random geometry or scaling.
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
# Per pose: left elbow/hand, right elbow/hand, left knee/foot, right knee/foot.
# Explicit anatomy poses: raised guard, extended strike, withdrawing arm, recoiling ribs,
# limp wrists, collapsing knees, prone legs, restrained torso. Feet are not a shifted sheet.
POSES={
 'telegraph':[(14,32,18,26,34,31,37,25,18,48,16,56,29,48,31,56),(13,30,18,24,35,29,38,22,18,48,15,56,30,48,33,56),(12,29,16,23,35,27,37,20,17,49,14,56,31,48,34,55)],
 'attack':[(13,30,19,24,35,28,39,21,16,49,13,56,30,48,33,56),(15,35,20,37,36,34,44,32,15,48,11,55,30,47,34,55),(16,36,22,38,36,36,42,37,17,48,14,56,30,48,34,55)],
 'recovery':[(16,36,22,38,35,37,40,39,17,48,14,56,30,48,33,56),(15,37,19,42,34,36,36,41,18,49,16,56,29,49,32,56),(14,36,15,42,33,36,34,42,19,49,17,56,29,49,31,56)],
 'hurt':[(13,36,19,39,34,35,29,40,18,49,14,55,30,47,33,54),(12,34,18,38,35,34,28,38,17,48,12,54,31,46,35,53),(14,35,20,38,33,36,29,41,18,49,15,56,30,48,32,56)],
 'stun':[(14,38,13,44,33,38,35,44,18,48,15,56,29,48,32,56),(13,39,12,45,34,39,36,45,17,49,14,56,30,49,33,56),(15,39,14,45,32,39,34,45,19,49,16,56,28,49,31,56)],
 'knockdown':[(13,39,10,46,34,39,39,45,17,48,13,54,30,47,34,53),(14,43,11,48,33,43,38,48,17,51,13,55,31,50,36,54),(17,47,12,49,31,48,37,50,19,52,15,56,30,52,35,56)],
 'death':[(13,42,10,47,34,42,39,47,16,50,11,55,31,49,37,54),(16,47,11,49,32,47,38,49,18,52,14,56,31,52,36,56),(17,48,10,51,32,49,40,51,18,53,12,57,32,54,38,57)],
 'finisher_reaction':[(14,34,20,31,33,34,28,31,18,49,16,56,29,49,32,56),(12,36,18,40,35,36,29,40,16,50,12,55,31,50,36,55),(16,47,11,49,32,47,38,49,18,52,14,56,31,52,36,56)],
 'unarmed':[(14,31,21,27,33,30,38,24,17,49,14,56,30,49,33,56),(16,34,26,33,35,34,43,32,16,49,12,56,31,48,35,55),(15,36,23,39,34,36,39,40,18,49,15,56,30,49,33,56)],
 'blunt':[(13,29,19,23,34,28,38,21,17,49,13,56,30,48,33,56),(15,34,24,34,35,34,41,36,16,49,12,56,31,48,35,55),(16,37,22,42,34,37,40,43,18,49,15,56,30,49,33,56)],
 'sharp':[(14,34,20,32,34,31,38,28,18,49,15,56,29,49,32,56),(16,36,23,38,35,35,43,34,17,49,13,56,31,48,35,55),(16,36,23,38,34,37,37,42,18,49,15,56,30,49,33,56)],
 'firearm':[(16,34,23,33,33,32,36,29,18,49,15,56,29,49,32,56),(18,34,30,33,35,33,41,32,17,49,14,56,30,48,34,55),(16,32,25,30,33,31,36,28,18,49,15,56,29,49,32,56)],
 'environmental':[(13,34,19,29,35,34,40,29,17,49,14,56,30,49,33,56),(17,37,27,38,36,37,44,39,16,49,12,56,31,48,36,55),(15,39,23,43,34,40,40,45,18,49,15,56,30,49,33,56)]}
COLORS={'outline':'#151824','pants':'#262b39','boot':'#151824','skin':'#bf947c','highlight':'#e0b89b','blood':'#9d3047','lightblood':'#cf5260','clot':'#542838','metal':'#99a6b5','wood':'#936241'}
inputs={}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def limb(d,points,fill,width=5):
 d.line(points,fill=COLORS['outline'],width=width+2)
 d.line(points,fill=fill,width=width)
 # Authored single-pixel seam along joint.
 x,y=points[1];d.point((x,y),fill=COLORS['highlight'] if fill==COLORS['skin'] else '#4a5061')
def pose(kind,direction,state,f,reaction=False):
 path=ROOT/f'game/assets/art/{"yakuza/world_sheet.png" if kind=="yakuza" else "enemies/"+kind+"_sheet.png"}'
 inputs[str(path.relative_to(ROOT))]=sha(path)
 source_row=2 if direction==1 else direction
 base=Image.open(path).convert('RGBA').crop((0,source_row*64,48,source_row*64+64))
 im=Image.new('RGBA',(48,64));d=ImageDraw.Draw(im)
 joints=list(POSES[state][f])
 # Down/up contact palms are projected along the respective facing, independently
 # of the original torso/head artwork. Each joint retains integer coordinates.
 if direction in [0,3]:
  for offset in [0,2,4,6]:
   x,y=joints[offset:offset+2]
   reach=max(0,x-24)
   joints[offset]=24+(x-24)*2//3
   joints[offset+1]=y+reach//2 if direction==0 else y-reach

 # Distinct category contact reactions: crumpled abdomen, overarm blow, cut ribs,
 # head recoil, and forward wall compression. Not a shared tinted generic reaction.
 fallen=state in ['death','knockdown','finisher_reaction'] and f>0 or reaction and f==2
 if fallen:
  # Independently posed reclined torso/head pieces; rotate only anatomy parts.
  torso=base.crop((14,29,34,44)).rotate(90,expand=True)
  head=base.crop((16,14,32,30)).rotate(90 if direction in [0,2] else -90)
  im.alpha_composite(torso,(18,40 if f==1 else 42));im.alpha_composite(head,(9,35) if f==1 else (7,39))
  limb(d,[(27,49),(34,52),(40,55)],COLORS['pants'],6)
  limb(d,[(25,49),(29,55),(35,57)],COLORS['pants'],6)
  limb(d,[(20,45),(16,49),(10,50)],COLORS['skin'],4)
  limb(d,[(26,44),(32,42),(37,46)],COLORS['skin'],4)
  if f==2:d.line([(14,51),(18,52),(23,51)],fill=COLORS['blood'],width=2)
 else:
  # Preserve approved helmet/hair and vest/tee motifs; author limbs around them.
  im.alpha_composite(base.crop((15,14,34,44)),(15,14+(2 if state in ['stun','knockdown'] else 0)))
  limb(d,[(20,43),(joints[8],joints[9]),(joints[10],joints[11])],COLORS['pants'],6)
  limb(d,[(28,43),(joints[12],joints[13]),(joints[14],joints[15])],COLORS['pants'],6)
  for i in [10,14]: d.rectangle((joints[i]-3,joints[i+1]-2,joints[i]+3,joints[i+1]),fill=COLORS['boot'])
  suit={'patrol':'#39435d','rusher':'#a05e41','shooter':'#663b55','yakuza':'#262733'}[kind]
  for shoulder,offset in [((16,31),0),((32,31),4)]:
   elbow=(joints[offset],joints[offset+1]);hand=(joints[offset+2],joints[offset+3])
   limb(d,[shoulder,elbow,hand],suit,5)
   d.rectangle((hand[0]-1,hand[1]-1,hand[0]+1,hand[1]+2),fill=COLORS['skin'])
  if state in ['hurt','stun'] or reaction:
   d.line([(24,33),(23,36),(26,38)],fill=COLORS['blood'],width=2)
   d.point((26,39),fill=COLORS['lightblood'])
  if state=='stun':
   d.line([(17,9),(20,7),(23,8)],fill='#edcf82',width=1)
   d.line([(30,9),(33,11),(31,13)],fill='#edcf82',width=1)
  if state=='hurt':d.line([(17,28),(20,30),(22,29)],fill=COLORS['lightblood'],width=1)
  if state in CATEGORIES and not reaction:
   hx,hy=joints[6:8]
   if state=='blunt':d.line([(hx,hy+2),(hx+2,hy-10)],fill=COLORS['wood'],width=3);d.point((hx+2,hy-10),fill='#ce9a62')
   if state=='sharp':d.line([(hx,hy),(hx+3,hy-6)],fill=COLORS['metal'],width=2)
   if state=='firearm':d.rectangle((hx-2,hy-3,hx+4,hy),fill='#99a6b5');d.point((hx+5,hy-2),fill='#ffe4a3' if f==1 else '#151824')
   if state=='environmental':d.line([(hx-2,hy+2),(hx+1,hy+1)],fill='#cfbca1',width=2)
  if reaction and f==1:
   if state=='firearm':d.line([(17,23),(22,26),(26,25)],fill=COLORS['blood'],width=2)
   if state=='blunt':d.rectangle((18,17,21,20),fill=COLORS['blood'])
   if state=='sharp':d.line([(19,36),(24,39),(29,38)],fill=COLORS['lightblood'],width=2)
   if state=='environmental':d.line([(29,23),(31,25),(29,29)],fill=COLORS['blood'],width=2)
 # Side-facing hands and asymmetric body details stay directional. No whole-sprite shifts.
 if direction==1:im=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 return im
frames=[]
def sheet(name,kind,states,reaction=False):
 im=Image.new('RGBA',(len(states)*3*48,256))
 for row,direction in enumerate(DIRECTIONS):
  for si,state in enumerate(states):
   for f in range(3):
    frame=pose(kind,row,state,f,reaction)
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
atlas={'schema':1,'frame_size':[48,64],'pivot':[24,58],'directions':DIRECTIONS,'states':STATES,'categories':CATEGORIES,'frames':frames,'effects_columns':['spray0','spray1','spray2','spray3','floor0','floor1','clothing0','clothing1','finish0','finish1','wall','reduced'],'portrait_variants':['baseline','bruised','wounded']}
(OUT/'atlas.json').write_text(json.dumps(atlas,indent=2)+'\n')
# A real native source copy of each newly authored raster, not a fake layered project.
for p in OUT.glob('*.png'):(SRC/(p.stem+'_native_source.png')).write_bytes(p.read_bytes())
provenance={'schema':1,'method':'source-authored integer pixel recipes and approved original anatomy motifs; Pillow rasterization; no image generation service','license':'Original project art; same owner-controlled rights as approved inputs; independent ART acceptance pending','private_photos_read':False,'inputs':inputs,'recipe_sha256':sha(Path(__file__)),'outputs':{str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.suffix in ['.png','.json']}}
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
