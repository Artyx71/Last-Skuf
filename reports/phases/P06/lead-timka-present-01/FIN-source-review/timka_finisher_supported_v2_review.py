from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import json, hashlib, ast
W=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0/.autopilot/worktrees/P06')
O=Path(__file__).resolve().parent
D=W/'assets/source_art/characters/timka'
PREFIX='timka_finisher_supported_v2_'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rawsha(im):return hashlib.sha256(im.tobytes()).hexdigest()
def box(row,col,sx=48,sy=64):return col*sx,row*sy,(col+1)*sx,(row+1)*sy
recipe=json.loads((D/'finisher_v4a_assembly.json').read_text())
raw=Image.open(D/'finisher_up5_master_v4.png').convert('RGBA');base=Image.open(D/'finisher_master_v2b.png').convert('RGBA');master=Image.open(D/'finisher_master_v4a.png').convert('RGBA');native=Image.open(D/'finisher_native_v4a.png').convert('RGBA');compact=Image.open(D/'finisher_native_supported_v2.png').convert('RGBA');oldnative=Image.open(D/'finisher_native_v2b.png').convert('RGBA');oldcompact=Image.open(D/'finisher_native_supported_v1.png').convert('RGBA');world=Image.open(D/'world_native_supported_v1.png').convert('RGBA');action=Image.open(D/'action_native_supported_v1.png').convert('RGBA')
b=raw.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox();assert list(b)==recipe['complete_figure_bounds'];rb=base.crop(box(3,5,192,256)).getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox();assert list(rb)==recipe['reference_bounds'];scale=(rb[3]-rb[1])/(b[3]-b[1]);assert scale==recipe['uniform_scale'];size=(round((b[2]-b[0])*scale),round((b[3]-b[1])*scale));assert list(size)==recipe['resized_complete_figure'];pose=raw.crop(b).resize(size,Image.Resampling.NEAREST);assert rawsha(pose)==recipe['resized_rgba_sha256'];cell=Image.new('RGBA',(192,256));cell.paste(pose,tuple(recipe['placement']));assert rawsha(cell)==recipe['output_cell_rgba_sha256'];assembled=base.copy();assembled.paste(cell,(960,768));assert assembled.tobytes()==master.tobytes();assert sha(D/'finisher_master_v4a.png')==recipe['output_sha256']
changes_source=[];changes_native=[];changes_compact=[]
for i in range(32):
 r,c=divmod(i,8)
 if base.crop(box(r,c,192,256)).tobytes()!=master.crop(box(r,c,192,256)).tobytes():changes_source.append(i)
 if native.crop(box(r,c)).tobytes()!=oldnative.crop(box(r,c)).tobytes():changes_native.append(i)
for i in range(24):
 r,c=divmod(i,6)
 if compact.crop(box(r,c)).tobytes()!=oldcompact.crop(box(r,c)).tobytes():changes_compact.append(i)
assert changes_source==changes_native==[29];assert changes_compact==[21]
m=json.loads((D/'finisher_manifest_supported_v2.json').read_text());m32=json.loads((D/'finisher_manifest_v4a.json').read_text());assert m['source_column_mapping']==[0,1,2,5,6,7];assert m['source_cells']==24;assert m['dimensions']==list(compact.size)==[288,256];assert m['sha256']==sha(D/'finisher_native_supported_v2.png');assert m32['sha256']==sha(D/'finisher_native_v4a.png');assert m['master_sha256']==sha(D/'finisher_master_v4a.png')
pack_ast=ast.parse((W/'assets/source_art/characters/pack_portraits.py').read_text());palette=next(ast.literal_eval(n.value) for n in pack_ast.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PALETTE' for t in n.targets));assert palette==m32['packing']['palette_hex'];colors=[tuple(bytes.fromhex(v)) for v in palette];pal=Image.new('P',(1,1));pal.putpalette([x for col in colors for x in col]+list(colors[0])*(256-len(colors)));repacked=Image.new('RGBA',(384,256));packing_rows=[]
for r,direction in enumerate(['down','left','right','up']):
 ref=master.crop(box(r,0,192,256)).resize((48,64),Image.Resampling.NEAREST);dy=58-ref.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()[3];packing_rows.append(dy)
 for c in range(8):
  small=master.crop(box(r,c,192,256)).resize((48,64),Image.Resampling.NEAREST);a=small.getchannel('A').point(lambda v:255 if v>=128 else 0);small=small.convert('RGB').quantize(palette=pal,dither=Image.Dither.NONE).convert('RGBA');small.putalpha(a);small.paste((0,0,0,0),(0,0),ImageOps.invert(a));aligned=Image.new('RGBA',(48,64));aligned.paste(small,(0,dy));assert sum(aligned.getchannel('A').get_flattened_data())==sum(a.get_flattened_data());repacked.paste(aligned,(c*48,r*64))
assert repacked.tobytes()==native.tobytes()
frames=[]
for i,f in enumerate(m['frames']):
 r,c=divmod(i,6);scol=[0,1,2,5,6,7][c];piece=compact.crop(box(r,c));assert piece.tobytes()==native.crop(box(r,scol)).tobytes();assert f['index']==i and f['source_column']==scol and f['column']==c and f['rgba_sha256']==rawsha(piece);bounds=piece.getbbox();assert bounds and min(bounds[:2])>0 and bounds[2]<48 and bounds[3]<64;frames.append({'index':i,'direction':f['direction'],'column':c,'source_column':scol,'bounds':list(bounds),'rgba_sha256':rawsha(piece),'opaque_pixels':sum(v==255 for v in piece.getchannel('A').get_flattened_data())})
assert set(compact.getchannel('A').get_flattened_data())=={0,255};assert all(p==(0,0,0,0) for p in compact.get_flattened_data() if p[3]==0);assert set(p[:3] for p in compact.get_flattened_data() if p[3]).issubset(colors)
# Complete-cell display only; no body part extraction or retouch.
def board(cells,names,path,bg,scale=6):
 im=Image.new('RGBA',(len(cells)*48,78),bg)
 for i,(cell,name) in enumerate(zip(cells,names)):
  im.alpha_composite(cell,(i*48,14));ImageDraw.Draw(im).text((i*48+1,2),name,fill=(140,70,50,255) if bg[0]>128 else (230,225,215,255))
 im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST).save(O/(PREFIX+path))
for r,direction in enumerate(['down','left','right','up']):
 cells=[compact.crop(box(r,c)) for c in range(6)];names=['0 ready','1 palm','2 blunt','3 env','4 reset','5 clinch']
 for label,bg in [('light',(225,228,220,255)),('dark',(30,36,43,255))]:board(cells,names,f'{direction}_{label}_required6.png',bg)
 board([world.crop(box(r,0)),action.crop(box(r,0))]+cells,['WORLD0','ACTION0']+names,f'{direction}_own_family.png',(225,228,220,255),5)
 for category,contact in [('unarmed',1),('blunt',2),('environmental',3),('clinch',5)]:board([cells[0],cells[contact],cells[4]],['0 ready',str(contact)+' contact','4 reset'],f'{direction}_{category}_SOURCE_ONLY_sequence.png',(30,36,43,255),5)
board([world.crop(box(3,0)),oldcompact.crop(box(3,0)),oldcompact.crop(box(3,1)),oldcompact.crop(box(3,3)),Image.open(D/'finisher_native_v3a.png').convert('RGBA').crop(box(3,5)),compact.crop(box(3,3)),compact.crop(box(3,4))],['WORLD','ready','palm','old env','v3a env','v4 env','reset'],'up_environment_history.png',(225,228,220,255),5)
metrics={'schema':1,'reviewer':'/root/art_timka_fin_v4','source_only':True,'changed_source_indices':changes_source,'changed_native32_indices':changes_native,'changed_compact24_indices':changes_compact,'other31_source_exact':True,'other31_native32_exact':True,'other23_selected_native_exact':True,'independent_whole_pose_recipe_reconstruction':True,'independent_complete_native32_repack':True,'native32_row_dy':packing_rows,'compact_rgba_sha256':rawsha(compact),'compact_png_sha256':sha(D/'finisher_native_supported_v2.png'),'unique_cells':len(set(f['rgba_sha256'] for f in frames)),'all24_frame_hashes_match':True,'binary_alpha':True,'transparent_rgb_zero':True,'opaque_palette_colors':len({p[:3] for p in compact.get_flattened_data() if p[3]}),'native_cell_bounds_clear':True,'anatomical_reconstruction':False,'raw_photo_read':False,'runtime_playback':False,'frame_metrics':frames}
(O/(PREFIX+'source_metrics.json')).write_text(json.dumps(metrics,indent=2)+'\n')
print(json.dumps({k:v for k,v in metrics.items() if k!='frame_metrics'}))
