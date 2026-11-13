"""Real Git index/worktree fixtures; never contact GitHub or push a branch."""
from contextlib import contextmanager
import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'autopilot'))
from github import GitHubBlocked, publish_branch


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.work=Path(self.temp.name)
        self.git('init','-b','phase/p04-fixture')
        self.git('config','user.name','Fixture');self.git('config','user.email','fixture@example.invalid')
        self.git('remote','add','origin','https://github.com/Artyx71/Last-Skuf.git')
        (self.work/'game').mkdir();(self.work/'game/mission.gd').write_text('original\n')
        (self.work/'reports').mkdir();(self.work/'reports/existing.json').write_text('{}')
        self.git('add','.');self.git('commit','-m','fixture')
        self.head=self.git('rev-parse','HEAD').strip()
    def tearDown(self):self.temp.cleanup()
    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.work,text=True,stderr=subprocess.DEVNULL)
    @contextmanager
    def mutations(self,on_privacy=None):
        original=subprocess.run;calls=[]
        def run(argv,*args,**kwargs):
            if argv[0]==sys.executable or argv[:2]==['git','push']:
                calls.append(argv)
                if argv[0]==sys.executable and on_privacy:on_privacy()
                return subprocess.CompletedProcess(argv,0,b'',b'')
            return original(argv,*args,**kwargs)
        with patch('github.subprocess.run',side_effect=run):yield calls
    def forbidden(self):
        with self.mutations() as mutation:
            with self.assertRaises(GitHubBlocked):publish_branch(self.work,'phase/p04-fixture')
            self.assertEqual(mutation,[])
    def test_unstaged_source_cannot_push(self):
        (self.work/'game/mission.gd').write_text('new\n');self.forbidden()
    def test_untracked_source_cannot_push(self):
        (self.work/'game/new.gd').write_text('new\n');self.forbidden()
    def test_staged_source_cannot_push(self):
        (self.work/'game/new.gd').write_text('new\n');self.git('add','game/new.gd');self.forbidden()
    def test_staged_then_restored_source_cannot_push(self):
        p=self.work/'game/mission.gd';p.write_text('new\n');self.git('add','game/mission.gd');p.write_text('original\n');self.forbidden()
    def test_source_deletion_cannot_push(self):
        (self.work/'game/mission.gd').unlink();self.forbidden()
    def test_source_renamed_into_reports_cannot_push(self):
        self.git('mv','game/mission.gd','reports/mission.gd');self.forbidden()
    def test_staged_report_cannot_push(self):
        (self.work/'reports/new.json').write_text('{}');self.git('add','reports/new.json');self.forbidden()
    def test_report_symlink_escape_cannot_push(self):
        (self.work/'reports/escape').symlink_to(self.work/'game/mission.gd');self.forbidden()
    def test_wrong_current_branch_cannot_push(self):
        self.git('switch','-c','phase/p03-fixture');self.forbidden()
    def test_dirty_prepare_never_pushes_or_creates_pull_request(self):
        from github import manage
        (self.work/'game/new.gd').write_text('uncommitted implementation\n')
        state={'active_phase':'P04','autopilot':{'history':[],'phases':{'P04':{
            'status':'VALIDATING','workspace':str(self.work),'branch':'phase/p04-fixture'}}}}
        controller=SimpleNamespace(root=self.work,config={'repository_visibility':'public'},
            state=lambda:state,persist=lambda value:None)
        calls=[]
        def api(endpoint,method='GET',payload=None):
            calls.append((endpoint,method))
            if '/pulls?' in endpoint:return []
            if endpoint=='repos/Artyx71/Last-Skuf':return {'private':False}
            raise AssertionError('Unexpected API mutation: '+method+' '+endpoint)
        with self.mutations() as mutations,patch('github.api',side_effect=api),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(manage(controller,'P04','prepare'),4)
            self.assertEqual(mutations,[])
        self.assertTrue(calls);self.assertTrue(all(method=='GET' for _,method in calls))
    def test_clean_and_generated_reports_push_verified_object(self):
        for reports in [False,True]:
            with self.subTest(reports=reports):
                if reports:
                    (self.work/'reports/existing.json').write_text('{"new":true}')
                    (self.work/'reports/new.json').write_text('{}')
                with self.mutations() as mutation:
                    publish_branch(self.work,'phase/p04-fixture')
                    self.assertEqual(len(mutation),2)
                    self.assertEqual(mutation[-1],['git','push','origin',self.head+':refs/heads/phase/p04-fixture'])
    def test_source_changed_during_privacy_prevents_push(self):
        def change():(self.work/'game/mission.gd').write_text('changed\n')
        with self.mutations(change) as mutation:
            with self.assertRaises(GitHubBlocked):publish_branch(self.work,'phase/p04-fixture')
            self.assertEqual(len(mutation),1)
    def test_head_changed_during_privacy_prevents_push(self):
        def change():self.git('commit','--allow-empty','-m','changed')
        with self.mutations(change) as mutation:
            with self.assertRaises(GitHubBlocked):publish_branch(self.work,'phase/p04-fixture')
            self.assertEqual(len(mutation),1)


if __name__=='__main__':unittest.main()
