from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]

class P05EvidenceTests(unittest.TestCase):
    def test_retained_story_evidence_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            output=Path(tmp)/'evidence';output.mkdir();retained=output/'original.json';retained.write_bytes(b'{"retained":true}')
            result=subprocess.run([sys.executable,str(ROOT/'tools/verify_p05.py'),'--headless','--output',str(output),'--build-output',str(Path(tmp)/'build')],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertEqual(retained.read_bytes(),b'{"retained":true}')
            self.assertEqual(sorted(p.name for p in output.iterdir()),['original.json'])

    def test_headless_story_execution_cannot_claim_movie_evidence(self):
        result=subprocess.run([sys.executable,str(ROOT/'tools/verify_p05.py'),'--headless','--movie','--output','unused','--build-output','unused'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('requires actual rendering',result.stderr)
