import json
import hashlib
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave

ROOT=Path(__file__).resolve().parents[2]

class P04GEvidenceTests(unittest.TestCase):
    def test_original_provenance_matches_actual_rasters_and_source_inputs(self):
        data=json.loads((ROOT/'assets/source_art/combat_polish/provenance.json').read_text())
        for relative,expected in {**data['inputs'],**data['outputs']}.items():
            self.assertEqual(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),expected,relative)
        self.assertEqual(hashlib.sha256((ROOT/'assets/source_art/combat_polish/render.py').read_bytes()).hexdigest(),data['recipe_sha256'])
        atlas=json.loads((ROOT/'game/assets/art/combat_polish/atlas.json').read_text())
        self.assertEqual(len(atlas['frames']),528)
        for f in atlas['frames']:
            raw=(ROOT/'game/assets/art/combat_polish'/f['sheet']).read_bytes()
            self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
            w,h=struct.unpack('>II',raw[16:24]);x,y,fw,fh=f['rect']
            self.assertLessEqual(x+fw,w);self.assertLessEqual(y+fh,h)
    def test_actual_dsp_pcm_and_hashes_match_manifest_without_listening_claim(self):
        data=json.loads((ROOT/'assets/source_audio/combat_polish/provenance.json').read_text())
        manifest=json.loads((ROOT/'game/assets/audio/combat_polish.json').read_text())
        self.assertEqual(len(manifest['sfx']),20)
        for id,entry in manifest['sfx'].items():
            file=ROOT/'game'/entry['path'].removeprefix('res://')
            self.assertEqual(hashlib.sha256(file.read_bytes()).hexdigest(),data['assets'][id]['sha256'])
            with wave.open(str(file),'rb') as w:
                self.assertEqual((w.getnchannels(),w.getsampwidth(),w.getframerate()),(1,2,44100))
                self.assertGreater(w.getnframes(),5000)
            self.assertEqual(data['assets'][id]['full_scale_samples'],0)
        self.assertIn('NOT_PERFORMED',data['listening'])
    def test_native_tool_refuses_to_overwrite_retained_attempt_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            output=Path(tmp)/'evidence';output.mkdir();(output/'retained.txt').write_text('do not overwrite')
            p=subprocess.run([sys.executable,str(ROOT/'tools/verify_p04g.py'),'--headless','--output',str(output),'--build-output',str(Path(tmp)/'build')],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)
            self.assertIn('Immutable evidence',p.stderr)
            self.assertEqual((output/'retained.txt').read_text(),'do not overwrite')
    def test_headless_movie_cannot_be_misreported_as_rendered(self):
        p=subprocess.run([sys.executable,str(ROOT/'tools/verify_p04g.py'),'--headless','--movie','--output','unused','--build-output','unused'],capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn('requires actual rendering',p.stderr)
