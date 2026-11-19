"""Read-only acceptance evidence review. No project operational imports."""
from pathlib import Path
import hashlib,json,ast,math
from PIL import Image,ImageDraw
O=Path(__file__).resolve().parent;R=O.parents[2];W=R/'.autopilot/worktrees/P07';E=W/'reports/pre_p07/pacing-acceptance-01'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=R/'reports/pre_p07/lead-pacing-calibration-02'
ns={'__file__':str(prior/'probe-final.py')};exec(compile((prior/'probe-final.py').read_text().split('rawpath=')[0],str(prior/'probe-final.py'),'exec'),ns,ns)
raw=json.loads((E/'raw.json').read_text());metrics=ns['namespace']['analyze'](raw)
assert metrics==json.loads((E/'metrics.json').read_text())
contractpath=W/'reports/pre_p07/pacing-contract-03/contract.PROPOSED.json';reviewpath=prior/'decision.json'
contract=json.loads(contractpath.read_text());current=contract['source_inventory_sha256'];before=json.loads((E/'source_before.json').read_text());after=json.loads((E/'source_after.json').read_text())
assert before==after==current
for rel,sha in current.items():assert h(W/rel)==sha,rel
assert raw['hardware']==contract['hardware']
validation=json.loads((E/'validation.json').read_text());assert validation['passed'] is True and validation['mode']=='acceptance' and validation['source_unchanged'] is True
assert h(contractpath)==validation['contract_sha256']=='4eb9b3f8a3aaa568a32c7b41ae1db80429f7f7f945a020513c206f0c1b23225a'
assert h(reviewpath)==validation['review_sha256']=='9966128fa846201420b9891d751e6f7da060871cdf819e5152337a488a5f5b85'
assert h(E/'raw.json')==validation['raw_sha256']=='7f6b1aaabb444fc1af0299a735bd8bde90d3057af685b5f28ff455c0ef1211e5'
measured={'accept_p95_ms':metrics['input_accept_ms']['p95'],'render_p95_ms':metrics['input_render_ms']['p95'],'frame_p95_ms':metrics['movement_frame_ms']['p95'],'frame_p99_ms':metrics['movement_frame_ms']['p99'],'restart_max_ms':metrics['death_to_control_ms']['max']}
checks=json.loads((E/'threshold_checks.json').read_text())
for key,value in measured.items():assert checks[key]=={'actual':value,'limit':contract['limits'][key],'passed':True} and value<contract['limits'][key]
job=R/'.autopilot/jobs/a75a4330de35414ab87b8a143a28cce0';receipt=json.loads((job/'receipt.json').read_text());assert receipt['operation']==job.name and receipt['exit_code']==0 and receipt['log_sha256']==h(job/'output.log')
runs=json.loads((E/'runs.json').read_text());assert len(runs)==2 and all(x['passed'] is True and x['exit_code']==0 for x in runs)
assert '--disable-vsync' in runs[1]['argv'] and '--max-fps' in runs[1]['argv'] and '--fixed-fps' not in runs[1]['argv']
frames=raw['clip_frames'];assert len(frames)==105
D=O/'diagnostics';D.mkdir(exist_ok=True)
images=[]
for i,row in enumerate(frames):
 p=Path(row['path']);assert row['error']==0 and p.is_file()
 with Image.open(p) as image:assert image.size==(640,360);images.append(image.convert('RGB'))
for group in range(math.ceil(len(images)/15)):
 board=Image.new('RGB',(1600,5*0+3*204),(24,24,24));draw=ImageDraw.Draw(board)
 for local in range(15):
  index=group*15+local
  if index>=len(images):break
  x=(local%5)*320;y=(local//5)*204
  board.paste(images[index].resize((320,180),Image.Resampling.NEAREST),(x,y+24));draw.text((x+3,y+4),f'{index:03} t={frames[index]["usec"]}',fill='white')
 board.save(D/f'sequence-{group+1:02}.png')
rows=[{'path':str(p.relative_to(E)),'sha256':h(p)} for p in sorted(E.rglob('*')) if p.is_file() and not any(x in p.parts for x in ['isolated_project','isolated_saves'])]
result={'schema':1,'scope':'FRESH_FROZEN_CONTRACT_SOFTWARE_NATIVE_ACCEPTANCE','operation':job.name,'receipt_sha256':h(job/'receipt.json'),'receipt_seconds':receipt['seconds'],'log_sha256_verified':True,'source_files_rehashed':len(current),'source_before_after_current_contract_equal':True,'hardware_exact_match':True,'fresh_raw_sha256':h(E/'raw.json'),'raw_functional_checks':len(raw['checks']),'request_count':len(raw['requests']),'draw_observations':len(raw['draws']),'physics_observations':len(raw['physics']),'actual_Core_contacts':len(raw['contacts']),'independently_rederived_metrics':metrics,'frozen_threshold_checks':checks,'capture_frames':len(frames),'capture_dimensions':[640,360],'native_movie_fixed_fps':False,'evidence_files':rows,'all_numeric_checks_passed':True,'no_engine_Controller_Git_network_or_production_writes':True}
(O/'own-assessment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['evidence_files','independently_rederived_metrics']},indent=2))
