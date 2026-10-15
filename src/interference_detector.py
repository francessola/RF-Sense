import numpy as np

def detect_peaks(amplitudes, threshold):
    """Detect local maxima above a threshold."""

    peaks = np.where(
        (amplitudes[1:-1] > amplitudes[:-2]) &
        (amplitudes[1:-1] > amplitudes[2:]) &
        (amplitudes[1:-1] >= threshold)
    )[0] + 1

    return peaks

def classify_frequency(detected_frequency, expected_frequency, tolerance):
    """Classify a detected frequency"""

    difference = abs(detected_frequency - expected_frequency)

    if difference <= tolerance:
        return "Expected Signal"
    else:
        return "Possible Interference"

