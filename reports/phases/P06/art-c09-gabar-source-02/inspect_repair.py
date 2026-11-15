from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json,hashlib,shutil
ROOT=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=ROOT/'.autopilot/worktrees/P06';O=ROOT/'reports/phases/P06/art-c09-gabar-source-02';S=W/'assets/source_art/npc_styles/gabar'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,d):
 p=O/n;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
files=list((S/'source-v3').iterdir())+list((S/'preview-v3').iterdir())+[S/'assemble_source_v3.py',S/'pack_source_v3.py',S/'source-v2/master.png',S/'preview-v2/gabar_npc_native.png',S/'preview-v2/manifest.json']+[W/p for p in ['AGENTS.md','docs/ART_BIBLE.md','specs/P06_COMBAT_ACCEPTANCE.md','planning/P06_C09_TASKS.md','game/assets/art/enemies/atlas.json','game/assets/art/combat_polish/atlas.json','game/assets/art/characters/gabar/finisher_sheet.png','game/assets/art/characters/gabar/finisher.json']]
for k in ['patrol','rusher','shooter']:
 files += [W/f'game/assets/art/enemies/{k}_sheet.png',W/f'game/assets/art/combat_polish/{k}_finishers_reduced.png']
files += [ROOT/'reports/phases/P06/art-c09-gabar-source-01'/p for p in ['decision.json','review.md','cell-review.json','FINAL_HASHES.json']]
files=sorted(set(files));write('source-freeze.json',{'scope':'Exact reviewed file SHA, not full WORK freeze','files':[{'path':str(p.relative_to(ROOT)),'sha256':h(p),'bytes':p.stat().st_size} for p in files]})
for p in files:
 q=O/'source-snapshot'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);assert not q.exists();shutil.copyfile(p,q)
old=Image.open(S/'source-v2/master.png').convert('RGBA');raw=Image.open(S/'source-v3/raw-edit.png').convert('RGBA');master=Image.open(S/'source-v3/master.png').convert('RGBA');native=Image.open(S/'preview-v3/gabar_npc_native.png').convert('RGBA');previous=Image.open(S/'preview-v2/gabar_npc_native.png').convert('RGBA')
assembly=json.loads((S/'source-v3/assembly.json').read_text());manifest=json.loads((S/'preview-v3/manifest.json').read_text());pal=json.loads((W/'game/assets/art/enemies/atlas.json').read_text())['palette']['rgb_hex']+['#ffe4a3','#936241','#ce9a62'];colors=[tuple(bytes.fromhex(p[1:])) for p in pal];pimg=Image.new('P',(1,1));pimg.putpalette([v for c in colors for v in c]+list(colors[0])*(256-len(colors)))
frames=[];reconstructed=Image.new('RGBA',native.size)
for r in range(6):
 for c,di in enumerate(['down','left','right','up']):
  rect=(c*256,r*256,c*256+256,r*256+256);cell=master.crop(rect);replaced=r%2==0 or (r in [3,5] and c==0);expected=(raw if replaced else old).crop(rect);support=cell.getchannel('A').point(lambda v:255 if v>=128 else 0);bbox=support.getbbox();assembly_exact=cell.tobytes()==expected.tobytes();size=None;x=None
  if r%2==0:
   cell.putalpha(support);whole=cell.crop(bbox);size=(round(whole.width*.24),round(whole.height*.24));small=whole.resize(size,Image.Resampling.NEAREST);kept=Image.new('RGBA',(48,64));x=min(max(1,24+round((bbox[0]-128)*.24)),47-size[0]);kept.paste(small,(x,0));embed_preserved=sum(kept.getchannel('A').histogram()[1:])==sum(small.getchannel('A').histogram()[1:])
  else:
   small=cell.resize((64,64),Image.Resampling.NEAREST);a=small.getchannel('A').point(lambda v:255 if v>=128 else 0);small.putalpha(a);kept=small.crop((8,0,56,64));embed_preserved=sum(kept.getchannel('A').histogram()[1:])==sum(a.histogram()[1:])
  a=kept.getchannel('A');dy=58-a.getbbox()[3];limited=kept.convert('RGB').quantize(palette=pimg,dither=Image.Dither.NONE).convert('RGBA');limited.putalpha(a);limited.paste((0,0,0,0),(0,0),ImageOps.invert(a));out=Image.new('RGBA',(48,64));out.paste(limited,(0,dy));reconstructed.paste(out,(c*48,r*64));actual=native.crop((c*48,r*64,c*48+48,r*64+64));retained=not replaced
  frames.append({'cell':f'R{r+1}C{c+1}','archetype':['patrol','rusher','shooter'][r//2],'role':'contact' if r%2==0 else 'release','direction':di,'new_or_retained':'new-wholefigure' if replaced else 'exact-retained-v2','source_rect_xyxy':rect,'source_alpha128_bounds':bbox,'contact_NN_target_size':size,'contact_wholebbox_embed_x':x,'whole_assembly_exact':assembly_exact,'assembly_metadata_SHA_exact':hashlib.sha256(master.crop(rect).tobytes()).hexdigest()==assembly['cells'][r*4+c]['rgba_sha256'],'opaque_sampling_preserved_on_embed_crop':embed_preserved,'opaque_sampling_preserved_on_anchor':sum(out.getchannel('A').histogram()[1:])==sum(a.histogram()[1:]),'native_bounds':actual.getbbox(),'native_rgba_sha256':hashlib.sha256(actual.tobytes()).hexdigest(),'independent_export_exact':out.tobytes()==actual.tobytes(),'native_retained_exact':actual.tobytes()==previous.crop((c*48,r*64,c*48+48,r*64+64)).tobytes() if retained else None})
write('independent-metrics.json',{'raw_sha256':h(S/'source-v3/raw-edit.png'),'master_sha256':h(S/'source-v3/master.png'),'native_sha256':h(S/'preview-v3/gabar_npc_native.png'),'new_wholefigures':sum(f['new_or_retained']=='new-wholefigure' for f in frames),'retained_wholefigures':sum(f['new_or_retained']=='exact-retained-v2' for f in frames),'native_unique_RGBA':len(set(f['native_rgba_sha256'] for f in frames)),'whole_assembly_all_exact':all(f['whole_assembly_exact'] for f in frames),'independent_export_byteexact':native.tobytes()==reconstructed.tobytes(),'retained10_native_all_exact':all(f['native_retained_exact'] is not False for f in frames),'master_alpha_values':[i for i,v in enumerate(master.getchannel('A').histogram()) if v],'native_alpha_histogram':{str(i):v for i,v in enumerate(native.getchannel('A').histogram()) if v},'native_palette_colors':sorted({'#%02x%02x%02x'%px[:3] for px in native.get_flattened_data() if px[3]}),'palette_subset':all(px[:3] in colors for px in native.get_flattened_data() if px[3]),'frames':frames})
def drawcell(b,im,x,y,s=4):
 bg=Image.new('RGBA',(48,64),(36,48,44,255));bg.alpha_composite(im);b.paste(bg.resize((48*s,64*s),Image.Resampling.NEAREST),(x,y))
b=Image.new('RGB',(4*192+90,4*280+30),(20,24,29));d=ImageDraw.Draw(b)
for c,t in enumerate(['P04 shooter U-contact','v3 shooter contact','v3 rusher contact','v3 shooter release']):d.text((90+c*192,8),t,fill='white')
ref=Image.open(W/'game/assets/art/combat_polish/shooter_finishers_reduced.png').convert('RGBA')
for r,di in enumerate(['down','left','right','up']):
 y=30+r*280;d.text((5,y+100),di,fill='white')
 ims=[ref.crop((48,r*64,96,r*64+64)),native.crop((r*48,256,r*48+48,320)),native.crop((r*48,128,r*48+48,192)),native.crop((r*48,320,r*48+48,384))]
 for c,im in enumerate(ims):drawcell(b,im,90+c*192,y)
b.save(O/'weapon-identity-comparison-4x.png')
# Raw/master wholecell views, not cut-out or reconstructed weapon pieces.
b=Image.new('RGB',(4*256,2*280+40),(20,24,29));d=ImageDraw.Draw(b)
for c in range(4):
 d.text((c*256+3,7),f'Raw shooter contact C{c+1}',fill='white');b.paste(raw.crop((c*256,1024,c*256+256,1280)),(c*256,30))
 d.text((c*256+3,300),f'Native contact C{c+1} 4x',fill='white');drawcell(b,native.crop((c*48,256,c*48+48,320)),c*256+30,322)
b.save(O/'shooter-source-native-wholecells.png')
print(json.dumps({'files':len(files),'export_exact':native.tobytes()==reconstructed.tobytes(),'retained10_exact':all(f['native_retained_exact'] is not False for f in frames),'new':14,'retained':10},ensure_ascii=False))
