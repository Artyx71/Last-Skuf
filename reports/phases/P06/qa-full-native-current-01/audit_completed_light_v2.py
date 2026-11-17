"""Lightweight completed prefix audit: JSON/logs/PNG headers only; no engines, scans, media decode."""
from pathlib import Path
import json,hashlib,math,re,struct,sys
Q=Path(__file__).resolve().parent;W=Q.parents[3]/'.autopilot/worktrees/P06';P=W/'reports/phases/P06/full-native-current-source-01'
def strict(text):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('duplicate '+k)
   out[k]=v
  return out
 def finite(s):
  v=float(s)
  if not math.isfinite(v):raise ValueError(s)
  return v
 def bad(s):raise ValueError(s)
 return json.loads(text,object_pairs_hook=pairs,parse_float=finite,parse_constant=bad)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return strict(p.read_text())
plan=read(Q/'inputs/plan.json');commands=read(P/'commands.json');error=re.compile(r'SCRIPT ERROR:|ERROR:|Parse Error|FAIL:|ObjectDB instances were leaked|resources still in use');rows=[]
for index,row in enumerate(commands):
 n=row['name'];stage=P/n;v=read(stage/'validation.json');log=P/'logs'/(n+'.log');text=log.read_text(errors='replace');checks={
 'sequential_plan_prefix':n==plan[index]['name'] and row['argv']==plan[index]['argv'],
 'actual_wrapper_exit0_typed':type(row.get('exit_code')) is int and row['exit_code']==0,
 'wrapper_log_hash_matches':sha(log)==row['log_sha256'],
 'wrapper_log_clean':not bool(error.search(text)),
 'wrapper_footer_exact':text.splitlines()[-1]=='exit_code=0',
 'no_unexpected_or_remaining_children':all(e.get('unexpected_live_children') is False and e.get('remaining_live_children')==[] for e in row.get('cleanup_events',[])) and bool(row.get('cleanup_events')),
 'validation_phasefalse':v.get('phase_approval') is False,
 'validation_current_head_if_recorded':v.get('source_head','beb30f319b2cf86a1799672ed24837c4640a9bee')=='beb30f319b2cf86a1799672ed24837c4640a9bee',
 'validation_sources_unchanged':v.get('source_unchanged',v.get('source_unchanged_after_import')) is True,
 'actual_child_commands_clean_typed0':bool(v.get('commands')) and all(type(c.get('exit_code')) is int and c['exit_code']==0 and c.get('passed') is True and isinstance(c.get('argv'),list) and bool(c['argv']) for c in v.get('commands',[])),
 }
 details={'name':n,'input_validation_sha256':sha(stage/'validation.json'),'wrapper_seconds_not_FPS':row.get('seconds'),'checks':checks,'recorded_modes':[]}
 for mode in ['live','movie']:
  p=stage/mode/'result.json'
  if not p.is_file():continue
  d=read(p);entries=d.get('checks',[]);contacts=d.get('contacts',[]);captures=d.get('captures',[]);command=next((x for x in v.get('commands',[]) if x.get('name')==mode),{});argv=command.get('argv',[]);mlog=stage/(mode+'.log');mtext=mlog.read_text(errors='replace')
  modechecks={'actual_Input':d.get('actual_input') is True,'actual_X11_or_Wayland':d.get('renderer') in ['X11','Wayland'],'nonempty_all_actual_checks':bool(entries) and all(x.get('passed') is True for x in entries),'mode_log_clean':not bool(error.search(mtext)),'mode_log_footer0':mtext.splitlines()[-1]=='exit_code=0','live_not_forced_movie_clock':mode!='live' or not any(x in argv for x in ['--fixed-fps','--write-movie','-w','--headless']),'movie_actual_engine_write_flag':mode!='movie' or any(x in argv for x in ['--write-movie','-w'])}
  pngs=[]
  for x in captures:
   f=Path(x['path']);hdr=f.open('rb').read(24);dims=struct.unpack('>II',hdr[16:24]) if len(hdr)==24 and hdr[:8]==b'\x89PNG\r\n\x1a\n' else None
   pngs.append({'name':x['name'],'path':str(f.relative_to(W)),'dimensions':list(dims) if dims else None,'passed':x.get('code')==0 and bool(dims) and dims[0]>0 and dims[1]>0 and dims[0]%640==0 and dims[1]%360==0 and dims[0]//640==dims[1]//360 and f.is_relative_to(stage)})
  modechecks['all_capture_records_valid_integer_scaled_640x360_PNG']=all(x['passed'] for x in pngs)
  outgoing=[x for x in contacts if x.get('finisher') and not x.get('target_is_player')]
  modechecks['outgoing_FIN_actual_contact_player_frame1']=all(x.get('player_frame')==1 for x in outgoing)
  details['recorded_modes'].append({'mode':mode,'source_result_sha256':sha(p),'actual_checks':len(entries),'captures':len(captures),'contacts':len(contacts),'outgoing_FIN':len(outgoing),'incoming_Core':sum(x.get('target_is_player') is True for x in contacts),'trace_samples':len(d.get('trace',d.get('observations',[]))),'checks':modechecks,'PNG_headers':pngs})
 details['passed']=all(checks.values()) and all(all(x['checks'].values()) for x in details['recorded_modes']);rows.append(details)
result={'scope':'LIGHT_COMPLETED_PREFIX_ONLY_NOT_FULL13_OR_PHASE_VERDICT','completed_stages':len(rows),'planned_stages':len(plan),'all_completed_checks_passed':all(x['passed'] for x in rows),'stages':rows,'heavy_decode_source_object_scan_or_engine':False,'final_receipt_still_required':True}
out=Q/('light-v2-prefix-%02d.json'%len(rows))
if out.exists():raise SystemExit('Immutable existing prefix audit; choose a fresh output/version before new analysis')
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'completed':len(rows),'passed':result['all_completed_checks_passed'],'failures':[(x['name'],[k for k,v in x['checks'].items() if not v],[(m['mode'],[k for k,v in m['checks'].items() if not v]) for m in x['recorded_modes'] if not all(m['checks'].values())]) for x in rows if not x['passed']]}))
