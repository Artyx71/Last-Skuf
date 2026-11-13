from array import array
import math
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import wave

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analyze_p04g_audio import analyze_asset
from audio_qa import decode


class P04GSignalTests(unittest.TestCase):
    def make_wav(self, directory, values):
        path = Path(directory)/'cue.wav'
        with wave.open(str(path), 'wb') as output:
            output.setparams((1, 2, 44100, 0, 'NONE', 'not compressed'))
            output.writeframes(struct.pack('<'+'h'*len(values), *values))
        return path

    def test_mono_decode_preserves_native_peak_and_two_identical_channels(self):
        with tempfile.TemporaryDirectory() as directory:
            values = [int(8000*math.sin(2*math.pi*440*i/44100)) for i in range(8820)]
            path = self.make_wav(directory, values)
            with self.assertRaises(ValueError):
                decode(path)
            signal, rate = decode(path, mono_to_stereo=True)
            self.assertEqual(rate, 44100)
            self.assertEqual(signal[::2], signal[1::2])
            self.assertAlmostEqual(max(map(abs, signal)), max(map(abs, values))/32768, places=6)

    def test_silent_actual_wav_fails_energy_and_true_peak(self):
        with tempfile.TemporaryDirectory() as directory:
            report = analyze_asset(self.make_wav(directory, [0]*8820))
            self.assertFalse(report['passed'])
            self.assertFalse(report['checks']['nonempty_signal_energy'])

    def test_positive_pcm_rail_is_rejected_even_below_float_one(self):
        with tempfile.TemporaryDirectory() as directory:
            values = [0]*100 + [32767, -32767]*4300 + [0]*120
            report = analyze_asset(self.make_wav(directory, values))
            self.assertFalse(report['passed'])
            self.assertFalse(report['checks']['no_pcm_rails'])
            self.assertEqual(report['signal']['pcm_full_scale_samples'], 8600)

    def test_abrupt_final_sample_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            values = [int(5000*math.sin(2*math.pi*440*i/44100)) for i in range(8820)]
            values[0] = 0
            values[-1] = 8000
            report = analyze_asset(self.make_wav(directory, values))
            self.assertFalse(report['checks']['quiet_endpoints'])
            self.assertFalse(report['passed'])


if __name__ == '__main__':
    unittest.main()
