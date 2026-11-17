"""Targeted contradictory duplicate-closure JSON/cache load proof; TEMP only."""
from pathlib import Path
import sys,json
O=Path(__file__).resolve().parent;sys.dont_write_bytecode=True;sys.path.insert(0,str(O/'isolated-source/tools/tests'));import test_production_readiness as tests
from runner import load
from github import validate_review,guarded_merge
t=tests.ProductionReadinessTests();t.setUp()
try:
 review=t.acceptance_review();review.update(base_branch='main',base_sha='b'*40,next_action='TEST_ONLY_DUPLICATE_REPRO',artistic_audio_acceptance=None)
 encoded=json.dumps(review);needle='"new_audio_acceptance": ';raw=encoded.replace(needle,'"new_audio_acceptance": {"status":"FAIL","evidence":[]}, '+needle,1);assert raw.count(needle)==2
 (O/'duplicate-raw-verdict.TEST_ONLY.txt').write_text(raw+'\n');path=t.root/'TEST_ONLY_CACHE_VERDICT.json';path.write_text(raw);parsed=load(path,{});errors=validate_review(t.root,parsed,t.head,'P07');snapshots=[];requests=[]
 def snapshot(*_):snapshots.append(1);return t.merge_view()
 def spy(*args):requests.append(args);return {'merged':False,'message':'TEST_ONLY REQUEST SPY; NO GITHUB REQUEST'}
 result=guarded_merge(t.root,4,{},parsed,'P07',snapshot,spy)
 record={'scope':'TEMP_GIT_FIXTURE_NO_REAL_AUTHORITY_OR_NETWORK','raw_new_audio_acceptance_key_occurrences':raw.count(needle),'first_duplicate_status':'FAIL','last_duplicate_status':'PASS','actual_runner_load_last_wins':parsed['production_acceptance']['closed_obligations']['new_audio_acceptance']['status'],'actual_validate_review_errors':errors,'actual_guarded_merge_snapshot_count':len(snapshots),'mock_requests':requests,'mock_PUT_count':sum(len(x)>1 and x[1]=='PUT' for x in requests),'returned_status':result['status'],'returned_blocked_only_because_spy_never_merges':result['blockers'],'actual_network_requests':0}
 (O/'duplicate-proof-result.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
finally:t.tearDown()
