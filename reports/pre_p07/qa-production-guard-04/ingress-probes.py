"""Actual v4 JSON load -> phase validation -> merge chain. TEMP fixtures only."""
from pathlib import Path
import sys,json,hashlib,copy
O=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(O/'isolated-source/tools/tests'));import test_production_readiness as tests
from runner import load,Blocked
from readiness import require_p07_production,require_p07_review_acceptance,ReadinessBlocked
from github import validate_review,guarded_merge
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=[]
def fixture(name,fn):
 t=tests.ProductionReadinessTests();t.setUp()
 try:row={'name':name,'scope':'TEMP_GIT_FAKE_RECEIPTS_NO_PRODUCTION_APPROVAL'};row.update(fn(t));rows.append(row);assert row['passed_expected_contract'],row
 finally:t.tearDown()
def review(t):
 r=t.acceptance_review();r.update(base_branch='main',base_sha='b'*40,next_action='TEST_ONLY',artistic_audio_acceptance=None);assert validate_review(t.root,r,t.head,'P07')==[];return r

def ingress(t,kind):
 r=review(t);raw=json.dumps(r);needle='"new_audio_acceptance":'
 if kind=='same_v3_bytes':raw=(O/'same-v3-raw-verdict.TEST_ONLY.txt').read_text()
 elif kind=='fresh_duplicate':raw=raw.replace(needle,needle+'{"status":"FAIL","evidence":[]},'+needle,1)
 elif kind=='decoded_unicode_duplicate':
  escaped='"'+chr(92)+'u006eew_audio_acceptance":';raw=raw.replace(needle,escaped+'{"status":"FAIL","evidence":[]},'+needle,1)
 elif kind=='top_status_duplicate':raw=raw.replace('"status": "PASS"','"status":"FAIL","status":"PASS"',1)
 else:raise ValueError(kind)
 p=t.root/'TEST_ONLY_CACHE.json';p.write_text(raw);original=sha(p);snapshots=[];requests=[];validation_calls=0;loader_error=None;cause=None
 def snap(*_):snapshots.append(1);return t.merge_view()
 def spy(*args):requests.append(args);return {'merged':False,'message':'TEST_ONLY NO NETWORK'}
 try:
  parsed=load(p,{});validation_calls+=1;errors=validate_review(t.root,parsed,t.head,'P07')
  if not errors:guarded_merge(t.root,4,{},parsed,'P07',snap,spy)
 except Blocked as e:loader_error=str(e);cause=str(e.__cause__)
 passed=loader_error is not None and not validation_calls and not snapshots and not requests and sha(p)==original
 return {'actual_loader_exception':loader_error,'actual_parser_cause':cause,'validation_calls':validation_calls,'snapshot_count':len(snapshots),'mock_request_count':len(requests),'raw_SHA':original,'raw_record_preserved':sha(p)==original,'passed_expected_contract':passed}
for kind in ['same_v3_bytes','fresh_duplicate','decoded_unicode_duplicate','top_status_duplicate']:fixture(kind,lambda t,k=kind:ingress(t,k))
for constant in ['NaN','Infinity','-Infinity']:
 def nonfinite(t,value=constant):
  p=t.root/'TEST_ONLY_BAD_CONSTANT.json';p.write_text('{"value":'+value+'}');h=sha(p);blocked=False;cause=None
  try:load(p,{'never':'fallback'})
  except Blocked as e:blocked=True;cause=str(e.__cause__)
  return {'actual_loader_blocked':blocked,'parser_cause':cause,'record_preserved':sha(p)==h,'passed_expected_contract':blocked and sha(p)==h}
 fixture('literal_nonfinite_'+constant,nonfinite)

def ready_duplicate(t,key):
 rec=t.state['autopilot']['production_gates']['readiness'];p=t.root/rec['decision'];raw=p.read_text();needle=json.dumps(key)+':';assert needle in raw;escaped='"'+chr(92)+'u'+format(ord(key[0]),'04x')+key[1:]+'":';raw=raw.replace(needle,escaped+'{"status":"FAIL"},'+needle,1);p.write_text(raw);rec['sha256']=sha(p);before=copy.deepcopy(t.state);h=sha(p);blocked=False;cause=None
 try:require_p07_production(t.root,t.state)
 except ReadinessBlocked as e:blocked=True;cause=str(e.__cause__)
 return {'hash_rebound_before_validation':True,'actual_receipt_blocked':blocked,'parser_cause':cause,'record_preserved':sha(p)==h,'state_unchanged':before==t.state,'passed_expected_contract':blocked and sha(p)==h and before==t.state}
fixture('ROOT_receipt_duplicate_capability_decoded_key',lambda t:ready_duplicate(t,'navigation_pilot'))
fixture('ROOT_receipt_duplicate_future_obligation_decoded_key',lambda t:ready_duplicate(t,'secret_delivery_7'))

def state_duplicate(t):
 r=review(t);p=t.root/'automation/phase_state.json';raw=p.read_text().replace('"production_gates":','"production_gates":{},"production_gates":',1);p.write_text(raw);h=sha(p);blocked=False;cause=None
 try:require_p07_review_acceptance(t.root,r,t.head)
 except ReadinessBlocked as e:blocked=True;cause=str(e.__cause__)
 return {'actual_canonical_reader_blocked':blocked,'parser_cause':cause,'record_preserved':sha(p)==h,'passed_expected_contract':blocked and sha(p)==h}
fixture('canonical_ROOT_state_duplicate_gate_key',state_duplicate)

def findings_case(t,value):
 r=review(t);r['findings']=value;p=t.root/'TEST_ONLY_CACHE.json';p.write_text(json.dumps(r));parsed=load(p);errors=validate_review(t.root,parsed,t.head,'P07');sent=[];calls=[]
 def snap(*_):calls.append(1);return t.merge_view()
 out=guarded_merge(t.root,4,{},parsed,'P07',snap,lambda *a:sent.append(a));ok=bool(errors) and out['status']=='BLOCKED' and len(calls)==1 and not sent
 return {'findings_type':type(value).__name__,'actual_validate_errors':errors,'actual_merge_status':out['status'],'snapshot_count':len(calls),'mock_request_count':len(sent),'passed_expected_contract':ok}
for value in [{},{'severity':'HIGH','status':'OPEN'},None,'',0,False]:fixture('findings_wrong_type_'+repr(value),lambda t,v=value:findings_case(t,v))
(O/'ingress-results.json').write_text(json.dumps({'schema':1,'records':rows,'passed':all(x['passed_expected_contract'] for x in rows),'actual_network_requests':0,'actual_production_controller_or_state_mutations':0},indent=2)+'\n');print(json.dumps(rows,indent=2))
