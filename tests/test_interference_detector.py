import unittest
import sys
from pathlib import Path
import numpy as np
from scipy.fft import rfft, rfftfreq

# Add src folder to Python's import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

# Import detector functions
from interference_detector import detect_peaks, classify_frequency

# Import evaluation functions
from evaluation import (calculate_precision, calculate_recall, calculate_f1_score)

class TestInterferenceDetector(unittest.TestCase):

    def test_detect_single_peak(self):
        amplitudes = np.array([0.1, 0.3, 0.9, 0.2, 0.1])
        threshold = 0.5

        peaks = detect_peaks(amplitudes, threshold)

        np.testing.assert_array_equal(peaks, [2])

    def test_no_peaks_above_threshold(self):
        amplitudes = np.array([0.1,0.3,0.9,0.2,0.1])
        threshold = 0.95

        peaks = detect_peaks(amplitudes, threshold)

        self.assertEqual(len(peaks),0)

    def test_detect_multiple_peaks(self):
        amplitudes = np.array([0.1,0.8,0.2,0.1,0.9,0.2,0.1])
        threshold = 0.5

        peaks = detect_peaks(amplitudes,threshold)

        np.testing.assert_array_equal(peaks, [1,4]) #verifica tambien que los indices sean correctos ademas del peak quantity

    def test_classify_expected_frequency(self):
        detected_frequency = 10.5
        expected_frequency = 10.0
        tolerance = 1.0

        result = classify_frequency(detected_frequency, expected_frequency, tolerance)

        self.assertEqual(result, "Expected Signal")

    def test_classify_possible_interference(self):
        detected_frequency = 30.0
        expected_frequency = 10.0
        tolerance = 1.0

        result = classify_frequency(detected_frequency, expected_frequency, tolerance)

        self.assertEqual(result, "Possible Interference")

    def test_frquency_just_outside_tolerance(self):
        detected_frequency = 11.01
        expected_frequency = 10.0
        tolerance = 1.0

        result = classify_frequency(detected_frequency, expected_frequency, tolerance)

        self.assertEqual(result, "Possible Interference")

    def test_frequency_just_below_lower_boundary(self):
        detected_frequency = 8.99
        expected_frequency = 10.0
        tolerance = 1.0

        result = classify_frequency(detected_frequency, expected_frequency, tolerance)

        self.assertEqual(result, "Possible Interference")

    def test_frquency_at_lower_boundary(self):
        detected_frequency = 27.5
        expected_frequency = 30.0
        tolerance = 2.5

        result = classify_frequency(detected_frequency, expected_frequency, tolerance)

        self.assertEqual(result, "Expected Signal")

    def test_detection_and_classification(self):
        frequencies = np.array([0,10,20,30,40])
        amplitudes = np.array([0.1,0.9,0.1,0.8,0.1])

        threshold = 0.5
        expected_frequency = 10.0
        tolerance = 1.0

        peaks = detect_peaks(amplitudes, threshold)

        classifications = []

        for peak in peaks:
            frequency = frequencies[peak]

            result = classify_frequency(frequency, expected_frequency, tolerance)

            classifications.append(result)

        self.assertEqual(classifications, ["Expected Signal", "Possible Interference"])

    def test_synthetic_signal_pipeline(self):
        sample_rate = 1000
        duration = 1.0

        time = np.arange(0, duration, 1 / sample_rate)

        expected_signal = np.sin(2 * np.pi * 10 * time)
        interference = 0.8 * np.sin(2 * np.pi * 30 * time)

        combined_signal = expected_signal + interference

        fft_values = rfft(combined_signal)
        frequencies = rfftfreq(len(combined_signal), 1 / sample_rate)
        amplitudes = 2 * np.abs(fft_values) / len(combined_signal)

        peaks = detect_peaks(amplitudes, threshold=0.5)

        detected_frequencies = frequencies[peaks]

        np.testing.assert_allclose(detected_frequencies, [10.0, 30.0], atol=0.01)

    def test_fft_frequency_resolution(self):
        sample_rate = 1000
        num_samples = 500

        frequencies = rfftfreq(num_samples, 1 / sample_rate)

        expected_resolution = 2.0
        actual_resolution = frequencies[1] - frequencies[0]

        self.assertAlmostEqual(actual_resolution, expected_resolution)

    def test_detection_with_noise(self):
        sample_rate = 1000
        duration = 1.0

        time = np.arange(0, duration, 1 /sample_rate)

        expected_signal = np.sin(2 * np.pi * 10 * time)
        interference = 0.8 * np.sin(2 * np.pi * 30 * time)

        rng = np.random.default_rng(42)
        noise = 0.3 * rng.normal(0, 1, len(time))

        combined_signal = expected_signal + interference + noise

        fft_values = rfft(combined_signal)
        frequencies = rfftfreq(len(combined_signal), 1 / sample_rate)
        amplitudes = 2 * np.abs(fft_values) / len(combined_signal)

        peaks = detect_peaks(amplitudes, threshold=0.5)
        detected_frequencies = frequencies[peaks]

        self.assertTrue(np.any(np.isclose(detected_frequencies, 10.0, atol=0.5)))
        self.assertTrue(np.any(np.isclose(detected_frequencies, 30.0, atol=0.5)))

    def test_no_false_positives_with_noise(self):
        sample_rate = 1000
        duration = 1.0

        time = np.arange(0, duration, 1 / sample_rate)

        expected_signal = np.sin(2 * np.pi * 10 * time)

        rng = np.random.default_rng(42)
        noise = 0.3 * rng.normal(0, 1, len(time))

        combined_signal = expected_signal + noise

        fft_values = rfft(combined_signal)
        frequencies = rfftfreq(len(combined_signal), 1 /sample_rate)
        amplitudes = 2 * np.abs(fft_values) / len(combined_signal)

        peaks = detect_peaks(amplitudes, threshold=0.5)

        detected_frequencies = frequencies[peaks]

        unexpected_frequencies = [
            frequency 
            for frequency in detected_frequencies
            if classify_frequency(frequency, 10.0, 1.0) == "Possible Interference"
        ]

        self.assertEqual(len(unexpected_frequencies), 0)

    def test_performance_evaluation(self):
        sample_rate = 1000
        duration = 1.0
        time = np.arange(0, duration, 1 / sample_rate)

        scenarios = [
            (30.0, True),
            (40.0, True),
            (None, False),
            (None, False)
        ]

        tp = 0
        fp = 0
        fn = 0
        tn = 0

        for interference_frequency, has_interference in scenarios:
            signal = np.sin(2 * np.pi * 10 * time)

            if has_interference:
                signal += 0.8 * np.sin(
                    2 * np.pi * interference_frequency * time
                )
            
            fft_values = rfft(signal)
            frequencies = rfftfreq(len(signal), 1 / sample_rate)
            amplitudes = 2 * np.abs(fft_values) / len(signal)

            peaks = detect_peaks(amplitudes, threshold=0.5)
            detected_frequencies = frequencies[peaks]

            predicted_interference = any(
                classify_frequency(frequency, 10.0, 1.0) == "Possible Interference"
                for frequency in detected_frequencies
            )

            if has_interference and predicted_interference:
                tp += 1
            elif not has_interference and predicted_interference:
                fp += 1
            elif has_interference and not predicted_interference:
                fn += 1
            else:
                tn += 1

        precision = calculate_precision(tp, fp)
        recall = calculate_recall(tp, fn)
        f1_score = calculate_f1_score(tp, fp, fn)

        self.assertEqual((tp, fp, fn, tn), (2, 0, 0, 2))
        self.assertAlmostEqual(precision, 1.0)
        self.assertAlmostEqual(recall, 1.0)
        self.assertAlmostEqual(f1_score, 1.0)



if __name__ == "__main__":
    unittest.main()