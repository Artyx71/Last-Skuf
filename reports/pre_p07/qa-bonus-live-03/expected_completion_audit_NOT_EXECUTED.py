#!/usr/bin/env python3
"""Read-only proof audit; no engine/controller/source mutation. Writes owned QA JSON only."""
import hashlib,json,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'.autopilot/worktrees/P07'
OWN=Path(__file__).parent
RUN=WORK/'reports/pre_p07/bonus-live-adapter-03'
CORE=WORK/'reports/pre_p07/bonus-live-adapter-02/core'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text())
def main():
    validation=read(RUN/'validation.json')
    before=read(RUN/'source_before.json');after=read(RUN/'source_after.json')
    assert before==after and validation['passed'] is True
    freeze=read(OWN/'source-freeze.json')
    assert all(before[x['path']]==x['sha256'] for x in freeze['records'])
    assert all(sha(WORK/k)==v for k,v in before.items())
    operation='295ba28fb99e434eb6f8a5288b782476'
    job=ROOT/'.autopilot/jobs'/operation
    receipt=read(job/'receipt.json');entry=read(job/'input.json')
    assert receipt['exit_code']==0 and receipt['log_sha256']==sha(job/'output.log')
    assert receipt['argv_sha256']==hashlib.sha256(json.dumps(entry['argv']).encode()).hexdigest()
    stages=[];captures=[]
    rows=read(RUN/'runs.json')
    assert [x['name'] for x in rows]==['live','cli','native','native_cli','old_story_replay']
    for row in rows:
        assert row['exit_code']==0 and row['passed'] is True
        log=RUN/(row['name']+'.log');text=log.read_text()
        assert sha(log)==row['log_sha256'] and not any(x in text for x in ['SCRIPT ERROR:','Parse Error:','FAIL BONUS','FAIL: P05'])
        data=read(RUN/(row['name']+'-result.json'));checks=data['checks']
        if isinstance(checks,dict):
            assert checks and all(value is True for value in checks.values())
        else:
            assert checks and len({x['check'] for x in checks})==len(checks)
            assert all(x['passed'] is True for x in checks)
            assert type(data['passed']) is int and data['passed']==len(checks) and data['failed']==0
        assert len(checks)==row['checks']
        stages.append({'name':row['name'],'checks':len(checks),'exit_code':0,'log_sha256':sha(log),'renderer':data.get('renderer',data.get('display')),'Input_events_are_engine_injected_not_physical_keys':True})
        for item in data.get('captures',[]):
            path=Path(item if isinstance(item,str) else item['path'])
            if isinstance(item,dict):assert item['error']==0
            raw=path.read_bytes();assert raw[:8]==b'\x89PNG\r\n\x1a\n'
            captures.append({'path':str(path.relative_to(WORK)),'sha256':sha(path),'bytes':len(raw),'size':list(struct.unpack('>II',raw[16:24]))})
    native=read(RUN/'native-result.json')
    for target in [21,22]:
        assert any(x.get('phase')=='DOWN_selection' and x['selected']==target and x['focus_is_list'] is True for x in native['UI_trace'])
    mouse=native['mouse_trace'];assert len(mouse)==6
    assert [(x['route'],x['selected']) for x in mouse]==[('legacy_window',18),('viewport_local',21),('viewport_local',21),('legacy_window',19),('viewport_local',22),('viewport_local',22)]
    for i in [0,3]:assert mouse[i]['point']==mouse[i+1]['point']
    assert native['UI_keyboard_mouse_tested'] is True
    assert read(RUN/'live-result.json')['UI_keyboard_mouse_tested'] is False
    reuse=read(RUN/'core-reuse.json');core=read(CORE/'validation.json');saved=read(CORE/'source_after.json')
    game={key for key in before if key.startswith('game/')}
    required=game|{'tools/p07_bonus_pilot.py','tools/fixtures/p07_bonus_contract.gd','tools/fixtures/p07_bonus_host.gd'}
    assert reuse['required_source_pins']=={key:before[key] for key in required}
    assert all(saved[key]==before[key] for key in required)
    assert sha(CORE/'validation.json')==reuse['validation_sha256'] and sha(CORE/'source_after.json')==reuse['source_after_sha256']
    assert core['passed'] is True and core['source_unchanged'] is True
    for row in core['runs']:assert row['passed'] is True and sha(CORE/(row['name']+'.log'))==row['log_sha256']
    lock=read(WORK/'tools/toolchain.lock.json');engine=WORK/'.tools/godot'/('Godot_v'+lock['release']+'_linux.x86_64')
    assert sha(engine)==core['engine_sha256']==lock['linux_binary_sha256']
    assert all(sha(RUN/'isolated_project/game'/Path(key).relative_to('game'))==before[key] for key in game)
    result={'schema':1,'source_head':freeze['source_head'],'operation':operation,'receipt_exit':0,'receipt_seconds':receipt['seconds'],'source_keys':len(before),'source_unchanged_and_current':True,'core_reused_not_rerun':True,'core_game_keys':len(game),'core_required_pins':len(required),'engine_sha256':sha(engine),'stages':stages,'native_mouse_trace':mouse,'window_size':native['window_size'],'viewport_size':native['viewport_size'],'screen_transform':native['screen_transform'],'actual_capture_inventory':captures,'ROOT_installation_Readiness_full_phase_approved':False}
    (OWN/'evidence-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'stages':stages,'source_keys':len(before),'captures':len(captures),'passed':True},indent=2))
if __name__=='__main__':main()
