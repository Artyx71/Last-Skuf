from pathlib import Path
from PIL import Image,ImageDraw
import json
W=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0/.autopilot/worktrees/P06');O=Path(__file__).resolve().parent;r=json.loads((W/'reports/phases/P06/timka-present-01/native-01/movie/result.json').read_text())
def render(label,picks):
 board=Image.new('RGB',(len(picks)*216,310),(225,228,220));draw=ImageDraw.Draw(board)
 for i,t in enumerate(picks):
  n=t['tick']-1;im=Image.open(O/'movie_frames'/('frame_'+str(n+1).zfill(4)+'.png')).convert('RGB');x,y=t['visual_origin'];piece=im.crop(((round(x)-36)*2,(round(y)-40)*2,(round(x)+36)*2,(round(y)+48)*2)).resize((216,264),Image.Resampling.NEAREST);board.paste(piece,(i*216,42));draw.text((i*216+3,2),t['animation']+' f'+str(t['frame']),fill=(70,30,30));draw.text((i*216+3,18),'tick'+str(t['tick'])+' video n'+str(n),fill=(70,30,30))
 board.save(O/(label+'_ALIGNED.png'))
for seg in ['disengage_down','disengage_left','disengage_right','disengage_up']:
 a=[t for t in r['trace'] if t['segment']==seg and t['action_kind']=='disengage'];picks=[]
 for phase in range(6):
  matches=[t for t in a if t['action_frame']==phase];picks.append(matches[len(matches)//2])
 render(seg+'_movie_six_phases',picks)
for seg in ['interrupt_hurt','interrupt_death']:
 a=[t for t in r['trace'] if t['segment']==seg];picks=[];last=None
 for t in a:
  key=t['animation'],t['frame']
  if key!=last:picks.append(t);last=key
 render(seg+'_movie_transitions',picks)
(O/'filmstrip_alignment.json').write_text(json.dumps({'basis':'movie_tick_pixel_alignment.json','video_n':'saved_physics_tick - 1','samples':24,'global_mean_opaque_pixel_RGB_difference':{'-2':25.400,'-1':12.067,'0':25.507,'1':30.019,'2':31.979},'initial_unaligned_preview_boards':'Not acceptance evidence; retained only as reviewer work-in-progress, names lack _ALIGNED suffix','final_evidence_suffix':'_ALIGNED.png','no_source_sprites_pasted_into_recording':True},indent=2)+'\n')
print('6 corrected aligned actual-film boards saved')
