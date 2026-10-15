import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq

# Signal parameters
sample_rate = 1000
duration = 1.0

# Generate time values
time = np.arange(0, duration, 1 / sample_rate)

# Generate two signals
signal_1 = 0.3 * np.sin(2 * np.pi * 10 * time)
signal_2 = 0.8 * np.sin(2 * np.pi * 30 * time)

# Combine the signals
combined_signal = signal_1 + signal_2

# Calculate the FFT
fft_values = rfft(combined_signal)
frequencies = rfftfreq(len(combined_signal), 1 / sample_rate)

# Calculate the amplitude spectrum
amplitudes = 2 * np.abs(fft_values) / len(combined_signal)

# Plot the frequency spectrum
plt.plot(frequencies, amplitudes)
plt.title("RF-Sense | First Spectrum Analyzer")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.xlim(0, 60)
plt.grid(True)
plt.show()