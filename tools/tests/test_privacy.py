"""Regression: an old manifest photo is still detected after local replacement/rename."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('privacy',ROOT/'tools/check_privacy.py')
privacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(privacy)

class PrivacyTests(unittest.TestCase):
    def test_original_reference_hash_catches_renamed_blob_after_local_replacement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            subprocess.run(['git','init','-q',root],check=True)
            (root/'.gitignore').write_bytes((ROOT/'.gitignore').read_bytes())
            original=b'private reference fixture; not a real photograph'
            reference=root/'assets/references/characters/timka_ref01.png';reference.parent.mkdir(parents=True)
            reference.write_bytes(b'new local reference fixture')
            manifest=[{'path':str(reference.relative_to(root)),'sha256':hashlib.sha256(original).hexdigest()}]
            (root/'assets/references/manifest.json').write_text(json.dumps(manifest))
            (root/'innocent.dat').write_bytes(original)
            subprocess.run(['git','add','.gitignore','innocent.dat'],cwd=root,check=True)
            old=privacy.ROOT;privacy.ROOT=root
            try:
                with contextlib.redirect_stdout(io.StringIO()) as output:failed=privacy.main()
            finally:privacy.ROOT=old
            self.assertTrue(failed)
            self.assertIn('Manifest/private reference content',output.getvalue())

if __name__=='__main__':unittest.main()
