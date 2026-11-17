"""Read-only Tega source inspection; whole-cell diagnostic composites only."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4];WORK=ROOT/'.autopilot/worktrees/P06';OUT=Path(__file__).parent
sys.path.insert(0,str(WORK/'assets/source_art/characters'));from pack_portraits import PALETTE
PFX='tega_world_preflight_v1';folder=WORK/'assets/source_art/characters/tega';master=folder/'world_master_v1.png';native=folder/'world_native_v1.png';meta_path=folder/'world_manifest_v1.json';manifest=json.loads(meta_path.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(master)=='93bbe92c89a48fce9e6969e63b21923e7a449fdfbc1a14eb54e26bab62222754';assert sha(native)=='e3b52ae7b4611b73e77c830155b973614c237cfe399095552ab5e8ca2138871c'
assert manifest['master_sha256']==sha(master) and manifest['sha256']==sha(native);assert manifest['actor_id']=='tega' and manifest['kind']=='world' and manifest['source_cells']==32 and manifest['frame_size']==[48,64] and manifest['pivot']==[24,58]
assert manifest['packing']['palette_hex']==PALETTE and manifest['packing']['alpha_threshold']==128;assert manifest['animations_source_columns']=={'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]}
im=Image.open(master).convert('RGBA');nm=Image.open(native).convert('RGBA');assert im.size==(1536,1024) and nm.size==(384,256)
colors=[tuple(bytes.fromhex(h)) for h in PALETTE];pal=Image.new('P',(1,1));pal.putpalette([c for x in colors for c in x]+list(colors[0])*(256-len(colors)));directions=['down','left','right','up'];rows=[];cells=[]
for row,direction in enumerate(directions):
 ref=im.crop((0,row*256,192,(row+1)*256)).resize((48,64),Image.Resampling.NEAREST);ref_alpha=ref.getchannel('A').point(lambda x:255 if x>=128 else 0);dy=58-ref_alpha.getbbox()[3];rows.append({'direction':direction,'fixed_native_dy':dy})
 for col in range(8):
  rect=[col*192,row*256,(col+1)*192,(row+1)*256];src=im.crop(rect);opaque=src.getchannel('A').point(lambda x:255 if x>=128 else 0);bounds=opaque.getbbox();small=src.resize((48,64),Image.Resampling.NEAREST);alpha=small.getchannel('A').point(lambda x:255 if x>=128 else 0);q=small.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');q.putalpha(alpha);q.paste((0,0,0,0),(0,0),ImageOps.invert(alpha));frame=Image.new('RGBA',(48,64));frame.paste(q,(0,dy));actual=nm.crop((col*48,row*64,(col+1)*48,(row+1)*64));saved=manifest['frames'][row*8+col];rgba=hashlib.sha256(actual.tobytes()).hexdigest();assert rgba==saved['rgba_sha256'];assert frame.tobytes()==actual.tobytes();assert saved['source_rect']==rect and saved['translate_native']==[0,dy];assert saved['column']==col and saved['direction']==direction
  before=sum(1 for a in alpha.get_flattened_data() if a);after=sum(1 for a in frame.getchannel('A').get_flattened_data() if a);assert before==after
  cells.append({'index':row*8+col,'direction':direction,'column':col,'rgba_sha256':rgba,'exact_reconstruction':True,'source_rect':rect,'source_opaque_bounds':list(bounds),'source_gutters':[bounds[0],bounds[1],192-bounds[2],256-bounds[3]],'native_bounds':list(actual.getbbox()),'native_height':actual.getbbox()[3]-actual.getbbox()[1],'native_opaque_pixels':after,'alignment_opaque_loss':before-after,'native_translation':[0,dy]})
font=ImageFont.load_default()
def label(board,text,x,y):ImageDraw.Draw(board).text((x,y),text,fill='#ffc982',font=font)
for row,direction in enumerate(directions):
 board=Image.new('RGBA',(1536,560),'#101417')
 for bgi,bg in enumerate(['#f0e6d0','#182529']):
  for col in range(8):
   cell=nm.crop((col*48,row*64,(col+1)*48,(row+1)*64)).resize((192,256),Image.Resampling.NEAREST);tile=Image.new('RGBA',cell.size,bg);tile.alpha_composite(cell);board.paste(tile,(col*192,24+bgi*280));label(board,direction+' col'+str(col),col*192+4,bgi*280+5)
 board.save(OUT/(PFX+'_'+direction+'_light_dark_4x.png'))
 if row in [1,2]:
  board=Image.new('RGBA',(1536,1072),'#101417')
  for bgi,bg in enumerate(['#e8dcc7','#182529']):
   for i,col in enumerate([2,4,6,7]):
    cell=im.crop((col*192,row*256,(col+1)*192,(row+1)*256)).resize((384,512),Image.Resampling.NEAREST);tile=Image.new('RGBA',cell.size,bg);tile.alpha_composite(cell);board.paste(tile,(i*384,24+bgi*536));label(board,direction+' SOURCE wholecell col'+str(col),i*384+4,bgi*536+5)
  board.save(OUT/(PFX+'_'+direction+'_source_2_4_6_7_wholecell2x.png'))
  guide=Image.open(WORK/'assets/source_art/characters/olezhka/world_native_v2b.png').convert('RGBA');board=Image.new('RGBA',(1152,816),'#172528')
  for who,image,yi in [('TEGA',nm,0),('OLEZHKA camera/gait reference',guide,408)]:
   for i,col in enumerate([2,4,6,7]):
    cell=image.crop((col*48,row*64,(col+1)*48,(row+1)*64)).resize((288,384),Image.Resampling.NEAREST);board.alpha_composite(cell,(i*288,yi+24));label(board,who+' '+direction+' c'+str(col),i*288+3,yi+5)
  board.save(OUT/(PFX+'_'+direction+'_native_gait_family6x.png'))
opaque={p[:3] for p in nm.get_flattened_data() if p[3]};assert opaque.issubset(set(colors));alpha_values=sorted(set(nm.getchannel('A').get_flattened_data()));assert alpha_values==[0,255]
metrics={'schema':1,'actor_id':'tega','kind':'world','master_sha256':sha(master),'native_sha256':sha(native),'source_cells':32,'unique_rgba_drawings':len(set(c['rgba_sha256'] for c in cells)),'source_dimensions':list(im.size),'native_dimensions':list(nm.size),'opaque_palette_colors':len(opaque),'opaque_palette_hex':sorted(bytes(x).hex() for x in opaque),'alpha_values':alpha_values,'all32_exact_native_reconstruction':True,'total_alignment_opaque_loss':sum(c['alignment_opaque_loss'] for c in cells),'row_anchors':rows,'cells':cells,'phase_approval':False,'actual_godot_animation_playback_reviewed':False,'diagnostics':'Wholecells/source or NN native, light/dark composites only; no source bitmap edits'}
(OUT/(PFX+'_metrics.json')).write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:metrics[k] for k in ['unique_rgba_drawings','opaque_palette_colors','all32_exact_native_reconstruction','total_alignment_opaque_loss','row_anchors']}))
