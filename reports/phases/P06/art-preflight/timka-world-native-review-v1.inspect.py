from pathlib import Path
from PIL import Image,ImageChops,ImageStat,ImageDraw
from functools import lru_cache
from collections import Counter,defaultdict
import json,hashlib,math,statistics,datetime
R=Path('/home/artyx/Projects/AYAY_SDD_v1.0_Codex/AYAY_SDD_v1.0');W=R/'.autopilot/worktrees/P06';B=W/'reports/phases/P06/attempt1/timka-world-native-02';O=R/'reports/phases/P06/art-preflight';D=O/'timka-world-native-review-v1-diagnostics';P='timka-world-native-review-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
validation=json.loads((B/'validation.json').read_text());assert validation['passed'] and validation['source_unchanged'] and validation['source_head']=='915e1c6b9672e55bed20d9de2bfb317ab09349aa' and validation['checks_passed']==validation['checks_total']==110 and validation['actual_captures']==40
recorded=json.loads((B/'source_hashes.json').read_text());mismatches=[n for n,h in recorded.items() if not (W/n).is_file() or sha(W/n)!=h];artifact_mismatches=[e['path'] for e in validation['artifacts'] if not (W/e['path']).is_file() or sha(W/e['path'])!=e['sha256']];assert not artifact_mismatches
live=json.loads((B/'live/result.json').read_text());movie=json.loads((B/'movie/result.json').read_text());assert all(c['passed'] for c in live['checks']) and all(c['passed'] for c in movie['checks']);assert len(live['checks'])==110 and len(movie['checks'])==70
atlaspath=W/'game/assets/art/characters/timka/world_sheet.png';assert sha(atlaspath)=='8e505380e88fb538988310a364c6b16a135cb69b94d136fe00307c8a49a99cea';atlas=Image.open(atlaspath).convert('RGBA');columns={'idle':[0,1],'walk':[2,3,4,5],'run':[6,7]};directions=['down','left','right','up'];templates={}
for row,direction in enumerate(directions):
 for state,cols in columns.items():
  for index,col in enumerate(cols):
   cell=atlas.crop((col*48,row*64,(col+1)*48,(row+1)*64));templates[(state+'_'+direction,index)]=cell

def roi(at):return (int(round(at['visual_origin'][0]-24)),int(round(at['visual_origin'][1]-32)),int(round(at['visual_origin'][0]+24)),int(round(at['visual_origin'][1]+32)))
def error(crop,template):
 stat=ImageStat.Stat(ImageChops.difference(crop.convert('RGB'),template.convert('RGB')),template.getchannel('A'));return sum(stat.mean)/3
# Lossless live PNGs prove exact rendered source pixels for all32 states/phases.
lossless=[];livecrops={}
for name,at in live['captures'].items():
 image=Image.open(B/'live'/(name+'.png')).convert('RGB');assert image.size==(640,360);crop=image.crop(roi(at));template=templates[(at['animation'],int(at['frame']))];mae=error(crop,template);lossless.append({'capture':name,'animation':at['animation'],'frame':at['frame'],'opaque_rgb_mae':mae,'exact_opaque_rgb':mae==0.0,'roi':list(roi(at))});livecrops[(at['animation'],int(at['frame']))]=crop
assert len(lossless)==32 and all(x['exact_opaque_rgb'] for x in lossless)
files=sorted((D/'decoded').glob('frame-*.png'));assert len(files)==750
@lru_cache(maxsize=96)
def film(index):
 image=Image.open(files[index]).convert('RGB');assert image.size==(1280,720);return image.resize((640,360),Image.Resampling.NEAREST)
# MovieMaker isMJPEG420at2x: compare geometry/phase with colourerror, not exactPNG.
chosen=[i for i in range(1,len(movie['trace'])-1) if movie['trace'][i]['animation']!=movie['trace'][i-1]['animation'] or movie['trace'][i]['frame']!=movie['trace'][i-1]['frame']][::3]
chosen=chosen[:60];offsets=[]
for offset in range(-6,7):
 values=[]
 for i in chosen:
  at=movie['trace'][i];index=int(at['physics_tick'])+offset
  if not 0<=index<len(files):continue
  values.append(error(film(index).crop(roi(at)),templates[(at['animation'],int(at['frame']))]))
 offsets.append({'decoded_zero_based_minus_physics_tick':offset,'samples':len(values),'mean_opaque_rgb_error':statistics.mean(values)})
best=min(offsets,key=lambda x:x['mean_opaque_rgb_error']);offset=best['decoded_zero_based_minus_physics_tick']
comparisons=[];phase_samples=defaultdict(list);registered=[]
for at in movie['trace']:
 index=int(at['physics_tick'])+offset;assert 0<=index<len(files);crop=film(index).crop(roi(at));state,direction=at['animation'].rsplit('_',1);candidates=[]
 for fi in range(len(columns[state])):candidates.append((error(crop,templates[(at['animation'],fi)]),fi))
 candidates.sort();expected_error=error(crop,templates[(at['animation'],int(at['frame']))]);comparisons.append({'physics_tick':at['physics_tick'],'decoded_frame_zero_based':index,'sequence':at['sequence'],'animation':at['animation'],'recorded_phase':at['frame'],'best_phase':candidates[0][1],'best_error':candidates[0][0],'expected_error':expected_error,'expected_is_best':candidates[0][1]==int(at['frame'])});phase_samples[(at['animation'],int(at['frame']))].append(index)
 registered.append((at,index,crop))
# Actual trace cadence and input/velocity facts, distinct from rendered FPS.
tracefacts={};cadence={}
for label,data in [('live',live),('movie',movie)]:
 samples=data['trace'];inputerrors=[];griderrors=[];step_errors=[];same_animation_dwells=defaultdict(list);last=None;run_start=None
 for i,at in enumerate(samples):
  state,direction=at['animation'].rsplit('_',1);direction_vector={'down':[0,1],'left':[-1,0],'right':[1,0],'up':[0,-1]}[direction];expected_input=[0.0,0.0] if state=='idle' else list(map(float,direction_vector));expected_velocity=[v*84*(1.44 if state=='run' else 1) for v in expected_input]
  if at['input_vector']!=expected_input or at['run_pressed']!=(state=='run') or max(abs(at['velocity'][j]-expected_velocity[j]) for j in range(2))>0.0001:inputerrors.append(i)
  griderrors.append(max(abs(v-round(v)) for v in at['visual_origin']))
  if i and at['sequence']=='continuous' and samples[i-1]['sequence']=='continuous':
   old=samples[i-1];dt=int(at['physics_tick'])-int(old['physics_tick']);dx=math.dist(at['position'],old['position']);
   if dx>84*1.44*dt/60+0.001:step_errors.append(i)
  key=(at['sequence'],at['animation'],int(at['frame']))
  if last is None:run_start=at['physics_tick']
  elif key!=last:
   prev=samples[i-1]
   if at['sequence']==prev['sequence'] and at['animation']==prev['animation']:same_animation_dwells[at['animation']].append(int(at['physics_tick'])-int(run_start))
   run_start=at['physics_tick']
  last=key
 tracefacts[label]={'samples':len(samples),'input_velocity_mismatches':inputerrors,'max_visual_grid_error':max(griderrors),'continuous_unbounded_step_samples':step_errors,'fractional_positions_observed':any(any(abs(v-round(v))>0.1 for v in a['position']) for a in samples),'focus_true_samples':sum(a['window_focused'] is True for a in samples),'focus_events':data['focus_events'],'no_focus_requested':data['movie_window_no_focus_requested']}
 cadence[label]={n:dict(Counter(v)) for n,v in same_animation_dwells.items()}
# Proof artifacts: source/native pixelregistered crops use REAL viewport and film.
artifacts=[]
for row,direction in enumerate(directions):
 board=Image.new('RGB',(8*48*6,64*6),(36,48,44));ci=0
 for state in ['idle','walk','run']:
  for fi in range(len(columns[state])):
   crop=livecrops[(state+'_'+direction,fi)];board.paste(crop.resize((288,384),Image.Resampling.NEAREST),(ci*288,0));ci+=1
 name=P+'-'+direction+'-live-all8-ground-registered-6x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
# Whole registered frame intervals for actualrun andwalk cycles, everythirdsample.
for direction,state in [('right','run'),('left','run'),('down','walk'),('up','run')]:
 selected=[x for x in registered if x[0]['sequence']=='grid' and x[0]['animation']==state+'_'+direction][::3]
 board=Image.new('RGB',(len(selected)*48*4,64*4),(36,48,44))
 for ci,(at,index,crop) in enumerate(selected):board.paste(crop.resize((192,256),Image.Resampling.NEAREST),(ci*192,0))
 name=P+'-'+state+'-'+direction+'-actual-movie-every3samples-4x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
# Continuous joins: actuallast2/first3 samples for each of7 unresetboundaries.
cont=[x for x in registered if x[0]['sequence']=='continuous'];boundaries=[i for i in range(1,len(cont)) if cont[i][0]['animation']!=cont[i-1][0]['animation']];assert len(boundaries)==7
board=Image.new('RGB',(5*48*5,len(boundaries)*64*5),(36,48,44));joins=[]
for ri,index in enumerate(boundaries):
 selected=cont[max(0,index-2):index+3];joins.append({'from':cont[index-1][0]['animation'],'to':cont[index][0]['animation'],'movie_frames':[x[1] for x in selected],'physics_ticks':[x[0]['physics_tick'] for x in selected]})
 for ci,(_,_,crop) in enumerate(selected):board.paste(crop.resize((240,320),Image.Resampling.NEAREST),(ci*240,ri*320))
name=P+'-all7-continuous-joins-actual-movie-5x.png';assert not (O/name).exists();board.save(O/name);artifacts.append(name)
frameinventory={p.name:sha(p) for p in files};(D/'decoded-inventory.json').write_text(json.dumps(frameinventory,indent=2)+'\n')
metrics={'schema':1,'reviewer':'/root/art_timka_recovery','source_head':validation['source_head'],'scope':'ACTUAL_NATIVE_TIMKA_WORLD_MOVEMENT_CAPTURED_CONFIGURATION_ONLY','phase_approval':False,'runtime_combat_abilities_approval':False,'source_recorded_entries':len(recorded),'source_recorded_current_mismatches':mismatches,'author_artifacts':len(validation['artifacts']),'author_artifact_mismatches':artifact_mismatches,'native_world_sha256':sha(atlaspath),'source_world_match':sha(atlaspath)==sha(W/'assets/source_art/characters/timka/world_native_v4c.png'),'live_opaque_source_matches':lossless,'live_all32_opaque_pixels_exact':all(x['exact_opaque_rgb'] for x in lossless),'decoded_avi_frames':len(files),'avi_dimensions':[1280,720],'movie_codec':'MJPEG YUV420; lossy colour, not pixel-exact compared withsource','avi_sha256':sha(W/'build/P06/attempt1/timka-world-native-02/world.avi'),'mp4_sha256':sha(W/'build/P06/attempt1/timka-world-native-02/world.mp4'),'movie_trace_alignment_offsets':offsets,'chosen_movie_alignment':best,'movie_sample_comparisons':comparisons,'movie_expected_best_phase_samples':sum(x['expected_is_best'] for x in comparisons),'movie_total_compared_trace_samples':len(comparisons),'movie_phase_winner_mismatches':[x for x in comparisons if not x['expected_is_best']],'trace_facts':tracefacts,'observed_phase_dwell_physics_ticks':cadence,'continuous_joins':joins,'decoded_inventory_path':str((D/'decoded-inventory.json').relative_to(R)),'decoded_inventory_sha256':sha(D/'decoded-inventory.json'),'diagnostic_artifacts':artifacts,'muted_fixture':True,'actual_hearing':False,'native_rerun_by_reviewer':False,'full_phase_approval':False}
path=O/(P+'-metrics.json');assert not path.exists();path.write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in metrics.items() if k not in ['live_opaque_source_matches','movie_trace_alignment_offsets','movie_sample_comparisons','movie_phase_winner_mismatches','trace_facts','observed_phase_dwell_physics_ticks','continuous_joins','diagnostic_artifacts']},ensure_ascii=False,indent=2));print('phase_mismatches',len(metrics['movie_phase_winner_mismatches']))
