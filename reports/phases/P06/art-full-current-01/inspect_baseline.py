from pathlib import Path
from PIL import Image,ImageDraw
import json,subprocess,hashlib
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';O=R/'reports/phases/P06/art-full-current-01';B=W/'reports/phases/P06/combat-movie-recovery-01/combat_baseline';D=O/'baseline';D.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();full=json.loads((B/'full_replay.json').read_text());red=json.loads((B/'reduced_replay.json').read_text());movie=json.loads((B/'movie_replay.json').read_text());records=[]
def tile(record,mode):
 p=Path(record['path']);im=Image.open(p).convert('RGB').resize((640,360),Image.Resampling.NEAREST);x,y=record['player_at'];box=(round(x)-80,round(y)-90,round(x)+80,round(y)+30);records.append({'mode':mode,'name':record['name'],'path':str(p.relative_to(W)),'sha256':sha(p),'tick':record['tick'],'draw_frame':record.get('draw_frame'),'player_at':record['player_at'],'diagnostic_box_logical':box});return im.crop(box).resize((320,240),Image.Resampling.NEAREST)
def get(d,name):return next(c for c in d['captures'] if c['name']==name)
for cat in ['unarmed','blunt','sharp','firearm','environmental']:
 board=Image.new('RGB',(1600,4*265+30),(21,25,32));draw=ImageDraw.Draw(board);draw.text((4,6),'FRESH C5 '+cat+' / Full windup-contact-recovery-clearcorpse / Reduced contact',fill='white')
 for r,di in enumerate(['down','left','right','up']):
  for c,phase in enumerate(['windup','contact','recovery','corpse_clear','contact']):
   d=red if c==4 else full;im=tile(get(d,cat+'_'+di+'_'+phase),'reduced' if c==4 else 'full');xx=c*320;yy=30+r*265;board.paste(im,(xx,yy));draw.text((xx+3,yy+243),di+' '+('Reduced ' if c==4 else '')+phase,fill='white')
 board.save(D/('finisher-'+cat+'-FullReduced.png'))
for kind in ['patrol','rusher','shooter']:
 for title,phases in [('active',['telegraph','attack','recovery']),('react',['hurt_contact','hurt_settled','stun_contact','stun_settled']),('fall',['knockdown_contact','knockdown_settled','death_contact','death_settled'])]:
  board=Image.new('RGB',(1280,len(phases)*265+30),(21,25,32));draw=ImageDraw.Draw(board);draw.text((4,6),'FRESH C5 '+kind+' '+title+' / columns playerDown Left Right Up (NPC opposite)',fill='white')
  for r,phase in enumerate(phases):
   for c,di in enumerate(['down','left','right','up']):
    im=tile(get(full,kind+'_'+di+'_'+phase),'full');xx=c*320;yy=30+r*265;board.paste(im,(xx,yy));draw.text((xx+3,yy+243),di+' '+phase,fill='white')
  board.save(D/(kind+'-'+title+'-actual.png'))
# Source-limited supplement supplies seven archetype/category pairs missing from the legacy P04 cases.
S=W/'reports/phases/P06/native-remaining5-02/npc_baseline';supp=json.loads((S/'result.json').read_text());sn=[]
for mode in ['full','reduced']:
 pairs=sorted(set(c['name'].rsplit('_',1)[0] for c in supp['captures'] if '_'+mode+'_' in c['name']));board=Image.new('RGB',(960,len(pairs)*265+30),(21,25,32));draw=ImageDraw.Draw(board);draw.text((4,6),'ACTUAL NPC CATEGORY SUPPLEMENT '+mode+' windup/contact/corpse',fill='white')
 for r,prefix in enumerate(pairs):
  for c,phase in enumerate(['windup','contact','corpse']):
   cap=next(x for x in supp['captures'] if x['name']==prefix+'_'+phase);p=Path(cap['path']);im=Image.open(p).convert('RGB').resize((640,360),Image.Resampling.NEAREST);# all declared player-right/target-left positions are300/320,240
   im=im.crop((225,150,385,270)).resize((320,240),Image.Resampling.NEAREST);xx=c*320;yy=30+r*265;board.paste(im,(xx,yy));draw.text((xx+3,yy+243),prefix+' '+phase,fill='white');sn.append({'path':str(p.relative_to(W)),'sha256':sha(p),'name':cap['name'],'tick':cap['tick'],'NPCkind':cap['npc_kind'],'NPCanimation':cap['npc_animation'],'NPCframe':cap['npc_frame']})
 board.save(D/('supplement-'+mode+'-actual.png'))
# Decode completed actual C5 Movie at producer's draw_frame labels; include all category/dir contact and clear terminal frames.
selected=[c for c in movie['captures'] if any(c['name']==cat+'_'+di+'_'+phase for cat in ['unarmed','blunt','sharp','firearm','environmental'] for di in ['down','left','right','up'] for phase in ['windup','contact','corpse_clear'])];frames=sorted(set(c['draw_frame'] for c in selected));out=D/'decoded-c5';out.mkdir(exist_ok=True);expr='+'.join('eq(n'+chr(92)+','+str(t)+')' for t in frames);cmd=['ffmpeg','-hide_banner','-loglevel','error','-threads','1','-i',str(B/'combat_polish.mp4'),'-vf','select='+expr,'-fps_mode','passthrough',str(out/'frame-%04d.png')];subprocess.run(cmd,check=True);images=sorted(out.glob('frame-*.png'));assert len(images)==len(frames),(len(images),len(frames));fm=dict(zip(frames,images));rec=[]
for cat in ['unarmed','blunt','sharp','firearm','environmental']:
 board=Image.new('RGB',(960,4*265+30),(21,25,32));draw=ImageDraw.Draw(board);draw.text((4,6),'COMPLETED ACTUAL C5 MOVIE '+cat+' windup/contact/clearcorpse',fill='white')
 for r,di in enumerate(['down','left','right','up']):
  for c,phase in enumerate(['windup','contact','corpse_clear']):
   cap=next(x for x in selected if x['name']==cat+'_'+di+'_'+phase);p=fm[cap['draw_frame']];im=Image.open(p).convert('RGB').resize((640,360),Image.Resampling.NEAREST);x,y=cap['player_at'];im=im.crop((round(x)-80,round(y)-90,round(x)+80,round(y)+30)).resize((320,240),Image.Resampling.NEAREST);xx=c*320;yy=30+r*265;board.paste(im,(xx,yy));draw.text((xx+3,yy+243),di+' '+phase+' n'+str(cap['draw_frame']),fill='white');rec.append({'name':cap['name'],'draw_frame':cap['draw_frame'],'decoded':str(p.relative_to(O))})
 board.save(D/('movie-'+cat+'-actual.png'))
(O/'baseline-inspection.json').write_text(json.dumps({'current_source_binding':str((B/'source_hashes.json').relative_to(W)),'actual_native_samples':records,'supplement_samples':sn,'movie_samples':rec,'movie_sha256':sha(B/'combat_polish.mp4'),'movie_decode_command':cmd,'completed_C5_child_modes':['full_replay','reduced_replay','movie_replay','linux_export_replay','wine_export_replay'],'outer_job_exit130_not_PASSED':True,'old_partial_movie_480_not_accepted':True,'NPC_new_style_C09_deferred':True},ensure_ascii=False,indent=2)+'\n');print({'C5_native_samples':len(records),'supplement_samples':len(sn),'actual_C5_decoded_frames':len(rec)})
