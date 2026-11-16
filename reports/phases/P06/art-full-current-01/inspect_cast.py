from pathlib import Path
from PIL import Image,ImageDraw,ImageChops
import json,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01';D=O/'cast-boards';D.mkdir(exist_ok=True)
records=[];emotions=['neutral','angry','surprise','hurt','catchphrase']
for actor in ['gabar','olezhka','timka','ryzhik','tega','pasha','kaban','ellana','elya']:
 sheet=Image.open(W/'game/assets/art/characters'/actor/'portraits.png').convert('RGBA');board=Image.new('RGB',(1800,5*360+35),(21,25,32));draw=ImageDraw.Draw(board)
 draw.text((5,7),actor+' NORMAL / LARGE actual text-region captures; original full images remain bound',fill='white')
 for row,emotion in enumerate(emotions):
  for col,mode in enumerate(['cast','cast_large_text']):
   p=W/'reports/phases/P06/native-remaining5-02'/mode/(actor+'_'+emotion+'.png');original=Image.open(p).convert('RGB');logical=original.resize((640,360),Image.Resampling.NEAREST);box=(20,128,180,288);actual=logical.crop(box);src=sheet.crop((row*160,0,row*160+160,160));expected=Image.new('RGBA',(160,160),actual.getpixel((0,0))+(255,));expected.alpha_composite(src);diff=ImageChops.difference(actual,expected.convert('RGB'));pixels=sum(px!=(0,0,0) for px in diff.get_flattened_data())
   y=35+row*360;draw.text((col*900+5,y),emotion+' '+mode,fill='white');text=logical.crop((185,118,635,286)).resize((900,336),Image.Resampling.NEAREST);board.paste(text,(col*900,y+20))
   records.append({'actor':actor,'emotion':emotion,'mode':mode,'path':str(p.relative_to(W)),'SHA':hashlib.sha256(p.read_bytes()).hexdigest(),'original_size':original.size,'native_portrait_rect':[20,128,160,160],'portrait_RGB_difference_pixels':pixels,'source_frame_index':row})
 board.save(D/(actor+'-normal-large.png'))
(O/'cast-pixel-comparison.json').write_text(json.dumps({'captures':records,'count':len(records),'all_portrait_pixels_exact':all(r['portrait_RGB_difference_pixels']==0 for r in records),'source_native_RGBA_for_9sets':81,'captured_static_expressions_each':5,'static_portraits_not_multiframe_animation':True,'raw_photos_copied':False},ensure_ascii=False,indent=2)+'\n')
print({'captures':len(records),'all90_portraits_exact':all(r['portrait_RGB_difference_pixels']==0 for r in records),'bad':[(r['actor'],r['mode'],r['emotion'],r['portrait_RGB_difference_pixels']) for r in records if r['portrait_RGB_difference_pixels']]})
