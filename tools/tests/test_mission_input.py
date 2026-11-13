"""Actual engine fault injection: QA must reject unexpected idle movement."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]


class MissionInputTests(unittest.TestCase):
    def test_idle_input_failure_cannot_reuse_stale_death_evidence(self):
        lock=json.loads((ROOT/'tools/toolchain.lock.json').read_text())
        godot=ROOT/'.tools/godot'/('Godot_v'+lock['release']+'_linux.x86_64')
        self.assertTrue(godot.is_file(),'Pinned Godot must be installed before integration tests')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);env=dict(os.environ)
            for key,name in [('AYAY_OPTIONS_PATH','options.json'),('AYAY_DIALOGUE_SAVE_PATH','dialogue.json'),
                             ('AYAY_CHAPTER_SAVE_PATH','chapter.json'),('AYAY_P04_RESULT_PATH','replay.json'),
                             ('AYAY_P04_AUDIO_PATH','replay.wav')]:env[key]=str(folder/name)
            proc=subprocess.run([str(godot),'--headless','--fixed-fps','60','--disable-vsync','--max-fps','0',
                '--path',str(ROOT/'game'),'--script','res://tests/mission_input_fault.gd','--','--p04-replay'],
                env=env,capture_output=True,text=True,timeout=30)
            output=proc.stdout+proc.stderr
            self.assertEqual(proc.returncode,1,output[-2000:])
            report=json.loads((folder/'replay.json').read_text())
            self.assertIs(report['passed'],False)
            self.assertEqual(report['abort']['cycle'],1)
            self.assertEqual(report['abort']['observed_input'],[1.0,0.0])
            self.assertEqual(len(report['deaths']),1,'No fabricated nine retries from prior snapshot')
            self.assertIs(report['deaths'][0]['actual_ai_death'],True)
            self.assertEqual(int(report['progress']['deaths']),1)
            self.assertNotIn('ObjectDB instances were leaked',output)
            self.assertNotIn('resources still in use',output)


if __name__=='__main__':unittest.main()
