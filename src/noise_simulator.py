import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import rfft, rfftfreq
#  scipy.signal import find_peaks

# Signal parameters
sample_rate = 1000
duration = 1.0
frequency = 10
amplitude = 1.0

# Generate time values 
time = np.arange(0, duration, 1 / sample_rate)

# Generate clean signal
clean_signal = amplitude * np.sin(2 * np.pi * frequency * time)

# Generate random noise
rng = np.random.default_rng(42)
noise = 0.3 * rng.normal(0, 1, len(time))

# Generate synthetic interference
interference_frequency = 30
interference_amplitude = 0.8

interference = interference_amplitude * np.sin(2 * np.pi * interference_frequency * time)

# Combine original signal, interference, and noise
noisy_signal = clean_signal + interference + noise

# Calculate signal and noise power
signal_power = np.mean(clean_signal ** 2)
noise_power = np.mean(noise ** 2)

# Calculate Signal-to-Noise Ratio
snr = 10 * np.log10(signal_power / noise_power)

print(f"Signal power: {signal_power:.4f}")
print(f"Noise power: {noise_power:.4f}")
print(f"SNR: {snr:.2f} dB")

# Plot both signals
plt.figure(figsize=(10,6))
plt.plot(time, clean_signal, label="Clean Signal", color="blue")
plt.plot(time, noisy_signal, label="Noisy Signal", color="red", alpha=0.7)

plt.title("RF-Sense | Clean vs Noisy Signal")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

# Calculate FFT of noisy signal
fft_values = rfft(noisy_signal)
frequencies = rfftfreq(len(noisy_signal), 1 /sample_rate)

# Calculate amplitude spectrum
amplitudes = 2 * np.abs(fft_values) / len(noisy_signal)

# Detect peaks above the threshold
threshold = 0.5
peaks = np.where (
    (amplitudes[1:-1] > amplitudes[:-2]) &
    (amplitudes[1:-1] > amplitudes[2:]) &
    (amplitudes[1:-1] >= threshold)
)[0] + 1

# Display detected frequencies
print("\nDetected Frequency Peaks: ")

for peak in peaks:
    print(f"Frequency: {frequencies[peak]:.2f} Hz | Amplitude: {amplitudes[peak]:.4f}")

# Expected signal frequency
expected_frequency = 10
tolerance = 1.0

print("\nSignal Classification: ")

for peak in peaks:
    detected_frequency = frequencies[peak]

    if abs(detected_frequency - expected_frequency) <= tolerance:
        print(f"{detected_frequency:.2f} Hz | Expected Signal")
    else:
        print(f"{detected_frequency:.2f} Hz | Possible Interference")

# Plot frequency spectrum
plt.figure(figsize=(10,6))
plt.plot(frequencies, amplitudes, color="purple")

plt.title("RF-Sense | Noisy Signal Spectrum")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.xlim(0, 60)
plt.grid(True)

plt.show()