import numpy as np
import matplotlib.pyplot as plt

def generate_signal(frequency, amplitude, sample_rate, duration, start_time=0.0):
    # Generate time values
    time = np.arange(0, duration, 1 / sample_rate) + start_time

    # Generate sinusoidal signal
    signal = amplitude * np.sin(2 * np.pi * frequency * time)

    return time, signal

if __name__ == "__main__":

    # Signal parameters
    amplitude = 1.0
    frequency = 10
    duration = 1.0

    #  Two different sampling rates
    good_sample_rate = 1000
    bad_sample_rate = 15

    # Generate time values
    time_good = np.arange(0, duration, 1 / good_sample_rate)
    time_bad = np.arange(0, duration, 1 / bad_sample_rate)

    # Generate the signal
    signal_good = amplitude * np.sin(2 * np.pi * frequency * time_good)
    signal_bad = amplitude * np.sin(2 * np.pi * frequency * time_bad)

    # Plot the signal
    plt.figure(figsize=(10,6))

    plt.plot(time_good, signal_good, label="1000 Hz Sampling", color="blue")

    plt.plot(time_bad, signal_bad, "o-", label="15 Hz Sampling", color="red")

    plt.title("RF-Sense | Sampling Rate Comparison")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)
    plt.show()