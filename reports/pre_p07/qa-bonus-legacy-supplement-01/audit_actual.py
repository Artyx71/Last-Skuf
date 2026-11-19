#!/usr/bin/env python3
"""Read-only actual proof verification; writes only this owned QA evidence JSON."""
from pathlib import Path
import json,hashlib,struct
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'.autopilot/worktrees/P07'
OWN=Path(__file__).parent
RUN=WORK/'reports/pre_p07/bonus-legacy-supplement-01'
PRIOR=WORK/'reports/pre_p07/bonus-live-adapter-03'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    before=read(RUN/'source_before.json');after=read(RUN/'source_after.json');old=read(PRIOR/'source_before.json')
    assert before==after
    assert all(sha(WORK/k)==v for k,v in before.items())
    game={k for k in before if k.startswith('game/')};driver='game/scripts/qa/story_replay.gd'
    assert game=={k for k in old if k.startswith('game/')}
    assert [k for k in sorted(game) if before[k]!=old[k]]==[driver]
    assert all(sha(RUN/'isolated_project/game'/Path(k).relative_to('game'))==before[k] for k in game)
    records=read(OWN/'source-freeze.json')['records']
    assert all(before[x['path']]==x['sha256'] for x in records)
    original=ROOT/'reports/pre_p07/qa-bonus-live-03/source-a684'/driver
    candidate=OWN/'source-a0ab'/driver
    calls=lambda p:[x.strip()for x in p.read_text().splitlines()if 'check(' in x and not x.strip().startswith('func check')]
    assert calls(original)==calls(candidate)
    validation=read(RUN/'validation.json');result=read(RUN/'result.json');checks=result['checks'];nested=result['p04_input']
    assert validation['passed']is True and validation['exit_code']==0 and validation['timed_out']is False and validation['timeout_seconds']==180
    assert checks and all(v is True for v in checks.values())and len(checks)==41
    assert result['passed']is True and result['rendered']is True and result['display']=='X11' and result['actual_input']is True and result['route_warps']==0
    assert nested['passed']is True and nested['actual_input']is True and nested['route_warps']==0 and len(nested['checks'])==49 and all(v is True for v in nested['checks'].values())
    assert len([k for k in nested['checks']if k.startswith('retry_')])==10
    assert len([k for k in nested['checks']if k.startswith('deterministic_reset_')])==10
    assert result['story']['domain']=='campaign'and result['story']['schema']==2 and result['story']['completion_rewards']==1
    for id in['EV_CH01_INTRO','EV_CH01_PHONE','EV_CH01_OUTRO','EV_CH01_SERVICE_ESCAPE']:
        assert sum(row['id']==id for row in result['story']['history'])==1
    assert result['startup_after_physics_wait']['drawn_frames']==0
    assert result['startup_before_first_key']['drawn_frames']>0
    assert result['startup_before_first_key']['current_is_bootstrap']is True
    assert result['startup_before_first_key']['node_ready']is True and result['startup_before_first_key']['journal_ready']is True
    text=(RUN/'native.log').read_text()
    assert validation['log_sha256']==sha(RUN/'native.log')and not any(s in text for s in['SCRIPT ERROR:','Parse Error:','FAIL: P05'])
    job=ROOT/'.autopilot/jobs/b72bdfd3dce24e3fb499c3d06bb06c02'
    receipt=read(job/'receipt.json');entry=read(job/'input.json')
    assert receipt['exit_code']==0 and receipt['log_sha256']==sha(job/'output.log')
    assert receipt['argv_sha256']==hashlib.sha256(json.dumps(entry['argv']).encode()).hexdigest()
    lock=read(WORK/'tools/toolchain.lock.json');engine=WORK/'.tools/godot'/('Godot_v'+lock['release']+'_linux.x86_64')
    assert sha(engine)==lock['linux_binary_sha256']
    captures=[]
    for row in result['captures']:
        f=Path(row['path']);raw=f.read_bytes();assert row['error']==0 and raw[:8]==b'\x89PNG\r\n\x1a\n'
        captures.append({'id':row['id'],'path':str(f.relative_to(WORK)),'sha256':sha(f),'size':list(struct.unpack('>II',raw[16:24]))})
    prior=read(PRIOR/'runs.json');assert [(r['name'],r['exit_code'],r['passed'])for r in prior]==[('live',0,True),('cli',0,True),('native',0,True),('native_cli',0,True)]
    for row in prior:assert row['log_sha256']==sha(PRIOR/(row['name']+'.log'))
    proof={'schema':1,'scope':'FINITE_NATIVE_LEGACY_STORY_REPLAY_SUPPLEMENT_ONLY','source_head':'a0ab23a9838d9308ee9acc38d3ef2cdc91cedfc4','operation':receipt['operation'],'exit_code':0,'receipt_seconds':receipt['seconds'],'source_keys':len(before),'source_before_after_and_current_exact':True,'Game_keys':len(game),'unchanged_Game_pins':len(game)-1,'only_changed_Game_input':driver,'copied_runtime_all_Game_pins_exact':True,'original_check_call_lines_unchanged':len(calls(candidate)),'original_180s_timeout_unchanged':True,'actual_fresh_native_checks':len(checks),'nested_actual_CH01_Input_checks':len(nested['checks']),'nested_retry_and_reset_each':10,'route_warps':0,'completion_rewards':1,'startup_before_physics':result['startup_before_physics_wait'],'startup_after_original_physics':result['startup_after_physics_wait'],'startup_before_first_F4':result['startup_before_first_key'],'engine_sha256':sha(engine),'captures':captures,'retained_not_rerun_stages':[{'name':x['name'],'checks':x['checks']}for x in prior],'original03_outer_failure_remains_exit1':True,'past_initial_F4_failure_OS_cause':'UNKNOWN','new_broad_loop_or_fullH05_approval':False}
    (OWN/'evidence-verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:proof[k]for k in['exit_code','source_keys','Game_keys','unchanged_Game_pins','actual_fresh_native_checks','nested_actual_CH01_Input_checks','original_check_call_lines_unchanged']},indent=2))
if __name__=='__main__':main()
