from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import hashlib,json
ROOT=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0')
WORK=ROOT/'.autopilot/worktrees/P06'
OUT=ROOT/'reports/phases/P06/art-c09-gabar-source-01'
SRC=WORK/'assets/source_art/npc_styles/gabar'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,data):
 p=OUT/name
 assert not p.exists(), str(p)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
paths=[WORK/p for p in ['AGENTS.md','README.md','docs/ART_BIBLE.md','docs/SECURITY_AND_RIGHTS.md','planning/PHASES.md','specs/P06_COMBAT_ACCEPTANCE.md','planning/P06_C09_TASKS.md','game/assets/art/enemies/atlas.json','game/assets/art/combat_polish/atlas.json','game/assets/art/characters/gabar/finisher.json','game/assets/art/characters/gabar/finisher_sheet.png']]
paths+=list(SRC.rglob('*'))
paths=[p for p in paths if p.is_file()]
for kind in ['patrol','rusher','shooter']:
 paths+=[WORK/f'game/assets/art/enemies/{kind}_sheet.png']
 for suffix in ['finishers','finishers_reduced','reactions','reactions_reduced']:
  paths+=[WORK/f'game/assets/art/combat_polish/{kind}_{suffix}.png']
for report,names in [('art-npc-style-audit-01',['audit.md','decision.json','proposed-budget.json','FINAL_HASHES.json']),('gameplay-npc-style-audit-01',['review.md','decision.json','packet-hashes.json'])]:
 paths += [ROOT/'reports/phases/P06'/report/n for n in names]
paths=sorted(set(paths))
write('source-freeze.json',{'scope':'exact read inputs; not entire WORK freeze','files':[{'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]})
src=Image.open(SRC/'source-v2/master.png').convert('RGBA'); native=Image.open(SRC/'preview-v2/gabar_npc_native.png').convert('RGBA')
manifest=json.loads((SRC/'preview-v2/manifest.json').read_text())
pal=json.loads((WORK/'game/assets/art/enemies/atlas.json').read_text())['palette']['rgb_hex']+['#ffe4a3','#936241','#ce9a62']
colors=[tuple(bytes.fromhex(c[1:])) for c in pal]
pp=Image.new('P',(1,1));pp.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
frames=[]; reconstructed=Image.new('RGBA',native.size)
for row in range(6):
 for col,direction in enumerate(['down','left','right','up']):
  cell=src.crop((256*col,256*row,256*(col+1),256*(row+1)))
  a=cell.getchannel('A'); support=a.point(lambda v:255 if v>=128 else 0); bbox=support.getbbox()
  small=cell.resize((64,64),Image.Resampling.NEAREST);a=small.getchannel('A').point(lambda v:255 if v>=128 else 0);small.putalpha(a)
  kept=small.crop((8,0,56,64));ka=kept.getchannel('A');dy=58-ka.getbbox()[3]
  q=kept.convert('RGB').quantize(palette=pp,dither=Image.Dither.NONE).convert('RGBA');q.putalpha(ka);q.paste((0,0,0,0),(0,0),ImageOps.invert(ka))
  exported=Image.new('RGBA',(48,64));exported.paste(q,(0,dy));actual=native.crop((48*col,64*row,48*(col+1),64*(row+1)))
  reconstructed.paste(exported,(col*48,row*64))
  ah=actual.getchannel('A').histogram();n=sum(ah[1:]);h=hashlib.sha256(actual.tobytes()).hexdigest()
  entry={'cell':f'R{row+1}C{col+1}','archetype':['patrol','rusher','shooter'][row//2],'role':'contact' if row%2==0 else 'release','direction':direction,'source_rect_xywh':[col*256,row*256,256,256],'source_alpha128_bbox_xyxy':bbox,'native_rect_xywh':[col*48,row*64,48,64],'native_bbox_xyxy':actual.getbbox(),'native_opaque_pixels':n,'native_alpha_values':[i for i,v in enumerate(ah) if v],'padding_crop_opaque_preserved':sum(a.histogram()[1:])==sum(ka.histogram()[1:]),'anchor_shift_dy':dy,'anchor_opaque_preserved':n==sum(ka.histogram()[1:]),'independent_reconstruction_byteexact':actual.tobytes()==exported.tobytes(),'manifest_frame_SHA_match':h==manifest['frames'][row*4+col]['native_rgba_sha256'],'rgba_sha256':h,'native_border_opaque':sum(actual.getchannel('A').crop((0,0,48,1)).histogram()[1:])+sum(actual.getchannel('A').crop((0,63,48,64)).histogram()[1:])+sum(actual.getchannel('A').crop((0,0,1,64)).histogram()[1:])+sum(actual.getchannel('A').crop((47,0,48,64)).histogram()[1:])}
  frames.append(entry)
metrics={'master_sha256':sha(SRC/'source-v2/master.png'),'native_sha256':sha(SRC/'preview-v2/gabar_npc_native.png'),'master_dimensions':src.size,'master_alpha_histogram':{str(i):v for i,v in enumerate(src.getchannel('A').histogram()) if v},'native_dimensions':native.size,'native_alpha_histogram':{str(i):v for i,v in enumerate(native.getchannel('A').histogram()) if v},'native_opaque_palette':sorted({'#%02x%02x%02x'%p[:3] for p in native.getdata() if p[3]}),'palette_subset_expected':all(p[:3] in colors for p in native.getdata() if p[3]),'native_unique_RGBA_cells':len(set(f['rgba_sha256'] for f in frames)),'all_recipe_reconstruction_matches':native.tobytes()==reconstructed.tobytes(),'source_not_binary_or_4x_pixel_master':True,'frames':frames,'mirror_checks':[]}
for row in range(6):
 l=native.crop((48,row*64,96,(row+1)*64));r=native.crop((96,row*64,144,(row+1)*64));m=ImageOps.mirror(l)
 metrics['mirror_checks'].append({'row':row+1,'LEFT_flipped_RGBA_identical_RIGHT':m.tobytes()==r.tobytes(),'limitation':'Nonidentity does not itself prove anatomically correct independent projection or handedness.'})
write('independent-metrics.json',metrics)
# Read-only diagnostic contact boards: juxtaposition only, no runtime positioning implied.
at=json.loads((WORK/'game/assets/art/combat_polish/atlas.json').read_text())
def cropref(kind,state,di,frame,group='reactions'):
 f=next(f for f in at['frames'] if f['kind']==kind and f['state']==state and f['direction']==di and f['frame']==frame and f['sheet']==kind+'_'+group+'.png')
 im=Image.open(WORK/'game/assets/art/combat_polish'/f['sheet']).convert('RGBA');x,y,w,h=f['rect'];return im.crop((x,y,x+w,y+h))
def drawcell(board,sprite,x,y,scale=3):
 bg=Image.new('RGBA',(48,64),(36,48,44,255));bg.alpha_composite(sprite);board.paste(bg.resize((48*scale,64*scale),Image.Resampling.NEAREST),(x,y))
for ki,kind in enumerate(['patrol','rusher','shooter']):
 cols=['WORLD idle','P04 restrained','P04 U contact','P04 B contact','P04 F contact','NEW contact','NEW release','P04 corpse']
 b=Image.new('RGB',(8*144+72,4*216+36),(20,24,29));d=ImageDraw.Draw(b)
 for c,label in enumerate(cols): d.text((72+c*144+3,8),label,fill='white')
 for row,di in enumerate(['down','left','right','up']):
  y=36+row*216;d.text((3,y+80),di,fill='white')
  world=Image.open(WORK/f'game/assets/art/enemies/{kind}_sheet.png').convert('RGBA').crop((0,row*64,48,(row+1)*64))
  sprites=[world,cropref(kind,'unarmed',di,0,'finishers'),cropref(kind,'unarmed',di,1,'finishers'),cropref(kind,'blunt',di,1,'finishers'),cropref(kind,'firearm',di,1,'finishers'),native.crop((row*48,ki*128,row*48+48,ki*128+64)),native.crop((row*48,ki*128+64,row*48+48,ki*128+128)),cropref(kind,'unarmed',di,2,'finishers')]
  for c,im in enumerate(sprites):drawcell(b,im,72+c*144,y)
 b.save(OUT/f'{kind}-comparison-3x.png')
# Existing player category contacts, exact source columns. Not claimed physical pair alignment.
g=Image.open(WORK/'game/assets/art/characters/gabar/finisher_sheet.png').convert('RGBA');b=Image.new('RGB',(4*192+80,4*280+36),(20,24,29));d=ImageDraw.Draw(b)
for c,label in enumerate(['Unarmed col1','Blunt col2','Firearm col4','Recovery col6']):d.text((80+c*192+2,8),label,fill='white')
for row,di in enumerate(['down','left','right','up']):
 y=36+row*280;d.text((3,y+90),di,fill='white')
 for c,col in enumerate([1,2,4,6]):drawcell(b,g.crop((col*48,row*64,col*48+48,row*64+64)),80+c*192,y,4)
b.save(OUT/'gabar-category-contacts-4x.png')
print(json.dumps({'inputs':len(paths),'cells':len(frames),'recipe_exact':metrics['all_recipe_reconstruction_matches'],'native_colors':len(metrics['native_opaque_palette']),'partial_master_pixels':sum(v for i,v in enumerate(src.getchannel('A').histogram()) if 0<i<255),'report':str(OUT)},ensure_ascii=False))
