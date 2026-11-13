"""Owner-authorized PR policy. No admin override, force push or protection changes."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import quote

REPO='Artyx71/Last-Skuf'
SHA=re.compile(r'^[0-9a-f]{40}$')


class GitHubBlocked(RuntimeError): pass


def gh(argv,payload=None,json_output=True):
    proc=subprocess.run(['gh',*argv],input=json.dumps(payload) if payload is not None else None,
                        capture_output=True,text=True,timeout=90)
    if proc.returncode:
        raise GitHubBlocked(proc.stderr.strip() or proc.stdout.strip())
    if not json_output: return proc.stdout
    return json.loads(proc.stdout) if proc.stdout.strip() else {}


def api(endpoint,method='GET',payload=None):
    argv=['api',endpoint,'--method',method]
    if payload is not None: argv+=['--input','-']
    return gh(argv,payload)


def validate_review(root,review,head,phase):
    errors=[]
    if review.get('phase')!=phase or review.get('reviewed_commit')!=head or not SHA.fullmatch(head or ''):
        errors.append('Independent review does not cover exact current head SHA/phase')
    if review.get('status') not in ['PASS','FAIL','BLOCKED'] or review.get('independent_review') is not True or not review.get('reviewer'):
        errors.append('Missing independent verdict/reviewer')
    evidence=review.get('evidence',[])
    if not isinstance(evidence,list) or not evidence: errors.append('No review evidence')
    else:
        for item in evidence:
            if not isinstance(item,dict) or not isinstance(item.get('path'),str):
                errors.append('Malformed evidence'); continue
            path=(Path(root)/item['path']).resolve()
            if not path.is_relative_to(Path(root).resolve()) or not path.is_file():
                errors.append('Evidence missing/escapes repository: '+item['path']); continue
            if hashlib.sha256(path.read_bytes()).hexdigest()!=item.get('sha256'):
                errors.append('Evidence changed: '+item['path'])
    if review.get('status')=='PASS':
        for item in review.get('findings',[]):
            if not isinstance(item,dict): errors.append('Malformed finding'); continue
            if item.get('severity') in ['CRITICAL','HIGH'] and item.get('status') not in ['CLOSED','RESOLVED']:
                errors.append('Unresolved CRITICAL/HIGH finding')
        if phase=='P03':
            acceptance=review.get('artistic_audio_acceptance') or {}
            if acceptance.get('status')!='PASS' or acceptance.get('method') not in ['human_listening','actual_listening_tool']:
                errors.append('P03 artistic acceptance cannot be replaced by signal metrics')
            proof=acceptance.get('evidence')
            if not isinstance(proof,dict) or proof not in evidence:
                errors.append('Actual listening acceptance must be hash-bound review evidence')
    return errors


def snapshot(number,config):
    if config['repository']!=REPO or config['main_branch']!='main' or config['merge_method']!='squash':
        raise GitHubBlocked('Policy allows only Artyx71/Last-Skuf squash into main')
    repo=api(f'repos/{REPO}')
    if repo['private'] != (config.get('repository_visibility','private')=='private'):
        raise GitHubBlocked('Repository visibility differs from owner-authorized configuration')
    pull=api(f'repos/{REPO}/pulls/{number}')
    query='''query($owner:String!,$name:String!,$number:Int!){repository(owner:$owner,name:$name){pullRequest(number:$number){reviewDecision mergeStateStatus reviewThreads(first:100){pageInfo{hasNextPage} nodes{isResolved}}}}}'''
    graph=gh(['api','graphql','-f','query='+query,'-f','owner=Artyx71','-f','name=Last-Skuf','-F',f'number={number}'])
    if graph.get('errors'): raise GitHubBlocked('GraphQL review/protection inspection failed')
    info=graph['data']['repository']['pullRequest']
    # Fail closed on 403/unknown protection. Never upgrade billing, make repo public or invoke --admin.
    branch=quote(config['main_branch'],safe='')
    rules=api(f'repos/{REPO}/rules/branches/{branch}?per_page=100')
    if len(rules)>=100: raise GitHubBlocked('Branch rule inspection truncated')
    protected=api(f'repos/{REPO}/branches/{branch}')
    protection=api(f'repos/{REPO}/branches/{branch}/protection') if protected.get('protected') else {}
    head=pull['head']['sha']
    checks=api(f'repos/{REPO}/commits/{head}/check-runs?per_page=100')
    statuses=api(f'repos/{REPO}/commits/{head}/status?per_page=100')
    if checks['total_count']>len(checks['check_runs']) or statuses.get('total_count',0)>len(statuses['statuses']):
        raise GitHubBlocked('CI inspection truncated')
    required=set(config['required_ci_checks'])
    integration_ids={}
    for item in protection.get('required_status_checks',{}).get('checks',[]):
        required.add(item['context']); integration_ids[item['context']]=item.get('app_id')
    required.update(protection.get('required_status_checks',{}).get('contexts',[]))
    approvals=protection.get('required_pull_request_reviews',{}).get('required_approving_review_count',0)
    queue_required=False
    for rule in rules:
        parameters=rule.get('parameters',{})
        if rule['type']=='required_status_checks':
            for item in parameters['required_status_checks']:
                required.add(item['context']); integration_ids[item['context']]=item.get('integration_id')
        if rule['type']=='pull_request': approvals=max(approvals,parameters.get('required_approving_review_count',0))
        if rule['type']=='merge_queue': queue_required=True
    latest={}
    for item in sorted(checks['check_runs'],key=lambda x:x['id']):
        latest[item['name']]={'status':item['status'],'conclusion':item['conclusion'],
                               'head_sha':item['head_sha'],'app_id':item['app']['id'],
                               'app_slug':item['app']['slug'],'url':item['html_url']}
    for item in statuses['statuses']:
        latest.setdefault(item['context'],{'status':'completed' if item['state']!='pending' else 'pending',
            'conclusion':'success' if item['state']=='success' else item['state'],'head_sha':head,'app_id':None})
    return {'number':number,'repository':REPO,'private':repo['private'],'permissions':repo.get('permissions',{}),
        'squash_allowed':repo.get('allow_squash_merge',False),'head_sha':head,'head_repo':pull['head']['repo']['full_name'],
        'base':pull['base']['ref'],'base_sha':protected['commit']['sha'],'state':pull['state'],'draft':pull['draft'],
        'merged':pull['merged'],'merge_commit_sha':pull.get('merge_commit_sha'),'mergeable':pull['mergeable'],
        'merge_state':info['mergeStateStatus'],'review_decision':info['reviewDecision'],
        'threads_complete':not info['reviewThreads']['pageInfo']['hasNextPage'],
        'unresolved_threads':sum(not x['isResolved'] for x in info['reviewThreads']['nodes']),
        'required_checks':sorted(required),'integration_ids':integration_ids,'checks':latest,
        'approvals_required':approvals,'queue_required':queue_required,'protection_inspected':True,
        'expected_ci_app_slug':'github-actions'}


def gate(root,view,review,phase):
    errors=validate_review(root,review,view['head_sha'],phase)
    if review.get('status')!='PASS': errors.append('Lead FAIL/BLOCKED prohibits merge')
    if review.get('base_branch')!='main' or review.get('base_sha')!=view['base_sha']:
        errors.append('Independent review must cover the current main base as well as head')
    for condition,message in [
        (view['repository']==REPO,'Wrong repository'),
        (view['head_repo']==REPO,'Foreign head repository'),
        (view['base']=='main','Stacked PR must be safely retargeted/reviewed against main'),
        (view['state']=='open' and not view['draft'],'PR closed/draft'),
        (view['squash_allowed'] and view['permissions'].get('push',False),'Missing squash/write permission'),
        (view['protection_inspected'],'Cannot inspect branch protection'),
        (view['mergeable'] is True and view['merge_state']=='CLEAN','GitHub merge state not clean'),
        (view['threads_complete'] and view['unresolved_threads']==0,'Unresolved or uninspected review threads'),
        (view['review_decision'] not in ['CHANGES_REQUESTED','REVIEW_REQUIRED'],'GitHub manual approval required'),
        (not view['approvals_required'] or view['review_decision']=='APPROVED','Required GitHub approvals missing'),
        (not view['queue_required'],'Merge queue requires repository-controlled approval path'),
        (bool(view['checks']),'No CI checks on current SHA'),
    ]:
        if not condition: errors.append(message)
    for name in view['required_checks']:
        check=view['checks'].get(name)
        if not check or check['status']!='completed' or check['conclusion']!='success' or check['head_sha']!=view['head_sha']:
            errors.append('Required CI not successful on current SHA: '+name)
        elif view['integration_ids'].get(name) not in [None,-1,check.get('app_id')]:
            errors.append('Required CI integration mismatch: '+name)
        elif check.get('app_slug')!=view.get('expected_ci_app_slug','github-actions'):
            errors.append('Required CI must be an actual GitHub Actions check: '+name)
    # Pending/failing extra checks are conservative blockers too; never mistake old green jobs for current ones.
    if any(c['status']!='completed' or c['conclusion'] not in ['success','neutral','skipped'] for c in view['checks'].values()):
        errors.append('A current-head check is pending/failing')
    return errors


def guarded_merge(root,number,config,review,phase,get_snapshot=snapshot,request=api):
    first=get_snapshot(number,config); problems=gate(root,first,review,phase)
    if problems: return {'status':'BLOCKED','blockers':problems,'snapshot':first}
    # Fresh remote read immediately before atomic server-side SHA precondition.
    fresh=get_snapshot(number,config)
    if fresh['head_sha']!=first['head_sha'] or fresh['base_sha']!=first['base_sha']:
        return {'status':'BLOCKED','blockers':['Head/base SHA changed immediately before merge']}
    problems=gate(root,fresh,review,phase)
    if problems: return {'status':'BLOCKED','blockers':problems,'snapshot':fresh}
    response=request(f'repos/{REPO}/pulls/{number}/merge','PUT',{'sha':fresh['head_sha'],'merge_method':'squash'})
    if not response.get('merged'):
        return {'status':'BLOCKED','blockers':[response.get('message','GitHub did not confirm merge')],'response':response}
    confirmation=request(f'repos/{REPO}/pulls/{number}')
    if not confirmation.get('merged') or confirmation['head']['sha']!=fresh['head_sha'] or confirmation['base']['ref']!='main':
        return {'status':'BLOCKED','blockers':['Merge response not independently confirmed; reconcile before continuing']}
    return {'status':'MERGED','reviewed_head':fresh['head_sha'],'merge_sha':response['sha'],'number':number,'method':'squash','base':'main'}


def manage(controller,phase,action,review=None):
    from runner import save,load,Blocked
    state=controller.state(); record=state['autopilot']['phases'][phase]
    # Authoritative independent FAIL/BLOCKED always wins over a stale external PASS receipt.
    if action=='merge' and not controller.config.get('automatic_merge',False):
        raise Blocked('Automatic merge disabled by configuration')
    if action=='merge' and record['status']!='PASS':
        raise Blocked(f'{phase} Lead status {record["status"]}: merge forbidden')
    if action=='merge': controller.prerequisite(phase)
    work=Path(record.get('workspace',controller.root)).resolve()
    number=record.get('pull_request_number')
    if number is None:
        decision=load(controller.root/record.get('decision','missing'),{})
        url=decision.get('pull_request','')
        if re.fullmatch(r'https://github.com/Artyx71/Last-Skuf/pull/\d+',url): number=int(url.rsplit('/',1)[1])
    try:
        if action=='prepare':
            if number is None:
                branch=subprocess.check_output(['git','branch','--show-current'],cwd=work,text=True).strip()
                if not branch.startswith('phase/'): raise GitHubBlocked('Only phase/* branches may create PRs')
                private=api(f'repos/{REPO}')
                if private['private'] != (controller.config.get('repository_visibility','private')=='private'):
                    raise GitHubBlocked('Repository visibility differs from owner authorization')
                origin=subprocess.check_output(['git','remote','get-url','origin'],cwd=work,text=True).strip()
                if not re.fullmatch(r'(?:https://github.com/|git@github.com:)Artyx71/Last-Skuf(?:\.git)?',origin):
                    raise GitHubBlocked('Push origin does not match the authorized repository')
                subprocess.run([sys.executable,'tools/check_privacy.py'],cwd=work,check=True,capture_output=True)
                subprocess.run(['git','push','--set-upstream','origin',branch],cwd=work,check=True,capture_output=True)
                pull=api(f'repos/{REPO}/pulls','POST',{'title':f'{phase}: phase implementation','head':branch,'base':'main',
                    'body':f'Phase {phase}. Independent review and exact-SHA CI required. Evidence in reports/phases/{phase}.','draft':True})
                number=pull['number']
            view=api(f'repos/{REPO}/pulls/{number}')
            if view['base']['ref']!='main':
                previous=controller.phases[:controller.phases.index(phase)]
                if previous and state['autopilot']['phases'][previous[-1]].get('merge',{}).get('status')!='MERGED':
                    raise GitHubBlocked('Previous stacked phase not merged; retarget deferred')
                api(f'repos/{REPO}/pulls/{number}','PATCH',{'base':'main'})
                record.pop('review_receipt',None)
                result={'status':'REVIEW_REQUIRED','reason':'Base changed to main; independent review and CI must be refreshed','number':number}
            else: result={'status':'PREPARED','number':number}
        else:
            if number is None: raise GitHubBlocked('No PR associated with phase; prepare one first')
            if action=='status': result={'status':'INSPECTED','snapshot':snapshot(number,controller.config)}
            else:
                head=api(f'repos/{REPO}/pulls/{number}')['head']['sha']
                review=review or load(controller.data/'reviews'/f'{phase}-{head}.json',{})
                current=api(f'repos/{REPO}/pulls/{number}')
                if current['merged']:
                    # Reconcile a lost merge response only with exact-head independent evidence.
                    problems=validate_review(work,review,head,phase)
                    if problems or review.get('status')!='PASS' or current['base']['ref']!='main':
                        raise GitHubBlocked('Already-merged PR lacks matching independent proof; manual reconciliation required')
                    result={'status':'MERGED','reviewed_head':head,'merge_sha':current['merge_commit_sha'],'number':number,'method':'squash','base':'main','recovered':True}
                else:
                    if current['draft'] and not validate_review(work,review,head,phase) and review.get('status')=='PASS':
                        gh(['pr','ready',str(number),'--repo',REPO],json_output=False)
                    result=guarded_merge(work,number,controller.config,review,phase)
    except (GitHubBlocked,subprocess.SubprocessError,OSError) as exc:
        result={'status':'BLOCKED','blockers':[str(exc)],'number':number,
                'merge_confirmation':'UNKNOWN_AFTER_ERROR' if action=='merge' else 'NOT_REQUESTED'}
    state=controller.state(); record=state['autopilot']['phases'][phase]
    if number: record['pull_request_number']=number
    record['merge']=result
    if result['status']=='MERGED':
        state['last_pass']=phase
        index=controller.phases.index(phase)
        if index+1<len(controller.phases):
            state['active_phase']=controller.phases[index+1]; state['status']='READY'
        state['autopilot']['history'].append({'event':'SQUASH_MERGE_CONFIRMED','phase':phase,**result})
    elif result['status']=='BLOCKED':
        state['autopilot']['history'].append({'event':'MERGE_BLOCKED','phase':phase,'findings':result['blockers']})
    controller.persist(state)
    destination=controller.root/f'reports/autopilot/{phase}/pull_request.json'; save(destination,result)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['status'] in ['MERGED','INSPECTED','PREPARED','REVIEW_REQUIRED'] else 4


def wait_ci(controller,phase):
    """Bounded wait; pending/failure is persisted and never turns into a green default."""
    state=controller.state(); item=state['autopilot']['phases'][phase]; number=item['pull_request_number']
    started=time.monotonic(); timeout=controller.config.get('ci_timeout_seconds',1200)
    while time.monotonic()-started < timeout:
        try:
            view=snapshot(number,controller.config)
            current=view['checks']
            required=view['required_checks']
            ready=all(name in current and current[name]['status']=='completed' and current[name]['conclusion']=='success' for name in required)
            if ready and current: return True
            failed=[name for name,c in current.items() if c['status']=='completed' and c['conclusion'] not in ['success','neutral','skipped']]
            if failed:
                controller.record('CI_FAILED',phase=phase,checks=failed)
                return False
        except GitHubBlocked as exc:
            controller.record('CI_INSPECTION_BLOCKED',phase=phase,reason=str(exc)); return False
        if controller.pause_path.exists(): return False
        time.sleep(5)
    controller.record('CI_WAIT_BLOCKED',phase=phase,reason='Current SHA lacks required successful checks before timeout')
    return False
