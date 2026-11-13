#!/usr/bin/env python3
"""Authored pixel environment, integer primitives only; no input images or tracing.
Pillow renders explicit tile/prop drawings at native resolution, with no resampling.
"""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'game/assets/art/missed_fight';OUT.mkdir(parents=True,exist_ok=True)
PAL=['#10141f','#191e2b','#262d3c','#384252','#4f5b68','#788a91','#afbcaf','#d9d3b2','#faf0c5','#25474b','#346766','#54958c','#80cbb4','#273c59','#3e6284','#6291aa','#4b334e','#70455e','#aa5979','#e68fa2','#4c392f','#795641','#ab7c4e','#d5aa6d','#756f4b','#a7ad75','#e0d08a','#4d4041','#7f5353','#ba7060','#da9368','#f5c58c']
P=PAL
atlas=Image.new('RGB',(256,64),P[0])
for tile in range(16):
 im=Image.new('RGB',(32,32),P[1]);d=ImageDraw.Draw(im)
 if tile<4: # ceramic floor: restrained chips, contrasting square inlay
  d.rectangle((0,0,31,31),fill=P[9]);d.rectangle((1,1,30,30),fill=P[10 if tile%2==0 else 9]);d.line((1,30,30,30),fill=P[5]);d.line((30,1,30,30),fill=P[2]);d.rectangle((3,3,13,13),fill=P[11]);d.rectangle((17,17,27,27),fill=P[11]);d.point((8+tile,24),fill=P[6]);d.line((21,5,24,8),fill=P[10])
 elif tile<8: # worn hallway boards
  d.rectangle((0,0,31,31),fill=P[3]);
  for y in [0,8,16,24]:
   d.rectangle((1,y+1,31,y+6),fill=P[4 if (tile+y)%3 else 3]);d.line((4+tile,y+3,15+tile,y+3),fill=P[5]);d.line((22,y,22,y+6),fill=P[2])
 elif tile<12: # rain-dark asphalt and drainage
  d.rectangle((0,0,31,31),fill=P[2]);
  for x,y in [(3,6),(21,13),(13,23),(29,29),(7,17)]:d.line((x,y,x+2,y),fill=P[3])
  if tile==11:
   d.rectangle((0,11,31,24),fill=P[1]);
   for x in range(2,31,4):d.line((x,12,x,23),fill=P[5])
 else: # wall top brick and bathroom wall cap
  d.rectangle((0,0,31,31),fill=P[16 if tile%2 else 2]);
  for y in [0,16]:
   for x in range(-16 if y else 0,32,32):
    d.rectangle((x+1,y+1,x+30,y+14),fill=P[17 if tile%2 else 3]);d.line((x+3,y+2,x+28,y+2),fill=P[18 if tile%2 else 4])
  d.line((0,29,31,29),fill=P[12 if tile==14 else 18])
 atlas.paste(im,((tile%8)*32,(tile//8)*32))
atlas.save(OUT/'tiles.png')
# Each prop is independently authored in a transparent 96x96 cell.
props=Image.new('RGBA',(96*8,96),(0,0,0,0))
for k in range(8):
 im=Image.new('RGBA',(96,96));d=ImageDraw.Draw(im)
 if k==0: # double basin, wall mirror, copper plumbing
  d.rectangle((8,3,86,30),fill=P[1]);d.rectangle((11,5,83,27),fill=P[14]);d.polygon([(15,8),(44,8),(22,25),(15,25)],fill=P[15]);d.line((70,6,50,26),fill=P[5],width=2)
  d.rectangle((10,35,87,65),fill=P[4]);d.rectangle((12,34,85,60),fill=P[6]);
  for x in [18,55]:
   d.ellipse((x,39,x+25,56),fill=P[5]);d.ellipse((x+3,41,x+22,53),fill=P[9]);d.rectangle((x+11,34,x+14,45),fill=P[7]);d.point((x+13,50),fill=P[1]);d.line((x+12,65,x+12,77),fill=P[22],width=3)
 elif k==1: # stall and visible toilet
  d.rectangle((7,5,87,82),fill=P[1]);d.rectangle((9,7,84,79),fill=P[9]);d.rectangle((13,10,80,75),fill=P[10]);d.rectangle((29,11,64,28),fill=P[6]);d.ellipse((29,22,64,61),fill=P[7]);d.ellipse((35,28,58,52),fill=P[5]);d.ellipse((39,30,54,47),fill=P[9]);d.rectangle((9,70,65,79),fill=P[11]);d.rectangle((68,69,72,75),fill=P[23])
 elif k==2: # coat on hook, yellow key sewn to cord
  d.rectangle((31,7,66,11),fill=P[22]);d.line((47,9,47,20),fill=P[6],width=2);d.polygon([(36,19),(45,16),(53,19),(62,28),(68,56),(57,59),(54,41),(56,75),(31,75),(33,42),(28,58),(18,54),(27,27)],fill=P[1]);d.line((44,23,43,70),fill=P[4],width=2);d.line((33,28,31,49),fill=P[3],width=3);d.rectangle((47,45,56,56),fill=P[2]);d.ellipse((48,49,54,55),outline=P[26]);d.line((52,54,52,64),fill=P[26],width=2);d.line((51,62,56,62),fill=P[26],width=2)
 elif k==3: # stacked crates, bottles
  for x,y in [(8,36),(47,30),(24,5)]:
   d.rectangle((x+3,y+5,x+37,y+39),fill=P[1]);d.rectangle((x,y,x+34,y+33),fill=P[20]);d.rectangle((x+2,y+2,x+32,y+30),outline=P[22],width=2);d.line((x+4,y+4,x+29,y+28),fill=P[21],width=3);d.line((x+29,y+4,x+4,y+28),fill=P[21],width=3);d.rectangle((x+10,y+9,x+24,y+19),fill=P[7]);d.line((x+13,y+13,x+21,y+13),fill=P[21])
 elif k==4: # industrial extractor machinery
  d.rectangle((9,14,88,82),fill=P[1]);d.rectangle((6,10,84,76),fill=P[4]);d.rectangle((9,13,81,72),fill=P[3]);
  for x in [29,61]:
   d.ellipse((x-13,25,x+13,51),fill=P[1],outline=P[5]);d.line((x-8,30,x+8,46),fill=P[4],width=4);d.line((x+8,30,x-8,46),fill=P[4],width=4);d.ellipse((x-3,35,x+3,41),fill=P[5])
  for y in range(57,68,4):d.line((16,y,71,y),fill=P[1])
  d.rectangle((10,4,19,10),fill=P[22]);d.rectangle((72,4,80,10),fill=P[22])
 elif k==5: # shutter closed, two-frame door sheet separate below
  d.rectangle((6,4,88,88),fill=P[1]);d.rectangle((10,8,84,85),fill=P[4]);
  for y in range(10,85,7):d.line((12,y,82,y),fill=P[2]);d.line((12,y+1,82,y+1),fill=P[5])
  d.rectangle((37,67,56,71),fill=P[1]);d.rectangle((40,69,53,70),fill=P[22])
 elif k==6: # street benches/planter
  d.rectangle((7,32,88,68),fill=P[1]);
  for y in [28,37,46]:d.rectangle((8,y,86,y+6),fill=P[21]);d.line((10,y,84,y),fill=P[23]);
  for x in [16,74]:d.rectangle((x,53,x+5,75),fill=P[4])
 else: # threshold hazard mat, metal bollard
  d.rectangle((10,20,86,65),fill=P[1]);d.rectangle((13,23,83,61),fill=P[4]);
  for x in range(15,80,12):d.line((x,24,x-7,60),fill=P[23],width=4)
  d.ellipse((35,65,61,77),fill=P[1]);d.rectangle((39,35,56,70),fill=P[4]);d.rectangle((39,41,56,47),fill=P[23]);d.ellipse((39,30,56,40),fill=P[5])
 props.paste(im,(k*96,0))
props.save(OUT/'props.png')
# Narrow sliding gate: locked, unlocked and open; actual state alters collision.
doors=Image.new('RGBA',(96,96))
for frame in range(3):
 d=ImageDraw.Draw(doors);x=frame*32
 d.rectangle((x,0,x+31,95),fill=P[1]);d.rectangle((x+2,0,x+29,95),fill=P[4]);
 if frame<2:
  for y in range(3,94,8):d.line((x+4,y,x+27,y),fill=P[2]);d.line((x+4,y+1,x+27,y+1),fill=P[5])
  d.rectangle((x+11,43,x+22,53),fill=P[1]);d.rectangle((x+19,44,x+21,47),fill=P[29 if frame==0 else 12])
 else:
  d.rectangle((x+5,0,x+26,95),fill=P[1]);d.line((x+4,0,x+4,95),fill=P[12]);d.line((x+28,0,x+28,95),fill=P[12])
doors.save(OUT/'doors.png')
# Tile world uses same collision JSON as engine. Design is not the P02 arena.
data=json.loads((ROOT/'game/resources/chapters/missed_fight.json').read_text())
world=Image.new('RGB',tuple(data['world_size']),P[1])
for y in range(0,640,32):
 for x in range(0,1152,32):
  t=((x//32+y//32)%4) if x<368 else (4+(x//32+y//32)%4 if x<976 else 8+(x//32+y//32)%4)
  world.paste(atlas.crop(((t%8)*32,(t//8)*32,(t%8)*32+32,(t//8)*32+32)),(x,y))
d=ImageDraw.Draw(world)
for x,y,w,h in data['walls']:
 for yy in range(y,y+h,32):
  for xx in range(x,x+w,32):
   t=14 if x<400 else 13
   block=atlas.crop(((t%8)*32,(t//8)*32,(t%8)*32+min(32,x+w-xx),(t//8)*32+min(32,y+h-yy)))
   world.paste(block,(xx,yy))
 d.line((x,y+h-1,x+w-1,y+h-1),fill=P[12 if x<400 else 18],width=2)
# Fixtures on explicit walls, two broad obstacles are rendered as complete prop banks.
placements=[(0,144,32),(1,240,400),(1,256,32),(2,48,70),(3,512,352),(3,608,352),(4,736,192),(4,800,224),(5,464,32),(6,1020,320),(7,1008,32)]
for k,x,y in placements:world.paste(props.crop((k*96,0,(k+1)*96,96)),(x,y),props.crop((k*96,0,(k+1)*96,96)))
d=ImageDraw.Draw(world)
# Club mural on the inaccessible north wall: deliberate mountain ridge and neon ring.
d.polygon([(408,27),(438,5),(460,19),(483,0),(521,28),(554,8),(588,30)],fill=P[13]);d.line([(408,26),(438,6),(460,20),(483,1),(521,29),(554,9),(588,31)],fill=P[15],width=2)
for x in range(432,928,64):
 d.rectangle((x,17,x+30,20),fill=P[18]);d.rectangle((x,21,x+30,23),fill=P[17])
# Deliberate wet footprints lead out, no random visual content.
for x,y in [(75,378),(85,397),(73,416),(83,435)]:d.ellipse((x,y,x+5,y+9),fill=P[9])
world.save(OUT/'world.png')
files=[OUT/f for f in ['tiles.png','props.png','doors.png','world.png']]
manifest={'schema':1,'author':'Codex; original explicit pixel drawings in render.py','method':'Native integer raster drawings with Pillow; no source photo, external generator, borrowed art, resampling or palette quantization','palette':PAL,'tile_size':[32,32],'prop_cell':[96,96],'door_cell':[32,96],'door_frames':['locked','unlocked','open'],'placements':placements,'approval':'Independent art/visual review pending','files':[{'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':Image.open(p).size} for p in files]}
(OUT/'atlas.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(HERE/'provenance.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
