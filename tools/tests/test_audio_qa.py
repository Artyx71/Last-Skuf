from array import array
import importlib.util
import math
from pathlib import Path
import tempfile
import unittest

path=Path(__file__).resolve().parents[1]/'audio_qa.py'
spec=importlib.util.spec_from_file_location('audio_qa',path);audio=importlib.util.module_from_spec(spec);spec.loader.exec_module(audio)

class SignalTests(unittest.TestCase):
    def sine(self,seconds=.5,gain=.2):
        return array('f',(gain*math.sin(2*math.pi*440*(i//2)/48000) for i in range(int(seconds*48000)*2)))
    def test_nonempty_sine_is_not_clipped(self):
        m=audio.metrics(self.sine(),48000)
        self.assertEqual(m['frames'],24000);self.assertEqual(m['clipped_samples'],0)
        self.assertTrue(all(audio.basic_checks(m).values()))
    def test_silent_file_fails_energy(self):
        m=audio.metrics(array('f',[0.]*9600),48000)
        self.assertFalse(audio.basic_checks(m)['nonempty_signal_energy'])
    def test_clipped_and_dc_signals_fail(self):
        m=audio.metrics(array('f',[1.1,-1.1]*1000),48000)
        self.assertGreater(m['clipped_samples'],0)
        self.assertFalse(audio.basic_checks(m)['no_full_scale_clipping'])
        m=audio.metrics(array('f',[.2,.2]*1000),48000)
        self.assertFalse(audio.basic_checks(m)['bounded_dc'])
    def test_internal_dropout_detected(self):
        sig=self.sine(.6);sig[12000:36000]=array('f',[0.]*24000)
        self.assertGreaterEqual(audio.metrics(sig,48000)['max_internal_silence_seconds'],.24)
    def test_broken_loop_boundary_detected(self):
        sig=self.sine();sig[-2:]=array('f',[.8,.8])
        self.assertGreater(audio.metrics(sig,48000)['boundary_step'],audio.POLICY['loop_join_limit'])
    def test_real_samples_in_event_window_detect_impulse(self):
        sig=self.sine();sig[24000:24002]=array('f',[.9,.9])
        window=audio.event_windows(sig,48000,[{'sample_time_seconds':.25}])[0]
        self.assertGreater(window['max_step'],.8);self.assertTrue(window['in_capture'])
    def test_corrupt_audio_not_accepted_as_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'not-audio.ogg';p.write_bytes(b'not actual audio')
            with self.assertRaises(ValueError):audio.decode(p)

if __name__=='__main__':unittest.main()
